---
name: vibe-buddy
description: "AI 编程（vibe coding）全过程的项目侧协作管理。当用户用 AI 开发项目、要让下一个会话或下一个 agent 接得上时启用：初始化项目协作契约（AGENTS.md，含 CLAUDE.md 迁移）、同步进度与决策、写跨会话交接、蒸馏可复用经验，或对开发类项目做只读审查（代码质量、架构、技术栈）。产物只落在该项目内，不管理 Agent 自身记忆；也可直接说 vibe-init、vibe-sync、vibe-handoff、vibe-distill、vibe-audit。Not for: Skill 项目评审（交 skill-workshop）、任务计划与需求转译、Git 提交与代码改动、CHANGELOG 规范化（交 changelog-manager）。"
metadata:
  author: ErgeAIA
  version: "1.6.1"
---

# vibe-buddy

## 定位

**vibe coding buddy**——用 AI 编程的人的项目侧伙伴，管的是 AI 编程**全过程**里那些会话一结束就蒸发的协作状态。

Core Task：

```text
当用户用 AI 开发一个项目时，
把契约、进度与决策、跨会话交接、可复用经验固化成项目内可审计的文件，
让下一次会话、下一个 agent 不必从零问起；并可对开发类项目做只读审查。
```

作用域是**单个项目**：产物全部落在 `<project>/` 内（`AGENTS.md`、`docs/.ai/`、`docs/handoff/`）。**不是 Agent 记忆管理技能**——运行时自身的记忆目录、跨项目的个人知识库都不碰（见「非目标」）。

## 核心原则

把项目的协作状态当成**可审计的文本资产**：规则留在 `AGENTS.md`，过程记录留在 `docs/.ai/`，会话交接留在 `docs/handoff/`。

1. **不覆盖** —— 已有文件只追加；需要新文件时先扫描目录再取名，永不重写既有内容。**唯一例外是受控迁移**（CLAUDE.md → AGENTS.md）：迁移允许重组目标契约，但必须完整读取源、逐条四态处置并留痕、先写目标、验证目标、最后才删源——不是放开重写，是可追溯的重组。
2. **不猜测** —— 读不到的事实写占位符，绝不编造版本号、路径、命令、结论。
3. **不越界** —— 只**写**协作契约与过程文档区（路径见下方产物布局）及**可选**的项目根 `CHANGELOG.md`（仅 `vibe-sync`，且文件已存在时追加），不改项目其他文件；唯一的删除动作是受控迁移完成后删除源 `CLAUDE.md`（闸门见 `references/init-agents-md.md`）；**读**可及项目内任意文件与白名单只读命令；不发布。
4. **不静默** —— 删除或改写必须留下「旧值 → 处置 → 新值」的可见记录。
5. **只读层（仅 `vibe-audit`）** —— 写入纪律只约束审计报告这一个落点：对报告文件本身仍「不覆盖 / 不静默」；不改被审项目任何其他文件；发现问题只报告，不代写 `project-progress.md` / `decision-log.md` / `debug-log.md`；只给问题 + 证据 + 方向，不生成待办与排期。第 2、3 条对审计照常生效。

## 路由与硬规则

### @步骤1: 路由决策

| 场景 | 命中信号 | 跳转到 |
|---|---|---|
| 项目首次接入协作管理，或补齐缺失的过程文档 | 「初始化项目」「生成 AGENTS.md」「vibe-init」；或项目缺 `AGENTS.md` 与 `docs/.ai/`；或项目存在 `CLAUDE.md` 要迁移/整理成唯一契约 | `references/init-agents-md.md` |
| 任务完成，要沉淀进度、决策、调试与用户可见变更日志，或回填工具链与命令 | 「同步进度」「更新项目进度」「把踩的坑记下来」「更新日志」「vibe-sync」 | `references/sync-progress.md` |
| 换会话、换 agent、上下文将满，要留下一份交接文档 | 「交接上下文」「写交接文档」「vibe-handoff」 | `references/handoff-context.md` |
| 一轮开发告一段落，要把其中反复成立的做法提炼成可复用经验 | 「经验蒸馏」「提炼可复用经验」「vibe-distill」 | `references/distill-experience.md` |
| 审查开发类项目（前端 / 后端 / Web）的代码质量、架构与技术栈，并要不动栈的优化方向 | 「审查项目」「审查技术栈」「vibe-audit」 | `references/audit-project.md` |

