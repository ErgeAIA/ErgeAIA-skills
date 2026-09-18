# skill-workshop 归档目录

本目录存放 v2 重构时从运行时迁出的历史资产，**不参与技能加载与默认工作流**。

## 结构

| 路径 | 内容 |
| --- | --- |
| `references/` | 原 52 份 references 的 workflows / rubrics / authoring / specs / templates / config / evaluation / examples 等 |
| `scripts/` | 已归档 CLI 实现（reconcile、family-diff、review_ops、eval/loop、selfheal 等） |
| `agents/` | 评测闭环 Agent 提示词（analyzer / comparator / grader） |
| `assets/` | eval 评审与编辑器 HTML |
| `docs-plans/` | （预留）历史计划类材料 |
| `test-prompts.json` | 旧触发测试提示词 |

## 原则

1. 归档件不再被 `SKILL.md` 默认路由消费；需要深度诊断时按主文档「条件触发」指引人工查阅。
2. 归档件已做步骤级 `@` 清理；若个别历史正则/史实叙述仍含 `@` 字样，仅作历史切片，不恢复为运行时契约，也不再被校验器当作通过条件。
3. 运行时权威文档仅：`references/core-method.md`、`creation.md`、`review.md`、`validation.md`。
4. 运行时 CLI 仅：`validate`、`package`、`init`、`spec`。
