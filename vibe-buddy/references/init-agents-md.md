---
name: init-agents-md
description: vibe-init 的执行契约：执行顺序、前置检查、Git 检查、状态识别与路由、决策保全、过程文档落点、Codegraph 集成、初始化报告、CLAUDE.md 镜像策略。
trigger-when: 用户说「初始化项目」「生成 AGENTS.md」「vibe-init」，或项目需要建立协作契约、补齐缺失过程文档时
role: workflow
reads-from:
  - references/agents-md-generator.md
  - references/init-env-checks.md
  - <project>/AGENTS.md（若已存在，用于决策保全）
  - <project>/CLAUDE.md（若已存在，用于决策保全）
writes-to:
  - <project>/AGENTS.md
  - <project>/CLAUDE.md（可选，指针）
  - <project>/docs/.ai/project-progress.md
  - <project>/docs/.ai/decision-log.md
  - <project>/docs/.ai/debug-log.md
  - <project>/docs/.ai/agents-changelog.md（层 C）
  - <project>/docs/.ai/init-report.md
  - <project>/docs/.ai/project-overview.md（可选）
  - <project>/docs/handoff/.gitkeep
  - <project>/.git/（仅 git init）
  - <project>/.codegraph/（仅 codegraph init）
---

# init · 建立协作契约与过程文档

## 目标

让一个从未见过本项目的 agent，读完 `AGENTS.md` 就知道：能做什么、用什么命令、遵守什么约定、去哪看进度与决策，以及**每完成一次任务必须同步哪些文档**。

一次初始化必须产出完整集合：

````text
<project>/
├── AGENTS.md
├── CLAUDE.md                        # 可选，指针
├── .git/                            # 无仓库时 git init 建立
├── .codegraph/                      # 已装 codegraph 且无索引时建立
└── docs/
    ├── .ai/
    │   ├── project-progress.md      # 进度，每次会话更新
    │   ├── decision-log.md          # 开发决策，优先级高于 PRD
    │   ├── debug-log.md             # bug 记录
    │   ├── agents-changelog.md      # 层 C：AGENTS.md 变更记录
    │   ├── init-report.md           # 本次初始化执行报告
    │   └── project-overview.md      # 可选，层 B
    └── handoff/                     # 交接文档
````

## 执行顺序

按此顺序执行，不跳步、不重排；某步失败记入报告后继续，不中断：

| 序 | 步骤 | 说明 |
| -- | ---- | ---- |
| 1 | 前置检查 | 可写性、monorepo 判定 |
| 2 | Git 检查 | 仓库检测，必要时 `git init` |
| 3 | 状态识别与路由 | 按可观测信号判定模式 |
| 4 | 决策保全 | 半程合成 / 已初始化优化 必做 |
| 5 | 生成 AGENTS.md | §4 → §4b → §5 → §6 → §7 |
| 6 | 建立过程文档 | 复制模板，补齐缺口 |
| 7 | CLAUDE.md 镜像 | 按需建指针 |
| 8 | Codegraph 集成 | 检测索引，或给出安装建议 |
| 9 | 初始化报告 | 汇总本次全部操作 |
| 10 | 终止回复 | 按格式回报 |

## 前置检查

| 检查项 | 不通过时 |
|---|---|
| 项目根是否已有 `AGENTS.md` 或 `CLAUDE.md` | 有 → 走「已初始化优化」；无 → 继续查状态信号 |
| agent 目录内是否已有规则文件（`.claude/`、`.codex/`、`.zcode/`、`.cursor/rules/` 等） | 有 → 纳入决策保全，按既有约定处置；**含点目录必须查，不能只看列目录工具的默认输出** |
| `docs/.ai/` 与 `docs/handoff/` 是否已存在 | 存在 → 只补缺失的文件，已存在的一字不动 |
| 项目根与 `docs/` 是否可写 | 不可写 → 停下报告，不写任何部分文件 |
| 目标项目是否为 monorepo | 是 → 各子包独立 `AGENTS.md`，根文件只留全局标准 |

## Git 检查

先只读检测：`git rev-parse --is-inside-work-tree`。

- 已是仓库 → 跳过，报告写「已存在仓库，跳过」
- 不是仓库 → 执行 `git init`，报告写「已初始化仓库」
- 不执行 `git add` / `commit` / `push`
- 失败不阻塞，记「失败 + 原因」后继续

