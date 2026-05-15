---
version: 2026-05
source: anthropics-skills/skill-creator/scripts/improve_description.py
trigger-when: W7 命中 T5 时建议转交 skill-creator 执行触发率测试
role: background
---

# 触发测试集模板

> **裁判角色声明**：本文件仅供评审时参考，触发率测试的执行应转交 skill-creator。
> skill-creator 的 `scripts/run_eval.py` 和 `scripts/run_loop.py` 提供数据驱动的自动化触发率评估与迭代优化。
> 裁判只识别触发问题（T5 命中），不执行测试。

---

## 正面集（应触发该 Skill 的提示，≥ 10 条）

**格式**：每行一条真实用户语气的提示，应包含具体细节（文件路径、个人背景、公司名等）。

**示例（针对 pdf-processing Skill）​**：
```
帮我从这份 PDF 里提取表格
这个 PDF 表单怎么自动填
把这三个 PDF 合并成一个
extract text from invoice.pdf
fill in the form fields in form.pdf
合并 Q1.pdf 和 Q2.pdf
我需要从扫描版 PDF 里抠出文字
PDF 转 Excel 怎么做
帮我读取 contract.pdf 第 5 页的内容
能从这个 PDF 里把所有图片导出来吗
ok so my boss just sent me this xlsx file (its in my downloads, called something 
like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows 
the profit margin as a percentage
```

**关键要求**：
- 必须包含具体细节（文件名、路径、背景故事）
- 应覆盖正式 / casual / 带拼写错误等多种语气
- 应包含边缘案例（用户没明确说 PDF 但实际需要）
- 至少包含 2 条英文 + 2 条中文混合表达

---

## 负面集（不应触发但易混淆，≥ 5 条）

**格式**：每行一条容易被误触发的提示，附简短理由。

**示例**：
```
帮我写一份 PDF 学习指南                # 是创作内容，不是处理 PDF 文件
PDF 是什么意思                         # 是概念解释，不需要 Skill
把这份 Word 转 PDF                     # 应该触发文档转换 Skill
推荐几个 PDF 阅读器                    # 是产品推荐
PDF 文件怎么打不开                     # 是故障排查
```

**关键要求**：
- 必须是 "near-misses"（关键词相似但意图不同）
- 不能是明显无关的（如"写个斐波那契函数"对 PDF Skill 太容易）
- 应测试边界情况（相邻领域、模糊表述）

---

## 回归方法

1. 把正面集逐条作为输入，观察 Agent 是否激活该 Skill
2. 把负面集逐条作为输入，观察 Agent 是否**未**激活该 Skill
3. 任一项不符合预期 → 调整 `description` 字段并重测
4. 每次修改 description 后必须完整回归测试

---

## 阈值建议

| 指标           | 阈值      | 行动                     |
| -------------- | --------- | ------------------------ |
| 正面集命中率   | ≥ 90%     | 通过                     |
| 正面集命中率   | 70% - 90% | P1：增强意图词           |
| 正面集命中率   | < 70%     | P0：description 严重失效 |
| 负面集误触发率 | ≤ 10%     | 通过                     |
| 负面集误触发率 | 10% - 30% | P1：增强边界声明         |
| 负面集误触发率 | > 30%     | P0：触发范围严重失控     |

---

## 官方优化循环参考

Anthropic 官方使用 `scripts/run_loop.py` 自动迭代 description：

1. 60% 训练集 + 40% 测试集
2. 每次迭代运行 3 次取平均触发率
3. 调用 Claude 提出改进建议
4. 迭代最多 5 轮，选测试集得分最高的版本

本 Skill 的评审模式可手动模拟此流程：
- 训练集结果反馈给 description 修订
- 测试集用于最终验收
- 不允许在测试集上反向调参（避免 overfitting）
