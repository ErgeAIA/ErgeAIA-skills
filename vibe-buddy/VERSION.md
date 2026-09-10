# vibe-buddy 版本记录

> 只记录版本号、核心变更与修改文件。设计取舍见 README，生成规范见 references。

---

## v1.0.0 (2026-09-10)

### 初始版本

**定位**：通用的项目 AI 协作记忆管理技能，读写项目根 `AGENTS.md`、`docs/.ai/` 与 `docs/handoff/`，不绑定任何 IDE 或运行时。

**五个触发词**

| 触发词 | 职责 | 产物 |
|---|---|---|
| `vibe-init` | 建立协作契约与过程文档；半程项目只补缺失项 | `AGENTS.md`、`CLAUDE.md`（可选）、`docs/.ai/` 三件套与层 C 变更日志、`docs/handoff/` |
| `vibe-sync` | 沉淀进度与决策 | `docs/.ai/project-progress.md`、`docs/.ai/decision-log.md` |
| `vibe-handoff` | 生成自包含交接文档 | `docs/handoff/handoff-YYYY-MM-DD.md` |
| `vibe-resume` | 只读并结构化汇报 | 无 |
| `vibe-distill` | 沉淀 bug 根因与预防规则 | `docs/.ai/debug-log.md` |

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

- 不覆盖（只追加 / 命名递增或加语义后缀）、不猜测（读不到写占位符）、不越界（只碰契约与过程文档区）、不静默（删除或改写留可见记录）。
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
