#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iconlab.py — lucide 图标目录、16px 描边剪影度量与离线对比页。

数据源只认本地 lucide-static 解包目录（icon-nodes.json / tags.json / package.json），
运行期不联网。四个子命令：

  catalog  从 lucide-static 解包目录生成紧凑目录 data/lucide-catalog.json
  search   基于真实 tags + id 词检索候选图标（内置可扩充的中文意图别名表）
  measure  按 lucide stroke 语义栅格化，输出两两 IoU / 墨量比 / 邻近混淆风险
  render   读取 case.yaml，产出单文件离线 HTML 对比页

退出码：0 = 成功；1 = 检出失败或校验失败；2 = 用法或内部错误。

依赖：Python 3.10+ 标准库；无第三方包。
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_CATALOG = SKILL_DIR / "data" / "lucide-catalog.json"

VIEWBOX = 24.0
STROKE_DEFAULT = 2.25
SUPERSAMPLE_DEFAULT = 8
INK_THRESHOLD_DEFAULT = 0.5
RISK_IOU = 0.75
CATALOG_MAX_BYTES = 1_500_000


class IconlabError(Exception):
    """带退出码的可读错误。"""

    def __init__(self, message: str, code: int = 2):
        super().__init__(message)
        self.message = message
        self.code = code


# --------------------------------------------------------------------------- #
# 通用 I/O
# --------------------------------------------------------------------------- #

def _configure_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def _load_json(path: Path, what: str):
    if not path.is_file():
        raise IconlabError(f"未找到{what}：{path}", 2)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise IconlabError(f"{what}不是合法 JSON：{path}（{exc}）", 2)
    except OSError as exc:
        raise IconlabError(f"读取{what}失败：{path}（{exc}）", 2)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _esc(text) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _disp_width(text: str) -> int:
    import unicodedata  # 惰性导入：只有终端对齐报表才用，省 CLI 启动时的固定开销
    width = 0
    for char in str(text):
        width += 2 if unicodedata.east_asian_width(char) in ("W", "F") else 1
    return width


def _pad(text: str, width: int) -> str:
    text = str(text)
    return text + " " * max(0, width - _disp_width(text))


def _truncate_display(text: str, width: int) -> str:
    import unicodedata  # 惰性导入，理由同 _disp_width
    text = str(text)
    if _disp_width(text) <= width:
        return text
    out = []
    used = 0
    for char in text:
        step = 2 if unicodedata.east_asian_width(char) in ("W", "F") else 1
        if used + step > width - 1:
            break
        out.append(char)
        used += step
    return "".join(out) + "…"


def _print_table(headers, rows) -> None:
    headers = [str(item) for item in headers]
    rows = [[str(cell) for cell in row] for row in rows]
    widths = [_disp_width(item) for item in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], _disp_width(cell))
    print("  ".join(_pad(item, widths[index]) for index, item in enumerate(headers)).rstrip())
    print("  ".join("-" * widths[index] for index in range(len(headers))))
    for row in rows:
        print("  ".join(_pad(cell, widths[index]) for index, cell in enumerate(row)).rstrip())


def _catalog_source_line(source: dict) -> str:
    return (
        f"{source.get('library', 'lucide-static')}@{source.get('version', 'unknown')}"
        f" · {source.get('icon_count', '?')} 个图标 · {source.get('license', '?')}"
        f" · 生成于 {source.get('generated_at', '?')}"
    )


def load_catalog(path: Path) -> dict:
    if not path.is_file():
        raise IconlabError(
            "未找到图标目录：" + str(path) + "\n"
            "请先运行：\n"
            "  PYTHONIOENCODING=utf-8 uv run --no-project python scripts/iconlab.py "
            "catalog --from <lucide-static 解包根目录> --out data/lucide-catalog.json",
            2,
        )
    doc = _load_json(path, "图标目录")
    if not isinstance(doc, dict):
        raise IconlabError(f"目录结构无效（顶层不是对象）：{path}", 2)
    source = doc.get("source")
    icons = doc.get("icons")
    if not isinstance(source, dict) or not isinstance(icons, dict) or not icons:
        raise IconlabError(f"目录结构无效（缺 source/icons）：{path}", 2)
    for icon_id, entry in icons.items():
        if not isinstance(entry, dict) or not isinstance(entry.get("n"), list):
            raise IconlabError(f"目录结构无效（图标 {icon_id} 缺 n）：{path}", 2)
    return doc


def _catalog_tag_coverage(icons: dict) -> tuple[int, int]:
    covered = sum(1 for entry in icons.values() if entry.get("t"))
    return covered, len(icons)


# --------------------------------------------------------------------------- #
# catalog
# --------------------------------------------------------------------------- #

def cmd_catalog(args) -> int:
    src = Path(args.from_dir)
    if not src.is_dir():
        raise IconlabError(f"--from 不是目录：{src}", 2)
    nodes_path = src / "icon-nodes.json"
    tags_path = src / "tags.json"
    pkg_path = src / "package.json"
    missing = [str(path) for path in (nodes_path, tags_path, pkg_path) if not path.is_file()]
    if missing:
        raise IconlabError("lucide-static 目录缺少文件：" + "、".join(missing), 2)

    nodes = _load_json(nodes_path, "icon-nodes.json")
    tags = _load_json(tags_path, "tags.json")
    package = _load_json(pkg_path, "package.json")
    if not isinstance(nodes, dict) or not nodes:
        raise IconlabError("icon-nodes.json 结构无效（应为 {id: [[tag, attrs], ...]}）", 2)
    if not isinstance(tags, dict):
        raise IconlabError("tags.json 结构无效（应为 {id: [tags]}）", 2)
    if not isinstance(package, dict):
        raise IconlabError("package.json 结构无效", 2)

    icons: dict[str, dict] = {}
    for icon_id in sorted(nodes):
        raw_nodes = nodes[icon_id]
        if not isinstance(raw_nodes, list) or not raw_nodes:
            raise IconlabError(f"图标 {icon_id} 的节点列表无效", 2)
        clean_nodes = []
        for item in raw_nodes:
            if (
                not isinstance(item, list)
                or len(item) != 2
                or not isinstance(item[0], str)
                or not isinstance(item[1], dict)
            ):
                raise IconlabError(f"图标 {icon_id} 的节点格式无效：{item!r}", 2)
            clean_nodes.append(item)
        raw_tags = tags.get(icon_id, [])
        if not isinstance(raw_tags, list):
            raise IconlabError(f"图标 {icon_id} 的 tags 无效", 2)
        clean_tags = [str(tag) for tag in raw_tags]
        icons[icon_id] = {"t": clean_tags, "n": clean_nodes}

    version = str(package.get("version") or "unknown")
    license_name = str(package.get("license") or "ISC")
    generated_at = date.today().isoformat()
    doc = {
        "source": {
            "library": "lucide-static",
            "version": version,
            "license": license_name,
            "generated_at": generated_at,
            "icon_count": len(icons),
        },
        "icons": icons,
    }
    out = Path(args.out)
    payload = json.dumps(doc, ensure_ascii=False, separators=(",", ":"))
    _write_text(out, payload)
    size = out.stat().st_size
    covered, total = _catalog_tag_coverage(icons)

    print("iconlab catalog · 完成")
    print(f"  来源目录：{src}")
    print(f"  数据版本：lucide-static {version}（{license_name}）")
    print(f"  图标数量：{len(icons)}")
    print(f"  tags 覆盖：{covered}/{total}（{covered / total * 100:.1f}%）")
    print(f"  输出文件：{out.resolve()}（{size} 字节 / {size / 1024:.1f} KiB）")
    print(f"  generated_at：{generated_at}")

    if size > CATALOG_MAX_BYTES:
        print(
            f"错误：目录体积 {size} 字节超过上限 {CATALOG_MAX_BYTES} 字节（1.5MB 口径）。",
            file=sys.stderr,
        )
        return 1
    return 0


# --------------------------------------------------------------------------- #
# search：真实 tags + id 词 + 可扩充中文意图别名
# --------------------------------------------------------------------------- #

# 中文意图 -> 真实英文检索词（首个为主词，其后为次词）。可在此继续追加。
INTENT_ALIASES: dict[str, list[str]] = {
    # 位置 / 来源
    "本地": ["local", "offline", "disk", "storage", "hard-drive"],
    "离线": ["offline", "local", "cloud-off", "disconnect"],
    "内置": ["built-in", "internal", "package", "box"],
    "来源": ["source", "origin", "import", "download"],
    "手动": ["manual", "hand", "pointer"],
    "安装": ["install", "download", "package-plus", "package"],
    "卸载": ["uninstall", "remove", "package-minus", "trash"],
    "插件": ["plugin", "puzzle", "extension", "module", "package"],
    "扩展": ["extension", "plugin", "puzzle", "module"],
    "仓库": ["registry", "package", "archive", "box", "github"],
    "包": ["package", "box", "archive", "briefcase"],
    "磁盘": ["disk", "hard-drive", "storage", "database"],
    "存储": ["storage", "database", "archive", "box", "disk"],
    "文件夹": ["folder", "directory"],
    "文件": ["file", "document", "page"],
    "目录": ["folder", "directory", "list"],
    # 动作
    "删除": ["delete", "remove", "trash", "erase"],
    "移除": ["remove", "delete", "minus", "x"],
    "清除": ["clear", "erase", "x", "trash"],
    "更新": ["update", "refresh", "sync", "download"],
    "升级": ["upgrade", "update", "arrow-up", "cloud-download"],
    "刷新": ["refresh", "rotate", "sync", "reload"],
    "同步": ["sync", "refresh", "rotate", "repeat"],
    "复制": ["copy", "duplicate", "clipboard"],
    "移动": ["move", "arrow-left-right", "arrow-right"],
    "打开": ["open", "external-link", "folder-open", "eye"],
    "关闭": ["close", "x", "power"],
    "搜索": ["search", "find", "magnifier", "scan"],
    "查看": ["eye", "view", "search", "scan"],
    "下载": ["download", "arrow-down", "cloud-download"],
    "上传": ["upload", "arrow-up", "cloud-upload"],
    "分享": ["share", "send", "external-link"],
    "链接": ["link", "chain", "url"],
    # 状态
    "缺失": ["missing", "absent", "file-x", "unavailable"],
    "丢失": ["missing", "lost", "file-x", "unavailable"],
    "共享": ["share", "link", "external-link"],
    "待定": ["pending", "clock", "schedule", "timer"],
    "进行中": ["progress", "loader", "pending", "clock"],
    "完成": ["check", "circle-check", "done", "ok"],
    "成功": ["check", "circle-check", "ok", "badge-check"],
    "失败": ["x", "circle-x", "error", "fail"],
    "警告": ["alert", "warning", "triangle-alert"],
    "错误": ["error", "x", "alert", "ban"],
    "禁止": ["ban", "forbidden", "prohibited", "lock"],
    "锁定": ["lock", "locked", "shield"],
    "解锁": ["unlock", "lock-open"],
    "安全": ["shield", "lock", "key"],
    "未知": ["unknown", "question", "file-question"],
    "状态": ["status", "state", "check", "alert"],
    # 控件
    "筛选": ["filter", "funnel", "list-filter"],
    "计数": ["count", "hash", "list", "number"],
    "角标": ["badge", "dot", "circle"],
    "导航": ["nav", "menu", "arrow", "chevron"],
    "菜单": ["menu", "hamburger", "list"],
    "设置": ["settings", "gear", "sliders"],
    "用户": ["user", "person", "account"],
    "标签": ["tag", "label", "badge"],
    "时间": ["clock", "time", "calendar"],
    "日历": ["calendar", "date", "schedule"],
    "历史": ["history", "clock", "rotate-ccw"],
}

# 槽位偏向词（只做加权，不做硬过滤）。权重低于查询词。
SLOT_ALIASES: dict[str, list[str]] = {
    "source": ["source", "origin", "import", "download", "package", "folder", "hard-drive"],
    "status": ["check", "x", "alert", "clock", "circle-check", "file-x", "link", "shield"],
    "action": ["arrow", "trash", "copy", "folder-open", "link", "download", "upload", "refresh", "pencil"],
    "filter": ["filter", "funnel", "list-filter", "sliders"],
    "count": ["count", "hash", "list", "number", "badge"],
    "nav": ["arrow", "chevron", "menu", "home", "panel-left", "compass"],
}

