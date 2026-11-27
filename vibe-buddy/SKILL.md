---
name: vibe-buddy
description: "固化项目协作契约、进度与跨会话交接，产出开发项目只读审查报告与档案体检结论。Use when 用户说初始化项目、生成 AGENTS.md、同步进度、把踩的坑记下来、写交接文档、经验蒸馏、审查项目、审这次改动、只看安全、发版前检查、体检档案或收尾，或直呼 vibe- 命令。"
metadata:
  author: ErgeAIA
  version: "1.11.0"
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

作用域是**单个项目**：产物全部落在 `<project>/` 内（`AGENTS.md`、`docs/agents/`、`docs/handoff/`）。**不是 Agent 记忆管理技能**——运行时自身的记忆目录、跨项目的个人知识库都不碰（见「非目标」）。

## 核心原则

把项目的协作状态当成**可审计的文本资产**：规则留在 `AGENTS.md`，过程记录留在 `docs/agents/`，会话交接留在 `docs/handoff/`。

1. **不覆盖** —— 已有文件只追加；需要新文件时先扫描目录再取名，永不重写既有内容。**唯一例外是受控迁移**（CLAUDE.md → AGENTS.md）：迁移允许重组目标契约，但必须完整读取源、逐条五态处置并留痕、先写目标、验证目标、最后才删源——不是放开重写，是可追溯的重组。
2. **不猜测** —— 读不到的事实写占位符，绝不编造版本号、路径、命令、结论。
3. **不越界** —— 只**写**协作契约与过程文档区（路径见下方产物布局）及**可选**的项目根 `CHANGELOG.md`（仅 `vibe-sync`，且文件已存在时追加），不改项目其他文件；唯一的删除动作是受控迁移完成后删除源 `CLAUDE.md`（闸门见 `references/init-agents-md.md`）；**读**可及项目内任意文件与白名单只读命令；不发布。
4. **不静默** —— 删除或改写必须留下「旧值 → 处置 → 新值」的可见记录。
5. **只读层（`vibe-audit` / `vibe-check`）** —— 写入纪律只约束报告与体检这一个落点：对报告文件本身仍「不覆盖 / 不静默」；不改被审项目任何其他文件；发现问题只报告，不代写过程文档；只给问题 + 证据 + 方向，不生成待办与排期。`vibe-check` 更进一步：**一个文件都不写**。第 2、3 条对二者照常生效。

## 路由与硬规则

### @步骤1: 路由决策

| 场景 | 命中信号 | 跳转到 |
|---|---|---|
| 项目首次接入协作管理，或补齐缺失的过程文档 | 「初始化项目」「生成 AGENTS.md」「vibe-init」；或项目缺 `AGENTS.md` 与 `docs/agents/`；或项目缺 `.gitignore` / `CHANGELOG.md` / `README.md`；或项目存在 `CLAUDE.md` 要迁移/整理成唯一契约 | `references/init-agents-md.md` |
| 任务完成，要沉淀进度、决策、调试与用户可见变更日志，或回填工具链与命令 | 「同步进度」「更新项目进度」「把踩的坑记下来」「更新日志」「vibe-sync」 | `references/sync-progress.md` |
| 换会话、换 agent、上下文将满，要留下一份交接文档 | 「交接上下文」「写交接文档」「vibe-handoff」 | `references/handoff-context.md` |
| 一轮开发告一段落，要把其中反复成立的做法提炼成可复用经验 | 「经验蒸馏」「提炼可复用经验」「vibe-distill」 | `references/distill-experience.md` |
| 审查开发类项目的代码质量、架构与技术栈，并要不动栈的优化方向；含「只审本次改动」与「只看安全」两种模式 | 「审查项目」「审查技术栈」「审这次改动」「只看安全」「vibe-audit」 | `references/audit-project.md` + `references/audit-checklist.md` |
| 发版前检查、定版本依据、记发布记录与回滚点 | 「准备发版」「发版前检查」「这次发布记一下」「vibe-release」 | `references/release-checklist.md`（**只持契约，不执行命令**） |
| 只想看协作档案健不健康：`updated` 过期、编号断裂、台账不一致、产物超阈值 | 「体检」「检查项目档案」「文档是不是过期了」「vibe-check」 | `references/check-artifacts.md`（**只读，不写任何文件**） |
| 一轮开发结束要收尾（同步进度 + 总结经验 + 留交接 + 文档同步） | 「收尾」「会话收尾」「vibe-wrap」 | 先自审，再按下方 triage 表**串行执行** `vibe-sync` → `vibe-distill` → `vibe-handoff`，中途不停 |

