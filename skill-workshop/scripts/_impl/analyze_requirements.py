"""
Skill Requirements Analyzer - Analyzes user needs and designs skill interface

Usage:
    python scripts/skill_cli.py analyze [--output design.md]

This script interactively collects requirements and outputs a design document
that can be used to guide skill creation.
"""

from pathlib import Path
import re
from typing import Optional


class SkillDesigner:
    """Analyzes skill requirements and designs the interface"""

    def __init__(self):
        self.requirements = {
            "user_intent": "",
            "pain_points": [],
            "triggers": [],
            "inputs": [],
            "outputs": [],
            "examples": [],
        }

    def collect_from_user(self) -> dict:
        """Step 1: 交互式收集用户需求"""
        print("=" * 60)
        print("Skill 需求分析器")
        print("=" * 60)

        self.requirements["user_intent"] = input("\n1. 用户希望这个 Skill 做什么？\n   > ").strip()

        print("\n2. 核心痛点（输入多个，空行结束）：")
        while True:
            pain = input("   - ")
            if not pain:
                break
            self.requirements["pain_points"].append(pain)

        print("\n3. 触发词（用户说什么会激活此 Skill，输入多个）：")
        while True:
            trigger = input("   - ")
            if not trigger:
                break
            self.requirements["triggers"].append(trigger)

        print("\n4. 输入参数（需要什么信息）：")
        print("   格式: 参数名|类型|是否必需|描述")
        while True:
            inp = input("   - ")
            if not inp:
                break
            self.requirements["inputs"].append(self._parse_param(inp))

        print("\n5. 输出形式：")
        self.requirements["outputs"] = (
            input("   （文件/报告/终端输出/代码修改等）> ").strip().split(", ")
        )

        print("\n6. 使用示例（描述具体场景）：")
        while True:
            ex = input("   - ")
            if not ex:
                break
            self.requirements["examples"].append(ex)

        return self.requirements

    def analyze_pain_points(self) -> list:
        """Step 2: 分析痛点，提取关键问题"""
        analysis = []

        for pain in self.requirements["pain_points"]:
            if any(kw in pain for kw in ["手动", "重复", "繁琐", "每次", "耗时"]):
                analysis.append(
                    {"type": "效率问题", "pain": pain, "solution": "提供自动化脚本处理"}
                )
            elif any(kw in pain for kw in ["错误", "不准", "遗漏", "问题"]):
                analysis.append(
                    {"type": "质量问题", "pain": pain, "solution": "增加验证和检查机制"}
                )
            elif any(kw in pain for kw in ["不会", "不懂", "复杂", "难"]):
                analysis.append(
                    {"type": "知识问题", "pain": pain, "solution": "提供清晰的步骤指导和示例"}
                )
            else:
                analysis.append({"type": "其他", "pain": pain, "solution": "需要进一步分析"})

        return analysis

    def design_interface(self) -> dict:
        """Step 3: 设计调用接口"""
        name_candidates = []
        for trigger in self.requirements["triggers"]:
            # 仅提取 ASCII 词（中文触发词不进入 kebab-case 名称），并强制小写、仅保留合法字符。
            words = re.findall(r"[A-Za-z0-9]+", trigger)
            if words:
                slug = "-".join(w.lower() for w in words[:3])
                slug = re.sub(r"[^a-z0-9-]", "", slug)
                if slug:
                    name_candidates.append(slug)

        description = self._generate_description()

        return {
            "name_candidates": name_candidates[:3],
            "description": description,
            "trigger_patterns": self._generate_trigger_patterns(),
            "interaction_mode": self._determine_interaction_mode(),
        }

    def _generate_description(self) -> str:
        """生成 SKILL.md 的 description"""
        pain_summary = (
            "、".join(self.requirements["pain_points"][:2])
            if self.requirements["pain_points"]
            else "特定任务"
        )
        triggers = (
            " / ".join(self.requirements["triggers"][:2])
            if self.requirements["triggers"]
            else "特定场景"
        )
        output = self.requirements["outputs"][0] if self.requirements["outputs"] else "根据需求定制"
        return f"解决{pain_summary}问题。当用户说「{triggers}」时触发。输出形式：{output}。"

    def _generate_trigger_patterns(self) -> list:
        """生成触发模式（用于验证）"""
        patterns = []
        for trigger in self.requirements["triggers"]:
            pattern = trigger.replace("帮我", "").replace("给我", "").strip()
            patterns.append(pattern)
        return patterns

    def _determine_interaction_mode(self) -> str:
        """确定交互模式"""
        if len(self.requirements["inputs"]) <= 1:
            return "single_shot"
        elif any(inp.get("required") for inp in self.requirements["inputs"]):
            return "interactive"
        else:
            return "flexible"

    def _parse_param(self, param_str: str) -> dict:
        """解析参数格式: name|type|required|desc"""
        parts = param_str.split("|")
        return {
            "name": parts[0] if len(parts) > 0 else "",
            "type": parts[1] if len(parts) > 1 else "string",
            "required": parts[2] == "是" if len(parts) > 2 else False,
            "description": parts[3] if len(parts) > 3 else "",
        }

    def generate_design_doc(self, output_path: Optional[str] = None) -> str:
        """生成设计文档"""
        pain_analysis = self.analyze_pain_points()
        interface = self.design_interface()

        doc = f"""# Skill 设计文档

## 1. 需求理解

**用户原始需求：**
{self.requirements['user_intent']}

## 2. 痛点分析

| 类型 | 痛点描述 | 解决方案 |
|------|----------|----------|
"""
        for pa in pain_analysis:
            doc += f"| {pa['type']} | {pa['pain']} | {pa['solution']} |\n"

        doc += f"""
## 3. 调用方式设计

### 推荐名称
"""
        for i, name in enumerate(interface["name_candidates"], 1):
            doc += f"- {i}. `{name}`\n"

        doc += f"""
### 触发词
"""
        for trigger in self.requirements["triggers"]:
            doc += f'- "{trigger}"\n'

        doc += f"""
### 输入参数
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
"""
        for inp in self.requirements["inputs"]:
            req = "是" if inp.get("required") else "否"
            doc += f"| {inp['name']} | {inp['type']} | {req} | {inp['description']} |\n"

        doc += f"""
### 输出形式
{', '.join(self.requirements['outputs'])}

### 交互模式
`{interface['interaction_mode']}`

## 4. SKILL.md 模板

```yaml
---
name: {interface['name_candidates'][0] if interface['name_candidates'] else 'skill-name'}
description: {interface['description']}
version: 1.0.0
---
```

## 5. 使用示例
"""
        for i, ex in enumerate(self.requirements["examples"], 1):
            doc += f"{i}. {ex}\n"

        if output_path:
            Path(output_path).write_text(doc, encoding="utf-8")
            print(f"\n✅ 设计文档已保存: {output_path}")

        return doc


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Skill Requirements Analyzer")
    parser.add_argument("--output", "-o", default="design.md", help="输出文件路径")
    args = parser.parse_args(argv)

    designer = SkillDesigner()
    designer.collect_from_user()
    designer.generate_design_doc(args.output)

    print("\n" + "=" * 60)
    print("设计完成！下一步：")
    print(f"1. 查看设计文档: {args.output}")
    print(
        "2. 运行 python scripts/skill_cli.py init <skill-name> --path <output-dir> 创建 Skill 结构"
    )
    print("3. 根据设计文档编写 SKILL.md")
    print("=" * 60)
    return 0
