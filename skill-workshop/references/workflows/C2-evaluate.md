---
name: C2-evaluate
description: 评测模式主入口；用 eval-set + eval_loop 跑数据驱动的迭代优化，60/40 train/test 分割最多 5 轮。
version: 1.2.0
trigger-when: "评测已有 Skill 时"
---

# C2 评测流程

> 对已有 Skill 进行评测迭代的完整工作流。

---

## 步骤 1：准备评测集

- 准备 eval-set JSON（参考 `references/evaluation/eval-loop.md`）
- 或使用现有 eval-set

---

## 步骤 2：运行评测

```bash
python scripts/skill_cli.py eval <skill-path> --eval-set <eval-set.json>
```

- 输出每个测试用例的 PASS/FAIL 结果

---

## 步骤 3：打分

```bash
python scripts/skill_cli.py benchmark <run-dir>
```

- 聚合多轮 benchmark 统计（pass_rate / time / tokens）

---

## 步骤 4：分析改进

- 使用 agents/grader.md 逐条打分
- 使用 agents/analyzer.md 分析胜因/败因
- 使用 agents/comparator.md 做 A/B 盲比

---

## 步骤 5：迭代优化

```bash
python scripts/skill_cli.py improve <skill-path> --eval-set <eval-set.json>
```

- 自动优化 description（基于失败案例泛化，≤1024 字符）

---

## 步骤 6：闭环循环

```bash
python scripts/skill_cli.py loop <skill-path> --eval-set <eval-set.json>
```

- eval + improve 自动迭代
- 生成 HTML 报告

---

## 步骤 7：可选评审

- 评测完成后可选进入 W1-W7 评审主链做深度质量审查
- 或使用 8 维加权评分（参考 `references/rubrics/weighted-scoring.md`）快速评分

---

## 验证闭环

- V1：评测通过率 ≥ 90%
- V2：benchmark 稳定（标准差可控）
- V3：description 优化后无退化
