---
name: sync-progress
description: vibe-sync 的执行契约：把本次会话的稳定增量写进 docs/.ai/ 的进度、决策与调试记录，按需回填 AGENTS.md 事实，并在项目根已有 CHANGELOG.md 时追加用户可见变更日志。
trigger-when: 用户说「同步进度」「更新项目进度」「把踩的坑记下来」「更新日志」「vibe-sync」，或任务完成、决策变化、调试定位到根因之后
role: workflow
reads-from:
  - references/command-policy.md
  - <project>/AGENTS.md
  - <project>/docs/.ai/project-progress.md
  - <project>/docs/.ai/decision-log.md
  - <project>/docs/.ai/debug-log.md
  - <project>/CHANGELOG.md（若存在）
  - <project>/docs/handoff/ 中最新一份（若存在）
  - git status / git log / git diff --stat（仅本项目在 Git 仓库内时）
writes-to:
  - <project>/docs/.ai/project-progress.md
  - <project>/docs/.ai/decision-log.md
  - <project>/docs/.ai/debug-log.md
  - <project>/CHANGELOG.md（仅当已存在且本轮有用户可见变更时追加）
  - <project>/AGENTS.md（仅 Toolchain 与 Commands 两个事实表）
---

# sync · 沉淀进度、决策、调试与更新日志

## 目标

把本次会话里**已经稳定的事实**写进项目的过程档案，让下一次会话不必重读对话历史。这是 `AGENTS.md` 里 `Permissions` 与 `Conventions` 文档义务的执行者。

**只记录，不提炼。** 把「什么事反复成立」提炼成可复用规则，归 `vibe-distill`。

**更新日志与进度不是同一件事**：`project-progress.md` 记过程流水；`CHANGELOG.md` 只记**用户/协作者可见**的产品变更摘要（若文件已存在）。

## 前置检查

| 检查项 | 不通过时 |
|---|---|
| `<project>/AGENTS.md` 是否存在 | 不存在 → 回复缺失项，引导先跑 `vibe-init`，不代建 |
| `docs/.ai/` 下 `project-progress.md`、`decision-log.md` 与 `debug-log.md` 是否存在 | 缺哪个补哪个：回复缺失项并引导 `vibe-init`，不自行创建 |
| `AGENTS.md` 的 `Toolchain` / `Commands` 是否仍是占位 | 是 → 本次若已确知工具链或命令，按「事实区回填」写入 |

## 契约区与事实区（动 `AGENTS.md` 前先判）

| 区域 | 内容 | 谁写 |
|---|---|---|
| 契约区 | `Permissions` / `Conventions` / `References` / 章节结构 | 只有 `vibe-init`；改动须在 `docs/.ai/agents-changelog.md` 留一行 |
| 事实区 | `Toolchain` 与 `Commands` 两个表的行数据 | `vibe-sync` 可回填；属填事实，不属改约定，不必留痕 |

事实区回填规则：只增改表格行，不动表头与其他章节；内容必须来自实际观测——版本号取自锁定文件或实跑输出，命令取自配置文件原文，读不到就保留占位，禁止编造。

**禁止从意图文档取材**：PRD、计划、设计稿、路线图里写的技术选型是**计划**（且常属未来阶段），不是已建立的事实。只接受锁定文件、依赖清单、配置文件原文、实跑输出；意图文档里写的东西一律不填进 `Toolchain` / `Commands`。

## 事实源与核对顺序

写任何一条之前，先按可信度从高到低取事实，**不得只凭上下文记忆落笔**：

| 序 | 事实源 | 取什么 |
| -- | ------ | ------ |
| 1 | `git status --short`（未提交改动的主力）、`git log --oneline -n <N>`、`git diff --stat`（只覆盖**已跟踪**文件） | 改了什么、已有哪些提交；**仅本项目在 Git 仓库内时可用** |
| 2 | `docs/handoff/` 中最新一份交接文档 | 上一个会话交接的已完成项、卡点、待办 |
| 3 | `docs/.ai/project-progress.md` 与 `decision-log.md` | 已记录在案的进度与决策，同时用于去重 |
| 4 | 本次会话上下文 | 仅作补充 |

**写入范围与取材范围是两件事**：能**写**的只有 `docs/.ai/`、`AGENTS.md` 的事实区，以及已存在的项目根 `CHANGELOG.md`（追加）；能**取材**的是**整个仓库**（含只读命令输出）。

