---
name: W7-description-audit
description: description 三维触发 + 引导性 + 边界声明的深度审计工作流；T1-T5 唯一判定者；新增 Step 6 自身反模式扫描。
version: 1.1.0
<!-- @类型: 工作流 -->
<!-- @优先级: 必须 -->
trigger-when: "评审模式 description 审计阶段"
role: Judge (T1-T5 exclusive)
reads-from:
  - references/rubrics/intent-calibration.md             # T1-T5 示例与阈值标尺
  - references/specs/frontmatter-style-guide.md         # description 字符数 / 字段归属 / 渐进披露定位
  - references/authoring/progressive-disclosure-patterns.md  # description 作为 Tier 1 角色的设计原则
writes-to: W3 P1 子项
---

# W7 Description 深度审计

> **版本**: v1.1.0
> **改动**: v1.1.0 - 委派链扩 frontmatter-style-guide.md + progressive-disclosure-patterns.md；新增 Step 6 description 自身反模式扫描（6.1 内省反模式 / 6.2 角色定位反模式）

## 契约
本工作流是 T1–T5（description 三维触发、引导性、边界）的**唯一判定者**。
W3 在扫描 T 系列时必须委托本工作流，不得自行判定。
判定时使用 `intent-calibration.md` 作为示例与阈值标尺；
**同时**引用 `frontmatter-style-guide.md` 第二节（description 字段约定）、第七节（description 优先原则）做 description 自身反模式扫描；
**同时**引用 `progressive-disclosure-patterns.md` 第一节（何时下沉 / 保留在正文里的应该是触发条件 + 主工作流 + 关键决策点）做 description 角色定位反模式扫描。

## 触发条件
SKILL.md 含 frontmatter 且包含 `description` 字段。

---

## 判定流程

### @步骤1: Step 1：三维触发扫描（T3）
对照 `intent-calibration.md` 第 1 节的三维矩阵，逐维度判定：

| 维度                 | 缺失后果                       |
| -------------------- | ------------------------------ |
| 意图 (Intent)        | P0：Agent 完全无法识别何时触发 |
| 技术特征 (Technical) | P1：可能在纯文本讨论时误触发   |
| 项目环境 (Context)   | P2：跨项目复用受阻             |

**输出**：每个缺失维度独立成一条 P 级问题，回写 W3。

### @步骤2: Step 2：动词与关键词扫描（T1）
- 是否动词开头？
- 是否含 ≥ 2 个意图关键词？

**输出**：未通过则一条 P0，回写 W3。

### @步骤3: Step 3：边界声明扫描（T2）
- 是否显式声明「不触发」场景？
- 是否声明相邻领域（容易混淆但应交给其他 Skill 的场景）？

**输出**：未通过则一条 P1，回写 W3。

### @步骤4: Step 4：意图内聚扫描（T4）
- description 是否描述了 ≥ 2 个互不相关的职责？
- 若是，建议拆分。

**输出**：命中则一条 P2，回写 W3，并触发拆分建议。

### @步骤5: Step 5：引导倾向扫描（T5）
- 描述是否过于被动（"Provides..." / "Tools for..."）？
- 是否缺少 "Make sure to use..." 类强引导话术？

**输出**：命中则一条 P2，回写 W3。

### @步骤6: Step 6：description 自身反模式扫描（新增 — 来自 frontmatter-style-guide + progressive-disclosure）

**6.1 description 内省反模式**（阈值来自 `frontmatter-style-guide.md` §2、§7）：
- ❌ description 把 frontmatter `version` 字段值也写了进来（"v0.2.1"）
- ❌ description 列了 3 个以上触发短语清单（应放进 `references/config/trigger-test-set.md`）
- ❌ description 重复了 body 段标题（如 "see body §决策矩阵"）—— body 在 Tier 2 必读，写一句"详见 body"是冗余
- ❌ description 把功能描述（"做什么"）与触发条件（"何时用"）混在同一段，>200 字无断行
- ✅ 命中任一即一条 P1，回写 W3

**6.2 description 角色定位反模式**（阈值来自 `progressive-disclosure-patterns.md` §1）：
- ❌ description 内嵌"主工作流摘要"（如 "1. 抽取 2. 验证 3. 报告"）—— 应下沉到 body 流程段
- ❌ description 出现 markdown 表格 / 列表 > 3 项
- ❌ description 写 "Requires X tool" / "Not for Y" 等**工具栈 / 边界**声明—— 应放到 body `Gotchas` / `Non-Goals` 段
- ✅ 命中任一即一条 P1，回写 W3

---

## 回写 W3 的格式

每条判定结果按以下格式注入 W3 报告的对应优先级段：

```
- [T<N>] <一句话问题陈述> —— <长期后果> —— 证据：SKILL.md frontmatter / description
  优化方向：<一句话方向描述>
```

**示例**：
```
- [T3] description 缺失「技术特征」触发维度 —— 在纯文本讨论"如何写 Skill"时会误触发 —— 证据：SKILL.md frontmatter
  优化方向：在描述中加入技术锚点，明确技能适用的技术栈或工具链
```

---

## 转交 skill-creator 判定

当 T5（引导倾向）命中时，除回写 W3 外，额外输出转交建议：

```
**转交建议**：description 的触发精度建议转交 skill-creator 执行数据驱动的触发率评估。
skill-creator 可通过 scripts/run_eval.py 进行真实环境触发率测试，
并通过 scripts/run_loop.py 进行迭代优化（60/40 train/test 分割，最多5轮）。
```

当 T4（意图内聚）命中时，额外输出拆分转交建议：

```
**转交建议**：description 描述了多重职责，建议转交 skill-creator 设计拆分方案。
```

当 Step 6（description 自身反模式）命中时，额外输出：

```
**转交建议**：description 内部反模式建议转交 frontmatter-style-guide 的"description 优先"原则（§7）做字段归属重排，必要时同步重写 body 对应段。
```

---

## 不输出条件
T1–T5 全部通过且 Step 6 反模式未命中时，W7 不输出任何内容，W3 报告中**不出现** description 相关段落。

---

## 与其他文件的关系

| 文件                                    | 关系                                                             |
| --------------------------------------- | ---------------------------------------------------------------- |
| `intent-calibration.md`                 | 提供示例与阈值标尺（R 角色）                                     |
| `frontmatter-style-guide.md`            | 提供 description 自身反模式判定（§2、§7）                       |
| `progressive-disclosure-patterns.md`    | 提供 description 角色定位反模式判定（§1 何时下沉 / 保留什么）    |
| `references/config/trigger-test-set.md` | 提供测试集参考，T5 命中时建议转交 skill-creator 执行触发率测试   |
| `checklist.md` T1–T5                    | 本工作流的判定依据                                               |
| `W3`                                    | 接收本工作流的输出                                               |
| `V0`                                    | 不重叠（V0 判 description 的长度、非空与字符合法性，本工作流判语义） |

---

## 版本历史

- **v1.1.0** (2026-06-18) - 委派链扩 frontmatter-style-guide.md + progressive-disclosure-patterns.md；新增 Step 6 description 自身反模式扫描（6.1 内省反模式 / 6.2 角色定位反模式）
- **v1.0.0** (2026-06-14) - 初版：T1-T5 三维触发 / 动词 / 边界 / 内聚 / 引导倾向扫描；转交 skill-creator 触发率评估建议
