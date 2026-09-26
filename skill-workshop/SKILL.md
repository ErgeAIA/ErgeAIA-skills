---
name: skill-workshop
description: "Agent Skill 全生命周期工作台：用于创建、评审、优化、重构、校验和打包 Skill，从明确任务与边界，到调整结构、规则与实现，再到验证结果，形成完整闭环。用户要新建、完善、重构或校验 Skill 时使用。Not for: 通用代码或应用项目开发与审查。"
metadata:
  author: ErgeAIA
  version: "2.5.0"
---

# skill-workshop

## 定位

**Agent Skill 全生命周期工作台**（轻量，不是治理系统）。Core Task：

```text
当用户要创建、评审、优化或校验一个 Agent Skill 时，
帮助用户以尽可能低的成本，发现并修复真正影响触发、执行、输出、维护与安全的问题。
```

```text
Core Task 锚点 → 风险驱动分级 → 证据化 findings → 用更小的规则系统解决问题
```

不是治理系统：不默认固定 W1–W7 全量流水线；不强制凑优点/拆分/收尾套话；不要求每个 Skill 都有脚本或评测集。

**审计与优化是两件事**：AUDIT 回答「有没有问题」，默认低成本、只出报告；OPTIMIZE 回答「怎么让它真的变好」，必须先全量读懂它实际怎么工作，再真正改文件并验证核心能力未丢。把优化做成「列问题 + 改几句措辞 + 加几条规则」即为失职（方法论见 `references/optimization.md`）。

**不可违背**：① 不破坏用户已有 skill 产物；② 遵守 Agent Skills 官方 frontmatter 约束；③ 机械问题交给 CLI，**语义质量不由正则判定**；④ 问题必须落到文件证据；⑤ **单一审计主流程**——方法论是判断框架，不是第二套并行流程；⑥ 任何新增规则必须写明它解决哪个**实际失败**，答不出就不新增。

**边界**：只处理 Agent Skill；不替代人类最终业务判断；评审路径默认只出报告。

## 路由

| 用户意图 | 模式 | 进入 | 产出 |
| --- | --- | --- | --- |
| 创建 / 做一个 / 封装 skill | CREATE | `references/creation.md`（意图不清先过其 Grill 闸）+ CLI `init` | SKILL.md + 目录 |
| 帮我看看 / 评审 / 审计 / 好不好 | AUDIT | **Fast Review（L0）**默认；疑点或显式深度 → **Deep Review（L1）** | 报告（`references/review.md`），**不改文件** |
| 优化 / 重构 / 改好 / 审查后帮我改 / 它为什么不好用 | **OPTIMIZE** | 读 `references/optimization.md`：**全量读运行时资产** → 八步流程 → 实际改文件 | 改进后的技能 + Target Architecture + Before/After + 回归结论 |
| 校验 / 合规 / validate | VALIDATE | CLI `spec` + `validate` | PASS/FAIL（只判结构，不判语义质量） |
| 评测 / benchmark / 触发率 | Eval（条件，属 Audit 侧） | **Eval Review（L2）**条件；工具在 `docs/archive/` | 评测结论 |
| 他技转交 Skill 审查 | AUDIT | 同评审入口（默认 Fast） | 报告 |
| 意图模糊 | — | 只澄清必要信息 | 路由决策 |

命中清晰信号即进入；不要先问「您要哪一种工作流编号」。**OPTIMIZE 不再沿用 AUDIT 的默认深度**：说「优化/重构」却只跑 Fast，是本技能最常见的失效方式。

### Fast / Deep / Optimize / Validate（摘要）

- **Fast（L0）**：默认。目录清单 + SKILL + 1–3 份相关文件；六段短报告。  
- **Deep（L1）**：Core Task 五问、Evidence-First、规则生命周期、结构膨胀（只诊断，不改文件）。  
- **Optimize**：Deep 的判断纪律 + 全量读取 + 目标架构 + 资产处置 + 实际重写 + 验证 + 能力回归（`references/optimization.md`）。  
- **Validate**：机器结构检查；不得冒充语义质量评估。  

