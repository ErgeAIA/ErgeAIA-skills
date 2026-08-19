# skill-workshop

Skill 全生命周期工作站：创建 → 评审 → 重构 → 评测。

由 [skill-reviewer](https://github.com/ErgeAIA/skill-reviewer)（ErgeAIA，裁判）与 [kz-skill-creator](https://gitee.com/kingzeus/skills#kz-skill-creator)（kingzeus，构建者）整合升级而来。前者提供 9 维 48 项深度评审体系，后者提供创建/重构/评测的完整工作流与 CLI 工具链。skill-workshop 在二者基础上统一了入口、路由和验证闭环。

## 为什么需要这个 Skill？

Skill 开发常见的困境：

- **创建**：从零搭建一个结构清晰、可触发、可验证的 Skill，缺乏系统方法
- **评审**：写完了不知道质量如何，48 项检查项靠人记不住
- **重构**：结构乱了想整理，不知道先改什么、改到什么程度
- **评测**：description 改了不知道触发率有没有退化，没有回归测试

skill-workshop 把这四条路径统一到一个工作站，用决策矩阵路由，按需加载对应的工作流和判定标准。

## 四种模式

| 模式     | 做什么                                    | 产出                                |
| -------- | ----------------------------------------- | ----------------------------------- |
| **创建** | 从需求到脚手架，全流程引导                | SKILL.md + 目录结构 + 可选脚本      |
| **评审** | 9 维 48 项深度审查，发现问题定级          | 8 段结构报告（P0/P1/P2 + 整改方向） |
| **重构** | 盘点问题 → 决定强度 → 执行重整 → 回归验证 | 改进后的 SKILL.md                   |
| **评测** | eval loop + benchmark + description 优化  | 通过率统计 + 最优 description       |

另外支持独立的**合规校验**（PASS/FAIL）和**快速评分**（8 维加权）。

## 怎么用

**创建新 Skill**：
```
帮我创建一个处理 PDF 的 Skill
```

**评审已有 Skill**：
```
评审一下这个 skill：/path/to/my-skill/
帮我看看这个技能有什么问题
```

**重构**：
```
重构一下这个 skill 的结构
整理这个 skill 的 workflow 边界
```

**评测**：
```
评测这个 skill 的触发率
跑一下 benchmark
```

**CLI 工具**（无需 Agent，直接运行）：
```bash
# 快速校验
python scripts/skill_cli.py validate /path/to/skill

# 官方规范检查
python scripts/skill_cli.py spec /path/to/skill

# 仓库 Checklist 扫描
python scripts/skill_cli.py checklist /path/to/skill

# 术语一致性检查
python scripts/skill_cli.py consistency /path/to/skill

# 初始化新 Skill 脚手架
python scripts/skill_cli.py init my-skill --path ./output

# 打包为 .skill 文件
python scripts/skill_cli.py package /path/to/skill
```

## 双评估系统

| 体系           | 维度                                                                       | 适用场景                     |
| -------------- | -------------------------------------------------------------------------- | ---------------------------- |
| **9 维 48 项** | O/S/C/I/T/M/P/V/B 全覆盖                                                   | 深度评审、审计、发现问题     |
| **8 维加权**   | 目标边界/指令一致性/IO契约/工作流完整性/鲁棒性/可维护性/可验证性/Token效率 | 创建后自评、快速评估结构质量 |

两者语义不重叠，按需选择。

## 评审报告结构

评审产出 8 段固定报告：

1. **一句话结论** — 阶段判断 + 最强项 + 最大短板
2. **复杂度判断** — 轻量 / 中等 / 中等偏复杂 / 复杂
3. **主要优点** — 每条引用具体文件作为证据
4. **主要问题** — P0（阻塞）/ P1（维护风险）/ P2（演进风险）
5. **拆分需求识别** — 职责耦合分析
6. **整改方向** — 按优先级，每条标注 checklist 编号
7. **结构性问题总结** — 核心问题 + 优化方向
8. **总评** — 产品方向 + 工程化程度定级

> skill-workshop 的评审模式是**裁判**：只发现问题、定级、出报告。具体修改由创建/重构流程执行，或用户自行修改后请求复审。

### Output Path（评审报告产物路径）

| 触发方式 | 报告位置 | 说明 |
|----------|----------|------|
| 评审模式（Agent 对话） | Agent 回复内容本身 | 8 段结构报告直接呈现给用户 |
| `python scripts/skill_cli.py review <path>` | stdout（终端） | 评审报告打印到 stdout |
| `python scripts/skill_cli.py review <path> --output reports/<name>.md` | `Inbox/skill-workshop-review-<timestamp>.md` | 落盘后供团队评审 / 归档 |
| 复审（用户修改后） | 同一报告，diff 增量输出 | 评审报告里"结构性问题总结"段对两次评审的 diff |

> **避免在项目根目录创建报告**：评审报告默认走 stdout 或 `Inbox/`，不要直接落盘到 `Skill-Depot/<target>/` 污染被评审 Skill 的工作区。

## 运行时要求

- Python ≥ 3.10
- PyYAML（可选）：`consistency` 子命令加载外部规则时需要；缺失时自动降级
- 操作系统：Linux / macOS / Windows 兼容

## 文件结构

```
skill-workshop/
├── SKILL.md                    # Agent 执行入口（路由层）
├── README.md                   # 本文件（面向人）
├── VERSION.md                  # 变更历史
├── agents/                     # 评测闭环 Agent 提示词
│   ├── analyzer.md             # 解盲分析器
│   ├── comparator.md           # 盲评对比器
│   └── grader.md               # 断言评分器
├── assets/
│   ├── eval_review.html        # 评测回放页面
│   └── eval_set_editor.html    # eval set 编辑器
├── references/
│   ├── authoring/              # 创建/编写指南（10 份）
│   ├── config/                 # 外部规则配置
│   ├── evaluation/             # 评测循环文档
│   ├── rubrics/                # 判定标尺
│   │   ├── review-checklist.md # 9 维 48 项检查清单
│   │   ├── complexity-rubric.md# 复杂度标尺
│   │   ├── intent-calibration.md# 意图校准标尺
│   │   └── weighted-scoring.md # 8 维加权评分
│   ├── specs/                  # 官方规范与最佳实践
│   ├── templates/              # 报告模板与测试集模板
│   ├── examples/               # 场景输入模板（input-template-*.md + 索引）
│   └── workflows/              # 工作流定义
│       ├── C1-create.md        # 创建主链
│       ├── C2-evaluate.md      # 评测主链
│       ├── C3-refactor.md      # 重构主链
│       ├── W0-W7 + V0          # 评审主链（继承自 skill-reviewer）
│       └── skill-creator-workflow-guide.md
├── scripts/
│   ├── skill_cli.py            # 统一 CLI 入口（17 子命令）
│   └── _impl/                  # 实现模块
```

> 评测日志位于仓库根 `.darwin/results.tsv`（与 skill 平级，不在 skill 自身目录内）。

## 16 个 CLI 子命令

| 子命令               | 来源     | 功能                    |
| -------------------- | -------- | ----------------------- |
| `validate`           | creator  | 快速校验 SKILL.md 结构  |
| `spec`               | reviewer | 官方规范合规检查        |
| `checklist`          | reviewer | 仓库 Checklist 快速扫描 |
| `consistency`        | reviewer | 术语一致性检查          |
| `review`             | reviewer | 评审报告 8 段校验       |
| `init`               | creator  | 初始化 Skill 脚手架     |
| `package`            | creator  | 校验 + 打包 .skill      |
| `analyze`            | creator  | 交互式需求分析          |
| `generate-templates` | creator  | 生成场景输入模板        |
| `eval`               | creator  | 运行触发评测            |
| `loop`               | creator  | eval + improve 迭代     |
| `benchmark`          | creator  | 聚合 benchmark 统计     |
| `report`             | creator  | 生成 HTML 评测报告      |
| `improve`            | creator  | description 改进        |
| `review-playback`    | creator  | 评测回放 UI             |
| `editor`             | creator  | eval set 编辑器         |

## 致谢

本技能由两个独立项目整合升级而成，感谢原作者的贡献：

| 来源                 | 作者     | 定位                                                     | 链接                                                                         |
| -------------------- | -------- | -------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **skill-reviewer**   | ErgeAIA  | 裁判——9 维 48 项评审体系、合规校验、V1-V7 自检闭环       | [GitHub](https://github.com/ErgeAIA/ErgeAIA-skills/tree/main/skill-reviewer) |
| **kz-skill-creator** | kingzeus | 构建者——创建/重构/评测工作流、语义化标记规范、CLI 工具链 | [Gitee](https://gitee.com/kingzeus/skills#kz-skill-creator)                  |

skill-workshop 在二者基础上做了统一入口、路由合并、脚本整合和双评估体系并存，但核心评审标尺和创建工作流的设计思路分别源自上述两个项目。

## 与 SKILL.md 的分工

- **README.md**：面向人，讲价值、快速使用、文件结构、CLI 参考
- **SKILL.md**：面向 Agent 执行，讲触发路由、硬规则、工作流调度、验证闭环
- **VERSION.md**：变更历史与合并溯源
