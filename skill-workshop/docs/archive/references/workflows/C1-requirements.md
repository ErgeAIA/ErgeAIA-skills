---
name: C1-requirements
description: C1 子阶段；需求收集 + 复杂度判断，决定走 C1.1 → C1.2 → C1.3 哪条子路径。
version: 1.3.0
trigger-when: "创建 Skill 需求收集阶段"
---

# C1.1 需求收集与复杂度判断


## 需求收集

### 统一确认


- 确认任务类型：创建新 Skill
- 确认交付物：SKILL.md + 目录结构 + 可选脚本/模板
- 确认是否需要 workflow 设计（中等以上复杂度必须）
- 若用户明确不需要进入当前流程，记录结论后转入轻量执行路径

### 收集触发示例


- 至少整理 2 条真实触发语句（"用户说什么会触发 Skill"）
- 整理 1 份痛点总结
- 输出一句话定义（作用 + 触发场景 + 边界）
- 建议先判定目标模式归属（Tool Wrapper / Generator / Reviewer / Inversion / Pipeline，见 [skill-patterns.md](../authoring/skill-patterns.md)），它决定 SKILL.md 的结构骨架（灌知识 / 固定输出 / 清单审查 / 先问后做 / 强制多步）

### 判断复杂度


- 读取 `references/rubrics/complexity-rubric.md`
- 对照六维触发条件逐项判定
- 标注"轻量 / 中等 / 复杂"，并写明依据
- 轻量 Skill 记录为什么可跳过完整 workflow 映射
- 复杂 Skill 记录后续必须补 workflow 映射表

---

## 输出

- 一句话定义
- 触发示例 ≥2 条
- 复杂度判断 + 依据
- 下一步：进入 C1.2 规划与初始化

---

## 版本历史

- **v1.3.0** (2026-08-30) - 步骤2 增「先判定目标模式归属」指针（对齐 skill-patterns.md，Google 5 模式基线）
- **v1.2.0** (2026-06-18) - 初版结构（需求收集 + 复杂度判断）
