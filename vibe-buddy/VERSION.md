# vibe-buddy 版本记录

> 只记录版本号、核心变更与修改文件。设计取舍见 README，生成规范见 references。

---

## v1.0.0 (2026-09-10)

### 初始版本

**定位**：通用的项目 AI 协作记忆管理技能，读写项目根 `AGENTS.md`、`docs/.ai/` 与 `docs/handoff/`，不绑定任何 IDE 或运行时。

**四个触发词**

| 触发词 | 职责 | 产物 |
|---|---|---|
| `vibe-init` | 建立协作契约与过程文档；半程项目只补缺失项 | `AGENTS.md`、`CLAUDE.md`（可选）、`docs/.ai/` 三件套与层 C 变更日志、`docs/handoff/` |
| `vibe-sync` | 沉淀进度与决策 | `docs/.ai/project-progress.md`、`docs/.ai/decision-log.md` |
| `vibe-handoff` | 生成自包含交接文档 | `docs/handoff/handoff-YYYY-MM-DD[-slug].md` |
| `vibe-distill` | 沉淀 bug 根因与预防规则 | `docs/.ai/debug-log.md` |

接手（接管）**不是触发词**：由目标项目 `AGENTS.md` 的 `Permissions` 义务承担，每会话自动生效。

**过程文档模型**

- `docs/.ai/project-progress.md`：进度，每次会话更新；任务开始时先读它。
- `docs/.ai/decision-log.md`：开发决策（`DEC-NNN` 三位，优先级高于 PRD，冲突时旧条目标 `superseded`），**随开发持续更新**。
- `docs/.ai/debug-log.md`：bug 记录；编号 `BUG-NNN`（三位）递增，含现象/根因/修复/验证限制/教训。
- `docs/.ai/agents-changelog.md`：AGENTS.md 变更记录（一行一条 `旧值 → 处置 → 新值/去处/原因`），**只在 AGENTS.md 变更时写入**，每次变更必留一行。
- **保证层级（写义务时按此判断效力）**：A 层 = `AGENTS.md` 被运行时自动注入，每会话必读，**唯一能覆盖「AI 未调用本技能」这个前提的层**；B 层 = 本技能被调用时生效（自检门、终止回复）；C 层 = 文件被打开才读到（过程文档模板内的自述说明），**不构成保证**。据此，AGENTS.md 的 `Permissions` 写 `YOU MUST 改 AGENTS.md 前先读、改后追加 docs/.ai/agents-changelog.md` 与 `禁止不记录就改动 AGENTS.md 的约定`，`Conventions` 写「改 AGENTS.md 须留变更记录，无记录视为静默丢失」。`References` 只负责让文件被发现，不承担强制力。契约改动只走 `vibe-init`，其他触发词对 `AGENTS.md` 只读。
- `docs/handoff/`：交接文档，命名 `handoff-YYYY-MM-DD-*.md`。
- 模板外置在 `assets/docs/`（`project-progress.md` / `decision-log.md` / `debug-log.md` / `agents-changelog.md`），初始化时原样复制，只替换 `<工程标识>` 并把 `updated` 改为当日；§4b 不再内联骨架，消除模板与规范两处漂移。
- 所有过程文档带 YAML frontmatter（`title` / `type` / `project` / `updated` / `description`），**每次修改须把 `updated` 同步为当日**。
- 全部**只追加**，历史条目永不删除或改写。`decision-log.md` 与 `agents-changelog.md` 职责分离：前者随开发更新，后者只在改 AGENTS.md 时更新。

**初始化流程三新增（Git 检查 / 初始化报告 / Codegraph 集成）**

