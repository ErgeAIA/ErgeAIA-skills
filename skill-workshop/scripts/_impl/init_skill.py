"""Skill Initializer - creates a pure-Markdown skill skeleton (v2)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from ._gate import require_plan

SKILL_TEMPLATE = """---
name: {skill_name}
description: "[TODO: 说明解决什么问题、何时触发。例如：帮助用户压缩 PDF，当用户说「帮我压缩 PDF」时触发。Not for: 通用文件管理]"
metadata:
  author: ErgeAIA
  version: "1.0.0"
---

# {skill_title}

## 定位

[这个 skill 是什么、不是什么。用 1–3 句写清用户任务单元。]

## 何时使用

- [触发场景 1，尽量使用用户真实说法中的关键词]
- [触发场景 2]
- Not for: [明确排除的相邻场景]

## 工作步骤

1. [读取什么输入 → 做出什么判断 → 产出什么]
2. [下一步]
3. [验证：如何确认任务完成]

## 输出契约

[必须产出的文件/字段/格式；失败时如何向用户报告。]

## 约束

- HARD: [不可违背项，如非破坏、不写密钥]
- CONDITIONAL: [仅有某能力时才要求]
- 禁止: [误用路径]

## 资源

细节按需读取 `references/` 下的具体文件（仅在技能确有需要时创建，不要预建空目录）。

## Gotchas

[仅当存在高概率反直觉失败时保留本节；否则删除整节。]

## Changelog

版本变更写入本技能根目录 `CHANGELOG.md`，不在正文维护版本历史块。
"""

CHANGELOG_TEMPLATE = """# 更新日志

skill-workshop 生成的占位变更记录。格式参考 Keep a Changelog。

## [1.0.0] - {date}

### 新增
- 初始 Skill 骨架
"""

README_TEMPLATE = """# {skill_title}

{skill_name}：由 skill-workshop `init` 生成。

- 主文档：`SKILL.md`
- 运行时校验：`python scripts/skill_cli.py validate .`（在技能目录或传入本目录路径）
- 字段规范：`python scripts/skill_cli.py spec .`

请先补全 `SKILL.md` 中的 TODO，再运行校验。
"""


def _validate_name(skill_name: str) -> list[str]:
    errors = []
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", skill_name or ""):
        errors.append(
            "skill name must be hyphen-case: lowercase letters, digits, single hyphens"
        )
    if skill_name and len(skill_name) > 64:
        errors.append("skill name must be <= 64 characters")
    return errors


def init_skill(skill_name: str, parent_path: str) -> Path | None:
    errors = _validate_name(skill_name)
    if errors:
        for e in errors:
            print(f"❌ {e}", file=sys.stderr)
        return None

    parent = Path(parent_path).resolve()
    skill_dir = parent / skill_name
    if skill_dir.exists():
        print(f"❌ Target already exists: {skill_dir}", file=sys.stderr)
        print("   Refusing to overwrite an existing skill directory.", file=sys.stderr)
        return None

    skill_title = skill_name.replace("-", " ").title()
    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        (skill_dir / "SKILL.md").write_text(
            SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=skill_title),
            encoding="utf-8",
        )
        from datetime import date

        (skill_dir / "CHANGELOG.md").write_text(
            CHANGELOG_TEMPLATE.format(date=date.today().isoformat()), encoding="utf-8"
        )
        (skill_dir / "README.md").write_text(
            README_TEMPLATE.format(skill_name=skill_name, skill_title=skill_title),
            encoding="utf-8",
        )
        # 可选目录不预建空树：与 references/creation.md「无则不要空目录」一致
    except OSError as e:
        print(f"❌ Error creating skill skeleton: {e}", file=sys.stderr)
        return None

    print(f"✅ Skill '{skill_name}' initialized at {skill_dir}")
    print("\nNext steps:")
    print("1. Edit SKILL.md — complete TODO items and write a real description")
    print("2. Create references/ or scripts/ only if the skill needs them (do not leave empty dirs)")
    print("3. Run: python scripts/skill_cli.py spec " + str(skill_dir))
    print("4. Run: python scripts/skill_cli.py validate " + str(skill_dir))
    return skill_dir


def main(argv: list[str] | None = None) -> int:
    import argparse

    usage_examples = [
        "  python scripts/skill_cli.py init my-new-skill --path ./skills",
        "  python scripts/skill_cli.py init my-api-helper --path ./skills --write",
    ]
    parser = argparse.ArgumentParser(
        prog="skill_cli.py init",
        description="Initialize a pure-Markdown skill skeleton",
        epilog="Skill name: hyphen-case, lowercase/digits/hyphens, <=64 chars.\nExamples:\n"
        + "\n".join(usage_examples),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("skill_name", help="Kebab-case skill name")
    parser.add_argument("--path", required=True, help="Parent directory for the new skill")
    parser.add_argument(
        "--write",
        action="store_true",
        help="actually create the skill skeleton (default: dry-run preview)",
    )
    parser.add_argument(
        "--plan",
        default=None,
        help="Plan-gate: path to five-section plan file (goal/scope/params/stop/rollback)",
    )
    parser.add_argument(
        "--plan-text",
        default=None,
        help="Plan-gate quick lane with a one-line plan (HUMANS ONLY; AI must use --plan)",
    )
    args = parser.parse_args(argv)

    name_errors = _validate_name(args.skill_name)
    if name_errors:
        for e in name_errors:
            print(f"❌ {e}", file=sys.stderr)
        return 2

    if not args.write:
        target = Path(args.path).resolve() / args.skill_name
        print("[dry-run] init preview")
        print(f"  would create: {target}")
        print("  files: SKILL.md, CHANGELOG.md, README.md only")
        print("  note: references/ scripts/ assets/ are optional — create only when needed")
        print("  add --write to actually create (plan-gate applies)")
        return 0

    require_plan(args.plan, args.plan_text, "init")
    print(f"Initializing skill: {args.skill_name}")
    print(f"Location: {args.path}")
    result = init_skill(args.skill_name, args.path)
    return 0 if result else 1


if __name__ == "__main__":
    raise SystemExit(main())