判断框架（五问/六类/生命周期/删除优先/HARD 防火墙）→ `references/core-method.md`；评审步骤与报告结构 → `references/review.md`；优化流程与处置表 → `references/optimization.md`。

## 核心约束

1. **主文档只做路由与硬边界**；细节按需读 references。**审计路径**禁止全量预加载目标技能的 `references/` 与 `scripts/`（成本约束）；**优化路径相反**，必须先全量读完再动手（`references/optimization.md` §2）。
2. **规则生命周期**：HARD / CONDITIONAL / HEURISTIC / EXPERIMENTAL / ARCHIVED；CONDITIONAL 条件不成立 = N/A。  
3. **删除优先**：删除 > 合并 > 条件化 > 迁移 > 重写 > 最后才新增；HARD 需真实失败证据。  
4. **废除硬凑**：无优点则省略；无职责耦合则「无需拆分」；不写固定收尾套话；**不摊派资产**——checklist / scripts / eval / Gotchas / FAQ / 示例只有在解决真实失败时才存在，缺它们不是缺陷。  
5. **版本 SSOT**：`metadata.version` + 根 `CHANGELOG.md`。  
6. **脚本与评测非必须**：无 scripts 可优秀；评测仅 Eval/高风险/显式要求。  
7. **纯净 Markdown**：不注入步骤级 `@` 标记；不建第二套 DSL。  
8. **Runtime/Governance 分离**：治理规则不注入被审计 Skill 运行时。  
9. **plan-gate**：`init`/`package --write` 默认 dry-run；`decision_required` 必须转述用户。  
10. **验证闭环**：创建/重构后跑 `validate`（建议 `spec`）；FAIL 不得宣称通过。  
11. **证据纪律**：结论能指到文件；无产物=未执行；不确定时标 CONFIRMED / INFERRED / UNKNOWN，猜测不得写成硬缺陷。  
12. **裁判边界**：评审不直接改用户文件；构建路径才写盘且非破坏。  
13. **反治理膨胀**：workshop 自身不得因整合方法论而长出第二流程或巨型 checklist。  
14. **优化不以新增量衡量**：评价一次优化只看 Core Task、Trigger、Execution、Output、Safety、Context 是否改善；行数增减本身不是指标。

## CLI（运行时仅此四项）

```bash
python scripts/skill_cli.py validate <skill-dir>
python scripts/skill_cli.py spec <skill-dir>
python scripts/skill_cli.py init <skill-name> --path <parent> [--write]
python scripts/skill_cli.py package <skill-dir> [out-dir] [--write]
```

退出码：`0=PASS`，`1=FAIL`，`2=ERROR`。诊断写 stderr。PowerShell 用 `;` 串联。

已归档子命令见 `docs/archive/scripts/`。

## 构建路径（创建 / 优化）

1. 路由确认意图（创建 vs 优化 vs 只评审）。  
2. 创建读 `references/creation.md`——**意图不清先走其「创建前 Grill 闸」对齐需求**（AI 快交付会把未澄清的需求固化进技能，维护成本远高于当场问清），再套模板；**优化读 `references/optimization.md` 并按其八步走**；格式闸门见 `validation.md`，判断框架见 `core-method.md`。  
3. 落盘前：创建用 `init` dry-run；优化必须先出 Target Architecture 与逐项处置表，只动权威源，不碰运行态目录。  
4. 落盘后：`spec` + `validate`；**再做能力回归**（原 Core Task、触发、输出契约、安全边界仍在，至少一条真实正例与一条负例）；需要时再 `package --write`。  
5. 升版：`metadata.version`、`CHANGELOG.md`、根 README，跑 Skills-Depot 索引同步。  
6. 输出 Before/After 与 10 节优化报告（见 `optimization.md` §12）。

