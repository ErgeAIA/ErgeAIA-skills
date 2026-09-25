---
name: init-agents-md
description: vibe-init 的执行契约：执行顺序、前置检查、Git 检查、状态机与路由、决策保全、CLAUDE 受控迁移、AGENTS 唯一源校验、过程文档落点、Codegraph 集成、初始化报告。
trigger-when: 用户说「初始化项目」「生成 AGENTS.md」「vibe-init」，或项目需要建立协作契约、补齐缺失过程文档时
role: workflow
reads-from:
  - references/agents-md-generator.md
  - references/init-env-checks.md
  - <project>/AGENTS.md（若已存在，用于决策保全与迁移主源）
  - <project>/CLAUDE.md（若已存在，作为迁移输入源，迁移完成后删除）
writes-to:
  - <project>/AGENTS.md
  - <project>/CLAUDE.md（仅受控迁移：安全闸全过后删除源文件；本技能从不创建）
  - <project>/docs/.ai/project-progress.md
  - <project>/docs/.ai/decision-log.md
  - <project>/docs/.ai/debug-log.md
  - <project>/docs/.ai/agents-changelog.md（层 C）
  - <project>/docs/.ai/init-report.md
  - <project>/docs/.ai/project-overview.md（可选）
  - <project>/docs/.ai/experience/.gitkeep
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
├── AGENTS.md                        # 唯一项目级协作契约源
├── .git/                            # 无仓库时 git init 建立
├── .codegraph/                      # 已装 codegraph 且无索引时建立
└── docs/
    ├── .ai/
    │   ├── project-progress.md      # 进度，每次会话更新
    │   ├── decision-log.md          # 开发决策，优先级高于 PRD
    │   ├── debug-log.md             # bug 记录
    │   ├── agents-changelog.md      # 层 C：AGENTS.md 变更记录
    │   ├── init-report.md           # 本次初始化执行报告
    │   ├── project-overview.md      # 可选，层 B
    │   └── experience/              # 可复用经验库（仅建空目录，内容由 vibe-distill 首次蒸馏时建）
    └── handoff/                     # 交接文档
````

## 执行顺序

按此顺序执行，不跳步、不重排；某步失败记入报告后继续，不中断：

| 序 | 步骤 | 说明 |
| -- | ---- | ---- |
| 1 | 前置检查 | 可写性、monorepo 判定 |
| 2 | Git 检查 | 仓库检测，必要时 `git init` |
| 3 | 状态识别与路由 | 按初始化状态机 A–E 判定 |
| 4 | 决策保全 | 状态 B / C / D / E 必做（判定依据见下） |
| 5 | 状态迁移 / 生成 AGENTS.md | 全新 / 增量走生成规范；迁移先写目标、验证目标、后删源 |
| 6 | 建立过程文档 | 复制模板，补齐缺口 |
| 7 | AGENTS 唯一源校验 | 实读复核 + 迁移留痕核对（见「AGENTS 唯一源校验」节） |
| 8 | Codegraph 集成 | 检测索引，或给出安装建议 |
| 9 | 初始化报告 | 汇总本次全部操作（含迁移处置计数） |
| 10 | 终止回复 | 按格式回报（含迁移结果与源文件处置） |

## 前置检查

| 检查项 | 不通过时 |
|---|---|
| 项目根是否已有 `AGENTS.md` / `CLAUDE.md`（含点目录逐查，不得只看列目录工具的默认输出） | 按下方「初始化状态机 A–E」路由；判入迁移态时先保全再处置 |
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

**判据真源**：`references/agents-md-generator.md` §2。先按项目根实际文件状态对号入座（含点目录逐查），再按其中三个可观测信号（既有契约 / 既有代码 / 既有项目文档）定模式；信号矛盾或无法查证时停下问用户，不自行归类。

### 初始化状态机（A–E）

| 状态 | 条件（以项目根实际文件为准） | 模式 | 动作 |
|---|---|---|---|
| A 全新项目 | 无 `AGENTS.md`，无 `CLAUDE.md` | 全新初始化 | 创建 `AGENTS.md`；**不创建 `CLAUDE.md`**；其余过程文档按原流程建立 |
| B 只有 AGENTS.md | 有 `AGENTS.md`，无 `CLAUDE.md` | 已初始化优化 | 读取并增量维护，只做必要增量优化；**不创建 `CLAUDE.md`** |
| C 只有 CLAUDE.md | 无 `AGENTS.md`，有 `CLAUDE.md` | 半程合成 + 受控迁移 | 按「CLAUDE 受控迁移」把 `CLAUDE.md` 整理为 `AGENTS.md`，验证后删除源 |
| D AGENTS + CLAUDE 并存 | 两者都存在 | 已初始化优化 + 受控迁移 | 以 `AGENTS.md` 为主源，把 `CLAUDE.md` 有效规则合并进去，冲突裁决留痕后删除 `CLAUDE.md` |
| E AGENTS + `.claude/` | 有 `AGENTS.md`，无 `CLAUDE.md`，项目存在 `.claude/` | 已初始化优化 | 继续以 `AGENTS.md` 为项目根协作契约；`.claude/` 内规则文件只作为决策保全输入纳入；**不因 `.claude/` 存在而创建 `CLAUDE.md`** |

