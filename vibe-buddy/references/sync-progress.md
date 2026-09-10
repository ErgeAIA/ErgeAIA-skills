---
name: sync-progress
description: vibe-sync 的执行契约：把本次会话的稳定增量沉淀到 docs/.ai/ 的进度与决策文档。
trigger-when: 用户说「同步进度」「更新项目进度」「vibe-sync」「沉淀一下」，或功能落地/决策达成/踩坑之后
role: workflow
reads-from:
  - <project>/AGENTS.md
  - <project>/docs/.ai/progress.md
  - <project>/docs/.ai/decisions.md
writes-to:
  - <project>/docs/.ai/progress.md
  - <project>/docs/.ai/decisions.md
---

# sync · 沉淀稳定增量

## 目标

把本次会话里**已经稳定的事实**——完成的模块、达成的架构或方向级决策——写进项目长期记忆，让下一次会话不必重读对话历史。

## 前置检查

| 检查项 | 不通过时 |
|---|---|
| `<project>/AGENTS.md` 是否存在 | 不存在 → 回复缺失项，引导先跑 `vibe-init`，不代建 |
| `docs/.ai/progress.md` 是否存在 | 不存在 → 回复缺失项，引导先跑 `vibe-init` |

## 只收稳定增量

写入前先判定每条内容是**稳定事实**还是**临时进度**。临时进度不进长期记忆。

| 类别 | 判定标准 | 落点 |
|---|---|---|
| 进度 | 已完成并通过用户本地验证的模块；或新发现的全局待办 | `docs/.ai/progress.md` |
| 决策 | 达成的架构或方向级共识 | `docs/.ai/decisions.md` |

不属于以上两类的（正在做的细节、过程中的推测、被推翻的中间方案）一律不写。

## 写入规则

- **仅追加**，禁止重写整个文件。
- 每条带日期，格式与文件既有条保持一致；文件为空时先建立表头。
- 写入前先扫描既有条目做去重：同一事实已存在则跳过；只有状态变化时更新该条。
- **不修改 `AGENTS.md`**。契约的改动属于 `vibe-init` 的增量维护，不属于 sync。
- 无稳定增量时明确回复「本次无可同步的稳定增量」，不写任何文件。

## 与相邻触发词的分界

| 场景 | 用哪个 |
|---|---|
| 功能落地、决策达成，要沉淀稳定事实 | 本文件 |
| 上下文将满、要交给另一个 agent | `references/handoff-context.md` |
| 新会话开始，要先弄清现状 | `references/resume-context.md` |
| 攒下可复用经验与踩坑 | `references/distill-lessons.md` |

## 终止回复

只回复一行统计：本次追加了哪些文件、各追加几条、去重跳过了几条。无增量时回复「本次无可同步的稳定增量」。
