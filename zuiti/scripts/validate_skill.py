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
"""

import argparse
import sys
from pathlib import Path


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
        for i, line in enumerate(quotes.read_text(encoding="utf-8").splitlines(), 1):
            s = line.strip()
            if not s.startswith("- "):
                continue
            if "[核验]" not in s:
                errors.append((
                    f"quotes-verified.md:{i} 缺 [核验] 标记：{s[:40]}",
                    "为该条目补 [核验] 标记，或删除非名言行",
                ))
            if "来源" not in s and "出处" not in s:
                errors.append((
                    f"quotes-verified.md:{i} 缺 来源/出处：{s[:40]}",
                    "为该条目补 '来源：' 字段",
                ))

    memes = skill_dir / "references" / "net-memes-verified.md"
    if memes.exists():
        for i, line in enumerate(memes.read_text(encoding="utf-8").splitlines(), 1):
            s = line.strip()
            if not s.startswith("- "):
                continue
            if "[核验]" not in s:
                errors.append((
                    f"net-memes-verified.md:{i} 缺 [核验] 标记：{s[:40]}",
                    "为该条目补 [核验] 标记，或删除非热梗行",
                ))
            if "来源" not in s:
                errors.append((
                    f"net-memes-verified.md:{i} 缺 来源：{s[:40]}",
                    "为该条目补 '来源：' 字段（平台+年份）",
                ))
    else:
        errors.append((
            "Missing references/net-memes-verified.md（热梗核验屉）",
            "创建热梗核验屉文件，至少放几条带 [核验]+来源 的真实热梗",
        ))

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
