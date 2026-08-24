---
name: W3-issues
description: 评审模式问题扫描阶段工作流；逐项引用 review-checklist.md 判定 P0/P1/P2；T 系列强制委托 W7；交叉核对前置找同技能规则冲突。
version: 1.2.0
<!-- @类型: 工作流 -->
<!-- @优先级: 必须 -->
trigger-when: "评审模式问题扫描阶段"
role: Workflow (Judge)
reads-from:
  - references/rubrics/review-checklist.md  # 唯一判定标准源
  - references/specs/best-practices.md      # 软性维度溯源（M/P/V/B）
  - references/specs/frontmatter-style-guide.md  # S 系列 frontmatter 过度工程化判定（S6）
  - references/authoring/versioning-and-validation.md  # S6 版本三处一致性硬校验
calls: workflows/W7-description-audit.md     # T 系列强制委托
writes-to: 报告第 4 段
---

# W3 问题扫描（P0/P1/P2）

> **版本**: v1.2.0
> **改动**: v1.2.0 - 契约补「交叉核对前置（5.3.1）」——读全部 references/scripts 找同技能规则冲突（对应 checklist C5）；三段式前置补质量杠杆第四问

## 契约

- **三段式前置**：进入逐项扫描前，必须先按 `references/rubrics/review-checklist.md`「三段式评审元框架」完成第一性锚定（第一性问题/不可违背约束/边界/质量杠杆，一句话锚定），并对可疑设计选择做双向钢人论证。锚定发现方向性错误时，无论清单命中多少项，报告第 2 段必须显式给出「方向判断：错位」。
- **交叉核对前置（5.3.1，对应 checklist C5）**：进入逐项扫描前，**必须读被评审 Skill 的全部 references/ 与 scripts/**（不只 SKILL.md 主文档），专门找同技能内规则直接打架：同一规范（引号口径、边界措辞、数字/阶段定义）在多个文件中表述不一致；SKILL.md 主文档与 references 的宣称矛盾；scripts 实际行为与 references 声明口径矛盾。判定口诀：**某个规范在 ≥2 个文件出现，就必须逐文件比对口径是否一致**。漏读 references 导致的冲突未发现 = 审查失职。
- 本工作流**不内嵌**检查项定义，逐项引用 `references/rubrics/review-checklist.md`
- T1–T5 的判定**强制委托** `W7-description-audit.md`，W3 不自行判定
- **T 系列裁决权禁令**：W3 在扫描过程中遇到任何与 description、触发意图、三维触发模型相关的问题时，**必须**停止自行判定，将问题标记为待 W7 裁决。W3 仅负责识别"T 系列可能命中"的信号，最终判定权唯一归属 W7。此约束与 SKILL.md §2 调用关系一致，但在本工作流内显式声明以确保 Agent 即使跳过 SKILL.md 也能遵守。
- M / P / V / B 维度命中时，**必须**在 `references/specs/best-practices.md` 中找到对应原则作为证据
- O / S / C / I / D 维度命中时，证据可直接落到被评审 Skill 的文件
- **S6 字段过度工程化**判定时，**必须**引用 `references/specs/frontmatter-style-guide.md` 第五、六、七节作为阈值；命中即按 frontmatter 风格指南给出整改方向
- **S6 升级为 P1 硬限**（不再标"软性建议"）：frontmatter `version / created / updated` 等元数据三处一致性（frontmatter / 头部版本块 / 文末首条版本历史）属于 V0 硬校验范畴，W3 命中即升 P1；详细阈值见 `references/authoring/versioning-and-validation.md` 第 1-3 节

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
- **D1 非破坏约束是否被强制**（仅靠 LLM 自觉 = 高风险，应有脚本/护栏兜底）

## P1 检查清单（维护风险）

- README 与 SKILL.md 是否职责重叠
- 时效性强的知识基线是否内嵌主文档
- 运行时依赖是否有「成功判定 + 失败排查 + 产物路径」闭环
- **参考文件是否有显式"何时加载"触发条件**
- **脚本错误信息是否可操作**（说出错处 + 预期 + 建议）
- **脚本是否结构化输出 + stdout/stderr 分离**
- **破坏性操作是否采用 Plan-Validate-Handoff 模式**
- **D2 价值权重是否错配**（优化堆在低弹性杠杆/借来的手段上）
- **D3 输入契约是否有缺口**（触发却缺必填输入 → 静默跳过/降级）
- **D4 是否与其他技能抢字段**（同一输出区域被多技能修改）

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

W7（description 子审计）的输出按优先级注入本段对应段（P0 → 本段 P0 清单、P1 → 本段 P1 清单、P2 → 本段 P2 清单），格式如下：

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

---

## 版本历史

- **v1.2.0** (2026-08-24) - 契约补「交叉核对前置（5.3.1）」：读全部 references/scripts 找同技能规则冲突，漏读 = 审查失职（对应 review-checklist C5）
- **v1.1.0** (2026-06-18) - 增 frontmatter-style-guide.md / versioning-and-validation.md 为 reads-from；S6 由 P2 软性建议升级为 P1 硬限（V0 硬校验范畴）
- **v1.0.0** (2026-06-14) - 初版：T1–T5 强制委托 W7；M/P/V/B 维度引用 best-practices.md 作为证据
