---
trigger-when: 需要理解 skill-workshop 审计判断框架、分级路由、证据预算或规则生命周期时
name: core-method
description: skill-workshop 底层审计判断框架：Core Task 锚点、五问、六类问题、Fast/Deep/Eval、规则生命周期、删除优先与 HARD 防火墙、Evidence-First。
---

# 核心方法（core-method）

## 第一性问题

用**最低审计成本**可靠发现会导致触发错误、执行错误、维护失控或上下文浪费的缺陷。

```text
低成本发现高风险问题 → 有证据的整改方向 → 必要时才深度诊断/评测
```

不是每次先跑完整检查清单，再组装标准化审计文书。

## Core Task Definition（审计锚点）

任何深度判断前，先用一句话锚定：

```text
当用户 ______ 时，Skill 负责 ______。
```

同步固定五项：

| 项 | 内容 |
| --- | --- |
| Input | 真正需要什么输入 |
| Output | 应该产出什么 |
| Non-Goals | 明确不负责什么 |
| Dependencies | 真正依靠哪些能力/文件 |
| Success condition | 什么算任务完成 |

后面所有规则、references、脚本与检查，都必须回到该定义判断。无法证明服务 Core Task 的规则 → 优先 CONDITIONAL / MIGRATE / DELETE，而不是默认保留。

无法写清 Core Task = **结构性风险**，不是用 checklist 兜底。

## 五问（判断框架）

1. 这个 Skill 到底解决什么用户任务？
2. 它真正需要什么输入？
3. 它应该产出什么？
4. 它真正依靠哪些能力？
5. 什么才算任务完成？

## 六类核心问题

| 类 | 含义 |
| --- | --- |
| 职责漂移 | 核心任务以外能力增多，description/流程失控 |
| 规则膨胀 | 一条原则被拆成多条表层规则 |
| 规则重复/冲突 | 多处权威、表述打架 |
| 模板化/机械化 | 固定句式/节拍/品牌语录替代判断 |
| 多重权威/引用漂移 | 同一事实多文件维护、死链 |
| 无证据规则 | 无真实失败依据的硬约束 |

## 任务路由

唯一路由表在 `SKILL.md`（agent 首先读的入口），本文件不复制。判断框架按本文件下文；Fast/Deep/Optimize 分工见 `SKILL.md` 摘要。

## 审查深度（风险驱动 + 证据预算）

| 层级 | 何时进入 | 读取预算 | 产出 |
| --- | --- | --- | --- |
| **Fast Review（L0）** | 默认 | 目录清单 + `SKILL.md` + 最多 1–3 份相关 reference；必要脚本入口 | **六段短报告** |
| **Deep Review（L1）** | 结构性问题 / 用户显式深度 / Fast 发现职责漂移等 | Inventory → 假设 → **定向读**；证据指示再扩展 | 短报告 + 证据化 findings |
| **Eval Review（L2）** | 高频/高风险/触发或质量有争议/明确 benchmark/重大重构后 | 按需启用工具链（多在 `docs/archive/`） | 实测结论；须标明是否用归档链 |

**Optimize 不在这张深度表里**：它与 Fast/Deep/Eval 不同类——那三级是「读多少、判多深」的审计成本分级，Optimize 是「动手改文件」的工作模式，复用 Deep 的判断纪律但读取预算与产出都不同（见 `optimization.md`）。

**禁止**：**审计**（Fast/Deep）默认全量预读目标技能的全部 `references/` 与 `scripts/`——该预算约束的是审计成本。
**OPTIMIZE 相反**：不改运行机制就改不动它，因此必须先全量读完、还原 Trigger→Input→Routing→Core Work→Tools→Output→Validation 的真实链路，再判断删什么、并什么、移什么。只读 `SKILL.md` 就动手重写属于 Optimize 的 P1 失效。

### Deep 内部决策阶段（叙述用，非强制门禁编号）

```text
Understand（Core Task）→ Inventory（资产地图）
→ Evidence（证据链）→ First-Principles（是否仍一个连贯任务）
→ Compression（删并条迁）→ Validation Design（针对高风险）
→ Final Review（判断型报告）
```

不恢复对外强制 W1–W7 全量流水线。

## 证据驱动扫描

1. 列目录与体量（主文档行数、references 数量、scripts 是否存在）。
2. 读 `SKILL.md` 与版本声明（`metadata.version` + `CHANGELOG.md`）。
3. 记录疑点，只打开能证实/证伪疑点的文件。
4. 每条 finding 落到**具体文件**（及章节/行）证据。

### Evidence-First（发现格式）

```text
Claim → Evidence（文件:位置）→ Impact → Recommendation → Confidence
```

`Confidence` 取 `CONFIRMED`（指得到文件与行为）/ `INFERRED`（机制推断）/ `UNKNOWN`；没有证据的猜测只能记作 Hypothesis，不得写成确定缺陷。

