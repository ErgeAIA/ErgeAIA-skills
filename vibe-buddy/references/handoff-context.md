---
name: handoff-context
description: vibe-handoff 的执行契约：生成自包含的会话交接文档，让另一个 agent 不读历史对话即可接手。
trigger-when: 用户说「交接上下文」「写交接文档」「vibe-handoff」，或上下文将满、要换会话或换 agent 时
role: workflow
reads-from:
  - references/command-policy.md
  - <project>/AGENTS.md
  - <project>/docs/.ai/project-progress.md
  - <project>/docs/.ai/decision-log.md
  - <project>/docs/.ai/debug-log.md
  - <project>/docs/handoff/ 上一份交接文档（存在时）
  - git status / git log / git diff --stat（仅本项目在 Git 仓库内时）
writes-to:
  - <project>/docs/handoff/handoff-YYYY-MM-DD[-slug].md
---

# handoff · 生成会话交接文档

## 目标

让**另一个 agent** 只读 `AGENTS.md`、`docs/.ai/` 与这一份交接文档，就能无歧义接手当前工作。读者是从未见过本项目、也没读过本次对话的 agent——不是"下一个窗口"。

## 前置检查

| 检查项 | 不通过时 |
|---|---|
| `<project>/AGENTS.md` 是否存在 | 不存在 → 回复缺失项，引导先跑 `vibe-init`，不代建 |
| `docs/.ai/project-progress.md` 与 `decision-log.md` 是否存在 | 缺哪个报哪个，引导先跑 `vibe-init`，不自行创建 |
| `docs/handoff/` 是否存在 | 不存在 → 引导先跑 `vibe-init`；用户坚持现在就要 → 建空目录并说明 |
| 本次会话是否有可交接的内容 | 没有实质进展 → 明说，不生成空文档 |

## 事实源与取材

写「已完成」与「未提交改动」之前先取客观事实，**不得只凭会话记忆落笔**：

| 序 | 事实源 | 取什么 |
| -- | ------ | ------ |
| 1 | `git status --short`、`git log --oneline -n <N>`、`git diff --stat` | 未提交改动、最近提交；**仅本项目在 Git 仓库内时可用** |
| 2 | `docs/handoff/` 上一份交接文档 | 上次交接下来的未完成项 |
| 3 | `AGENTS.md` 与 `docs/.ai/` 各文档 | 规则、进度、决策、已记录的坑 |
| 4 | 本次会话上下文 | 仅作补充 |

- `git diff --stat` **不显示未跟踪文件**，它为空不等于没有改动，以 `git status --short` 为准
- 仓库零提交（刚 `git init`、尚未提交）时 git 只能给出「全部未跟踪」，属正常状态，不代表没有进展
- 项目不是 Git 仓库 → 跳过第 1 项，不报错
- 取材覆盖整个仓库；但**只写** `docs/handoff/`，源码与配置一律只读

## 命名与落盘

- 路径：`docs/handoff/handoff-YYYY-MM-DD.md`。
- 同日已有交接文档时，追加语义后缀区分：`handoff-YYYY-MM-DD-<slug>.md`（如 `handoff-2026-09-10-review.md`）。
- **永不覆盖**。目标路径已存在就换后缀，不得改写既有文件。
- 文档头部带 YAML frontmatter，与 `docs/.ai/` 各过程文档同族：

````markdown
---
title: <一句话交接主题>
type: handoff
project: <工程标识>
date: YYYY-MM-DD
updated: YYYY-MM-DD
supersedes: <被取代的交接文档文件名，无则删掉本行>
description: >
  <本次交接覆盖了哪段工作、下一个 agent 从哪接手>
---
````

`date` 是会话日期；事后修订本文件时把 `updated` 改为当日——`AGENTS.md` 的 Conventions 要求「改 handoff 须同步 `updated`」，靠的就是这个字段。

## 内容要求（按此顺序成文）

| 段落 | 内容 |
|---|---|
| 当前状态 | 一句话说清现在停在哪 |
| 已完成 | 逐条写可验证事实：改了哪些文件、跑了什么验证、结果如何 |
| 未提交改动 | 工作区里未验证或未提交的改动，逐项说明改了什么、验证到哪一步 |
| 下次会话待办 | 按序列出，每条可独立执行 |
| 关键背景 | 影响判断的约束、环境坑、用户既定纪律 |
| 建议调用的技能 | 点名下一个 agent 该用哪些技能，一句话说明用途 |
| 待用户确认项 | 需要人拍板才能继续的议题，原样列出，不自行裁决 |

## 硬性约束

- **不重复已有产物**：进度、决策、bug 记录、规格、提交、diff 里已有的，一律写路径引用（commit hash、`docs/.ai/decision-log.md` 的 `DEC-NNN` 等）。
- **只展开尚未落入任何产物的内容**：未提交改动、下次会话待办、待用户确认项——这三类没有产物可引用，才逐条展开写。
- **脱敏**：密钥、token、凭据、连接串、个人隐私一律不写入；发现即替换为占位符。
- **不生成代码**，不重构，不新增功能。
- **只跑白名单内的只读 Git 命令**（`status` / `log` / `diff --stat`）；构建、测试、依赖安装与任何写命令都不跑。构建与测试状态写实际观测值，本次没跑就写「未运行」。
- **建议调用的技能只点名确实存在的**：不确定某技能是否存在就不写，不虚构技能名。
- 无法从 `AGENTS.md`、`docs/.ai/`、git 或本次对话确证的内容，写「未知」。
- 写完不改 `docs/.ai/` 里的历史条目；若本次产生新的稳定增量，提示用户另跑 `vibe-sync`。

## 终止回复

只回复两行：交接文档落盘路径；`docs/.ai/` 本次是否被改动（无则写「无」）。不预览文档正文。
