---
version: 2026-05-r1
source: skill-reviewer V4
trigger-when: description 修改后的回归验证、触发率校准
role: test-set
---

# skill-reviewer 触发测试集

> 本文件是 skill-reviewer 自身的 V4 落地产物。
> 每次修改 `description` 字段后，必须使用本测试集完整回归验证。

---

## 正面集（应触发 skill-reviewer，12 条）

```
评审一下这个 skill，看看有什么问题
帮我审查这个技能的 SKILL.md，我需要知道它合规不合规
skill review 这个仓库，检查一下工程化程度
校验一下这个 skill 的 frontmatter 是否符合 agentskills 规范
这个 skill 有什么问题？帮我诊断一下
帮我看看这个 skill 的 description 写得好不好，触发准不准
skill audit：检查一下这个技能的质量
validate this skill against the official spec
我想重构这个 skill，先帮我评审一下现状
这个技能的 SKILL.md 超过 500 行了，帮我审查一下结构
帮我做一下 skill 的质量检查，看看工程化程度怎么样
skill 合规校验：检查 frontmatter 和目录结构是否符合规范
```

---

## 负面集（不应触发但易混淆，8 条）

```
帮我写一个新 skill，用来处理 PDF 文件                    # 是创建新 Skill，应触发 skill-creator
帮我优化这个 skill 的 description 触发率                  # 是优化触发率，应触发 skill-creator
这段 Python 代码有 bug，帮我调试一下                      # 是通用代码调试
帮我写一篇关于 Agent Skill 工程化的博客                    # 是文档创作，非评审
把这个 skill 的 SKILL.md 里的 description 改一下           # 是执行修改，应触发 skill-creator
LangChain 的 Agent 框架怎么用                              # 是框架开发，非 Skill 评审
帮我给这个 skill 加一个 scripts/validate.py               # 是具体实现，应触发 skill-creator
review 一下这个 React 组件的代码质量                        # 是通用代码审查，非 Skill 评审
```

---

## 回归方法

1. 将正面集逐条作为用户输入，观察 Agent 是否激活 skill-reviewer
2. 将负面集逐条作为用户输入，观察 Agent 是否**未**激活 skill-reviewer
3. 任一项不符合预期 → 调整 `description` 字段并重测
4. 每次修改 description 后必须完整回归

---

## 阈值

| 指标           | 阈值      | 行动                     |
| -------------- | --------- | ------------------------ |
| 正面集命中率   | ≥ 90%     | 通过                     |
| 正面集命中率   | 70% - 90% | P1：增强意图词           |
| 正面集命中率   | < 70%     | P0：description 严重失效 |
| 负面集误触发率 | ≤ 10%     | 通过                     |
| 负面集误触发率 | 10% - 30% | P1：增强边界声明         |
| 负面集误触发率 | > 30%     | P0：触发范围严重失控     |