- **Git 检查**：`git rev-parse --is-inside-work-tree` 只读检测，无仓库则 `git init`；不做 `add` / `commit` / `push`。
- **初始化报告**：新增模板 `assets/docs/init-report.md` → `docs/.ai/init-report.md`，每次初始化追加一节，逐条记录实际操作（结果取值 完成 / 跳过 / 未执行 / 失败，禁止虚报），含可扩展的条目类型表与「建议」小节；不列入 `AGENTS.md` 的 `References`。
- **Codegraph 集成**：新增 `references/init-env-checks.md`。判定链为 `codegraph --version`（是否安装）→ `codegraph status`（本项目是否已建索引）→ 已装且无索引且有代码则 `codegraph init`；未安装时在报告「建议」写明用途、安装命令 `npx @colbymchenry/codegraph` 与初始化命令 `codegraph init`。不代做 `codegraph install` / `uninstall`（会改写各 agent 配置，含 `AGENTS.md` 标记区块）。
- **终端命令规则改为白名单制**：原「全程不运行终端命令」硬规则与新增功能冲突，改为只放开 5 条命令（3 条只读检测 + `git init` + `codegraph init`），其余仍禁止；命令失败不阻塞流程，记入报告继续。
- init 契约新增十步「执行顺序」表，明确 Git 检查在状态识别之前、报告在终止回复之前。
- **三新增功能的干跑修复**（空目录 / 已有仓库 / 未装 codegraph / 父仓库子目录 四环境）：
  - Git 检查区分「本项目即仓库根」与「位于父仓库内」，后者不建嵌套仓库，报告写实际根路径并记录 `git init` 的默认分支名
  - 索引检测限定**只认项目根下的 `.codegraph/`**：codegraph 会向上取最近索引，祖先目录的索引属父项目，不算本项目已有索引
  - 补「项目有代码」判据（复用生成规范 §2 的既有代码信号），否则跳过分支无法执行
  - 未安装建议补三类内容：`npx` 执行第三方安装器的风险提示、安装器会改写 `AGENTS.md`／`CLAUDE.md` 的留痕提醒、`.codegraph/` 加入 `.gitignore` 的忽略建议
  - 报告明确「只列本次实际涉及的步骤行」，避免每次生成一堆「未执行」噪音行；条目类型表降级为可选清单
  - `codegraph status` 降级为补充信息，退出码不参与判定；记录实际耗时

**真实试跑（指定目录实跑整条流程）修复**

在真实目录上真实执行了一次完整 init，暴露 5 处：

- **「既有契约」信号定义太窄**：原只列根目录 AGENTS.md / CLAUDE.md / .cursorrules，漏掉 **agent 目录内的规则文件**（实测有 `.claude/task-focus.md`、`.codex/redline.md`）→ 信号拆为「标准契约」与「非标准规则文件」两行，后者存在即判半程合成；模式判定表改为两列，语义唯一。
- **采集清单未提示隐藏项**：常见列目录工具默认不显示点目录，导致漏查 `.claude/`、`.codex/`、`.zcode/` → 清单显式点名这些目录，并写明「隐藏项必须逐个查，不能只看列目录工具的默认输出」；前置检查同步补一行。
- **决策保全来源不全**：原只写「既有契约文件」，未含 agent 目录规则文件与项目文档硬约束 → 补齐三类来源；并明确「已在别处维护的规则可 keep 原地保留 + 在 `AGENTS.md` 加指针，不搬进正文复述」。
- **「行数」无口径**：数组式行计数跳过空行（实测 69）与总行数（实测 82）差 13 行 → 定为**含空行的总行数**，且必须实测。
- **报告数字靠估算**：首版写「76 行」而实际 82，违反「禁止虚报」→ 报告规则加「所有数字（行数、条数、份数）必须实测读取，禁止估算」。

**vibe-sync 复核修复**

- **契约区与事实区划界（原为自相矛盾）**：sync 原写「不修改 `AGENTS.md`」，但初始化报告却建议「Toolchain 与 Commands 由 `vibe-sync` 回填」——两处打架。现明确：契约区（Permissions / Conventions / References / 章节结构）只由 `vibe-init` 写且须留痕；事实区（Toolchain 与 Commands 表数据）由 `vibe-sync` 回填、不必留痕。
- **不代改 PRD / ADR**：原规则要求决策冲突时「回写 PRD/ADR」，但两者都在本技能边界之外 → 改为「在终止回复提示用户回写，本技能只写 `decision-log.md`」。
- **补 `updated` 同步**：`AGENTS.md` 的 Conventions 要求「改 `docs/.ai` 须同步 `updated`」，sync 的执行规则却未落实 → 补入两处写入规则。
- **定死进展块语义**：原只写「更新顶部 `last_updated`」，但模板字段是「最后更新」，且「新增保留历史」与「单数字段名」语义冲突 → 定为：可变区（分支/阶段/代码/工具链/下一步/本阶段禁止）直接覆盖；进展为追加区，每次在旧「最后更新」之前新增一条，旧条保留。
- **补验证来源**：sync 不代跑命令 → 验证结果只取本次实际执行过的输出，由用户在会话中提供，禁止推测。
- **补决策编号取法**（读文件取最大编号加一）与「新条目置顶」。
- 术语修正：`last_updated` → frontmatter `updated` + 正文「最后更新」；路由表述去掉 sync 行的「bug 经验」（该归 `vibe-distill`）；`compatibility` 与「非目标」同步白名单口径。