- 状态机先于模式：先对号入座，再落 `<!-- mode: -->`。mode 行仍只填 §2 三值之一（C 落 `半程合成`、D 落 `已初始化优化`），迁移性质记入 `init-report.md` 与 `agents-changelog.md`，**不新增第四个 mode 值**。
- 状态 B / E 不得因为「运行时已支持 `AGENTS.md`」就新建 `CLAUDE.md`。
- 判为开源项目（存在 `LICENSE` / `CONTRIBUTING`）→ 层 B 追加许可限制与贡献约定。

## 决策保全（状态 B / C / D / E 必做）

1. 摘录既有契约文件全部条目；**无契约文件时**，摘录代码、提交、配置中可识别的现存约定，形成既有约定清单。
2. 逐条四态处置：`keep` 原样继承 / `update` 以代码现状为准改写 / `drop` 删除 / `merge` 合并去重。
3. 每一条 `update` 与 `drop` 写入 `docs/.ai/agents-changelog.md`，一行一条 `<旧值> → 处置 → <新值/去处/原因>`，**禁止静默丢失**。
4. 旧位置残留（如项目根 `references/` 下的旧决策或变更日志）：内容合并进 `docs/.ai/` 的新落点，旧文件按 `drop` 处理并留痕，**禁止新旧两处并存**。
5. 处置不下的条目标记为待确认交给用户裁决，不自行删除。
6. **源文件未被 git 跟踪时必须先留档**：`git status` 显示为未跟踪（`??`）的既有契约，一旦处置就无法从版本历史回溯。此时先把原文完整存一份到 `docs/.ai/` 下（推荐并入 `agents-changelog.md` 的存档小节），再执行 `drop` / `update`；**禁止在无留档的情况下丢弃未跟踪文件的内容**。
7. **既有档案不是六节结构时，允许按 `merge` 重组**：「已初始化优化」的「禁止整体重写」指的是**不得在没有处置记录的情况下换掉契约**，不是不能调整章节。既有档案若为项目自建的多节结构，逐条四态处置后重组为六节是**允许的**，前提是每条处置都在 `agents-changelog.md` 留痕。

**全新初始化**跳过四态处置，但仍建 `docs/.ai/agents-changelog.md` 并写一行兜底：`<无旧约定> → 全新初始化 → 直建当前 AGENTS.md`。

## 过程文档

目录结构、各文档的建立条件、`<工程标识>` 取法的单一真源是 `references/agents-md-generator.md` §4b。各文档从 `assets/docs/` 直接复制，替换 `<工程标识>` 并把 `updated` 改为当日；已有同名文件跳过，不覆盖。

| 文件 | 用途 | 维护者 |
|---|---|---|
| `docs/.ai/project-progress.md` | 进度，每次会话更新；任务开始时先读它 | `vibe-sync` |
| `docs/.ai/decision-log.md` | 开发决策（`DEC-NNN`，优先级高于 PRD），随开发持续更新 | `vibe-sync` |
| `docs/.ai/debug-log.md` | bug 记录，编号 `BUG-NNN` 递增 | `vibe-sync` |
| `docs/.ai/agents-changelog.md` | AGENTS.md 变更记录，**只在 AGENTS.md 改动时更新** | `vibe-init` 独占 |
| `docs/.ai/init-report.md` | 初始化执行记录，只追加 | `vibe-init` 独占 |
| `docs/.ai/experience/` | 可复用经验库，按领域分目录；初始化只建空目录，内容由首次蒸馏时按 `assets/experience/` 模板建立 | `vibe-distill` |
| `docs/handoff/` | 交接文档，命名 `handoff-YYYY-MM-DD-*.md` | `vibe-handoff` |

全部**只追加**，历史条目永不删除或改写；决策冲突时把旧条目标 `superseded`。

## AGENTS.md 的文档义务（必做）

生成的 `AGENTS.md` 必须让 AI 时刻知道各文档做什么、每次任务完成要同步哪些。按三处落实：

**句子原文的唯一真源是 `references/agents-md-generator.md` §5**：本表只登记「必须有哪几类义务」，不复制句子、不记条数——两处各记一份必然漂移。