### @步骤2: 强规则摘要

- 🔴 **CHECKPOINT · 先确认再执行**：识别触发词后先回一行路由确认（触发词 / 将读的契约 / 待做的前置检查）；🛑 本技能的「停」= 只输出文字、不碰任何文件，用户确认前不产生任何写入。
- 🛑 **STOP · 目标类型前置判定（仅 `vibe-audit`）**：执行前先判目标。命中「含 `SKILL.md` 且 frontmatter 有 `name`」→ 停止自审，只输出转交说明（目标路径 / 已观测 frontmatter 字段 / 是否含 `scripts/` / 判定依据一句话）并指向 skill-workshop。无法判定 → 停下问用户，不猜、不自审。
- **写入前声明**：操作类型 / 目标路径 / 是否覆盖 / 风险等级；同一触发词内只声明一次。
- **一次只走一个触发词**：「同步并交接」拆成两轮各自确认，不自动串联。
- 🛑 **STOP · 前置缺失即停**：如 `vibe-sync` 找不到 `docs/.ai/` 时引导先跑 `vibe-init`，绝不代建。
- **接管不由本技能触发**：新会话的「读项目档案 + 复述现状」是目标项目 `AGENTS.md` 的 `Permissions` 义务，每次会话自动生效。听到「接管 / 接手 / 继续上次」这类措辞时不必触发本技能——那条义务已经在跑。
- **终端命令白名单**：默认不运行命令。`vibe-init` 可做 Git 仓库检测与初始化、codegraph 检测与建索引；`vibe-sync`、`vibe-handoff`、`vibe-distill` 与 `vibe-audit` 可做只读 Git 核对（各自允许的子集见白名单）。构建、测试、依赖安装、`git add` / `commit` / `push` 一律不做；白名单单一真源见 `references/command-policy.md`。
- **产物必须脱敏**：密钥、token、凭据、连接串、个人隐私一律不落盘；无法脱敏则拒绝写入。
- **不重复已有产物**：规格、计划、决策、提交、diff 已有的内容，用路径引用。
- **契约区与事实区**：`AGENTS.md` 的契约区（Permissions / Conventions / References / 章节结构）只由 `vibe-init` 写，任何改动都必须在 `docs/.ai/agents-changelog.md` 留一行；事实区（Toolchain / Commands 表数据）可由 `vibe-sync` 回填，属填事实不必留痕。
- 🔴 **CHECKPOINT · AGENTS.md 唯一源**：`AGENTS.md` 是唯一项目级协作契约源。`vibe-init` 按五状态机（A–E，见 `references/init-agents-md.md`）执行，任何路径都**不创建、不维护、不镜像 `CLAUDE.md`**；旧 `CLAUDE.md` 走受控迁移并入 `AGENTS.md`，安全闸全过后才删除源文件，迁移失败则保留源并如实报告。
- **记录与提炼分开**：`vibe-sync` 记录流水事实（进度 / 决策 / 调试）并可选追加 `CHANGELOG.md` 用户可见变更，`vibe-distill` 提炼可复用规则（`docs/.ai/experience/`），互不代做。
- 🔴 **CHECKPOINT · 蒸馏不裁决冲突**：新旧经验冲突时**先比适用条件**；前提不同即两条并存并各自标注，前提相同才停下问用户，不自行取舍。

## 产物布局

