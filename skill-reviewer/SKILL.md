---
name: skill-reviewer
description: "Review and validate local Agent Skill repositories against a 9-dimension, 48-item checklist. Produces structured reports with prioritized issues (P0/P1/P2) and actionable remediation directions. Two modes: full review (8-section report) and compliance validation (PASS/FAIL). Use this skill whenever the user wants to review, audit, evaluate, validate, or diagnose a skill — including checking skill quality, compliance, engineering maturity, or getting improvement suggestions. Also triggers on Chinese phrases: skill审查, skill评审, skill校验, skill合规, skill诊断, skill质量检查, skill规范检查, 帮我看看这个skill, 这个skill有什么问题. Not for: creating new skills (use skill-creator), optimizing trigger rates (use skill-creator), general code review/debugging, writing documentation/blogs, agent framework development."
compatibility: Requires Python ≥ 3.10. PyYAML optional (for external consistency rules; script degrades gracefully without it).
metadata:
  author: ErgeAIA
  version: "4.6"
---

# skill-reviewer

> 用途：评审与校验本地 Agent Skill 仓库（基于目录结构和文件内容）。
> 裁判原则：格式合规是底线，意图识别是核心，执行轨迹是真理。
> 工程原则：**职责单一，判定收敛，证据可追溯。​**
> 角色定位：**裁判**——只发现问题、定级、出具报告、复审验证；不执行具体优化，不修改被评审对象。优化实施由 skill-creator 承担。

---

## 1. 调度模式

- **评审模式**：执行 `workflows/W1-complexity.md` 起的完整分析链路。
- **合规校验模式**：执行 `workflows/V0-validate.md`。
- **澄清前置**：当用户语义模糊时，先执行 `workflows/W0-clarify.md`。

两种模式互斥；用户要求"先校验再评审"时，按 V0 → W1 串行执行。

---

## 2. 工作流路由表

| 工作流                    | 触发条件                       | 类型     | 输出去向                    |
| ------------------------- | ------------------------------ | -------- | --------------------------- |
| **W0 澄清**               | 用户语义模糊 / 未声明评审深度  | 前置     | 决定后续走 V0 或 W1         |
| **V0 合规校验**           | 用户明确要求 "校验 / validate" | 独立     | PASS / FAIL 终态            |
| **W1 复杂度判定**         | 用户明确要求 "评审 / review"   | 主链入口 | 决定是否走 W4               |
| **W2 优点扫描**           | W1 完成后无条件触发            | 主链     | 报告第 3 段                 |
| **W3 问题扫描**           | W1 完成后无条件触发            | 主链     | 报告第 4 段（接收 W7 回写） |
| **W7 description 子审计** | W3 扫描 T 系列时**强制委托**   | 子工作流 | 回写 W3 P1 子项             |
| **W4 拆分需求识别**       | W1 判定 ≥ 中等复杂度           | 条件主链 | 报告第 5 段                 |
| **W5 整改方向映射**       | W3 至少有一条命中项            | 条件主链 | 报告第 6 段                 |
| **W6 总评**               | W2 + W3 完成后无条件触发       | 主链     | 报告第 1 段 + 第 8 段       |

### 调用关系（防断链）
- `W3` **必须**在扫描 T1–T5 时委托 `W7`，不得自行判定 description
- `W2` 和 `W3` **必须**引用 `references/rubrics/review-checklist.md` 作为唯一判定源
- `W1` **必须**引用 `references/rubrics/complexity-rubric.md` 作为复杂度判定的唯一标尺
- `W5` **必须**逐条对应到 `W3` 的命中编号，禁止预设清单
- `W4` 仅在 `W1` 判定 ≥ 中等复杂度时触发，轻量级**显式跳过**并在报告中注明
- `V0` 与 W 系列**互斥**：用户走校验就不走评审，反之亦然

---

## 3. 文件角色映射

