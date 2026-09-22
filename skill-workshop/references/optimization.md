---
trigger-when: 用户要优化 / 重构 / 改进一个 Skill，或要求在审计之后真正改文件时
name: optimization
description: Optimize 模式权威方法论：全量读取运行时资产、还原运行机制、证据化诊断、目标架构、资产处置、实际重写、机器验证与能力回归。
---

# 优化方法（optimization）

判断框架（Core Task 锚点 + 五项、六类问题、规则生命周期、删除优先与处置标记、证据格式）在 `core-method.md`，本文件**只规定如何把诊断转化为真实优化**，不复制判据。

## 0. Audit ≠ Optimize

| 维度 | AUDIT（Fast/Deep） | OPTIMIZE（本文件） |
| --- | --- | --- |
| 目的 | 判断有没有问题 | 让核心任务完成得更可靠、更省上下文 |
| 读取面 | 成本优先：SKILL + 1–3 份相关文件 | **全量**运行时资产（见 §2） |
| 产出 | 报告 + 整改方向 | 实际改动后的文件 + Before/After + 回归结论 |
| 写文件 | 否（裁判不下场） | 是（构建路径，非破坏、可回溯） |
| 结束判据 | 报告交付 | 目标架构落地 **且** 核心能力未丢 **且** `validate`/`spec` 通过 |

只出报告不动手 = Audit；用户说「优化 / 重构 / 改好 / 审查后帮我改 / 它为什么不好用」即进入本模式，**不再走 Fast**。用户已给完整重构指令时按指令执行并套用本模式闸门。

## 1. 核心原则

> **优化不是「增加更多规则」，而是「用更小的规则系统，让原来的任务完成得更好」。**

- 任何新增（规则、文件、章节、脚本、checklist、示例）必须写明它解决**哪个实际失败**。「为了完整 / 更专业 / 更规范 / 以后可能用不到但保险」都不构成理由。
- 不以新增内容多少衡量优化成果。`300 行 → 180 行` 不一定更好，`180 → 220` 也可能更好；只看 Core Task、Trigger、Execution、Output、Safety、Context 六项是否改善。
- 不摊派资产：无脚本可以很优秀；无 eval/Gotchas/FAQ 不是缺陷。
- 删除优先顺序见 `core-method.md` §删除优先与 HARD 防火墙。

## 2. 八步流程（固定顺序，不是新增流水线编号）

```text
1 Understand → 2 Inventory → 3 Model → 4 Diagnose
→ 5 Decide → 6 Rewrite → 7 Validate → 8 Regression
```

| 步 | 动作 | 产物 |
| --- | --- | --- |
| Understand | 回答：服务谁 / 何时调用 / 给什么 / 做什么 / 得到什么 | Core Task 锚点 + 五项（`core-method.md` §Core Task Definition） |
| Inventory | 全量读运行时资产并列体量 | 资产地图 + 每项处置候选（§5） |
| Model | 还原真实运行机制（§3） | Runtime Flow |
| Diagnose | 只找影响用户结果的问题（§4） | Evidence-First findings |
| Decide | 定目标架构与处置表（§6、§7） | Target Architecture + Disposition |
| Rewrite | 按处置表实际改文件（§8） | 改动后的技能 |
| Validate | 跑 `validate` + `spec`；新增判据须有测试 | 机器结果原样输出 |
| Regression | 证明核心能力未丢（§9） | Before/After + 回归结论 |

**禁止**：Core Task 写不清就开始「优化措辞」——先解决任务模型。

## 3. Model：优化对象是运行机制，不是 Markdown

```text
Trigger → Input → Decision/Routing → Core Work → Tools(References/Scripts/Templates) → Output → Validation
```

复杂技能再补三条：Failure Path（失败怎么表现）、Safety Boundary（写盘/发布/覆盖）、State/Persistence。

按机制归因，不按文件顺序总结。真正的问题常藏在脚本实现、模板、输出契约、或「同一条规则在三个文件里各写一遍」。

## 4. Diagnose：只报影响结果的证据

- 问题必须归入 `core-method.md` 的六类；每条 finding 用 `core-method.md` §Evidence-First 的五元组（含 `Confidence` 三态 `CONFIRMED / INFERRED / UNKNOWN`），本文件不另立格式。
- 无证据不得写成确定缺陷，只能记 **Hypothesis**。
- 禁止产出「标题是否更漂亮 / 这段是否更专业 / 要不要加一节 / 要不要加 checklist / 要不要加例子」类风格 finding，除非能连到触发、执行、输出、安全、维护或上下文成本的实际影响。

## 5. 规则膨胀与 HARD 的正确判据

判膨胀不看条数，看**这些规则是否在同一种失败上各说一遍**：是 → 合并为一个原则；只有当任务、失败、条件、处理四者不同时才保留多条。

新增 HARD 前必须答七问（前 5 问见 `core-method.md`，此处补后 2 问）：防什么失败 / 真发生过吗 / 频率 / 后果 / 现有规则为何不够 / **有没有更小替代** / **能否用脚本、validate 或测试替代 runtime 条文**。答不出 → 不得新增 HARD。

## 6. Decide：先目标架构，后逐文件处置

必须给 Current → Problems → **Target Architecture**，且目标架构要**比现状更简单或更有解释力**，否则不算优化完成。

```text
当前：SKILL ─ 8 类规则 + 5 份重复 reference + 2 个冲突输出定义
目标：SKILL ─ Core Task + Workflow + Output Contract + 2 份按需 references
```