| 产物 | 路径 | 写入者 |
|---|---|---|
| AI 协作契约（唯一契约源） | `<project>/AGENTS.md` | `vibe-init` 写契约区；`vibe-sync` 回填 Toolchain 与 Commands 表 |
| 项目进度，实时更新 | `<project>/docs/.ai/project-progress.md` | `vibe-init` 建模板，`vibe-sync` 维护 |
| 决策日志，优先级高于 PRD，随开发持续更新 | `<project>/docs/.ai/decision-log.md` | `vibe-init` 建模板，`vibe-sync` 追加 |
| bug 修复经验 | `<project>/docs/.ai/debug-log.md` | `vibe-init` 建模板，`vibe-sync` 追加 |
| AGENTS.md 变更记录，只在契约改动时写 | `<project>/docs/.ai/agents-changelog.md` | `vibe-init` 独占 |
| 初始化执行报告，只追加 | `<project>/docs/.ai/init-report.md` | `vibe-init` 独占 |
| 项目概览（可选，按需自建） | `<project>/docs/.ai/project-overview.md` | `vibe-init` |
| 可复用经验库，按领域分目录 | `<project>/docs/.ai/experience/` | `vibe-init` 建空目录；内容由 `vibe-distill` 写 |
| 会话交接文档，带 frontmatter | `<project>/docs/handoff/handoff-YYYY-MM-DD[-slug].md` | `vibe-handoff` |
| 项目审计报告，只追加 | `<project>/docs/.ai/audit/audit-YYYY-MM-DD[-slug].md` | `vibe-audit`；目录缺失时由 `vibe-audit` 首次执行时建（含 `.gitkeep`） |
| 变更日志（可选，仅已存在时追加） | `<project>/CHANGELOG.md` | `vibe-sync`；**不代建**——无此文件则跳过并在终止回复提示（完整规范归 changelog-manager 或用户自建） |

`vibe-init` 不创建、不维护、不生成指针、不复制镜像 `CLAUDE.md`；项目已有 `CLAUDE.md` 时按受控迁移并入 `AGENTS.md` 后删除源文件（状态机与迁移细则见 `references/init-agents-md.md`）。

## 何时读 references

- 要建 `AGENTS.md`、判定初始化状态（A–E）、执行 CLAUDE 迁移、补齐缺失文档 → `references/init-agents-md.md`
- 要执行 `AGENTS.md` 的生成规范本身（句式契约、黑名单、自检门） → `references/agents-md-generator.md`
- 要走 Git 检查与 Codegraph 集成 → `references/init-env-checks.md`（判定表与失败处理）
- 要运行任何终端命令前 → `references/command-policy.md`（白名单与各触发词允许的子集）
- 要落地 `docs/.ai/` 各文档 → `assets/docs/project-progress.md` 等五份模板（原样复制，只换 `<工程标识>` 与 `updated`）
- 要沉淀进度、决策与调试记录 → `references/sync-progress.md`
- 要生成交接文档 → `references/handoff-context.md`
- 要蒸馏可复用经验 → `references/distill-experience.md`
- 要审查开发类项目的代码质量、架构与技术栈 → `references/audit-project.md`
- 要落地经验库 → `assets/experience/` 下 `README.md` 与 `changelog.md` 两份模板（首次蒸馏时原样复制，只换 `<域标识>`、`<工程标识>` 与 `updated`）
- 改过 description 要回归触发 → `references/trigger-test-set.md`

## 失败模式与兜底