| 路径                                                     | 角色                                                        | 谁消费它                            |
| -------------------------------------------------------- | ----------------------------------------------------------- | ----------------------------------- |
| `workflows/W0-clarify.md`                                | 流程                                                        | 用户请求入口                        |
| `workflows/V0-validate.md`                               | 流程                                                        | 校验模式入口                        |
| `workflows/W1-complexity.md` ~ `W7-description-audit.md` | 流程                                                        | 评审模式主链                        |
| `references/rubrics/review-checklist.md`                 | **唯一判定标准源**                                          | W2 / W3                             |
| `references/rubrics/complexity-rubric.md`                | **唯一复杂度标尺**                                          | W1                                  |
| `references/rubrics/intent-calibration.md`               | T 系列示例库                                                | W7                                  |
| `references/specs/spec-zh.md`                            | 官方规范（硬限）                                            | V0                                  |
| `references/specs/validate-zh.md`                        | 官方校验规则（硬限）                                        | V0                                  |
| `references/specs/best-practices.md`                     | 官方最佳实践（软限）                                        | W3（M/P/V/B 维度补充标尺）          |
| `references/specs/frontmatter-style-guide.md`            | 风格参考（非审查规则）                                      | Skill 设计时自检                    |
| `references/templates/output-template.md`                | 评审报告骨架                                                | 评审模式最终装配                    |
| `references/templates/trigger-test-set.md`               | 触发测试集参考（转交 skill-creator）                        | W7 命中 T5 时建议转交 skill-creator |
| `references/trigger-test-set.md`                         | 本 Skill 自身触发测试集（V4 落地）                          | description 修改后回归验证          |
| `scripts/validate_review.py`                             | V0 实现 + 自检 + 术语一致性检查 + name/description 合规校验 | V0 / V7 调用                        |
| `examples/skill-reviewer-self-review.md`                 | 自检参考样本                                                | 不参与判定，仅供示范                |

---

## 4. 做法优于答案（方法论指导）

在进行评审时，**严禁直接给出修复后的代码全量内容**。应遵循以下方法论：
1. **识别模式**：先指出违背了哪项最佳实践（参考 `references/rubrics/intent-calibration.md` 与 `references/specs/best-practices.md`）。
2. **解释逻辑**：利用 LLM 的 Theory of Mind，解释为什么这种改动能提升 Agent 的理解力。
3. **优化方向**：指出整改方向与原则，不给出具体修改片段。具体实施由 skill-creator 或用户执行，裁判只负责复审。

---

## 5. 指导自由度分级

本 Skill 对模型的约束强度因模式而异：

| 模式       | 自由度 | 约束方式                                  | 原因                                   |
| ---------- | ------ | ----------------------------------------- | -------------------------------------- |
| W0 澄清    | 高     | 给原则（启发式提问）                      | 依赖上下文判断用户意图，无法预设模板   |
| V0 合规    | 低     | 给代码（`validate_review.py` 判定）       | 合规结果确定，不允许模型自由发挥       |
| W1–W7 评审 | 中     | 给模板（`output-template.md` + 检查清单） | 有首选输出结构，但判定过程需结合上下文 |

> 评审模式下，Agent 应严格遵循检查清单的判定标准（低自由度），但在优缺点的措辞和组织上有一定灵活空间（中自由度）。

---

## 6. Plan-Validate-Handoff (P-V-H) 模式

当用户请求对现有 Skill 进行「重构」或「批量修改」等破坏性操作时：
- **Plan**：先输出重构计划表（参考 `workflows/W4-workflow-split.md`）。
- **Validate**：要求用户确认计划，并运行 `scripts/validate_review.py` 校验当前基线。
- **Handoff**：将确认后的计划转交 skill-creator 执行具体修改，或由用户自行修改后请求裁判复审。

> **裁判不下场踢球**：本 Skill 只输出评审结论与整改方向，不执行被评审对象的文件写入操作。

---

## 7. 渐进式披露纪律

**严禁全量预加载。必须按需读取单个文件：​**

| 评审任务         | 按需加载                                                         |
| ---------------- | ---------------------------------------------------------------- |
| 复杂度判定       | `references/rubrics/complexity-rubric.md`                        |
| 优点 / 问题扫描  | `references/rubrics/review-checklist.md`                         |
| description 审计 | `references/rubrics/intent-calibration.md`（W7 内部按需读取）    |
| 软性建议补充     | `references/specs/best-practices.md`                             |
| 规范校验         | `references/specs/spec-zh.md`、`references/specs/validate-zh.md` |
| 报告装配         | `references/templates/output-template.md`                        |

---

## 8. Gotchas（评审坑点）

