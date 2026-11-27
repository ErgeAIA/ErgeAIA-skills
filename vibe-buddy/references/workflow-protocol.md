---
name: workflow-protocol
description: vibe-buddy 全部工作流的公共协议：触发与前置顺序、事实源优先级、变更集三要素、写入落点唯一性、高风险四类、终止回复格式、完成判据两栏、失败处理、原因码枚举、档案增长阈值。
trigger-when: 执行任一触发词前，或需要判定“该读什么、该写哪里、算不算完成”时
role: spec
consumed-by: references/init-agents-md.md、references/sync-progress.md、references/handoff-context.md、references/distill-experience.md、references/audit-project.md、references/command-policy.md
---

# 公共协议

各工作流只写专有段，公共段一律引本文件。**本文件不写具体动作**——只写顺序与形态，避免与专有段重复。

## P1 触发与前置顺序

固定四步，不得跳序：

1. **判目标类型**（仅需要时）：Skill 项目 → 转交 skill-workshop；开发类项目 → 继续；判不出 → 停下问用户。
2. **判前置文件**：缺 `AGENTS.md` 或 `docs/agents/` → 引导先跑 `vibe-init`，**不代建**。
3. **自审**：按分级（见 P11）输出产物清单、依据、风险、跳过原因码。
4. **执行**：无高风险 → 连续执行到完；有高风险 → 只针对那一件事停一次。

「停」= 只输出文字、不碰任何文件。

## P2 事实源优先级

从高到低，**不得只凭会话记忆落笔**：git 客观源（白名单只读命令）> `docs/handoff/` 最新一份 > `docs/agents/` 各过程文档 > 本次会话上下文。非 Git 仓库跳过第一项、不报错；上下文与前三项冲突时**以客观源为准**并把冲突记入备注。

**取材范围 ≠ 写入范围**：可取材整个仓库；可写的只有本技能产物落点（见 P3）。

## P3 写入落点唯一性

一个产物只有一个写者；其余角色只报告缺口，不代写。

| 产物 | 唯一写者 |
|---|---|
| `AGENTS.md` 契约区 / 事实区 | `vibe-init` / `vibe-sync` |
| `project-progress.md` · `decision-log.md` · `debug-log.md` | `vibe-sync` |
| `agents-changelog.md` · `init-report.md` | `vibe-init` |
| `experience/`（含双台账） | `vibe-distill` |
| `docs/handoff/` · `docs/agents/audit/` | `vibe-handoff` · `vibe-audit` |
| `CHANGELOG.md` | `changelog-manager` 建与归档；`vibe-sync` 只按既有格式追加 |
| `README.md` · `.gitignore` | `shuxu` · `git-manager` |

## P4 高风险四类

只有这四类必须拿到用户点头，其余动作不按触发词逐个确认：

1. 覆盖既有文件；2. 删除源文件；3. `CLAUDE.md` 迁移；4. 白名单外写入。

## P5 变更集三要素

凡说“本次改动”，必须三要素齐全，否则范围由用户指定：

| 要素 | 取值 |
|---|---|
| 基线 | 工作区未提交 / `<base>..HEAD` 区间 / 用户指定的文件清单 |
| 范围 | 全部路径，或指定目录/文件 |
| 上限 | ≤30 个文件 · 单文件 diff ≤400 行 · 总量 ≤80KB；超限只取增删最多的前 N 个，并在产物里写“未覆盖哪些” |

## P6 终止回复与完成判据

终止回复 ≤3 行 + 待确认项，**不复述产物正文**：① 落盘路径（或未写入原因）；② 统计（写了几个文件 / 各几条 / 跳过几个及原因码）；③ 待确认项（无则写「无」）。

判定分两栏，不得混写：

- **可判定项**：存在性、frontmatter `updated` 为当日、编号连续、台账区间一致、行数上限、`References` 每条为条件式指针。
- **人工项**：语义质量、冲突是否真冲突、证据是否足够、方向是否合理。

漏判的可判定项必须显式写 `skipped:<原因码>`，否则视为未完成。

## P7 委托契约

交相邻技能时给证据包，不让下游重新调研：① 写前声明（操作类型 / 目标路径 / 交给谁 / 是否可能覆盖）；② 证据包字段按产物固定（见 `init-agents-md.md` 委托表）；③ 对方未完成 → 标「待补」并写明卡在哪一步，**不算完成**；④ 完成后实读复验。

## P8 失败处理

- 单步失败**不中断**后续步骤；记「失败 + 原因」后继续。
- 先判是否属正常状态（零提交仓库 `git log` 返回 128、`git diff --stat` 为空均属正常）。
- 无法降级 → 明说「未完成」并列出未过项，**禁止宣称完成**。

## P9 原因码枚举

取值必须来自本表，禁止临时造词；`<条目>` 填编号不填描述。

`no-change` · `no-decision` · `no-root-cause` · `no-rule` · `single-occurrence` · `no-fact-source` · `project-param` · `covered-by:<条目>` · `same-session` · `release-only` · `no-surface-change` · `no-threshold-hit` · `evidence-insufficient` · `out-of-scope`

## P10 档案增长阈值

活跃产物超阈值时**先归档再写新条目**；归档只追加、不改写；归档前后**总条目数守恒**。

| 产物 | 活跃上限 | 归档落点 | 粒度 |
|---|---|---|---|
| `project-progress.md` | ≤300 行 | `docs/agents/archive/progress-YYYY-MM.md` | 月 |
| `decision-log.md` | ≤200 条 | `archive/decision-YYYY.md` | 年 |
| `debug-log.md` | ≤100 条 | `archive/debug-YYYY.md` | 年 |
| `agents-changelog.md` | ≤200 行 | `archive/agents-changelog-YYYY.md` | 年 |
| `init-report.md` | 最近 3 节 | `archive/init-report-YYYY.md` | 年 |
| `experience/changelog.md` | ≤300 行 | `archive/experience-changelog-YYYY.md` | 年 |
| `docs/handoff/` | ≤30 份 | `archive/handoff-YYYY-QN/` | 季 |
| `docs/agents/audit/` | ≤20 份 | `archive/audit-YYYY/` | 年 |

三条纪律：

1. **先写归档、验证成功、再移出活跃**；中途失败不删原文。
2. **编号全局唯一**：`DEC-NNN` / `BUG-NNN` 取「活跃 + 归档」的最大值加一，不能只看活跃文件。
3. **归档不改判据**：`docs/handoff/` 归档后仍按文件名日期取最新一份，`archive/` 不参与候选。

## P11 任务分级

| 档 | 判定（任一命中即升档） | 自审 | 停顿 | 阶段产物 |
|---|---|---|---|---|
| T1 | 单产物；只读或纯追加；不触高风险；不委托 | ≤2 行 | 0 | 不需要 |
| T2 | 2–3 产物串行；或 1 次委托；不触高风险 | ≤4 行 | 0 | 可选 |
| T3 | 触高风险四类；或跨契约；或 ≥4 产物；或需并行/多技能 | ≤6 行 | 高风险那件事 1 次 | 必须每阶段一个可验证产物 |

判定只认四项输入：产物数、是否触高风险、是否需外部技能、是否跨会话。**不引入 token 估算或文件数启发式。**
