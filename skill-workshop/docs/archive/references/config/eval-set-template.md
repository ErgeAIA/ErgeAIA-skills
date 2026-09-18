---
version: 2026-09
source: skill-workshop（依据 agentskills.io 官方评测协议）
trigger-when: 为目标 Skill 构建触发评测集、C2 评测迭代前
role: test-set
---

# 触发评测集模板（官方评测协议）

> 复制本文件结构生成 `eval-set.json` 后交由 `skill_cli.py eval / loop` 消费。
> 实跑需要 `claude` CLI 环境；无该环境时本模板仅作规范与干跑推演依据。

## 评测协议要点

协议六要点（20 条 / 60-40 / 跑 3 次 / ≤5 轮 / validation 选版 / 未见数据 ≥90%）**唯一真源**：[optimizing-descriptions.md §4-§7](../specs/optimizing-descriptions.md)。本文件不复制协议正文，避免双源漂移（三道审查门·门1 砍出：同规范两个正文违反 C5）。

## eval-set.json 结构（run_eval.py 消费格式）

```json
[
  { "query": "帮我评审一下这个 skill 的 SKILL.md", "should_trigger": true },
  { "query": "这段 Python 代码有 bug 帮我调试", "should_trigger": false }
]
```

字段约束：`query` 全局唯一；`should_trigger` 必须为布尔值。train/validation 划分在文件名或外部记录中维护（`run_eval.py` 不消费 split 字段）。

## 正/负样本设计维度（每条应触发查询至少覆盖一个变化维度）

- 语气：正式 / casual / 带拼写错误
- 显式度：直接提领域词 / 只描述需求不提领域词
- 详细度：简短 / 带文件路径、背景故事
- 复杂度：单步 / 嵌在更大任务链中
