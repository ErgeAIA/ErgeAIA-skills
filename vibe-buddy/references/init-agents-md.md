---
name: init-agents-md
description: vibe-init 的执行契约：前置检查、状态识别与路由、决策保全、过程文档落点、AGENTS.md 文档义务、CLAUDE.md 镜像策略。
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
  - <project>/docs/.ai/decision-log.md（含层 C 小节）
  - <project>/docs/.ai/debug-log.md
  - <project>/docs/.ai/project-overview.md（可选）
  - <project>/docs/handoff/.gitkeep
---

# init · 建立协作契约与过程文档

## 目标

让一个从未见过本项目的 agent，读完 `AGENTS.md` 就知道：能做什么、用什么命令、遵守什么约定、去哪看进度与决策，以及**每完成一次任务必须同步哪些文档**。

一次初始化必须产出完整集合：

````text
<project>/
├── AGENTS.md
├── CLAUDE.md                        # 可选，指针
└── docs/
    ├── .ai/
    │   ├── project-progress.md      # 进度，每次会话更新
    │   ├── decision-log.md          # 开发决策 + 层 C，优先级高于 PRD
    │   ├── debug-log.md             # bug 记录
    │   └── project-overview.md      # 可选，层 B
    └── handoff/                     # 交接文档
````

## 前置检查

| 检查项 | 不通过时 |
|---|---|
| 项目根是否已有 `AGENTS.md` 或 `CLAUDE.md` | 有 → 走「已初始化优化」；无 → 继续查状态信号 |
| `docs/.ai/` 与 `docs/handoff/` 是否已存在 | 存在 → 只补缺失的文件，已存在的一字不动 |
| 项目根与 `docs/` 是否可写 | 不可写 → 停下报告，不写任何部分文件 |
| 目标项目是否为 monorepo | 是 → 各子包独立 `AGENTS.md`，根文件只留全局标准 |

## 状态识别与路由（写文件前判定一次）

**判据真源**：`references/agents-md-generator.md` §2。按其中三个可观测信号（既有契约 / 既有代码 / 既有项目文档）查证后定模式，三个信号矛盾或无法查证时停下问用户，不自行归类。本技能按模式执行对应动作：

| 模式 | 本技能的动作 |
|---|---|
| 全新初始化 | 生成契约 + 建立全部过程文档 |
| 半程合成 | 先做决策保全，再生成契约与文档 |
| 已初始化优化 | 增量维护，**禁止整体重写**；文档只补缺失 |

产物头部按 `<!-- mode: <模式> -->` 只填一个值。判为开源项目（存在 `LICENSE` / `CONTRIBUTING`）→ 层 B 追加许可限制与贡献约定。

## 决策保全（半程合成 / 已初始化优化必做）

1. 摘录既有 `AGENTS.md` / `CLAUDE.md` 全部条目，加上代码、提交、配置中可识别的约定，形成既有约定清单。
2. 逐条四态处置：`keep` 原样继承 / `update` 以代码现状为准改写 / `drop` 删除 / `merge` 合并去重。
3. 每一条 `update` 与 `drop` 写入 `docs/.ai/decision-log.md` 的 `## Layer C — AGENTS.md 约定处置` 小节，一行一条 `<旧值> → 处置 → <新值/去处/原因>`，**禁止静默丢失**。
4. 处置不下的条目标记为待确认交给用户裁决，不自行删除。

## 过程文档

目录结构与初始模板的单一真源是 `references/agents-md-generator.md` §4b。三件套从 `assets/docs/` 直接复制，只替换 `<工程标识>` 并把 `updated` 改为当日；已有同名文件跳过，不覆盖。

| 文件 | 用途 | 维护者 |
|---|---|---|
| `docs/.ai/project-progress.md` | 进度，每次会话更新；任务开始时先读它 | `vibe-sync` |
| `docs/.ai/decision-log.md` | 开发决策（`DEC-NNN`，优先级高于 PRD）+ 层 C 约定处置 | `vibe-sync`（层 C 由 `vibe-init` 写） |
| `docs/.ai/debug-log.md` | bug 记录，编号 `BUG-NNN` 递增 | `vibe-distill` |
| `docs/handoff/` | 交接文档，命名 `handoff-YYYY-MM-DD-*.md` | `vibe-handoff` |

全部**只追加**，历史条目永不删除或改写；决策冲突时把旧条目标 `superseded`。

## AGENTS.md 的文档义务（必做）

生成的 `AGENTS.md` 必须让 AI 时刻知道各文档做什么、每次任务完成要同步哪些。按三处落实：

| 位置 | 写什么 |
|---|---|
| `Permissions` | `YOU MUST 每次会话更新 docs/.ai/project-progress.md` |
| `Conventions` | 会话文档体系、bug 追加、交接命名、改文档须同步 `updated` 四条表格行 |
| `References` | 项目自带文档 + `docs/.ai/` 三件套 + `docs/handoff/`，逐条 `见 <path>` 指针 |

具体文本见 `references/agents-md-generator.md` §5。

## CLAUDE.md 镜像

仅当检测到 Claude Code 使用痕迹（项目存在 `.claude/`）或用户显式要求时创建。

写入内容是**指针，不是副本**：

````markdown
# CLAUDE.md

本项目的协作契约见 AGENTS.md，那是唯一真相源。
````

禁止把 `AGENTS.md` 整份复制到 `CLAUDE.md`：两处内容会在下一轮维护后漂移。

## 终止回复

只回复：判定模式与依据信号、`AGENTS.md` 落盘路径与实际行数、自检门是否五项全过、各过程文档的建立与补齐情况（区分「新建」「已存在跳过」）、Layer C 记录条数、未决的待确认条目（若有）。