命令白名单、Codegraph 判定与失败处理细则见 `references/init-env-checks.md`。

## 状态识别与路由（写文件前判定一次）

**判据真源**：`references/agents-md-generator.md` §2。按其中三个可观测信号（既有契约 / 既有代码 / 既有项目文档）查证后定模式，三个信号矛盾或无法查证时停下问用户，不自行归类。本技能按模式执行对应动作：

| 模式 | 本技能的动作 |
|---|---|
| 全新初始化 | 生成契约 + 建立全部过程文档 |
| 半程合成 | 先做决策保全，再生成契约与文档 |
| 已初始化优化 | 增量维护，**禁止整体重写**；文档只补缺失 |

产物头部按 `<!-- mode: <模式> -->` 只填一个值。判为开源项目（存在 `LICENSE` / `CONTRIBUTING`）→ 层 B 追加许可限制与贡献约定。

## 决策保全（半程合成 / 已初始化优化必做）

1. 摘录既有契约文件全部条目；**无契约文件时**，摘录代码、提交、配置中可识别的现存约定，形成既有约定清单。
2. 逐条四态处置：`keep` 原样继承 / `update` 以代码现状为准改写 / `drop` 删除 / `merge` 合并去重。
3. 每一条 `update` 与 `drop` 写入 `docs/.ai/agents-changelog.md`，一行一条 `<旧值> → 处置 → <新值/去处/原因>`，**禁止静默丢失**。
4. 旧位置残留（如项目根 `references/` 下的旧决策或变更日志）：内容合并进 `docs/.ai/` 的新落点，旧文件按 `drop` 处理并留痕，**禁止新旧两处并存**。
5. 处置不下的条目标记为待确认交给用户裁决，不自行删除。

**全新初始化**跳过四态处置，但仍建 `docs/.ai/agents-changelog.md` 并写一行兜底：`<无旧约定> → 全新初始化 → 直建当前 AGENTS.md`。

## 过程文档

目录结构、各文档的建立条件、`<工程标识>` 取法的单一真源是 `references/agents-md-generator.md` §4b。各文档从 `assets/docs/` 直接复制，替换 `<工程标识>` 并把 `updated` 改为当日；已有同名文件跳过，不覆盖。

| 文件 | 用途 | 维护者 |
|---|---|---|
| `docs/.ai/project-progress.md` | 进度，每次会话更新；任务开始时先读它 | `vibe-sync` |
| `docs/.ai/decision-log.md` | 开发决策（`DEC-NNN`，优先级高于 PRD），随开发持续更新 | `vibe-sync` |
| `docs/.ai/debug-log.md` | bug 记录，编号 `BUG-NNN` 递增 | `vibe-distill` |
| `docs/.ai/agents-changelog.md` | AGENTS.md 变更记录，**只在 AGENTS.md 改动时更新** | `vibe-init` 独占 |
| `docs/.ai/init-report.md` | 初始化执行记录，只追加 | `vibe-init` 独占 |
| `docs/handoff/` | 交接文档，命名 `handoff-YYYY-MM-DD-*.md` | `vibe-handoff` |

全部**只追加**，历史条目永不删除或改写；决策冲突时把旧条目标 `superseded`。

## AGENTS.md 的文档义务（必做）

生成的 `AGENTS.md` 必须让 AI 时刻知道各文档做什么、每次任务完成要同步哪些。按三处落实：

| 位置 | 写什么 |
|---|---|
| `Permissions` | `YOU MUST 每次会话更新 docs/.ai/project-progress.md`；`YOU MUST 改 AGENTS.md 前先读、改后追加 docs/.ai/agents-changelog.md` |
| `Conventions` | 会话文档体系、bug 追加、交接命名、改文档须同步 `updated`、改 AGENTS.md 须留变更记录 五条表格行 |
| `References` | 项目自带文档 + `docs/.ai/` 各过程文档 + `docs/handoff/`，逐条 `见 <path>` 指针 |

## 保证层级（写文档时按此判断）

规则的效力取决于该文件**是否必然被读到**，分三层：

