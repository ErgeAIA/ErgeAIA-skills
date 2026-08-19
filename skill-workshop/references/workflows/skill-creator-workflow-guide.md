---
trigger-when: "了解 Skill 创建流程全貌时"
name: skill-creator-workflow-guide
description: Skill 创建器的工作流与业务流程说明。用于理解 kz-skill-creator 的功能边界、业务流程、子工作流关系与支撑参考文档分工时使用。
version: 1.3.3
---

# Skill 创建器的工作流与业务流程说明

<!-- @类型: 参考指南 -->
<!-- @名称: Skill 创建器的工作流与业务流程说明 -->
<!-- @适用场景: 需要理解 kz-skill-creator 的功能边界、业务流程和各工作流关系时 -->
<!-- @说明: 本文档用于帮助理解 Skill 的能力边界与工作流结构，不负责具体任务路由或内部执行细节 -->

> **版本**: v1.3.3
> **用途**: 帮助理解 `kz-skill-creator` 的功能定位、业务流程、子工作流关系与支撑参考分工
> **适用范围**: 使用者、维护者、协作者、需要快速理解本 Skill 结构的团队成员

---

## @工作流: 理解 Skill 创建器的业务流程与工作流关系

<!-- @类型: 主工作流 -->
<!-- @目的: 帮助读者理解 kz-skill-creator 的总体定位、业务流程、工作流边界和支撑参考关系 -->
<!-- @场景: 需要快速理解本 Skill 整体能力，或需要向协作者解释各子工作流之间的关系时 -->
<!-- @前置条件: 已知当前文档属于 kz-skill-creator 的参考资料 -->
<!-- @后置验证: 读者能够区分主 SKILL、子工作流与支撑参考，并知道下一步应去读哪份文档 -->
<!-- @触发条件: 当需要理解而不是直接执行 Skill 创建/重构任务时 -->
<!-- @ID: wf-understand-skill-creator-workflows -->

## 1. 文档定位

### @步骤1: 明确本文档解决什么问题

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @验证点: 已明确本文档是理解性说明，而不是执行手册 -->
<!-- @验证方式: 能说清本文档回答什么问题，以及执行具体任务时应转向哪些文档 -->
<!-- @ID: step-clarify-workflow-guide-purpose -->

本文档不是执行手册，也不是实现细节说明，而是一份面向人阅读的“总览文档”，重点回答：

- `kz-skill-creator` 整体负责什么，不负责什么
- 它包含哪些子工作流，这些工作流之间是什么关系
- 从业务视角看，一次 Skill 创建或重构任务通常如何流转
- `SKILL.md` 本身和各份 `references/` 文档分别承担什么角色

如果你要直接执行任务，请优先阅读：

- [SKILL.md](../../SKILL.md)
- [skill-foundations.md](../authoring/skill-foundations.md)
- [business-to-workflow-mapping.md](../authoring/business-to-workflow-mapping.md)
- [skill-refactoring-workflow.md](../authoring/skill-refactoring-workflow.md)
- [versioning-and-validation.md](../authoring/versioning-and-validation.md)

---

## 2. Skill 总体定位

### @步骤2: 理解本 Skill 的职责边界

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @依赖: step-clarify-workflow-guide-purpose -->
<!-- @验证点: 已明确本 Skill 主要负责什么、明确不负责什么 -->
<!-- @验证方式: 能基于本文档区分本 Skill 的能力范围与非职责边界 -->
<!-- @ID: step-understand-skill-creator-boundary -->

`kz-skill-creator` 是一个围绕“创建、重构、验证、评测 Skill”展开的方法论型 Skill。它的核心目标不是产出某一份特定领域文档，而是帮助执行者把一个 Skill 做成：

- 可触发
- 可执行
- 可验证
- 可迭代
- 可理解

### 2.1 它主要负责什么

- 帮助创建新 Skill，并收敛主工作流与资源结构
- 帮助重构已有 Skill，整理 workflow 边界、references 与验证机制
- 帮助判断哪些内容应留在主 `SKILL.md`，哪些应下沉到 `references/`
- 帮助把强制规则固化到语义化标记、版本规则与校验入口里
- 帮助理解本 Skill 自己的工作流分层和支撑参考分工

