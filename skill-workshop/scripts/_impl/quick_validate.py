"""
Quick validation script for skills - minimal version
"""

from pathlib import Path
import functools
import re
import sys

from .utils import ensure_skill_path, load_markdown_document, load_skill_document


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
WORKFLOW_HEADER_RE = re.compile(r"^#{2,3}\s+@工作流:\s*.+$", re.MULTILINE)
STRICT_WORKFLOW_HEADER_RE = re.compile(r"^##\s+@工作流:\s*.+$", re.MULTILINE)
NONSTANDARD_WORKFLOW_HEADER_RE = re.compile(r"^###\s+@工作流:\s*.+$", re.MULTILINE)


def append_error(bucket: list[str], scope: str, message: str) -> None:
    bucket.append(f"{scope}: {message}")


def append_warning(bucket: list[str], scope: str, message: str) -> None:
    bucket.append(f"{scope}: {message}")


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


def validate_semantic_markup(content):
    """
    Validate semantic markup requirements in SKILL.md content.

    Checks for:
    - At least one ## @工作流: header
    - At least one ### @步骤N: header
    - HTML comment metadata (@类型, @优先级, @验证点, @验证方式)
    - Action items using - @动作: format
    """
    errors = []

    # Check for workflow header (@工作流:)
    workflows = re.findall(WORKFLOW_HEADER_RE, content)
    if not workflows:
        errors.append("Missing required '@工作流:' header")

    # Check for step headers (### @步骤N:)
    step_pattern = r"^###\s+@步骤\d+:\s*.+$"
    steps = re.findall(step_pattern, content, re.MULTILINE)
    if not steps:
        errors.append("Missing required '### @步骤N:' headers (at least one step required)")

    # Check for HTML comment metadata in steps
    # Look for <!-- @类型: --> comments
    type_comment_pattern = r"<!--\s*@类型:\s*[^>]+-->"
    type_comments = re.findall(type_comment_pattern, content)
    if not type_comments:
        errors.append("Missing HTML comment metadata '@类型' (e.g., <!-- @类型: 操作步骤 -->)")

    # Check for @验证点 in content
    if "@验证点:" not in content:
        errors.append("Missing required '@验证点:' markers")

    # Check for @验证方式 in content
    if "@验证方式:" not in content:
        errors.append("Missing required '@验证方式:' markers")

    # Check for action items (- @动作:)
    action_pattern = r"^-\s+@动作:"
    actions = re.findall(action_pattern, content, re.MULTILINE)
    if not actions:
        errors.append("Missing action items (use '- @动作:' format for executable actions)")

    if errors:
        return False, "Semantic markup validation failed:\n  - " + "\n  - ".join(errors)

    return True, "Semantic markup is valid"


def validate_version_history_length(content, max_entries=5, *, skill_path: Path | None = None):
    # If no version history in content, check VERSION.md fallback
    has_history = bool(
        re.search(r"^##\s+(?:版本历史|Version History)\s*$", content, re.MULTILINE)
    )
    if not has_history and skill_path is not None:
        version_md = skill_path / "VERSION.md"
        if version_md.is_file():
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