SLOT_WEIGHT = 0.4


def _tokenize_query(query: str) -> list[tuple[str, str]]:
    """切成 (kind, text)：intent=别名词，ascii=英文词，unknown=未识别中文词。"""
    tokens: list[tuple[str, str]] = []
    index = 0
    length = len(query)
    alias_keys = sorted(INTENT_ALIASES.keys(), key=len, reverse=True)
    while index < length:
        char = query[index]
        if char.isspace() or char in ",，、;；/|":
            index += 1
            continue
        if char.isascii() and (char.isalnum() or char in "-_."):
            end = index
            while end < length:
                nxt = query[end]
                if not (nxt.isascii() and (nxt.isalnum() or nxt in "-_.")):
                    break
                end += 1
            tokens.append(("ascii", query[index:end].lower()))
            index = end
            continue
        matched = None
        for key in alias_keys:
            if query.startswith(key, index):
                matched = key
                break
        if matched:
            tokens.append(("intent", matched))
            index += len(matched)
        else:
            tokens.append(("unknown", char))
            index += 1
    return tokens


def _expand_query(tokens: list[tuple[str, str]], slot: str | None):
    weighted: dict[str, float] = {}
    sources: dict[str, list[str]] = {}
    unknown: list[str] = []
    intent_notes: list[tuple[str, list[str]]] = []

    def add(term: str, weight: float, source: str) -> None:
        current = weighted.get(term, 0.0)
        if weight > current:
            weighted[term] = weight
        sources.setdefault(term, [])
        if source not in sources[term]:
            sources[term].append(source)

    for kind, text in tokens:
        if kind == "intent":
            terms = INTENT_ALIASES[text]
            intent_notes.append((text, terms))
            for order, term in enumerate(terms):
                add(term, max(0.35, 1.0 - 0.12 * order), text)
        elif kind == "ascii":
            add(text, 1.0, text)
        else:
            if text.strip():
                unknown.append(text)

    if slot:
        for term in SLOT_ALIASES[slot]:
            add(term, SLOT_WEIGHT, f"槽位:{slot}")

    return weighted, sources, unknown, intent_notes


def _score_icon(icon_id: str, tags: list[str], weighted: dict[str, float], sources: dict[str, list[str]]):
    id_words = set(icon_id.split("-"))
    tag_set = set(tags)
    score = 0.0
    hit_id: set[str] = set()
    hit_tags: set[str] = set()
    hit_terms: set[str] = set()
    for term, weight in weighted.items():
        matched = False
        if term == icon_id:
            score += 14.0 * weight
            hit_id.add(term)
            matched = True
        elif term in id_words:
            score += 11.0 * weight
            hit_id.add(term)
            matched = True
        elif len(term) >= 3 and term in icon_id:
            score += 5.0 * weight
            hit_id.add(term)
            matched = True
        if term in tag_set:
            score += 8.0 * weight
            hit_tags.add(term)
            matched = True
        elif len(term) >= 3:
            partial = [tag for tag in tags if term in tag][:2]
            if partial:
                score += 2.8 * weight * len(partial)
                hit_tags.update(partial)
                matched = True
        if matched:
            for source in sources.get(term, []):
                if not source.startswith("槽位:"):
                    hit_terms.add(source)
    return round(score, 2), hit_id, hit_tags, hit_terms


def _match_reason(hit_id: set[str], hit_tags: set[str], hit_terms: set[str]) -> str:
    parts = []
    if hit_id:
        parts.append("id:" + ",".join(sorted(hit_id)))
    if hit_tags:
        parts.append("tag:" + ",".join(sorted(hit_tags)))
    if hit_terms:
        parts.append("词:" + ",".join(sorted(hit_terms)))
    return " · ".join(parts) if parts else "—"


def cmd_search(args) -> int:
    if not args.query.strip():
        raise IconlabError("--query 不能为空", 2)
    catalog_path = Path(args.catalog)
    doc = load_catalog(catalog_path)
    source = doc["source"]
    icons = doc["icons"]
    covered, total = _catalog_tag_coverage(icons)

    tokens = _tokenize_query(args.query)
    weighted, sources, unknown, intent_notes = _expand_query(tokens, args.slot)
    if not weighted:
        raise IconlabError(f"查询词无法识别为检索词：{args.query!r}（可改用英文 tag，如 delete/plugin）", 2)

    scored = []
    for icon_id, entry in icons.items():
        score, hit_id, hit_tags, hit_terms = _score_icon(icon_id, entry.get("t") or [], weighted, sources)
        if score <= 0:
            continue
        scored.append((score, icon_id, hit_id, hit_tags, hit_terms))
    scored.sort(key=lambda item: (-item[0], item[1]))
    top = scored[: args.top]

    if args.json:
        payload = {
            "source": source,
            "catalog": str(catalog_path.resolve()),
            "query": args.query,
            "slot": args.slot,
            "tokens": [
                {"text": text, "kind": kind, "terms": INTENT_ALIASES.get(text, [])}
                for kind, text in tokens
            ],
            "unknown_tokens": unknown,
            "results": [
                {
                    "rank": index + 1,
                    "id": icon_id,
                    "score": score,
                    "matched_id_words": sorted(hit_id),
                    "matched_tags": sorted(hit_tags),
                    "matched_terms": sorted(hit_terms),
                    "reason": _match_reason(hit_id, hit_tags, hit_terms),
                }
                for index, (score, icon_id, hit_id, hit_tags, hit_terms) in enumerate(top)
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"iconlab search · 查询「{args.query}」")
    print(f"目录：{_catalog_source_line(source)}")
    print(f"覆盖：tags {covered}/{total}（{covered / total * 100:.1f}%）· 检索口径：真实 tags + id 词")
    if intent_notes:
        notes = "；".join(f"{word} → {'/'.join(terms)}" for word, terms in intent_notes)
        print(f"词表：{notes}")
    if args.slot:
        bias = "/".join(SLOT_ALIASES[args.slot])
        print(f"槽位偏向：{args.slot}（附加 {bias}，权重 {SLOT_WEIGHT}）")
    if unknown:
        print(f"未识别词：{'、'.join(unknown)}（已忽略；可改用英文 tag）", file=sys.stderr)
    print()

    if not top:
        print(f"无命中：查询「{args.query}」在当前目录没有分数 > 0 的图标。")
        print("建议：改用英文 tag（如 delete / plugin / observe）、缩短查询、或检查 --slot 是否过窄。")
        return 0

    rows = []
    for index, (score, icon_id, hit_id, hit_tags, hit_terms) in enumerate(top):
        rows.append(
            [
                index + 1,
                icon_id,
                f"{score:g}",
                _truncate_display(_match_reason(hit_id, hit_tags, hit_terms), 78),
            ]
        )
    _print_table(["排名", "图标 id", "分数", "命中（tag/词）"], rows)
    return 0


# --------------------------------------------------------------------------- #
# 几何：SVG 元素 -> 折线；描边剪影栅格化
# --------------------------------------------------------------------------- #

_NUMBER_RE = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
_PATH_TOKEN_RE = re.compile(r"[MmZzLlHhVvCcSsQqTtAa]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
_CMD_CHARS = set("MmZzLlHhVvCcSsQqTtAa")


def _is_cmd(token: str) -> bool:
    return len(token) == 1 and token in _CMD_CHARS


def _float_attr(attrs: dict, key: str, default=None):
    value = attrs.get(key)
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        raise IconlabError(f"属性 {key} 不是数字：{value!r}", 1)


def _dist(p, q) -> float:
    return math.hypot(p[0] - q[0], p[1] - q[1])


def _sample_cubic(p0, p1, p2, p3, step=0.35, min_steps=6, max_steps=96):
    length = _dist(p0, p1) + _dist(p1, p2) + _dist(p2, p3)
    steps = int(min(max_steps, max(min_steps, math.ceil(length / step))))
    points = []
    for index in range(1, steps + 1):
        t = index / steps
        mt = 1.0 - t
        x = mt * mt * mt * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t * t * t * p3[0]
        y = mt * mt * mt * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t * t * t * p3[1]
        points.append((x, y))
    return points


def _sample_quadratic(p0, p1, p2, step=0.35, min_steps=4, max_steps=64):
    length = _dist(p0, p1) + _dist(p1, p2)
    steps = int(min(max_steps, max(min_steps, math.ceil(length / step))))
    points = []
    for index in range(1, steps + 1):
        t = index / steps
        mt = 1.0 - t
        x = mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0]
        y = mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]
        points.append((x, y))
    return points


def _sample_arc(p0, p1, rx, ry, rotation_deg, large_arc, sweep, max_angle=0.18):
    if p0 == p1:
        return []
    rx = abs(rx)
    ry = abs(ry)
    if rx < 1e-9 or ry < 1e-9:
        return [p1]
    phi = math.radians(rotation_deg % 360.0)
    cos_phi = math.cos(phi)
    sin_phi = math.sin(phi)
    dx = (p0[0] - p1[0]) / 2.0
    dy = (p0[1] - p1[1]) / 2.0
    x1p = cos_phi * dx + sin_phi * dy
    y1p = -sin_phi * dx + cos_phi * dy
    lam = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
    if lam > 1.0:
        scale = math.sqrt(lam)
        rx *= scale
        ry *= scale
    numerator = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    denominator = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    coef = math.sqrt(max(0.0, numerator / denominator)) if denominator else 0.0
    if bool(large_arc) == bool(sweep):
        coef = -coef
    cxp = coef * (rx * y1p / ry)
    cyp = coef * (-ry * x1p / rx)
    cx = cos_phi * cxp - sin_phi * cyp + (p0[0] + p1[0]) / 2.0
    cy = sin_phi * cxp + cos_phi * cyp + (p0[1] + p1[1]) / 2.0
    ux = (x1p - cxp) / rx
    uy = (y1p - cyp) / ry
    vx = (-x1p - cxp) / rx
    vy = (-y1p - cyp) / ry
    start = math.atan2(uy, ux)
    delta = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
    if not sweep and delta > 0:
        delta -= math.tau
    elif sweep and delta < 0:
        delta += math.tau
    steps = int(min(160, max(4, math.ceil(abs(delta) / max_angle))))
    points = []
    for index in range(1, steps + 1):
        theta = start + delta * index / steps
        ct = math.cos(theta)
        st = math.sin(theta)
        x = cx + rx * ct * cos_phi - ry * st * sin_phi
        y = cy + rx * ct * sin_phi + ry * st * cos_phi
        points.append((x, y))
    return points