| 层 | 前提 | 效力 |
|---|---|---|
| A | `AGENTS.md` 被运行时自动注入 | 每会话必读，**唯一能覆盖「AI 未调用本技能」这个前提的层**。义务只写在这里才算硬约束 |
| B | 本技能被调用 | 只在走 `vibe-init` 时生效：§7 自检门、终止回复报告条数 |
| C | 文件被打开才读到 | 过程文档模板内的说明（如 `agents-changelog.md` 头部那句「每改动一次必须追加一行」）**不构成保证**，只是文件自述 |

结论：**过程文档之间不要互相充当强制机制**。要保证某件事，就把它写进 `AGENTS.md`（A 层）；A 层要覆盖「AI 会去读某个文件」，必须用 `前先读` 这类措辞把读取动作写进义务本身。`References` 只负责让文件被发现，不承担强制力。

具体文本见 `references/agents-md-generator.md` §5。

## CLAUDE.md 镜像

仅当检测到 Claude Code 使用痕迹（项目存在 `.claude/`）或用户显式要求时创建。

写入内容是**指针，不是副本**：

````markdown
# CLAUDE.md

本项目的协作契约见 AGENTS.md，那是唯一真相源。
````

禁止把 `AGENTS.md` 整份复制到 `CLAUDE.md`：两处内容会在下一轮维护后漂移。

## Codegraph 集成

判定顺序：先 `codegraph --version` 查安装，再 `codegraph status` 查本项目索引。

- 已安装且无索引、项目有代码 → 执行 `codegraph init`
- 已安装且已有索引 → 跳过
- 未安装 → 不执行，在报告「建议」小节写清用途、安装命令与初始化命令
- 不执行 `codegraph install` / `uninstall`（会改写各 agent 配置）

完整判定表、建议文案与失败处理见 `references/init-env-checks.md`。

## 初始化报告

在 `docs/.ai/init-report.md` 追加一节，记录本次执行的**全部**操作。模板与条目类型见 `assets/docs/init-report.md`。

追加格式：

````markdown
## YYYY-MM-DD 初始化报告 — <模式>

| 步骤 | 动作 | 目标 | 结果 | 备注 |
| ---- | ---- | ---- | ---- | ---- |
| 前置检查 | 检查可写性与 monorepo | <项目根> | 完成 | — |
| Git 检查 | 缺失仓库则初始化 | `<project>/.git` | 完成 / 跳过 / 失败 | — |
| 状态识别 | 三信号查表 | — | 完成 | 判定为 <模式> |
| 决策保全 | 既有约定四态处置 | `docs/.ai/agents-changelog.md` | 完成 / 跳过 | N 条 |
| 契约生成 | 生成或增量维护 | `AGENTS.md` | 完成 | N 行 |
| 过程文档 | 复制模板、补齐缺口 | `docs/.ai/*` | 完成 | 新建 X / 跳过 Y |
| CLAUDE.md | 建镜像指针 | `<project>/CLAUDE.md` | 完成 / 跳过 | — |
| Codegraph | 索引检测与初始化 | `<project>/.codegraph` | 完成 / 跳过 / 未执行 | — |
| 其他技能 | 依赖安装等 | — | 未执行 | 由用户或其他技能执行 |

### 建议

- <未安装 codegraph 时写用途、安装命令、初始化命令>
- <其他需用户决策的事项>
````

规则：

- **只列本次实际涉及的步骤行**；上表是格式示意，不是必须全列，不相关的类型不占行
- 每行必须反映**实际结果**；流程内该做但没做的写「未执行」并注明原因，禁止虚报
- 所有数字（行数、条数、份数）必须**实测读取**，禁止估算；行数口径为含空行的总行数
- 命令输出只留结论，长输出截断，含密钥或敏感路径时脱敏
- 「建议」小节可为空，但不写空泛客套
- 本文件**不列入 `AGENTS.md` 的 `References`**：它是执行留痕，不承担日常上下文职责（依 §6 写入闸「删掉此行 Agent 会犯错吗」判定）

## 终止回复

只回复：判定模式与依据信号、`AGENTS.md` 落盘路径与实际行数、自检门是否五项全过、各过程文档的建立与补齐情况（区分「新建」「已存在跳过」）、AGENTS.md 约定处置条数、Git 与 Codegraph 的执行结果、报告落盘路径、未决的待确认条目（若有）。