**vibe-sync 补客观事实源与压缩降级**

- **原状态**：sync 完全依赖上下文记忆，`reads-from` 只有三个文档，全文不含 git；`git log` 也不在白名单里。会话压缩后按「记忆」写进度，会静默失真。
- **新增事实源与核对顺序**：写任何一条前按可信度取事实——① `git log` / `git status` / `git diff --stat`（仅 Git 仓库内）② `docs/handoff/` 最新交接文档 ③ 既有 `project-progress.md` 与 `decision-log.md` ④ 本次上下文（仅作补充）。上下文与 ①–③ 冲突时**以客观源为准**并把冲突记入备注；git 输出只用于核对，**不搬进文档**，需引用时写 commit hash。
- **新增「上下文被压缩过时」降级路径**：先重建再落笔；只写能核实的，覆盖不到的标 `待确认`；完全无法重建则明说「本次进展无法核实」，不写条目、不用「大概/可能」凑数；发现比本次会话更新的交接文档 → 停下问用户，不覆盖。
- **命令白名单抽为技能级单一真源**：新增 `references/command-policy.md`，按触发词声明允许子集；`vibe-sync` 新增只读的 `git status` / `git log --oneline -n N` / `git diff --stat`。`init-env-checks.md` 移除重复的白名单表，只留判定逻辑。

**vibe-sync 真跑（真实项目）修复**

在真实项目上执行了一次完整 sync（前置检查 → 事实源取材 → 增量判定），结果为「无可同步的稳定增量」——该项目自初始化后确实零改动。据此暴露并修复：

- **`git diff --stat` 被当成「改动规模」是错的（实跑复现）**：它**不显示未跟踪文件**。实测 `git status --short` 有 7 条 `??`，`git diff --stat` 却完全为空 → 改以 `git status --short` 为未提交改动的主力，`git diff --stat` 只覆盖**已跟踪**文件，并补一条判据「为空 ≠ 没有改动」。
- **未覆盖「已 `git init` 但零提交」这一状态**：这是 `vibe-init` 刚跑完项目的**标准状态**（init 不替用户提交），此时 git 只能给出「全部未跟踪」。原表述易被读成「没有进展」→ 补「零提交属正常状态，不因 git 无信息就判定无可同步」。
- **事实区回填未禁止从意图文档取材**：实跑项目的 PRD 写着「桌面壳（建议 Tauri 2）」属 P1 计划，照抄进 `Toolchain` 即把**建议**写成**已建立的事实**（P0 是 Web UI，桌面壳尚不存在）→ 显式加「禁止取自 PRD / 计划 / 设计稿；只接受锁定文件、依赖清单、配置文件原文、实跑输出」。
- **（方法论）规则文件可能是符号链接**：实测 `.claude/task-focus.md` 等 `Length = 0`，实为 symlink 指向集中管理的规则库，内容非空。若以文件大小判定「无内容」，会误判为无既有约定而**漏掉决策保全** → 采集清单加「不得以文件大小为 0 判定其无内容，必须实际读取再判」。

**handoff / resume / distill 复核修复**

逐条复核剩余三个触发词，与模板、命令白名单、`SKILL.md` 交叉核对后修复：