核对规则：

- 上下文与 1–3 项冲突时，**以客观源为准**，并把冲突写进 `project-progress.md` 的备注，不静默采信记忆
- **取材覆盖整个仓库**：本会话改动的源码、配置、文档都是进度素材，「只改了 `docs/.ai/` 之外的代码」这类进展必须记进去
- **不复述原始输出**：不粘贴整段 `git log` / `git status` / diff，提炼成「做了什么 + 路径或 commit hash」；需要细节时让读者自己去看 git
- **`git diff --stat` 空 ≠ 没有改动**：它**不显示未跟踪文件**。新项目里常见 `git status --short` 有几十条而 `git diff --stat` 全空，此时以 `git status --short` 为准
- **零提交是正常状态**：仓库已 `git init` 但尚无任何提交（`vibe-init` 不替用户提交）时，git 只能给出「全部未跟踪」，这只说明尚未提交，**不代表本次会话没有进展**；此时进度以文档与用户提供为准，不因 git 无信息就判定「无可同步」
- 项目不是 Git 仓库 → 跳过第 1 项，视为无此事实源，不报错
- **不顺手改任何写入范围之外的文件**：源码、配置、`.gitignore` 等一律只读（例外仅：已存在的项目根 `CHANGELOG.md` 可追加）；发现问题只报告，不动手

### 上下文被压缩过时

会话中途经过压缩、或用户告知上下文已被摘要时，按下列降级处理：

1. **先重建再落笔**：先走完上面 1–3 项，把能核实的事实拼出来，再动笔
2. **只写能核实的**：客观源覆盖不到的细节（尤其「为什么这么做」）标 `待确认`，不写具体内容，也不凭记忆补全
3. **记忆与客观源冲突** → 以客观源为准，冲突记入备注
4. **完全无法重建** → 明说「本次进展无法核实」，不写任何条目，不用「大概」「可能」这类措辞凑数
5. **发现更新的交接文档** → 若 `docs/handoff/` 中存在比本次会话更新的交接文档，说明可能有其他会话在工作，停下问用户，不覆盖

## 只收稳定增量

写入前先判定每条内容是**稳定事实**还是**临时进度**，临时进度不进过程档案。

| 类别 | 判定标准 | 落点 |
|---|---|---|
| 进度 | 任务状态变化、阶段推进、实际执行过的验证结果 | `docs/.ai/project-progress.md` |
| 决策 | 偏离 PRD 或重要技术选择 | `docs/.ai/decision-log.md` |
| 调试 | **反复调试才定位到根因**的问题与预防规则 | `docs/.ai/debug-log.md`（`BUG-NNN`） |
| 事实 | 工具链版本、安装/测试/lint/构建命令原文 | `AGENTS.md` 的 `Toolchain` / `Commands` 表 |
| 更新日志 | **用户/协作者可见**的功能、修复、破坏性变更、对外行为变化 | 项目根 `CHANGELOG.md`（**仅已存在时**追加） |

不属于以上各类的（正在做的细节、过程中的推测、被推翻的中间方案）一律不写。

`debug-log` 只收**已定位根因**的问题：还只有现象、根因仍在猜 → 不写，列入终止回复的待确认项。

**CHANGELOG 与 progress 分工**：同一件事可以既进 progress（过程）又进 CHANGELOG（对外摘要）；但**纯过程**（只改 `docs/.ai/`、纯内部重构且对外无感知）**不进** CHANGELOG。

## 写入规则 · `project-progress.md`

- **可变区直接覆盖**：`当前分支`、`阶段`、`代码`、`工具链`、`下一步`、`本阶段禁止` 覆盖为最新值。
- **进展为追加区**：每次在「当前状态」块内、上一条「最后更新」**之前**新增一条 `- **最后更新**：YYYY-MM-DD <一句话主题>`，其下用子条目逐条写改了什么、落在哪个路径、产出什么；旧条保留，不删不改。
- **同步 `updated`**：改完把 frontmatter 的 `updated` 改为当日。漏改等于让 `updated` 说谎。
- 验证结果只写**本次实际执行过**的命令与输出；未实际执行不得写「已通过」，也不凭推测填。本技能不代跑命令，验证输出由用户在会话中提供。
- 不删除、不改写任何既有条目；禁止重写整个文件。

## 写入规则 · `decision-log.md`