| 位置 | 写什么 |
|---|---|
| `Permissions` | **接管义务**：会话开始先读 `docs/.ai/` 三件套与 `docs/handoff/` 最新一份；先复述现状与待确认项再动手。**文档义务**：改码前先读项目文档与 `decision-log`；每次会话更新 `project-progress.md`；改 AGENTS.md 前先读、改后追加 `agents-changelog.md`；改某领域代码前先读 `docs/.ai/experience/<领域>/`。**常驻纪律**：一阶段一停等验证；不得自行宣称已修复，须由用户验证；既有文件只做最小精确补丁。另含 `IMPORTANT` 定位一句与 `禁止` 两类 |
| `Conventions` | 会话文档体系、bug 追加（`vibe-sync` 写）、交接命名、交接文档同日多份的取新判据、改文档须同步 `updated`、改 AGENTS.md 须留变更记录、经验库按领域分目录且正文可改写 |
| `References` | 项目自带文档 + `docs/.ai/` 各过程文档（含 `docs/.ai/experience/`）+ `docs/handoff/`，逐条**条件式指针** `- <何时读> → 见 <path>`；触发条件按使用场景登记，不按目录罗列 |

**接管为什么写在 `Permissions` 而不是做成触发词**：触发词要求用户先想起它，A 层义务每会话自动生效。写进去之后，「新会话先弄清现状」不再依赖任何人记得敲命令——这是本技能对「AI 未调用技能」这个前提的唯一覆盖手段。

`Conventions` 的「交接文档同日多份」一行必须写清取新判据，**不得依赖目录列出的顺序**：

| 观察到的现象 | 要求 Agent 的行为 |
|---|---|
| 交接文档同日多份 | 按文件名里的日期取最新（兼容 `YYYY-MM-DD` 与 `YYYYMMDD` 两种写法）；同日多份再取 frontmatter `updated` 最新者，仍不可判则列出问用户 |

原因：**字典序不等于时间序**。`handoff-2026-08-22-evening.md` 排在 `handoff-2026-08-22.md` **之前**（`-` 0x2D < `.` 0x2E）；旧写法的 `handoff-20260802.md` 更会排在所有 `handoff-2026-*` **之后**（`-` < `0`）——取「目录里最后一条」会取到一个多月前的文件。

## 保证层级（写文档时按此判断）

规则的效力取决于该文件**是否必然被读到**，分三层：

| 层 | 前提 | 效力 |
|---|---|---|
| A | `AGENTS.md` 被运行时自动注入 | 每会话必读，**唯一能覆盖「AI 未调用本技能」这个前提的层**。义务只写在这里才算硬约束 |
| B | 本技能被调用 | 只在走 `vibe-init` 时生效：§7 自检门、终止回复报告条数 |
| C | 文件被打开才读到 | 过程文档模板内的说明（如 `agents-changelog.md` 头部那句「每改动一次必须追加一行」）**不构成保证**，只是文件自述 |

结论：**过程文档之间不要互相充当强制机制**。要保证某件事，就把它写进 `AGENTS.md`（A 层）；A 层要覆盖「AI 会去读某个文件」，必须用 `前先读` 这类措辞把读取动作写进义务本身。`References` 负责**发现 + 调度**——`- <触发条件> → 见 <path>` 写清何时读哪个文件，只列文件不写「何时读」等于把指引链断在中间；把读取变成强制义务仍归 `Permissions`，两者不互相替代。

具体文本见 `references/agents-md-generator.md` §5。

## CLAUDE 受控迁移（状态 C / D）

`AGENTS.md` 是唯一项目级协作契约源；`CLAUDE.md` 在迁移中只是**输入源**，不是长期运行时源。迁移完成后项目根不得再以 `CLAUDE.md` 作为协作契约存在。

迁移不是机械重命名，也不是保留指针。每条旧规则按「keep / update / merge / drop」四态处置（处置与留痕规则同决策保全节），并逐条检查是否存在 Claude 专属语法、Claude 专属工具说明或已过时规则——此类条目按 `drop` 处置并留痕。

### 执行顺序（状态 C：只有 CLAUDE.md）

1. 完整读取 `CLAUDE.md`
2. 提取全部有效项目规则
3. 按 `references/agents-md-generator.md` 的生成规范结构化整理
4. 形成新的 `AGENTS.md`（六节结构）
5. 对照旧 `CLAUDE.md` 做完整内容保全
6. 把无法明确处置的内容标记为待确认
7. 写入 `AGENTS.md`
8. 实读验证 `AGENTS.md` 已成功落盘且内容完整
9. 在 `docs/.ai/agents-changelog.md` 记录迁移
10. 删除 `CLAUDE.md`
11. 在 `init-report.md` 记录迁移与删除

**严禁先删 `CLAUDE.md` 再建 `AGENTS.md`**——必须先保证 AGENTS 成功落盘，再删除源文件。

### 执行顺序（状态 D：AGENTS + CLAUDE 并存）

