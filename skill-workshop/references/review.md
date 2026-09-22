---
trigger-when: 评审/审计/「帮我看看这个 skill」、Deep Review、或需要 T/E/C 与 Fast/Deep/Eval 判据时
name: review
description: Fast/Deep/Eval 评审分层；Core Task 锚点；T/E/C 三轴；Evidence-First；P0/P1/P2 风险表；短报告与 Deep 扩展字段。
---

# 评审标准（review）

判断框架（五问/六类/生命周期/删除优先）见 `core-method.md`；本文件规定**怎么做评审、怎么写报告**。

## 三级评审（风险驱动）

| 级别 | 何时 | 平均读取 | 报告 |
| --- | --- | --- | --- |
| **Fast Review（L0）** | 默认「帮我看看」 | SKILL + 1–3 refs | **六段短报告** |
| **Deep Review（L1）** | Fast 发现结构问题；用户要第一性/深度；明显膨胀或职责混杂 | 定向扩展 | 短报告 + 证据化 findings |
| **Eval Review（L2）** | 高频/高风险/触发或质量争议/benchmark/重大重构后 | 按工具链 | 实测结论 |

**Optimize 不是第四个深度**，而是与之并列的工作模式：它复用 Deep 的判断纪律，但要求全量读取、给出目标架构、真正改文件并做能力回归——见 `optimization.md`。用户说「优化 / 重构 / 改好 / 审查后帮我改」时直接切过去，不要停留在本文件的报告产出上。

### Fast → Deep 升级信号（任一）

- Core Task 无法写清或与 description/流程明显错位  
- 职责漂移 / 多个不相关用户任务  
- 多重权威、跨文件规则冲突  
- references/规则数量与运行需求明显不符（膨胀）  
- 输出质量或触发争议、高频维护技能  
- 用户显式要求深度/第一性审查  

### Eval Review 触发（任一）

- 高频或高风险 Skill  
- 触发率或核心质量有争议  
- 明确要求 benchmark / 回归  
- 完成重大结构重构后需实测  

## 第 0 步：Core Task Definition

任何级别先锚定（Deep 时写入报告）：

```text
当用户 ______ 时，Skill 负责 ______。
Input / Output / Non-Goals / Dependencies / Success condition
```

## 三轴（一级质量模型）

| 轴 | 问题 | 主要看什么 |
| --- | --- | --- |
| **T — Trigger** | 触发正确吗？ | description 语义、触发词、Not for、误触发风险 |
| **E — Execution** | 执行正确吗？ | 步骤可执行、输入输出契约、失败路径、HARD 护栏、脚本纪律（若有） |
| **C — Context** | 上下文成本合理吗？ | 主文档体量、是否堆砌、references 按需、无死链 |

高风险 Skill 另加 **Safety/Contract**（写盘/发布/覆盖类能力时）。

## Fast Review 清单（默认）

1. Frontmatter：`name`/`description`/版本 SSOT、字段是否越权。  
2. Description：做什么、何时触发、边界。  
3. Core Task 能否一句话说清（说不清 → 结构性风险，升 Deep 候选）。  
4. 主职责是否一个连贯用户任务单元。  
5. 主文档体量与是否只做路由/硬边界。  
6. references：存在性、是否声明加载时机、明显死链。  
7. 已打开文件之间有无明显冲突。  
8. 输出契约是否写清。  
9. 明显职责漂移 / 模板化污染信号。  

产出**六段短报告**；不强制优点条数；不写固定收尾套话。

## Deep Review（条件展开）

在 Fast 之上按疑点扩展：

- Core Task 五问完整化；六类问题对照。  
- Evidence-First：`Claim → Evidence → Impact → Recommendation`（文件:位置）。  
- 规则证据测试与生命周期标注（HARD/CONDITIONAL/HEURISTIC/EXPERIMENTAL/ARCHIVED）。  
- 结构性膨胀五类（含治理膨胀）。  
- First-Principles：是否仍一个连贯任务；无独立任务 → `Split: Not recommended`。  
- CONDITIONAL / N-A（无 scripts/eval/家族/编排 → 不写缺陷）。  
- 安全与非破坏（若目标会改文件）。  
- 方向性争议才用钢人；格式/触发问题不升级仪式。  