**对象分流（防抢）**：`vibe-check` 看**档案**，`vibe-audit` 看**代码**。用户只说「检查一下这个项目」时**问一句**查档案还是查代码，不自行归类。含 `SKILL.md` 的项目要审质量 → 转 skill-workshop。

### @步骤2: 强规则摘要

- 🔴 **自审闸 · 唯一的前置停顿**：识别触发后先输出一次自审（≤4 行），再动手——① 本轮将写的产物清单；② 每项依据（哪条事实触发它）；③ 是否触及高风险（覆盖既有文件 / 删除源文件 / CLAUDE 迁移 / 写白名单外路径）；④ 显式跳过的产物与原因码。**无高风险 → 连续执行到完，中途不再停**；有高风险 → 只针对那一件事停一次。🛑 本技能的「停」= 只输出文字、不碰任何文件。
- 🛑 **STOP · 目标类型前置判定（`vibe-audit` / `vibe-check`）**：执行前先判目标。`vibe-audit` 命中「含 `SKILL.md` 且 frontmatter 有 `name`」→ 停止自审，只输出转交说明（目标路径 / 已观测 frontmatter 字段 / 是否含 `scripts/` / 判定依据一句话）并指向 skill-workshop。`vibe-check` 只查档案，目标含 `SKILL.md` 且要审质量 → 同样转交。无法判定 → 停下问用户，不猜、不自审。
- **写入前声明并入自审**：操作类型 / 目标路径 / 是否覆盖 / 风险等级一次说完，不逐文件重复声明。**只有高风险四类**（覆盖既有文件、删除源文件、`CLAUDE.md` 迁移、跨白名单写入）必须拿到用户点头，其余动作不按触发词逐个确认；「同步并交接」这类组合意图在自审里列全，通过后串行执行。
- 🛑 **STOP · 前置缺失即停**：如 `vibe-sync` 找不到 `docs/agents/` 时引导先跑 `vibe-init`，绝不代建。
- **接管不由本技能触发**：新会话的「读项目档案 + 复述现状」是目标项目 `AGENTS.md` 的 `Permissions` 义务，每次会话自动生效。听到「接管 / 接手 / 继续上次」这类措辞时不必触发本技能——那条义务已经在跑。
- **终端命令白名单**：默认不运行命令。`vibe-init` 可做 Git 仓库检测与初始化、codegraph 检测与建索引；`vibe-sync`、`vibe-handoff`、`vibe-distill` 与 `vibe-audit` 可做只读 Git 核对（各自允许的子集见白名单）。构建、测试、依赖安装、`git add` / `commit` / `push` 一律不做；白名单单一真源见 `references/command-policy.md`。
- **产物必须脱敏（单一真源）**：密钥、token、凭据、连接串、个人隐私一律不写入任何产物；发现即替换为占位符，无法安全脱敏则拒绝写入并说明原因。命令输出的截断与脱敏细则见 `references/command-policy.md`，各工作流只引用本条，不复述。
- **不重复已有产物**：规格、计划、决策、提交、diff 已有的内容，用路径引用。
- **契约区与事实区**：`AGENTS.md` 的契约区（Permissions / Conventions / References / 章节结构）只由 `vibe-init` 写，任何改动都必须在 `docs/agents/agents-changelog.md` 留一行；事实区（Toolchain / Commands 表数据）可由 `vibe-sync` 回填，属填事实不必留痕。
- 🔴 **CHECKPOINT · AGENTS.md 唯一源**：`AGENTS.md` 是唯一项目级协作契约源。`vibe-init` 按五状态机（A–E，见 `references/init-agents-md.md`）执行，任何路径都**不创建、不维护、不镜像 `CLAUDE.md`**；旧 `CLAUDE.md` 走受控迁移并入 `AGENTS.md`，安全闸全过后才删除源文件，迁移失败则保留源并如实报告。
- **记录与提炼分开**：`vibe-sync` 记录流水事实（进度 / 决策 / 调试）并可选追加 `CHANGELOG.md` 用户可见变更，`vibe-distill` 提炼可复用规则（`docs/agents/experience/`），互不代做。
- **契约只收约束**：`AGENTS.md` 是每会话自动注入的 system prompt，只留「不这样就会做错」的规则。变更日志、人读说明、决策叙事、日期化裁决出处、执行流水一律不写进去，按 `references/agents-md-generator.md` §6b 迁往各自归宿；有效规则写错位置的走 `relocate`（原文进新落点、原处留指针、留痕），不走 `drop`。增量维护时必扫存量杂音，扫完必须让产物自带反杂音义务行，否则下一轮重新积灰。
- **仓库文档只委托不自写**：`README.md` 生成或优化 → `shuxu`；`CHANGELOG.md` 的建立、结构变更与版本归档 → `changelog-manager`；`.gitignore` 新增或修正 → `git-manager`。三者缺失时由 `vibe-init` 检测、委托并验收，未完成标「待补」，不得代写。
- 🔴 **CHECKPOINT · 蒸馏不裁决冲突**：新旧经验冲突时**先比适用条件**；前提不同即两条并存并各自标注，前提相同才停下问用户，不自行取舍。