- 条目追加到 `DEC-NNN` 序列：读文件取最大编号加一，三位补齐。
- 新条目**置顶**（放在首个 `---` 分隔线之后、既有条目之前）。
- 与既有 active 决策冲突时，把旧条目标 `superseded`，**不删除历史条目**。
- **不代改 PRD 与 ADR**：决策与 PRD 冲突时，在终止回复中提示用户回写 PRD/ADR；本技能只写 `decision-log.md`。
- 改完同步 frontmatter 的 `updated`。

## 写入规则 · `debug-log.md`

- 格式与 `docs/.ai/debug-log.md` 模板一致：`## BUG-NNN: 标题` + 日期/现象/根因/修复/验证限制/教训。**不另立格式**。
- 编号 `BUG-NNN` 三位递增：读文件取最大编号加一。
- **只追加**，不改写既有条目；同一根因已存在则跳过，或补充新的表现。
- 不贴大段修复代码，需要时写文件路径与行号。
- 未实际运行的验证不写「已通过」，写「未运行」或「验证限制」。
- 改完同步 frontmatter 的 `updated`。
- 某条经验若能提炼成跨项目成立的规则 → 提示用户另跑 `vibe-distill`；本技能只记录，不提炼。

## 写入规则 · `CHANGELOG.md`（项目根，可选）

- **前置**：仅当 `<project>/CHANGELOG.md` **已存在**时追加。不存在 → **不创建**，终止回复写「无 CHANGELOG.md，本轮未写更新日志」，并提示用户自建或使用 changelog-manager；用户书面要求代建最小骨架时才可建，并注明非完整 Keep a Changelog 规范。
- **只收用户可见变更**：新功能、行为修复、破坏性变更、配置/接口对外变化、对使用者有影响的文档。内部过程文档、`docs/.ai/`、无行为变化的重构 **不写**。
- **格式跟随文件既有风格**：Keep a Changelog 的 `### Added / Fixed / Changed` 或该文件已用的自定义列表；**禁止**另起一套与文件内历史不一致的结构。
- **追加位置**：优先 `## [Unreleased]`（若存在）；无 Unreleased 则在最新版本节之后、历史节之前新增当日 `## [YYYY-MM-DD]` 或项目惯用小节；**永不改写**已发布历史版本节。
- **条目口吻**：面向使用者的一句话（做了什么 / 修了什么），可附路径或 issue 指针；不写内部工单式流水。
- **与 Git 对齐**：可引用本次相关 `commit` hash；未提交改动写「工作区（未提交）」，不编造版本号。
- **只追加**：不删除、不重排既有条目；同一变更已写过则跳过。
- CHANGELOG 有更新时，`project-progress.md` 仍必须写过程条目——二者不互相替代。

## 不写什么

- **不写 `docs/.ai/agents-changelog.md`**：那是 `AGENTS.md` 契约改动的记录，由 `vibe-init` 独占。
- **不回写 `docs/.ai/init-report.md`**：那是初始化执行留痕，不是待办清单；遗留的待确认项由用户或计划类技能跟进。
- **不动 `AGENTS.md` 契约区**：契约改动走 `vibe-init`。
- **不写 `docs/.ai/experience/`**：可复用经验的提炼归 `vibe-distill`；这里只记录流水事实。
- **不在无 `CHANGELOG.md` 时创建**（见上节）；也不把 CHANGELOG 写成进度流水。
- **不顺手改源码 / 配置 / `.gitignore`**（`CHANGELOG.md` 除外的根文件仍只读）。
- 同一事实已存在则跳过；只有值变化时更新。

## 与相邻触发词的分界

| 场景 | 用哪个 |
|---|---|
| 任务完成、决策变化、调试定位到根因，要沉淀事实 | 本文件 |
| 一轮开发告一段落，要把反复成立的做法提炼成可复用经验 | `references/distill-experience.md` |
| 上下文将满，要交给另一个 agent | `references/handoff-context.md` |

## 终止回复

只回复一行统计：写了哪些文件、各追加或更新几条、CHANGELOG 是否追加（或跳过原因）、事实区回填几条、去重跳过几条。

- 无增量时回复「本次无可同步的稳定增量」
- 走了「上下文被压缩」降级路径时，注明「已按客观源重建」与待确认条数
- 无 `CHANGELOG.md` 或无用户可见变更时，明确写「CHANGELOG：跳过（无文件 / 无可见变更）」
