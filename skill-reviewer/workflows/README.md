# 工作流目录

评审流程由 9 个工作流文件组成，按调度顺序执行：

```
W0 澄清前置 ──→ W1 复杂度判定 ──→ W2 优点 ──→ W3 问题 ──→ W7 description 子审计
                                                              │
                                                              ↓
                                              W4 拆分需求识别 ←┘
                                              W5 整改方向映射
                                              W6 总评
```

| 文件 | 阶段 | 何时加载 |
|------|------|----------|
| W0-clarify.md | 澄清前置 | 用户意图不明确时 |
| W1-complexity.md | 复杂度判定 | 每次评审必经 |
| W2-strengths.md | 主要优点 | 低/中复杂度 |
| W3-issues.md | 主要问题 | 每次评审必经 |
| W4-workflow-split.md | 拆分需求识别 | W3 发现耦合时 |
| W5-recommendations.md | 整改方向映射 | W3 发现问题时 |
| W6-verdict.md | 总评 | 每次评审必经 |
| W7-description-audit.md | description 子审计 | W3 命中 T 维度时 |
| V0-validate.md | 合规校验 | 用户请求校验时 |

加载纪律：按需读取，不预加载全部文件。详见 SKILL.md §6 渐进式披露。