### @步骤3: 按需触发（triage）

不是每轮都要写全部产物。自审时按下表判定，**跳过的必须写进自审第 ④ 行的原因码**——不写即视为漏做。

| 产物 | 写 | 跳过（原因码） |
|---|---|---|
| `project-progress.md` | 有可核实的改动 | `no-change`（纯问答、未动文件） |
| `decision-log.md` | 出现口径变更、取舍、被否方案 | `no-decision` |
| `debug-log.md` | 定位到根因 | `no-root-cause`（只有现象） |
| `experience/` | 同一做法有**第二条事实源**支撑 | `single-occurrence` / `covered-by:<条目>` |
| `docs/handoff/` | 换窗口、换 agent、上下文将满 | `same-session`（同一会话继续） |
| `README.md` | 入口 / 命令 / 能力边界发生结构性变化 | `no-surface-change`（**默认跳过**） |
| `CHANGELOG.md` | 发版时由 `changelog-manager` 归档 | `release-only`（**收尾流程一律不写**） |
| `archive/` | 任一产物超 `workflow-protocol.md` P10 阈值 | `no-threshold-hit`（未超阈值） |

**依据优先级**：项目 `AGENTS.md` 的收尾义务 > 本表 > 各 references 的默认动作。项目契约要求写而本表判跳过的，按项目契约写。

## 产物布局

| 产物 | 路径 | 写入者 |
|---|---|---|
| AI 协作契约（唯一契约源） | `<project>/AGENTS.md` | `vibe-init` 写契约区；`vibe-sync` 回填 Toolchain 与 Commands 表；`vibe-init` 迁出杂音（`relocate`） |
| 进度 / 决策 / 调试三份 | `<project>/docs/agents/` 下 `project-progress.md` · `decision-log.md` · `debug-log.md` | `vibe-init` 建模板，`vibe-sync` 维护（决策优先级高于 PRD） |
| 契约变更记录 / 初始化报告 | `docs/agents/agents-changelog.md` · `init-report.md` | `vibe-init` 独占 |
| 项目概览（可选） | `docs/agents/project-overview.md` | `vibe-init`；建则须含分层 / 依赖方向 / 禁跨层 / 例外四段 |
| 超阈值产物归档落点 | `docs/agents/archive/` | `vibe-sync` 首次归档时建；`handoff` / `audit` 各自目录另有 `archive/` |
| 可复用经验库，按领域分目录 | `docs/agents/experience/` | `vibe-init` 建空目录；内容与两份台账（`changelog.md` / `.distill-index.json`）由 `vibe-distill` 写 |
| 会话交接 / 审计报告 | `docs/handoff/handoff-YYYY-MM-DD[-slug].md` · `docs/agents/audit/audit-YYYY-MM-DD[-slug].md` | `vibe-handoff` · `vibe-audit`（目录缺失时首次执行建，含 `.gitkeep`） |
| 发布记录（不落独立文件） | `docs/agents/project-progress.md` 的一条 | `vibe-sync` 写；契约见 `references/release-checklist.md` |
| 仓库三件：变更日志 / 忽略规则 / 项目说明 | `<project>/CHANGELOG.md` · `.gitignore` · `README.md` | 唯一写者分别为 `changelog-manager` / `git-manager` / `shuxu`；`vibe-init` 只检测、委托与验收，`vibe-sync` 只按既有格式追加 CHANGELOG |

