---
name: sync-progress
description: vibe-sync 的执行契约：把本次会话的稳定增量写进 docs/.ai/ 的进度文档与决策日志。
trigger-when: 用户说「同步进度」「更新项目进度」「vibe-sync」，或任务完成、决策变化之后
role: workflow
reads-from:
  - <project>/AGENTS.md
  - <project>/docs/.ai/project-progress.md
  - <project>/docs/.ai/decision-log.md
writes-to:
  - <project>/docs/.ai/project-progress.md
  - <project>/docs/.ai/decision-log.md
---

# sync · 沉淀进度与决策

## 目标

把本次会话里**已经稳定的事实**写进项目长期记忆，让下一次会话不必重读对话历史。这是 `AGENTS.md` 里 `Permissions` 与 `Conventions` 文档义务的执行者。

## 前置检查

| 检查项 | 不通过时 |
|---|---|
| `<project>/AGENTS.md` 是否存在 | 不存在 → 回复缺失项，引导先跑 `vibe-init`，不代建 |
| `docs/.ai/` 下两类文档是否存在 | 缺哪个补哪个：回复缺失项并引导 `vibe-init`，不自行创建 |

## 只收稳定增量

写入前先判定每条内容是**稳定事实**还是**临时进度**，临时进度不进长期记忆。

| 类别 | 判定标准 | 落点 |
|---|---|---|
| 进度 | 任务状态变化、当前分支、阶段推进、实际执行过的验证结果 | `docs/.ai/project-progress.md` |
| 决策 | 偏离 PRD 或重要技术选择 | `docs/.ai/decision-log.md` |

不属于以上两类的（正在做的细节、过程中的推测、被推翻的中间方案）一律不写。

## 写入规则

- **只追加**，禁止重写整个文件。
- 更新 `project-progress.md` 顶部的 `last_updated`、当前分支与当前阶段；任务状态与验证结果写进对应小节。
- 验证结果如实记录实际执行过的命令与结果；**未实际执行不得写"已通过"**。
- 决策条目追加到 `docs/.ai/decision-log.md` 的 `DEC-NNN` 序列，编号递增（三位）；与既有 active 决策冲突时，把旧条目标 `superseded`，**不删除历史条目**。
- **不写 `docs/.ai/agents-changelog.md`**：那是 AGENTS.md 约定处置区，由 `vibe-init` 独占，不随开发更新。
- 同一事实已存在则跳过；只有状态变化时更新该条。
- **不修改 `AGENTS.md`**：契约改动属于 `vibe-init` 的增量维护。
- 调试经验与 bug 根因归 `vibe-distill`，不在本触发词内重复写。
- 无稳定增量时明确回复「本次无可同步的稳定增量」，不写任何文件。

## 与相邻触发词的分界

| 场景 | 用哪个 |
|---|---|
| 任务完成、决策变化，要沉淀稳定事实 | 本文件 |
| 反复调试的 bug 定位到根因 | `references/distill-lessons.md` |
| 上下文将满，要交给另一个 agent | `references/handoff-context.md` |
| 新会话开始，要先弄清现状 | `references/resume-context.md` |

## 终止回复

只回复一行统计：写了哪些文件、各追加或更新几条、去重跳过几条。无增量时回复「本次无可同步的稳定增量」。
