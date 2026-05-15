---
role: Judge (T1-T5 exclusive)
reads-from: references/rubrics/intent-calibration.md
writes-to: W3 P1 子项
---

# W7 Description 深度审计

## 契约
本工作流是 T1–T5（description 三维触发、引导性、边界）的**唯一判定者**。
W3 在扫描 T 系列时必须委托本工作流，不得自行判定。
判定时使用 `intent-calibration.md` 作为示例与阈值标尺。

## 触发条件
SKILL.md 含 frontmatter 且包含 `description` 字段。

---

## 判定流程

### Step 1：三维触发扫描（T3）
对照 `intent-calibration.md` 第 1 节的三维矩阵，逐维度判定：

| 维度                 | 缺失后果                       |
| -------------------- | ------------------------------ |
| 意图 (Intent)        | P0：Agent 完全无法识别何时触发 |
| 技术特征 (Technical) | P1：可能在纯文本讨论时误触发   |
| 项目环境 (Context)   | P2：跨项目复用受阻             |

**输出**：每个缺失维度独立成一条 P 级问题，回写 W3。

### Step 2：动词与关键词扫描（T1）
- 是否动词开头？
- 是否含 ≥ 2 个意图关键词？

**输出**：未通过则一条 P0，回写 W3。

### Step 3：边界声明扫描（T2）
- 是否显式声明「不触发」场景？
- 是否声明相邻领域（容易混淆但应交给其他 Skill 的场景）？

**输出**：未通过则一条 P1，回写 W3。

### Step 4：意图内聚扫描（T4）
- description 是否描述了 ≥ 2 个互不相关的职责？
- 若是，建议拆分。

**输出**：命中则一条 P2，回写 W3，并触发拆分建议。

### Step 5：引导倾向扫描（T5）
- 描述是否过于被动（"Provides..." / "Tools for..."）？
- 是否缺少 "Make sure to use..." 类强引导话术？

**输出**：命中则一条 P2，回写 W3。

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

---

## 不输出条件
T1–T5 全部通过时，W7 不输出任何内容，W3 报告中**不出现** description 相关段落。

---

## 与其他文件的关系

| 文件                    | 关系                                                             |
| ----------------------- | ---------------------------------------------------------------- |
| `intent-calibration.md` | 提供示例与阈值标尺（R 角色）                                     |
| `trigger-test-set.md`   | 提供测试集参考，T5 命中时建议转交 skill-creator 执行触发率测试   |
| `checklist.md` T1–T5    | 本工作流的判定依据                                               |
| `W3`                    | 接收本工作流的输出                                               |
| `V0`                    | 不重叠（V0 判 description 的长度、非空与字符合法性，本工作流判语义） |