`vibe-init` 任何路径都不创建、不维护、不镜像 `CLAUDE.md`（见上「CHECKPOINT · AGENTS.md 唯一源」）。

## 何时读 references

- 要判定该读什么、该写哪里、算不算完成 → `references/workflow-protocol.md`（触发顺序 / 事实源 / 变更集 / 终止回复 / 原因码 / 归档阈值 / 分级）
- 要建 `AGENTS.md`、判定初始化状态（A–E）、执行 CLAUDE 迁移、补齐缺失文档 → `references/init-agents-md.md`
- 要执行 `AGENTS.md` 的生成规范本身（句式契约、黑名单、自检门） → `references/agents-md-generator.md`
- 要走 Git 检查与 Codegraph 集成 → `references/init-env-checks.md`
- 要运行任何终端命令前 → `references/command-policy.md`（白名单与各触发词允许的子集）
- 要落地过程文档与经验库 → `assets/docs/` 五份模板、`assets/experience/` 两份模板（原样复制，只换 `<工程标识>` / `<域标识>` 与 `updated`）
- 要沉淀进度、决策与调试记录 → `references/sync-progress.md`
- 要生成交接文档 → `references/handoff-context.md`
- 要蒸馏可复用经验 → `references/distill-experience.md`
- 要审查开发类项目（全项目 / 变更集 / 只看安全） → `references/audit-project.md` + `references/audit-checklist.md`
- 要发版前检查、定版本依据、记发布与回滚点 → `references/release-checklist.md`
- 要做只读档案体检 → `references/check-artifacts.md`
- 改过 description 要回归触发 → `references/trigger-test-set.md`

## 本文件写入闸

入口每次调用全量进上下文，新增内容前过三道闸：① **约束行为吗**——删掉这行，AI 执行下一个任务会不会做错？不会 → 归 `references/` 或 README；② **优先进 reference**——操作明细、清单、长流程下沉，本文件只留义务与指针；③ **行数 ≤185**——要加长就先压缩或下沉同等篇幅。判据复用 `agents-md-generator.md` §6b 的 N1–N6。

## 失败模式与兜底

