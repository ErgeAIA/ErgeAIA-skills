---
name: skill-workshop
description: "Skill 质量工作站：把创建 / 评审 / 重构 / 评测 Agent Skill 四类动作路由到对应工作流，并保障产出通过结构校验。Use this skill whenever the user wants to create, review, refactor, or evaluate an Agent Skill. Invoke on '做个新 skill'/'帮我看看这个 skill'/'audit skill'/'重构 skill'/'评测 skill'/'校验 skill 规范'. Not for: 通用代码调试、非 Skill 文档创作、Agent 框架开发."
metadata:
  author: ErgeAIA
  version: "1.17.0"
---

# skill-workshop

<!-- @类型: 主工作流 -->
<!-- @目的: 指导创建、评审、重构、评测高质量的 AI Skill -->
<!-- @场景: 用户需要创建新 Skill、评审/审查已有 Skill、重构优化或评测迭代 -->
<!-- @ID: wf-skill-workshop-main -->

---

## @工作流: Skill 全生命周期管理

<!-- @类型: 主工作流 -->
<!-- @后置验证: Skill 通过校验并可被打包发布 -->
<!-- @ID: wf-skill-lifecycle -->

### @步骤1: 路由决策

<!-- @类型: 决策步骤 -->
<!-- @优先级: 必须 -->
<!-- @验证点: 已把当前请求稳定路由到创建、评审、重构或评测路径 -->
<!-- @验证方式: 根据用户原话命中决策矩阵，决定后续读取哪份 workflow -->
<!-- @ID: step-route-by-decision-matrix -->

## 1. 决策矩阵

| 场景       | 命中信号                                     | 入口工作流                                                                            | 产出              |
| ---------- | -------------------------------------------- | ------------------------------------------------------------------------------------- | ----------------- |
| 创建新技能 | 创建/新建/create/做一个/封装成技能           | [C1-create.md](references/workflows/C1-create.md)                                     | SKILL.md + 脚手架 |
| 深度评审   | 评审/review/审计/诊断/帮我看看/skill质量检查 | [W1-complexity.md](references/workflows/W1-complexity.md) → W2/W3(→W7) → W4 → W5 → W6 | 8 段结构报告      |
| 快速评分   | 评分/score/快速评估/加权评分                 | [weighted-scoring.md](references/rubrics/weighted-scoring.md)                         | 维度评分表        |
| 合规校验   | 校验/validate/合规/skill规范                 | [V0-validate.md](references/workflows/V0-validate.md)                                 | PASS / FAIL       |
| 重构优化   | 重构/refactor/优化/整理/workflow边界         | [C3-refactor.md](references/workflows/C3-refactor.md)                                 | 改进后 SKILL.md   |
| 评测迭代   | 评测/evaluate/benchmark/skill迭代            | [C2-evaluate.md](references/workflows/C2-evaluate.md)                                 | benchmark + 报告  |
| 澄清意图   | 模糊请求/未声明深度                          | [W0-clarify.md](references/workflows/W0-clarify.md)                                   | 路由决策          |

> 🔴 **CHECKPOINT**：决策矩阵路由前必须把"待选 workflow + 命中理由"展示给用户确认；用户不确认不进入下一步。

---

### @步骤1b: 触发方式

<!-- @类型: 信息步骤 -->
<!-- @优先级: 可选 -->
<!-- @验证点: Agent 能从用户请求中识别本技能 -->
<!-- @ID: step-trigger-method -->

## 1b. 触发方式

- **显式触发**：用户直接说"审查/评审/创建/重构/校验 skill"
- **隐式触发**：用户提到"skill 质量"/"skill 生命周期"/"帮我看看这个 skill"等意图关键词
- **否定触发**：通用代码调试、非 Skill 文档创作、Agent 框架开发 → 不触发本技能

---

### @步骤2: 应用硬规则

<!-- @类型: 规则步骤 -->
<!-- @优先级: 必须 -->
<!-- @验证点: 命中矩阵后已应用本 Skill 的固定约束 -->
<!-- @验证方式: 能说清哪些是运行期默认动作，哪些是设计期补充工作 -->
<!-- @ID: step-apply-hard-rules -->

