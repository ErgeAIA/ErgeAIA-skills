#!/usr/bin/env python3
"""
Hard validation for the zuiti skill (嘴替).

Validates the skill itself (structure / safety contract), NOT its output.
Mechanically enforces safety hard rule A2: every quote/典故 entry in the
verified drawer must carry a [核验] marker plus an explicit source — no
fabricated attributions allowed.

Output contract:
- Success message goes to stdout (exit 0).
- Every error goes to stderr (exit 1) and carries an actionable fix hint.

Performance note (v0.3.5): each drawer file is read and parsed exactly ONCE —
the [核验] / 来源 / 同文重复 checks all run in a single pass over a lazily
iterated file handle. Previously the duplicate check re-read and re-parsed
both drawers, costing ~47% of verify() runtime and doubling drawer I/O.
"""

import argparse
import re
import sys
from pathlib import Path

# Precompiled once at import time (avoids per-call re-cache lookup in the
# per-line hot loop).
_QUOTE_RE = re.compile(r"「(.+?)」")
_PUNCT_RE = re.compile(r"[\s\[\]（）()，。、！？.,:：]")


def _quote_key(line: str) -> str:
    """Extract a normalized quote key from a drawer entry line.

    Uses the content inside the first 「」 pair if present, otherwise the
    text before the first em-dash. Whitespace / punctuation / brackets are
    stripped and the result lowercased, so near-identical quotes collide.
    """
    s = line.strip()
    m = _QUOTE_RE.search(s)
    core = m.group(1) if m else s.partition("—")[0]
    return _PUNCT_RE.sub("", core).lower()


def _check_drawer(
    drawer_path: Path,
    errors: list[tuple[str, str]],
    label: str,
    source_markers: tuple[str, ...],
) -> None:
    """Single-pass drawer validation: [核验] + 来源/出处 + 抽屉内同文重复.

    Reads the file once and iterates it lazily (memory O(longest line)
    instead of O(file size)), running all three checks per entry line.

    - `source_markers`: accepted source markers, e.g. ("来源", "出处") for
      the quote drawer or ("来源",) for the meme drawer.
    - Duplicate detection is within a single file only; cross-drawer
      intentional reuse (e.g. a quote and a meme) is allowed.
    """
    seen: dict[str, int] = {}
    with drawer_path.open(encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            s = line.strip()
            if not s.startswith("- "):
                continue
            if "[核验]" not in s:
                errors.append((
                    f"{label}:{i} 缺 [核验] 标记：{s[:40]}",
                    "为该条目补 [核验] 标记，或删除非条目行",
                ))
            if not any(marker in s for marker in source_markers):
                errors.append((
                    f"{label}:{i} 缺 来源/出处：{s[:40]}",
                    "为该条目补 '来源：' 字段",
                ))
            key = _quote_key(s)
            if not key:
                continue
            if key in seen:
                errors.append((
                    f"{label}:{i} 抽屉内同文重复：与第 {seen[key]} 行重复「{key[:30]}」",
                    "删除/合并重复条目，或改为不同引文（防 R3 回归）",
                ))
            else:
                seen[key] = i


def verify(skill_dir: Path) -> list[tuple[str, str]]:
    """Return list of (error_msg, fix_hint) tuples; empty means pass."""
    errors: list[tuple[str, str]] = []

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append(("Missing SKILL.md", "确认 SKILL.md 存在于技能根目录"))
    else:
        text = skill_md.read_text(encoding="utf-8")
        if "## @工作流:" not in text:
            errors.append((
                "SKILL.md 缺少 '## @工作流:' 头（builder-class 标记）",
                "补一个 '## @工作流:' 主流程段",
            ))
        if "⚠️ 未过审" not in text:
            errors.append((
                "SKILL.md 缺少 ⚠️ 人工闸可见标 规范（安全硬规则 D10）",
                "在输出模板每条候选头部加 '⚠️ 未过审·发送前请人工核对'",
            ))
        if "可识别个人的虚假事实" not in text:
            errors.append((
                "SKILL.md 禁区缺少 A3 个人虚假事实红线",
                "在禁区文件加 '不断言可识别个人的虚假事实' 条款",
            ))
        if "格局" not in text:
            errors.append((
                "SKILL.md 未接入『格局·路转粉』风格（v0.2.5 新增）",
                "在哲学锚定/step-3/输出模板/交付前自检 补入 格局·路转粉",
            ))
        if "[TODO" in text or "YYYY-MM-DD" in text:
            errors.append((
                "SKILL.md 残留占位符",
                "替换/删除所有 TODO 与 YYYY-MM-DD 占位",
            ))

    quotes = skill_dir / "references" / "quotes-verified.md"
    if not quotes.exists():
        errors.append((
            "Missing references/quotes-verified.md（名言核验屉）",
            "创建核验屉文件，至少放几条带 [核验]+来源 的真实名言",
        ))
    else:
        _check_drawer(quotes, errors, "quotes-verified.md", ("来源", "出处"))

    memes = skill_dir / "references" / "net-memes-verified.md"
    if not memes.exists():
        errors.append((
            "Missing references/net-memes-verified.md（热梗核验屉）",
            "创建热梗核验屉文件，至少放几条带 [核验]+来源 的真实热梗",
        ))
    else:
        _check_drawer(memes, errors, "net-memes-verified.md", ("来源",))

    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True, help="Skill folder path")
    args = parser.parse_args()

    skill_dir = Path(args.skill).resolve()
    if not skill_dir.exists():
        print("ERROR: skill folder not found: " + str(skill_dir), file=sys.stderr)
        sys.exit(1)

    errors = verify(skill_dir)
    if errors:
        for msg, fix in errors:
            print(f"ERROR: {msg} | 修复建议：{fix}", file=sys.stderr)
        sys.exit(1)

    print("OK: zuiti 硬校验通过（禁区/D10/A2 物理落地）")
    sys.exit(0)


if __name__ == "__main__":
    main()