禁止「感觉冗余所以删除」类无证据结论。

### 规则证据测试（重要规则）

```text
Rule → 防什么真实失败？ → 是否真发生过？ → 严重度？
→ 是否已有规则覆盖？ → 有无更小替代？
```

据此标生命周期；**答不出真实失败 → 不得升为 HARD**。

## 规则生命周期

| 级别 | 含义 | 默认行为 |
| --- | --- | --- |
| **HARD** | 违反即失效或破坏契约；有重复真实失败证据、无更小替代 | 必须报告；阻塞「通过」 |
| **CONDITIONAL** | 仅某类 Skill/输入/结构适用 | 条件不成立 → **N/A**，不凑缺陷 |
| **HEURISTIC** | 经验建议 | 有证据才报；不升格 P0 |
| **EXPERIMENTAL** | 验证中，不作用于所有 Skill | 不进默认硬门槛 |
| **ARCHIVED** | 历史规则 | 不参与运行时；见 `docs/archive/` |

### HARD 示例（运行时）

- 非破坏：重构不得静默覆盖用户已有 skill 产物。
- 平台字段：frontmatter 必含 `name` + `description`；`name` 与目录一致、hyphen-case。
- 版本 SSOT：`metadata.version` + `CHANGELOG.md`。
- 主文档体量：原则 `<500` 行；工作室主文档目标约 120–150 行。
- 结构性引用路径必须真实存在。

### CONDITIONAL / N-A

| 条件 | 才检查；否则 |
| --- | --- |
| 有 `scripts/` | 查脚本纪律；无 → N/A |
| 高风险/用户要求评测 | Eval；否则 N/A |
| 指定 baseline/family | family 类诊断；否则 N/A |
| 编排共享字段 | 字段争用；否则 N/A |
| 有已知 recurring gotcha | 报 Gotchas；无强制造 Gotchas |
| 多权威冲突迹象 | reconcile 类诊断（归档工具）；否则不默认跑 |

## 删除优先与 HARD 防火墙

整改顺序：

```text
删除 > 合并 > 条件化 > 迁移 > 重写 > 最后才新增
```

**处置标记唯一真源**（review / optimization 只引用，不再各写一份）：
`KEEP`（保留）/ `MERGE`（并入他处）/ `MOVE`（迁移位置或文件）/ `CONDITIONALIZE`（加成立条件，条件不成立即 N/A）/ `REWRITE`（原处重写）/ `ARCHIVE`（移入 `docs/archive/`）/ `DELETE` / `ADD`（须写它解决哪个实际失败）。

新增 HARD 前必须能答：

1. 删除后会产生什么**真实**失败？
2. 是否重复发生？
3. 是否影响核心任务？
4. 是否存在更小替代方案？
5. 能否用 test/脚本而非 runtime 规则解决？

任一答不出 → 不升级为 HARD。

### 反膨胀（规则侧）

- 一类问题只保留**一个**最小有效原则（强原则优于多条表层规则）。
- 优先删：重复规则、README 运行规则、已无运行意义的历史兼容、无证据硬规则、固定模板语言、全局记忆已覆盖的信息、脚本已可靠保证的机械项。

## 结构性膨胀五类（Deep 必看）

1. **职责膨胀** — 核心任务外能力增多  
2. **规则膨胀** — 一原则拆成多表层条  
3. **文件膨胀** — references 增多但运行需求未增  
4. **模板膨胀** — 固定句式/流程/结构增多  
5. **治理膨胀** — 检查 Skill 的规则本身变复杂  

> skill-workshop **不得**被自己的治理体系拖垮。

Complexity ≠ 必须拆分。仍是一个连贯用户任务 → 允许「复杂但无需拆分」。仅当出现多个独立用户任务/触发逻辑/输入输出契约/生命周期/安全标准时，才形成 split candidate。

## Runtime vs Governance

| 层 | 只包含 |
| --- | --- |
| **Runtime**（被审计 Skill 自身） | 任务定义、必要流程、必要硬规则、条件 references |
| **Governance**（仅 workshop 审计时） | rubric、lifecycle、证据模型、架构模型、历史分析 |

**禁止**把治理规则注入被审计 Skill 的运行时文档。

## 机器闸门

- 创建/重构后：`python scripts/skill_cli.py validate <path>`
- 字段合规：`python scripts/skill_cli.py spec <path>`
- 打包：`python scripts/skill_cli.py package <path>`（默认 dry-run）
- 脚本 FAIL 不得写「已通过」。

## 与 archive 的关系

`docs/archive/` 保存旧 W 流水线、旧 checklist 脚本、评测 agents 等。仅条件诊断时查阅；不得默认写回运行时报告模板。reconcile / family-diff / selfheal 等**不**作为默认审计阶段。