| 触发条件 | 一线修复 | 仍失败兜底 |
|---|---|---|
| 前置文件缺失（如无 `docs/.ai/` 却要 sync） | 回复缺失项，引导先跑 `vibe-init` | 用户坚持从零建立 → 转 `vibe-init`，不就地代建 |
| `vibe-init` 遇到已有文档 | 普通路径只补缺失项，已存在的文件一字不动；受控迁移（状态 C / D）按迁移契约执行 | 内容冲突且无法判定 → 停下请用户裁决 |
| CLAUDE → AGENTS 迁移中断（读取、整理或写入任一步失败） | 停止迁移，按已完成部分留痕 | 保留 `CLAUDE.md` 原样，终止回复「迁移未完成，原 CLAUDE.md 保留」 |
| `AGENTS.md` 迁移写入后实读验证失败 | 修复缺项并复验 | 仍失败 → 禁止删除 `CLAUDE.md`，报告失败原因与已留痕部分 |
| `AGENTS.md` 与 `CLAUDE.md` 规则冲突 | 以代码 / 配置 / 实际项目状态为事实证据裁决 | 相同适用条件且证据不足 → 停下问用户，未裁决前不删 `CLAUDE.md` |
| `CLAUDE.md` 删除前置闸未全过 | 补齐缺项后复闸 | 禁止删除，终止回复「迁移未完成，原 CLAUDE.md 保留」 |
| AGENTS 唯一源校验失败 | 按缺项修复（补迁移记录 / 补契约内容） | 无法修复 → 终止回复列明未过项，不宣称完成 |
| 同日已有同名交接文档 | 加语义后缀（`handoff-YYYY-MM-DD-<slug>.md`） | 后缀仍冲突 → 加两位序号（`-02`），不回头打扰用户 |
| 本次会话无可交接内容 | 明说「没有可交接的实质进展」，不生成空文档 | 用户坚持 → 只写有对话依据的条目，宁缺勿造 |
| 关键事实采集不到（项目定位、命令、权限边界） | 停下问用户，不猜、不编造 | 用户未答 → 写占位并在终止回复列为待确认项 |
| 白名单命令失败（`git init` / `codegraph init`） | 记「失败 + 原因」，继续后续步骤 | 仍失败 → 不自动重试，在报告建议里提示手动执行 |
| 同步时上下文已被压缩或记忆不可靠 | 先按客观源（git 核对 / 最新交接文档 / 过程文档）重建事实再落笔 | 无法重建 → 明说「本次进展无法核实」，不写条目、不凭记忆补全 |
| 本次会话无稳定增量 | 明说「本次无可同步的稳定增量」，不写文件 | 用户要求留痕 → 追加一行说明性占位，不编造内容 |
| 本轮没有可蒸馏的稳定经验 | 明说「本轮无可蒸馏的稳定经验」，不编造 | 用户坚持 → 只写有事实源支撑的条目，宁缺勿造 |
| 本轮原料区间已蒸馏过 | 指向 `changelog.md` 里已记录的那一轮，不重复蒸 | 用户要求重蒸 → 只蒸新增部分并在备注说明 |
| 新旧经验冲突 | 先比适用条件：前提不同则两条并存、各自标注 | 前提相同 → 停下问用户，不自行取舍 |
| 待写内容含密钥 / 凭据 / 隐私 | 脱敏为占位符后写入 | 无法安全脱敏 → 拒绝写入并说明原因 |
| 项目无 `CHANGELOG.md` 却要写更新日志 | 不创建文件；终止回复说明可自建或用 changelog-manager | 用户明确要求代建最小骨架 → 仅在用户书面确认后建，并注明非 Keep a Changelog 全规范 |
| 参考文件缺失或读不通 | 报告缺失路径，停止执行 | 用户要求硬做 → 拒绝，缺规则不做 |
| `vibe-audit` 目标为 Skill 项目 | 只输出转交说明并指向 skill-workshop | 用户坚持本技能内审 → 拒绝，说明标尺不适用 |
| `vibe-audit` 目标类型无法判定 | 停下问用户，不猜 | 用户未答 → 不执行，列为待确认项 |
| 审计证据读不到（文件不存在 / 行号对不上） | 该条标「证据不足」，不写入断言 | 全篇无法取证 → 中止，只输出已取证部分 |
| 审计报告当日已有同名文件 | 加语义后缀（`audit-YYYY-MM-DD-<slug>.md`） | 后缀仍冲突 → 加两位序号（`-02`） |

## Gotchas

- `AGENTS.md` 是**规则契约**，不承载进度与待办；进度写 `docs/.ai/project-progress.md`。
- `docs/.ai/` 的**进度 / 决策 / 调试**三份只追加；决策冲突时把旧条目改标 `superseded`，不删除历史条目。
- `AGENTS.md` 是项目级**唯一协作契约源**；`CLAUDE.md` 迁移完成后不得继续作为项目级协作契约存在，也不得靠新建空 `CLAUDE.md` / 指针文件解决兼容问题。
- 交接文档写给**另一个 agent**：能从 `git log`、diff、规格文档里读到的，写路径，不复述。
- `docs/.ai/` 是**过程档案区**不是人类文档区；人类项目文档（README、设计稿）不放这里。
- 过程文档的 frontmatter `updated` 必须随每次修改同步改当日；漏改等于让 `updated` 说谎。
- `vibe-init` 对半程项目**只补齐缺失文档**，绝不重写已有文件——哪怕内容看起来过时；受控迁移（CLAUDE → AGENTS）是唯一例外，且必须可追溯。
- 不新增 `AGENTS.md` 章节：文档义务写进固定的 `Permissions` 与 `Conventions`，不另起段落。
- `docs/.ai/experience/` 是**可移植产物**，不是项目过程档案：**正文可改写**（错的规则留着会持续误导），历史靠 `changelog.md` 保追溯；`docs/.ai/` 其余三份则严格**只追加**。
- 经验条目**五要素缺一不可**（主张 / 适用 / Why / How / 反例）。写不出反例说明还没想清楚，不入库。
- 经验库的主题名用领域名（`ui` / `frontend` / `motion` / …），不另造词——外送汇总时它就是分域依据。

