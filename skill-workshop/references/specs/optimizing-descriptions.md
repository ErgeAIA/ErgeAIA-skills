---
version: 2026-06
purpose: 官方 description 优化指南（本地缓存）
source: https://agentskills.io/skill-creation/optimizing-descriptions
audience: AI agents
role: official-spec
consumed-by: W7 / C2-evaluate / improve_description.py
trigger-when: 用户要求优化 description / W7 命中 T5 / C2 评测迭代
last-fetched: 2026-06-24
last-verified: 2026-06-24 (VERIFIED)
---

# Optimizing skill descriptions

> **来源**: https://agentskills.io/skill-creation/optimizing-descriptions
> **本文件**: 2026-06-24 拉取的官方内容缓存
> **更新方式**: AI 可通过 WebFetch 源 URL 拉取最新内容，对比差异后更新本文件

---

## 1. description 为什么重要

Agent 启动时只加载每个 Skill 的 `name` + `description`，据此决定是否加载完整 SKILL.md。description 承担了**全部触发责任**。

注意：Agent 通常只在任务超出自身能力时才调用 Skill。简单请求（如"读这个 PDF"）即使 description 匹配也可能不触发。

## 2. 写好 description 的原则

- **用祈使句**：告诉 Agent 何时行动（"Use this skill when..."），不是描述功能（"This skill does..."）
- **关注用户意图**：描述用户想做什么，不是 Skill 内部机制
- **宁可 Pushy**：显式列出适用场景，包括用户没直接提域名的情况
- **保持简洁**：几句话到一小段，硬限 1024 字符

## 3. description 三段式结构

```yaml
# 第一段：做什么（功能 + 核心能力）
# 第二段：何时触发 + 关键词（Use this skill when... / Invoke on...）
# 第三段：边界（Not for: ...）

description: "第一段。Use this skill whenever... Invoke on '关键词1'/'关键词2'. Not for: 边界1/边界2."
```

**反例**：
```yaml
description: Process CSV files.
```

**正例**：
```yaml
description: >
  Analyze CSV and tabular data files — compute summary statistics,
  add derived columns, generate charts, and clean messy data. Use this
  skill when the user has a CSV, TSV, or Excel file and wants to
  explore, transform, or visualize the data, even if they don't
  explicitly mention "CSV" or "analysis."
```

## 4. 设计触发测试集

目标：~20 条查询（8-10 应触发 + 8-10 不应触发）。

### 应触发查询（变化维度）

- **语气**：正式 / casual / 带拼写错误
- **显式度**：直接提域名 / 描述需求不提域名
- **详细度**：简短 / 带文件路径、列名、背景故事
- **复杂度**：单步 / 多步（Skill 用途嵌在更大任务链中）

最有价值的应触发查询是"连接不明显"的——如果查询已经直接问了 Skill 做的事，任何合理 description 都会触发。

### 不应触发查询（near-misses）

弱反例（没用）：`"Write a fibonacci function"` — 无关键词重叠
强反例（有用）：`"I need to update the formulas in my Excel budget spreadsheet"` — 共享"spreadsheet"但需要的是 Excel 编辑

### 真实感要素

- 文件路径（`~/Downloads/report_final_v2.xlsx`）
- 个人背景（`"my manager asked me to..."`）
- 具体细节（列名、公司名、数据值）
- casual 语言、缩写、偶尔拼写错误

## 5. 测试触发率

每条查询跑 3 次，计算**触发率**（被触发的次数 / 总次数）。

- 应触发：触发率 > 0.5 → 通过
- 不应触发：触发率 < 0.5 → 通过

## 6. 防止过拟合：train/validation 分割

- **Train set（~60%）**：用于发现问题和指导改进
- **Validation set（~40%）**：留出来检查改进是否泛化

两个集合都要包含成比例的应触发/不应触发查询。

## 7. 优化循环

1. **评估**当前 description（train + validation）
2. **识别 train set 失败**：哪些应触发没触发？哪些不应触发却触发了？
3. **修改 description**：
   - 应触发失败 → description 太窄，扩大范围
   - 不应触发误触发 → description 太宽，加边界声明
   - 避免直接加失败查询的关键词（过拟合），找通用类别
   - 保持 < 1024 字符
4. **重复** 1-3，直到 train set 全通过或无明显改善
5. **选最佳迭代**：按 validation 通过率选（不一定是最新的）

通常 5 轮够了。如果性能不改善，问题可能在查询集（太容易/太难/标签错误），不在 description。

## 8. 应用结果

1. 更新 SKILL.md frontmatter `description`
2. 验证 < 1024 字符
3. 手动试几个 prompt 做 sanity check
4. 写 5-10 条全新查询跑 eval（从未参与优化的，诚实检验泛化）