1. 完整读取 `AGENTS.md`
2. 完整读取 `CLAUDE.md`
3. 分别建立规则清单
4. 对两份规则做去重、冲突与来源分析
5. 以 `AGENTS.md` 作为主源
6. `CLAUDE.md` 中 AGENTS 没有的有效规则 → 合并进 `AGENTS.md`
7. `CLAUDE.md` 中与 AGENTS 冲突的规则 → 按项目真实代码 / 配置 / 文档裁决
8. 可验证的过时规则 → `drop`
9. 无法裁决的冲突 → 标记待确认，不自行取舍
10. 将全部 update / drop / merge / migration 留痕到 `agents-changelog.md`
11. 写入最终 `AGENTS.md`
12. 实读验证 `AGENTS.md` 完整且可读
13. 删除 `CLAUDE.md`
14. 在 `init-report.md` 记录此次迁移

### 迁移保全规则

- 旧 `CLAUDE.md` 中每条有效规则必须落入三处之一：`keep` / `merge` → 进入 `AGENTS.md`；`drop` → 在 `agents-changelog.md` 记录原因。**不得出现「既不进 AGENTS.md、也无 drop 记录」的规则。**
- 待确认条目写入终止回复交用户裁决；未裁决前源文件保留。
- 源文件未被 git 跟踪时，先按决策保全的留档规则把原文存入 `agents-changelog.md` 存档小节，再执行处置。
- 迁移记录若早于「建立过程文档」步骤落盘：先按 §4b 模板建立 `docs/.ai/agents-changelog.md`，再写迁移条目——**处置留痕必须先于源文件删除**。

### 冲突裁决（状态 D）

裁决依据是**事实，不是文件名**——`AGENTS.md` 并不天然比 `CLAUDE.md` 正确，不能把「文件名优先」误写成「事实优先」。完整裁决阶梯见 `references/agents-md-generator.md` §2b，要点：

1. 两份文件都作为历史来源读取
2. 代码 / 配置 / 实际项目状态作为事实证据
3. 当前真实事实明确 → update `AGENTS.md`
4. 只是文本版本不同但意图一致 → merge
5. 一条明显过时 → drop 并留痕
6. 两条都合理且适用条件不同 → 并存，各自标注适用条件
7. 相同适用条件且无法裁决 → 停下问用户，不猜测

### 安全删除闸

删除旧 `CLAUDE.md` 前必须**全部满足**，任何一项不满足即禁止删除：

- `AGENTS.md` 已创建 / 更新成功
- `AGENTS.md` 重新实读通过（内容完整、可读）
- 迁移内容校验通过（每条有效规则已落入 keep / merge，或已有 drop 留痕）
- `docs/.ai/agents-changelog.md` 已成功写入迁移记录

闸门不过时，终止回复必须写明：**迁移未完成，原 CLAUDE.md 保留**。后续步骤照常继续，但不得宣称迁移完成。

## AGENTS 唯一源校验（执行顺序步骤 7）

校验靠实读与核对，不是纯字符串匹配：

1. 列出项目根实际文件，确认不存在本次执行新建的 `CLAUDE.md`（`.claude/` 目录不是 `CLAUDE.md`，不在此列）
2. `AGENTS.md` 存在——重新打开并实读内容，非仅做存在性检测
3. `AGENTS.md` 可读：六节结构完整，迁移并入的内容确实就位
4. `AGENTS.md` 是当前唯一项目级协作契约：本技能未创建、未保留任何 `CLAUDE.md` 契约文件；项目其他既有第三方规则文件（`.cursorrules` / `GEMINI.md` 等）不属于本闸处置范围，其内容已在决策保全中读取与处置
5. 若原存在 `CLAUDE.md`：迁移记录已在 `agents-changelog.md`，处置计数与本次初始化报告一致，源文件已按安全闸删除（或明确保留并写明原因）

校验失败 → 按失败模式处理：能修复的当场修复并复验；不能修复的列明未过项，不宣称完成。

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
| 契约迁移 | `CLAUDE.md` → `AGENTS.md`（状态 C / D） | 源 `<project>/CLAUDE.md` → `AGENTS.md` | 完成 / 跳过 / 失败（保留源） | keep N / update N / merge N / drop N；冲突待确认 N |
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

只回复：判定状态（A–E）与依据信号、`AGENTS.md` 落盘路径与实际行数、自检门是否五项全过、各过程文档的建立与补齐情况（区分「新建」「已存在跳过」）、AGENTS.md 约定处置条数、迁移执行结果（状态 C / D：迁移类型、四态处置计数、冲突与裁决情况、`CLAUDE.md` 是否已删除——未删则写明卡在哪条闸）、AGENTS 唯一源校验结论、Git 与 Codegraph 的执行结果、报告落盘路径、未决的待确认条目（若有）。