## 反例黑名单（已知会犯错的写法）

| 不许做 | 为什么 | 正确做法 |
|---|---|---|
| 按目录列出的顺序取「最新」交接文档 | 字典序 ≠ 时间序：`handoff-2026-08-22-evening.md` 排在 `handoff-2026-08-22.md` **之前**（`-` < `.`）；旧写法 `handoff-20260802.md` 更会排在所有 `handoff-2026-*` **之后** | 解析文件名里的日期做比较；同日多份再比 frontmatter `updated` |
| 从 PRD / 计划 / 设计稿填 `Toolchain` 与 `Commands` | 那是意图不是事实，会把「建议」写成「已建立」 | 只取锁定文件、依赖清单、配置文件原文与实跑输出 |
| 用文件大小判断文件有没有内容 | 规则文件可能是符号链接，大小报 0 而内容非空 | 实际读取内容再判 |
| 把可能含 `##` 的模板放进无围栏的代码块 | 模板标题会变成文档自身的章节标题 | 模板一律用 4 个以上反引号围栏 |

## 非目标

- 不做任务拆解、排期、待办追踪。
- 不把模糊需求转译成 PRD 或结构化指令。
- 不写代码、不重构、不运行构建与测试命令；Git 仅限白名单内的仓库检测、初始化与只读核对。
- 不管理规格与变更的生命周期。
- 不做对外发布，不代发内容。
- 不管理 Agent 自身的记忆：运行时记忆目录、跨项目共享的个人记忆库与外部知识库都不读写；也不把经验条目写入任何外部仓库或目录，外送由用户另行触发。本技能只服务**当前这一个项目**。
- 不提供「接管汇报」触发词：那是目标项目 `AGENTS.md` 的义务，不是本技能的入口。
- 不评审 Skill 项目（归 skill-workshop）。
- 审计不产出待办、排期与整改清单；只给问题 + 证据 + 方向。

## 验证

| 触发词 | 成功判定 |
|---|---|
| `vibe-init` | 状态判定（A–E）有可观测依据；`AGENTS.md` 六节成文且未新增章节；接管义务与常驻纪律已写入 `Permissions`；`References` 每条为条件式指针（含触发条件）；`AGENTS.md` 存在、实读可读且为唯一项目级协作契约；本次执行未新建 `CLAUDE.md`；若存在旧 `CLAUDE.md`：有效内容已迁移、四态处置已留痕、`AGENTS.md` 已实读验证、源文件已安全删除（未删则明示原因）；`docs/.ai/` 各过程文档与 `docs/handoff/` 就位；Git 与 Codegraph 检查有结论；`init-report.md` 已记录全部实际操作（含迁移处置计数）；缺失项已补齐，既有文件未被覆盖 |
| `vibe-sync` | `project-progress.md` 有新进展且 `updated` 已同步；有决策时 `decision-log.md` 已追加；调试定位到根因时 `debug-log.md` 已追加 `BUG-NNN`；项目根已有 `CHANGELOG.md` 且本轮含用户可见变更时已按其既有格式追加（无文件或无可见变更则明示跳过）；`AGENTS.md` 仅事实区被回填，契约区未动 |
| `vibe-handoff` | 交接文档落入 `docs/handoff/`，frontmatter 合规且 `updated` 为当日，正文只展开「别处读不到」的四类、其余写指针，未覆盖既有文件 |
| `vibe-distill` | 条目五要素齐全且各有事实源；编号在主题内递增；`experience/changelog.md` 已追加本轮（原料区间 + 覆盖主题 + 产出）；冲突已标出而非自行取舍 |
| `vibe-audit` | 每条结论带 `路径:行` 或明写「证据不足」；报告落入 `docs/.ai/audit/` 且 `updated` 为当日；未改动被审项目任何文件；Skill 项目已转交而非自审 |