## 2. 硬规则摘要

- @动作: **Plan-Validate-Handoff (P-V-H) 模式强制使用所有破坏性操作**——评审模式（W1-W7）只输出报告+整改方向不修改文件；创建/重构模式（C1/C3）执行 scaffold/edit/重构前必须先输出 Plan 让用户确认，再跑 V0 验证，最后交付。*Why：任何破坏性操作（文件覆盖/目录创建/SKILL.md 重写）若直接 Execute 风险过高，P-V-H 让用户始终握有否决权。*
- @动作: 新建/重构的 Skill **必须使用语义化标记**（`@工作流`/`@步骤N`/`@动作`/`@验证点`），参考 [skill-markup-guide.md](references/authoring/skill-markup-guide.md)。*Why：语义标记让 Agent 可机器解析工作流结构，纯 Markdown 标题只能被人类阅读。*
- @动作: 主 SKILL.md 只做路由，细节下沉到 references/。按需读取单个文件，**严禁全量预加载**。*Why：上下文窗口是公共资源，全量加载会挤占推理空间。*
- @动作: W5 整改方向必须标注 W3 checklist 编号（如 `命中：S1、P3`），否则断链。*Why：无编号追溯的建议缺乏证据支撑，用户无法验证建议的合理性。*
- @动作: W3 遇 T1-T5 **强制委托 W7**，不得自行判定 description。*Why：description 的语义判断需要专门的意图校准标尺，W3 的通用扫描精度不够。*
- @动作: frontmatter.metadata.version 必填；头部版本块和版本历史 section 可选（VERSION.md 存在时 V0 不强校验）。*Why：版本漂移会导致 Agent 加载过期指令；但头部/文末版本信息是人类维护点，不是 LLM 决策依赖，不应占用上下文。*
- @动作: 完成后必须跑 `python scripts/skill_cli.py validate <path>`。*Why：人工检查容易遗漏 frontmatter 格式、链接断裂等机械性错误。*

## 3. 失败模式编码（if-then 三段式）

> 路由/评估/重构过程中遇到以下症状，按"一线修复 → 仍失败兜底"两段处理。所有失败最终都收敛到 W0-clarify 重新路由。

| 症状 | 一线修复 | 仍失败兜底 |
|------|----------|------------|
| 决策矩阵无明确命中（模糊请求如"我有个 skill 问题"） | 默认路由 W0-clarify 询问深度 | 引导到 weighted-scoring 快速通道 |
| 路径冲突（同时命中"创建"和"评审"） | 按优先级：创建 > 重构 > 评测；后到的进 backlog | 🔴 CHECKPOINT 询问用户 |
| 命中 C1-create 但 skill 目录已存在 | 切到 C3-refactor | 询问"覆盖/重命名/合并" |
| 命中 V0-validate 但脚本报错 | 检查 `skill_path.resolve().name` 误判（Gotchas #8） | 手动跑 `quick_validate.py` 替代 |
| W7 判定 T1-T5 时无 rubric 支撑 | 引用 [intent-calibration.md](references/rubrics/intent-calibration.md) 标尺 | 委托独立 judge agent |
| results.tsv 损坏/列数不匹配 | 备份 `.bak.YYYYMMDD-HHMM` 后重建 | 询问用户是否继续 |
| subagent 不可用 | dim8 降级 dry_run，results.tsv 标注 `eval_mode=dry_run` | 提示用户需要 full_test 环境 |
| 优化后体积 > 原 × 1.5 | 强制精简（删冗余/合并重复） | 询问用户是否接受扩展 |
| test-prompts.json 已存在 | 复用并展示，问"复用/重写/追加" | 默认复用 |
| SKILL.md 找不到 | 该 skill 终止，results.tsv 记 `status=error` | 继续下一个 |

