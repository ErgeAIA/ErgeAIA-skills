"""
Skill Initializer - Creates a new skill from template

Usage:
    python scripts/skill_cli.py init <skill-name> --path <path>

Examples:
    python scripts/skill_cli.py init my-new-skill --path skills/public
    python scripts/skill_cli.py init my-api-helper --path skills/private
    python scripts/skill_cli.py init custom-skill --path /custom/location
"""

from pathlib import Path
import re
import sys

SKILL_TEMPLATE = """---
name: {skill_name}
description: "[TODO: 说明 Skill 解决什么问题，当用户说什么时会触发。例如：帮助用户压缩PDF文件，当用户说'帮我压缩PDF'时触发]"
metadata:
  author: ErgeAIA
  version: 1.0.0
---

# {skill_title}

<!-- @类型: Skill 概览 -->
<!-- @目的: 说明此 Skill 的核心能力和使用场景 -->

> **一句话**: [TODO: 用一句话概括此 Skill 的核心价值，例如："我是PDF压缩助手，帮用户减小文件体积"]
> **版本**: v1.0.0
> **用途**: [TODO: 一句话说明此 Skill 的用途]
> **适用范围**: [TODO: 说明适用场景]

## Overview

[TODO: 1-2 sentences explaining what this skill enables]

## 触发示例

用户说以下话时会触发此 Skill：

- "[TODO: 触发语句示例1，如：帮我压缩这个PDF]"
- "[TODO: 触发语句示例2，如：减小PDF文件大小]"
- "[TODO: 触发语句示例3]"

## 工程化脚本（推荐）

- `scripts/validate_skill.py`: 硬校验入口（验证 Skill 本身的结构/格式/版本一致性等，而非验证 Skill 产出物）
- `scripts/run.py`（可选）: 当涉及落盘修改/批量处理/严格格式输出时，按 `plan/apply/verify` 组织执行流程

在修改或打包前先运行：

```bash
python scripts/validate_skill.py --skill .
```

## @工作流: 主工作流名称

<!-- @类型: 标准操作流程(SOP) -->
<!-- @目的: 描述完成主要任务的标准流程 -->
<!-- @场景: 描述此工作流适用的具体场景 -->
<!-- @前置条件: 执行此工作流前需要满足的条件 -->
<!-- @后置验证: 工作流完成后的验收标准 -->
<!-- @ID: wf-main -->

### @步骤1: 第一步标题

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @验证点: 此步骤完成后应达到的状态 -->
<!-- @验证方式: 如何验证此步骤是否成功 -->
<!-- @ID: step-1 -->

- @动作: 具体的执行动作 1
- @动作: 具体的执行动作 2

@提示: 执行此步骤的注意事项或技巧

### @步骤2: 第二步标题

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @依赖: step-1 -->
<!-- @改动文件: 此步骤会修改的文件路径 -->
<!-- @产物: 此步骤产生的输出物 -->
<!-- @验证点: 验证此步骤成功的标准 -->
<!-- @验证方式: 验证方法 -->
<!-- @失败信号: 失败的标志（如退出码!=0） -->
<!-- @排查: 失败时的排查方法 -->
<!-- @ID: step-2 -->

- @动作: 执行具体操作的步骤

@工具: 使用工具或脚本示例

```bash
@命令类型: 命令类型（如脚手架、验证工具）
@用途: 命令的用途说明
@路径: 执行路径
@成功判定: 如何判断成功
@失败信号: 如何判断失败
具体命令放在这里
```

## 输出模式

<!-- @类型: 输出配置 -->
<!-- @说明: 根据 Skill 输出复杂度选择合适的模式 -->

本 Skill 使用以下输出模式（选择一项并删除其他）：

### 模式1: 严格模板（固定结构）
<!-- 适用: API响应、数据格式、标准化报告 -->
<!-- 特征: 输出结构固定，每个部分都有明确位置 -->

输出格式：
```
# [标题]

## 执行摘要
[关键发现概述]

## 详细结果
- 结果1
- 结果2

## 下一步
1. [建议1]
2. [建议2]
```

### 模式2: 灵活模板（可调整章节）
<!-- 适用: 分析报告、创意写作 -->
<!-- 特征: 有默认结构，但可根据情况调整 -->

输出格式：
```
# [标题]

## 概述
[内容]

## 分析
[根据具体情况调整章节]

## 结论
[内容]
```

### 模式3: 示例模式（风格敏感）
<!-- 适用: 代码生成、特定格式输出 -->
<!-- 特征: 通过示例展示期望风格 -->

参考示例：
- 示例1: [输入] → [输出]
- 示例2: [输入] → [输出]

---

## Resources

<!-- TODO: 根据 Skill 需求保留或删除以下目录 -->

### scripts/
可执行代码（Python/Bash等），用于需要确定性可靠性的任务。

推荐至少提供一个硬校验入口：

```bash
@命令类型: 验证工具
@用途: 在落盘修改/打包前做硬校验
@路径: scripts/
@成功判定: 退出码=0
@失败信号: 退出码!=0 或输出包含 ERROR
python scripts/validate_skill.py --skill .
```

### references/
参考文档，用于告知 Claude 过程和思考。

### references/templates/（可选）
当某个高频使用场景逐渐形成稳定输入方式时，在这里放“可直接复制的场景输入模板”。

- 这类文档只负责输入补全，不负责工作流路由
- 固定结构至少包含：`适用场景`、`建议提供的信息`、`可直接复制输入模板`
- 固定模板来源建议放在：`references/templates/<template-name>.md`

### references/examples/（可选）
当 `SKILL.md` 的工作流已经比较完整时，在这里放自动生成或人工收敛的“场景示例文档”。

- 自动生成的场景示例建议放在：`references/examples/input-template-<english-slug>.md`
- 可维护一个 `references/examples/index.md`，用表格列出示例文件、场景内容和对应工作流

```markdown
# <场景名称> 输入模板

> **用途**: 用于 `<场景名称>` 这个高频使用场景，帮助一次性给出高质量输入
> **边界**: 本文档不负责工作流路由；工作流应由目标 Skill 根据“目的”和“提供的信息”判断

## 适用场景
## 建议提供的信息
## 可直接复制输入模板
```

### assets/
输出资源，用于在最终输出中使用的文件（模板、图标等）。

**不需要的目录可以删除。**

---

## 版本历史

- **v1.0.0** (YYYY-MM-DD) - 初始版本
"""