| 触发条件 | 一线修复 | 仍失败兜底 |
|---|---|---|
| 前置文件缺失（如无 `docs/agents/` 却要 sync） | 回复缺失项，引导先跑 `vibe-init` | 用户坚持从零建立 → 转 `vibe-init`，不就地代建 |
| `vibe-init` 遇到已有文档 | 普通路径只补缺失项，已存在的文件一字不动；受控迁移（状态 C / D）按迁移契约执行 | 内容冲突且无法判定 → 停下请用户裁决 |
| CLAUDE 迁移与唯一源校验的五种失败 | 见 `references/init-agents-md.md` 的「失败处理」节 | 同上 |
| 同日已有同名交接文档 | 加语义后缀（`handoff-YYYY-MM-DD-<slug>.md`） | 后缀仍冲突 → 加两位序号（`-02`），不回头打扰用户 |
| `vibe-audit` 的四类失败（Skill 项目 / 类型不明 / 证据读不到 / 报告撞名） | 见 `references/audit-project.md` 的「失败处理」节 | 同上 |
| `vibe-check` / `vibe-release` 的失败（档案不可读 / 未初始化 / 前置不通过 / tag 冲突） | 分别见 `references/check-artifacts.md` 与 `references/release-checklist.md` 的「失败处理」节 | 同上 |
| 本次会话无可交接内容 | 明说「没有可交接的实质进展」，不生成空文档 | 用户坚持 → 只写有对话依据的条目，宁缺勿造 |
| 关键事实采集不到（项目定位、命令、权限边界） | 停下问用户，不猜、不编造 | 用户未答 → 写占位并在终止回复列为待确认项 |
| 白名单命令失败（`git init` / `codegraph init`） | 记「失败 + 原因」，继续后续步骤 | 仍失败 → 不自动重试，在报告建议里提示手动执行 |
| 同步时上下文已被压缩或记忆不可靠 | 先按客观源（git 核对 / 最新交接文档 / 过程文档）重建事实再落笔 | 无法重建 → 明说「本次进展无法核实」，不写条目、不凭记忆补全 |
| 本次会话无稳定增量 / 本轮无可蒸馏经验 / 原料区间已蒸馏过 | 明说「本次无可同步（或可蒸馏）的稳定增量」，不写文件、不编造 | 用户要求留痕 → 指向台账里已记录的那一轮，只蒸新增部分 |
| 新旧经验冲突 | 先比适用条件：前提不同则两条并存、各自标注 | 前提相同 → 停下问用户，不自行取舍 |
| 待写内容含密钥 / 凭据 / 隐私 | 脱敏为占位符后写入 | 无法安全脱敏 → 拒绝写入并说明原因 |
| 项目无 `CHANGELOG.md` 却要写更新日志 | 不创建文件；引导先跑 `vibe-init`（由它交 `changelog-manager +init` 建骨架） | 用户要求就地建 → 转 `changelog-manager`，本技能不代写 |
| 杂音命中但归宿文件不存在 | 按 `agents-md-generator.md` §6b 兜底：变更日志回落 `docs/agents/decision-log.md`，人读说明不写并列待确认项 | 仍说不清归属 → 列为待确认交用户裁决，**不得留在 `AGENTS.md` 里等以后再说** |
| 存量 AGENTS.md 反复积灰 | 增量维护时必扫全文，逐段过 §6b 六类，迁出后由产物自带反杂音义务行防复发 | 一次扫不干净 → 在终止回复列出未过项与保留理由，不宣称已清干净 |
| 委托技能不可用或未执行 | 标「待补」并写明缺什么，不代写 | 用户坚持 → 拒绝代写，说明归属 |
| 新忽略规则命中已追踪文件 | 列出 `git ls-files -ci --exclude-standard` 结果，不自动 untrack | 用户要求 untrack → 转 `git-manager` 并显式确认 |
| `shuxu` 动笔前 CHECKPOINT 未过 / 参考文件缺失 | 前者只交证据包并标「待补」；后者报告缺失路径并停止 | 硬做 → 拒绝，缺事实或规则不生成 |

## Gotchas

- `AGENTS.md` 是**规则契约**，不承载进度与待办（进度写 `docs/agents/project-progress.md`）；它是每会话自动注入的 system prompt，进来的每行都花上下文——「看着有用但删了也不会让 AI 做错」的段落就是杂音，判据是 §6b 的 N1–N6。
- `docs/agents/` 的**进度 / 决策 / 调试**三份只追加；决策冲突时把旧条目改标 `superseded`，不删除历史条目。它是**过程档案区**不是人类文档区，人类项目文档（README、设计稿）不放这里。
- `CLAUDE.md` 迁移完成后不得继续作为项目级协作契约存在，也不得靠新建空 `CLAUDE.md` / 指针文件解决兼容问题。
- 交接文档写给**另一个 agent**：能从 `git log`、diff、规格文档里读到的，写路径，不复述。过程文档的 frontmatter `updated` 必须随每次修改同步改当日；漏改等于让 `updated` 说谎。
- `vibe-init` 对半程项目**只补齐缺失文档**，绝不重写已有文件——哪怕内容看起来过时；受控迁移（CLAUDE → AGENTS）是唯一例外，且必须可追溯。不新增 `AGENTS.md` 章节：文档义务写进固定的 `Permissions` 与 `Conventions`，不另起段落。
- `docs/agents/experience/` 是**可移植产物**，不是项目过程档案：**正文可改写**（错的规则留着会持续误导），历史靠 `changelog.md` 保追溯；`docs/agents/` 其余三份则严格**只追加**。经验条目**五要素缺一不可**（主张 / 适用 / Why / How / 反例），写不出反例说明还没想清楚；主题名用领域名（`ui` / `frontend` / `motion` / …），不另造词——外送汇总时它就是分域依据。

## 反例黑名单（已知会犯错的写法）

