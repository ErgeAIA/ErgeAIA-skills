---
title: 经验库变更日志
type: experience-changelog
project: <工程标识>
updated: YYYY-MM-DD
description: >
  每轮蒸馏一行：日期 · 原料区间 · 产出 · 跳过原因码；人读台账，机读去重看 .distill-index.json。
  AI 在本文件新增或修改任何条目后，必须同步更新 frontmatter 的 updated 字段为当日日期（YYYY-MM-DD）。
---

# 变更日志与蒸馏台账

> 每轮蒸馏追加**一行**，**兼台账**。去重判定看同目录 `.distill-index.json`（按 SHA，不看这里的文字）。
> 只追加，不删除历史。

---

<!--
追加格式（本文件自带全部规格，不依赖外部文档）：

YYYY-MM-DD | <首个commit>..<末个commit> | +新增条目, ~修订条目 | skip: <原因码>, <原因码>

- 原料区间三种写法：已提交 `A..B`；尚未提交 `A..工作区（未提交）`；首次蒸馏 `HEAD..工作区`
- 跳过原因码（只取下列值，不写长句）：no-rule / single-occurrence / no-fact-source / project-param / covered-by:<条目>
- 产出写条目号：新增用 `+`、修订用 `~`（如 `+UI-T12, ~UI-R5`）
- 需要解释某个判断时，在该行下方缩进写一句，不展开成小节
- 同一区间必须同时写入 .distill-index.json 的 `range` 字段，两处不一致视为台账损坏：先修台账再蒸
- 修订既有条目时，本行要写「旧结论 → 新结论 + 为什么」，因为经验正文允许改写、历史只靠这里追溯
-->

（尚无。第一轮蒸馏时按上格式追加一行。）
