---
role: Workflow (Scanner)
reads-from: references/rubrics/review-checklist.md
writes-to: 报告第 3 段
trigger-when: 评审模式 W2 优点扫描阶段（W1 完成后无条件触发）
---

# W2 优点扫描

## 目标
识别被评审 Skill 中**值得保留的高阶设计**，给出 3-5 条优点，每条必须有具体证据。

## 深度观察五要素

Agent 在扫描优点时，必须优先从以下五个高阶维度寻找证据，而非泛泛而谈"设计清晰"。

### 要素 1：起源 (Origin)
- 是否源自真实任务提炼？（如 "本 Skill 提炼自 2026-04 某次生产环境数据库迁移"）
- 是否经过 execute-then-revise 迭代？（如 changelog 提及修复了某次 Agent 试错）
- 是否阅读过 Trace 并据此修订指令？

### 要素 2：渐进式披露 (Progressive Disclosure)
- `SKILL.md` 是否极简（仅承担路由职责）？
- 详细规范是否下沉到 `references/` 按需加载？
- 是否有显式的「何时加载」触发指引？

### 要素 3：控制校准 (Control Calibration)
- 是否对脆弱操作（数据库写入 / 资金交易 / 文件删除）使用了强规定（MUST / Plan-Validate-Handoff）？
- 是否对弹性任务（文案生成 / 创意输出）给出了自由度？
- 控制强度是否与风险匹配？

### 要素 4：指令模式 (Instruction Patterns)
- 是否使用 **Plan-Validate-Handoff** 模式处理破坏性操作？
- 是否有高价值的 **Gotchas** 段（环境特定的反直觉事实）？
- 是否教**方法论**而非**死指令**？
- 关键指令是否解释了 **Why** 而非单纯使用 MUST？

### 要素 5：脚本友好性 (Agentic Scripts)
- 脚本是否完全无交互（无 `input()` / TTY 阻塞）？
- 是否实现 stdout（数据）/ stderr（诊断）分离？
- 错误信息是否可操作（说出错处 + 预期 + 建议）？
- 是否考虑了输出截断（默认摘要 / `--offset` / `--output`）？

---

## 写作要求

每条优点必须遵循三段式：

> **​[现象描述]​** —— **​[为什么这能提升 Agent 性能 / 长期维护性]​** —— 参考：`<文件名>`

**示例**：
> 主文档采用纯路由结构，所有领域知识下沉到 `references/` —— 这让 Agent 在不同任务下只加载必要的上下文，节省 Token 预算 —— 参考：`SKILL.md`、`references/`

---

## 写作禁忌

- 禁止使用"设计精美"、"非常实用"、"很专业"等形容词
- 禁止抄检查清单原文
- 禁止泛泛而谈，每条必须落到具体文件
- 至少 3 条，最多 5 条