| 不许做 | 为什么 | 正确做法 |
|---|---|---|
| 按目录列出的顺序取「最新」交接文档 | 字典序 ≠ 时间序：`handoff-2026-08-22-evening.md` 排在 `handoff-2026-08-22.md` **之前**（`-` < `.`）；旧写法 `handoff-20260802.md` 更会排在所有 `handoff-2026-*` **之后** | 解析文件名里的日期做比较；同日多份再比 frontmatter `updated` |
| 从 PRD / 计划 / 设计稿填 `Toolchain` 与 `Commands` | 那是意图不是事实，会把「建议」写成「已建立」 | 只取锁定文件、依赖清单、配置文件原文与实跑输出 |
| 用文件大小判断文件有没有内容 | 规则文件可能是符号链接，大小报 0 而内容非空 | 实际读取内容再判 |
| 把可能含 `##` 的模板放进无围栏的代码块 | 模板标题会变成文档自身的章节标题 | 模板一律用 4 个以上反引号围栏 |

## 非目标

- 不做任务拆解、排期、待办追踪；不把模糊需求转译成 PRD 或结构化指令。
- 不写代码、不重构、不运行构建与测试命令；Git 仅限白名单内的仓库检测、初始化与只读核对。
- 不代写 `README.md` / `CHANGELOG.md` / `.gitignore`：分别归 shuxu / changelog-manager / git-manager，本技能只检测、委托与验收。
- 不管理规格与变更的生命周期；不做对外发布，不代发内容；**发布只持契约与记录，不执行 commit / tag / push**。
- 不管理 Agent 自身的记忆：运行时记忆目录、跨项目共享的个人记忆库与外部知识库都不读写；也不把经验条目写入任何外部仓库或目录，外送由用户另行触发。本技能只服务**当前这一个项目**。
- 不提供「接管汇报」触发词（那是目标项目 `AGENTS.md` 的义务）；不评审 Skill 项目（归 skill-workshop）。
- 审计与体检不产出待办、排期与整改清单；只给问题 + 证据 + 方向（体检另给修复入口）。

## 验证

| 触发词 | 成功判定 |
|---|---|
| `vibe-init` | 状态判定（A–E）有可观测依据；`AGENTS.md` 六节成文且未新增章节，接管义务 / 常驻纪律 / 反杂音义务在 `Permissions`、杂音归宿表在 `Conventions`，`References` 每条为条件式指针；存量杂音已按 §6b 扫描并给出归宿；唯一源校验通过；`docs/agents/` 与 `docs/handoff/` 就位；三件仓库产物均有处置结论；**逐项判据见 `references/init-agents-md.md` 的「终止回复」节** |
| `vibe-sync` | `project-progress.md` 有新进展且 `updated` 已同步；有决策时 `decision-log.md` 已追加；调试定位到根因时 `debug-log.md` 已追加 `BUG-NNN`；`AGENTS.md` 仅事实区被回填，契约区未动；**`CHANGELOG.md` 不在收尾职责内**（用户明确要求时才写，归档交 `changelog-manager`） |
| `vibe-wrap` | 自审四行齐全（产物清单 / 依据 / 风险 / 跳过原因码）；该写的产物都已落盘且 `updated` 为当日；跳过的产物带原因码；全程停顿 ≤1 次且只在高风险动作上 |
| `vibe-handoff` | 交接文档落入 `docs/handoff/`，frontmatter 合规且 `updated` 为当日，正文只展开「别处读不到」的四类、其余写指针，未覆盖既有文件 |
| `vibe-distill` | 条目五要素齐全且各有事实源；编号在主题内递增；`changelog.md` 与 `.distill-index.json` **同轮各写一条**且区间一致；跳过项有原因码；冲突已标出而非自行取舍 |
| `vibe-audit` | 每条结论带 `路径:行` 或明写「证据不足」；报告落入 `docs/agents/audit/` 且 `updated` 为当日；未改动被审项目任何文件；Skill 项目已转交而非自审；变更集模式写明基线与未覆盖项；`mode=security` 首行写「静态检查，非安全认证」 |
| `vibe-check` | 逐项给出通过 / 问题 / 证据不足三态；每条问题带 `路径:行` 与修复入口（该跑哪个触发词）；**写入文件数 = 0**；不产待办 |
| `vibe-release` | 六步闸按需分段执行；前置不通过即停且逐条给证据；版本依据可追溯到 `[Unreleased]` 分类；回滚点四项齐全；**0 次写 CHANGELOG、0 次 commit、0 次 tag** |
