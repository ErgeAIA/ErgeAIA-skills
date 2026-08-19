---
name: C1-scaffold
description: C1 子阶段；内容规划 + 脚手架初始化（SKILL.md / references/ / scripts/ 目录结构创建）。
version: 1.2.0
trigger-when: "创建 Skill 规划与初始化阶段"
---

# C1.2 规划与初始化

<!-- @类型: 工作流 -->
<!-- @优先级: 必须 -->

## @工作流: 内容规划与脚手架初始化

### @步骤1: 规划内容结构

<!-- @类型: 操作步骤 -->
<!-- @验证点: 产出资源清单 -->

- @动作: 轻量 Skill：直接规划 SKILL.md 结构
- @动作: 中等/复杂 Skill：
  1. 读取 `references/authoring/business-to-workflow-mapping.md`
  2. 产出 workflow 映射表
  3. 规划 `scripts/`、`references/`、`assets/` 职责
- @动作: 若存在多个稳定用户意图，规划"决策矩阵 + 强规则摘要"

### @步骤2: 初始化脚手架

<!-- @类型: 操作步骤 -->
<!-- @验证点: 输出目录存在且包含 SKILL.md -->

```bash
python scripts/skill_cli.py init <skill-name> --path <output-dir>
```

- @动作: 修正 frontmatter（name、description、version）
- @动作: 按需创建子目录
- @动作: 清理 TODO / 占位信息

---

## 输出

- 目录结构（SKILL.md + 子目录）
- frontmatter 就绪
- 下一步：进入 C1.3 编辑与验证
