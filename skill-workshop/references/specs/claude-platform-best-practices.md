---
version: 2026-09
purpose: Anthropic 官方 Skill 编写最佳实践（description 相关章节缓存；全量原文可在线重取）
source: https://platform.claude.com/docs/zh-CN/agents-and-tools/agent-skills/best-practices
audience: AI agents
role: official-spec
consumed-by: W7 / spec.md / W3
trigger-when: W7 description 审计 / spec 收敛裁决 / description 写法争议时
last-fetched: 2026-09-11
last-verified: 2026-09-11 (VERIFIED — 在线逐节核对)
---

# description 字段规范（Anthropic 官方）

> **来源**: https://platform.claude.com/docs/zh-CN/agents-and-tools/agent-skills/best-practices
> **本文件**: 2026-09-11 在线逐节核对的要点缓存。如与官方源冲突，以官方源为准。
> **背景**: 本仓此前的 `role: official-spec` 文件（spec.md / best-practices.md / validate.md / optimizing-descriptions.md）均为社区 agentskills.io 镜像；Anthropic 官方 best-practices 此前无本地缓存，本文件补齐该缺口。

## 硬约束（4 条）

1. 必须非空
2. 最多 1,024 字符（**无建议字数区间**，只有上限）
3. 不能包含 XML 标签
4. 应描述 Skill 的功能以及何时使用它

补充：每个 Skill 只有一个 `description` 字段。

## 写法

- 结构 = **功能句 + `Use when…` 触发句**（官方三正例全部如此）。
- **始终第三人称**：好例 `"Processes Excel files and generates reports"`；避免 `"I can help you…"` / `"You can use this…"`（描述注入系统提示，视角不一致会出问题）。
- 关键术语同时分布在功能段与触发段（如 "PDF files"、"PDFs, forms, or document extraction"、".xlsx files"）；描述是从可能超过 100 个可用 Skills 中做选择的唯一依据。
- 反面示例（模糊描述）：`Helps with documents` / `Processes data` / `Does stuff with files`。
- **全文未提 "Pushy"**（该说法出自社区 agentskills.io《Optimizing skill descriptions》，非官方出处）。

## 官方正例（三例均 `Use when` 触发句）

```
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.

description: Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.

description: Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.
```