### 2.2 它明确不负责什么

- 不替代目标 Skill 所在业务域的专业知识
- 不直接执行目标 Skill 的业务任务本身
- 不把所有解释都塞进主 `SKILL.md`
- 不把理解性文档误当成执行路由文档

---

## 3. 业务流程总览

### @步骤3: 从业务视角理解主链和分支

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @依赖: step-understand-skill-creator-boundary -->
<!-- @验证点: 已理解 Skill 创建/重构任务的主链与典型分支 -->
<!-- @验证方式: 能复述主业务链，并指出新建型、重构型、校验发布型等典型分支 -->
<!-- @ID: step-understand-skill-creator-business-flow -->

从业务角度看，`kz-skill-creator` 常见任务通常按下面的路径流转：

1. 先用主 `SKILL.md` 前段的“决策矩阵 + 强规则摘要”命中当前路径，再确认当前任务到底是“新建 Skill”“重构已有 Skill”，还是“评测已有 Skill”
2. 明确目标 Skill 要解决的问题、触发边界和复杂度
3. 决定是否需要进入“业务流程 -> workflow”映射
4. 规划主 `SKILL.md`、`references/`、`scripts/`、`assets/` 的分工
5. 完成编写或重构
6. 跑验证、打包与必要的评测闭环
7. 在真实使用中继续迭代

### 3.1 用一句话理解主业务链

可以把这条链理解成：

`主文档路由 -> 需求确认 -> 复杂度判断 -> workflow/资源拆分 -> 创建 / 重构 / 评测 -> 校验打包 -> 真实使用迭代`

### 3.2 典型业务分支

- **新建型**：从零创建 Skill，先走创建流程
- **重构型**：已有 Skill 结构混乱，先走重构流程
- **理解型**：不立即执行，只需要看懂这个 Skill 的边界和工作流关系
- **评测型**：先评价一个已有 Skill 的结构质量，再决定是否进入重构
- **发布型**：主要关注版本、链接、验证与打包

---

## 4. 工作流映射表

### @步骤4: 用映射表理解主 SKILL 与子工作流边界

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @依赖: step-understand-skill-creator-business-flow -->
<!-- @验证点: 已能根据映射表理解主 SKILL 和各子工作流的边界与衔接 -->
<!-- @验证方式: 能指出任一工作流的做什么、不做什么、上下游和是否可单独触发 -->
<!-- @ID: step-read-skill-creator-workflow-map -->

| 工作流 | 类型 | 做什么 | 不做什么 | 上游 | 下游 | 失败回流 | 可否单独触发 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `SKILL.md` 主工作流：理解并创建 Skill | 主 workflow | 负责总路由、总原则、关键入口与加载时机 | 不承载所有展开细节 | 用户请求 | 创建流程 / 重构流程 / 各参考文档 | 边界不清时回到需求确认 | 是 |
| 创建流程（含前置确认） | 子 workflow | 指导从零创建或增量完善一个 Skill | 不负责解释所有支持文档的展开细节 | 主 `SKILL.md` 路由 | 初始化、编辑、验证、迭代 | 需求不清时回到前置确认 | 是 |
| 重构现有 Skill | 子 workflow | 指导整理已有 Skill 的结构、边界、references 与验证机制 | 不替代从零创建流程 | 主 `SKILL.md` 路由 / 现有 Skill | 重构参考、验证与打包 | 结构判断失误时回到盘点 | 是 |
| 评测已有 Skill | 子 workflow | 指导评价已有 Skill 的结构质量、问题优先级与评估文档输出 | 不默认直接改写目标 Skill | 主 `SKILL.md` 路由 / 现有 Skill | 结构评估参考 / 后续重构 | 证据不足时回到盘点 | 是 |

---

## 5. 支撑参考文档映射表

### @步骤5: 区分“子工作流”和“支撑参考”

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @依赖: step-read-skill-creator-workflow-map -->
<!-- @验证点: 已能区分哪些文档负责执行路由，哪些文档负责提供支撑规则 -->
<!-- @验证方式: 能指出任一参考文档的定位、做什么和不做什么 -->
<!-- @ID: step-read-supporting-reference-map -->

