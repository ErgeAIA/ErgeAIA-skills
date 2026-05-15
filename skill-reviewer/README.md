# skill-reviewer

对本地 Agent Skill 仓库进行结构化评审与合规校验。本 Skill 自身遵循 [Agent Skills 官方规范](https://agentskills.io/)。

## 为什么需要这个 Skill？

你写了一个 Skill，它能跑——但 Agent 真的能正确触发它吗？别人拿到能维护吗？

很多 Skill 停留在「一篇文档 + 几段代码片段」的阶段，常见问题包括：
- 主文档同时装规则、知识、实现，越改越乱
- 执行路径只在文档里，仓库里没有真正的脚本入口
- frontmatter 不规范，Agent 根本触发不了
- 脚本含交互式提示，Agent 执行直接挂死
- 时效性强的基线内嵌主文档，频繁过期

skill-reviewer 把这些问题显式化为 **48 项可机器校验的检查项**，产出结构化的评审报告和整改方向，而不是泛泛的建议。

## 两种模式

| 模式 | 做什么 | 产出 |
|------|--------|------|
| **评审模式** | 完整分析 Skill 的结构、触发、实现、验证 | 8 段评审报告（P0/P1/P2 分级 + 整改方向） |
| **合规校验模式** | 快速检查 frontmatter 和目录结构是否符合官方规范 | PASS / FAIL |

两种模式互斥。如果不确定该用哪个，直接说"帮我看看这个 skill"，会先走澄清流程。

## 怎么用

**评审**：告诉 Agent 你想评审一个 Skill，提供本地目录路径即可。
```
评审一下这个 skill：/path/to/my-skill/
帮我审查这个技能的 SKILL.md
```

**校验**：快速检查合规性。
```
校验一下这个 skill 是否合规：/path/to/my-skill/
```

**自检脚本**（无需 Agent，直接运行）：
```bash
# 合规校验
python scripts/validate_review.py --spec /path/to/my-skill/

# 仓库快速扫描
python scripts/validate_review.py --checklist /path/to/my-skill/

# 术语一致性检查
python scripts/validate_review.py --consistency /path/to/my-skill/

# 组合运行
python scripts/validate_review.py --spec --checklist --consistency /path/to/my-skill/
```

## 评审报告长什么样？

评审报告包含 8 个固定段落：

1. **一句话结论** — 阶段判断 + 最强项 + 最大短板
2. **复杂度判断** — 轻量 / 中等 / 中等偏复杂 / 复杂
3. **主要优点** — 每条引用具体文件作为证据
4. **主要问题** — P0（阻塞使用）/ P1（维护风险）/ P2（演进风险）
5. **拆分需求识别** — 哪些文件职责耦合需要拆分
6. **整改方向** — 按优先级排列，每条标注 checklist 编号
7. **结构性问题总结** — 当前结构的核心问题 + 优化方向
8. **总评** — 产品方向 + 工程化程度定级

> 注意：skill-reviewer 是**裁判**，只发现问题、定级、出具报告。具体修改由 skill-creator 执行，裁判不下场踢球。

## 运行时要求

- Python ≥ 3.10
- PyYAML（可选）：`--consistency` 模式加载外部规则时需要；缺失时自动降级为仅使用内置规则

## 文件结构

```
skill-reviewer/
├── SKILL.md              # 主文档（Agent 执行入口）
├── README.md             # 本文件（面向人）
├── VERSION.md            # 变更历史
├── examples/
│   └── skill-reviewer-self-review.md   # 自检样例
├── workflows/            # 评审流程定义
│   ├── W0-clarify.md     # 澄清前置
│   ├── W1-complexity.md  # 复杂度判定
│   ├── W2-strengths.md   # 优点扫描
│   ├── W3-issues.md      # 问题扫描
│   ├── W4-workflow-split.md  # 拆分需求识别
│   ├── W5-recommendations.md # 整改方向映射
│   ├── W6-verdict.md     # 总评
│   ├── W7-description-audit.md  # description 子审计
│   └── V0-validate.md    # 合规校验
├── references/           # 判定标准与规范（按需加载）
│   ├── config/           # 外部规则配置
│   ├── rubrics/          # 检查清单与标尺
│   ├── specs/            # 官方规范与最佳实践
│   └── templates/        # 报告模板与测试集模板
├── scripts/
│   └── validate_review.py    # 自校验脚本
└── tests/
    └── test_validate_review.py  # 单元测试
```

## 自我遵循

- 本 Skill 自身的 `SKILL.md` 符合官方 frontmatter 规范
- 主文档 < 500 行，详细规范全部下沉到 `references/`
- `scripts/validate_review.py` 支持 `--help`、退出码（0=PASS/1=FAIL/2=参数错误）、stdout/stderr 分离
- 可自评审：`python scripts/validate_review.py --checklist .`
- 单元测试：`python -m unittest tests.test_validate_review -v`

## 与 SKILL.md 的分工

- 本文件：面向人，讲价值、快速使用、运行时要求
- SKILL.md：面向 Agent 执行，讲触发、模式调度、契约、验证