**P-V-H 关键决策点**：
- **🔴 CHECKPOINT**：所有"询问用户"路径都是 P-V-H 强制守关
- **🛑 STOP**：失败兜底收敛到 W0-clarify，禁止越权处理

---

## 4. 渐进式披露

> **三库索引**：9 个 authoring 文件 × 5 个 workflow reads-from 块的全部引用关系见 [`references/routing-table.md`](references/routing-table.md)（路由表 ↔ workflow 一致性硬校验的真相源，详见 `versioning-and-validation.md` 第 4 节"路由一致性"）

| 任务                               | 按需加载                                                                                                                                                                                                                                      |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 创建 Skill                         | [C1-create.md](references/workflows/C1-create.md) → [skill-foundations.md](references/authoring/skill-foundations.md)                                                                                                                         |
| 复杂度判定                         | [complexity-rubric.md](references/rubrics/complexity-rubric.md)                                                                                                                                                                               |
| 优点/问题扫描                      | [review-checklist.md](references/rubrics/review-checklist.md)                                                                                                                                                                                 |
| description 审计                   | [intent-calibration.md](references/rubrics/intent-calibration.md) + [frontmatter-style-guide.md](references/specs/frontmatter-style-guide.md) + [progressive-disclosure-patterns.md](references/authoring/progressive-disclosure-patterns.md) |
| description 优化                   | [optimizing-descriptions.md](references/specs/optimizing-descriptions.md)：三段式结构 + 触发测试集 + 优化循环                                                                                                                                  |
| frontmatter 字段过度工程化判定     | [frontmatter-style-guide.md](references/specs/frontmatter-style-guide.md)                                                                                                                                                                     |
| 版本一致性（V0 硬校验 + 规范指南） | [versioning-and-validation.md](references/authoring/versioning-and-validation.md)：V0 校验器检查 frontmatter.version 必填 + VERSION.md fallback；规范指南含完整版本维护规则                                                                   |
| 命名与归属                         | [naming-and-ownership.md](references/authoring/naming-and-ownership.md)                                                                                                                                                                       |
| 写作方法论                         | [writing-a-good-skill.md](references/authoring/writing-a-good-skill.md)                                                                                                                                                                       |
| 业务到工作流映射                   | [business-to-workflow-mapping.md](references/authoring/business-to-workflow-mapping.md)                                                                                                                                                       |
| 工作流模式                         | [workflow-patterns.md](references/authoring/workflow-patterns.md)                                                                                                                                                                             |
| 渐进披露模式                       | [progressive-disclosure-patterns.md](references/authoring/progressive-disclosure-patterns.md)                                                                                                                                                 |
| 重构指引                           | [skill-refactoring-workflow.md](references/authoring/skill-refactoring-workflow.md)                                                                                                                                                           |
| 评测方法                           | [skill-evaluation-workflow.md](references/authoring/skill-evaluation-workflow.md)                                                                                                                                                             |
| 快速评分                           | [weighted-scoring.md](references/rubrics/weighted-scoring.md)                                                                                                                                                                                 |
| 软性建议补充                       | [best-practices.md](references/specs/best-practices.md)                                                                                                                                                                                       |
| 规范校验                           | [spec.md](references/specs/spec.md)、[validate.md](references/specs/validate.md)                                                                                                                                                              |
| 规范演进跟踪                       | [CHANGELOG.md](references/specs/CHANGELOG.md)                                                                                                                                                                                                 |
| 报告装配                           | [evaluation-template.md](references/templates/evaluation-template.md)                                                                                                                                                                         |
| 语义标记规范                       | [skill-markup-guide.md](references/authoring/skill-markup-guide.md)                                                                                                                                                                           |
| 评测循环                           | [eval-loop.md](references/evaluation/eval-loop.md)                                                                                                                                                                                            |
| 一致性规则                         | [consistency-rules.yaml](references/config/consistency-rules.yaml)                                                                                                                                                                            |