def parse_path_polylines(d: str) -> list[list[tuple[float, float]]]:
    """把 SVG path 的 d 解析成折线列表（贝塞尔/圆弧按弦长采样，折线误差远小于 1/8 px）。"""
    tokens = _PATH_TOKEN_RE.findall(d or "")
    polylines: list[list[tuple[float, float]]] = []
    current: list[tuple[float, float]] | None = None
    pen: tuple[float, float] = (0.0, 0.0)
    start_point: tuple[float, float] | None = None
    previous_control = None
    previous_cmd = ""
    index = 0
    total = len(tokens)

    def flush() -> None:
        nonlocal current
        if current and len(current) >= 2:
            polylines.append(current)
        current = None

    def read_point(relative: bool) -> tuple[float, float]:
        nonlocal index
        if index + 1 >= total:
            raise IconlabError(f"path 数字不足：{d[:60]}", 1)
        x = float(tokens[index])
        y = float(tokens[index + 1])
        index += 2
        if relative:
            return (pen[0] + x, pen[1] + y)
        return (x, y)

    def begin() -> None:
        nonlocal current
        if current is None:
            current = [pen]

    cmd = ""
    while index < total:
        token = tokens[index]
        if _is_cmd(token):
            cmd = token
            index += 1
            if cmd in "Zz":
                if current:
                    current.append(start_point if start_point is not None else current[0])
                    flush()
                if start_point is not None:
                    pen = start_point
                previous_control = None
                previous_cmd = "Z"
                continue
        elif not cmd:
            raise IconlabError(f"path 数据缺少命令：{d[:60]}", 1)

        upper = cmd.upper()
        relative = cmd == cmd.lower()

        if upper == "M":
            first = True
            while index < total and not _is_cmd(tokens[index]):
                point = read_point(relative)
                if first:
                    if current:
                        flush()
                    current = [point]
                    start_point = point
                    first = False
                else:
                    current.append(point)
                pen = point
                previous_control = None
                previous_cmd = "M"
            cmd = "l" if relative else "L"
        elif upper == "L":
            while index < total and not _is_cmd(tokens[index]):
                begin()
                point = read_point(relative)
                current.append(point)
                pen = point
                previous_control = None
                previous_cmd = "L"
        elif upper == "H":
            while index < total and not _is_cmd(tokens[index]):
                value = float(tokens[index])
                index += 1
                begin()
                point = (pen[0] + value, pen[1]) if relative else (value, pen[1])
                current.append(point)
                pen = point
                previous_control = None
                previous_cmd = "H"
        elif upper == "V":
            while index < total and not _is_cmd(tokens[index]):
                value = float(tokens[index])
                index += 1
                begin()
                point = (pen[0], pen[1] + value) if relative else (pen[0], value)
                current.append(point)
                pen = point
                previous_control = None
                previous_cmd = "V"
        elif upper == "C":
            while index < total and not _is_cmd(tokens[index]):
                if index + 5 >= total:
                    raise IconlabError(f"path C 参数不足：{d[:60]}", 1)
                c1 = _read_xy(tokens, index, relative, pen)
                c2 = _read_xy(tokens, index + 2, relative, pen)
                end = _read_xy(tokens, index + 4, relative, pen)
                index += 6
                begin()
                current.extend(_sample_cubic(pen, c1, c2, end))
                pen = end
                previous_control = c2
                previous_cmd = "C"
        elif upper == "S":
            while index < total and not _is_cmd(tokens[index]):
                if index + 3 >= total:
                    raise IconlabError(f"path S 参数不足：{d[:60]}", 1)
                base = pen
                c2 = _read_xy(tokens, index, relative, base)
                end = _read_xy(tokens, index + 2, relative, base)
                index += 4
                if previous_cmd in ("C", "S") and previous_control is not None:
                    c1 = (2 * base[0] - previous_control[0], 2 * base[1] - previous_control[1])
                else:
                    c1 = base
                begin()
                current.extend(_sample_cubic(pen, c1, c2, end))
                pen = end
                previous_control = c2
                previous_cmd = "S"
        elif upper == "Q":
            while index < total and not _is_cmd(tokens[index]):
                if index + 3 >= total:
                    raise IconlabError(f"path Q 参数不足：{d[:60]}", 1)
                base = pen
                c1 = _read_xy(tokens, index, relative, base)
                end = _read_xy(tokens, index + 2, relative, base)
                index += 4
                begin()
                current.extend(_sample_quadratic(pen, c1, end))
                pen = end
                previous_control = c1
                previous_cmd = "Q"
        elif upper == "T":
            while index < total and not _is_cmd(tokens[index]):
                if index + 1 >= total:
                    raise IconlabError(f"path T 参数不足：{d[:60]}", 1)
                base = pen
                end = _read_xy(tokens, index, relative, base)
                index += 2
                if previous_cmd in ("Q", "T") and previous_control is not None:
                    c1 = (2 * base[0] - previous_control[0], 2 * base[1] - previous_control[1])
                else:
                    c1 = base
                begin()
                current.extend(_sample_quadratic(pen, c1, end))
                pen = end
                previous_control = c1
                previous_cmd = "T"
        elif upper == "A":
            while index < total and not _is_cmd(tokens[index]):
                if index + 6 >= total:
                    raise IconlabError(f"path A 参数不足：{d[:60]}", 1)
                rx = float(tokens[index])
                ry = float(tokens[index + 1])
                rotation = float(tokens[index + 2])
                large_arc = float(tokens[index + 3]) != 0
                sweep = float(tokens[index + 4]) != 0
                end = _read_xy(tokens, index + 5, relative, pen)
                index += 7
                begin()
                current.extend(_sample_arc(pen, end, rx, ry, rotation, large_arc, sweep))
                pen = end
                previous_control = None
                previous_cmd = "A"
        else:
            raise IconlabError(f"不支持的 path 命令：{cmd}", 1)
    flush()
    return polylines


def _read_xy(tokens, index, relative, base):
    x = float(tokens[index])
    y = float(tokens[index + 1])
    return (base[0] + x, base[1] + y) if relative else (x, y)


def _ellipse_arc_points(cx, cy, rx, ry, start_angle, end_angle, steps=12):
    points = []
    for index in range(1, steps + 1):
        angle = start_angle + (end_angle - start_angle) * index / steps
        points.append((cx + rx * math.cos(angle), cy + ry * math.sin(angle)))
    return points


def _circle_points(cx, cy, rx, ry, steps=72):
    return [(cx + rx * math.cos(math.tau * i / steps), cy + ry * math.sin(math.tau * i / steps)) for i in range(steps)]


def _parse_points(text: str):
    numbers = [float(item) for item in _NUMBER_RE.findall(text or "")]
    return list(zip(numbers[0::2], numbers[1::2]))


def element_polylines(tag: str, attrs: dict):
    """返回 (描边折线列表, 填充多边形列表)，坐标都在 24 视框内。"""
    strokes: list[list[tuple[float, float]]] = []
    fills: list[list[tuple[float, float]]] = []
    fill_value = attrs.get("fill")
    filled = fill_value is not None and str(fill_value) not in ("none", "transparent")

    if tag == "path":
        polylines = parse_path_polylines(str(attrs.get("d", "")))
        strokes.extend(polylines)
        if filled:
            for polyline in polylines:
                if len(polyline) >= 3:
                    fills.append(polyline)
    elif tag == "circle":
        cx = _float_attr(attrs, "cx", 0.0)
        cy = _float_attr(attrs, "cy", 0.0)
        r = _float_attr(attrs, "r", 0.0)
        points = _circle_points(cx, cy, r, r, 72)
        strokes.append(points + [points[0]])
        if filled:
            fills.append(points)
    elif tag == "ellipse":
        cx = _float_attr(attrs, "cx", 0.0)
        cy = _float_attr(attrs, "cy", 0.0)
        rx = _float_attr(attrs, "rx", 0.0)
        ry = _float_attr(attrs, "ry", 0.0)
        points = _circle_points(cx, cy, rx, ry, 72)
        strokes.append(points + [points[0]])
        if filled:
            fills.append(points)
    elif tag == "rect":
        x = _float_attr(attrs, "x", 0.0)
        y = _float_attr(attrs, "y", 0.0)
        width = _float_attr(attrs, "width", 0.0)
        height = _float_attr(attrs, "height", 0.0)
        rx = _float_attr(attrs, "rx", None)
        ry = _float_attr(attrs, "ry", None)
        if rx is None and ry is None:
            rx = ry = 0.0
        elif rx is None:
            rx = ry
        elif ry is None:
            ry = rx
        rx = min(abs(rx), width / 2.0)
        ry = min(abs(ry), height / 2.0)
        if rx <= 1e-9 or ry <= 1e-9:
            points = [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]
        else:
            points = [(x + rx, y), (x + width - rx, y)]
            points.extend(_ellipse_arc_points(x + width - rx, y + ry, rx, ry, -math.pi / 2, 0, 10))
            points.append((x + width, y + height - ry))
            points.extend(_ellipse_arc_points(x + width - rx, y + height - ry, rx, ry, 0, math.pi / 2, 10))
            points.append((x + rx, y + height))
            points.extend(_ellipse_arc_points(x + rx, y + height - ry, rx, ry, math.pi / 2, math.pi, 10))
            points.append((x, y + ry))
            points.extend(_ellipse_arc_points(x + rx, y + ry, rx, ry, math.pi, math.pi * 1.5, 10))
        points.append(points[0])
        strokes.append(points)
        if filled:
            fills.append(points[:-1])
    elif tag == "line":
        points = [
            (_float_attr(attrs, "x1", 0.0), _float_attr(attrs, "y1", 0.0)),
            (_float_attr(attrs, "x2", 0.0), _float_attr(attrs, "y2", 0.0)),
        ]
        strokes.append(points)
    elif tag in ("polyline", "polygon"):
        points = _parse_points(str(attrs.get("points", "")))
        if len(points) >= 2:
            strokes.append(points + ([points[0]] if tag == "polygon" else []))
        if filled and len(points) >= 3:
            fills.append(points)
    else:
        raise IconlabError(f"不支持的 SVG 元素：{tag}", 1)
    return strokes, fills


def flatten_icon(nodes):
    strokes: list[list[tuple[float, float]]] = []
    fills: list[list[tuple[float, float]]] = []
    for tag, attrs in nodes:
        item_strokes, item_fills = element_polylines(tag, attrs)
        strokes.extend(item_strokes)
        fills.extend(item_fills)
    return strokes, fills


def _stamp_capsule(buffer: bytearray, grid: int, ss: int, x0, y0, x1, y1, radius: float) -> None:
    """把「胶囊」（线段 + radius 圆头）栅格化进超采样缓冲。

    胶囊是凸集，同一行上的墨迹在 x 方向必为一段连续区间：按行解析求出该区间
    再整段填充，只在区间两端用逐像素判定校正浮点误差，结果与原逐像素判定一致。
    """
    min_x = min(x0, x1) - radius
    max_x = max(x0, x1) + radius
    min_y = min(y0, y1) - radius
    max_y = max(y0, y1) + radius
    i0 = max(0, int(math.ceil(min_x * ss - 0.5)))
    i1 = min(grid - 1, int(math.floor(max_x * ss - 0.5)))
    j0 = max(0, int(math.ceil(min_y * ss - 0.5)))
    j1 = min(grid - 1, int(math.floor(max_y * ss - 0.5)))
    if i0 > i1 or j0 > j1:
        return
    dx = x1 - x0
    dy = y1 - y0
    seg2 = dx * dx + dy * dy
    radius2 = radius * radius
    inv_ss = 1.0 / ss
    degenerate = seg2 <= 1e-12
    buf = buffer
    if degenerate:
        # 退化段即圆：逐行取圆内 x 区间
        for j in range(j0, j1 + 1):
            py = (j + 0.5) * inv_ss
            py0 = py - y0
            if py0 * py0 > radius2:
                continue
            half = math.sqrt(radius2 - py0 * py0) * ss
            lo = max(i0, int(math.ceil(x0 * ss - 0.5 - half)) - 1)
            hi = min(i1, int(math.floor(x0 * ss - 0.5 + half)) + 1)
            while lo <= hi:
                px0 = (lo + 0.5) * inv_ss - x0
                if px0 * px0 + py0 * py0 <= radius2:
                    break
                lo += 1
            while hi >= lo:
                px0 = (hi + 0.5) * inv_ss - x0
                if px0 * px0 + py0 * py0 <= radius2:
                    break
                hi -= 1
            if lo <= hi:
                row = j * grid
                buf[row + lo:row + hi + 1] = b'\x01' * (hi - lo + 1)
        return
    seg_len = math.sqrt(seg2)
    band_w = radius * seg_len
    for j in range(j0, j1 + 1):
        py = (j + 0.5) * inv_ss
        py0 = py - y0
        py1 = py - y1
        lo = None
        hi = None
        # 两端圆在该行的 x 区间
        if py0 * py0 <= radius2:
            half = math.sqrt(radius2 - py0 * py0)
            lo = x0 - half
            hi = x0 + half
        if py1 * py1 <= radius2:
            half = math.sqrt(radius2 - py1 * py1)
            b_lo = x1 - half
            b_hi = x1 + half
            if lo is None or b_lo < lo:
                lo = b_lo
            if hi is None or b_hi > hi:
                hi = b_hi
        # 线段正投影段 [0, seg2] 与垂距带 [-r*|d|, r*|d|] 的公共 x 区间
        if dx != 0.0:
            s1 = x0 - py0 * dy / dx
            s2 = s1 + seg2 / dx
            band_lo, band_hi = (s1, s2) if s1 <= s2 else (s2, s1)
            if dy != 0.0:
                t1 = x0 + (py0 * dx - band_w) / dy
                t2 = x0 + (py0 * dx + band_w) / dy
                p_lo, p_hi = (t1, t2) if t1 <= t2 else (t2, t1)
                if p_lo > band_lo:
                    band_lo = p_lo
                if p_hi < band_hi:
                    band_hi = p_hi
            elif py0 * py0 > radius2:
                band_lo, band_hi = 1.0, 0.0  # 水平段：该行在垂距带之外，交集为空
        else:
            # 竖直段：投影落在 [0, seg2] 内时 x 区间为 [x0-radius, x0+radius]
            tproj = py0 * dy
            if 0.0 <= tproj <= seg2:
                band_lo, band_hi = x0 - radius, x0 + radius
            else:
                band_lo, band_hi = 1.0, 0.0
        if band_lo <= band_hi:
            if lo is None or band_lo < lo:
                lo = band_lo
            if hi is None or band_hi > hi:
                hi = band_hi
        if lo is None or hi is None:
            continue
        lo_i = max(i0, int(math.ceil(lo * ss - 0.5)) - 1)
        hi_i = min(i1, int(math.floor(hi * ss - 0.5)) + 1)
        # 区间两端用逐像素判定校正（解析边界只差浮点误差）
        while lo_i <= hi_i:
            px = (lo_i + 0.5) * inv_ss
            t = ((px - x0) * dx + py0 * dy) / seg2
            if t < 0.0:
                t = 0.0
            elif t > 1.0:
                t = 1.0
            qx = x0 + t * dx
            qy = y0 + t * dy
            if (px - qx) * (px - qx) + (py - qy) * (py - qy) <= radius2:
                break
            lo_i += 1
        while hi_i >= lo_i:
            px = (hi_i + 0.5) * inv_ss
            t = ((px - x0) * dx + py0 * dy) / seg2
            if t < 0.0:
                t = 0.0
            elif t > 1.0:
                t = 1.0
            qx = x0 + t * dx
            qy = y0 + t * dy
            if (px - qx) * (px - qx) + (py - qy) * (py - qy) <= radius2:
                break
            hi_i -= 1
        if lo_i <= hi_i:
            row = j * grid
            buf[row + lo_i:row + hi_i + 1] = b'\x01' * (hi_i - lo_i + 1)