| 文档 | 类型 | 做什么 | 不做什么 | 何时读取 |
| --- | --- | --- | --- | --- |
| [skill-foundations.md](../authoring/skill-foundations.md) | 基础参考 | 解释 Skill 基础概念、目录结构、资源职责、渐进加载 | 不负责具体任务路由 | 需要回顾基础设计口径时 |
| [business-to-workflow-mapping.md](../authoring/business-to-workflow-mapping.md) | workflow 设计参考 | 指导中复杂 Skill 做业务流程到 workflow 的映射 | 不替代主创建流程 | 需要拆 workflow 边界时 |
| [skill-refactoring-workflow.md](../authoring/skill-refactoring-workflow.md) | 重构参考 | 指导已有 Skill 的迁移顺序、渐进加载检查与回归校验 | 不替代从零创建流程 | 任务是重构已有 Skill 时 |
| [skill-evaluation-workflow.md](../authoring/skill-evaluation-workflow.md) | 结构评估参考 | 指导已有 Skill 的证据收集、8 维加权评分、问题归纳与评估文档输出 | 不替代自动化 eval-loop 或直接重构流程 | 任务是评价已有 Skill 时 |
| [skill-markup-guide.md](../authoring/skill-markup-guide.md) | 强制规范 | 规定 `@工作流`、`@步骤`、元数据注释与 `@动作` 的写法 | 不负责业务流程设计 | 修改 `SKILL.md` 或 references 时 |
| [versioning-and-validation.md](../authoring/versioning-and-validation.md) | 强制规范 | 规定版本三处一致、版本历史位置与校验打包流程 | 不负责内容设计本身 | 修改后准备验证或发布时 |
| [workflow-patterns.md](../authoring/workflow-patterns.md) | 设计参考 | 提供顺序 / 条件 workflow 的写法模式 | 不负责业务边界判断 | 需要写 workflow 结构时 |
| [writing-a-good-skill.md](../authoring/writing-a-good-skill.md) | 总览参考 | 总结高质量 Skill 的常见做法与误区 | 不承担具体执行路由 | 需要整体写作建议时 |
| [naming-and-ownership.md](../authoring/naming-and-ownership.md) | 目录规范 | 区分本 Skill 与目标 Skill 的目录归属和命名 | 不负责 workflow 设计 | 需要判断文件该放哪里时 |
| [skill-evaluation-template.md](../templates/skill-evaluation-template.md) | 模板参考 | 提供结构评估报告的标准 Markdown 骨架，内含 8 维加权评分表与重构建议字段 | 不替代评测流程本身 | 需要落正式 `skill-evaluation.md` 时 |
| [skill-evaluation-checklist.md](../templates/skill-evaluation-checklist.md) | 内部清单 | 提供可量化到 8 维评分的内部复核清单，帮助正式评分前减少漏判 | 不替代正式评估报告模板 | 需要稳定 8 个维度分数时 |
| [scenario-input-template.md](../templates/scenario-input-template.md) | 模板参考 | 提供场景输入模板的固定结构 | 不负责工作流路由 | 需要新增模板文档时 |
| [eval-loop.md](../evaluation/eval-loop.md) | 专项执行 workflow 参考 | 说明评测闭环、回放、benchmark、editor 与迭代路径 | 不负责整体业务流程总览 | 需要做评测、复盘或迭代优化时 |

---

## 6. 各工作流的具体功能边界

### @步骤6: 逐个理解“能做什么 / 不能做什么”

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @依赖: step-read-supporting-reference-map -->
<!-- @验证点: 已理解主 SKILL 和两个子工作流的具体职责边界 -->
<!-- @验证方式: 能说明任一工作流适合处理什么，不适合处理什么 -->
<!-- @ID: step-understand-each-subworkflow -->

### 6.1 主 `SKILL.md` 本身

它更像“路由与编排中心”。

#### 能做什么

- 说明本 Skill 何时触发
- 给出主流程和子流程入口
- 告诉执行者何时读取哪份参考
- 保留关键规则入口和校验入口

#### 不能做什么

- 不能承载全部展开说明
- 不能替代所有 references 的细则
- 不能把理解性文档当成执行流程

### 6.2 创建流程（含前置确认）

这是“从零创建或增量完善 Skill”的默认执行路径。

#### 能做什么

