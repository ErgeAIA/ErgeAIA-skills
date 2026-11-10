"""受限 YAML 子集解析器（badge_lint 专用，仅标准库）。

支持：
- 块状 mapping / sequence（空格缩进）
- 行内 mapping {a: b, c: d} 与 sequence [a, b]（可嵌套）
- 双引号字符串（含常见转义）、单引号字符串（两个单引号转义）
- 裸标量、整数、浮点、true/false、null/~
- 行尾 # 注释（引号内的 # 不算注释）

不支持（遇到即抛 YamlSubsetError 并附行号，CLI 以 exit 2 结束）：
块状标量（竖线 / 大于号）、锚点 / 别名 / 标签、
制表符缩进、跨行行内值、复杂键。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

__all__ = ["YamlSubsetError", "parse_yaml", "load_yaml"]


class YamlSubsetError(Exception):
    """受限 YAML 子集无法解析（带 1 基行号）。"""

    def __init__(self, line: int, message: str) -> None:
        self.line = line
        self.message = message
        super().__init__(f"第 {line} 行：{message}")


_INT_RE = re.compile(r"^[+-]?\d+$")
_FLOAT_RE = re.compile(r"^[+-]?(?:\d+\.\d*|\.\d+|\d+(?:[eE][+-]?\d+))$")
_TRUE = {"true", "True", "TRUE"}
_FALSE = {"false", "False", "FALSE"}
_NULL = {"null", "Null", "NULL", "~", ""}


def _convert_scalar(text: str) -> Any:
    s = text.strip()
    if s in _NULL:
        return None
    if s in _TRUE:
        return True
    if s in _FALSE:
        return False
    if _INT_RE.match(s):
        return int(s)
    if _FLOAT_RE.match(s):
        return float(s)
    return s


def _split_comment(line: str) -> str:
    """去掉行尾注释；引号内的 # 保留。"""
    out: list[str] = []
    quote: str | None = None
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if quote:
            out.append(ch)
            if quote == '"' and ch == "\\" and i + 1 < n:
                out.append(line[i + 1])
                i += 2
                continue
            if ch == quote:
                if quote == "'" and i + 1 < n and line[i + 1] == "'":
                    out.append("'")
                    i += 2
                    continue
                quote = None
            i += 1
            continue
        if ch in "\"'":
            quote = ch
            out.append(ch)
            i += 1
            continue
        if ch == "#" and (not out or out[-1] in " \t"):
            break
        out.append(ch)
        i += 1
    return "".join(out)


_ESCAPES = {
    "n": "\n",
    "t": "\t",
    "r": "\r",
    '"': '"',
    "\\": "\\",
    "0": "\0",
    "/": "/",
    "b": "\b",
    "f": "\f",
    " ": " ",
}


