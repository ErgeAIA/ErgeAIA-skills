# skill-workshop · 审计方法论整合记录（2026-09-19）

> 分支：`compose/skill-workshop-audit-integration` · 版本：2.0.1 → **2.1.0**  
> 指令：`19092026_skill-workshop-审计方法论整合-本地AI执行指令.md`  
> 原则：单一审计主流程；判断框架并入；Rule Compression；无 `@` DSL。

## 1. 整合目标

将通用 Skill 审计方法论吸收为 skill-workshop 的**底层判断框架**，而非第二套并行流程。

## 2. 现有状态基线（P0 · 整合前）

| 指标 | 值 |
| --- | --- |
| 版本 | 2.0.1 |
| SKILL.md | 133 行 / 7957 bytes |
| 运行时 references | 4（core-method / creation / review / validation） |
| scripts（含 _impl） | 16 文件（CLI 入口 skill_cli.py） |
| agents / evals | 无（已归档） |
| archive 文件 | 75 |
| review.md | 110 行 |
| core-method.md | 101 行 |
| 审计阶段（对外） | L0 / L1 / L2 |
| 强制阶段 | 无默认 W1–W7 |
| 运行链 | 入口 → SKILL.md 路由 → references（按需）→ CLI validate/spec → 报告 |

## 3. 方法论 ↔ 现有流程映射

| 方法论要点 | 整合去向 |
| --- | --- |
| Core Task Definition | `core-method.md` + `review.md` 第 0 步 |
| 五问 / 六类问题 | `core-method.md` |
| Fast/Deep/Eval | 对外命名；≡ L0/L1/L2；`SKILL.md` / `review.md` |
| Evidence-First / 规则证据测试 | `core-method.md` + Deep 报告 |
| 生命周期 +EXPERIMENTAL | `core-method.md` |
| 删除优先 + HARD 防火墙 | `core-method.md`（并入原反膨胀四问） |
| P0/P1/P2 风险表 | `review.md`（替代归档百科 checklist 作默认） |
| N/A 机制 | `core-method.md` + `validation.md` |
| Runtime/Governance 分离 | `core-method.md` + `validation.md` HARD |
| W1–W7 | **不恢复对外门禁**；Deep 内叙述用决策阶段 |
| checklist 50+ | 不进运行时；归档保留 |

## 4. 删除 / 合并 / 条件化

- 不新增第二审计流程、不新增 CLI 子命令、不新增 `@` DSL。  
- 默认报告仍为 **Fast 六段短报告**；13 节完整结构仅用于 Deep 复杂重构附录或本类整合任务报告。  
- reconcile / family-diff / selfheal / eval：保持条件/归档，非默认阶段。  
- 强制优点条数、强制拆分：维持废除。

## 5. 新增 / 保留的核心机制

- Core Task 锚点；五问；六类问题；Evidence-First；规则证据测试；EXPERIMENTAL；删除阶梯与 HARD 防火墙；治理膨胀检查；Fast/Deep/Eval 分层与升级信号。

## 6. After 指标（P5）

| 指标 | Before | After |
| --- | --- | --- |
| SKILL.md 行数 | 133 | **137** |
| core-method.md 行数 | 101 | **201** |
| review.md 行数 | 110 | **160** |
| validation.md 行数 | 70 | **82** |
| 运行时 references | 4 | **4**（未增第 5 份；判断并入 core-method） |
| 默认强制阶段 | 无 W 全量 | 无（Fast 默认） |
| CLI 子命令 | 4 | **4** |
| @ DSL | 无 | **无** |
| 第二套审计流程 | 无 | **无** |
| spec / validate | — | **PASS / PASS**（exit 0；validate 含非阻断 advisory） |
| 版本 | 2.0.1 | 2.1.0 |

## 7. Audit 路径回归（P4 · dry-run 映射）

| Case | 目标技能（示例） | 预期路径 |
| --- | --- | --- |
| Audit-01 小而清晰 | qiao 等指令型 | Fast 结束，不升 Deep |
| Audit-02 复杂但单一 | huiyi / video-script（重构前） | 允许「复杂无需拆分」 |
| Audit-03 职责漂移 | description 跨任务混杂样本 | 给出 split/scope 判断 |
| Audit-04 多 ref 少运行 | 含大量 archive 引用的技能 | 不要求全量读完才 Fast |
| Audit-05 有 scripts | skill-workshop 自身 / zhile | CONDITIONAL 查脚本纪律 |
| Audit-06 无 scripts | 纯指令技能 | script checks = N/A |
| Audit-07 无 eval | 多数技能 | eval = N/A |
| Audit-08 重复规则 | 多文件同规样本 | 识别多重权威、建议合并 |
| Audit-09 模板/品牌污染 | 含固定语录技能 | 识别模板化污染 |
| Audit-10 可删不必增规 | 规则膨胀样本 | 结论：删除/合并即可 |
| Audit-11 规则多证据少 | 无失败依据硬规则集 | 降级 HEURISTIC/CONDITIONAL/ARCHIVED |
| Audit-12 显式 Deep | 用户点名深度 | Fast→Deep 升级正确 |

说明：上表为**方法论路径验收**，非逐技能重新出审计报告；详细单技能审计按需另开任务。

## 8. 自审五问（P3）

| 问 | 答 |
| --- | --- |
| 是否更清楚何时做什么？ | 是——路由表 Fast/Deep/Eval + 升级信号 |
| 是否更少固定规则、更多证据与任务定义？ | 是——Core Task + Evidence-First + 生命周期 |
| 简单 Skill 能否快速结束？ | 是——默认 Fast，短报告 |
| 复杂 Skill 能否自动升 Deep？ | 是——升级信号写入 review.md |
| 无真实证据时能否避免新增规则？ | 是——HARD 防火墙 + 删除优先 |

## 9. 机器校验

- `python scripts/skill_cli.py spec .` → **PASS**（exit 0）  
- `python scripts/skill_cli.py validate .` → **Skill is valid!**（exit 0；warnings 为 advisory，非 FAIL）  

## 10. Final Verdict

判断框架已并入单一审计主流程；CLI/ references 数量未扩；spec/validate PASS。分支待用户验证后决定是否合入 main / push。

## 11. Deferred

- 未对库内每个技能重跑完整 Deep 审计（非本指令范围）。  
- 未把归档 checklist 迁回运行时（防治理膨胀）。  
- 治理膨胀控制：SKILL.md 仅 +4 行；新增内容集中在 core-method/review（按需读取），不进默认 Fast 读取面。