- **路径假设**：脚本 `validate_review.py` 必须在 Skill 根目录运行，否则 Windows 下的 `resolve().name` 可能返回空或父目录名。
- **正则误报**：自检脚本对 `in` + `put` 极为敏感，开发脚本时须使用过滤函数（如 `_is_real_input_call()` 排除注释行和正则定义行）或十六进制转义（如 `\x69\x6e\x70\x75\x74`）规避。
- **描述禁忌**：`description` 字段严禁出现尖括号 `<` `>`，否则官方合规校验必败。
- **判定权归属**：T1–T5 由 W7 唯一裁决；W3 在 T 系列上不得自行判定，避免「四个裁判判一个球」。
- **W5 必须有证据**：W5 任何整改方向必须能在 W3 命中项中找到对应编号，否则不输出（防止空判）。
- **裁判边界**：W5 只指出整改方向，不给出具体修改方案；W4 只识别拆分需求，不设计目标架构。具体实施由 skill-creator 执行。
- **rubrics 与 templates 不可混淆**：`rubrics/` 是判定标尺，`templates/` 是产出骨架，迁移 / 引用时不可错位。
- **术语漂移**：v4.0 重构后若修改 SKILL.md 中的术语（如 P-V-H、拆分需求识别、整改方向），必须同步更新 workflows/、examples/、references/ 中的引用。运行 `scripts/validate_review.py --consistency .` 可自动检测旧术语残留。
- **退出码约定**：`validate_review.py` 退出码：0=PASS、1=FAIL、2=参数错误。Agent 或 CI 脚本应依据退出码判断校验结果。

---

## 9. 验证闭环（自检标准）

- **V1 成功判定**：评审报告必须包含 `### 8. 总评` 段落。
- **V2 完整性检查**：执行 `scripts/validate_review.py --checklist .` 必须返回 `Checklist PASS`。
- **V3 产出检查**：合规模式输出必须严格遵循 `**Validation**: [PASS/FAIL]` 格式。
- **V4 评估测试集**：检查被评审 Skill 是否有正面/负面触发测试集（参考 `references/templates/trigger-test-set.md`），用于 description 修改后的回归验证。本 Skill 自身测试集：`references/trigger-test-set.md`（正面 12 条 + 负面 8 条）。
- **V4.1 评测驱动迭代纪律**：修改 description 或触发逻辑后，必须执行回归验证：① 不加 Skill 跑目标任务建立基线 ② 应用修改 ③ 跑触发测试集验证正面命中率 ≥90% 且负面误触发 ≤10% ④ 若未通过，优先简化 description 而非叠加新规则。所有新增规则均需对应新增或已有测试用例。
- **V5 评估断言可机器判定**：检查评估断言是否可机器判定（非主观评分），确保验证结果可客观复现。`validate_review.py --checklist` 已机器化的检查项：S2（结构化标记）、B3（触发关键词覆盖）、B4（Non-Goals）、C4（参考文件 trigger-when）、I2（可运行脚本）、M1（Gotchas）、M6（方法论）、M8（P-V-H）、P3–P7（脚本设计）、T3（三维触发）、V1–V5（验证闭环）、版本一致性。
- **V6 证据链检查**：评审报告中 W5 的每条建议必须包含 checklist 编号标注（如 `命中：S1、P3`），否则视为断链。
- **V7 术语一致性检查**：执行 `scripts/validate_review.py --consistency .` 扫描全仓库 Markdown 文件，检测旧术语残留（如 P-V-E、工作流拆分、优化建议等 v4.0 前的命名）。

---

## 10. 运行时要求

- Python ≥ 3.10
- PyYAML（可选）：`--consistency` 模式加载外部规则时需要；缺失时脚本自动降级为仅使用内置规则
- 操作系统：Linux / macOS / Windows 均兼容（Windows 下注意 Gotchas 中的路径假设）

---

## 11. 非目标 (Non-Goals)

为避免触发竞争与上下文浪费，本 Skill **不处理**以下场景：

- 通用代码调试 / 重构（非 Skill 仓库）
- 与 Skill 无关的文档创作（如博客、教程、营销稿）
- Agent 框架本身的开发（如 LangChain、AutoGPT 内核）
- 非 Markdown / 非 Python 的 Skill（如纯 Bash / 纯 YAML 配置类）

如用户请求落在上述范围内，应礼貌拒绝并建议使用更合适的工具。