def _inside_polygon(px: float, py: float, points) -> bool:
    inside = False
    count = len(points)
    j = count - 1
    for i in range(count):
        xi, yi = points[i]
        xj, yj = points[j]
        if (yi > py) != (yj > py):
            if px < (xj - xi) * (py - yi) / (yj - yi) + xi:
                inside = not inside
        j = i
    return inside


def _stamp_polygon(buffer: bytearray, grid: int, ss: int, points) -> None:
    if len(points) < 3:
        return
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    i0 = max(0, int(math.ceil(min(xs) * ss - 0.5)))
    i1 = min(grid - 1, int(math.floor(max(xs) * ss - 0.5)))
    j0 = max(0, int(math.ceil(min(ys) * ss - 0.5)))
    j1 = min(grid - 1, int(math.floor(max(ys) * ss - 0.5)))
    if i0 > i1 or j0 > j1:
        return
    inv_ss = 1.0 / ss
    for j in range(j0, j1 + 1):
        py = (j + 0.5) * inv_ss
        row = j * grid
        for i in range(i0, i1 + 1):
            index = row + i
            if buffer[index]:
                continue
            px = (i + 0.5) * inv_ss
            if _inside_polygon(px, py, points):
                buffer[index] = 1


def rasterize_icon(nodes, size: int, stroke: float = STROKE_DEFAULT, supersample: int = SUPERSAMPLE_DEFAULT, threshold: float = INK_THRESHOLD_DEFAULT) -> bytearray:
    """按 lucide stroke 语义生成 size×size 二值剪影（1=有墨）。"""
    if size <= 0:
        raise IconlabError(f"--size 必须为正整数，收到 {size}", 2)
    if stroke <= 0:
        raise IconlabError(f"--stroke 必须为正数，收到 {stroke}", 2)
    if supersample < 1:
        raise IconlabError(f"--supersample 必须 >= 1，收到 {supersample}", 2)
    if not (0.0 < threshold <= 1.0):
        raise IconlabError(f"--threshold 必须在 (0, 1] 内，收到 {threshold}", 2)

    strokes, fills = flatten_icon(nodes)
    scale = size / VIEWBOX
    half_width = stroke / 2.0 * scale
    grid = size * supersample
    buffer = bytearray(grid * grid)
    for polyline in strokes:
        points = [(x * scale, y * scale) for x, y in polyline]
        if len(points) == 1:
            _stamp_capsule(buffer, grid, supersample, points[0][0], points[0][1], points[0][0], points[0][1], half_width)
            continue
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            _stamp_capsule(buffer, grid, supersample, x0, y0, x1, y1, half_width)
    for polygon in fills:
        _stamp_polygon(buffer, grid, supersample, [(x * scale, y * scale) for x, y in polygon])

    mask = bytearray(size * size)
    need = threshold * supersample * supersample
    buf = buffer
    ss = supersample
    index = 0
    for y in range(size):
        base = y * ss * grid
        for x in range(size):
            count = 0
            row = base + x * ss
            for sy in range(ss):
                count += buf[row:row + ss].count(1)
                row += grid
            if count >= need:
                mask[index] = 1
            index += 1
    return mask


def mask_iou(mask_a: bytearray, mask_b: bytearray) -> float:
    intersection = 0
    union = 0
    for left, right in zip(mask_a, mask_b):
        if left or right:
            union += 1
            if left and right:
                intersection += 1
    return intersection / union if union else 0.0


def mask_ink_ratio(mask: bytearray, size: int) -> float:
    return sum(mask) / (size * size) if size else 0.0


def _stroke_px(stroke: float, size: int) -> float:
    return stroke * size / VIEWBOX


# --------------------------------------------------------------------------- #
# measure
# --------------------------------------------------------------------------- #

def _parse_id_list(text: str, option: str) -> list[str]:
    ids = [item.strip() for item in (text or "").split(",") if item.strip()]
    deduped = list(dict.fromkeys(ids))
    if not deduped:
        raise IconlabError(f"{option} 不能为空（用逗号分隔图标 id）", 2)
    return deduped