VALIDATE_SKILL_SCRIPT = '''#!/usr/bin/env python3
"""
Validate-skill script for {skill_name}

This script validates the Skill itself (structure, frontmatter, semantic markup, etc.),
NOT the Skill's output or artifacts. It provides deterministic checks that complement
SKILL.md instructions.
"""

import argparse
import re
import sys
from pathlib import Path


def _read_text(path: Path):
    return path.read_text(encoding="utf-8")


def _extract_frontmatter(markdown: str):
    match = re.match(r"\\A---\\s*\\n([\\s\\S]*?)\\n---\\s*\\n", markdown)
    if not match:
        return None
    return match.group(1)


def _has_required_frontmatter(frontmatter: str):
    required_keys = ["name:", "description:"]
    return all(key in frontmatter for key in required_keys)


def _has_project_version(frontmatter: str):
    return "version:" in frontmatter


def verify(skill_dir: Path):
    errors = []

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("Missing SKILL.md: " + str(skill_md))
    else:
        try:
            content = _read_text(skill_md)
        except Exception as e:
            errors.append("Failed to read SKILL.md: " + str(e))
            content = ""

        frontmatter = _extract_frontmatter(content) if content else None
        if not frontmatter:
            errors.append("SKILL.md missing YAML frontmatter (--- ... ---)")
        elif not _has_required_frontmatter(frontmatter):
            errors.append("SKILL.md frontmatter must include name/description")
        elif not _has_project_version(frontmatter):
            errors.append(
                "SKILL.md should include project version metadata via top-level version or"
                " metadata.version"
            )

        if "## @工作流:" not in content:
            errors.append("SKILL.md must include a '## @工作流:' section")

        if "## 版本历史" not in content:
            errors.append("SKILL.md must include a '## 版本历史' section")

    if errors:
        for message in errors:
            print("ERROR: " + message)
        return 1

    print("OK: basic skill structure checks passed")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True, help="Skill folder path")
    args = parser.parse_args()

    skill_dir = Path(args.skill).resolve()
    if not skill_dir.exists():
        print("ERROR: skill folder not found: " + str(skill_dir))
        sys.exit(1)

    sys.exit(verify(skill_dir))

if __name__ == "__main__":
    main()
'''


def title_case_skill_name(skill_name):
    """Convert hyphenated skill name to Title Case for display."""
    return " ".join(word.capitalize() for word in skill_name.split("-"))


