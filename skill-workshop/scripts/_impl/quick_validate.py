"""
Quick validation script for skills - minimal version
"""

from pathlib import Path
import functools
import re
import sys

from .utils import YAML_AVAILABLE, ensure_skill_path, load_markdown_document, load_skill_document


ALLOWED_SPEC_PROPERTIES = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
}

PROJECT_PROPERTIES = {
    "version",
}

ALL_ALLOWED_PROPERTIES = ALLOWED_SPEC_PROPERTIES | PROJECT_PROPERTIES
# 仅用于识别历史 builder 标记（分类提示），v2 不再把 @ 当作硬校验对象。
WORKFLOW_HEADER_RE = re.compile(r"^#{2,3}\s+@工作流:\s*.+$", re.MULTILINE)
STRICT_WORKFLOW_HEADER_RE = re.compile(r"^##\s+@工作流:\s*.+$", re.MULTILINE)
NONSTANDARD_WORKFLOW_HEADER_RE = re.compile(r"^###\s+@工作流:\s*.+$", re.MULTILINE)
# description 原始行（YAML 结构检查用：是否双引号包裹、是否含转义符）。
DESC_RAW_RE = re.compile(r"^description:(.*)$", re.M)


def _load_profiles() -> dict[str, set[str]]:
    """Load profile fail_on sets (optional YAML; archived in v2).

    Runtime v2 keeps embedded defaults only. Historical
    references/config/script-profiles.yaml now lives under docs/archive/.
    """
    defaults = {
        "strict": {"official-hard", "incident-backed"},
        "standard": {"official-hard", "incident-backed"},
        "advisory": set(),
    }
    yaml_path = Path(__file__).resolve().parent.parent / "references" / "config" / "script-profiles.yaml"
    if not yaml_path.is_file():
        return defaults
    try:
        text = yaml_path.read_text(encoding="utf-8")
    except OSError:
        return defaults
    profiles: dict[str, set[str]] = {}
    for name in ("strict", "standard", "advisory"):
        m = re.search(rf"^[ \t]*{name}:[ \t]*\n((?:^[ \t]+.*\n?)*)", text, re.M)
        if not m:
            continue
        block = m.group(1)
        fm = re.search(r"fail_on:[ \t]*\[([^\]]*)\]", block)
        if fm:
            items = [x.strip().strip('"\'') for x in fm.group(1).split(",") if x.strip()]
            profiles[name] = set(items)
    if not profiles:
        return defaults
    for name in defaults:
        profiles.setdefault(name, defaults[name])
    return profiles


PROFILES = _load_profiles()


def append_error(bucket: list[dict], scope: str, message: str, rule_class: str = "official-hard") -> None:
    """追加一条 blocker finding（默认 rule_class: official-hard）。"""
    bucket.append({"rule_class": rule_class, "message": message})


def append_warning(bucket: list[dict], scope: str, message: str, rule_class: str = "style-regex") -> None:
    """追加一条 warning finding（默认 rule_class: style-regex）。"""
    bucket.append({"rule_class": rule_class, "message": message})


