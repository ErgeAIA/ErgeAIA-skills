---
role: Workflow (Judge)
reads-from:
  - references/rubrics/review-checklist.md  # 唯一判定标准源
  - references/specs/best-practices.md      # 软性维度溯源（M/P/V/B）
calls: workflows/W7-description-audit.md     # T 系列强制委托
writes-to: 报告第 4 段
---

# W3 问题扫描（P0/P1/P2）

## 契约

- 本工作流**不内嵌**检查项定义，逐项引用 `references/rubrics/review-checklist.md`
- T1–T5 的判定**强制委托** `W7-description-audit.md`，W3 不自行判定
- **T 系列裁决权禁令**：W3 在扫描过程中遇到任何与 description、触发意图、三维触发模型相关的问题时，**必须**停止自行判定，将问题标记为待 W7 裁决。W3 仅负责识别"T 系列可能命中"的信号，最终判定权唯一归属 W7。此约束与 SKILL.md §2 调用关系一致，但在本工作流内显式声明以确保 Agent 即使跳过 SKILL.md 也能遵守。
- M / P / V / B 维度命中时，**必须**在 `references/specs/best-practices.md` 中找到对应原则作为证据
- O / S / C / I 维度命中时，证据可直接落到被评审 Skill 的文件

---

## 输出格式
每条遵循「问题陈述 + 长期后果 + 证据文件」三段式。

## P0 检查清单（阻塞使用）

- 主文档是否使用结构化标记
- 主文档是否承担「路由 + 知识库 + 实现」多重职责
- 描述的执行路径是否沉淀为真实脚本入口
- **​`SKILL.md` 是否含合规 frontmatter（name + description）​**
- **关键 Gotchas 是否缺失**（环境特定的反直觉事实）
- **脚本是否含交互式 `input()` / TTY 阻塞**（会让 Skill 挂死）
- **​`SKILL.md` 是否超过 500 行 / 5000 Token**

## P1 检查清单（维护风险）

- README 与 SKILL.md 是否职责重叠
- 时效性强的知识基线是否内嵌主文档
- 运行时依赖是否有「成功判定 + 失败排查 + 产物路径」闭环
- **参考文件是否有显式"何时加载"触发条件**
- **脚本错误信息是否可操作**（说出错处 + 预期 + 建议）
- **脚本是否结构化输出 + stdout/stderr 分离**
- **破坏性操作是否采用 Plan-Validate-Handoff 模式**

> **注**：description 相关的 T1–T5 判定**不在本清单**，由 W7 子审计执行，结果回写本段 P1。

## P2 检查清单（演进风险）

- 非执行性材料（创作复盘、传播稿）是否混入主执行语义
- 是否过深绑定某运行环境却未声明
- **是否有正面/负面触发测试集**
- **复杂命令是否仍以内联形式存在而未转脚本**
- **退出码是否区分失败类型**
- **是否考虑了输出截断（默认摘要 / `--offset` / `--output`）​**

## 执行轨迹原则

官方明确指出：**读 trace 不只看输出**。若用户提供了 Agent 在该 Skill 下的执行轨迹，必须额外扫描三类信号：
- 指令模糊 → Agent 多次试错
- 指令不适用 → Agent 仍照着做
- 选项太多无默认 → Agent 不一致选择

每条命中即落成对应 P0/P1 问题，证据引用 trace 片段。

> **复杂档位强制要求**：当 W1 判定为「复杂」时，本段**必须出现**，无 Trace 也需说明缺失影响。

## 子审计接入

W7（description 子审计）的输出按以下格式注入本段 P1：

```
- [T<N>] <一句话问题陈述> —— <长期后果> —— 证据：SKILL.md frontmatter
  优化方向：<一句话动作>
```

W7 全部通过时不注入。

## 规则
- 每项命中 → 落成一条问题
- 未命中 → **不写"无此问题"占位**
- 每条问题必须有至少一个文件名作为证据
- **证据优先级**：被评审 Skill 文件 > `best-practices.md` 章节 > `review-checklist.md` 编号
  - 即先指实例，再指原则，最后兜底引编号