def validate_skill_name(skill_name):
    """Validate skill name against kebab-case requirements."""
    if not re.match(r"^[a-z0-9-]+$", skill_name):
        return (
            False,
            "Skill name must use lowercase letters, digits, and hyphens only",
        )
    if skill_name.startswith("-") or skill_name.endswith("-") or "--" in skill_name:
        return (
            False,
            "Skill name cannot start/end with a hyphen or contain consecutive hyphens",
        )
    if len(skill_name) > 64:
        return False, "Skill name must be 64 characters or fewer"
    return True, None


def init_skill(skill_name, path):
    """
    Initialize a new skill directory with template SKILL.md.

    Args:
        skill_name: Name of the skill
        path: Path where the skill directory should be created

    Returns:
        Path to created skill directory, or None if error
    """
    valid_name, validation_error = validate_skill_name(skill_name)
    if not valid_name:
        print(f"❌ Error: invalid skill name '{skill_name}'")
        print(f"   {validation_error}")
        return None

    # Determine skill directory path
    skill_dir = Path(path).resolve() / skill_name

    # Check if directory already exists
    if skill_dir.exists():
        print(f"❌ Error: Skill directory already exists: {skill_dir}")
        return None

    # Create skill directory
    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"✅ Created skill directory: {skill_dir}")
    except Exception as e:
        print(f"❌ Error creating directory: {e}")
        return None

    # Create SKILL.md from template
    skill_title = title_case_skill_name(skill_name)
    skill_content = SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=skill_title)

    skill_md_path = skill_dir / "SKILL.md"
    try:
        skill_md_path.write_text(skill_content, encoding="utf-8")
        print("✅ Created SKILL.md")
    except Exception as e:
        print(f"❌ Error creating SKILL.md: {e}")
        return None

    # Create resource directories
    try:
        # Create scripts/ directory with verify script
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        validate_script = scripts_dir / "validate_skill.py"
        validate_script.write_text(
            VALIDATE_SKILL_SCRIPT.format(skill_name=skill_name), encoding="utf-8"
        )
        validate_script.chmod(0o755)
        print("✅ Created scripts/validate_skill.py")

        # Create references/ directory without placeholder files
        references_dir = skill_dir / "references"
        references_dir.mkdir(exist_ok=True)
        (references_dir / "templates").mkdir(exist_ok=True)
        (references_dir / "examples").mkdir(exist_ok=True)
        print("✅ Created references/")

        # Create assets/ directory without placeholder files
        assets_dir = skill_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        print("✅ Created assets/")
    except Exception as e:
        print(f"❌ Error creating resource directories: {e}")
        return None

    # Print next steps
    print(f"\n✅ Skill '{skill_name}' initialized successfully at {skill_dir}")
    print("\nNext steps:")
    print("1. Edit SKILL.md to complete the TODO items and update the description")
    print("2. Add files to references/ and assets/ only if the skill actually needs them")
    print("3. If the skill needs 固定模板来源, create references/templates/<template-name>.md")
    print(
        "4. If SKILL.md workflows are already clear, run python scripts/skill_cli.py"
        " generate-templates . to create examples and update references/examples/index.md"
    )
    print("5. Run: python scripts/validate_skill.py --skill .")

    return skill_dir


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in {"-h", "--help"}:
        print("Usage: python scripts/skill_cli.py init <skill-name> --path <path>")
        print("\nSkill name requirements:")
        print("  - Kebab-case identifier (e.g., 'my-data-analyzer')")
        print("  - Lowercase letters, digits, and hyphens only")
        print("  - Max 64 characters")
        print("  - Must match directory name exactly")
        print("\nExamples:")
        print("  python scripts/skill_cli.py init my-new-skill --path skills/public")
        print("  python scripts/skill_cli.py init my-api-helper --path skills/private")
        print("  python scripts/skill_cli.py init custom-skill --path /custom/location")
        return 0
    if len(argv) < 3 or argv[1] != "--path":
        print("Usage: python scripts/skill_cli.py init <skill-name> --path <path>")
        print("\nSkill name requirements:")
        print("  - Kebab-case identifier (e.g., 'my-data-analyzer')")
        print("  - Lowercase letters, digits, and hyphens only")
        print("  - Max 64 characters")
        print("  - Must match directory name exactly")
        print("\nExamples:")
        print("  python scripts/skill_cli.py init my-new-skill --path skills/public")
        print("  python scripts/skill_cli.py init my-api-helper --path skills/private")
        print("  python scripts/skill_cli.py init custom-skill --path /custom/location")
        return 1

    skill_name = argv[0]
    path = argv[2]

    print(f"🚀 Initializing skill: {skill_name}")
    print(f"   Location: {path}")
    print()

    result = init_skill(skill_name, path)

    if result:
        return 0
    return 1