def validate_description_format(frontmatter: dict) -> tuple[bool, str]:
    """V0/W7 description 联锁校验（见 spec.md §description 格式约束）。

    Returns (ok, message).
    """
    desc = frontmatter.get("description")
    if not desc:
        return False, "description 字段缺失"

    # YAML `|` 块被 yaml 库解析为带换行的 string（多行）。
    # 硬约束：description 必须是单行 string，检测换行符判断。
    if isinstance(desc, str) and "\n" in desc.strip():
        return False, (
            "description 包含换行符（疑似 YAML `|` 多行块），违反单行 string 硬约束。"
            "改为 description: <单行 string>"
        )

    # 1-1024 chars
    if len(desc) > 1024:
        return False, f"description 超过 1024 字符（当前 {len(desc)}）"

    # Pushy 句式
    pushy_patterns = [
        r"Use this skill whenever",
        r"Make sure to invoke it when",
        r"Invoke (this skill |on |when)",
        r"Make sure to use this skill",
    ]
    if not any(re.search(p, desc, re.IGNORECASE) for p in pushy_patterns):
        return False, (
            "description 缺少 Pushy 主动句式。"
            "应包含 'Use this skill whenever...' / 'Make sure to invoke it when...' / 'Invoke on...'"
        )

    # 触发词（至少 3 个，宽松匹配——引号内 / 中文词 / 英文 / 拼音都算）
    quoted_tokens = re.findall(r'[""「\']([^""」\']+)[""」\']', desc)
    # 中文 2+ 字 token
    chinese_chars = re.findall(r"[\u4e00-\u9fff]{2,}", desc)
    # 英文 2+ 字 token（去停用词）
    stopwords = {
        "this", "skill", "use", "when", "the", "and", "for", "with", "not", "from",
        "are", "but", "any", "all", "can", "has", "have", "had", "its", "you", "your",
        "whenever", "make", "sure", "invoke", "even", "explicitly", "ask", "mentions",
        "wants", "wants", "should", "would", "could", "should", "says", "want",
    }
    english_words_raw = re.findall(r"\b[A-Za-z][A-Za-z0-9\-_]{2,}\b", desc)
    english_words = [w for w in english_words_raw if w.lower() not in stopwords]
    # 中文顿号/斜杠/分号/逗号分隔的词也算
    slash_tokens = re.findall(r"[/、,，;；]\s*([\u4e00-\u9fffA-Za-z][\u4e00-\u9fffA-Za-z0-9\-_]*)", desc)
    trigger_count = len(set(quoted_tokens + chinese_chars + english_words + slash_tokens))
    if trigger_count < 3:
        return False, (
            f"description 触发词不足（找到 {trigger_count} 个，需 ≥ 3）。"
            "应列出至少 3 个核心触发词（中文 / 英文 / 拼音）"
        )

    return True, f"description 格式合规（{len(desc)} 字符，{trigger_count} 个触发词）"


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

    return None


