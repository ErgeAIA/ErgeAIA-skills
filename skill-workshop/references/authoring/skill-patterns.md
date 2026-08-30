---
name: skill-patterns
description: Agent Skill 五种设计模式（Google ADK 总结）——创建/评审时判定目标模式归属的基线，决定 SKILL.md 结构骨架
version: 1.0.0
trigger-when: 创建需求阶段（C1-requirements 步骤2）/ 评审扫描阶段（W3）判定目标模式归属时
---

# Agent Skill 五种设计模式（Google ADK 总结）

> 来源：Google Cloud Tech《5 Agent Skill Design Patterns Every ADK Developer Should Know》（2025）。经 dev.to（Lavi Nigam / Google ADK Agent Engineering 专家 distill）、besthub.dev、华为云社区中文详版交叉核对。
> 用途：创建（C1）需求阶段与评审（W3）扫描阶段，先判定目标 Skill 归属哪类模式——模式决定结构骨架，是比"看起来完整"更根本的质量维度。

## 模式总览

| # | 模式 | 中文 | 解决的失控点 | 复杂度 |
|---|------|------|--------------|--------|
| 1 | Tool Wrapper | 工具包装器 | 缺领域知识（瞎编约定） | 低 |
| 2 | Generator | 生成器 | 输出格式漂移（结构不一致） | 中 |
| 3 | Reviewer | 审阅者 | 审查标准混乱（主观打分） | 中 |
| 4 | Inversion | 反转 | 盲目假设（未问先做） | 中 |
| 5 | Pipeline | 流水线 | 跳步骤（复杂任务缺校验） | 高 |

## 各模式要点

### 1. Tool Wrapper（工具包装器）
- **核心**：SKILL.md 在库/框架关键词上触发，从 `references/` 加载约定，Agent 瞬时变专家。无脚本、无模板，纯知识封装。
- **结构**：`SKILL.md` + `references/conventions.md`
- **何时用**：需对某库/SDK/内部系统套用一致专家级约定（FastAPI、Terraform、团队内部 API 规范）。

### 2. Generator（生成器）
- **核心**：`assets/` 模板定「输出什么结构」，`references/` 样式指南定「怎么写」。模板强制结构，样式指南强制质量。
- **结构**：`SKILL.md` + `assets/template.md` + `references/style-guide.md`
- **何时用**：输出每次固定结构、一致性 > 创造力（技术报告、API 文档、Conventional Commits、Agent 脚手架）。

### 3. Reviewer（审阅者）
- **核心**：分离「怎么审」（protocol 在 SKILL.md）与「审什么」（checklist 在 `references/review-checklist.md`）。换 checklist 即变审查类型。
- **输出分级**：❌ Error（必修）/ ⚠️ Warning（应修）/ ℹ️ Info（可选）
- **何时用**：凡人类用清单审查的场景（代码 Review、安全审计、编辑审阅、Agent 自审）。

### 4. Inversion（反转）
- **核心**：翻转对话角色——Agent 先当采访者按阶段提问，收齐信息后才产出。靠门控指令阻止抢跑，纯指令模式。
- **何时用**：需求收集、故障诊断、配置向导、报告前信息收集等「必须先拿语境才能干活」的高风险/模糊任务。

### 5. Pipeline（流水线）
- **核心**：严格有序多步工作流，步间设检查点（Gate），禁止跳过验证步。
- **结构**：`SKILL.md`（步骤+门控）+ `references/`（各步规范）+ `assets/`（模板）+ `scripts/`（可选）
- **何时用**：代码文档、数据清洗、部署流程、多步审批。

## 选型决策

```
需要灌某库/工具的专家知识      → Tool Wrapper
需要输出结构永远一致            → Generator
需要按标准对已有内容评分/分级   → Reviewer
需要先收集语境、防止瞎假设      → Inversion
需要严格有序、带检查点的多步流  → Pipeline
```

五种模式可组合（如 Pipeline 某步内嵌 Reviewer 质检，Generator 产出某步文档）。

## 与本技能 10 维的映射

| Google 模式 | 对应检查维度 |
|-------------|--------------|
| Tool Wrapper | C3 下沉、O1 起源 |
| Generator | M2 模板、C3 下沉 |
| Reviewer | V 验证闭环、M1 Gotchas |
| Inversion | D3 输入契约、M5 P-V-H |
| Pipeline | M3 Checklist、D1 非破坏护栏 |

> 评审（W3）建议：识别目标模式后，对照上表检查该模式的关键维度是否命中；模式归属不清（既像 Generator 又像 Pipeline）通常是 C2 范围不内聚的信号。
