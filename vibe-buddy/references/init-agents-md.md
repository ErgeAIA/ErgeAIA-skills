---
name: init-agents-md
description: vibe-init 的执行契约：前置检查、路由判定、决策保全、落点映射、docs/.ai 骨架初始化、CLAUDE.md 镜像策略。
trigger-when: 用户说「初始化项目」「生成 AGENTS.md」「vibe-init」，或项目需要建立 AI 协作契约时
role: workflow
reads-from:
  - references/agents-md-generator.md
  - <project>/AGENTS.md（若已存在，用于决策保全）
  - <project>/CLAUDE.md（若已存在，用于决策保全）
writes-to:
  - <project>/AGENTS.md
  - <project>/CLAUDE.md（可选，指针）
  - <project>/docs/.ai/progress.md
  - <project>/docs/.ai/decisions.md
  - <project>/docs/.ai/lessons.md
  - <project>/docs/.ai/handoffs/.gitkeep
---

# init · 建立 AI 协作契约

## 目标

让一个从未见过本项目的 agent，读完 `AGENTS.md` 就知道：能做什么、用什么命令、要遵守什么约定、去哪里看更多。

`AGENTS.md` 是**规则契约**，不承载进度、待办与任务计划——那两类分别由 `docs/.ai/progress.md` 和计划类技能负责。

## 前置检查

| 检查项 | 不通过时 |
|---|---|
| 项目根是否已有 `AGENTS.md` 或 `CLAUDE.md` | 有 → 不新建，改走「已初始化优化」增量维护；无 → 继续 |
| 项目根与 `docs/.ai/` 是否可写 | 不可写 → 停下报告，不写任何部分文件 |
| 目标项目是否为 monorepo | 是 → 各子包独立 `AGENTS.md`，根文件只留全局标准 |

## 路由（写文件前判定一次，并在产物头部注明模式）

判定信号：是否已存在 `AGENTS.md` / `CLAUDE.md`；提交历史与既有约定规模。

| 模式 | 条件 | 动作 |
|---|---|---|
| 全新初始化 | 无文件、决策负载低 | 直接生成 |
| 半程合成 | 无文件、决策负载高 | 先做决策保全，再生成 |
| 已初始化优化 | 有文件 | 增量维护，**禁止整体重写** |

判定为开源项目（存在 `LICENSE` / `CONTRIBUTING`）→ 层 B 追加许可限制与贡献约定。

## 决策保全（半程合成 / 已初始化优化必做）

1. 摘录既有 `AGENTS.md` / `CLAUDE.md` 全部条目，加上代码、提交、配置中可识别的约定，形成既有约定清单。
2. 逐条四态处置：`keep` 原样继承 / `update` 以代码现状为准改写 / `drop` 删除 / `merge` 合并去重。
3. `update` 与 `drop` 必须写入层 C 变更日志（旧值 → 处置 → 新值 / 原因），**禁止静默丢失**。
4. 处置不下的条目标记为待确认，交给用户裁决，不自行删除。

## 落点映射（本技能约定）

生成规范中的层 B 产物落到 `docs/.ai/` 下，与本技能的产物布局保持一致：

| 层级 | 落点 | 内容 |
|---|---|---|
| 层 A | `<project>/AGENTS.md` | 根契约 |
| 层 B（可选） | `<project>/docs/.ai/project-overview.md` | 目录索引、依赖方向、开源附加分析 |
| 层 C | `<project>/docs/.ai/decisions.md` | 决策变更日志，一行一条 |

> 生成规范原文写作 `references/project-overview.md`，落盘时按上表改写为 `docs/.ai/project-overview.md`。

## docs/.ai 骨架

首次初始化时建立以下文件；**已存在则一字不动**。

### `docs/.ai/progress.md`

```markdown
# 项目进度

> 由 vibe-sync 追加。每条一行，带日期。
```

### `docs/.ai/decisions.md`

```markdown
# 决策与变更日志

> 一行一条：旧值 → keep/update/drop/merge → 新值/原因。
```

### `docs/.ai/lessons.md`

```markdown
# 踩坑与经验档案

> 由 vibe-distill 追加。每条含症状、根因、预防规则。
```

### `docs/.ai/handoffs/.gitkeep`

空文件，用于让 Git 追踪空目录。

## CLAUDE.md 镜像

仅当检测到 Claude Code 使用痕迹（项目存在 `.claude/`）或用户显式要求时创建。

写入内容是**指针，不是副本**：

```markdown
# CLAUDE.md

本项目的 AI 协作契约见 AGENTS.md，那是唯一真相源。
```

禁止把 `AGENTS.md` 整份复制到 `CLAUDE.md`：两处内容会在下一轮维护后漂移。

## 生成规范

`AGENTS.md` 正文的生成与自检，逐字执行 `references/agents-md-generator.md`（句式契约、黑名单、证据采集、写入闸、自检门、自维护协议）。

## 终止回复

写入完成后只回复：模式判定结果、`AGENTS.md` 落盘路径与实际行数、自检门是否五项全过、`docs/.ai/` 骨架建立情况、未决的待确认条目（若有）。