**禁止**：审计（Fast/Deep）在进入问题扫描前强制读完目标全部 references/scripts——那是 OPTIMIZE 的前置动作（`optimization.md` §2）。

## Eval Review（条件）

仅当触发条件满足；工具多在 `docs/archive/`。报告须写明是否使用归档工具链。

## 风险分级（报告问题用）

| 级 | 含义 | 示例 |
| --- | --- | --- |
| **P0 Core Failure** | **核心任务失效**：用户拿到结果就是错的或拿不到结果 | 根本无法触发、核心输出错误、关键引用断裂、核心安全契约失效、职责严重冲突 |
| **P1 Structural Risk** | 明显影响质量、可维护性或上下文成本 | 职责漂移、多重权威、重复规则、无证据硬规则、上下文膨胀、过度模板化 |
| **P2 Maintenance** | 文档级与小型维护问题 | README 小幅不同步、历史残留、命名、文档重复 |

定级看**对核心任务的影响**，不看显眼程度：「标题不够漂亮」「描述略长」「README 差一行」不得挤占核心优化的注意力与报告位置。

### Description 与触发质量怎么定级

结构不合规（缺字段、非单行、超 1024、YAML 转义风险、未完成占位符）→ CLI 硬 FAIL。
语义问题（看不出干什么、只有裸词表、无边界易误触发、写的是内部机制）→ 由评审判断，一般 P1；**完全无法被真实用户话术触发**才算 P0。
禁止把「触发词数量少」当缺陷——数量不是判据，路由结果才是（见 `optimization.md` §11）。

默认 **P2 不阻塞**核心结论。

### 规则级别在报告中的表现

| 生命周期 | 报告 |
| --- | --- |
| HARD 失败 | P0/P1；阻塞「通过」 |
| CONDITIONAL 且条件成立 | 按影响定级 |
| CONDITIONAL 条件不成立 | **N/A**，不进问题清单 |
| HEURISTIC | 建议区，不与 HARD 混排 |
| EXPERIMENTAL / ARCHIVED | 不作为默认硬门槛 |

### 职责内聚

- 合理：围绕一个连贯用户任务的多步骤闭环。  
- 不合理：互不相关能力塞进同一 description。  
- 无职责耦合 → **无需拆分**（复杂但单一任务是正常结果）。

### 明确废除

- 强制 3–5 条优点 → 0–N 条有证据的可保留设计。  
- 强制拆分候选 → 查职责耦合，无则「无需拆分」。  
- 固定收尾套话与 W1–W7 默认全量流水线。  
- 默认全量预读；默认跑 reconcile/family-diff/selfheal/eval。

## 默认报告结构

### Fast（六段）

1. **一句话结论**  
2. **第一性判断**（Deep 或方向存疑时）  
3. **值得保留的设计**（0–N，无则省略整节）  
4. **问题清单**（P0/P1/P2 + 证据位置 + HARD/CONDITIONAL/HEURISTIC）  
5. **最值得做的动作**（≤3）  
6. **是否值得继续重构**（是/否 + 一句理由）  

### Deep 扩展字段（复杂重构 / 用户要处置表时附）

```text
Core Task Definition
Current Architecture / Runtime Flow
Major Findings（Evidence-First）
Rule Disposition（标记真源见 core-method.md §删除优先）
File-by-File Disposition
Target Architecture
Optimization Plan
Validation & Regression
Remaining Risks / Deferred Items
Final Verdict
```

不要求每次 Deep 都写满 13 节；**判断型问题清单优先于检查计数**（回答：真正要做什么、为何变复杂、哪些规则必要/历史负担/应删/应条件化/应迁移、优化后为何更简单、有无证据表明核心能力未丢）。

完整集成审计报告（workshop 自身方法论整合等）另按任务指令的 13 节结构输出。

## 论证质量（Deep）

- 第一性锚定从本质矛盾推导，不写空洞「必须/绝不」填空。  
- 钢人仅用于方向性架构争议；反方须最强；结论带条件。  
- 无产物的步骤 = 未执行；结论必须出现在报告中。

## 评审者边界

- 裁判不下场：评审默认只出报告与整改方向，不直接改用户文件。  
- 构建/重构走授权写路径 + `spec`/`validate`；破坏性写入须 plan-gate。  
- 指出违背的原则与整改方向，不把整份修复稿塞进评审报告（除非用户明确要求并授权写文件）。