- **distill 条目格式与模板两套（硬伤）**：契约写 `### BUG-001 · 日期 · 标题` + 症状/根因/修复/**预防规则**，而 `assets/docs/debug-log.md` 模板与全部已落盘产物用 `## BUG-NNN: 标题` + 日期/现象/根因/修复/**验证限制**/教训——层级、标题格式、字段名三处不一致，契约还缺「验证限制」→ 契约对齐模板，不再另立一套。
- **handoff 要写「未提交改动」却没有 Git 事实源（硬伤）**：`reads-from` 只有三份文档，而内容要求里的「已完成」「未提交改动」正需要 Git 观测，原设计只能凭会话记忆填——与 `vibe-sync` 被点破的是同一类缺陷，而交接文档的全部价值恰恰在这里 → 新增事实源与取材顺序（Git → 上一份交接 → 过程文档 → 上下文），并把只读 Git 加进 `vibe-handoff` 白名单。
- **交接文档没有 frontmatter 规范**：其余五类过程文档都带 `title/type/project/updated/description`，唯独 handoff 无规定；但 `AGENTS.md` 的 Conventions 写着「改 handoff 须同步 `updated`」——**A 层义务指向一个不存在的字段** → 补 frontmatter（`title/type/project/date/updated/supersedes/description`）。
- **handoff「不重复已有产物」与「逐条写已完成」自相矛盾**：Git 与文档里已有的一律引用，而「未提交改动 / 下次待办 / 待确认项」恰恰无产物可引用 → 补判据「只展开尚未落入任何产物的那三类」。
- **resume 缺 `docs/.ai/` 前置检查**：只查了 `AGENTS.md` 与交接文档，`project-progress.md` 缺失时读取顺序 2–4 全落空却无提示 → 补检查项。
- **resume「最新一份交接文档」无判据**：同日多份 slug 时判不出来 → 定为「按文件名日期取最新；同日多份读全部并取 `updated` 最新者；仍不可判则列出全部问用户」。
- **resume 只读不写，却看不到工作区状态**：原「只读命令也不跑」使新会话无法知道上次改动提交了没 → 开放只读 Git（`status --short` / `log --oneline -n`），汇报结构增「Git 状态」；仍不写任何文件。
- **`compatibility` 与非目标的 Git 口径仍过时**：只写「Git 仓库检测与初始化」，漏了 `vibe-sync` 早已获得的只读核对 → 统一为「仅限白名单内的仓库检测、初始化与只读核对」。
- **handoff 前置检查与硬规则打架**：`docs/handoff/` 不存在时原写「先创建目录」，与「前置缺失即停、绝不代建」冲突 → 改为先引导 `vibe-init`，用户坚持才建空目录并说明。
- 杂项：`vibe-handoff` 验证行补「frontmatter 合规且 `updated` 为当日」；产物布局中交接命名补 `[-slug]`；「建议调用的技能」限定为只点名确实存在的技能。

**接管去触发词化与交接工作流重构（第一性重审）**

按要求对 handoff / resume 从第一性原理重审。三条结论推翻或修正了上一轮的方案：

- **`vibe-resume` 彻底删除，触发词 5 → 4**。接管的全部内容 = 读五样 + 对齐汇报 + 停下；这三步里读与停是纪律，产出只有「汇报」。上一轮想保留「只读模式」的三条理由经审查全不成立：① 用户主动想接管 → A 层义务已覆盖；② `AGENTS.md` 缺失时有通路 → 但 handoff 契约本身也要求 `AGENTS.md` 存在，那条通路并不存在；③ 零副作用 → 不构成必要性。**接管的正确落点是目标项目 `AGENTS.md` 的 `Permissions` 义务**——每会话自动生效，是唯一能覆盖「AI 未调用任何技能」这个前提的层。故 `vibe-init` 新增两条义务：会话开始先读 `docs/.ai/` 三件套与 `docs/handoff/` 最新一份、先复述现状与待确认项再动手。
- **删掉上一轮给 handoff 加的 `date` 与 `supersedes` 字段**。文件名已承载日期，再写 `date` 是同一事实两处存放；`supersedes` 更是把**我自己的旧设计当成了用户认可的事实**——与「层 C 照抄 lingjian」属同一类错误。frontmatter 现与其余五份过程文档完全同构，只有 `type` 不同。
- **交接文档从「七段结构」改为「只写别处读不到的」**。接手方能自己读 `AGENTS.md`、`docs/.ai/`、git 与代码，正文因此只展开四类无处可查的内容：验证状态、下一步聚焦点、卡点与失败路径、待用户拍板项；某类没有内容就整段省略，不写「无」。旧设计（`w3-handoff` 的十节结构）把新增文件表、修改文件表、错误清单、文件上下文清单一并抄入，属复述。
- **常驻协作纪律移入 `AGENTS.md`**（用户同意，视为早期设计可再调）：每次只推进一个阶段、完成即停等验证；不得自行宣称已修复、须由用户验证；修改既有文件用最小精确补丁、禁止整文件重写。它们每会话都要生效，写进交接文档等于在每份文档里重复一遍——来源是 `trae-dev-buddy` 的 `03-handoff-in.md` 那 7 条「后续协作规则」。
- **失败模式与测试集同步**：删掉「触发词歧义 → 反问」条（只剩写，歧义消失）；「同日同名交接文档」的后缀再冲突改为加两位序号，不回头打扰用户；新增「本次会话无可交接内容」。触发测试集把「接管项目 / 继续上次的活」由正面集移入负面集，并新增「接管类措辞不触发率」阈值——这类措辞若触发了本技能，说明强规则没被读到。