class _FlowParser:
    """单行行内值解析：{...} / [...] / 引号字符串 / 裸标量。"""

    def __init__(self, text: str, line: int) -> None:
        self.text = text
        self.line = line
        self.i = 0
        self.n = len(text)

    def _err(self, message: str) -> None:
        raise YamlSubsetError(self.line, message)

    def _skip_ws(self) -> None:
        while self.i < self.n and self.text[self.i] in " \t":
            self.i += 1

    def parse_all(self) -> Any:
        self._skip_ws()
        value = self._parse_value()
        self._skip_ws()
        if self.i != self.n:
            self._err(f"行内值后存在无法解析的内容：{self.text[self.i:]!r}")
        return value

    def _parse_value(self) -> Any:
        self._skip_ws()
        if self.i >= self.n:
            self._err("行内值缺失")
        ch = self.text[self.i]
        if ch == "{":
            return self._parse_map()
        if ch == "[":
            return self._parse_list()
        if ch == '"':
            return self._parse_double()
        if ch == "'":
            return self._parse_single()
        if ch in "|>":
            self._err("不支持块状标量")
        if ch in "&*!":
            self._err("不支持锚点 / 别名 / 标签")
        return self._parse_plain(",}]")

    def _parse_plain(self, stop: str) -> Any:
        start = self.i
        while self.i < self.n and self.text[self.i] not in stop:
            self.i += 1
        raw = self.text[start:self.i].strip()
        if raw == "":
            self._err("行内值为空")
        return _convert_scalar(raw)

    def _parse_key(self) -> str:
        self._skip_ws()
        if self.i >= self.n:
            self._err("行内映射缺少键")
        ch = self.text[self.i]
        if ch == '"':
            value = self._parse_double()
        elif ch == "'":
            value = self._parse_single()
        else:
            start = self.i
            while self.i < self.n and self.text[self.i] not in ":":
                self.i += 1
            raw = self.text[start:self.i].strip()
            if raw == "":
                self._err("行内映射缺少键")
            value = _convert_scalar(raw)
        return value if isinstance(value, str) else str(value)

    def _parse_map(self) -> dict[str, Any]:
        self.i += 1
        result: dict[str, Any] = {}
        self._skip_ws()
        if self.i < self.n and self.text[self.i] == "}":
            self.i += 1
            return result
        while True:
            key = self._parse_key()
            self._skip_ws()
            if self.i >= self.n or self.text[self.i] != ":":
                self._err(f"行内映射缺少冒号：{key!r}")
            self.i += 1
            value = self._parse_value()
            result[key] = value
            self._skip_ws()
            if self.i >= self.n:
                self._err("行内映射未闭合（缺少右花括号）")
            ch = self.text[self.i]
            if ch == ",":
                self.i += 1
                self._skip_ws()
                if self.i < self.n and self.text[self.i] == "}":
                    self.i += 1
                    return result
                continue
            if ch == "}":
                self.i += 1
                return result
            self._err(f"行内映射中出现意外字符：{ch!r}")

    def _parse_list(self) -> list[Any]:
        self.i += 1
        items: list[Any] = []
        self._skip_ws()
        if self.i < self.n and self.text[self.i] == "]":
            self.i += 1
            return items
        while True:
            items.append(self._parse_value())
            self._skip_ws()
            if self.i >= self.n:
                self._err("行内序列未闭合（缺少右方括号）")
            ch = self.text[self.i]
            if ch == ",":
                self.i += 1
                self._skip_ws()
                if self.i < self.n and self.text[self.i] == "]":
                    self.i += 1
                    return items
                continue
            if ch == "]":
                self.i += 1
                return items
            self._err(f"行内序列中出现意外字符：{ch!r}")

    def _parse_double(self) -> str:
        self.i += 1
        out: list[str] = []
        while self.i < self.n:
            ch = self.text[self.i]
            if ch == '"':
                self.i += 1
                return "".join(out)
            if ch == "\\":
                self.i += 1
                if self.i >= self.n:
                    self._err("双引号字符串以反斜杠结尾")
                esc = self.text[self.i]
                if esc in _ESCAPES:
                    out.append(_ESCAPES[esc])
                    self.i += 1
                    continue
                if esc in "xuU":
                    width = {"x": 2, "u": 4, "U": 8}[esc]
                    raw = self.text[self.i + 1 : self.i + 1 + width]
                    if len(raw) != width or not re.fullmatch(r"[0-9a-fA-F]+", raw):
                        self._err(f"非法反斜杠转义：{esc}")
                    try:
                        out.append(chr(int(raw, 16)))
                    except ValueError:
                        self._err(f"非法反斜杠转义：{esc}")
                    self.i += 1 + width
                    continue
                self._err(f"不支持的反斜杠转义：{esc}")
            out.append(ch)
            self.i += 1
        self._err("双引号字符串未闭合")

    def _parse_single(self) -> str:
        self.i += 1
        out: list[str] = []
        while self.i < self.n:
            ch = self.text[self.i]
            if ch == "'":
                if self.i + 1 < self.n and self.text[self.i + 1] == "'":
                    out.append("'")
                    self.i += 2
                    continue
                self.i += 1
                return "".join(out)
            out.append(ch)
            self.i += 1
        self._err("单引号字符串未闭合")