- 做前置统一确认
- 判断目标 Skill 复杂度
- 规划 workflow 边界和资源结构
- 指导初始化、编辑、验证与迭代

#### 不能做什么

- 不负责已有 Skill 的完整重构策略
- 不直接替代 workflow 映射参考或版本规范本身

### 6.3 重构现有 Skill

这是“整理一个已经在用的 Skill”的专门路径。

#### 能做什么

- 盘点现有 Skill 的稳定边界
- 判断哪些内容应保留在主文档
- 指导把解释层、规则层和模板层迁移到合适位置
- 检查渐进加载是否被破坏

#### 不能做什么

- 不替代从零创建流程
- 不凭直觉跳过回归校验

### 6.4 评测已有 Skill

这是“先判断一个 Skill 当前结构质量怎么样”的专门路径。

#### 能做什么

- 盘点目标 Skill 的主文档、companion files 和验证入口
- 默认先跑 `validate`，再判断是否存在结构硬伤或是否值得进入重构
- 使用 8 个主维度分别按 `0-100` 打分，并按权重汇总总分
- 识别结构硬伤、主文档职责问题、references 分层问题与重复维护
- 产出 `skill-evaluation.md` 这类书面评估文档
- 为后续是否进入重构流程提供优先级依据

#### 不能做什么

- 不默认直接改写目标 Skill
- 不替代自动化盲测、benchmark 与回放闭环

### 6.5 评测闭环属于重要的专项执行 workflow

它不属于“创建 / 重构”的主业务链，但属于本 Skill 里非常重要的专项执行 workflow。

#### 能做什么

- 为目标 Skill 提供盲测对比、回放、benchmark、editor 和多轮迭代路径
- 把“修改后到底有没有变好”这件事变成可验证的闭环
- 为 `description`、`references/` 和脚本调整提供反馈依据

#### 不能做什么

- 不替代主 `SKILL.md` 的总路由作用
- 不定义目标 Skill 的业务边界
- 不等同于整体工作流说明文档

@提示: 因为它更偏“专项执行流程”，所以保留在 `references/evaluation/` 比放进 `references/workflows/` 更合适；但从理解层面看，它仍应被当作本 Skill 的重要 workflow 能力之一。

---

## 7. 如何理解这些文档之间的关系

### @步骤7: 把它们看成“路由层 + 规则层 + 工具层”

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @依赖: step-understand-each-subworkflow -->
<!-- @验证点: 已能用更高一层的结构理解本 Skill 的文档关系 -->
<!-- @验证方式: 能用三层视角解释主 SKILL、references 与 scripts 的关系 -->
<!-- @ID: step-understand-document-layers -->

可以把 `kz-skill-creator` 的结构理解成三层：

- **路由层**：主 `SKILL.md`，决定何时触发、走哪条流程、何时读哪份参考
- **规则层**：`references/authoring/`、`references/workflows/`、`references/evaluation/`、`references/templates/`，负责解释、规范、模板和理解文档
- **工具层**：`scripts/skill_cli.py` 和 `scripts/_impl/*`，负责初始化、校验、打包、评测等工程动作

@提示: 这份说明文档属于“规则层中的理解文档”，它帮助理解整体，不参与具体任务路由。

---

## 版本历史

- **v1.3.3** (2026-05-17) - 补齐 8 维量化 checklist 入口：在 supporting reference 映射中加入 `skill-evaluation-checklist.md`，明确其“内部复核而非正式报告”的定位
- **v1.3.2** (2026-05-17) - 补齐独立评估模板入口：在 supporting reference 映射中加入 `skill-evaluation-template.md`，避免正式评估模板继续埋在 workflow 说明里
- **v1.3.1** (2026-05-17) - 对齐评测口径：补充“评测已有 Skill”默认采用 8 维加权评分，并同步 supporting reference 映射说明
- **v1.3.0** (2026-05-17) - 对齐主文档新路由：补充“先用决策矩阵命中路径”的理解口径，并明确评测路径默认先跑 validate
- **v1.2.0** (2026-05-13) - 新增“评测已有 Skill”子工作流与对应参考文档入口，补齐结构评估路径
- **v1.1.0** (2026-05-13) - 单独强调评测闭环是重要的专项执行 workflow，并澄清其与主业务流程说明的关系
