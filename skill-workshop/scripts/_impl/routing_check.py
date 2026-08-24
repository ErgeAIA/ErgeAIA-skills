"""
Routing consistency check for skill-workshop.

Verifies three-way consistency between:
  1. SKILL.md §4 routing table (markdown table after "## 4. 渐进式披露")
  2. workflow files' reads-from: blocks (in frontmatter)
  3. authoring/specs/rubrics files' trigger-when: blocks (in frontmatter)

References: references/routing-table.md (the truth source)
Spec: references/authoring/versioning-and-validation.md §4 路由一致性

Usage:
    python -m scripts._impl.routing_check [SKILL_PATH]
    # default: Skills-Depot/ErgeAIA-skills/skill-workshop
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


WORKFLOW_FILES = [
    "references/workflows/W0-clarify.md",
    "references/workflows/W1-complexity.md",
    "references/workflows/W2-strengths.md",
    "references/workflows/W3-issues.md",
    "references/workflows/W4-workflow-split.md",
    "references/workflows/W5-recommendations.md",
    "references/workflows/W6-verdict.md",
    "references/workflows/W7-description-audit.md",
    "references/workflows/V0-validate.md",
]

# ---------- 文件读取缓存 ----------
_file_cache: dict[Path, str] = {}


def _cached_read(p: Path) -> str:
    if p not in _file_cache:
        _file_cache[p] = p.read_text(encoding="utf-8")
    return _file_cache[p]


def extract_frontmatter_block(content: str) -> str:
    """Return raw frontmatter text between --- markers, or empty string.

    Strips BOM if present, since some authoring tools write UTF-8 BOM.
    """
    # strip BOM
    if content.startswith("\ufeff"):
        content = content[1:]
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    for idx, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:idx])
    return ""


def extract_reads_from(frontmatter: str) -> list[str]:
    """Parse reads-from: list values from frontmatter.

    Strips inline ``#`` comments so entries like
    ``- references/specs/spec.md  # note`` resolve to the bare path.
    """
    lines = frontmatter.splitlines()
    in_block = False
    items: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("reads-from:"):
            in_block = True
            # inline value (rare)
            inline = stripped.split(":", 1)[1].strip()
            if inline and inline != "|":
                items.append(inline.strip('"').strip("'").split("#", 1)[0].strip())
            continue
        if in_block:
            if stripped.startswith("- "):
                item = stripped[2:].strip().strip('"').strip("'").split("#", 1)[0].strip()
                if item:
                    items.append(item)
            elif stripped and not stripped.startswith("-"):
                break
    return items


def extract_trigger_when(frontmatter: str) -> str | None:
    """Return trigger-when value or None.

    Accepts both bare values and double-quoted values:
      trigger-when: V0 合规校验阶段
      trigger-when: "V0 合规校验阶段"
    """
    for line in frontmatter.splitlines():
        # Capture: optional leading whitespace, "trigger-when:", value
        m = re.match(r"^\s*trigger-when:\s+(.+?)\s*$", line)
        if m:
            value = m.group(1)
            # strip matching double quotes
            if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            return value.strip()
    return None


def extract_skill_md_routing_table(skill_md: str) -> set[str]:
    """Extract referenced file basenames from SKILL.md §4 routing table.

    Heuristic: find "## 4. 渐进式披露" section, then collect all markdown
    links of the form [name](references/<path>) within that section.
    """
    if "## 4. 渐进式披露" not in skill_md:
        return set()
    section = skill_md.split("## 4. 渐进式披露", 1)[1]
    # cut at next ## heading
    section = re.split(r"^##\s+", section, maxsplit=1, flags=re.MULTILINE)[0]
    refs = set()
    for m in re.finditer(r"\[[^\]]+\]\((references/[^)]+)\)", section):
        refs.add(m.group(1))
    return refs


def extract_routing_table_workflow_refs(routing_table: str) -> dict[str, set[str]]:
    """Parse routing-table.md §4 workflow reads-from declarations.

    Each workflow section looks like:
        ### 4.2 W1-complexity.md
        ```
        reads-from:
          - references/rubrics/complexity-rubric.md  # comment
        ```
    Returns {workflow_filename: set(reads-from refs)}.
    """
    result: dict[str, set[str]] = {}
    sections = re.split(r"^###\s+4\.\d+\s+([\w-]+\.md)", routing_table, flags=re.MULTILINE)
    # sections[0] is the preamble; then alternating (filename, body)
    for i in range(1, len(sections), 2):
        wf_name = sections[i].strip()
        body = sections[i + 1]
        # extract first fenced code block
        m = re.search(r"```(.*?)```", body, re.S)
        if not m:
            continue
        refs: set[str] = set()
        for line in m.group(1).splitlines():
            stripped = line.strip()
            if stripped.startswith("- ") and "references/" in stripped:
                ref = stripped[2:].split("#", 1)[0].strip()
                if ref.startswith("references/"):
                    refs.add(ref)
        result[wf_name] = refs
    return result


def check_routing_consistency(skill_path: Path) -> list[str]:
    """Return list of error strings. Empty list = consistent."""
    errors: list[str] = []
    skill_md_path = skill_path / "SKILL.md"
    if not skill_md_path.exists():
        return [f"[routing-mismatch] SKILL.md not found at {skill_md_path}"]
    skill_md = _cached_read(skill_md_path)
    skill_table = extract_skill_md_routing_table(skill_md)

    # 1. Check workflow files' reads-from is consistent with themselves
    workflow_refs: set[str] = set()
    actual_by_workflow: dict[str, set[str]] = {}
    for wf_rel in WORKFLOW_FILES:
        wf_path = skill_path / wf_rel
        if not wf_path.exists():
            errors.append(f"[routing-mismatch] workflow file missing: {wf_rel}")
            continue
        content = _cached_read(wf_path)
        fm = extract_frontmatter_block(content)
        refs = extract_reads_from(fm)
        actual_by_workflow[Path(wf_rel).name] = {r for r in refs if r.startswith("references/")}
        for ref in refs:
            # normalize: references/... or external
            if ref.startswith("references/"):
                workflow_refs.add(ref)
                # Blind-spot fix: a reads-from target that does not exist is a
                # broken load instruction (e.g. a deleted file still referenced).
                if not (skill_path / ref).exists():
                    errors.append(
                        f"[routing-mismatch] reads-from missing target: {ref} (in {wf_rel})"
                    )

    # 2. Check all 9/9 authoring files have trigger-when
    for sub in ("authoring", "specs", "rubrics", "templates", "evaluation", "config"):
        sub_dir = skill_path / "references" / sub
        if not sub_dir.exists():
            continue
        for f in sub_dir.glob("*.md"):
            content = _cached_read(f)
            fm = extract_frontmatter_block(content)
            tw = extract_trigger_when(fm)
            if tw is None:
                rel = f.relative_to(skill_path).as_posix()
                errors.append(
                    f"[routing-mismatch] file={rel}, missing-from=trigger-when"
                )

    # 3. Cross-check: each ref in skill table should be loadable
    for ref in skill_table:
        if not (skill_path / ref).exists():
            errors.append(f"[routing-mismatch] SKILL.md table references missing file: {ref}")

    # 4. Cross-check: routing-table.md §4 declarations vs actual workflow reads-from
    # (truth-source consistency — v1.20.0 补读真源，此前仅做存在性检查)
    rt_path = skill_path / "references" / "routing-table.md"
    if rt_path.exists():
        rt = _cached_read(rt_path)
        declared = extract_routing_table_workflow_refs(rt)
        for wf_name, declared_refs in declared.items():
            actual_refs = actual_by_workflow.get(wf_name, set())
            missing = declared_refs - actual_refs
            extra = actual_refs - declared_refs
            if missing:
                errors.append(
                    f"[routing-mismatch] routing-table declares {wf_name} reads-from "
                    f"{sorted(missing)} but workflow frontmatter lacks them"
                )
            if extra:
                errors.append(
                    f"[routing-mismatch] routing-table missing declaration for {wf_name} "
                    f"reads-from {sorted(extra)}"
                )

    return errors


def main() -> int:
    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])
    else:
        # 默认指向本仓库根（脚本位于 scripts/_impl/，向上两级即 skill-workshop 根）。
        skill_path = Path(__file__).resolve().parents[2]

    errors = check_routing_consistency(skill_path)
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print("routing-consistency: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