| 任务 | 按需加载 |
| --- | --- |
| 评测闭环 Agent 提示词 | [analyzer.md](agents/analyzer.md) · [comparator.md](agents/comparator.md) · [grader.md](agents/grader.md)（仅 C2 评测链按需加载） |
| 场景输入模板 | [index.md](references/examples/index.md)（决策矩阵命中速查，创建/评测前置） |
| 评测回放 / 编辑器 | [eval_review.html](assets/eval_review.html) · [eval_set_editor.html](assets/eval_set_editor.html)（C2 产出展示） |

> **双风格说明（评审链 vs 创建链）**：评审链（W0-W7）使用纯 Markdown 标题 + frontmatter 元数据，创建/重构链（C1-C3）和 authoring/ 使用 `@工作流`/`@步骤N` 语义化标记。两种风格共存是设计选择——评审链为裁判角色设计，步骤间通过 checklist 编号串联；创建链为构建者设计，步骤间通过语义标记串联。阅读时按任务路径加载，不会同时面对两种风格。

---

## 5. 做法优于答案

在评审或创建时，**严禁直接给出修复后的代码全量内容**：
1. **识别模式**：指出违背了哪项最佳实践。
2. **解释逻辑**：解释为什么这种改动能提升 Agent 的理解力。
3. **优化方向**：指出整改方向与原则，不给出具体修改片段。

---

## 6. 双评估系统

| 体系           | 用途                 | 来源                                                          |
| -------------- | -------------------- | ------------------------------------------------------------- |
| **9 维 48 项** | 深度评审（发现问题） | [review-checklist.md](references/rubrics/review-checklist.md) |
| **8 维加权**   | 快速评分（结构质量） | [weighted-scoring.md](references/rubrics/weighted-scoring.md) |

两者语义不重叠：
- 评审/审计 → 用 9 维 48 项
- 创建后自评/快速评估 → 用 8 维加权

---

## 7. Gotchas（坑点）

- **路径假设**：脚本必须在 Skill 根目录运行，否则 Windows 下路径解析可能异常。
- **正则误报**：自检脚本对 `input(` 极为敏感，开发时须用过滤函数规避。
- **描述禁忌**：`description` 字段严禁出现尖括号 `<` `>`，否则合规校验必败。
- **判定权归属**：T1-T5 由 W7 唯一裁决；W3 在 T 系列上不得自行判定。
- **W5 必须有证据**：W5 任何整改方向必须能在 W3 命中项中找到对应编号。
- **裁判边界**：评审模式只输出报告，不执行文件写入。
- **术语一致性**：v4.0 重构后禁止使用旧术语（P-V-E、工作流拆分、优化建议等）。跑 `consistency` 子命令可自动检测。
- **路径假设（validate .）**：`validate .` 在 Skill 子目录内运行时，`skill_path.name` 返回 `.` 而非目录名，导致 "Name must match parent directory" 误报。V0 校验器已用 `skill_path.resolve().name` 修复，但其他脚本若直接用 `.name` 仍有此风险。

---

## 8. 非目标 (Non-Goals)

- 通用代码调试 / 重构（非 Skill 仓库）
- 与 Skill 无关的文档创作（博客、教程、营销稿）
- Agent 框架本身的开发（LangChain、AutoGPT 内核）
- 非 Markdown / 非 Python 的 Skill
- frontmatter 字段裁剪决策（哪些字段该删/该留由用户判断，本技能只提供过度工程化检测）

---

## 9. 验证闭环

- **V1 成功判定**：评审报告必须包含 `### 8. 总评` 段落。
- **V2 自检标准**：`python scripts/skill_cli.py checklist <path>` 必须返回 PASS。
- **V3 产出检查**：合规模式输出必须严格遵循 `**Validation**: [PASS/FAIL]` 格式。
- **V4**：检查被评审 Skill 是否有正面/负面触发测试集（参考 [trigger-test-set.md](references/templates/trigger-test-set.md)）。
- **V5**：评估断言可机器判定（非主观评分）。
- **V6**：W5 每条建议必须包含 checklist 编号标注。
- **V7**：`python scripts/skill_cli.py consistency <path>` 无旧术语残留。