评审路径不要跳到第 3–6 步，除非用户明确授权写文件。用户已提供**完整重构执行指令**时，按指令执行 + 本技能闸门，不另起平行流程。

Fast 检查清单（9 项）与其升级信号只在 `references/review.md` 定义，本文件不重复；疑点再升 Deep，不在 Fast 扩大读取面。

## 资源指引（按需读取）

| 文件 | 何时读 |
| --- | --- |
| `references/core-method.md` | 判断框架：Core Task、五问、六类、生命周期、删除优先、证据预算 |
| `references/creation.md` | 创建/脚手架、**创建前 Grill 闸（条件·自持决策树）**、纯净模板、description 的 Trigger+Job+Boundary 写法 |
| `references/review.md` | Fast/Deep/Eval、T/E/C、证据格式、P0/P1/P2、报告结构 |
| `references/optimization.md` | **优化模式**：全量读取、运行机制建模、目标架构、资产处置、重写、回归、Before/After |
| `references/validation.md` | 格式 HARD、版本 SSOT、CLI/plan-gate、N/A 与安全 |

`docs/archive/`：历史工具与评测链——仅条件诊断，不写回默认报告模板。

## 默认输出（评审）

Fast：六段短报告（结论 / 第一性判断按需 / 可保留设计 / 问题清单 / ≤3 动作 / 是否继续重构）。

Deep：在短报告上附证据化 findings；复杂重构再附 Rule/File Disposition 等扩展字段（见 `review.md`）。

## Gotchas

- `description` 禁止尖括号（本仓约定）；`name` 必须等于目录名且 hyphen-case。  
- **validator 只判结构**：v2.3.0 起不再统计触发词、不再数引号词、不再用正则判「主动句式」。若某个 description 的 `validate` 通过但语义很差，那是评审/优化的活，不要反过来给 CLI 加回词法判据。  
- 斜杠与半角冒号是 **advisory**（风格约定）；未双引号与反斜杠才是 **HARD**（YAML 真实解析风险）。不要为了过检查把自然语言改拧。  
- **说不出来源的 blocker 一律降级**：判据严重度分四级（官方 spec / 有后果的本仓约定 / 纯风格 / 已归档作者体系），只有前两级可 FAIL；见 `validation.md`「判据来源与严重度」。  
- `validate` 建议传显式路径。  
- `package`/`init` 不带 `--write` 不落盘（plan-gate）。  
- 不要把 `docs/archive/` 旧 W 流水线或巨型 checklist 默认套到新报告上。  
- 升版同步：`metadata.version` = CHANGELOG 顶部 = 根 README，并跑 `sync_skills_browser.py`。  
- **评审 ≠ 重构指令**；执行重构须用户授权；已有完整指令则按指令 + 闸门执行。  
- **优化 ≠ 加规则**：一次优化没有删掉或合并掉任何东西时，先怀疑是没读懂问题，而不是问题已经很干净。

## 非目标

- 通用代码/应用项目审查、Agent 框架开发  
- 默认重建全量 W 流水线、巨型 checklist、并行第二审计流程  
- 评审路径未授权写文件  
- 修改运行态目录（`~/.agents/skills` 等）  
- 为 workshop 自身引入 `@` DSL 或治理规则注入目标 Skill  
- 用关键词数量、引号计数或句式正则代替语义判断（v2.3.0 已废除该类词法评分）  
- 把优化做成「加更多规则、加章节、加 checklist」  
- 为通过 validator 而改写本来自然的描述文本

## 验证闭环

- 交付前：`spec` + `validate` 均应 PASS（advisory 不阻塞，FAIL 阻塞）。  
- 优化模式额外要求：`python scripts/tests/test_validator.py` 全绿（改 validator 必改/加对应用例）+ 能力回归有真实正例与负例输出。  
- 本技能：版本三处对齐 + 用户验证后方可宣称重构/整合完成。