def validate_version_consistency(frontmatter: dict, content: str, *, skill_path: Path | None = None):
    top_level_version, metadata_version = get_project_version_sources(frontmatter)
    resolved_version = top_level_version or metadata_version
    header_version = extract_header_version(content)
    history_version = extract_latest_version_history_entry(content)

    # Fallback: read version history from VERSION.md if not in SKILL.md
    if history_version is None and skill_path is not None:
        version_md = skill_path / "VERSION.md"
        if version_md.is_file():
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
        # SKILL.md 头部版本块与版本历史 section 都不是 LLM 决策必需；
        # 真实版本源是 frontmatter.metadata.version。
        # 当 VERSION.md 存在时，以下两个字段应作为人类参考而非 V0 硬约束——降级为 warning。
        if skill_path is not None and (skill_path / "VERSION.md").is_file():
            return (
                True,
                "Version fields are in sync (skipped header/history checks; VERSION.md fallback present)",
            )
        return (
            False,
            (
                "Missing version info in document header (add '> **版本**: vX.Y.Z' after the main"
                " title)"
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
        if skill_path is not None and (skill_path / "VERSION.md").is_file():
            return (
                True,
                "Version fields are in sync (skipped history check; VERSION.md fallback present)",
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
    re.compile(r"^##\s+@工作流:\s*主工作流名称\s*$"),
    re.compile(r"^###\s+@步骤1:\s*第一步标题\s*$"),
    re.compile(r"^###\s+@步骤2:\s*第二步标题\s*$"),
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
    """Return version history content from SKILL.md or VERSION.md fallback.

    If SKILL.md contains a '## 版本历史' section, use it.
    Otherwise, read VERSION.md from the same directory.
    """
    if re.search(r"^##\s+(?:版本历史|Version History)\s*$", content, re.MULTILINE):
        return content
    version_md = skill_path / "VERSION.md"
    if version_md.is_file():
        return version_md.read_text(encoding="utf-8")
    return content


def validate_version_history_position(content: str, doc_label: str = "SKILL.md", *, skill_path: Path | None = None):
    # If SKILL.md has no version history, check VERSION.md fallback
    has_history_in_content = bool(
        re.search(r"^##\s+(?:版本历史|Version History)\s*$", content, re.MULTILINE)
    )
    if not has_history_in_content and skill_path is not None:
        version_md = skill_path / "VERSION.md"
        if version_md.is_file():
            # Version history lives in VERSION.md — valid arrangement
            return True, "Version history is in VERSION.md"

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
    # If no version history in content, check VERSION.md fallback
    has_history = bool(
        re.search(r"^##\s+(?:版本历史|Version History)\s*$", content, re.MULTILINE)
    )
    if not has_history and skill_path is not None:
        version_md = skill_path / "VERSION.md"
        if version_md.is_file():
            content = version_md.read_text(encoding="utf-8")

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
    templates_reference_dir = skill_path / "references" / "templates"
    examples_dir = skill_path / "references" / "examples"
    required_sections = [
        "## 适用场景",
        "## 建议提供的信息",
        "## 可直接复制输入模板",
    ]
    templates_dir = skill_path / "references" / "templates"
    errors = []

    if templates_reference_dir.exists():
        for markdown_path in sorted(templates_reference_dir.rglob("*.md")):
            if not markdown_path.is_file():
                continue

            try:
                frontmatter, content = load_markdown_document(markdown_path)
            except Exception as exc:
                errors.append(f"{markdown_path.relative_to(skill_path)} frontmatter error: {exc}")
                continue

            errors.extend(
                validate_project_doc_frontmatter(
                    frontmatter, str(markdown_path.relative_to(skill_path))
                )
            )

            version_sync_valid, version_sync_message = validate_version_consistency(
                frontmatter, content, skill_path=skill_path
            )
            if not version_sync_valid:
                errors.append(f"{markdown_path.relative_to(skill_path)} {version_sync_message}")

            history_pos_valid, history_pos_message = validate_version_history_position(
                content,
                doc_label=str(markdown_path.relative_to(skill_path)),
                skill_path=skill_path,
            )
            if not history_pos_valid:
                errors.append(f"{markdown_path.relative_to(skill_path)} {history_pos_message}")

            history_count_valid, history_count_message = validate_version_history_entry_count(
                content, skill_path=skill_path
            )
            if not history_count_valid:
                errors.append(f"{markdown_path.relative_to(skill_path)} {history_count_message}")

    if not examples_dir.exists():
        if errors:
            preview = errors[:10]
            message = "Input template validation failed:\n  - " + "\n  - ".join(preview)
            if len(errors) > len(preview):
                message += f"\n  - ... and {len(errors) - len(preview)} more"
            return False, message
        return True, "Input templates are valid"

    for markdown_path in sorted(examples_dir.rglob("*.md")):
        if not markdown_path.is_file():
            continue
        if markdown_path.name == "index.md":
            continue

        try:
            frontmatter, content = load_markdown_document(markdown_path)
        except Exception as exc:
            errors.append(f"{markdown_path.relative_to(skill_path)} frontmatter error: {exc}")
            continue

        if not re.match(r"^input-template-[a-z0-9-]+\.md$", markdown_path.name):
            errors.append(
                f"{markdown_path.relative_to(skill_path)} should use"
                " 'input-template-<english-slug>.md' naming"
            )

        errors.extend(
            validate_project_doc_frontmatter(frontmatter, str(markdown_path.relative_to(skill_path)))
        )

        missing_sections = [section for section in required_sections if section not in content]
        if missing_sections:
            errors.append(
                f"{markdown_path.relative_to(skill_path)} missing sections: "
                + ", ".join(missing_sections)
            )

        if "不负责工作流路由" not in content:
            errors.append(
                f"{markdown_path.relative_to(skill_path)} must explicitly state '不负责工作流路由'"
            )

        version_sync_valid, version_sync_message = validate_version_consistency(
            frontmatter, content, skill_path=skill_path
        )
        if not version_sync_valid:
            errors.append(f"{markdown_path.relative_to(skill_path)} {version_sync_message}")

        history_pos_valid, history_pos_message = validate_version_history_position(
            content,
            doc_label=str(markdown_path.relative_to(skill_path)),
            skill_path=skill_path,
        )
        if not history_pos_valid:
            errors.append(f"{markdown_path.relative_to(skill_path)} {history_pos_message}")

        history_count_valid, history_count_message = validate_version_history_entry_count(content, skill_path=skill_path)
        if not history_count_valid:
            errors.append(f"{markdown_path.relative_to(skill_path)} {history_count_message}")

    index_path = examples_dir / "index.md"
    if any(
        path.is_file() and re.match(r"^input-template-[a-z0-9-]+\.md$", path.name)
        for path in examples_dir.iterdir()
    ):
        if not index_path.exists():
            errors.append("references/examples/index.md is missing")
        else:
            index_content = index_path.read_text(encoding="utf-8")
            if "| 示例文件 | 场景内容 | 对应工作流 |" not in index_content:
                errors.append(
                    "references/examples/index.md must include a table header: "
                    "| 示例文件 | 场景内容 | 对应工作流 |"
                )

    if errors:
        preview = errors[:10]
        message = "Input template validation failed:\n  - " + "\n  - ".join(preview)
        if len(errors) > len(preview):
            message += f"\n  - ... and {len(errors) - len(preview)} more"
        return False, message

    return True, "Input templates are valid"


def count_workflow_headers(content: str) -> int:
    return len(re.findall(WORKFLOW_HEADER_RE, content))


def validate_workflow_identification_pattern(skill_path: Path, content: str):
    errors = []
    warnings = []

    if re.search(NONSTANDARD_WORKFLOW_HEADER_RE, content):
        warnings.append(
            "RECOMMENDED: Found nonstandard '### @工作流:' headers. Use '## @工作流:' for main and"
            " child workflows to stay consistent with the skill markup guide and avoid parser"
            " drift."
        )

    has_matrix_header = bool(
        re.search(r"^\|\s*场景\s*\|\s*命中信号\s*\|\s*跳转到\s*\|", content, re.MULTILINE)
    )
    has_strong_rules_step = bool(
        re.search(r"^###\s+@步骤\d+:\s*.*强规则摘要.*$", content, re.MULTILINE)
    )
    workflow_count = count_workflow_headers(content)

    examples_dir = skill_path / "references" / "examples"
    has_example_templates = False
    if examples_dir.exists():
        has_example_templates = any(
            path.is_file() and re.match(r"^input-template-[a-z0-9-]+\.md$", path.name)
            for path in examples_dir.rglob("input-template-*.md")
        )

    if has_matrix_header and not has_strong_rules_step:
        errors.append(
            "SKILL.md uses the routing decision matrix table but is missing a matching '强规则摘要'"
            " step"
        )
    if has_strong_rules_step and not has_matrix_header:
        errors.append(
            "SKILL.md defines a '强规则摘要' step but is missing the routing decision matrix"
            " table header '| 场景 | 命中信号 | 跳转到 |' (whitespace-tolerant match)"
        )

    if has_matrix_header and has_example_templates:
        index_path = examples_dir / "index.md"
        if not index_path.exists():
            errors.append(
                "references/examples/index.md is missing (required when using the decision matrix"
                " pattern together with input templates)"
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
            if not has_index_section or not has_index_table:
                errors.append(
                    "references/examples/index.md must include '## 决策矩阵命中速查' and the"
                    " table header '| 用户常见说法 | 命中矩阵行 | 建议先打开 |' when the"
                    " decision matrix pattern is adopted"
                )

    if workflow_count >= 3 and not (has_matrix_header and has_strong_rules_step):
        warnings.append(
            "RECOMMENDED: This skill has 3 or more workflow headers; consider using a routing"
            " decision matrix plus a strong-rules summary in SKILL.md for more stable workflow"
            " recognition"
        )
    if (
        has_example_templates
        and workflow_count >= 2
        and not (has_matrix_header and has_strong_rules_step)
    ):
        warnings.append(
            "RECOMMENDED: This skill already maintains scenario input templates; if workflow"
            " routing is becoming ambiguous, add a decision matrix and a quick-reference table in"
            " references/examples/index.md"
        )

    if errors:
        return (
            False,
            "Workflow identification validation failed:\n  - " + "\n  - ".join(errors),
            warnings,
        )

    return True, "Workflow identification pattern is valid", warnings


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
        lines.extend(f"  - {message}" for message in spec_errors)
    elif spec_warnings:
        lines.append("Spec checks: passed with warnings")
    else:
        lines.append("Spec checks: passed")

    if project_errors:
        lines.append("Project errors:")
        lines.extend(f"  - {message}" for message in project_errors)
    elif project_warnings:
        lines.append("Project checks: passed with warnings")
    else:
        lines.append("Project checks: passed")

    if spec_warnings:
        lines.append("Spec warnings:")
        lines.extend(f"  - {message}" for message in spec_warnings)

    if project_warnings:
        lines.append("Project warnings:")
        lines.extend(f"  - {message}" for message in project_warnings)

    return "\n".join(lines)


def validate_skill(skill_path):
    """Basic validation of a skill"""
    skill_path = Path(skill_path)

    skill_ok, skill_message = ensure_skill_path(skill_path)
    if not skill_ok:
        return False, skill_message

    try:
        frontmatter, content = load_skill_document(skill_path)
    except Exception as e:
        return False, str(e)

    spec_errors: list[str] = []
    spec_warnings: list[str] = []
    project_errors: list[str] = []
    project_warnings: list[str] = []

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
            else:
                # 联锁校验：YAML 单行 + Pushy 句式 + 触发词 ≥ 3
                desc_format_ok, desc_format_message = validate_description_format(frontmatter)
                if not desc_format_ok:
                    append_error(spec_errors, "spec", f"Description format: {desc_format_message}")
                else:
                    append_warning(
                        project_warnings,
                        "project",
                        f"Description format: {desc_format_message}",
                    )

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

    markup_valid, markup_message = validate_semantic_markup(content)
    if not markup_valid:
        append_error(project_errors, "project", markup_message)

    history_position_valid, history_position_message = validate_version_history_position(content, skill_path=skill_path)
    if not history_position_valid:
        append_error(project_errors, "project", history_position_message)

    history_valid, history_message = validate_version_history_length(content, skill_path=skill_path)
    if not history_valid:
        append_error(project_errors, "project", history_message)

    version_sync_valid, version_sync_message = validate_version_consistency(frontmatter, content, skill_path=skill_path)
    if not version_sync_valid:
        append_error(project_errors, "project", version_sync_message)

    placeholders_valid, placeholders_message = validate_template_placeholders(content)
    if not placeholders_valid:
        append_error(project_errors, "project", placeholders_message)

    example_templates_valid, example_templates_message = validate_example_input_templates(skill_path)
    if not example_templates_valid:
        append_error(project_errors, "project", example_templates_message)

    routing_pattern_valid, routing_pattern_message, routing_pattern_warnings = (
        validate_workflow_identification_pattern(skill_path, content)
    )
    if not routing_pattern_valid:
        append_error(project_errors, "project", routing_pattern_message)
    for warning in routing_pattern_warnings:
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
        append_error(project_errors, "project", links_message)

    asset_paths_valid, asset_paths_message = validate_referenced_asset_paths(skill_path)
    if not asset_paths_valid:
        append_error(project_errors, "project", asset_paths_message)

    ref_trigger_valid, ref_trigger_message = validate_reference_trigger_when(skill_path)
    if not ref_trigger_valid:
        append_warning(project_warnings, "project", ref_trigger_message)

    message = format_validation_report(
        spec_errors=spec_errors,
        project_errors=project_errors,
        spec_warnings=spec_warnings,
        project_warnings=project_warnings,
    )
    return not spec_errors and not project_errors, message


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in {"-h", "--help"}:
        print("Usage: python scripts/skill_cli.py validate <skill_directory>")
        return 0
    if len(argv) != 1:
        print("Usage: python scripts/skill_cli.py validate <skill_directory>", file=sys.stderr)
        return 1

    valid, message = validate_skill(argv[0])
    lines = message.split("\n")
    # First line is status → stdout; errors/warnings → stderr
    if lines:
        print(lines[0])
    for line in lines[1:]:
        print(line, file=sys.stderr)
    return 0 if valid else 1
