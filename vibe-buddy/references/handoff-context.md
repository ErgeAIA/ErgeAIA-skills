---
name: handoff-context
description: vibe-handoff 的执行契约：把当前会话压成一份自包含交接文档，让另一个 agent 不读历史对话即可接手。
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

让**另一个 agent** 只读 `AGENTS.md`、`docs/.ai/` 与本文件，就能无歧义接手。读者是从未见过本项目、也没读过本次对话的 agent。

**接手不是本技能的职责**：新会话的「读记忆 + 复述现状」由目标项目 `AGENTS.md` 的义务承担——它每次会话自动生效，不依赖任何人想起触发词。本技能只负责**写**。

## 前置检查

| 检查项 | 不通过时 |
|---|---|
| `<project>/AGENTS.md` 是否存在 | 不存在 → 回复缺失项，引导先跑 `vibe-init`，不代建 |
| `docs/.ai/project-progress.md` 与 `decision-log.md` 是否存在 | 缺哪个报哪个，引导先跑 `vibe-init`，不自行创建 |
| `docs/handoff/` 是否存在 | 不存在 → 引导先跑 `vibe-init`；用户坚持现在就要 → 建空目录并说明 |
| 本次会话是否有可交接的内容 | 没有实质进展 → 明说，不生成空文档 |

## 事实源与取材

写「验证状态」与「未提交改动」之前先取客观事实，**不得只凭会话记忆落笔**：

| 序 | 事实源 | 取什么 |
| -- | ------ | ------ |
| 1 | `git status --short`、`git log --oneline -n <N>`、`git diff --stat` | 未提交改动、已提交的改动；**仅本项目在 Git 仓库内时可用** |
| 2 | `docs/handoff/` 上一份交接文档 | 上次交接下来的未完成项 |
| 3 | `AGENTS.md` 与 `docs/.ai/` 各文档 | 规则、进度、决策、已记录的坑 |
| 4 | 本次会话上下文 | 仅作补充 |

- `git diff --stat` **不显示未跟踪文件**，为空不等于没有改动，以 `git status --short` 为准
- 仓库零提交（刚 `git init`、尚未提交）时 git 只能给出「全部未跟踪」，属正常状态，不代表没有进展
- 项目不是 Git 仓库 → 跳过第 1 项，不报错
- 取材覆盖整个仓库；但**只写** `docs/handoff/`，源码与配置一律只读

## 只写「别处读不到的」

接手方自己就能读到 `AGENTS.md`、`docs/.ai/`、git 与代码。所以：

| 信息 | 别处在哪 | 本文件怎么写 |
|---|---|---|
| 协作纪律、红线、边界 | `AGENTS.md`（每会话自动注入） | 不写 |
| 进度、决策、已定位根因的 bug | `docs/.ai/` | 只写指针（`DEC-NNN` / `BUG-NNN`） |
| 已提交的改动 | git | 只写 commit hash |
| **只有本次会话知道的** | 无处可查 | **展开写** |

只有下面四类无处可查，它们是正文主体；**某一类没有内容就整段省略，不写「无」**：

1. **验证状态** —— 本次改了什么、验证到哪一步、哪些仍未验证。git 只给文件清单，给不出「验没验」
2. **下一步聚焦点** —— 相对 `project-progress.md`「下一步」的**变化**；用户在本会话新指定的，以其为准
3. **卡点与失败路径** —— 试过什么、为什么不行。已定位根因的归 `debug-log.md`，仍是坑的写这里
4. **待用户拍板项** —— 需要人决定才能继续的议题，原样列出，不自行裁决

另可写「**建议调用的技能**」，但**仅在接手方不会自然想到时**写（如「须先重建某索引」）；没有就省略，不写客套。

## 命名与落盘

- 路径：`docs/handoff/handoff-YYYY-MM-DD.md`。
- 当日已有同名文件时追加语义后缀：`handoff-YYYY-MM-DD-<slug>.md`（如 `handoff-2026-09-10-review.md`）。
- 后缀仍撞名时加两位序号，**不回头打扰用户**：`handoff-YYYY-MM-DD-<slug>-02.md`。
- **永不覆盖**。目标路径已存在就换名，不得改写既有文件。
- frontmatter 与 `docs/.ai/` 各过程文档同构，只有 `type` 不同：

````markdown
---
title: <一句话交接主题>
type: handoff
project: <工程标识>
updated: YYYY-MM-DD
description: >
  <本次交接覆盖了哪段工作、下一个 agent 从哪接手>
---
````

文件名已承载会话日期，不再另设 `date` 字段（同一事实两处存放必然漂移）。事后修订本文件时把 `updated` 改为当日——`AGENTS.md` 的 Conventions 要求「改 handoff 须同步 `updated`」，靠的就是这个字段。

## 硬性约束

- **不重复已有产物**：`docs/.ai/`、规格、提交、diff 里已有的，一律写路径引用（commit hash、`DEC-NNN` 等）。
- **不搬常驻规则**：协作纪律与红线已在 `AGENTS.md`。逐条抄进交接文档，既在每份文档里重复一遍，也违反上一条。
- **脱敏**：密钥、token、凭据、连接串、个人隐私一律不写入；发现即替换为占位符。
- **不生成代码**，不重构，不新增功能。
- **只跑白名单内的只读 Git 命令**（`status` / `log` / `diff --stat`）；构建、测试、依赖安装与任何写命令都不跑。验证状态写实际观测值，本次没跑就写「未运行」。
- 无法从 `AGENTS.md`、`docs/.ai/`、git 或本次对话确证的内容，写「未知」。
- 写完不改 `docs/.ai/` 里的历史条目。

## 终止回复

两行：交接文档落盘路径；`docs/.ai/` 本次是否被改动（无则写「无」）。

若本会话有已稳定的进度或决策尚未同步，追加一句建议接着跑 `vibe-sync`。不预览文档正文。
