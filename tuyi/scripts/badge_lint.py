#!/usr/bin/env python3
"""badge_lint.py —— profile 驱动的徽章系统审查器（仅标准库）。

把一份设计规范（profile YAML）编译成可执行检查，扫描目标 HTML/CSS/TSX，
输出 file:line 级 findings、已合规清单、N/A 清单与 pending 冲突提示。

子命令：
  check   按 profile.rules 扫描目标（默认）
  rules   打印 profile 的规则清单（不扫描）

退出码：0=PASS（无 blocker/major）；1=检出 blocker 或 major；2=用法/解析/目标错误。
用法见 --help。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from bisect import bisect_right
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    from _profile_yaml import YamlSubsetError, load_yaml
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _profile_yaml import YamlSubsetError, load_yaml  # type: ignore

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_ERROR = 2

SEVERITY_ORDER = {"blocker": 0, "major": 1, "minor": 2, "info": 3}
BLOCK_LEVELS = {"blocker", "major"}

# —— 性能：预编译正则与进程内缓存（单次 CLI 运行内目标文件不变，可安全复用）——
_RE_CLASS_ATTR = re.compile(r'class(?:Name)?\s*=\s*[\x27\x22]([^\x27\x22]*)[\x27\x22]')
_RE_CLASSNAME_JSX = re.compile(r'className\s*=\s*\{\{([^}]*)\}\}')
_RE_INNER_TEXT = re.compile(r'>([^<>]*)</')
_RE_MUSTACHE = re.compile(r'\{\{[^}]*\}\}')
_RE_JSX_COMMENT = re.compile(r'\{/\*.*?\*/\}', re.S)
_RE_OPEN_TAG = re.compile(r'^<[a-zA-Z][\w-]*')
_RE_TOKEN_REF = re.compile(r'--([a-zA-Z0-9-]+)')
_RE_ANY_TAG = re.compile(r'<([a-zA-Z][\w-]*)[\s>/]')
_TAG_RX_CACHE: dict[str, re.Pattern] = {}
_ATTR_RX_CACHE: dict[str, re.Pattern] = {}
_SLH_CACHE: dict[tuple[str, str], list[int]] = {}

CHECK_KINDS = (
    "css_forbid",
    "css_value_in",
    "css_value_not_in",
    "css_value_min",
    "dom_attr_required",
    "dom_text_forbidden",
    "dom_forbid_descendant",
    "source_forbid_regex",
    "phase_css_required",
    "phase_anim_reduce_required",
    "phase_slot_overlay_required",
    "phase_aria_busy_required",
)

PROPERTY_ALIASES = {
    "border": ("border", "border-width", "border-color", "border-style"),
    "border-width": ("border-width", "border-width-top", "border-width-left"),
    "background": ("background", "background-color", "background-image"),
    "background-color": ("background-color",),
    "margin": ("margin", "margin-left", "margin-right", "margin-top", "margin-bottom"),
    "margin-left": ("margin-left",),
    "padding": ("padding", "padding-left", "padding-right"),
    "position": ("position",),
    "color": ("color",),
    "fill": ("fill",),
    "stroke": ("stroke",),
    "width": ("width",),
    "height": ("height",),
    "min-width": ("min-width",),
    "min-height": ("min-height",),
    "font-size": ("font-size",),
}

SEL_TOKEN_RE = re.compile(r"^[\w\-]+(?:#[\w\-]+)?$")



class LintError(Exception):
    '''用法或输入错误。'''


def _rel(path: Path, root: Path) -> str:
    '''取相对 root 的路径。入口已 resolve 过的路径直接算，避免重复走文件系统。'''
    try:
        return str(Path(path).relative_to(root))
    except ValueError:
        pass
    try:
        return str(Path(path).resolve().relative_to(root))
    except ValueError:
        return str(path)


def _numeric(value: str) -> tuple[float, str] | None:
    m = re.match(r'^([+-]?(?:[0-9]+\.?[0-9]*|\.[0-9]+))([a-z%]*)$', value.strip())
    if not m:
        return None
    return float(m.group(1)), (m.group(2) or '').lower()


_DECL_RE = re.compile(r'([a-zA-Z-]+)\s*:\s*([^;{}]+?)(?:;|$)')


def declarations_of(text: str) -> list[tuple[int, str, str]]:
    '''返回 (行号, 属性名, 属性值) 列表；跳过整行注释。'''
    out: list[tuple[int, str, str]] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('/*'):
            continue
        for m in _DECL_RE.finditer(line):
            prop = m.group(1).strip().lower()
            raw = re.sub(r'\s*!\s*important$', '', m.group(2).strip(), flags=re.I).strip()
            if raw:
                out.append((idx, prop, raw))
    return out


PROPERTY_ALIASES = {
    'border': ('border', 'border-width', 'border-color', 'border-style'),
    'border-width': ('border-width', 'border-top-width', 'border-left-width'),
    'background': ('background', 'background-color', 'background-image'),
    'background-color': ('background-color',),
    'margin': ('margin', 'margin-left', 'margin-right', 'margin-top', 'margin-bottom'),
    'margin-left': ('margin-left',),
    'margin-right': ('margin-right',),
    'padding': ('padding', 'padding-left', 'padding-right'),
    'position': ('position',),
    'color': ('color',),
    'fill': ('fill',),
    'stroke': ('stroke',),
    'width': ('width',),
    'height': ('height',),
    'min-width': ('min-width',),
    'min-height': ('min-height',),
    'font-size': ('font-size',),
}


def expand_properties(props) -> tuple[str, ...]:
    out: list[str] = []
    for p in props:
        key = str(p).strip().lower()
        for real in PROPERTY_ALIASES.get(key, (key,)):
            if real not in out:
                out.append(real)
    return tuple(out)


def _token_hexs(token_color: str | None, value: str) -> str | None:
    '''把属性值里的 var(--token) 或十六进制色解析为小写 hex，取不到返回 None。'''
    if not value:
        return None
    m = re.search(r'var\(\s*--([a-zA-Z0-9-]+)', value)
    if m:
        name = m.group(1)
        if isinstance(token_color, dict) and name in token_color:
            got = token_color[name]
            return str(got).strip().lower() or None
        return None
    m = re.match(r'^#([0-9a-fA-F]{3,8})$', value.strip())
    if m:
        raw = m.group(1).lower()
        if len(raw) == 3:
            raw = ''.join(ch * 2 for ch in raw)
        return '#' + raw[:6]
    return None


class CssRule:
    '''一段 CSS 规则块。media 记录所在 @media 查询（顶层为 None），供相位动画 reduce 检查用。'''

    def __init__(self, selector: str, start: int, end: int, media: str | None = None) -> None:
        self.selector = selector.strip()
        self.start = start
        self.end = end
        self.media = media
        self.declarations: list[tuple[int, str, str]] = []

    def matches(self, sel: str) -> bool:
        want = sel.strip()
        if want.startswith('.'):
            cls = want[1:]
            return ('.' + cls) in self.selector
        if want.startswith('[') and want.endswith(']'):
            attr = want[1:-1].split('=')[0].split('~')[0].split('|')[0].split('^')[0].split('$')[0].split('*')[0]
            return attr in self.selector
        return self.selector.split()[0] == want


def parse_css(text: str, path: Path) -> list[CssRule]:
    '''抽出所有块级规则；行号用逐行计数，不猜。

    两项启发式（只做注记，不影响既有结论）：
    - @media 上下文按大括号净计数跟随，规则带 media 属性；嵌套 @media 只记最内层查询。
    - 逗号续行的选择器组（`.a,` 换行 `.b {`）合并进规则头；遇到 `}` 或 @ 行即作废。
    '''
    rules: list[CssRule] = []
    current: CssRule | None = None
    media: str | None = None
    media_depth = 0
    pending: list[str] = []
    for idx, raw in enumerate(text.splitlines(), start=1):
        line = raw
        if media is not None:
            media_depth += line.count('{') - line.count('}')
        elif re.match(r'^\s*@media\b', line) and '{' in line:
            m = re.match(r'^\s*@media\b([^{]*)\{', line)
            media = (m.group(1).strip() if m else line.strip())
            media_depth = line.count('{') - line.count('}')
            if media_depth <= 0:
                media = None
                media_depth = 0
            continue
        if media is not None and media_depth <= 0:
            media = None
            media_depth = 0
        if current is None:
            if '{' in line and not re.match(r'^\s*@', line):
                head = line.split('{', 1)[0].strip()
                if pending:
                    head = (' '.join(pending) + ' ' + head).strip()
                    pending = []
                if head:
                    current = CssRule(head, idx, idx, media=media)
                    depth = 1
                    if '}' in line.split('{', 1)[1]:
                        body = line.split('{', 1)[1].split('}', 1)[0]
                        _attach(current, body, idx)
                        current.end = idx
                        rules.append(current)
                        current = None
                continue
            stripped = line.strip()
            if stripped.endswith(',') and '{' not in stripped and not stripped.startswith(('@', '//', '*', '/*')):
                pending.append(stripped)
                continue
            if stripped == '}' or stripped.startswith('@'):
                pending = []
        else:
            if '}' in line:
                before = line.split('}', 1)[0]
                if before.strip():
                    _attach(current, before, idx)
                current.end = idx
                rules.append(current)
                current = None
            else:
                _attach(current, line, idx)
    if current is not None:
        rules.append(current)
    return rules


def _attach(rule: CssRule, body: str, line_no: int) -> None:
    for idx, prop, val in declarations_of(body):
        rule.declarations.append((line_no, prop, val))


_RE_TAG_NAME = re.compile(r'[A-Za-z][A-Za-z0-9._:-]*')
_RE_ATTR_NAME = re.compile(r'[A-Za-z_:][A-Za-z0-9_:.-]*')
# 开标签属性区里可能改变边界语义的字符：'"' 引号、'{' 表达式、'<' 泛型/嵌套、'`' 模板串
_RE_TAG_STOP = re.compile(r'[>"\'`{<]')
_RE_NEWLINE = re.compile(r'\n')
_RE_TEMPLATE_EXPR = re.compile(r'\$\{[^}]*\}')
_RE_CLASS_LITERAL = re.compile(r'[\'"`]([^\'"`]*)[\'"`]')
_RE_CLASS_NAME = re.compile(r'[A-Za-z_][A-Za-z0-9_-]*')
# 属性选择器体（去掉外层方括号后）的解析式，预编译避免每个元素重复编译
_RE_ATTR_SELECTOR = re.compile(r'([A-Za-z_:][A-Za-z0-9_:.-]*)\s*(?:([~|^$*]?=)\s*(.*))?$', re.S)
_RE_NUMERIC_LITERAL = re.compile(r'^[+-]?(?:[0-9]+\.?[0-9]*|\.[0-9]+)$')
_RE_IDENT_LITERAL = re.compile(r'^[A-Za-z_$][\w$.-]*(?:\.[\w$]+)*$')


class OpenTag:
    '''一次开标签解析结果；complete=False 表示无法可靠解析，不能计入 passed。'''

    __slots__ = (
        'name', 'start_line', 'end_line', 'start_offset', 'end_offset', 'raw',
        'attrs', 'classes', 'self_closing', 'complete', 'parse_error',
        'style', 'style_unknown',
    )

    def __init__(self) -> None:
        self.name = ''
        self.start_line = 1
        self.end_line = 1
        self.start_offset = 0
        self.end_offset = 0
        self.raw = ''
        self.attrs: dict[str, str] = {}
        self.classes: set[str] = set()
        self.self_closing = False
        self.complete = False
        self.parse_error = ''
        self.style: list[tuple[int, str, str]] = []
        # (行号, 属性名或 '*'（属性名不可知）, 原因)：无法静态判定的内联样式条目
        self.style_unknown: list[tuple[int, str, str]] = []


def _balanced_end(text: str, start: int, end: int, open_ch: str, close_ch: str) -> int:
    '''从 start 的 open_ch 起找匹配 close_ch；忽略字符串、注释与转义。找不到返回 -1。'''
    depth = 0
    quote = ''
    i = start
    while i < end:
        ch = text[i]
        if quote:
            if ch == '\\':
                i += 2
                continue
            if ch == quote:
                quote = ''
            i += 1
            continue
        if ch in ('\'', '"', '`'):
            quote = ch
            i += 1
            continue
        if ch == '/' and i + 1 < end and text[i + 1] == '*':
            k = text.find('*/', i + 2, end)
            i = end if k < 0 else k + 2
            continue
        if ch == '/' and i + 1 < end and text[i + 1] == '/':
            k = text.find('\n', i + 2, end)
            i = end if k < 0 else k
            continue
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def _fast_tag_end(text: str, k: int) -> int:
    '''从属性区起点 k 用 C 级查找跳到 '>'，返回其后一位偏移；需要慢路径时返回 -1。

    只用普通字符与成对且无转义的引号时，逐字符扫描的结果与这里一致；
    遇到花括号表达式、裸尖括号、反引号或带转义的引号则交回慢路径。
    '''
    while True:
        m = _RE_TAG_STOP.search(text, k)
        if m is None:
            return -1
        ch = m.group(0)
        if ch == '>':
            return m.start() + 1
        if ch != '"' and ch != "'":
            return -1
        close = text.find(ch, m.start() + 1)
        if close < 0 or text.find('\\', m.start() + 1, close) >= 0:
            return -1
        k = close + 1


def _tag_span(text: str, start: int) -> tuple[int, bool, bool]:
    '''从 start 的 '<' 扫到开标签结束；返回 (结束偏移, 是否自闭合, 是否闭合)。

    属性跨行、引号内的 '>'、JSX 表达式/泛型里的尖括号都不会提前截断。
    '''
    n = len(text)
    m = _RE_TAG_NAME.match(text, start + 1)
    if m is None:
        return start + 1, False, False
    k = m.end()
    fast_end = _fast_tag_end(text, k)
    if fast_end >= 0:
        p = fast_end - 2
        while p > start and text[p].isspace():
            p -= 1
        return fast_end, text[p] == '/', True
    quote = ''
    brace = 0
    angle = 0
    while k < n:
        ch = text[k]
        if quote:
            if ch == '\\':
                k += 2
                continue
            if ch == quote:
                quote = ''
            k += 1
            continue
        if brace > 0 and ch in ('\'', '"', '`'):
            quote = ch
            k += 1
            continue
        if brace > 0 and ch == '/' and k + 1 < n and text[k + 1] == '*':
            e = text.find('*/', k + 2)
            k = n if e < 0 else e + 2
            continue
        if brace > 0 and ch == '/' and k + 1 < n and text[k + 1] == '/':
            e = text.find('\n', k + 2)
            k = n if e < 0 else e
            continue
        if ch == '{':
            brace += 1
        elif ch == '}':
            if brace > 0:
                brace -= 1
        elif brace > 0:
            pass
        elif ch in ('\'', '"'):
            quote = ch
        elif ch == '<':
            angle += 1
        elif ch == '>':
            if angle > 0:
                angle -= 1
            else:
                p = k - 1
                while p > start and text[p].isspace():
                    p -= 1
                return k + 1, text[p] == '/', True
        k += 1
    return n, False, False


def _strip_literal(raw: str) -> str | None:
    '''把内联样式里的字面量还原成可比较的值；动态表达式返回 None。'''
    v = raw.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ('\'', '"', '`'):
        if v[0] == '`' and '${' in v:
            return None
        return v[1:-1].strip()
    if _RE_NUMERIC_LITERAL.match(v):
        return v
    if _RE_IDENT_LITERAL.match(v):
        return v
    if any(x in v for x in ('${', '=>', '<', '>', '?', '&&', '||', '[', ']', '{', '}')):
        return None
    return v


def _kebab(name: str) -> str:
    out = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', name.strip())
    return re.sub(r'[\'"`]', '', out).strip().lower()


def _split_top(text: str, start: int, end: int, sep: str) -> list[tuple[int, int]]:
    '''按顶层分隔符切分；忽略括号、方括号、花括号与字符串内部。'''
    parts: list[tuple[int, int]] = []
    depth = 0
    quote = ''
    seg = start
    i = start
    while i < end:
        ch = text[i]
        if quote:
            if ch == '\\':
                i += 2
                continue
            if ch == quote:
                quote = ''
            i += 1
            continue
        if ch in ('\'', '"', '`'):
            quote = ch
        elif ch in '([{':
            depth += 1
        elif ch in ')]}':
            if depth > 0:
                depth -= 1
        elif ch == sep and depth == 0:
            parts.append((seg, i))
            seg = i + 1
        i += 1
    parts.append((seg, end))
    return parts


def _top_colon(text: str, start: int, end: int) -> int:
    depth = 0
    quote = ''
    i = start
    while i < end:
        ch = text[i]
        if quote:
            if ch == '\\':
                i += 2
                continue
            if ch == quote:
                quote = ''
            i += 1
            continue
        if ch in ('\'', '"', '`'):
            quote = ch
        elif ch in '([{':
            depth += 1
        elif ch in ')]}':
            if depth > 0:
                depth -= 1
        elif ch == ':' and depth == 0:
            return i
        i += 1
    return -1


def _class_tokens(raw: str) -> set[str]:
    '''从 class/className 的属性值抽静态类名；动态插值不猜。'''
    s = raw.strip()
    if not s:
        return set()
    if s.startswith('{') and s.endswith('}'):
        s = s[1:-1]
        lits = _RE_CLASS_LITERAL.findall(s)
        if not lits:
            return set()
        text = ' '.join(lits)
    else:
        text = s
    text = _RE_TEMPLATE_EXPR.sub(' ', text)
    return {t for t in text.split() if _RE_CLASS_NAME.fullmatch(t)}


def _parse_attrs(text: str, start: int, end: int) -> tuple[dict[str, str], tuple[str, str, int] | None, list[str]]:
    '''解析开标签里的属性；style 单独返回 (类型, 内容, 内容偏移)。'''
    attrs: dict[str, str] = {}
    style: tuple[str, str, int] | None = None
    errors: list[str] = []
    i = start
    while i < end:
        while i < end and (text[i].isspace() or text[i] == '/'):
            i += 1
        m = _RE_ATTR_NAME.match(text, i)
        if m is None:
            i += 1
            continue
        name = m.group(0)
        j = m.end()
        while j < end and text[j].isspace():
            j += 1
        if j < end and text[j] == '=':
            j += 1
            while j < end and text[j].isspace():
                j += 1
            if j >= end:
                break
            ch = text[j]
            if ch in ('\'', '"'):
                k = text.find(ch, j + 1, end)
                if k < 0:
                    attrs[name] = text[j + 1:end]
                    errors.append('属性 ' + name + ' 的字符串未闭合')
                    if name == 'style':
                        style = ('css', text[j + 1:end], j + 1)
                    break
                val = text[j + 1:k]
                attrs[name] = val
                if name == 'style':
                    style = ('css', val, j + 1)
                i = k + 1
            elif ch == '{':
                k = _balanced_end(text, j, end, '{', '}')
                if k < 0:
                    attrs[name] = text[j:end]
                    errors.append('属性 ' + name + ' 的表达式未闭合')
                    if name == 'style':
                        style = ('jsx', text[j + 1:end], j + 1)
                    break
                val = text[j:k + 1]
                attrs[name] = val
                if name == 'style':
                    style = ('jsx', val[1:-1], j + 1)
                i = k + 1
            else:
                k = j
                while k < end and not text[k].isspace() and text[k] != '>':
                    k += 1
                val = text[j:k]
                attrs[name] = val
                if name == 'style':
                    style = ('css', val, j)
                i = k
        else:
            attrs[name] = ''
            i = j
    return attrs, style, errors


def _jsx_style_decls(body: str, body_offset: int, target: 'Target') -> tuple[list[tuple[int, str, str]], list[tuple[int, str, str]]]:
    '''解析 JSX 内联 style；返回 (可静态判定的声明, 无法判定的条目)。

    无法判定的条目为 (行号, 属性名或 '*'（属性名不可知）, 原因)；
    简写属性（`{ color }`）属性名可知、取值动态，按已知属性名登记。
    '''
    decls: list[tuple[int, str, str]] = []
    unknown: list[tuple[int, str, str]] = []
    for (s, e) in _split_top(body, 0, len(body), ','):
        seg = body[s:e]
        if not seg.strip():
            continue
        seg_pos = body_offset + s
        while seg_pos < body_offset + e and target.text[seg_pos].isspace():
            seg_pos += 1
        line = target.line_at(seg_pos)
        colon = _top_colon(seg, 0, len(seg))
        if colon < 0:
            prop = _kebab(seg.strip())
            if prop and not seg.strip().startswith('...'):
                unknown.append((line, prop, '内联 style 的 ' + prop + ' 取值无法静态判定'))
            else:
                unknown.append((line, '*', '内联 style 片段无法解析：' + seg.strip()[:60]))
            continue
        key_raw = seg[:colon].strip()
        val_raw = seg[colon + 1:].strip()
        if key_raw.startswith('...'):
            unknown.append((line, '*', '内联 style 使用展开语法，无法静态判定'))
            continue
        prop = _kebab(key_raw)
        if not prop:
            unknown.append((line, '*', '内联 style 缺少属性名'))
            continue
        val = _strip_literal(val_raw)
        if val is None:
            unknown.append((line, prop, '内联 style 的 ' + prop + ' 取值无法静态判定'))
            continue
        vpos = body_offset + s + colon + 1
        while vpos < body_offset + e and target.text[vpos].isspace():
            vpos += 1
        decls.append((target.line_at(vpos), prop, val))
    return decls, unknown


def _css_style_decls(body: str, body_offset: int, target: 'Target') -> tuple[list[tuple[int, str, str]], list[tuple[int, str, str]]]:
    '''解析 HTML 内联 style；无法判定的条目为 (行号, '*', 原因)。'''
    decls: list[tuple[int, str, str]] = []
    unknown: list[tuple[int, str, str]] = []
    for (s, e) in _split_top(body, 0, len(body), ';'):
        seg = body[s:e]
        if not seg.strip():
            continue
        seg_pos = body_offset + s
        while seg_pos < body_offset + e and target.text[seg_pos].isspace():
            seg_pos += 1
        line = target.line_at(seg_pos)
        colon = _top_colon(seg, 0, len(seg))
        if colon < 0:
            unknown.append((line, '*', '内联 style 片段无法解析：' + seg.strip()[:60]))
            continue
        prop = _kebab(seg[:colon])
        val = re.sub(r'\s*!\s*important$', '', seg[colon + 1:].strip(), flags=re.I).strip()
        if not prop or not val:
            unknown.append((line, '*', '内联 style 片段缺少属性名或值'))
            continue
        vpos = body_offset + s + colon + 1
        while vpos < body_offset + e and target.text[vpos].isspace():
            vpos += 1
        decls.append((target.line_at(vpos), prop, val))
    return decls, unknown


def _scan_open_tags(target: 'Target') -> list[OpenTag]:
    '''扫描所有开标签（含跨行/自闭合），并解析属性、类名与内联 style。'''
    text = target.text
    tags: list[OpenTag] = []
    n = len(text)
    i = 0
    while i < n:
        j = text.find('<', i)
        if j < 0:
            break
        i = j + 1
        prev = text[j - 1] if j > 0 else ''
        if prev.isalnum() or prev in '_$.':
            continue
        if j + 1 < n and text[j + 1] in ('/', '!'):
            continue
        m = _RE_TAG_NAME.match(text, j + 1)
        if m is None:
            continue
        name = m.group(0)
        end, self_closing, closed = _tag_span(text, j)
        tag = OpenTag()
        tag.name = name
        tag.start_offset = j
        tag.end_offset = end
        tag.start_line = target.line_at(j)
        tag.end_line = target.line_at(max(j, end - 1))
        tag.raw = text[j:end]
        tag.self_closing = self_closing
        tag.complete = closed
        if not closed:
            tag.parse_error = '开标签未闭合（文件在属性/表达式/字符串内结束）'
        attr_end = end - 1 if closed else end
        attrs, style, errors = _parse_attrs(text, m.end(), attr_end)
        tag.attrs = attrs
        tag.parse_error = tag.parse_error or '；'.join(errors)
        tag.classes = _class_tokens(attrs.get('className') or attrs.get('class') or '')
        if style is not None:
            kind, body, offset = style
            if kind == 'jsx':
                # style={{ ... }}：剥掉对象字面量最外层的一对花括号
                stripped = body.strip()
                if stripped.startswith('{') and stripped.endswith('}'):
                    lead = len(body) - len(body.lstrip())
                    trail = len(body) - len(body.rstrip())
                    body = body[lead + 1:len(body) - trail - 1]
                    offset += lead + 1
                tag.style, tag.style_unknown = _jsx_style_decls(body, offset, target)
            else:
                tag.style, tag.style_unknown = _css_style_decls(body, offset, target)
        tags.append(tag)
    return tags


@lru_cache(maxsize=512)
def _element_selector_spec(sel: str) -> tuple:
    '''把元素级选择器解析成不可变的匹配规格（同一选择器只解析一次）。'''
    want = sel.strip()
    if not want:
        return ('none', '')
    head = want.split()[0]
    if head.startswith('.') and '.' in head[1:]:
        return ('compound', frozenset(c for c in head.split('.') if c))
    if head.startswith('.'):
        return ('class', head[1:])
    if head.startswith('[') and head.endswith(']'):
        body = head[1:-1].strip()
        m = _RE_ATTR_SELECTOR.match(body)
        if m is None:
            return ('nomatch', '')
        name, op, raw = m.group(1), m.group(2), m.group(3)
        if not op:
            return ('attr-exists', name)
        cmp = _strip_literal(raw or '')
        if cmp is None:
            cmp = (raw or '').strip('\'"')
        return ('attr-eq' if op == '=' else 'attr-contains', name, cmp)
    if head.isalpha() and head.islower():
        return ('tag', head)
    return ('raw', want)


def _element_matches(el: OpenTag, sel: str) -> bool:
    '''元素级选择器匹配；后代选择器只看首段（后代结构由 dom_forbid_descendant 处理）。'''
    return _element_matches_spec(el, _element_selector_spec(sel))


def _element_matches_spec(el: OpenTag, spec: tuple) -> bool:
    '''按已解析的选择器规格匹配单个元素（热路径：省掉每次调用的缓存查找）。'''
    kind = spec[0]
    if kind == 'compound':
        return spec[1] <= el.classes
    if kind == 'class':
        return spec[1] in el.classes
    if kind == 'attr-exists':
        return spec[1] in el.attrs
    if kind == 'attr-eq' or kind == 'attr-contains':
        if spec[1] not in el.attrs:
            return False
        got = el.attrs[spec[1]]
        return got == spec[2] if kind == 'attr-eq' else spec[2] in got
    if kind == 'tag':
        return el.name.lower() == spec[1]
    if kind == 'none' or kind == 'nomatch':
        return False
    return spec[1] in el.raw


def _attr_present(el: OpenTag, attr: str) -> bool:
    names = [attr]
    if attr.startswith('aria-'):
        names.append(attr.replace('aria-', 'aria'))
    return any(n in el.attrs for n in names)


def _literal_end(text: str, start: int, end: int) -> int:
    '''从 start 的引号起找配对的同种引号；找不到返回 -1。'''
    q = text[start]
    i = start + 1
    while i < end:
        ch = text[i]
        if ch == '\\':
            i += 2
            continue
        if ch == q:
            return i
        i += 1
    return -1


def _expr_direct_text(content: str) -> tuple[str, bool]:
    '''从 JSX 表达式里取可能成为父元素「直接文本」的字面量。

    表达式里嵌套的 JSX 元素（含其属性与子文本）不算父元素的直接文本；
    只剩标识符/运算符/null 时不产生文本；无法可靠解析时返回 undecidable=True。
    '''
    out: list[str] = []
    i = 0
    n = len(content)
    while i < n:
        ch = content[i]
        if ch == '<':
            if content.startswith('</', i):
                k = content.find('>', i)
                if k < 0:
                    return '', True
                i = k + 1
                continue
            end, _self_closing, closed = _tag_span(content, i)
            if not closed:
                return '', True
            i = end
            continue
        if ch in ('\'', '"', '`'):
            k = _literal_end(content, i, n)
            if k < 0:
                return '', True
            piece = content[i + 1:k].strip()
            if piece:
                out.append(piece)
            i = k + 1
            continue
        if ch == '{':
            k = _balanced_end(content, i, n, '{', '}')
            if k < 0:
                return '', True
            i = k + 1
            continue
        if ch == '/' and i + 1 < n and content[i + 1] == '*':
            k = content.find('*/', i + 2)
            if k < 0:
                return '', True
            i = k + 2
            continue
        i += 1
    return ' '.join(out), False


def _direct_text(text: str, el: OpenTag) -> tuple[str, str]:
    '''取元素的直接文本节点；嵌套子元素的文本不算；动态表达式无法判定时返回错误。'''
    if el.self_closing:
        return '', ''
    i = el.end_offset
    depth = 1
    buf: list[str] = []
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == '<':
            if text.startswith('</', i):
                m = _RE_TAG_NAME.match(text, i + 2)
                k = text.find('>', i)
                i = n if k < 0 else k + 1
                depth -= 1
                if depth == 0:
                    break
                continue
            end, self_closing, closed = _tag_span(text, i)
            if not closed:
                return '', '子标签未闭合，内文无法判定'
            if not self_closing:
                depth += 1
            i = end
            continue
        if ch == '{':
            k = _balanced_end(text, i, n, '{', '}')
            if k < 0:
                return '', '表达式未闭合，内文无法判定'
            content = text[i + 1:k].strip()
            if depth == 1 and content:
                if content.startswith('/*') or content.startswith('//'):
                    pass
                else:
                    piece, undecidable = _expr_direct_text(content)
                    if undecidable:
                        return '', '内文含无法静态判定的表达式'
                    if piece:
                        buf.append(piece)
            i = k + 1
            continue
        if depth == 1:
            buf.append(ch)
        i += 1
    return re.sub(r'\s+', ' ', ''.join(buf)).strip(), ''


class Target:
    '''一个被扫描的文件及其派生内容。'''

    def __init__(self, path: Path, root: Path) -> None:
        self.path = path
        self.root = root
        self.text = path.read_text(encoding='utf-8', errors='replace')
        self.lines = self.text.splitlines()
        self.newlines = [m.start() for m in _RE_NEWLINE.finditer(self.text)]
        self.is_css = path.suffix.lower() in ('.css', '.scss', '.less')
        self.is_markup = path.suffix.lower() in ('.html', '.htm', '.vue')
        self.css_rules = parse_css(self.text, path) if (self.is_css or self.is_markup) else []
        self._rel_cache: str | None = None
        # 非 CSS 目标建倒排索引：类名 → 行号、标签 → 行号，避免每个选择器全量重扫
        self.class_index: dict[str, list[int]] = {}
        self.tag_index: dict[str, list[int]] = {}
        self.class_groups: list[tuple[set, ...]] = []
        self.elements: list[OpenTag] = []
        self._indexed = False
        if not self.is_css:
            self.elements = _scan_open_tags(self)

    def line_at(self, offset: int) -> int:
        '''源码偏移 → 1 起的行号。'''
        if offset < 0:
            return 1
        return bisect_right(self.newlines, offset) + 1

    def _ensure_index(self) -> None:
        '''按需建倒排索引：只有「按选择器取行号」的老路径才需要它。'''
        if not self._indexed and not self.is_css:
            self._build_index()

    def _build_index(self) -> None:
        self._indexed = True
        for n, line in enumerate(self.lines, start=1):
            groups = _class_attr_tokens(line)
            self.class_groups.append(groups)
            for g in groups:
                for c in g:
                    self.class_index.setdefault(c, []).append(n)
            if '<' in line:
                for m in _RE_ANY_TAG.finditer(line):
                    self.tag_index.setdefault(m.group(1), []).append(n)

    def line(self, n: int) -> str:
        if 1 <= n <= len(self.lines):
            return self.lines[n - 1].strip()
        return ''

    def rel(self) -> str:
        if self._rel_cache is None:
            self._rel_cache = _rel(self.path, self.root)
        return self._rel_cache


def _tag_rx(name: str) -> re.Pattern:
    '''标签选择器的预编译搜索（按名字缓存）。'''
    rx = _TAG_RX_CACHE.get(name)
    if rx is None:
        rx = re.compile(r'<' + re.escape(name) + r'[\s>/]')
        _TAG_RX_CACHE[name] = rx
    return rx


def _attr_rx(name: str) -> re.Pattern:
    '''属性存在性的预编译搜索（按名字缓存）。'''
    rx = _ATTR_RX_CACHE.get(name)
    if rx is None:
        rx = re.compile(r'\b' + re.escape(name) + r'\s*=')
        _ATTR_RX_CACHE[name] = rx
    return rx


@lru_cache(maxsize=65536)
def _class_attr_tokens(line: str) -> tuple[set, ...]:
    '''取出一行里所有 class= / className= 的类名集合（每次出现一份；元组便于缓存，调用方只读）。'''
    groups: list[set] = []
    if 'class' not in line:
        return ()
    for m in _RE_CLASS_ATTR.finditer(line):
        groups.append(set(m.group(1).split()))
    for m in _RE_CLASSNAME_JSX.finditer(line):
        groups.append(set(m.group(1).split()))
    return tuple(groups)


def _compound_class_match(line: str, sel: str) -> bool:
    '''形如 .icon-btn.has-count：同一 class 属性里同时含这些类。'''
    want = {c for c in sel.split('.') if c}
    return any(want <= g for g in _class_attr_tokens(line))


def _elem_hits(line: str, sel: str) -> bool:
    '''单行 HTML/TSX 粗匹配：复合 class / 属性选择器 / 标签选择器 / 后代组合。'''
    want = sel.strip()
    if not want:
        return False
    parts = [p for p in want.split() if p]
    if len(parts) >= 2:
        head = parts[0]
        if head.startswith('.'):
            return _compound_class_match(line, head) if '.' in head[1:] else (any(head[1:] in g for g in _class_attr_tokens(line)))
        if head.startswith('[') and head.endswith(']'):
            return head[1:-1].split('=')[0].strip() in line
        return _tag_rx(head).search(line) is not None
    if want.startswith('.') and '.' in want[1:]:
        return _compound_class_match(line, want)
    if want.startswith('.'):
        return any(want[1:] in g for g in _class_attr_tokens(line))
    if want.startswith('[') and want.endswith(']'):
        return want[1:-1].split('=')[0].strip() in line
    if want.isalpha() and want.islower():
        return _tag_rx(want).search(line) is not None
    return want in line

def _looks_like_open_tag(text: str) -> bool:
    t = text.strip()
    if not t.startswith('<'):
        return False
    return _RE_OPEN_TAG.match(t) is not None and t.rstrip().endswith('>')


def _mk(rule: dict, target: Target, line: int, message: str, detail: str) -> dict:
    return {
        'rule': str(rule.get('id', '?')),
        'text': str(rule.get('text', '')),
        'severity': str(rule.get('severity', 'major')),
        'source_ref': str(rule.get('source_ref', '')),
        'file': target.rel(),
        'line': line,
        'message': message,
        'detail': detail,
        'fix': str(rule.get('fix', '')),
    }


def _simple_class_lines(target: Target, cls: str) -> list[int]:
    '''倒排索引取：含该类名的行号。'''
    target._ensure_index()
    return list(target.class_index.get(cls, []))


def _compound_class_lines(target: Target, sel: str) -> list[int]:
    '''倒排索引取：同一 class 属性里同时含这些类的行号（形如 .icon-btn.has-count）。'''
    want = {c for c in sel.split('.') if c}
    if not want:
        return []
    target._ensure_index()
    cand: set[int] | None = None
    for c in want:
        lines = set(target.class_index.get(c, []))
        cand = lines if cand is None else (cand & lines)
    if not cand:
        return []
    out: list[int] = []
    for n in sorted(cand):
        for g in target.class_groups[n - 1]:
            if want <= g:
                out.append(n)
                break
    return out


def _markup_lines_for(target: Target, sel: str) -> list[int]:
    '''非 CSS 目标按选择器取行号：类名/标签走倒排索引，属性与兜底走逐行匹配。'''
    target._ensure_index()
    want = sel.strip()
    if not want:
        return []
    parts = [p for p in want.split() if p]
    head = parts[0] if parts else want
    if len(parts) >= 2:
        if head.startswith('.'):
            if '.' in head[1:]:
                return _compound_class_lines(target, head)
            return _simple_class_lines(target, head[1:])
        if head.startswith('[') and head.endswith(']'):
            key = head[1:-1].split('=')[0].strip()
            return [n for n, line in enumerate(target.lines, start=1) if key in line]
        return list(target.tag_index.get(head, []))
    if want.startswith('.') and '.' in want[1:]:
        return _compound_class_lines(target, want)
    if want.startswith('.'):
        return _simple_class_lines(target, want[1:])
    if want.startswith('[') and want.endswith(']'):
        key = want[1:-1].split('=')[0].strip()
        return [n for n, line in enumerate(target.lines, start=1) if key in line]
    if want.isalpha() and want.islower():
        return list(target.tag_index.get(want, []))
    return [n for n, line in enumerate(target.lines, start=1) if want in line]


def _selector_line_hits(target: Target, sel: str) -> list[int]:
    '''按选择器取行号：CSS 规则取块首行；HTML/TSX 取出现该 class/attr/tag 的行。

    进程内按（目标路径, 选择器）记忆化——单次 CLI 运行内目标文件不变。
    '''
    key = (str(target.path), sel)
    cached = _SLH_CACHE.get(key)
    if cached is not None:
        return cached
    lines: list[int] = []
    if target.is_css or target.path.suffix.lower() in ('.html', '.htm', '.vue'):
        for rule in target.css_rules:
            if rule.matches(sel):
                lines.append(rule.start)
    if not target.is_css:
        lines.extend(_markup_lines_for(target, sel))
    lines = sorted(dict.fromkeys(lines))
    _SLH_CACHE[key] = lines
    return lines


def _attr_missing(line: str, attr: str) -> bool:
    names = [attr]
    if attr.startswith('aria-'):
        names.append(attr.replace('aria-', 'aria'))
    for name in names:
        if _attr_rx(name).search(line):
            return False
    return True


def _inner_text(line: str) -> str:
    m = _RE_INNER_TEXT.search(line)
    if not m:
        return ''
    inner = m.group(1)
    inner = _RE_MUSTACHE.sub('', inner)
    inner = _RE_JSX_COMMENT.sub('', inner)
    return inner.strip()


def _rule_block_for(target: Target, line_no: int) -> CssRule | None:
    for rule in target.css_rules:
        if rule.start <= line_no <= rule.end:
            return rule
    return None


def _selector_hits_with_elements(targets: list[Target], sels: list[str]) -> list[tuple[Target, int, OpenTag | None]]:
    '''选择器命中：CSS 目标取规则块；非 CSS 目标优先元素级匹配，内嵌 CSS 规则也保留。

    元素按起始偏移去重（同一元素被多个选择器命中只算一次）；CSS 规则行单独保留。
    '''
    rows: list[tuple[Target, int, OpenTag | None]] = []
    specs = [(sel, _element_selector_spec(sel)) for sel in sels]
    for t in targets:
        for sel in sels:
            if t.is_css:
                for n in _selector_line_hits(t, sel):
                    rows.append((t, n, None))
        if t.is_css:
            continue
        for sel, spec in specs:
            for el in t.elements:
                if _element_matches_spec(el, spec):
                    rows.append((t, el.start_line, el))
            for css_rule in t.css_rules:
                if css_rule.matches(sel):
                    rows.append((t, css_rule.start, None))
    keyed: dict[tuple[str, int, int], tuple[Target, int, OpenTag | None]] = {}
    for t, n, el in rows:
        key = (t.rel(), n, el.start_offset if el is not None else -1)
        keyed.setdefault(key, (t, n, el))
    return sorted(keyed.values(), key=lambda x: (x[0].rel(), x[1], x[2].start_offset if x[2] is not None else -1))


def _decls_for_hit(t: Target, n: int, el: OpenTag | None, skipped: list[str],
                   props: tuple[str, ...]) -> list[tuple[int, str, str]]:
    '''取一条命中的可判定声明：CSS 规则块 + 元素内联 style。

    与规则属性相关的、解析不了的内联样式条目记入 skipped，且不计入 checked/passed；
    与规则属性无关的动态条目（如只查 border 时的 `{ color }`）不影响本规则。
    '''
    decls: list[tuple[int, str, str]] = []
    if el is not None:
        if not el.complete:
            skipped.append(t.rel() + ':' + str(n) + ' 开标签无法解析：' + (el.parse_error or '原因未知'))
            return decls
        for line, prop, reason in el.style_unknown:
            if prop == '*' or prop in props:
                skipped.append(t.rel() + ':' + str(line) + ' ' + reason)
        decls.extend(el.style)
        return decls
    block = _rule_block_for(t, n)
    if block is not None:
        return list(block.declarations)
    if t.is_css:
        return [d for css_rule in t.css_rules for d in css_rule.declarations]
    return decls


_RE_REDUCE_MEDIA = re.compile(r'prefers-reduced-motion', re.I)


def _token_rx(token: str) -> re.Pattern:
    '''类名/记号整词匹配：前后不能是字母数字连字符。'''
    return re.compile(r'(?<![\w-])' + re.escape(token) + r'(?![\w-])')


def _is_reduce_media(media: str | None) -> bool:
    if not media:
        return False
    low = media.lower()
    return 'prefers-reduced-motion' in low and 'reduce' in low and 'no-preference' not in low


def run_check(rule: dict, targets: list[Target], token_color: dict) -> tuple[list[dict], int, list[str], list[str]]:
    '''执行一条规则；返回 (findings, 检查数, N/A 原因, 未检查原因)。'''
    c = rule.get('check') or {}
    kind = str(c.get('kind', '')).strip()
    sels = _selectors_of(rule)
    findings: list[dict] = []
    checked = 0
    na: list[str] = []
    skipped: list[str] = []

    if kind not in CHECK_KINDS:
        na.append('check.kind 为 ' + (kind or '空') + '，本工具不执行，转人判')
        return findings, checked, na, skipped

    if kind == 'source_forbid_regex':
        pattern = str(c.get('pattern', '')).strip()
        if not pattern:
            na.append('缺少 check.pattern')
            return findings, checked, na, skipped
        try:
            rx = re.compile(pattern)
        except re.error as exc:
            na.append('check.pattern 不是合法正则：' + str(exc))
            return findings, checked, na, skipped
        except_files = {_normalize_rel(x) for x in (c.get('except_files') or [])}
        for t in targets:
            if _is_exempt(t.rel(), except_files):
                continue
            for n, line in enumerate(t.lines, start=1):
                if rx.search(line):
                    findings.append(_mk(rule, t, n, '源码命中禁止模式 ' + pattern, line.strip()))
            checked += len(t.lines)
        return findings, checked, na, skipped

    if kind == 'phase_css_required':
        base = str(c.get('base_class', '')).strip()
        prefix = (str(c.get('class_prefix', 'is-')).strip() or 'is-')
        phases = [str(p).strip() for p in (c.get('phases') or []) if str(p).strip()]
        if not base or not phases:
            na.append('缺少 check.base_class 或 check.phases')
            return findings, checked, na, skipped
        for t in targets:
            if not t.is_css:
                continue
            base_rules = [r for r in t.css_rules if _token_rx(base).search(r.selector)]
            if not base_rules:
                continue
            for phase in phases:
                checked += 1
                if not any(_token_rx(prefix + phase).search(r.selector) for r in t.css_rules):
                    findings.append(_mk(rule, t, base_rules[0].start,
                                        '相位 ' + phase + ' 缺少 .' + base + '.' + prefix + phase + ' 样式覆盖',
                                        base_rules[0].selector))
        return findings, checked, na, skipped

    if kind == 'phase_anim_reduce_required':
        base = str(c.get('base_class', '')).strip()
        prefix = (str(c.get('class_prefix', 'is-')).strip() or 'is-')
        phases = [str(p).strip() for p in (c.get('phases') or []) if str(p).strip()]
        if not base or not phases:
            na.append('缺少 check.base_class 或 check.phases')
            return findings, checked, na, skipped
        for t in targets:
            if not t.is_css:
                continue
            for r in t.css_rules:
                if _is_reduce_media(r.media):
                    continue
                if not _token_rx(base).search(r.selector):
                    continue
                anims = [(ln, val) for ln, prop, val in r.declarations
                         if prop == 'animation' and val.strip().lower() != 'none']
                if not anims:
                    continue
                hit_phase = next((p for p in phases if _token_rx(prefix + p).search(r.selector)), None)
                if hit_phase is None:
                    continue
                checked += 1
                rx = _token_rx(prefix + hit_phase)
                reduced = any(
                    _is_reduce_media(r2.media)
                    and rx.search(r2.selector)
                    and any(prop == 'animation' and val.strip().lower() == 'none'
                            for _, prop, val in r2.declarations)
                    for r2 in t.css_rules
                )
                if not reduced:
                    findings.append(_mk(rule, t, anims[0][0],
                                        '相位 ' + hit_phase + ' 的动画未在 prefers-reduced-motion: reduce 下关闭',
                                        r.selector + ' { animation: ' + anims[0][1] + ' }'))
        return findings, checked, na, skipped

    if kind == 'phase_slot_overlay_required':
        if not sels:
            na.append('缺少 check.selectors')
            return findings, checked, na, skipped
        for t in targets:
            if not t.is_css:
                continue
            for r in t.css_rules:
                if not any(r.matches(sel) for sel in sels):
                    continue
                checked += 1
                decl = {prop: (ln, val) for ln, prop, val in r.declarations}
                pos = decl.get('position')
                if pos is None or pos[1].strip().lower() not in ('absolute', 'fixed'):
                    got = pos[1] if pos else '未声明'
                    findings.append(_mk(rule, t, pos[0] if pos else r.start,
                                        '槽位图标须绝对定位叠放（position: absolute/fixed），当前：' + got,
                                        r.selector))
                opa = decl.get('opacity')
                if opa is None or opa[1].strip() != '0':
                    got = opa[1] if opa else '未声明'
                    findings.append(_mk(rule, t, opa[0] if opa else r.start,
                                        '槽位图标默认须 opacity: 0（由相位切换点亮），当前：' + got,
                                        r.selector))
        return findings, checked, na, skipped

    if kind == 'phase_aria_busy_required':
        marker = str(c.get('marker', '')).strip()
        if not marker:
            na.append('缺少 check.marker')
            return findings, checked, na, skipped
        for t in targets:
            if t.is_css:
                continue
            hits = [n for n, line in enumerate(t.lines, start=1) if marker in line]
            if not hits:
                continue
            checked += 1
            if not any('aria-busy' in line for line in t.lines):
                findings.append(_mk(rule, t, hits[0],
                                    '编排类源文件含 ' + marker + ' 但未设置 aria-busy（相位联动缺失）',
                                    t.line(hits[0]).strip()))
        return findings, checked, na, skipped

    if not sels:
        na.append('缺少 check.selectors，无法定位元素')
        return findings, checked, na, skipped

    hits = _selector_hits_with_elements(targets, sels)
    props = _props_of(rule)

    if kind == 'css_forbid':
        if not props:
            na.append('缺少 check.properties')
            return findings, checked, na, skipped
        for t, n, el in hits:
            decls = _decls_for_hit(t, n, el, skipped, props)
            if not decls:
                continue
            checked += 1
            for ln, prop, val in decls:
                if prop in props:
                    findings.append(_mk(rule, t, ln, '出现被禁属性 ' + prop + ': ' + val, t.line(ln)))
        return findings, checked, na, skipped

    if kind in ('css_value_in', 'css_value_not_in', 'css_value_min'):
        if not props:
            na.append('缺少 check.properties')
            return findings, checked, na, skipped
        allowed = [str(x) for x in (c.get('allowed') or [])]
        bad_tokens = [str(x) for x in (c.get('forbidden_tokens') or [])]
        bad_hexs = [str(x).strip().lower() for x in (c.get('forbidden_values') or [])]
        floor = _numeric(str(c.get('min', '')) + 'px') if c.get('min') is not None else None
        for t, n, el in hits:
            decls = _decls_for_hit(t, n, el, skipped, props)
            if not decls:
                continue
            checked += 1
            for ln, prop, val in decls:
                if prop not in props:
                    continue
                if kind == 'css_value_in':
                    num = _numeric(val)
                    ok = val in allowed or (num is not None and str(int(num[0])) in allowed)
                    if not ok:
                        findings.append(_mk(rule, t, ln, prop + ' 取值 ' + val + ' 不在白名单 [' + ', '.join(allowed) + ']', t.line(ln)))
                elif kind == 'css_value_not_in':
                    tok_refs = _RE_TOKEN_REF.findall(val)
                    hit_tok = [tok for tok in tok_refs if tok in bad_tokens]
                    token_hex = _token_hexs(token_color, val)
                    if not hit_tok and token_hex and token_hex in bad_hexs:
                        hit_tok = ['hex ' + token_hex]
                    if not hit_tok and any(h in val.lower() for h in bad_hexs):
                        hit_tok = ['hex ' + val]
                    if hit_tok:
                        findings.append(_mk(rule, t, ln, prop + ' 使用被禁色 ' + ', '.join(hit_tok) + '（' + val + '）', t.line(ln)))
                else:
                    got = _numeric(val)
                    # React 内联样式的无单位数字按 px 计
                    got_unit = (got[1] or floor[1]) if (got and floor) else (got[1] if got else '')
                    if floor and got and got_unit == floor[1] and got[0] < floor[0]:
                        findings.append(_mk(rule, t, ln, prop + ' = ' + val + ' 低于下限 ' + str(c.get('min')), t.line(ln)))
        return findings, checked, na, skipped

    if kind == 'dom_attr_required':
        attrs = [str(a).strip() for a in (c.get('attributes') or []) if str(a).strip()]
        if not attrs:
            na.append('缺少 check.attributes')
            return findings, checked, na, skipped
        any_of = []
        raw_groups = c.get('attrs_any_of') or []
        for grp in raw_groups:
            if isinstance(grp, str):
                grp = [grp]
            any_of.append([str(a).strip() for a in grp if str(a).strip()])
        for t, n, el in hits:
            if el is None:
                # CSS 规则不是 DOM 元素，不参与属性检查，也不记为未检查
                continue
            if not el.complete:
                skipped.append(t.rel() + ':' + str(n) + ' 开标签无法解析：' + (el.parse_error or '原因未知'))
                continue
            checked += 1
            detail = ' '.join(el.raw.split())[:200] or t.line(n)
            missing = [a for a in attrs if not _attr_present(el, a)]
            if missing:
                findings.append(_mk(rule, t, el.start_line, '元素缺少 ' + ', '.join(missing), detail))
                continue
            if any_of and not any(all(_attr_present(el, a) for a in grp) for grp in any_of):
                labels = [' 或 '.join(grp) for grp in any_of]
                findings.append(_mk(rule, t, el.start_line, '提示属性缺失，需要 ' + ' / '.join(labels) + ' 之一', detail))
        return findings, checked, na, skipped

    if kind == 'dom_text_forbidden':
        for t, n, el in hits:
            if el is None:
                continue
            if not el.complete:
                skipped.append(t.rel() + ':' + str(n) + ' 开标签无法解析：' + (el.parse_error or '原因未知'))
                continue
            inner, err = _direct_text(t.text, el)
            if err:
                skipped.append(t.rel() + ':' + str(n) + ' ' + err)
                continue
            checked += 1
            if inner:
                findings.append(_mk(rule, t, el.start_line, '图标内出现文本「' + inner + '」', ' '.join(el.raw.split())[:200]))
        return findings, checked, na, skipped

    if kind == 'dom_forbid_descendant':
        inner_sels = [str(s).strip() for s in (c.get('forbidden_selectors') or []) if str(s).strip()]
        if not inner_sels:
            na.append('缺少 check.forbidden_selectors')
            return findings, checked, na, skipped
        for t, n, el in hits:
            if el is None:
                continue
            if not el.complete:
                skipped.append(t.rel() + ':' + str(n) + ' 开标签无法解析：' + (el.parse_error or '原因未知'))
                continue
            checked += 1
            lo = max(1, n)
            hi = min(len(t.lines), max(n + 12, el.end_line + 6))
            for n2 in range(lo, hi + 1):
                text = t.lines[n2 - 1] if n2 - 1 < len(t.lines) else ''
                for inner in inner_sels:
                    if _elem_hits(text, inner):
                        findings.append(_mk(rule, t, n2, '内部出现被禁结构 ' + inner, text.strip()))
        return findings, checked, na, skipped

    return findings, checked, na, skipped


def _head(profile: dict) -> dict:
    got = profile.get('profile')
    return got if isinstance(got, dict) else {}


def _normalize_rel(path: str) -> str:
    return str(path).replace('\\', '/').lstrip('./')


def _common_root(paths: list[Path]) -> Path:
    '''取多个文件的最深公共父目录；空列表回退 cwd。'''
    resolved = [p for p in paths if p.is_absolute()]
    if not resolved:
        return Path.cwd()
    if len(resolved) == 1:
        return resolved[0].parent
    parts = [list(p.parts) for p in resolved]
    common: list[str] = []
    for group in zip(*parts):
        if all(x == group[0] for x in group):
            common.append(group[0])
        else:
            break
    return Path(common[0]).joinpath(*common[1:]) if common else Path.cwd()


def _is_exempt(rel: str, except_files: set[str]) -> bool:
    '''rel 命中豁免名单：完整相等，或任一方是另一方的路径后缀。

    root 视点会变（扫 src/ 时 root=src/；扫项目根时 root=项目根），
    因此 src/components/Icon.tsx 与 components/Icon.tsx 应视为同一文件。
    '''
    norm = _normalize_rel(rel)
    for exc in except_files:
        e = _normalize_rel(exc)
        if not e:
            continue
        if norm == e:
            return True
        if norm.endswith('/' + e) or e.endswith('/' + norm):
            return True
    return False


def _selectors_of(rule: dict, key: str = 'selectors') -> list[str]:
    raw = (rule.get('check') or {}).get(key) or []
    if isinstance(raw, str):
        raw = [raw]
    return [str(s).strip() for s in raw if str(s).strip()]


def _props_of(rule: dict, key: str = 'properties') -> tuple[str, ...]:
    raw = (rule.get('check') or {}).get(key) or []
    if isinstance(raw, str):
        raw = [raw]
    return expand_properties(raw) if raw else ()


DEFAULT_INCLUDE = ('.html', '.htm', '.css', '.scss', '.less', '.tsx', '.jsx', '.vue')
SKIP_DIRS = {'node_modules', '.git', 'dist', 'build', '__pycache__', '.next', '.tmp'}


def _collect_targets(paths: list[str], include: set[str], root: Path) -> list[Path]:
    found: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_file():
            found.append(p)
            continue
        if p.is_dir():
            for sub in sorted(p.rglob('*')):
                if not sub.is_file():
                    continue
                if any(part in SKIP_DIRS for part in sub.parts):
                    continue
                if include and sub.suffix.lower() not in include:
                    continue
                found.append(sub)
            continue
        raise LintError('目标不存在：' + raw)
    unique = sorted(dict.fromkeys(found))
    if not unique:
        raise LintError('没有可扫描的文件（检查 --target 与 --include）')
    return unique


def load_profile(path: str) -> dict:
    p = Path(path)
    if not p.is_file():
        raise LintError('profile 不存在：' + path)
    try:
        data = load_yaml(p)
    except YamlSubsetError as exc:
        raise LintError('profile 解析失败（第 ' + str(exc.line) + ' 行）：' + exc.message + ' —— 本工具只支持受限 YAML 子集')
    if not isinstance(data, dict):
        raise LintError('profile 顶层必须是映射')
    return data


def _report_text(profile: dict, targets: list[Target], findings: list[dict],
                  passed: list[dict], na_rows: list[dict], unchecked_rows: list[dict],
                  conflicts: list[dict]) -> str:
    counts = {'blocker': 0, 'major': 0, 'minor': 0, 'info': 0}
    for f in findings:
        counts[f['severity']] = counts.get(f['severity'], 0) + 1
    verdict = 'FAIL' if counts['blocker'] or counts['major'] else 'PASS'
    out: list[str] = []
    out.append('徽章系统审查 · ' + ', '.join(t.rel() for t in targets))
    head = profile.get('profile') or {}
    out.append('profile：' + str(head.get('name', '?')) + ' @ ' + str(head.get('version', '?')))
    out.append('规则 ' + str(len(passed) + len(na_rows) + len(unchecked_rows)) + ' 条，扫描文件 ' + str(len(targets)) + ' 个，检查元素 ' + str(sum(p.get('checked', 0) for p in passed)) + ' 处，未检查规则 ' + str(len(unchecked_rows)) + ' 条')
    out.append('')
    out.append('== Findings（' + str(len(findings)) + ' 条）==')
    if not findings:
        out.append('  （无）')
    for f in sorted(findings, key=lambda x: (SEVERITY_ORDER.get(x['severity'], 9), x['file'], x['line'])):
        mark = {'blocker': '✗ blocker', 'major': '✗ major   ', 'minor': '· minor   ', 'info': '· info    '}.get(f['severity'], '·')
        out.append(mark + ' ' + f['rule'] + '  ' + f['message'])
        out.append('    ' + f['file'] + ':' + str(f['line']) + '  ' + f['detail'])
        out.append('    违反「' + f['source_ref'] + '」' + (f['text'] or ''))
        if f['fix']:
            out.append('    改法：' + f['fix'])
        out.append('')
    out.append('== 已合规（检查过且无违规）==')
    for p in passed:
        out.append('  ✓ ' + p['rule'] + '（命中 ' + str(p['checked']) + ' 处）')
    if not passed:
        out.append('  （无）')
    out.append('')
    out.append('== N/A（未覆盖，不算通过）==')
    for n in na_rows:
        out.append('  - ' + n['rule'] + '：' + '；'.join(n['reasons']))
    if not na_rows:
        out.append('  （无）')
    out.append('')
    out.append('== 未检查（解析失败/无法判定，不算通过）==')
    for u in unchecked_rows:
        out.append('  - ' + u['rule'] + '（已检查 ' + str(u.get('checked', 0)) + ' 处）：' + '；'.join(u['reasons']))
    if not unchecked_rows:
        out.append('  （无）')
    if conflicts:
        out.append('')
        out.append('== 待裁决冲突（不得静默选边）==')
        for c in conflicts:
            status = str(c.get('resolution', 'pending'))
            out.append('  ! ' + str(c.get('id', '?')) + ' ' + str(c.get('topic', '')) + ' · resolution=' + status + ' · interim=' + str(c.get('interim', '')))
            for claim in (c.get('claims') or []):
                out.append('      · ' + str(claim.get('text', '')) + ' ← ' + str(claim.get('source_ref', '')))
    out.append('')
    out.append('结论：' + verdict + ' · blocker ' + str(counts['blocker']) + ' / major ' + str(counts['major']) + ' / minor ' + str(counts['minor']))
    return '\n'.join(out)


def _configure_streams() -> None:
    '''强制 stdout/stderr 用 UTF-8，避免 Windows GBK 控制台输出中文时崩溃或乱码。'''
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):
            pass


def main(argv: list[str] | None = None) -> int:
    _configure_streams()
    ap = argparse.ArgumentParser(
        prog='badge_lint.py',
        description='profile 驱动的徽章系统审查：按规范条款扫描 HTML/CSS/TSX，输出 file:line 级 findings。',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='退出码：0=PASS；1=检出 blocker/major；2=用法/解析/目标错误。',
    )
    ap.add_argument('--profile', required=True, help='profile YAML 路径')
    ap.add_argument('--target', action='append', default=[], help='扫描目标（文件或目录），可重复')
    ap.add_argument('--include', default=','.join(DEFAULT_INCLUDE), help='目录扫描的扩展名过滤，逗号分隔')
    ap.add_argument('--format', choices=('text', 'json'), default='text')
    ap.add_argument('--out', help='同时把报告写入文件')
    ap.add_argument('--rules', action='store_true', help='只打印规则清单，不扫描')
    args = ap.parse_args(argv)

    try:
        profile = load_profile(args.profile)
    except LintError as exc:
        print('错误：' + str(exc), file=sys.stderr)
        return EXIT_ERROR

    rules_raw = profile.get('rules') or []
    if not isinstance(rules_raw, list):
        print('错误：profile.rules 必须是列表', file=sys.stderr)
        return EXIT_ERROR
    rules = [r for r in rules_raw if isinstance(r, dict)]
    conflicts = [c for c in (profile.get('conflicts') or []) if isinstance(c, dict)]
    tokens = profile.get('tokens') or {}
    token_color = tokens.get('color') or {}

    if args.rules:
        for r in rules:
            kind = str((r.get('check') or {}).get('kind', '?'))
            print(r.get('id', '?') + '\t' + kind + '\t' + str(r.get('severity', 'major')) + '\t' + str(r.get('source_ref', '')))
        return EXIT_OK

    if not args.target:
        print('错误：需要至少一个 --target（或用 --rules 只看清单）', file=sys.stderr)
        return EXIT_ERROR

    try:
        include = {e.strip().lstrip('.').lower() for e in args.include.split(',') if e.strip()}
        files = _collect_targets(args.target, {'.' + e for e in include}, Path.cwd())
    except LintError as exc:
        print('错误：' + str(exc), file=sys.stderr)
        return EXIT_ERROR

    files = [p.resolve() for p in files]
    root = _common_root(files)

    targets: list[Target] = []
    for f in files:
        try:
            targets.append(Target(f, root))
        except OSError as exc:
            print('警告：跳过无法读取的 ' + _rel(f, root) + '（' + str(exc) + '）', file=sys.stderr)

    findings: list[dict] = []
    passed: list[dict] = []
    na_rows: list[dict] = []
    unchecked_rows: list[dict] = []
    for rule in rules:
        rid = str(rule.get('id', '?'))
        try:
            got, checked, na, skipped = run_check(rule, targets, token_color)
        except Exception as exc:  # 单条规则失败不拖垮全局
            na_rows.append({'rule': rid, 'reasons': ['执行异常：' + str(exc)]})
            continue
        findings.extend(got)
        skipped = list(dict.fromkeys(skipped))
        if na:
            na_rows.append({'rule': rid, 'reasons': na})
        elif skipped:
            # 有解析失败或无法判定的部分：该规则不得计入 passed
            unchecked_rows.append({'rule': rid, 'checked': checked, 'reasons': skipped})
        elif checked == 0:
            na_rows.append({'rule': rid, 'reasons': ['目标中未命中相关元素']})
        else:
            passed.append({'rule': rid, 'checked': checked})

    if args.format == 'json':
        counts = {'blocker': 0, 'major': 0, 'minor': 0, 'info': 0}
        for f in findings:
            counts[f['severity']] = counts.get(f['severity'], 0) + 1
        verdict = 'FAIL' if counts['blocker'] or counts['major'] else 'PASS'
        payload = {
            'profile': {'name': _head(profile).get('name'), 'version': _head(profile).get('version')},
            'targets': [t.rel() for t in targets],
            'findings': findings,
            'passed': passed,
            'na': na_rows,
            'unchecked': unchecked_rows,
            'conflicts': conflicts,
            'summary': {
                'blocker': counts['blocker'],
                'major': counts['major'],
                'minor': counts['minor'],
                'rules_total': len(rules),
                'rules_passed': len(passed),
                'rules_na': len(na_rows),
                'rules_unchecked': len(unchecked_rows),
                'unchecked_items': sum(len(u.get('reasons') or []) for u in unchecked_rows),
                'verdict': verdict,
            },
        }
        text = json.dumps(payload, ensure_ascii=False, indent=2)
    else:
        text = _report_text(profile, targets, findings, passed, na_rows, unchecked_rows, conflicts)

    if args.out:
        try:
            Path(args.out).write_text(text + '\n', encoding='utf-8')
        except OSError as exc:
            print('错误：写报告失败：' + str(exc), file=sys.stderr)
            return EXIT_ERROR
        if args.format == 'text':
            print(text)
        print('报告已写入 ' + args.out)
    else:
        print(text)

    counts = {'blocker': 0, 'major': 0}
    for f in findings:
        if f['severity'] in counts:
            counts[f['severity']] += 1
    return EXIT_FAIL if (counts['blocker'] or counts['major']) else EXIT_OK


if __name__ == '__main__':
    sys.exit(main())
