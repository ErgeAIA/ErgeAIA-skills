---
name: C3-refactor
description: 重构模式主入口；按 V0 / W1-W6 / C1 三段式重整已有 Skill 的结构与 frontmatter。强制包含内容三层分层（SKILL.md / README / references）与访问性核实门禁。
version: 1.3.0
trigger-when: "重构已有 Skill 时"
---

# C3 重构流程

> 对已有 Skill 进行结构重整的完整工作流。**强制步骤**：内容三层分层 + 访问性核实门禁。

---

## 步骤 1：问题盘点

- 先跑快速校验：

```bash
python scripts/skill_cli.py validate <skill-path>
python scripts/skill_cli.py checklist <skill-path>
```

- 或进入 W1-W7 评审主链做深度审查
- 记录所有问题，按 P0/P1/P2 分级

---

## 步骤 2：决定重构强度

| 强度 | 触发条件 | 操作范围 |
|------|---------|---------|
| 轻量修订 | 仅 P2 级问题 | 改 frontmatter、修措辞 |
| 结构重整 | 有 P1 级问题 | 移动文件、重整 references、内容分层 |
| 深度重构 | 有 P0 级问题 | 重写 SKILL.md、拆分 workflow |

> 无论哪一档，**只要涉及"把内容从 SKILL.md 移出"，就必须走步骤 3 的三层分层与步骤 4 的访问性核实**——这是技能优化的必做项，不再需要用户显式下指令。

---

## 步骤 3：执行重构（内容三层分层）

按**三层模型**决定每段内容的落点，禁止把人类可读叙述留在 SKILL.md：

| 层 | 落点 | 内容 |
|----|------|------|
| AI 专属 | `SKILL.md` | 触发条件、主工作流、强制规则、决策点、参考文档索引（指针） |
| 人类可读 | `README.md` | 技能是什么、何时用/不用、人类如何调用、设计哲学、进阶指引 |
| 按需细节 | `references/` | 长流程、模板、示例、反模式、可视化契约、各类子模板 |

操作：

1. 先判定哪些内容**只给 AI 读**（留在 SKILL.md），哪些**给人类读**（必须新建/补充 `README.md`）。
2. 把解释层、示例层、模板层下沉到 `references/`。
3. 把人类向叙述（定位、用法、哲学）移出 SKILL.md，写入 `README.md`，并在 SKILL.md 顶部或尾部加一句"人类使用说明见 README.md"的指针。
4. 移动文件后，更新 SKILL.md 中的引用——**链接、代码块内路径、正文裸路径都要同步更新**。

> 反模式：把 README 内容塞回 SKILL.md、或把本该常驻的强制规则下沉得过深。

---

## 步骤 4：访问性核实（强制门禁，不做即失败）

重构后、回归校验前，**必须**完成以下自动核实；任何一项不通过都回到步骤 3 修复：

1. **路径存在性**：抽取 SKILL.md（及所有 `.md`）中全部 `references/*.md` / `scripts/*.py` / `examples/*.md` 引用——含 Markdown 链接、代码块内路径、正文裸路径——逐一确认文件真实存在。
2. **trigger-when**：若新增了 `references/` 文件，确认其 frontmatter 含 `trigger-when`，保证下沉内容有明确加载条件、不是孤儿文件。
3. **README 存在性**：若从 SKILL.md 抽出了人类阅读内容，确认 `README.md` 已创建且被 SKILL.md 引用。

> 上述三项已由 `validate` 自动化覆盖（见 `quick_validate.py`：引用路径存在性检查 + references `trigger-when` 检查）；本步骤是"必须跑且必须 PASS"的硬门禁，不是可选清单。

---

## 步骤 5：回归验证

```bash
python scripts/skill_cli.py validate <skill-path>
```

- 确认 `validate` 返回 PASS（含步骤 4 的访问性核实）
- 确认版本三处一致（frontmatter / 头部 / 版本历史）

---

## 步骤 6：可选评审

- 重构完成后进入 W1-W7 评审主链验证改进效果
- 或使用 8 维加权评分快速评估

---

## 验证闭环

- V1：`validate` 返回 PASS（含引用路径存在性 + references trigger-when）
- V2：版本号已更新
- V3：语义化标记完整（@工作流 / @步骤N / @动作 / @验证点）
- V4：无旧术语残留（`consistency` 检查通过）
- V5（新增）：人类可读内容已剥离到 README.md，SKILL.md 仅含 AI 专属与指针