每一项文件/规则给处置（标记唯一真源见 `core-method.md` §删除优先与 HARD 防火墙：`KEEP / MERGE / MOVE / CONDITIONALIZE / REWRITE / ARCHIVE / DELETE / ADD`），每项写 **why + evidence + user impact**（`ADD` 还须写它解决的实际失败）。禁止「凭感觉重写」。

**拆分**：只有「独立用户意图 + 独立触发逻辑 + 独立 Input/Output + 独立生命周期」四者同时成立才产生 split candidate；一个任务的多个步骤不是拆分理由，此时结论写「复杂，但无需拆分」。

## 7. 钢人只用在结构决策上

需要：架构方向争议、职责拆分、规则删除、规则是否升 HARD、运行时与治理边界、重大输出契约变化。

不需要（直接改，别仪式化）：死链、错路径、frontmatter 缺字段、拼写、未使用的旧文件、明显重复。

需要时按双向写：`方案A vs 方案B → 支持A最强 / 反对A最强 / 支持B最强 / 反对B最强 → 最终判断 + 成立条件`；判断只能来自 Core Task、证据、风险、维护成本、用户影响，不得来自偏好。

## 8. Rewrite 纪律

- 按处置表逐条落文件；改动可回溯到某条 finding 或某项处置。
- 非破坏：不覆盖用户未授权文件；迁移用 `git mv` 等价手段保历史；不碰运行态目录。
- 不改测试或断言来「让验证变绿」；规则变了要同步改对应测试与文档。
- 治理规则不得写进被优化技能的运行时文档（`core-method.md` §Runtime vs Governance）。

## 9. Regression：优化后必须证明没丢能力

1. 逐项对照 Core Task、触发场景、输出契约、安全边界，确认原核心能力仍然存在。
2. 至少一条真实正例 + 一条真实负例走一遍改后流程（跑该技能自己的命令或按其契约手工推演），记录输出。
3. `python scripts/skill_cli.py validate <path>` 与 `spec <path>` 原样贴结果；FAIL 或没跑 → 不得写「已验证」。
4. 被删除或合并的规则，说明失败为什么不会重新出现（更小替代是什么）。

## 10. Description 语义评审（替代词法统计）

结构合规由 `validate` 保证（存在、非空、单行 string、长度、YAML 转义、无未完成占位符；`spec` 只对官方字段契约负责，见 `validation.md`）。**质量与触发命中属语义判断**，按 `Trigger + Job + Boundary` 模型逐项回答：

```text
1 第一次读到它，能否知道这个 Skill 是干什么的？
2 用户什么时候会想到调用它？
3 说的是真实用户任务，还是内部机制？
4 有没有不必要的实现细节（路径、版本号、内部步骤名）？
5 有没有为了命中而堆的同义词与裸词表？
6 有没有容易误触发的泛化描述（「分析 / 处理 / 帮助」这类无边界大词）？
7 有没有明显漏掉的真实触发场景？
8 是否需要一个 Not for 边界来和相邻 Skill 分工？
9 是否与 Core Task 一致？
10 改后是否更短、更清楚，还是只是更长？
```

模型：`[什么时候用] + [解决什么问题] + [必要时一句边界]`。例：

> 当用户准备提交代码、创建或切换分支、合并、推送或处理 Git 错误时，提供规范的 Git 工作流指导，并在可能改写历史或删除数据的危险操作前要求确认。

不要求同义动词全列（`review / audit / check / inspect` 选一即可），不要求把每个命令名都写进去，不要求引号包裹关键词。结论只给 `KEEP` 或 `REWRITE` + 一句理由；**禁止把 description 打成百分数或分数**。

## 11. Trigger Quality（与描述文本分开评）

| 维度 | 判据 |
| --- | --- |
| Coverage | 用户真实会用的场景是否覆盖 |
| Precision | 不相关任务是否误触发（相邻词如 `Git` 出现在「写 GitHub Action」场景不应抢走路由） |
| Boundary | 与相邻 Skill 是否有清楚分工（Not for / 交棒对象） |
| Natural Language Fit | 用户说自然语言时是否容易联想到该 Skill |

判据是**路由结果**，不是关键词数量。需要实证时用三类用例覆盖：真实会用的说法、明显无关的说法、与相邻技能易混的说法——各写几条按该技能复杂度决定，不设配额（写死数字只会让人往用例里凑数）。

## 12. Before / After 与最终报告

After 必须对比八项：Core Task、Description、Workflow、Rules、References、Scripts、Output Contract，并说明**删了什么、并了什么、留了什么、加了什么、为什么**。

OPTIMIZE 默认报告骨架（10 节；可按结论裁剪叙述篇幅，但 7 Before/After、8 Validation、9 Regression 三节不得省；不得退化成几十条 checklist）：

```markdown
# Optimization Summary
## 1. Core Task
## 2. 最重要的问题
## 3. 当前结构
## 4. 目标结构
## 5. 决策与处置
## 6. 实际修改
## 7. Before / After
## 8. Validation
## 9. Regression
## 10. Remaining Risks
```

## 13. 本模式的失效模式（自检）

- 把优化做成「加了一堆新文档」→ 违反 §1，退回删。
- 只有诊断没有改文件 → 那是 Audit，不配叫 Optimize。
- 改了文件但没跑 Validate/Regression → 结论无效。
- 为通过 validator 改写自然语言 → 反向信号，说明在优化检查器而不是优化 Skill。
- 用「更复杂的流程」证明工作量大 → 本文件本身若长到没人读，就该被压缩。
