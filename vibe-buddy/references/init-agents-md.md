---
name: init-agents-md
description: vibe-init 的执行契约：前置检查、路由判定、决策保全、过程文档落点与骨架、AGENTS.md 文档指引、CLAUDE.md 镜像策略。
trigger-when: 用户说「初始化项目」「生成 AGENTS.md」「vibe-init」，或项目需要建立协作契约、补齐缺失过程文档时
role: workflow
reads-from:
  - references/agents-md-generator.md
  - <project>/AGENTS.md（若已存在，用于决策保全）
  - <project>/CLAUDE.md（若已存在，用于决策保全）
writes-to:
  - <project>/AGENTS.md
  - <project>/CLAUDE.md（可选，指针）
  - <project>/docs/.ai/project-progress.md
  - <project>/docs/.ai/decision-log.md
  - <project>/docs/.ai/debug-log.md
  - <project>/docs/handoff/.gitkeep
---

# init · 建立协作契约与过程文档

## 目标

让一个从未见过本项目的 agent，读完 `AGENTS.md` 就知道：能做什么、用什么命令、遵守什么约定、去哪看进度与决策，以及**每完成一次任务必须同步哪些文档**。

一次初始化必须产出完整集合：

````text
<project>/
├── AGENTS.md
├── CLAUDE.md                     # 可选，指针
└── docs/
    ├── .ai/
    │   ├── project-progress.md   # 项目进度，实时更新
    │   ├── decision-log.md       # 决策日志，优先级高于 PRD
    │   ├── debug-log.md          # bug 修复经验
    │   └── project-overview.md   # 可选，层 B 概览
    └── handoff/                  # 会话交接文档
````

## 前置检查

| 检查项 | 不通过时 |
|---|---|
| 项目根是否已有 `AGENTS.md` 或 `CLAUDE.md` | 有 → 走「已初始化优化」增量维护；无 → 继续 |
| `docs/.ai/` 与 `docs/handoff/` 是否已存在 | 存在 → 只补缺失的文件，已存在的一字不动 |
| 项目根与 `docs/` 是否可写 | 不可写 → 停下报告，不写任何部分文件 |
| 目标项目是否为 monorepo | 是 → 各子包独立 `AGENTS.md`，根文件只留全局标准 |

## 路由（写文件前判定一次，并在产物头部注明模式）

判定信号：是否已存在 `AGENTS.md` / `CLAUDE.md`；是否已存在过程文档；提交历史与既有约定规模。

| 模式 | 条件 | 动作 |
|---|---|---|
| 全新初始化 | 无契约、无过程文档 | 生成契约 + 建立全部过程文档 |
| 半程补齐 | 无契约但有过程文档，或契约在而过程文档缺 | 生成或增量维护契约 + **只补缺失的过程文档** |
| 已初始化优化 | 已有契约 | 增量维护，**禁止整体重写**；文档只补缺失 |

判为开源项目（存在 `LICENSE` / `CONTRIBUTING`）→ 层 B 追加许可限制与贡献约定。

## 决策保全（半程补齐 / 已初始化优化必做）

1. 摘录既有 `AGENTS.md` / `CLAUDE.md` 全部条目，加上代码、提交、配置中可识别的约定，形成既有约定清单。
2. 逐条四态处置：`keep` 原样继承 / `update` 以代码现状为准改写 / `drop` 删除 / `merge` 合并去重。
3. `update` 与 `drop` 必须在 `docs/.ai/decision-log.md` 留下「旧值 → 处置 → 新值 / 原因」，**禁止静默丢失**。
4. 处置不下的条目标记为待确认交给用户裁决，不自行删除。

## 过程文档骨架

三类文档均**只追加**，历史条目永不删除或改写。

| 文件 | 用途 | 维护者 |
|---|---|---|
| `docs/.ai/project-progress.md` | 项目进度，实时更新；任务开始时先读它 | `vibe-sync` |
| `docs/.ai/decision-log.md` | 决策日志，**优先级高于 PRD**；决策冲突时旧条目改标 `superseded` | `vibe-sync` |
| `docs/.ai/debug-log.md` | bug 修复经验，编号递增 | `vibe-distill` |

### `docs/.ai/project-progress.md`

````markdown
# 项目进度

> 实时更新。任务开始时先读本文件。

- **last_updated**：
- **当前分支**：
- **当前阶段**：

## 已完成

## 进行中

## 待办

## 验证记录

> 如实记录实际执行过的验证命令与结果；未执行不得写"已通过"。
````

### `docs/.ai/decision-log.md`

````markdown
# 决策日志

> 开发过程中的最新决策，优先级高于 PRD。只追加；与既有决策冲突时，旧条目标 superseded。

## 条目格式

### DEC-001 · YYYY-MM-DD

- **决策**：
- **理由**：
- **影响**：
- **状态**：active

<!-- 待首条决策填入 -->
````

### `docs/.ai/debug-log.md`

````markdown
# Debug 日志

> bug 修复经验。只追加，编号递增。

## 条目格式

### BUG-001 · YYYY-MM-DD · <一句话标题>

- **症状**：
- **根因**：
- **修复**：
- **预防规则**：

<!-- 待首条记录填入 -->
````

### `docs/handoff/.gitkeep`

空文件，让 Git 追踪空目录。

## AGENTS.md 的文档指引（必做）

生成的 `AGENTS.md` 必须让 AI 时刻知道各文档用途与收尾动作，落实两处：

- `## References`：为四类文档各写一行指针，写明用途。
- `## 收尾同步`：写明每完成一次任务必须更新哪些文档，以及未同步不得声称完成。

具体文本见 `references/agents-md-generator.md` 的 §5 层 A 模板。

## CLAUDE.md 镜像

仅当检测到 Claude Code 使用痕迹（项目存在 `.claude/`）或用户显式要求时创建。

写入内容是**指针，不是副本**：

````markdown
# CLAUDE.md

本项目的协作契约见 AGENTS.md，那是唯一真相源。
````

禁止把 `AGENTS.md` 整份复制到 `CLAUDE.md`：两处内容会在下一轮维护后漂移。

## 生成规范

`AGENTS.md` 正文的生成与自检，逐字执行 `references/agents-md-generator.md`（句式契约、黑名单、证据采集、写入闸、自检门、自维护协议）。

## 终止回复

只回复：模式判定结果、`AGENTS.md` 落盘路径与实际行数、自检门是否五项全过、四类过程文档的建立与补齐情况（区分「新建」「已存在跳过」）、未决的待确认条目（若有）。