def cmd_measure(args) -> int:
    doc = load_catalog(Path(args.catalog))
    source = doc["source"]
    icons = doc["icons"]
    ids = _parse_id_list(args.ids, "--ids")
    neighbors = _parse_id_list(args.neighbors, "--neighbors") if args.neighbors else []

    missing = [icon_id for icon_id in ids + neighbors if icon_id not in icons]
    if missing:
        import difflib  # 惰性导入：只有报错提示才需要相近名
        hints = []
        for icon_id in missing:
            close = difflib.get_close_matches(icon_id, list(icons.keys()), n=2, cutoff=0.6)
            if close:
                hints.append(f"{icon_id}（相近：{', '.join(close)}）")
            else:
                hints.append(icon_id)
        raise IconlabError("目录中不存在这些图标：" + "、".join(hints), 1)

    masks = {icon_id: rasterize_icon(icons[icon_id]["n"], args.size, args.stroke, args.supersample, args.threshold) for icon_id in ids}
    neighbor_masks = {
        icon_id: rasterize_icon(icons[icon_id]["n"], args.size, args.stroke, args.supersample, args.threshold)
        for icon_id in neighbors
    }

    ink = {icon_id: mask_ink_ratio(masks[icon_id], args.size) for icon_id in ids}
    matrix = {left: {right: mask_iou(masks[left], masks[right]) for right in ids} for left in ids}
    max_neighbor: dict[str, dict] = {}
    for icon_id in ids:
        best = None
        for neighbor_id in neighbors:
            value = mask_iou(masks[icon_id], neighbor_masks[neighbor_id])
            if best is None or value > best[1]:
                best = (neighbor_id, value)
        if best is not None:
            max_neighbor[icon_id] = {
                "neighbor": best[0],
                "iou": round(best[1], 4),
                "risk": best[1] > RISK_IOU,
            }

    empty = [icon_id for icon_id, value in ink.items() if value <= 0.0]
    warnings = []
    if empty:
        warnings.append("以下图标在 " + str(args.size) + "px 生成空剪影：" + "、".join(empty))

    if args.json:
        payload = {
            "source": source,
            "catalog": str(Path(args.catalog).resolve()),
            "params": {
                "size_px": args.size,
                "stroke_units": args.stroke,
                "stroke_px": round(_stroke_px(args.stroke, args.size), 3),
                "supersample": args.supersample,
                "ink_threshold": args.threshold,
                "risk_iou": RISK_IOU,
                "viewbox": VIEWBOX,
                "rule": "stroke 剪影：按 24 视框路径扁平化（含圆弧/贝塞尔），线宽 stroke 居中、圆头圆角，8× 超采样后按覆盖阈值二值化；IoU=交集/并集",
            },
            "ids": ids,
            "neighbors": neighbors,
            "ink_ratio": {icon_id: round(value, 4) for icon_id, value in ink.items()},
            "iou": {
                left: {right: round(value, 4) for right, value in row.items()}
                for left, row in matrix.items()
            },
            "max_neighbor_iou": max_neighbor,
            "warnings": warnings,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print("iconlab measure")
    print(f"目录：{_catalog_source_line(source)}")
    print(
        f"口径：目标 {args.size}px · stroke {args.stroke:g}（24 视框 → {_stroke_px(args.stroke, args.size):.2f}px）"
        f" · {args.supersample}× 超采样 · 覆盖阈值 {args.threshold:g} · 风险阈值 {RISK_IOU:g}"
    )
    print()

    print("图标墨量比（ink ratio）：")
    for icon_id in ids:
        bar_len = int(round(ink[icon_id] * 40))
        print(f"  {_pad(icon_id, 22)} {ink[icon_id]:6.3f}  {'#' * bar_len}")
    print()

    header = ["图标"] + [icon_id for icon_id in ids]
    rows = []
    for left in ids:
        row = [left]
        for right in ids:
            row.append("—" if left == right else f"{matrix[left][right]:.2f}")
        rows.append(row)
    print(f"两两 IoU（{args.size}px 描边剪影）：")
    _print_table(header, rows)
    print()

    if neighbors:
        print(f"与 neighbors 的最大 IoU（>{RISK_IOU:g} 标注高混淆风险）：")
        rows = []
        for icon_id in ids:
            entry = max_neighbor[icon_id]
            rows.append(
                [
                    icon_id,
                    "← " + entry["neighbor"],
                    f"{entry['iou']:.2f}",
                    " [高风险]" if entry["risk"] else "",
                ]
            )
        _print_table(["图标", "最相近 neighbor", "最大 IoU", "风险"], rows)
    else:
        print("未提供 --neighbors，跳过邻近混淆检查。")
    print()

    off_diagonal = [value for left in ids for right in ids if left != right for value in [matrix[left][right]]]
    if off_diagonal:
        print(f"矩阵最大非对角 IoU：{max(off_diagonal):.2f}")
    for warning in warnings:
        print(f"警告：{warning}", file=sys.stderr)
    return 0


# --------------------------------------------------------------------------- #
# 极简 YAML 子集解析（case.yaml 用）
# --------------------------------------------------------------------------- #

class YamlError(Exception):
    pass


def _strip_comment(line: str) -> str:
    out = []
    quote = None
    index = 0
    while index < len(line):
        char = line[index]
        if quote:
            out.append(char)
            if quote == '"' and char == "\\" and index + 1 < len(line):
                out.append(line[index + 1])
                index += 2
                continue
            if char == quote:
                quote = None
            index += 1
            continue
        if char in "\"'":
            quote = char
            out.append(char)
            index += 1
            continue
        if char == "#" and (index == 0 or line[index - 1] in " \t"):
            break
        out.append(char)
        index += 1
    return "".join(out).rstrip()


def _split_key(content: str):
    quote = None
    depth = 0
    for index, char in enumerate(content):
        if quote:
            if char == quote and (index == 0 or content[index - 1] != "\\"):
                quote = None
            continue
        if char in "\"'":
            quote = char
        elif char in "[{":
            depth += 1
        elif char in "]}":
            depth -= 1
        elif char == ":" and depth == 0:
            if index + 1 == len(content) or content[index + 1] in " \t":
                return content[:index].strip(), content[index + 1:].strip()
    raise YamlError(f"无法解析键值对：{content[:60]}")


def _looks_like_key(content: str) -> bool:
    if not content or content[0] in "\"'[{":
        return False
    try:
        _split_key(content)
        return True
    except YamlError:
        return False


def _parse_scalar(text: str):
    text = text.strip()
    if not text:
        return None
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        body = text[1:-1]
        out = []
        index = 0
        while index < len(body):
            char = body[index]
            if char == "\\" and index + 1 < len(body):
                nxt = body[index + 1]
                out.append({"n": "\n", "t": "\t", '"': '"', "\\": "\\"}.get(nxt, nxt))
                index += 2
                continue
            out.append(char)
            index += 1
        return "".join(out)
    if len(text) >= 2 and text[0] == "'" and text[-1] == "'":
        return text[1:-1].replace("''", "'")
    lowered = text.lower()
    if lowered in ("true", "false"):
        return lowered == "true"
    if lowered in ("null", "~"):
        return None
    if re.fullmatch(r"[-+]?\d+", text):
        return int(text)
    if re.fullmatch(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?", text):
        return float(text)
    return text


def _parse_flow(text: str):
    position = 0

    def skip() -> None:
        nonlocal position
        while position < len(text) and text[position] in " \t\r\n":
            position += 1

    def parse_string(quote: str) -> str:
        nonlocal position
        position += 1
        buffer = []
        while position < len(text):
            char = text[position]
            if quote == '"' and char == "\\":
                position += 1
                if position >= len(text):
                    break
                buffer.append({"n": "\n", "t": "\t", '"': '"', "\\": "\\"}.get(text[position], text[position]))
                position += 1
                continue
            if char == quote:
                if quote == "'" and position + 1 < len(text) and text[position + 1] == "'":
                    buffer.append("'")
                    position += 2
                    continue
                position += 1
                return "".join(buffer)
            buffer.append(char)
            position += 1
        raise YamlError("flow 字符串引号未闭合")

    def parse_value():
        nonlocal position
        skip()
        if position >= len(text):
            raise YamlError("flow 值意外结束")
        char = text[position]
        if char in "[{":
            return parse_collection()
        if char in "\"'":
            return parse_string(char)
        start = position
        while position < len(text) and text[position] not in ",]}":
            position += 1
        return _parse_scalar(text[start:position])

    def parse_collection():
        nonlocal position
        opening = text[position]
        position += 1
        if opening == "[":
            items = []
            while True:
                skip()
                if position < len(text) and text[position] == "]":
                    position += 1
                    return items
                items.append(parse_value())
                skip()
                if position < len(text) and text[position] == ",":
                    position += 1
                    continue
                if position < len(text) and text[position] == "]":
                    position += 1
                    return items
                raise YamlError("flow 列表缺少逗号或右方括号")
        result = {}
        while True:
            skip()
            if position < len(text) and text[position] == "}":
                position += 1
                return result
            if position >= len(text):
                raise YamlError("flow 映射未闭合")
            if text[position] in "\"'":
                key = parse_string(text[position])
            else:
                start = position
                while position < len(text) and text[position] != ":":
                    if text[position] in ",}":
                        raise YamlError("flow 映射缺少冒号")
                    position += 1
                key = text[start:position].strip()
            skip()
            if position >= len(text) or text[position] != ":":
                raise YamlError("flow 映射缺少冒号")
            position += 1
            result[key] = parse_value()
            skip()
            if position < len(text) and text[position] == ",":
                position += 1
                continue
            if position < len(text) and text[position] == "}":
                position += 1
                return result
            raise YamlError("flow 映射缺少逗号或右花括号")

    value = parse_value()
    skip()
    if position != len(text):
        raise YamlError("flow 值后存在多余字符")
    return value


def _parse_block_scalar(lines, index, parent_indent, style):
    collected = []
    while index < len(lines) and lines[index][0] > parent_indent:
        collected.append(lines[index][1])
        index += 1
    if not collected:
        return "", index
    if style.startswith(">"):
        return " ".join(collected), index
    return "\n".join(collected), index


def _parse_block(lines, index, indent):
    if lines[index][1].startswith("-"):
        return _parse_list(lines, index, indent)
    return _parse_map(lines, index, indent)


def _parse_map(lines, index, indent):
    result = {}
    while index < len(lines):
        current_indent, content, lineno = lines[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            raise YamlError(f"第 {lineno} 行缩进异常（期待 {indent}，实际 {current_indent}）")
        if content.startswith("-"):
            break
        try:
            key, rest = _split_key(content)
        except YamlError as exc:
            raise YamlError(f"第 {lineno} 行：{exc}")
        if not key:
            raise YamlError(f"第 {lineno} 行：键名为空")
        index += 1
        if rest == "":
            if index < len(lines) and lines[index][0] > indent:
                value, index = _parse_block(lines, index, lines[index][0])
            else:
                value = None
        elif rest.startswith("|") or rest.startswith(">"):
            value, index = _parse_block_scalar(lines, index, indent, rest)
        elif rest[0] in "[{":
            value = _parse_flow(rest)
        else:
            value = _parse_scalar(rest)
        if key in result:
            raise YamlError(f"第 {lineno} 行：重复键 {key}")
        result[key] = value
    return result, index


def _parse_list(lines, index, indent):
    items = []
    while index < len(lines):
        current_indent, content, lineno = lines[index]
        if current_indent != indent or not content.startswith("-"):
            break
        if content != "-" and content[1:2] not in (" ", "\t"):
            raise YamlError(f"第 {lineno} 行：列表项缺少空格")
        rest = content[1:].strip()
        index += 1
        if rest == "":
            if index < len(lines) and lines[index][0] > indent:
                value, index = _parse_block(lines, index, lines[index][0])
            else:
                value = None
        elif rest[0] in "[{":
            value = _parse_flow(rest)
        elif _looks_like_key(rest):
            synthetic = [(indent + 2, rest, lineno)]
            cursor = index
            while cursor < len(lines) and lines[cursor][0] > indent:
                synthetic.append(lines[cursor])
                cursor += 1
            value, used = _parse_map(synthetic, 0, indent + 2)
            if used < len(synthetic):
                raise YamlError(f"第 {synthetic[used][2]} 行：列表项后续缩进不一致")
            index = cursor
        else:
            value = _parse_scalar(rest)
        items.append(value)
    return items, index


def parse_yaml_subset(text: str):
    lines = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        stripped = _strip_comment(raw)
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        if "\t" in stripped[:indent]:
            raise YamlError(f"第 {lineno} 行：缩进不能用制表符")
        lines.append((indent, stripped.strip(), lineno))
    if not lines:
        return {}
    if lines[0][0] != 0:
        raise YamlError(f"第 {lines[0][2]} 行：顶层必须从第 0 列开始")
    value, index = _parse_block(lines, 0, 0)
    if index != len(lines):
        raise YamlError(f"第 {lines[index][2]} 行：结构未解析完")
    return value


# --------------------------------------------------------------------------- #
# render：单文件离线 HTML
# --------------------------------------------------------------------------- #

PALETTES = {
    "dark": {
        "bg": "#0e1116",
        "surface": "#151b23",
        "surface-2": "#1a2230",
        "surface-3": "#212b3a",
        "border": "#2a3441",
        "border-strong": "#3d4c5f",
        "text": "#e8ecf1",
        "text-muted": "#9aa6b4",
        "text-faint": "#7b8796",
        "accent": "#6da2ff",
        "accent-soft": "rgba(109, 162, 255, 0.16)",
        "ok": "#4fb36c",
        "ok-soft": "rgba(79, 179, 108, 0.16)",
        "warn": "#d9a038",
        "warn-soft": "rgba(217, 160, 56, 0.18)",
        "error": "#e05a5a",
        "error-soft": "rgba(224, 90, 90, 0.18)",
        "risk-bg": "rgba(224, 90, 90, 0.24)",
        "shadow": "rgba(0, 0, 0, 0.45)",
        "code-bg": "#0a0e13",
        "code-border": "#263140",
        "focus": "#9cc0ff",
    },
    "light": {
        "bg": "#f4f6f9",
        "surface": "#ffffff",
        "surface-2": "#f7f9fc",
        "surface-3": "#eef2f7",
        "border": "#dde3ea",
        "border-strong": "#c3cdd9",
        "text": "#1b2430",
        "text-muted": "#5b6878",
        "text-faint": "#7d8896",
        "accent": "#2f6fdb",
        "accent-soft": "rgba(47, 111, 219, 0.12)",
        "ok": "#2e7d4f",
        "ok-soft": "rgba(46, 125, 79, 0.12)",
        "warn": "#9a6a12",
        "warn-soft": "rgba(154, 106, 18, 0.14)",
        "error": "#b93a3a",
        "error-soft": "rgba(185, 58, 58, 0.12)",
        "risk-bg": "rgba(185, 58, 58, 0.16)",
        "shadow": "rgba(23, 32, 45, 0.12)",
        "code-bg": "#f0f3f7",
        "code-border": "#d7dee7",
        "focus": "#2f6fdb",
    },
}

TOKEN_VARS = {
    "text-muted": "var(--text-muted)",
    "text-primary": "var(--text)",
    "accent": "var(--accent)",
    "state-ok": "var(--ok)",
    "state-warn": "var(--warn)",
    "state-error": "var(--error)",
    "line": "var(--border)",
}


def build_theme_css() -> str:
    blocks = []
    for selector, name in ((":root", "dark"), ('[data-theme="light"]', "light")):
        lines = [f"{selector} {{", f"  color-scheme: {name};"]
        for key, value in PALETTES[name].items():
            lines.append(f"  --{key}: {value};")
        if selector == ":root":
            for token, value in TOKEN_VARS.items():
                lines.append(f"  --token-{token}: {value};")
        lines.append("}")
        blocks.append("\n".join(lines))
    return "\n".join(blocks)


PAGE_CSS = r"""
*, *::before, *::after { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
html { scrollbar-gutter: stable; }
body {
  background: var(--bg);
  color: var(--text);
  font: 15px/1.55 system-ui, -apple-system, "Segoe UI", "Noto Sans SC", "Microsoft YaHei", sans-serif;
  -webkit-font-smoothing: antialiased;
}
.wrap { max-width: 1360px; margin: 0 auto; padding: 20px 24px 40px; display: flex; flex-direction: column; gap: 14px; }
.card {
  min-width: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px 18px;
  box-shadow: 0 1px 0 var(--shadow);
}
.hero { padding: 18px 20px; }
.hero-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.eyebrow { margin: 0 0 4px; font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--text-faint); }
h1 { margin: 0 0 6px; font-size: 23px; line-height: 1.3; letter-spacing: 0.01em; overflow-wrap: anywhere; }
h2 { margin: 0 0 8px; font-size: 16px; line-height: 1.4; }
h3 { margin: 0; font-size: 14px; line-height: 1.4; }
p { margin: 0; }
.request { color: var(--text-muted); font-size: 13px; max-width: 880px; }
.toolbar { display: flex; gap: 8px; flex-wrap: wrap; }
.btn {
  font: inherit;
  font-size: 12px;
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid var(--border-strong);
  background: var(--surface-3);
  color: var(--text);
  cursor: pointer;
}
.btn:hover { border-color: var(--accent); color: var(--accent); }
.btn:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 14px; }
.chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  line-height: 1.5;
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--text-muted);
  max-width: 100%;
  overflow-wrap: anywhere;
}
.chip b { color: var(--text); font-weight: 600; }
.chip-accent { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); }
.chip-warn { border-color: var(--warn); color: var(--warn); background: var(--warn-soft); }
.chip-ok { border-color: var(--ok); color: var(--ok); background: var(--ok-soft); }
.chip-error { border-color: var(--error); color: var(--error); background: var(--error-soft); }
.tooltip-line { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; margin-top: 14px; }
.tooltip-label { font-size: 11px; color: var(--text-faint); }
.bubble {
  max-width: 100%;
  padding: 5px 10px;
  border-radius: 8px;
  border: 1px solid var(--border-strong);
  background: var(--surface-3);
  color: var(--text);
  font-size: 12px;
  overflow-wrap: anywhere;
}
.caption { font-size: 11px; color: var(--text-faint); line-height: 1.6; }
.section-head { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin-bottom: 10px; }
.section-head h2 { margin: 0; }
.ladder { display: flex; align-items: flex-end; flex-wrap: wrap; gap: 22px; padding: 6px 2px 2px; }
.ladder-item { display: flex; flex-direction: column; align-items: center; gap: 6px; min-width: 58px; }
.ladder-icon { height: 30px; display: flex; align-items: flex-end; justify-content: center; }
.ladder-px { font-size: 11px; color: var(--text); }
.ladder-ink { font-size: 11px; color: var(--text-faint); }
.context-grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 14px; margin-top: 16px; }
.context-block { min-width: 0; background: var(--surface-2); border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px; }
.context-block .caption { margin-bottom: 8px; }
.row-demo { display: flex; align-items: center; gap: 10px; min-height: 40px; padding: 4px 2px; }
.row-icon { display: inline-flex; color: var(--token-text-muted); flex: none; }
.row-text { flex: 1 1 auto; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 13px; }
.row-actions { display: flex; align-items: center; gap: 8px; flex: none; color: var(--text-muted); }
.grayscale { filter: grayscale(1); }
.alts { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }
.alt-card {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--surface-2);
}
.alt-top { display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap; }
.alt-id { font-size: 13px; color: var(--text); font-weight: 600; overflow-wrap: anywhere; }
.verdict { font-size: 11px; padding: 2px 7px; border-radius: 999px; border: 1px solid var(--border-strong); color: var(--text-muted); }
.verdict-rejected { border-color: var(--error); color: var(--error); background: var(--error-soft); }
.verdict-backup { border-color: var(--warn); color: var(--warn); background: var(--warn-soft); }
.alt-sizes { display: flex; align-items: flex-end; flex-wrap: wrap; gap: 16px; }
.alt-size { display: flex; flex-direction: column; align-items: center; gap: 4px; color: var(--text-muted); }
.alt-size span { font-size: 11px; color: var(--text-faint); }
.alt-reason { font-size: 12px; color: var(--text-muted); overflow-wrap: anywhere; }
.alt-metric { font-size: 11px; color: var(--text-faint); }
.matrix-wrap { width: 100%; overflow: hidden; }
.matrix-note { margin-top: 8px; }
.icon { display: inline-flex; align-items: center; justify-content: center; }
table.matrix { width: 100%; border-collapse: collapse; table-layout: fixed; }
.matrix th, .matrix td {
  border: 1px solid var(--border);
  padding: 6px 4px;
  font-size: 12px;
  text-align: center;
  overflow-wrap: anywhere;
  color: var(--text-muted);
}
.matrix th { color: var(--text); font-weight: 600; background: var(--surface-2); }
.matrix th.row-head { text-align: left; padding-left: 8px; }
.matrix td.self { color: var(--text-faint); }
.matrix td.risk { background: var(--risk-bg); color: var(--error); font-weight: 700; }
.rationale { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 12px; }
.reason-block { min-width: 0; padding: 12px 14px; border-radius: 10px; border: 1px solid var(--border); background: var(--surface-2); }
.reason-block h3 { margin-bottom: 6px; color: var(--text); }
.reason-block p { font-size: 13px; color: var(--text-muted); overflow-wrap: anywhere; }
.spec-tools { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin-bottom: 10px; }
pre.spec {
  margin: 0;
  padding: 14px 16px;
  border-radius: 10px;
  border: 1px solid var(--code-border);
  background: var(--code-bg);
  color: var(--text);
  font: 12px/1.65 ui-monospace, "Cascadia Code", "Consolas", "Liberation Mono", monospace;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
footer { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px; padding: 2px 4px; }
footer p { font-size: 11px; color: var(--text-faint); }
.overflow-status { display: block; margin-top: 10px; padding: 8px 10px; border-radius: 8px; border: 1px solid var(--error); background: var(--error-soft); color: var(--error); font-size: 12px; }
@media print {
  @page { margin: 10mm; }
  body { background: var(--surface); }
  .wrap { max-width: none; padding: 0; gap: 10px; }
  .card { box-shadow: none; break-inside: avoid; }
  .toolbar, .spec-tools .btn { display: none; }
}
"""

PAGE_JS = r"""
(function () {
  var root = document.documentElement;
  var themeButton = document.getElementById('theme-toggle');
  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    if (themeButton) {
      themeButton.textContent = theme === 'dark' ? '切到浅色' : '切到深色';
    }
  }
  applyTheme(root.getAttribute('data-theme') || 'dark');
  if (themeButton) {
    themeButton.addEventListener('click', function () {
      applyTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
    });
  }
  var copyButton = document.getElementById('copy-spec');
  var specBlock = document.getElementById('spec-text');
  if (copyButton && specBlock) {
    copyButton.addEventListener('click', function () {
      var text = specBlock.textContent || '';
      function report(ok) {
        copyButton.textContent = ok ? '已复制' : '复制失败，请手动选择';
        window.setTimeout(function () { copyButton.textContent = '复制规格块'; }, 1800);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { report(true); }, function () { report(false); });
      } else {
        report(false);
      }
    });
  }
  var overflowOk = root.scrollWidth <= window.innerWidth;
  root.setAttribute('data-overflow-ok', overflowOk ? 'true' : 'false');
  console.log('[iconlab] horizontal-overflow ' + (overflowOk ? 'none' : 'DETECTED') +
    ' | scrollWidth=' + root.scrollWidth + ' | innerWidth=' + window.innerWidth);
  var status = document.getElementById('overflow-status');
  if (!overflowOk && status) {
    status.hidden = false;
    status.textContent = '横向溢出：scrollWidth=' + root.scrollWidth + ' > innerWidth=' + window.innerWidth;
  }
})();
"""


def _slot_color_class(color: str) -> tuple[str, str | None]:
    """返回 (CSS 类名, 警告文本或 None)。颜色一律走主题变量。"""
    token = (color or "").strip()
    if token == "inherit":
        return "slot-color-inherit", None
    if token in TOKEN_VARS:
        return f"slot-color-{token}", None
    return "slot-color-fallback", f"未识别的色令牌 {token!r}，已回退到 text-muted"


def _svg_markup(nodes, size: int, stroke: float, label: str | None = None, decorative: bool = False) -> str:
    attrs = [
        f'width="{size}"',
        f'height="{size}"',
        'viewBox="0 0 24 24"',
        'fill="none"',
        'stroke="currentColor"',
        f'stroke-width="{("%g" % stroke)}"',
        'stroke-linecap="round"',
        'stroke-linejoin="round"',
    ]
    if decorative:
        attrs.extend(['aria-hidden="true"', 'focusable="false"'])
    else:
        attrs.extend(['role="img"', f'aria-label="{_esc(label or "")}"'])
    children = []
    for tag, child_attrs in nodes:
        pairs = " ".join(f'{key}="{_esc(value)}"' for key, value in child_attrs.items())
        children.append(f"<{tag} {pairs}/>")
    return "<svg " + " ".join(attrs) + ">" + "".join(children) + "</svg>"


def _case_get(case: dict, key: str):
    value = case.get(key)
    return value


def _require_str(case: dict, key: str, where: str = "case") -> str:
    value = case.get(key)
    if not isinstance(value, str) or not value.strip():
        raise IconlabError(f"{where}.{key} 必须是非空字符串", 2)
    return value.strip()


def _optional_str(case: dict, key: str) -> str | None:
    value = case.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise IconlabError(f"case.{key} 必须是字符串", 2)
    return value.strip()


def _string_list(case: dict, key: str, required: bool = False) -> list[str]:
    value = case.get(key)
    if value is None:
        if required:
            raise IconlabError(f"case.{key} 缺失", 2)
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise IconlabError(f"case.{key} 必须是字符串列表", 2)
    return list(dict.fromkeys(item.strip() for item in value if item.strip()))


def _validate_case(case: dict, icons: dict) -> dict:
    if not isinstance(case, dict):
        raise IconlabError("case.yaml 顶层必须是映射（case: {...}）", 2)
    request = _require_str(case, "request")
    slot = _require_str(case, "slot")
    chosen = _require_str(case, "chosen")
    chosen_label = _optional_str(case, "chosen_label") or chosen

    slot_facts_raw = case.get("slot_facts")
    slot_facts: dict = {}
    if slot_facts_raw is None:
        slot_facts = {}
    elif isinstance(slot_facts_raw, dict):
        slot_facts = slot_facts_raw
    else:
        raise IconlabError("case.slot_facts 必须是映射", 2)

    form = slot_facts.get("form")
    icon_px = slot_facts.get("icon_px")
    color = slot_facts.get("color")
    tooltip_raw = slot_facts.get("tooltip")
    if icon_px is None:
        icon_px = 16
    if not isinstance(icon_px, int) or isinstance(icon_px, bool) or icon_px <= 0:
        raise IconlabError(f"case.slot_facts.icon_px 必须是正整数，收到 {icon_px!r}", 2)
    if not isinstance(form, str) or not form.strip():
        form = "未声明"
    if not isinstance(color, str) or not color.strip():
        color = "未声明"

    tooltip_requirement = "未声明"
    tooltip_text = None
    if isinstance(tooltip_raw, bool):
        tooltip_requirement = "required" if tooltip_raw else "forbidden"
    elif isinstance(tooltip_raw, str):
        normalized = tooltip_raw.strip().lower()
        if normalized in ("required", "optional", "forbidden"):
            tooltip_requirement = normalized
        elif normalized in ("true", "false"):
            tooltip_requirement = "required" if normalized == "true" else "forbidden"
        elif tooltip_raw.strip():
            tooltip_requirement = "required"
            tooltip_text = tooltip_raw.strip()
    extra_tooltip = _optional_str(case, "tooltip_text") or _optional_str(case, "tooltip")
    if extra_tooltip:
        tooltip_text = extra_tooltip

    alternatives_raw = case.get("alternatives")
    if alternatives_raw is None:
        alternatives_raw = []
    if not isinstance(alternatives_raw, list):
        raise IconlabError("case.alternatives 必须是列表", 2)
    alternatives = []
    for index, item in enumerate(alternatives_raw):
        if not isinstance(item, dict):
            raise IconlabError(f"case.alternatives[{index}] 必须是映射", 2)
        alt_id = item.get("id")
        if not isinstance(alt_id, str) or not alt_id.strip():
            raise IconlabError(f"case.alternatives[{index}].id 缺失", 2)
        verdict = item.get("verdict")
        if verdict not in ("rejected", "backup"):
            raise IconlabError(f"case.alternatives[{index}].verdict 只能是 rejected 或 backup，收到 {verdict!r}", 2)
        reason = item.get("reason")
        if reason is not None and not isinstance(reason, str):
            raise IconlabError(f"case.alternatives[{index}].reason 必须是字符串", 2)
        alternatives.append({"id": alt_id.strip(), "verdict": verdict, "reason": (reason or "").strip()})

    neighbors = _string_list(case, "neighbors")
    sizes_raw = case.get("sizes")
    if sizes_raw is None:
        sizes = [12, 16, 18, 20, 24]
    elif isinstance(sizes_raw, list) and all(isinstance(item, int) and not isinstance(item, bool) and item > 0 for item in sizes_raw):
        sizes = list(dict.fromkeys(sizes_raw))
    else:
        raise IconlabError("case.sizes 必须是正整数列表", 2)

    rationale_raw = case.get("rationale")
    if rationale_raw is None:
        rationale_raw = []
    if not isinstance(rationale_raw, list):
        raise IconlabError("case.rationale 必须是列表", 2)
    rationale = []
    for index, item in enumerate(rationale_raw):
        if not isinstance(item, dict):
            raise IconlabError(f"case.rationale[{index}] 必须是映射", 2)
        title = item.get("title")
        body = item.get("body")
        if not isinstance(title, str) or not title.strip():
            raise IconlabError(f"case.rationale[{index}].title 缺失", 2)
        if not isinstance(body, str) or not body.strip():
            raise IconlabError(f"case.rationale[{index}].body 缺失", 2)
        rationale.append({"title": title.strip(), "body": body.strip()})

    spec_note = _optional_str(case, "spec_note") or ""

    referenced = [chosen] + [item["id"] for item in alternatives] + neighbors
    missing = [icon_id for icon_id in referenced if icon_id not in icons]
    if missing:
        import difflib  # 惰性导入，理由同 cmd_measure
        hints = []
        for icon_id in missing:
            close = difflib.get_close_matches(icon_id, list(icons.keys()), n=2, cutoff=0.6)
            hints.append(f"{icon_id}（相近：{', '.join(close)}）" if close else icon_id)
        raise IconlabError("case 引用了目录中不存在的图标：" + "、".join(hints), 1)

    return {
        "request": request,
        "slot": slot,
        "chosen": chosen,
        "chosen_label": chosen_label,
        "slot_facts": {
            "form": form,
            "icon_px": icon_px,
            "color": color,
            "tooltip_requirement": tooltip_requirement,
            "tooltip_text": tooltip_text,
        },
        "alternatives": alternatives,
        "neighbors": neighbors,
        "sizes": sizes,
        "rationale": rationale,
        "spec_note": spec_note,
    }


def _fmt_iou(value: float) -> str:
    return f"{value:.2f}"


def _build_html(case_data: dict, catalog: dict, stroke: float, case_name: str) -> tuple[str, dict]:
    icons = catalog["icons"]
    source = catalog["source"]
    chosen = case_data["chosen"]
    chosen_label = case_data["chosen_label"]
    slot_facts = case_data["slot_facts"]
    matrix_size = slot_facts["icon_px"]
    color_class, color_warning = _slot_color_class(slot_facts["color"])
    warnings = []
    if color_warning:
        warnings.append(color_warning)

    matrix_ids = list(
        dict.fromkeys(
            [chosen]
            + [item["id"] for item in case_data["alternatives"]]
            + case_data["neighbors"]
        )
    )
    masks = {
        icon_id: rasterize_icon(icons[icon_id]["n"], matrix_size, stroke, SUPERSAMPLE_DEFAULT, INK_THRESHOLD_DEFAULT)
        for icon_id in matrix_ids
    }
    ious = {
        left: {right: (1.0 if left == right else mask_iou(masks[left], masks[right])) for right in matrix_ids}
        for left in matrix_ids
    }

    ladder_chosen_masks = {
        size: rasterize_icon(icons[chosen]["n"], size, stroke, SUPERSAMPLE_DEFAULT, INK_THRESHOLD_DEFAULT)
        for size in case_data["sizes"]
    }

    def icon(icon_id: str, size: int, label: str | None = None, decorative: bool = True, color_cls: str = "") -> str:
        markup = _svg_markup(
            icons[icon_id]["n"],
            size,
            stroke,
            label=label or icon_id,
            decorative=decorative,
        )
        return f'<span class="icon {color_cls}">{markup}</span>' if color_cls else f'<span class="icon">{markup}</span>'

    # ---- 顶部 ----
    chips = [
        f'<span class="chip">槽位 <b>{_esc(case_data["slot"])}</b></span>',
        f'<span class="chip">形式 <b>{_esc(slot_facts["form"])}</b></span>',
        f'<span class="chip">尺寸 <b>{matrix_size}px</b></span>',
        f'<span class="chip">色令牌 <b>{_esc(slot_facts["color"])}</b></span>',
        f'<span class="chip">Tooltip <b>{_esc(slot_facts["tooltip_requirement"])}</b></span>',
        f'<span class="chip">选中 <b>{_esc(chosen)}</b></span>',
    ]
    tooltip_text = slot_facts["tooltip_text"]
    tooltip_display = tooltip_text if tooltip_text else "（case 未给出 Tooltip 文案）"
    tooltip_line = (
        '<div class="tooltip-line">'
        '<span class="tooltip-label">Tooltip 文案</span>'
        f'<span class="bubble">{_esc(tooltip_display)}</span>'
        "</div>"
    )

    hero = f"""
<header class="card hero">
  <div class="hero-top">
    <div>
      <p class="eyebrow">ICONLAB · 图标选型对比 · 离线单页</p>
      <h1>{_esc(case_data["request"])}</h1>
      <p class="request">选中图标 <b>{_esc(chosen)}</b>（{_esc(chosen_label)}）；本页核对槽位事实、真实像素可辨性与混淆风险。</p>
    </div>
    <div class="toolbar">
      <button id="theme-toggle" class="btn" type="button">切换主题</button>
      <button id="copy-spec" class="btn" type="button">复制规格块</button>
    </div>
  </div>
  <div class="chips">{"".join(chips)}</div>
  {tooltip_line}
  <div id="overflow-status" class="overflow-status" hidden></div>
</header>
"""

    # ---- 尺寸阶梯 + 行上下文 ----
    ladder_items = []
    for size in case_data["sizes"]:
        ink = mask_ink_ratio(ladder_chosen_masks[size], size) * 100.0
        ladder_items.append(
            '<div class="ladder-item">'
            f'<div class="ladder-icon">{icon(chosen, size, label=f"{chosen} {size}px")}</div>'
            f'<div class="ladder-px">{size} px</div>'
            f'<div class="ladder-ink">墨量 {ink:.1f}%</div>'
            "</div>"
        )

    row_actions = "".join(
        icon(icon_id, 16, label=f"邻近候选 {icon_id}") for icon_id in case_data["neighbors"]
    )
    row_demo = (
        '<div class="row-demo">'
        f'<span class="row-icon {color_class}">{_svg_markup(icons[chosen]["n"], 16, stroke, label=chosen, decorative=False)}</span>'
        f'<span class="row-text">{_esc(chosen_label)}</span>'
        f'<span class="row-actions">{row_actions}</span>'
        "</div>"
    )
    if not case_data["neighbors"]:
        row_actions_note = "（case 未给出 neighbors，右侧动作图标留空）"
    else:
        row_actions_note = "右侧动作图标取 neighbors：" + "、".join(case_data["neighbors"])

    show = f"""
<section class="card">
  <div class="section-head">
    <h2>主展示 · 真实像素</h2>
    <p class="caption">SVG 以 width/height 真实像素渲染，非 font-size 缩放；墨量为 {matrix_size}px 口径之外的各尺寸二值剪影占比。</p>
  </div>
  <div class="ladder">{"".join(ladder_items)}</div>
  <div class="context-grid">
    <div class="context-block">
      <p class="caption">真实行上下文 · 16px（模拟列表一行：图标 + 文本 + 右侧动作图标）</p>
      {row_demo}
      <p class="caption">{_esc(row_actions_note)}</p>
    </div>
    <div class="context-block grayscale">
      <p class="caption">同上的灰度版（filter: grayscale，检查明度分离）</p>
      {row_demo}
      <p class="caption">灰度下仍应可辨：图标与文本、右侧动作图标不糊成一团。</p>
    </div>
  </div>
</section>
"""

    # ---- 候选对比 ----
    alt_cards = []
    for item in case_data["alternatives"]:
        alt_id = item["id"]
        verdict = item["verdict"]
        reason = item["reason"] or "（case 未给出理由）"
        alt_ious = ious[chosen].get(alt_id, 0.0)
        sizes_html = "".join(
            '<div class="alt-size">'
            f'{icon(alt_id, size, label=f"{alt_id} {size}px")}'
            f"<span>{size}px</span>"
            "</div>"
            for size in (16, 18, 20)
        )
        verdict_class = "verdict-rejected" if verdict == "rejected" else "verdict-backup"
        verdict_text = "rejected · 淘汰" if verdict == "rejected" else "backup · 备选"
        alt_cards.append(
            '<article class="alt-card">'
            '<div class="alt-top">'
            f'<span class="alt-id">{_esc(alt_id)}</span>'
            f'<span class="verdict {verdict_class}">{_esc(verdict_text)}</span>'
            "</div>"
            f'<div class="alt-sizes">{sizes_html}</div>'
            f'<p class="alt-reason">{_esc(reason)}</p>'
            f'<p class="alt-metric">与 chosen 的 {matrix_size}px 剪影 IoU：<b>{_fmt_iou(alt_ious)}</b></p>'
            "</article>"
        )
    if not alt_cards:
        alt_cards.append('<p class="caption">case 未给出 alternatives。</p>')
    alts = f"""
<section class="card">
  <div class="section-head">
    <h2>候选对比</h2>
    <p class="caption">每个候选渲染 16/18/20px 真实像素；IoU 口径同下方矩阵（{matrix_size}px 二值描边剪影）。</p>
  </div>
  <div class="alts">{"".join(alt_cards)}</div>
</section>
"""

    # ---- 混淆矩阵 ----
    header_cells = "".join(f'<th scope="col">{_esc(icon_id)}</th>' for icon_id in matrix_ids)
    body_rows = []
    for left in matrix_ids:
        cells = []
        for right in matrix_ids:
            if left == right:
                cells.append('<td class="self">—</td>')
                continue
            value = ious[left][right]
            if value > RISK_IOU:
                cells.append(f'<td class="risk">{_fmt_iou(value)}</td>')
            else:
                cells.append(f"<td>{_fmt_iou(value)}</td>")
        body_rows.append(
            f'<tr><th scope="row" class="row-head">{_esc(left)}</th>{"".join(cells)}</tr>'
        )
    risk_pairs = [
        (left, right, ious[left][right])
        for left in matrix_ids
        for right in matrix_ids
        if left < right and ious[left][right] > RISK_IOU
    ]
    risk_note = (
        "高混淆对：" + "；".join(f"{left} ↔ {right} {value:.2f}" for left, right, value in risk_pairs)
        if risk_pairs
        else f"无超过 {RISK_IOU:g} 的高混淆对。"
    )
    matrix_html = f"""
<section class="card">
  <div class="section-head">
    <h2>混淆矩阵 · 两两 IoU</h2>
    <p class="caption">{matrix_size}px 二值描边剪影；&gt;{RISK_IOU:g} 单元格高亮为高混淆风险。</p>
  </div>
  <div class="matrix-wrap">
    <table class="matrix">
      <thead><tr><th scope="col">图标</th>{header_cells}</tr></thead>
      <tbody>{"".join(body_rows)}</tbody>
    </table>
  </div>
  <p class="caption matrix-note">{_esc(risk_note)}</p>
</section>
"""

    # ---- 理由区 ----
    rationale_blocks = "".join(
        f'<article class="reason-block"><h3>{_esc(item["title"])}</h3><p>{_esc(item["body"])}</p></article>'
        for item in case_data["rationale"]
    )
    if not rationale_blocks:
        rationale_blocks = '<p class="caption">case 未给出 rationale。</p>'
    rationale_html = f"""
<section class="card">
  <div class="section-head">
    <h2>为什么选它</h2>
    <p class="caption">理由按 case.rationale 原样呈现。</p>
  </div>
  <div class="rationale">{rationale_blocks}</div>
</section>
"""

    # ---- 规格块 ----
    alt_lines = []
    for item in case_data["alternatives"]:
        alt_lines.append(
            f'  - {item["id"]} [{item["verdict"]}] IoU {_fmt_iou(ious[chosen].get(item["id"], 0.0))} — '
            f'{item["reason"] or "（未给出理由）"}'
        )
    spec_lines = [
        f"icon: {chosen}",
        f"label: {chosen_label}",
        f"slot: {case_data['slot']}（{slot_facts['form']} · {matrix_size}px · {slot_facts['color']}）",
        "sizes: " + " / ".join(str(size) for size in case_data["sizes"]),
        f"tooltip: {tooltip_text or '（case 未给出）'}",
        "alternatives:",
        *(alt_lines if alt_lines else ["  - （无）"]),
    ]
    if case_data["neighbors"]:
        spec_lines.append("neighbors: " + ", ".join(case_data["neighbors"]))
    if case_data["spec_note"]:
        spec_lines.append(f"spec_note: {case_data['spec_note']}")
    spec_text = "\n".join(spec_lines)
    spec_html = f"""
<section class="card">
  <div class="section-head">
    <h2>可复制规格块</h2>
    <p class="caption">复制后可直接粘贴进选型记录或交接文档。</p>
  </div>
  <pre class="spec" id="spec-text">{_esc(spec_text)}</pre>
</section>
"""

    footer = f"""
<footer>
  <p>由 iconlab.py 生成 · 目录 {_esc(source.get('library', 'lucide-static'))}@{_esc(source.get('version', '?'))} · {_esc(source.get('icon_count', '?'))} 个图标 · {_esc(source.get('license', '?'))}</p>
  <p>case：{_esc(case_name)} · 生成日期 {date.today().isoformat()} · 纯离线单文件（无 CDN / 无外链资源）</p>
</footer>
"""

    page = f"""<!doctype html>
<html lang="zh-CN" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>iconlab · {_esc(chosen_label)} · {_esc(case_data["slot"])}</title>
<style>
{build_theme_css()}
{PAGE_CSS}
</style>
</head>
<body>
<div class="wrap">
{hero}
{show}
{alts}
{matrix_html}
{rationale_html}
{spec_html}
{footer}
</div>
<script>
{PAGE_JS}
</script>
</body>
</html>
"""

    stats = {
        "matrix_ids": matrix_ids,
        "matrix_size": matrix_size,
        "ious": ious,
        "risk_pairs": risk_pairs,
        "svg_count": page.count("<svg "),
        "warnings": warnings,
        "rule": "stroke 剪影：24 视框路径扁平化（含贝塞尔/圆弧），线宽居中圆头，8× 超采样后二值化；IoU=交集/并集",
    }
    return page, stats


def _validate_generated_html(page: str, stats: dict) -> list[str]:
    """页面自检：主题块外零颜色字面量、最小字号 >= 11px、无外部引用、var() 均已定义。"""
    problems = []
    theme_css = build_theme_css()
    page_without_theme = page.replace(theme_css, "", 1)
    rest = PAGE_CSS + page_without_theme
    color_pattern = re.compile(r"(?<!&)#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?)\s*\(")
    color_hits = color_pattern.findall(rest)
    if color_hits:
        problems.append(f"主题块外出现 {len(color_hits)} 处颜色字面量：{color_hits[:6]}")

    font_sizes = [float(value) for value in re.findall(r"font-size:\s*([0-9.]+)px", PAGE_CSS)]
    too_small = [value for value in font_sizes if value < 11.0]
    if too_small:
        problems.append(f"存在小于 11px 的 font-size：{too_small}")

    external = re.findall(r'(?:src|href)\s*=\s*["\']https?://|@import|url\(', page)
    if external:
        problems.append(f"页面存在外部引用：{external[:4]}")

    defined = set(re.findall(r"--([a-z0-9-]+)\s*:", theme_css))
    used = set(re.findall(r"var\(--([a-z0-9-]+)\)", rest))
    undefined = sorted(used - defined)
    if undefined:
        problems.append(f"使用了未定义的 CSS 变量：{undefined}")

    if "<svg " not in page:
        problems.append("页面没有内联 SVG")
    return problems


def cmd_render(args) -> int:
    case_path = Path(args.case)
    if not case_path.is_file():
        raise IconlabError(f"未找到 case 文件：{case_path}", 2)
    catalog_doc = load_catalog(Path(args.catalog))
    icons = catalog_doc["icons"]
    try:
        raw = parse_yaml_subset(case_path.read_text(encoding="utf-8"))
    except YamlError as exc:
        raise IconlabError(f"case.yaml 解析失败：{exc}", 2)
    except OSError as exc:
        raise IconlabError(f"读取 case 文件失败：{case_path}（{exc}）", 2)

    if not isinstance(raw, dict) or "case" not in raw:
        raise IconlabError("case.yaml 顶层必须包含 case: 映射", 2)
    case_data = _validate_case(raw["case"], icons)
    page, stats = _build_html(case_data, catalog_doc, args.stroke, case_path.name)
    problems = _validate_generated_html(page, stats)
    if problems:
        raise IconlabError("HTML 自检失败：\n  - " + "\n  - ".join(problems), 1)

    out = Path(args.out)
    _write_text(out, page)
    size = out.stat().st_size

    print("iconlab render · 完成")
    print(f"  case：{case_path.resolve()}")
    print(f"  输出：{out.resolve()}（{size} 字节 / {size / 1024:.1f} KiB）")
    print(f"  目录：{_catalog_source_line(catalog_doc['source'])}")
    print(f"  选中：{case_data['chosen']}（{case_data['chosen_label']}）")
    print("  尺寸阶梯：" + " / ".join(str(item) for item in case_data["sizes"]) + " px")
    print(f"  矩阵口径：{stats['matrix_size']}px · 图标 {len(stats['matrix_ids'])} 个 · 内联 svg {stats['svg_count']} 个")
    if stats["risk_pairs"]:
        print("  高混淆对：" + "；".join(f"{a} ↔ {b} {value:.2f}" for a, b, value in stats["risk_pairs"]))
    else:
        print(f"  高混淆对：无（阈值 {RISK_IOU:g}）")
    print("  自检：主题块外颜色字面量 0 处 · 最小字号 11px · 外部引用 0 · var() 全部已定义")
    for warning in stats["warnings"]:
        print(f"  警告：{warning}", file=sys.stderr)
    print('  页面自检：console 会输出 "[iconlab] horizontal-overflow none"（scrollWidth <= innerWidth）')
    return 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def _positive_int(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"需要整数，收到 {text!r}")
    if value <= 0:
        raise argparse.ArgumentTypeError(f"需要正整数，收到 {value}")
    return value


def _positive_float(text: str) -> float:
    try:
        value = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"需要数字，收到 {text!r}")
    if value <= 0:
        raise argparse.ArgumentTypeError(f"需要正数，收到 {value}")
    return value


def _threshold_float(text: str) -> float:
    value = _positive_float(text)
    if value > 1.0:
        raise argparse.ArgumentTypeError(f"阈值必须在 (0, 1] 内，收到 {value}")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="iconlab.py",
        description=(
            "iconlab —— lucide 图标目录、16px 描边剪影度量与离线对比页。\n"
            "数据只来自本地 lucide-static 解包目录，运行期不联网。"
        ),
        epilog=(
            "退出码：0 = 成功；1 = 检出失败或校验失败；2 = 用法或内部错误。\n"
            "自测示例：\n"
            "  catalog --from <lucide-static> --out data/lucide-catalog.json\n"
            '  search --query "本地 插件" --slot source --top 8\n'
            "  measure --ids hard-drive,folder-input --neighbors git-fork --size 16 --json\n"
            "  render --case case.yaml --out out.html"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--debug", action="store_true", help="出错时打印完整 traceback（排障用）")
    subparsers = parser.add_subparsers(dest="cmd", metavar="<command>", required=True)

    catalog_parser = subparsers.add_parser(
        "catalog",
        help="从 lucide-static 解包目录生成紧凑目录 JSON",
        description="读取 icon-nodes.json / tags.json / package.json，生成 data/lucide-catalog.json。",
        epilog="示例：catalog --from D:/path/lucide-static/package --out data/lucide-catalog.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    catalog_parser.add_argument("--from", dest="from_dir", required=True, metavar="DIR", help="lucide-static 解包根目录")
    catalog_parser.add_argument("--out", default=str(DEFAULT_CATALOG), metavar="FILE", help=f"输出路径（默认 {DEFAULT_CATALOG}）")
    catalog_parser.set_defaults(func=cmd_catalog)

    search_parser = subparsers.add_parser(
        "search",
        help="基于真实 tags + id 词检索候选图标",
        description=(
            "用真实 tags 与图标 id 词检索；内置中文意图别名表（本地/插件/删除/更新/待定等）映射到英文检索词。\n"
            "输出候选表：图标 id | 命中的 tag/词 | 分数。"
        ),
        epilog='示例：search --query "本地 插件" --slot source --top 8',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    search_parser.add_argument("--query", required=True, help="查询词（中文/英文，空格分隔）")
    search_parser.add_argument("--slot", choices=["source", "status", "action", "filter", "count", "nav"], help="槽位偏向（只加权，不过滤）")
    search_parser.add_argument("--top", type=_positive_int, default=8, metavar="N", help="返回条数（默认 8）")
    search_parser.add_argument("--json", action="store_true", help="输出 JSON")
    search_parser.add_argument("--catalog", default=str(DEFAULT_CATALOG), metavar="FILE", help="目录文件路径")
    search_parser.set_defaults(func=cmd_search)

    measure_parser = subparsers.add_parser(
        "measure",
        help="16px 描边剪影几何度量（IoU / 墨量比 / 邻近混淆）",
        description=(
            "把 path/circle/ellipse/rect/line/polyline/polygon 扁平化为折线，按 lucide stroke 语义\n"
            "（线宽默认 2.25、居中、圆头圆角）在目标尺寸上 8× 超采样盖章、降采样二值化，再算 IoU。"
        ),
        epilog="示例：measure --ids hard-drive,folder-input --neighbors git-fork,external-link --size 16 --json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    measure_parser.add_argument("--ids", required=True, help="逗号分隔的图标 id 列表")
    measure_parser.add_argument("--size", type=_positive_int, default=16, metavar="PX", help="目标像素尺寸（默认 16）")
    measure_parser.add_argument("--neighbors", default="", metavar="IDS", help="逗号分隔的邻近候选 id（只算与 ids 的最大 IoU）")
    measure_parser.add_argument("--stroke", type=_positive_float, default=STROKE_DEFAULT, metavar="W", help=f"线宽（24 视框单位，默认 {STROKE_DEFAULT}）")
    measure_parser.add_argument("--supersample", type=_positive_int, default=SUPERSAMPLE_DEFAULT, metavar="N", help=f"超采样倍数（默认 {SUPERSAMPLE_DEFAULT}）")
    measure_parser.add_argument("--threshold", type=_threshold_float, default=INK_THRESHOLD_DEFAULT, metavar="T", help=f"降采样二值化覆盖阈值（默认 {INK_THRESHOLD_DEFAULT}）")
    measure_parser.add_argument("--json", action="store_true", help="输出 JSON")
    measure_parser.add_argument("--catalog", default=str(DEFAULT_CATALOG), metavar="FILE", help="目录文件路径")
    measure_parser.set_defaults(func=cmd_measure)

    render_parser = subparsers.add_parser(
        "render",
        help="读取 case.yaml，产出单文件离线 HTML 对比页",
        description=(
            "读取 case.yaml（case/slot_facts/chosen/alternatives/neighbors/sizes/rationale），\n"
            "产出内联 SVG、双主题、灰度、真实行上下文、候选对比、混淆矩阵与可复制规格块的单文件 HTML。"
        ),
        epilog="示例：render --case case.yaml --out out.html",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    render_parser.add_argument("--case", required=True, metavar="FILE", help="case.yaml 路径")
    render_parser.add_argument("--out", required=True, metavar="FILE", help="输出 HTML 路径")
    render_parser.add_argument("--stroke", type=_positive_float, default=STROKE_DEFAULT, metavar="W", help=f"线宽（24 视框单位，默认 {STROKE_DEFAULT}）")
    render_parser.add_argument("--catalog", default=str(DEFAULT_CATALOG), metavar="FILE", help="目录文件路径")
    render_parser.set_defaults(func=cmd_render)

    return parser


def main(argv=None) -> int:
    _configure_streams()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except IconlabError as exc:
        print(f"错误：{exc.message}", file=sys.stderr)
        return exc.code
    except BrokenPipeError:
        return 0
    except KeyboardInterrupt:
        print("已中断", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - CLI 兜底
        if getattr(args, "debug", False):
            import traceback

            traceback.print_exc()
        print(f"内部错误：{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
