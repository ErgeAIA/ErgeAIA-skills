---
trigger-when: 需要理解 skill-workshop 路由分级、证据驱动读取或规则分级时
name: core-method
description: skill-workshop v2 核心方法：L0/L1/L2 路由、证据预算、HARD/CONDITIONAL/HEURISTIC 规则分级、反膨胀四问。
---

# 核心方法（core-method）

## 第一性问题

用**最低审查成本**可靠发现会导致触发错误、执行错误、维护失控或上下文浪费的缺陷。

```text
低成本发现高风险问题 → 给出有证据的整改方向 → 必要时才深度诊断/评测
```

不是每次先跑完整检查清单，再组装标准化审计文书。

## 任务路由

| 用户意图 | 路径 | 产出 |
| --- | --- | --- |
| 创建 / 做一个 skill | 创建流 → `references/creation.md` | SKILL.md + 目录骨架 |
| 校验 / 合规 / validate | CLI `validate` + `spec` | PASS/FAIL + 错误清单 |
| 帮我看看 / 评审 / 审计 | 默认 **L0**；疑点或显式深度 → **L1** | 短报告（见 review.md） |
| 重构 / 优化结构 | L0/L1 发现问题 → 按 creation/validation 原则整改 | 改进后的技能文件 |
| 评测 / 触发率 / benchmark | **L2 条件触发** | 见下方 L2 |

命中清晰信号即进入对应路径；仅当意图无法归类时才向用户澄清一句。

## 审查深度（证据预算）

| 层级 | 何时进入 | 读取预算 | 产出 |
| --- | --- | --- | --- |
| **L0** | 默认（「帮我看看这个 skill」） | `SKILL.md` + 最多 1–3 份相关 reference；必要脚本入口 | **与 review.md 相同的六段短报告**（结论/第一性判断按需/可保留设计/问题清单/≤3 动作/是否继续重构）；可不附完整证据矩阵 |
| **L1** | 结构性疑点、跨文件冲突、用户显式要求深度/第一性审查 | 按疑点扩展：冲突文件、相关 scripts、契约文档 | 同上报告 + 证据化 findings（文件:位置）与 CONDITIONAL 展开 |
| **L2** | 明确要求评测/benchmark/触发率回归，或高风险自动执行需要实测 | 全面读取 + 工具链；脚本与 agents 在 `docs/archive/`，需时人工启用 | 触发率/回归结论（须标明使用了归档工具链） |

**禁止**：默认全量预读目标技能的 `references/` 与 `scripts/`。先做目录清单与机械事实（frontmatter、体量、链接、版本声明），发现可疑再打开相关文件。

## 证据驱动扫描

1. 列目录与体量（主文档行数、references 数量、scripts 是否存在）。
2. 读 `SKILL.md` 与版本声明（`metadata.version` + `CHANGELOG.md`）。
3. 记录疑点清单，只打开能证实/证伪疑点的文件。
4. 每条 finding 必须落到**具体文件**（及行号/章节）证据；无证据不报。

## 规则分级

| 级别 | 含义 | 默认行为 |
| --- | --- | --- |
| **HARD** | 违反即失效或破坏契约 | 必须报告；阻塞「通过」结论 |
| **CONDITIONAL** | 目标具备对应能力时才查 | 无该能力 → N/A，不硬凑 |
| **HEURISTIC** | 经验建议 | 有证据才报；不升格为 P0 |
| **ARCHIVED** | 历史规则 | 不参与运行时，见 `docs/archive/` |

### HARD 示例（运行时）

- 非破坏：重构不得静默覆盖用户已有 skill 产物。
- 平台字段：frontmatter 必含 `name` + `description`；`name` 与目录一致、hyphen-case。
- 版本 SSOT：`metadata.version` + `CHANGELOG.md`；不默认要求「三处版本块一致」。
- 主文档体量：原则 `<500` 行；工作室自用主文档目标 120–150 行。
- 结构性引用路径必须真实存在。

### CONDITIONAL 示例

| 条件 | 才检查 |
| --- | --- |
| 目标存在 `scripts/` | 脚本无交互、`--help`、退出码 0/1/2、stderr/stdout 分离 |
| 高频触发 / 高误触发风险 / 用户要求评测 | 评测集与触发质量（L2） |
| 明确要求家族一致性或指定 baseline | 家族差分（归档诊断） |
| 被其他 skill 编排且共享输出字段 | 字段争用 |
| description 有明显触发疑点或用户要求触发优化 | description 深度校准 |

### 明确废除（不得再作为阻塞规则）

- 强制输出 3–5 条优点（无高价值优点则省略）。
- 中等复杂度强制「至少识别 1 个拆分候选」（无职责耦合则写「无需拆分」）。
- 固定报告收尾套话。
- 「必须存在脚本」作为 P1。
- 默认强制评测集 / family-diff / 全量 W1–W7 流水线。
- 「三处版本一致」默认硬约束。

## 反膨胀四问（新增规则前）

1. 删掉它，哪个真实失败会重新出现？答不出 → 不进 HARD。
2. 该失败是否足以让 Skill 真正失效？否 → 不是 P0。
3. 是否只有某类 Skill 才会遇到？是 → CONDITIONAL。
4. 有没有真实执行证据？无 → 先 HEURISTIC，不要立法。

## 机器闸门

- 每次创建/重构后：`python scripts/skill_cli.py validate <path>`
- 字段合规：`python scripts/skill_cli.py spec <path>`
- 交付打包：`python scripts/skill_cli.py package <path>`（默认 dry-run）
- 脚本 FAIL 不得写「已通过」。

## 与 archive 的关系

`docs/archive/` 保存旧 W 流水线、54 项 checklist 脚本、评测 agents 等。  
**仅当** L1/L2 需要对照历史方法论时查阅；不得把归档规则默认写回运行时报告模板。