class _BlockParser:
    def __init__(self, text: str) -> None:
        self.lines = self._prepare(text)
        self.i = 0

    @staticmethod
    def _prepare(text: str) -> list[tuple[int, int, str]]:
        lines: list[tuple[int, int, str]] = []
        for ln, raw in enumerate(text.splitlines(), 1):
            leading = raw[: len(raw) - len(raw.lstrip(" \t"))]
            if "\t" in leading:
                raise YamlSubsetError(ln, "缩进包含制表符（只支持空格）")
            content = _split_comment(raw).rstrip()
            if not content.strip():
                continue
            indent = len(content) - len(content.lstrip(" "))
            body = content.strip()
            if body in ("---", "...") and indent == 0:
                continue
            lines.append((ln, indent, body))
        return lines

    def parse(self) -> Any:
        if not self.lines:
            raise YamlSubsetError(1, "YAML 内容为空")
        value, i = self._parse_block(0, self.lines[0][1])
        if i != len(self.lines):
            ln = self.lines[i][0]
            raise YamlSubsetError(ln, "缩进不一致或存在多余的顶层内容")
        return value

    def _parse_block(self, i: int, indent: int) -> tuple[Any, int]:
        ln, ind, text = self.lines[i]
        if ind != indent:
            raise YamlSubsetError(ln, "缩进不一致")
        if text == "-" or text.startswith("- "):
            return self._parse_seq(i, indent)
        return self._parse_map(i, indent)

    def _parse_seq(self, i: int, indent: int) -> tuple[list[Any], int]:
        items: list[Any] = []
        while i < len(self.lines):
            ln, ind, text = self.lines[i]
            if ind < indent:
                break
            if ind > indent:
                raise YamlSubsetError(ln, "缩进不一致")
            if not (text == "-" or text.startswith("- ")):
                break
            rest = text[1:].strip()
            if rest == "":
                nxt = i + 1
                if nxt < len(self.lines) and self.lines[nxt][1] > indent:
                    value, i = self._parse_block(nxt, self.lines[nxt][1])
                else:
                    value = None
                    i += 1
            elif rest[0] in "{[":
                value = self._parse_inline(rest, ln)
                i += 1
                self._forbid_deeper(i, indent)
            elif rest[0] in "|>":
                raise YamlSubsetError(ln, "不支持块状标量")
            elif rest[0] in "&*!":
                raise YamlSubsetError(ln, "不支持锚点 / 别名 / 标签")
            elif self._try_split_key(rest, ln) is not None:
                after_dash = text[1:]
                ws = len(after_dash) - len(after_dash.lstrip(" "))
                key_col = indent + 1 + ws
                value, i = self._parse_map(i + 1, key_col, first=(ln, rest))
            else:
                value = self._parse_inline(rest, ln)
                i += 1
                self._forbid_deeper(i, indent)
            items.append(value)
        return items, i

    def _parse_map(
        self,
        i: int,
        indent: int,
        first: tuple[int, str] | None = None,
    ) -> tuple[dict[str, Any], int]:
        result: dict[str, Any] = {}
        if first is not None:
            ln, text = first
            i = self._parse_pair(result, ln, text, indent, i)
        while i < len(self.lines):
            ln, ind, text = self.lines[i]
            if ind < indent:
                break
            if ind > indent:
                raise YamlSubsetError(ln, "缩进不一致")
            if text == "-" or text.startswith("- "):
                raise YamlSubsetError(ln, "同一层不允许映射键与列表项混用")
            i = self._parse_pair(result, ln, text, indent, i + 1)
        return result, i

    def _parse_pair(
        self,
        result: dict[str, Any],
        ln: int,
        text: str,
        indent: int,
        next_i: int,
    ) -> int:
        split = self._try_split_key(text, ln)
        if split is None:
            raise YamlSubsetError(ln, f"无法解析映射项：{text!r}")
        key, rest = split
        if rest == "":
            if next_i < len(self.lines) and self.lines[next_i][1] > indent:
                value, after = self._parse_block(next_i, self.lines[next_i][1])
            else:
                value = None
                after = next_i
        else:
            value = self._parse_inline(rest, ln)
            if next_i < len(self.lines) and self.lines[next_i][1] > indent:
                bad_ln = self.lines[next_i][0]
                raise YamlSubsetError(
                    bad_ln, "键的内联值之后出现更深缩进（不支持多行标量 / 隐式续行）"
                )
            after = next_i
        result[key] = value
        return after

    def _try_split_key(self, text: str, ln: int) -> tuple[str, str] | None:
        quote: str | None = None
        depth = 0
        i = 0
        n = len(text)
        while i < n:
            ch = text[i]
            if quote:
                if ch == "\\" and quote == '"' and i + 1 < n:
                    i += 2
                    continue
                if ch == quote:
                    if quote == "'" and i + 1 < n and text[i + 1] == "'":
                        i += 2
                        continue
                    quote = None
                i += 1
                continue
            if ch in "\"'":
                quote = ch
                i += 1
                continue
            if ch in "[{":
                depth += 1
                i += 1
                continue
            if ch in "]}":
                depth -= 1
                i += 1
                continue
            if ch == ":" and depth == 0:
                if i + 1 == n or text[i + 1] in " \t":
                    raw_key = text[:i].strip()
                    if raw_key == "":
                        raise YamlSubsetError(ln, "映射键为空")
                    if raw_key[0] in "\"'":
                        key = _FlowParser(raw_key, ln).parse_all()
                        key = key if isinstance(key, str) else str(key)
                    else:
                        key = raw_key
                    return key, text[i + 1 :].strip()
                i += 1
                continue
            i += 1
        return None

    def _parse_inline(self, rest: str, ln: int) -> Any:
        if rest[0] in "{[" or rest[0] in "\"'":
            return _FlowParser(rest, ln).parse_all()
        if rest[0] in "|>":
            raise YamlSubsetError(ln, "不支持块状标量")
        if rest[0] in "&*!":
            raise YamlSubsetError(ln, "不支持锚点 / 别名 / 标签")
        if rest.startswith("- "):
            raise YamlSubsetError(ln, "块状映射的值不能是行内列表项")
        return _convert_scalar(rest)

    def _forbid_deeper(self, i: int, indent: int) -> None:
        if i < len(self.lines) and self.lines[i][1] > indent:
            ln = self.lines[i][0]
            raise YamlSubsetError(ln, "缩进不一致（不支持多行标量 / 隐式续行）")


def parse_yaml(text: str) -> Any:
    """解析受限 YAML 文本；失败抛 YamlSubsetError。"""
    return _BlockParser(text).parse()


def load_yaml(path: str | Path) -> Any:
    """读取并解析 UTF-8 YAML 文件；IO 异常原样抛出。"""
    p = Path(path)
    data = p.read_bytes()
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise YamlSubsetError(1, f"profile 不是合法 UTF-8 文本：{exc}") from exc
    return parse_yaml(text)