**干跑（三场景）修复**

对「全新空白项目 / 半程项目 / 已初始化优化」各干跑一遍，暴露并修复：

- 模板硬编码 `先读 PRD` → 空白项目无 PRD，产物会带一条指向不存在文件的强制指令；改为占位 `<项目文档，如 PRD.md>`，并规定占位文档不存在时整项删除。
- 层 B `project-overview.md` 号称可选却**无模板、无建立条件**，实际不可执行 → 明确为「无模板、按需自建」并给触发条件。
- `<工程标识>` 无来源定义（4 个模板都要用）→ 定义取法：用户指定 → 依赖清单 name → 项目根目录名。
- 全新初始化是否建 `agents-changelog.md` 前后矛盾（§3 说跳过、模板说要写兜底行）→ 统一为「总是建，写一行兜底」。
- 旧位置残留无规则（如项目根 `references/` 下的旧日志）→ 内容并入 `docs/.ai/`，旧文件按 `drop` 处理并留痕，禁止两处并存。
- 证据采集漏「运行时痕迹检测」（`.claude/` 等）却依赖它决定是否建 `CLAUDE.md` → 补入采集清单。
- 关键事实采不到时的兜底缺失 → 补「停下问用户；未答则写占位并列入待确认项」。
- `mode` 行变更未定义是否算一次契约改动 → 明确算改动，须留痕。
- 自检门只管 `References` 路径，不管 `Permissions` → 扩为两条路径全覆盖。

**状态识别（初始态 vs 开发中）**

- 旧判据「决策负载低/高」不可观测、无法判定，已废除。
- 改用三个可观测信号查表定模式：既有契约（AGENTS.md / CLAUDE.md / .cursorrules）、既有代码（源码目录 / 依赖清单 / 锁定文件 / 有提交）、既有项目文档（PRD / CONTEXT / 设计稿）。任一为「有」即排除全新初始化。
- 信号矛盾或无法查证 → 停下问用户，不自行归类。判据真源在生成规范 §2，init 契约只留动作列，避免两处漂移。

**AGENTS.md 契约强化**

- 章节固定不增删；产物头部写 `<!-- mode: 全新初始化|半程合成|已初始化优化 -->` 注明路由模式。
- 文档义务落在既有两节：`Permissions` 写 `YOU MUST 每次会话更新 docs/.ai/project-progress.md`；`Conventions` 写会话文档体系、bug 追加、交接命名、改文档须同步 `updated` 四条表格行。
- `References` 只写 `见 <path>` 纯指针，用途说明归 `Conventions`。
- 生成规范新增 §4b「项目文档结构生成」，承载目录结构与各文档骨架（单一真源）。
- 生成规范内的模板用 4 反引号围栏承载，避免嵌套代码块渲染异常。

**核心契约**

- 不覆盖（只追加 / 命名递增或加语义后缀）、不猜测（读不到写占位符）、不越界（只**写**契约与过程文档区，读可及项目内任意文件）、不静默（删除或改写留可见记录）。
- 先确认再执行；写入前声明操作类型 / 路径 / 是否覆盖 / 风险等级；一次只走一个触发词。
- 全程不运行终端命令；产物强制脱敏；不重复已有产物，一律用路径引用。

**设计取舍**

- 触发词从早期的 9 个收敛为 5 个：合并「保存进度 + 会话压缩」（写同一文件同一位置），「记录踩坑」并入调试经验沉淀，移除低频的「知识整合」与旧「初始化后同步」入口。
- 进度与决策不进 `AGENTS.md`：契约只承载规则，过程只承载事实。
- 完全移除 OpenSpec 及其兼容设计（规范源三模式、优先级链）。
- 移除状态文件与并行工作流目录：不再维护 `.workflow-state.json`；路由只保留 SKILL.md 一张决策矩阵表。
- `CLAUDE.md` 定位为指针而非副本。
- 交接机制继承 `handoff` 参考实现的四项契约：自包含、不重复已有产物、强制脱敏、含建议调用的技能段。

**修改文件**：全部新建 —— `SKILL.md`、`README.md`、`VERSION.md`、`references/init-agents-md.md`、`references/agents-md-generator.md`、`references/sync-progress.md`、`references/handoff-context.md`、`references/resume-context.md`、`references/distill-lessons.md`、`references/trigger-test-set.md`