def is_nonempty_string(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def parse_version_token(text: str) -> str | None:
    match = re.search(r"v?([0-9]+(?:\.[0-9]+)+)", text)
    if not match:
        return None
    return match.group(1)


def get_metadata_map(frontmatter: dict) -> dict | None:
    metadata = frontmatter.get("metadata")
    if isinstance(metadata, dict):
        return metadata
    return None


def get_project_version_sources(frontmatter: dict) -> tuple[str | None, str | None]:
    top_level_version = frontmatter.get("version")
    top_level_text = str(top_level_version).strip() if top_level_version is not None else None
    if top_level_text == "":
        top_level_text = None

    metadata_version = None
    metadata = get_metadata_map(frontmatter)
    if metadata is not None and metadata.get("version") is not None:
        metadata_version = str(metadata.get("version")).strip()
        if metadata_version == "":
            metadata_version = None

    return top_level_text, metadata_version


def get_resolved_project_version(frontmatter: dict) -> str | None:
    top_level_text, metadata_text = get_project_version_sources(frontmatter)
    return top_level_text or metadata_text


def is_builder_class_skill(content):
    """
    Classify SKILL.md for diagnostics only (v2 does not gate on this).

    Legacy builder-class: contains a `@工作流:` heading (old workshop scaffolding).
    Runtime-class / v2 pure Markdown: no such header — and neither class fails
    validate for missing `@` markup.

    Returns (is_builder, reason) for auditable classification.
    """
    has_workflow_header = bool(re.search(WORKFLOW_HEADER_RE, content))
    if has_workflow_header:
        return True, "contains '@工作流:' header (legacy builder form; markup not enforced in v2)"
    return False, "no '@工作流:' header — pure Markdown / runtime skill (v2 default)"


def validate_semantic_markup(content, *, skill_is_builder=True):
    """
    v2: step-level `@` markup is never a hard validation requirement.

    Historical builder checks are retained only as advisory classification.
    Pure Markdown skills MUST pass validate without `@工作流` / `@步骤` / `@动作`.
    """
    has_legacy = bool(re.search(WORKFLOW_HEADER_RE, content))
    if skill_is_builder and has_legacy:
        return True, (
            "Semantic markup (legacy '@工作流' form) detected — advisory only in v2; "
            "not required, not blocking"
        )
    return True, (
        "Semantic markup waived: v2 runtime contract is pure Markdown "
        "(no @ workflow markers required)"
    )


def _external_version_record(skill_path: Path) -> Path | None:
    """返回存在的外部变更记录文件（CHANGELOG.md 优先，其次 VERSION.md），无则 None。"""
    for name in ("CHANGELOG.md", "VERSION.md"):
        p = skill_path / name
        if p.is_file():
            return p
    return None


def validate_version_history_length(content, max_entries=5, *, skill_path: Path | None = None):
    # If no version history in content, check external version record fallback
    has_history = bool(
        re.search(r"^##\s+(?:版本历史|Version History)\s*$", content, re.MULTILINE)
    )
    if not has_history and skill_path is not None:
        version_md = _external_version_record(skill_path)
        if version_md is not None:
            content = version_md.read_text(encoding="utf-8")

    sections = re.split(r"^##\s+", content, flags=re.MULTILINE)
    version_history_block = None
    for section in sections:
        if section.startswith("版本历史"):
            version_history_block = section
            break
        if section.startswith("Version History"):
            version_history_block = section
            break
    if version_history_block is None:
        return True, "Version history section exists"

    lines = version_history_block.splitlines()
    entries = []
    for line in lines[1:]:
        if line.startswith("### ") or line.startswith("## "):
            break
        if re.match(r"^- \*\*v[0-9]+(?:\.[0-9]+)+\*\*", line.strip()):
            entries.append(line.strip())

    if len(entries) > max_entries:
        return (
            False,
            f"Version history must keep at most {max_entries} entries, got {len(entries)}",
        )

    return True, "Version history length is valid"


def extract_header_version(content: str) -> str | None:
    match = re.search(
        r"^>\s+\*\*(?:版本|Version)\*\*:\s*(.+?)\s*$", content, re.MULTILINE
    )
    if not match:
        return None
    return parse_version_token(match.group(1).strip())


def validate_description_symbols(raw_frontmatter: str) -> tuple[list[str], list[str]]:
    """description 原始行检查，返回 (硬问题, 风格建议)。

    只有会造成 YAML 真实解析失败的两条留在硬判据：未双引号包裹、含反斜杠（双引号标量里
    反斜杠是转义符，实测会让外部技能管理软件与 YAML 头解析出错）。斜杠与半角冒号在双引号内
    完全合法，把它们判硬错会逼作者把自然语言改拧，2026-09-22 反向审计后降为风格建议。
    """
    problems: list[str] = []
    advisories: list[str] = []
    m = DESC_RAW_RE.search(raw_frontmatter or "")
    if not m:
        return problems, advisories
    raw = m.group(1).strip()
    quoted = len(raw) >= 2 and raw.startswith('"') and raw.endswith('"')
    if not quoted:
        problems.append('description 未用双引号包裹（须为单行 string，形如 description: "…"）')
    if chr(92) in raw:
        problems.append("description 含反斜杠（双引号 YAML 里是转义符，硬禁止）")
    if problems:
        # 结构本身不合法时先修结构：此时对未加引号的原文挑风格符号只会叠加噪音。
        return problems, advisories
    body = raw[1:-1] if quoted else raw
    if "/" in body:
        advisories.append("description 含斜杠（本仓风格：并列词改顿号，字面路径改写为「某目录」）")
    if re.search(r"(?<!Not for):", body):
        advisories.append("description 含半角冒号（本仓风格：改全角；规格标记 Not for: 除外）")
    return problems, advisories


PLACEHOLDER_RE = re.compile(r"\{\{.*?\}\}|TODO|FIXME", re.S)


def validate_description_format(frontmatter: dict) -> tuple[bool, str, str]:
    """description 的结构校验：存在、非空、单行 string、长度、未完成占位符。

    语义质量（触发是否自然、是否堆词、是否说清用户任务）不是机器判据，由
    `references/optimization.md` §Description 语义评审与评审模式承担。
    v2.2.0 及更早的意图词表计数、引号词计数与 Pushy 句式正则已于 v2.3.0 删除：
    实测它们把裸词表判成合规高分、把自然中文描述判成硬错误，属于反向激励。

    Returns (ok, message, severity)；severity 为 "error"（硬 FAIL）或 "info"（不再刷屏）。
    """
    desc = frontmatter.get("description")
    if not desc:
        return False, "description 字段缺失", "error"
    if not isinstance(desc, str):
        return False, f"description 必须是字符串，实为 {type(desc).__name__}", "error"

    # YAML 的块标量（| 或 >）会被解析成带换行的字符串；官方与本仓均要求单行 string。
    if "\n" in desc.strip():
        return False, (
            "description 含换行（疑似 YAML 块标量 | 或 >），违反单行 string 约束；"
            '改为 description: "<单行文本>"'
        ), "error"

    if len(desc) > 1024:
        return False, f"description 超过 1024 字符（当前 {len(desc)}）", "error"

    hit = PLACEHOLDER_RE.search(desc)
    if hit:
        return False, f"description 含未完成占位符：{hit.group(0)[:30]!r}", "error"

    return True, f"description 结构合规（{len(desc)} 字符）", "info"


def extract_latest_version_history_entry(content: str) -> str | None:
    # Format 1: "## 版本历史" section with "- **vX.Y.Z** ..." entries
    history_match = re.search(
        r"^##\s+(?:版本历史|Version History)\s*$([\s\S]*)",
        content,
        re.MULTILINE,
    )
    if history_match:
        for line in history_match.group(1).splitlines():
            stripped = line.strip()
            if not stripped or stripped == "---":
                continue
            match = re.match(r"^-\s+\*\*v([0-9]+(?:\.[0-9]+)+)\*\*", stripped)
            if match:
                return match.group(1)
            if stripped.startswith("## "):
                break

    # Format 2: VERSION.md style "## vX.Y.Z (date)" headings
    for line in content.splitlines():
        match = re.match(r"^##\s+v([0-9]+(?:\.[0-9]+)+)\s*\(", line.strip())
        if match:
            return match.group(1)

    # Format 3: CHANGELOG.md style "## [1.25.0] - date" or "## 1.25.0"
    m = re.search(r"^##\s+\[?v?(\d+\.\d+\.\d+)\]?", content, re.MULTILINE)
    if m:
        return m.group(1)

    return None


def validate_version_consistency(frontmatter: dict, content: str, *, skill_path: Path | None = None):
    top_level_version, metadata_version = get_project_version_sources(frontmatter)
    resolved_version = top_level_version or metadata_version
    header_version = extract_header_version(content)
    history_version = extract_latest_version_history_entry(content)

    # Fallback: read version history from external record (CHANGELOG.md/VERSION.md) if not in SKILL.md
    if history_version is None and skill_path is not None:
        version_md = _external_version_record(skill_path)
        if version_md is not None:
            version_md_content = version_md.read_text(encoding="utf-8")
            history_version = extract_latest_version_history_entry(version_md_content)

    if top_level_version and metadata_version and top_level_version != metadata_version:
        return (
            False,
            (
                "Project version mismatch between top-level version and metadata.version: "
                f"version={top_level_version}, metadata.version={metadata_version}"
            ),
        )

    if not resolved_version:
        return (
            False,
            "Missing project version metadata (add top-level 'version' or 'metadata.version')",
        )

    if not header_version:
        # v2 SSOT：正文头部版本块可省略；机器事实 = metadata.version + CHANGELOG/VERSION 顶部。
        if skill_path is not None and _external_version_record(skill_path) is not None:
            if history_version and resolved_version != history_version:
                return (
                    False,
                    (
                        "Project version mismatch between metadata.version and external record top: "
                        f"resolved={resolved_version}, record={history_version}"
                    ),
                )
            if history_version:
                return (
                    True,
                    (
                        f"Version SSOT in sync: metadata.version={resolved_version} "
                        f"matches external record top {history_version}"
                    ),
                )
            return (
                True,
                (
                    f"External version record present but no parseable top entry; "
                    f"metadata.version={resolved_version} accepted as SSOT"
                ),
            )
        return (
            False,
            (
                "Missing version info in document header (add '> **版本**: vX.Y.Z' after the main"
                " title) or provide CHANGELOG.md / VERSION.md"
            ),
        )

    if resolved_version != header_version:
        return (
            False,
            (
                "Project version mismatch between frontmatter/metadata and header: "
                f"resolved_version={resolved_version}, header={header_version}"
            ),
        )

    if not history_version:
        # history_version 缺失：frontmatter 与头部一致即可，VERSION.md fallback 已在
        # _load_version_history_content 兜底
        if skill_path is not None and _external_version_record(skill_path) is not None:
            return (
                True,
                "Version fields are in sync (skipped history check; external version record present)",
            )
        return (
            False,
            "Version history must contain a latest entry in the format '- **vX.Y.Z** (...) - ...'",
        )

    if resolved_version != history_version:
        return (
            False,
            (
                "Project version mismatch between frontmatter/metadata and latest version history"
                f" entry: resolved_version={resolved_version}, latest_history={history_version}"
            ),
        )

    return True, "Version fields are in sync"


PLACEHOLDER_PATTERNS = [
    re.compile(r"\[TODO(?::|\])"),
    re.compile(r"<!--\s*TODO[:\s]"),
    re.compile(r"\(YYYY-MM-DD\)"),
    re.compile(r"^##\s+\s*主工作流名称\s*$"),
    re.compile(r"^###\s+\s*第一步标题\s*$"),
    re.compile(r"^###\s+\s*第二步标题\s*$"),
]

def validate_template_placeholders(content: str):
    matches = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern.search(line):
                matches.append(f"line {line_number}: {line.strip()}")
                break

    if matches:
        preview = "\n  - ".join(matches[:10])
        more = ""
        if len(matches) > 10:
            more = f"\n  - ... and {len(matches) - 10} more"
        return (
            False,
            "Unfinished template placeholders found in SKILL.md:\n  - " + preview + more,
        )

    return True, "No unfinished template placeholders found"


def find_frontmatter_end_line(content: str) -> int | None:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return index

    return None


def get_body_line_count(content: str) -> int:
    end_line = find_frontmatter_end_line(content)
    lines = content.splitlines()
    if end_line is None:
        return len(lines)
    return len(lines[end_line + 1 :])


def _load_version_history_content(skill_path: Path, content: str) -> str:
    """Return version history content from SKILL.md or external record fallback.

    If SKILL.md contains a '## 版本历史' section, use it.
    Otherwise, read CHANGELOG.md/VERSION.md from the same directory.
    """
    if re.search(r"^##\s+(?:版本历史|Version History)\s*$", content, re.MULTILINE):
        return content
    version_md = _external_version_record(skill_path)
    if version_md is not None:
        return version_md.read_text(encoding="utf-8")
    return content


def validate_version_history_position(content: str, doc_label: str = "SKILL.md", *, skill_path: Path | None = None):
    # If SKILL.md has no version history, check external record fallback
    has_history_in_content = bool(
        re.search(r"^##\s+(?:版本历史|Version History)\s*$", content, re.MULTILINE)
    )
    if not has_history_in_content and skill_path is not None:
        version_md = _external_version_record(skill_path)
        if version_md is not None:
            # Version history lives in CHANGELOG.md/VERSION.md — valid arrangement
            return True, "Version history is in CHANGELOG.md/VERSION.md"

    lines = content.splitlines()
    history_index = None

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped in {"## 版本历史", "## Version History"}:
            history_index = index

    if history_index is None:
        return (
            False,
            f"Missing version history section (add '## 版本历史' at the end of {doc_label})",
        )

    trailing_lines = lines[history_index + 1 :]
    saw_entry = False
    for line in trailing_lines:
        stripped = line.strip()
        if not stripped or stripped == "---":
            continue
        if re.match(r"^- \*\*v[0-9]+(?:\.[0-9]+)+\*\*", stripped):
            saw_entry = True
            continue
        return (
            False,
            (
                f"Version history must stay at the end of {doc_label} (only entries, blank lines,"
                " or a final --- are allowed after '## 版本历史')"
            ),
        )

    if not saw_entry:
        return False, "Version history section must contain at least one version entry"

    return True, "Version history position is valid"


def validate_version_history_entry_count(content: str, max_entries: int = 5, *, skill_path: Path | None = None):
    # If no version history in content, check external record fallback
    has_history = bool(
        re.search(r"^##\s+(?:版本历史|Version History)\s*$", content, re.MULTILINE)
    )
    if not has_history and skill_path is not None:
        record = _external_version_record(skill_path)
        if record is not None:
            # 版本历史维护在外部变更记录（CHANGELOG.md/VERSION.md），不强制内联 ## 版本历史，
            # 也不对其施加 5 条上限（Keep a Changelog 保留完整历史）。
            return True, "Version history is maintained in external CHANGELOG.md/VERSION.md"
        # record 为 None：无外部记录，保持原 content 继续内联历史校验

    history_match = re.search(
        r"^##\s+(?:版本历史|Version History)\s*$([\s\S]*)",
        content,
        re.MULTILINE,
    )
    if not history_match:
        return False, "Missing version history section"

    entries = re.findall(r"^- \*\*v[0-9]+(?:\.[0-9]+)+\*\*", history_match.group(1), re.MULTILINE)
    if len(entries) > max_entries:
        return (
            False,
            f"Version history must keep at most {max_entries} entries; found {len(entries)}",
        )
    return True, "Version history entry count is valid"


def should_skip_markdown_file(markdown_path: Path) -> bool:
    if any(part in {"dist", "__pycache__"} for part in markdown_path.parts):
        return True
    if markdown_path.name.startswith("."):
        return True
    return False


def slugify_markdown_heading(heading_text: str) -> str:
    heading_text = re.sub(r"`([^`]*)`", r"\1", heading_text.strip())
    heading_text = re.sub(r"[!-/:-@\[-`{-~]", "", heading_text)
    heading_text = re.sub(r"\s+", "-", heading_text)
    heading_text = re.sub(r"-+", "-", heading_text)
    return heading_text.strip("-").lower()


@functools.lru_cache(maxsize=128)
def extract_markdown_anchors(markdown_path: Path) -> set[str]:
    anchors: set[str] = set()
    explicit_anchor_pattern = re.compile(r"\{#([^}]+)\}\s*$")
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

    in_fence = False
    for line in markdown_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        heading_match = heading_pattern.match(stripped)
        if not heading_match:
            continue

        heading_text = heading_match.group(2).strip()
        explicit_match = explicit_anchor_pattern.search(heading_text)
        if explicit_match:
            anchors.add(explicit_match.group(1).strip().lower())
            heading_text = explicit_anchor_pattern.sub("", heading_text).strip()

        slug = slugify_markdown_heading(heading_text)
        if slug:
            anchors.add(slug)

    return anchors


def validate_markdown_links(skill_path: Path):
    markdown_files = [
        markdown_path
        for markdown_path in skill_path.rglob("*.md")
        if markdown_path.is_file()
        and not should_skip_markdown_file(markdown_path.relative_to(skill_path))
    ]
    broken_links = []
    link_pattern = re.compile(r"!?\[[^\]]+\]\(([^)]+)\)")
    external_scheme_pattern = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
    resolve_cache: dict[Path, Path] = {}
    content_cache: dict[Path, str] = {}

    def cached_resolve(p: Path) -> Path:
        if p not in resolve_cache:
            resolve_cache[p] = p.resolve()
        return resolve_cache[p]

    def cached_read(p: Path) -> str:
        if p not in content_cache:
            content_cache[p] = p.read_text(encoding="utf-8")
        return content_cache[p]

    def format_available_anchors(anchors: set[str]) -> str:
        if not anchors:
            return "no anchors found"
        preview = sorted(anchors)[:5]
        suffix = "" if len(anchors) <= len(preview) else ", ..."
        return ", ".join(f"#{anchor}" for anchor in preview) + suffix

    def format_anchor_suggestions(anchor_part: str, anchors: set[str]) -> str:
        if not anchors:
            return ""
        try:
            from difflib import get_close_matches
        except Exception:
            return ""
        matches = get_close_matches(anchor_part, sorted(anchors), n=3, cutoff=0.6)
        if not matches:
            return ""
        return "; maybe: " + ", ".join(f"#{match}" for match in matches)

    for markdown_path in markdown_files:
        content = cached_read(markdown_path)
        in_fence = False
        for line_number, line in enumerate(content.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            for match in link_pattern.finditer(line):
                raw_target = match.group(1).strip()
                if not raw_target:
                    continue
                if raw_target.startswith("<") and raw_target.endswith(">"):
                    raw_target = raw_target[1:-1].strip()
                if not raw_target:
                    continue
                if external_scheme_pattern.match(raw_target):
                    continue

                target_without_query = raw_target.split("?", 1)[0].strip()
                if not target_without_query:
                    continue

                target_path_part, anchor_part = (
                    target_without_query.split("#", 1)
                    if "#" in target_without_query
                    else (target_without_query, "")
                )
                target_path_part = target_path_part.strip()
                anchor_part = anchor_part.strip().lower()

                if not target_path_part:
                    target_markdown = markdown_path
                    display_target = markdown_path.relative_to(skill_path)
                else:
                    target_markdown = cached_resolve(markdown_path.parent / target_path_part)
                    display_target = target_path_part
                    if not target_markdown.exists():
                        broken_links.append(
                            f"{markdown_path.relative_to(skill_path)}:{line_number} ->"
                            f" {raw_target} (missing file: {target_path_part})"
                        )
                        continue

                if anchor_part and target_markdown.suffix.lower() == ".md":
                    anchors = extract_markdown_anchors(target_markdown)
                    if anchor_part not in anchors:
                        suggestions = format_anchor_suggestions(anchor_part, anchors)
                        broken_links.append(
                            f"{markdown_path.relative_to(skill_path)}:{line_number} ->"
                            f" {raw_target} (missing anchor #{anchor_part} in {display_target};"
                            f" available: {format_available_anchors(anchors)}{suggestions})"
                        )

    if broken_links:
        preview = broken_links[:10]
        message = "Broken local Markdown links found:\n  - " + "\n  - ".join(preview)
        if len(broken_links) > len(preview):
            message += f"\n  - ... and {len(broken_links) - len(preview)} more"
        return False, message

    return True, "Markdown links are valid"


def _extract_frontmatter(text: str) -> str | None:
    """Return the YAML frontmatter block (between the first pair of ---) or None."""
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    return parts[1]


def validate_referenced_asset_paths(skill_path: Path):
    """Check that references/, scripts/, examples/, assets/ paths mentioned in any
    .md file (Markdown links, fenced code blocks, and bare prose mentions) actually
    exist. Closes the gap where validate_markdown_links only checks [text](link)
    syntax outside code fences. Paths are resolved relative to the skill root,
    matching the skill-workshop root-relative reference convention."""
    asset_pattern = re.compile(
        r"(?:(?:references|scripts|examples|assets)/[A-Za-z0-9_.\-/]+?\."
        r"(?:md|py|json|html|css|ts|js|yaml|yml|png|svg))"
    )
    skill_md = skill_path / "SKILL.md"
    if not skill_md.is_file():
        return True, "Referenced asset paths are valid (no SKILL.md)"
    missing = []
    seen = set()
    try:
        content = skill_md.read_text(encoding="utf-8")
    except Exception:
        return True, "Referenced asset paths are valid (unreadable)"
    for line_number, line in enumerate(content.splitlines(), start=1):
        for m in asset_pattern.finditer(line):
            token = m.group(0)
            if token in seen:
                continue
            seen.add(token)
            if not (skill_path / token).resolve().exists():
                missing.append(f"SKILL.md:{line_number} -> {token} (missing file)")
    if missing:
        preview = missing[:10]
        message = "Broken referenced asset paths found:\n  - " + "\n  - ".join(preview)
        if len(missing) > len(preview):
            message += f"\n  - ... and {len(missing) - len(preview)} more"
        return False, message
    return True, "Referenced asset paths are valid"


def validate_reference_trigger_when(skill_path: Path):
    """Every references/**/*.md should declare a trigger-when frontmatter key, so
    sunk content has an explicit load condition and is not an orphan. Emitted as a
    warning (not a hard error) to avoid breaking skills that predate the convention."""
    missing = []
    for ref_path in sorted(skill_path.glob("references/**/*.md")):
        if not ref_path.is_file():
            continue
        rel = ref_path.relative_to(skill_path).as_posix()
        if "examples/" in rel or "templates/" in rel:
            continue
        try:
            text = ref_path.read_text(encoding="utf-8")
        except Exception:
            continue
        fm = _extract_frontmatter(text)
        if fm is None or "trigger-when" not in fm:
            missing.append(rel)
    if missing:
        preview = missing[:10]
        message = (
            "references files missing 'trigger-when' frontmatter (warning):\n  - "
            + "\n  - ".join(preview)
        )
        if len(missing) > len(preview):
            message += f"\n  - ... and {len(missing) - len(preview)} more"
        return False, message
    return True, "All references declare a trigger-when"


def collect_local_markdown_targets(content: str) -> list[tuple[str, str]]:
    targets: list[tuple[str, str]] = []
    link_pattern = re.compile(r"!?\[[^\]]+\]\(([^)]+)\)")
    external_scheme_pattern = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")

    in_fence = False
    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        for match in link_pattern.finditer(raw_line):
            raw_target = match.group(1).strip()
            if not raw_target:
                continue
            if raw_target.startswith("<") and raw_target.endswith(">"):
                raw_target = raw_target[1:-1].strip()
            if not raw_target or external_scheme_pattern.match(raw_target):
                continue

            target_without_query = raw_target.split("?", 1)[0].strip()
            target_without_anchor = target_without_query.split("#", 1)[0].strip()
            if not target_without_anchor or target_without_anchor.startswith("/"):
                continue

            targets.append((raw_target, target_without_anchor))

    return targets


def validate_main_skill_reference_navigation(content: str) -> list[str]:
    warnings: list[str] = []
    local_targets = collect_local_markdown_targets(content)

    excessive_depth_targets: list[str] = []
    for raw_target, target_path in local_targets:
        parts = [part for part in Path(target_path).parts if part not in {".", ""}]
        if not parts:
            continue

        root = parts[0]
        if root == "references":
            # Allow one semantic bucket under references, e.g. references/authoring/foo.md.
            if len(parts) >= 4:
                excessive_depth_targets.append(raw_target)
        elif root in {"scripts", "assets", "agents"}:
            # These directories are usually navigated directly; nesting past one subdir is noisy.
            if len(parts) >= 3:
                excessive_depth_targets.append(raw_target)

    if excessive_depth_targets:
        preview = ", ".join(f"`{target}`" for target in excessive_depth_targets[:4])
        suffix = ""
        if len(excessive_depth_targets) > 4:
            suffix = f" and {len(excessive_depth_targets) - 4} more"
        warnings.append(
            "Main SKILL.md contains direct links that jump deeper than the preferred semantic"
            f" bucket depth: {preview}{suffix}. Meaningful multi-level directories are allowed,"
            " but prefer avoiding direct jumps beyond paths like references/<category>/<file>.md"
            " unless the extra nesting materially improves navigation."
        )

    return warnings


def validate_project_doc_frontmatter(frontmatter: dict, doc_label: str) -> list[str]:
    errors: list[str] = []

    for required_key in ("name", "description"):
        value = frontmatter.get(required_key)
        if not is_nonempty_string(value):
            errors.append(f"{doc_label} missing non-empty frontmatter key: {required_key}")

    resolved_version = get_resolved_project_version(frontmatter)
    if not resolved_version:
        errors.append(
            f"{doc_label} missing project version metadata: add top-level 'version' or"
            " 'metadata.version'"
        )

    top_level_version, metadata_version = get_project_version_sources(frontmatter)
    if top_level_version and metadata_version and top_level_version != metadata_version:
        errors.append(
            f"{doc_label} project version mismatch between top-level version and"
            f" metadata.version: version={top_level_version}, metadata.version={metadata_version}"
        )

    return errors


def validate_example_input_templates(skill_path: Path):
    """返回 (ok, message, notes)：notes 为归档作者体系结构的建议，不阻断。"""
    templates_reference_dir = skill_path / "references" / "templates"
    examples_dir = skill_path / "references" / "examples"
    required_sections = [
        "## 适用场景",
        "## 建议提供的信息",
        "## 可直接复制输入模板",
    ]
    # v2.4.0 反向审计：命名 / 固定三章节 / 「不负责工作流路由」/ 速查表 4 项出自归档作者体系
    # （docs/archive/references/authoring/progressive-disclosure-patterns.md:98，原文措辞即「结构建议」），
    # 原先却是 blocker；版本纪律与 frontmatter 完整性仍阻断。
    blocking: list[str] = []   # 仓库版本纪律与 frontmatter 完整性：仍阻断
    notes: list[str] = []     # 归档作者体系结构（命名/固定章节/速查表）：只提示

    if templates_reference_dir.exists():
        for markdown_path in sorted(templates_reference_dir.rglob("*.md")):
            if not markdown_path.is_file():
                continue

            try:
                frontmatter, content = load_markdown_document(markdown_path)
            except Exception as exc:
                blocking.append(f"{markdown_path.relative_to(skill_path)} frontmatter error: {exc}")
                continue

            blocking.extend(
                validate_project_doc_frontmatter(
                    frontmatter, str(markdown_path.relative_to(skill_path))
                )
            )

            version_sync_valid, version_sync_message = validate_version_consistency(
                frontmatter, content, skill_path=skill_path
            )
            if not version_sync_valid:
                blocking.append(f"{markdown_path.relative_to(skill_path)} {version_sync_message}")

            history_pos_valid, history_pos_message = validate_version_history_position(
                content,
                doc_label=str(markdown_path.relative_to(skill_path)),
                skill_path=skill_path,
            )
            if not history_pos_valid:
                blocking.append(f"{markdown_path.relative_to(skill_path)} {history_pos_message}")

            history_count_valid, history_count_message = validate_version_history_entry_count(
                content, skill_path=skill_path
            )
            if not history_count_valid:
                blocking.append(f"{markdown_path.relative_to(skill_path)} {history_count_message}")

    if not examples_dir.exists():
        if blocking:
            preview = blocking[:10]
            message = "Input template validation failed:\n  - " + "\n  - ".join(preview)
            if len(blocking) > len(preview):
                message += f"\n  - ... and {len(blocking) - len(preview)} more"
            return False, message, notes
        return True, "Input templates are valid", notes

    for markdown_path in sorted(examples_dir.rglob("*.md")):
        if not markdown_path.is_file():
            continue
        if markdown_path.name == "index.md":
            continue

        try:
            frontmatter, content = load_markdown_document(markdown_path)
        except Exception as exc:
            blocking.append(f"{markdown_path.relative_to(skill_path)} frontmatter error: {exc}")
            continue

        if not re.match(r"^input-template-[a-z0-9-]+\.md$", markdown_path.name):
            notes.append(
                f"{markdown_path.relative_to(skill_path)} 建议改用 'input-template-<english-slug>.md' 命名"
                "（归档作者体系约定，v2.4.0 起不阻断）"
            )

        blocking.extend(
            validate_project_doc_frontmatter(frontmatter, str(markdown_path.relative_to(skill_path)))
        )

        missing_sections = [section for section in required_sections if section not in content]
        if missing_sections:
            notes.append(
                f"{markdown_path.relative_to(skill_path)} 可按建议补示例章节 "
                + ", ".join(missing_sections) + "（示例模板结构建议，不阻断）"
            )

        if "不负责工作流路由" not in content:
            notes.append(
                f"{markdown_path.relative_to(skill_path)} 可显式声明「不负责工作流路由」（归档作者体系约定，不阻断）"
            )

        version_sync_valid, version_sync_message = validate_version_consistency(
            frontmatter, content, skill_path=skill_path
        )
        if not version_sync_valid:
            blocking.append(f"{markdown_path.relative_to(skill_path)} {version_sync_message}")

        history_pos_valid, history_pos_message = validate_version_history_position(
            content,
            doc_label=str(markdown_path.relative_to(skill_path)),
            skill_path=skill_path,
        )
        if not history_pos_valid:
            blocking.append(f"{markdown_path.relative_to(skill_path)} {history_pos_message}")

        history_count_valid, history_count_message = validate_version_history_entry_count(content, skill_path=skill_path)
        if not history_count_valid:
            blocking.append(f"{markdown_path.relative_to(skill_path)} {history_count_message}")

    index_path = examples_dir / "index.md"
    if any(
        path.is_file() and re.match(r"^input-template-[a-z0-9-]+\.md$", path.name)
        for path in examples_dir.iterdir()
    ):
        if not index_path.exists():
            notes.append("references/examples/index.md 缺失（沿用示例速查表时才需要，不阻断）")
        else:
            index_content = index_path.read_text(encoding="utf-8")
            if "| 示例文件 | 场景内容 | 对应工作流 |" not in index_content:
                notes.append(
                    "references/examples/index.md 建议含表头 | 示例文件 | 场景内容 | 对应工作流 |（不阻断）"
                )

    if blocking:
        preview = blocking[:10]
        message = "示例模板校验失败：\n  - " + "\n  - ".join(preview)
        if len(blocking) > len(preview):
            message += f"\n  - ... and {len(blocking) - len(preview)} more"
        return False, message, notes

    return True, "Input templates are valid", notes


def count_workflow_headers(content: str) -> int:
    return len(re.findall(WORKFLOW_HEADER_RE, content))


def validate_workflow_identification_pattern(skill_path: Path, content: str) -> list[str]:
    """Routing-matrix consistency: advisory only, never blocks."""
    warnings = []

    if re.search(NONSTANDARD_WORKFLOW_HEADER_RE, content):
        warnings.append(
            "RECOMMENDED: Found nonstandard '### ' headers. Use '## ' for main and"
            " child workflows to stay consistent with the skill markup guide and avoid parser"
            " drift."
        )

    has_matrix_header = bool(
        re.search(r"^\|\s*场景\s*\|\s*命中信号\s*\|\s*跳转到\s*\|", content, re.MULTILINE)
    )
    has_strong_rules = bool(re.search(r"^#{2,4}.*强规则", content, re.MULTILINE))
    workflow_count = count_workflow_headers(content)

    examples_dir = skill_path / "references" / "examples"
    has_example_templates = False
    if examples_dir.exists():
        has_example_templates = any(
            path.is_file() and re.match(r"^input-template-[a-z0-9-]+\.md$", path.name)
            for path in examples_dir.rglob("input-template-*.md")
        )

    # v2.4.0 反向审计：以下三条原为 blocker 并标 incident-backed，实测三点不成立——
    # (1) 判据出自已归档的作者体系（docs/archive/references/authoring/versioning-and-validation.md:96、
    #     business-to-workflow-mapping.md:89），归档原文本身是「若采用则成套」的条件建议；
    # (2) 判定 key 在 `### @步骤N:` 标记上，而本技能 creation.md:130 明令禁止注入步骤级标记，
    #     按自家规范写的技能一旦用矩阵就永远过不了；
    # (3) 没有任何事故登记支撑 blocker 级别。
    # 因 AGENTS.md「架构偏好」仍保留矩阵/强规则写法，判据降为建议而不删除；「强规则」只认标题含该词。
    if has_matrix_header and not has_strong_rules:
        warnings.append(
            "RECOMMENDED: 用了决策矩阵（场景/命中信号/跳转到）但没有强规则摘要——工作流 ≥2 时建议在"
            " SKILL.md 加一小节强规则摘要（普通标题即可，不要求 @步骤N: 标记）"
        )
    if has_strong_rules and not has_matrix_header:
        warnings.append(
            "RECOMMENDED: 定义了强规则摘要但没有决策矩阵，二者易漂移——考虑补一张路由决策矩阵或"
            "删掉多余的摘要节"
        )
    if has_matrix_header and has_example_templates:
        index_path = examples_dir / "index.md"
        if not index_path.exists():
            warnings.append(
                "RECOMMENDED: 同时用了决策矩阵与 input-template 素材，但缺 references/examples/index.md"
                "（归档作者体系的速查表；v2 不强制）"
            )
        else:
            index_content = index_path.read_text(encoding="utf-8")
            has_index_section = "## 决策矩阵命中速查" in index_content
            has_index_table = bool(
                re.search(
                    r"^\|\s*用户常见说法\s*\|\s*命中矩阵行\s*\|\s*建议先打开\s*\|",
                    index_content,
                    re.MULTILINE,
                )
            )
            if not (has_index_section and has_index_table):
                warnings.append(
                    "RECOMMENDED: references/examples/index.md 缺「决策矩阵命中速查」节或其速查表"
                    "（沿用归档作者体系时才需要；v2 不强制）"
                )

    if workflow_count >= 3 and not (has_matrix_header and has_strong_rules):
        warnings.append(
            "RECOMMENDED: This skill has 3 or more workflow headers; consider using a routing"
            " decision matrix plus a strong-rules summary in SKILL.md for more stable workflow"
            " recognition"
        )
    if (
        has_example_templates
        and workflow_count >= 2
        and not (has_matrix_header and has_strong_rules)
    ):
        warnings.append(
            "RECOMMENDED: This skill already maintains scenario input templates; if workflow"
            " routing is becoming ambiguous, add a decision matrix and a quick-reference table in"
            " references/examples/index.md"
        )

    return warnings


def format_validation_report(
    spec_errors: list[str],
    project_errors: list[str],
    spec_warnings: list[str],
    project_warnings: list[str],
) -> str:
    lines: list[str] = []
    is_valid = not spec_errors and not project_errors
    lines.append("Skill is valid!" if is_valid else "Skill validation failed!")

    if spec_errors:
        lines.append("Spec errors:")
        lines.extend(f"  - {entry['message']}" for entry in spec_errors)
    elif spec_warnings:
        lines.append("Spec checks: passed with warnings")
    else:
        lines.append("Spec checks: passed")

    if project_errors:
        lines.append("Project errors:")
        lines.extend(f"  - {entry['message']}" for entry in project_errors)
    elif project_warnings:
        lines.append("Project checks: passed with warnings")
    else:
        lines.append("Project checks: passed")

    if spec_warnings:
        lines.append("Spec warnings:")
        lines.extend(f"  - {entry['message']}" for entry in spec_warnings)

    if project_warnings:
        lines.append("Project warnings:")
        lines.extend(f"  - {entry['message']}" for entry in project_warnings)

    return "\n".join(lines)


def validate_skill(skill_path):
    """Basic validation of a skill（向后兼容包装，findings 版见 validate_skill_detailed）"""
    valid, message, _findings = validate_skill_detailed(skill_path)
    return valid, message


def validate_skill_detailed(skill_path, profile: str = "standard"):
    """校验并返回 (valid, message, findings)。

    目标驱动 profile（分层声明见 references/config/script-profiles.yaml）：
    - strict / standard：官方硬约束 + 事故背书约束判 blocker；风格类（style-regex）降为 warn。
      Phase 2：每条 finding 携带 rule_class（来自 script-profiles.yaml，现由代码消费），
      severity 由 profile 的 fail_on 推导。
    - advisory：只报不判——findings 照常输出，但 valid 恒为 True（AI 探索阶段用）。
    """
    skill_path = Path(skill_path)

    skill_ok, skill_message = ensure_skill_path(skill_path)
    if not skill_ok:
        # 三个返回元素必须齐全：main() 以 (valid, message, findings) 解包，
        # 少一个元素会让坏路径变成 ValueError 崩溃而不是报告。
        return False, skill_message, []

    try:
        frontmatter, content = load_skill_document(skill_path)
    except Exception as e:
        # 未加引号的 description 含 `: ` 时 YAML 直接解析失败——这是要报给作者的缺陷，
        # 不是运行环境错误，因此按 FAIL 返回并给可执行的修复建议。
        # 建议同时进 message：main() 的非 --json 路径只渲染 message，findings 不会被打印。
        hint = ('修复建议：description 用双引号包裹成单行 string（description: "…"），'
                "并确认 YAML 键值缩进一致")
        return False, f"frontmatter 解析失败：{e}\n  - {hint}", [{
            "rule_class": "official-hard",
            "message": hint,
            "severity": "blocker",
        }]

    spec_errors: list[dict] = []
    spec_warnings: list[dict] = []
    project_errors: list[dict] = []
    project_warnings: list[dict] = []

    if not YAML_AVAILABLE:
        append_warning(
            spec_warnings,
            "spec",
            "PyYAML 不可用，frontmatter 走降级解析：值类型判据（如 metadata 值必须为 string，"
            "裸 true/1/null 会被当成字符串）本轮未生效，报告 PASS 不代表类型合规",
        )

    unexpected_keys = set(frontmatter.keys()) - ALL_ALLOWED_PROPERTIES
    if unexpected_keys:
        append_warning(
            project_warnings,
            "project",
            (
                "Unexpected top-level frontmatter key(s): "
                f"{', '.join(sorted(unexpected_keys))}. Prefer moving custom fields into metadata"
            ),
        )

    name = frontmatter.get("name")
    if name is None:
        append_error(spec_errors, "spec", "Missing 'name' in frontmatter")
    elif not isinstance(name, str):
        append_error(spec_errors, "spec", f"Name must be a string, got {type(name).__name__}")
    else:
        normalized_name = name.strip()
        if not normalized_name:
            append_error(spec_errors, "spec", "Name must be a non-empty string")
        elif not re.match(r"^[a-z0-9-]+$", normalized_name):
            append_error(
                spec_errors,
                "spec",
                (
                    f"Name '{normalized_name}' should be kebab-case (lowercase letters, digits,"
                    " and hyphens only)"
                ),
            )
        else:
            if normalized_name.startswith("-") or normalized_name.endswith("-") or "--" in normalized_name:
                append_error(
                    spec_errors,
                    "spec",
                    (
                        f"Name '{normalized_name}' cannot start/end with hyphen or contain"
                        " consecutive hyphens"
                    ),
                )
            if len(normalized_name) > 64:
                append_error(
                    spec_errors,
                    "spec",
                    f"Name is too long ({len(normalized_name)} characters). Maximum is 64 characters.",
                )
            if normalized_name != skill_path.resolve().name:
                append_error(
                    spec_errors,
                    "spec",
                    (
                        "Name must match the parent directory name: "
                        f"frontmatter={normalized_name}, directory={skill_path.resolve().name}"
                    ),
                )

    description = frontmatter.get("description")
    if description is None:
        append_error(spec_errors, "spec", "Missing 'description' in frontmatter")
    elif not isinstance(description, str):
        append_error(
            spec_errors,
            "spec",
            f"Description must be a string, got {type(description).__name__}",
        )
    else:
        normalized_description = description.strip()
        if not normalized_description:
            append_error(spec_errors, "spec", "Description must be a non-empty string")
        else:
            if "<" in normalized_description or ">" in normalized_description:
                append_error(
                    spec_errors, "spec", "Description cannot contain angle brackets (< or >)"
                )
            if len(normalized_description) > 1024:
                append_error(
                    spec_errors,
                    "spec",
                    (
                        "Description is too long "
                        f"({len(normalized_description)} characters). Maximum is 1024 characters."
                    ),
                )
            # 结构检查与长度互不遮蔽：超长描述仍要报出引号/转义/占位符问题
            try:
                raw_skill_text = (Path(skill_path) / "SKILL.md").read_text(encoding="utf-8")
            except OSError:
                raw_skill_text = ""
            symbol_problems, symbol_advisories = validate_description_symbols(raw_skill_text)
            for problem in symbol_problems:
                append_error(spec_errors, "spec", f"Description symbol: {problem}")
            for advice in symbol_advisories:
                append_warning(project_warnings, "project", f"Description style: {advice}")
            desc_ok, desc_message, desc_severity = validate_description_format(frontmatter)
            if not desc_ok or desc_severity == "error":
                append_error(spec_errors, "spec", f"Description format: {desc_message}")

    license_value = frontmatter.get("license")
    if license_value is not None:
        if not isinstance(license_value, str):
            append_error(
                spec_errors, "spec", f"License must be a string, got {type(license_value).__name__}"
            )
        elif not license_value.strip():
            append_error(spec_errors, "spec", "License cannot be an empty string when provided")

    compatibility = frontmatter.get("compatibility")
    if compatibility is not None:
        if not isinstance(compatibility, str):
            append_error(
                spec_errors,
                "spec",
                f"Compatibility must be a string, got {type(compatibility).__name__}",
            )
        else:
            normalized_compatibility = compatibility.strip()
            if not normalized_compatibility:
                append_error(
                    spec_errors, "spec", "Compatibility cannot be an empty string when provided"
                )
            elif len(normalized_compatibility) > 500:
                append_error(
                    spec_errors,
                    "spec",
                    (
                        "Compatibility is too long "
                        f"({len(normalized_compatibility)} characters). Maximum is 500 characters."
                    ),
                )

    metadata = frontmatter.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict):
            append_error(
                spec_errors, "spec", f"Metadata must be a mapping, got {type(metadata).__name__}"
            )
        else:
            for key, value in metadata.items():
                if not isinstance(key, str):
                    append_error(spec_errors, "spec", "Metadata keys must all be strings")
                if not isinstance(value, str):
                    append_error(
                        spec_errors,
                        "spec",
                        f"Metadata value for '{key}' must be a string, got {type(value).__name__}",
                    )

    allowed_tools = frontmatter.get("allowed-tools")
    if allowed_tools is not None:
        if not isinstance(allowed_tools, str):
            append_error(
                spec_errors,
                "spec",
                f"allowed-tools must be a string, got {type(allowed_tools).__name__}",
            )
        elif not allowed_tools.strip():
            append_error(
                spec_errors, "spec", "allowed-tools cannot be an empty string when provided"
            )

    is_builder, builder_reason = is_builder_class_skill(content)
    append_warning(
        project_warnings,
        "project",
        f"Semantic markup classification: {'builder-class' if is_builder else 'runtime-class'} "
        f"— {builder_reason}",
    )
    markup_valid, markup_message = validate_semantic_markup(content, skill_is_builder=is_builder)
    if not markup_valid:
        append_error(project_errors, "project", markup_message, rule_class="incident-backed")

    history_position_valid, history_position_message = validate_version_history_position(content, skill_path=skill_path)
    if not history_position_valid:
        append_error(project_errors, "project", history_position_message, rule_class="incident-backed")

    history_valid, history_message = validate_version_history_length(content, skill_path=skill_path)
    if not history_valid:
        append_error(project_errors, "project", history_message, rule_class="incident-backed")

    version_sync_valid, version_sync_message = validate_version_consistency(frontmatter, content, skill_path=skill_path)
    if not version_sync_valid:
        append_error(project_errors, "project", version_sync_message, rule_class="incident-backed")

    placeholders_valid, placeholders_message = validate_template_placeholders(content)
    if not placeholders_valid:
        append_error(project_errors, "project", placeholders_message, rule_class="incident-backed")

    example_templates_valid, example_templates_message, example_template_notes = (
        validate_example_input_templates(skill_path)
    )
    if not example_templates_valid:
        append_error(project_errors, "project", example_templates_message, rule_class="incident-backed")
    for note in example_template_notes:
        append_warning(project_warnings, "project", note)

    for warning in validate_workflow_identification_pattern(skill_path, content):
        append_warning(project_warnings, "project", warning)

    body_line_count = get_body_line_count(content)
    if body_line_count > 500:
        append_warning(
            project_warnings,
            "project",
            (
                f"SKILL.md body is {body_line_count} lines after frontmatter; keep it at or below"
                " 500 lines when possible by moving details into references/"
            ),
        )
    for warning in validate_main_skill_reference_navigation(content):
        append_warning(project_warnings, "project", warning)

    links_valid, links_message = validate_markdown_links(skill_path)
    if not links_valid:
        append_error(project_errors, "project", links_message, rule_class="incident-backed")

    asset_paths_valid, asset_paths_message = validate_referenced_asset_paths(skill_path)
    if not asset_paths_valid:
        append_error(project_errors, "project", asset_paths_message, rule_class="incident-backed")

    ref_trigger_valid, ref_trigger_message = validate_reference_trigger_when(skill_path)
    if not ref_trigger_valid:
        append_warning(project_warnings, "project", ref_trigger_message)

    fail_on = PROFILES.get(profile, PROFILES["standard"])

    def _severity(rule_class: str, is_error: bool) -> str:
        if is_error:
            return "blocker"
        return "blocker" if rule_class in fail_on else "warn"

    findings = (
        [
            {
                "rule_class": f["rule_class"],
                "severity": _severity(f["rule_class"], True),
                "message": f["message"],
            }
            for f in spec_errors + project_errors
        ]
        + [
            {
                "rule_class": f["rule_class"],
                "severity": _severity(f["rule_class"], False),
                "message": f["message"],
            }
            for f in spec_warnings + project_warnings
        ]
    )
    message = format_validation_report(
        spec_errors=spec_errors,
        project_errors=project_errors,
        spec_warnings=spec_warnings,
        project_warnings=project_warnings,
    )
    valid = not spec_errors and not project_errors
    if profile == "advisory":
        valid = True
    return valid, message, findings


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="skill_cli.py validate", description="Run static SKILL.md validation"
    )
    parser.add_argument("skill_path", help="Skill directory")
    parser.add_argument(
        "--profile",
        choices=["strict", "standard", "advisory"],
        default="standard",
        help=(
            "strict/standard: hard boundaries FAIL (Phase 1 identical); "
            "advisory: findings only, never a verdict"
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Structured findings output (goal-driven script protocol)",
    )
    args = parser.parse_args(argv)

    valid, message, findings = validate_skill_detailed(args.skill_path, profile=args.profile)

    if args.json:
        import json

        print(
            json.dumps(
                {
                    "command": "validate",
                    "status": "PASS" if valid else "FAIL",
                    "profile": args.profile,
                    "decision_required": None,
                    "findings": findings,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        for line in message.split("\n"):
            print(line, file=sys.stderr)
        return 0 if valid else 1

    lines = message.split("\n")
    # First line is status → stdout; errors/warnings → stderr
    if lines:
        print(lines[0])
    if args.profile == "advisory":
        print("[advisory profile] findings only — not a PASS/FAIL verdict")
    for line in lines[1:]:
        print(line, file=sys.stderr)
    return 0 if valid else 1
