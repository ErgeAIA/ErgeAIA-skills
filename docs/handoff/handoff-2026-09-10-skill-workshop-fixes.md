---
title: skill-workshop 待修清单与 description 最佳实践依据
type: handoff
project: ErgeAIA-skills
updated: 2026-09-10
description: >
  交给下一个在本仓库工作的会话：skill-workshop 的 3 处遗留问题（含证据文件与行号）、
  description 权威最佳实践来源链接、以及验收要求。本次只交接，不改任何技能文件。
---

# skill-workshop 待修清单

## 范围

只改 `skill-workshop/`。以下 3 项问题**均已定位到文件与节次**，可直接开工；不要顺手改其他技能。

## 待修 1 · 「description 边界声明」三处口径打架

**证据**：

- `skill-workshop/references/specs/frontmatter-style-guide.md` §9「description 字段联锁规则」把「边界：声明不适用场景（Not for: …）」标为 **⚠️ 推荐**
- `skill-workshop/references/rubrics/intent-calibration.md` §3「边界声明对照」把它列为 **正例**（`适用于：… 不适用于：…`）
- `skill-workshop/references/workflows/W7-description-audit.md` Step 6.2「description 角色定位反模式」却把「description 写 `Not for Y` 等边界声明」标为 **❌ 命中即一条 P1**，理由是「应放到 body `Gotchas` / `Non-Goals`」

**后果**：按 §9 写边界，W7 反而扣分——同一套审计链自相矛盾。

**建议方向**：以其中一个为准，另两处改为引用。倾向「边界留在 description」：官方最佳实践明确 `description` 应含「何时使用」，而负面边界是「何时**不**使用」的镜像；且 W7 6.2 若要保留「边界下沉 body」，须同时改 §9 与 intent-calibration §3，成本更高。

## 待修 2 · W7 6.1 与 §9 互斥（无法同时满足）

**证据**：`W7-description-audit.md` Step 6.1 把「description 把功能描述（做什么）与触发条件（何时用）混在同一段，**>200 字无断行**」列为反模式；而 `frontmatter-style-guide.md` §9 硬要求 **YAML 单行 string、禁用 YAML 块**。单行必然无法断行。

**建议方向**：把 6.1 该项的判据从「无断行」改为**可判定的替代判据**，例如「是否用句号分成功能句 / 触发句两段语义」（中文单行内可用「。」分段，与单行约束不冲突）。

## 待修 3 · description 应改为「以意图为主、不堆触发词」

**用户口径**：`description` 应聚焦意图，不靠穷举触发词；且当前排行榜靠前的技能描述普遍较短。

**这条已被权威来源印证**（见下节链接）：

- 社区侧四原则之一即「**聚焦用户意图，而非实现细节**」；并明确两条禁令——**不要把每一种可能的应用都列进描述**（`overly long descriptions bloat the agent's context across many skills`）、**不要把失败查询里的关键词逐条塞进描述**（原文直接称之为 overfitting）。
- 官方侧写法为「**功能句 + `Use when…` 触发句**」两段都要有，且官方正例中的关键词**嵌在 `Use when…` 句内**，不是裸词表。

**连带要改的位置**：

1. `frontmatter-style-guide.md` §9 的 **200–400 字符**自设区间 —— 官方只有 **≤1024 上限**，无建议区间；建议改为「上限 1024（硬）」+「软建议：几句话到短段落」。
2. `W7-description-audit.md` Step 6.1 的「列了 3 个以上触发短语清单」判据 —— 与 §9「**至少 3 个核心触发词**（必）」本身就有张力（3 是下限、>3 又要罚），需划清「核心触发词 vs 变体清单」的界线。
3. `intent-calibration.md` 示例库 —— 补入「意图句 vs 裸词表」的正反对照。
4. **补入官方评测协议**（本仓库当前 `trigger-test-set` 类文件只有干跑推演，**真实触发率从未复测**）：20 条评测查询（8–10 正 / 8–10 负，**负样本优先用近邻混淆项**）、60/40 train 与 validation 划分、**只用 train 的失败指导修改**、每条跑 **3 次**算触发率（should-trigger >0.5 通过 / should-not >0.5 通过）、最多迭代 **5 轮**、**按 validation 通过率挑版本而非最后一版**；产出验收判据为**未见数据通过率 ≥90%**。

## description 最佳实践来源链接

**已逐字核对全文**：

- 官方 · Skill 编写最佳实践（中文）—— <https://platform.claude.com/docs/zh-CN/agents-and-tools/agent-skills/best-practices>
  要点：`description` 硬约束**仅三条**（非空、≤1024 字符、不含 XML 标签）；**未给建议字数区间**；写法 = 功能句 + `Use when…` 触发句；**始终第三人称**；官方正例关键词嵌在句中；**全篇未提「Pushy」**（该说法非官方出处）。
- 社区 · Optimizing skill descriptions（agentskills.io 原文，本会话取到的是 implexa 增强镜像）—— <https://agentskills.io/skill-creation/optimizing-descriptions>
  镜像：<https://implexa.ai/s/agentskills/skill-creation-optimizing-descriptions>
  要点：长度「几句话到一个短段落」；四原则（祈使句式 / 聚焦用户意图 / 倾向 pushy / 简洁）；两条禁令（不列举每一种可能应用、不塞失败查询关键词）；长描述会膨胀多技能共存时的上下文；含完整 20 条评测协议。**「Pushy」的出处在这里**（原文 `Err on the side of being pushy`）。

**仅见搜索摘要、未逐字核对（可作旁证，勿当权威引用）**：

- <https://aman.ai/primers/ai/agent-skills/>
- <https://github.com/robertguss/skills-best-practices>
- <https://docingest.com/docs/agentskills.io>
- <https://tipsmake.com/how-to-optimize-skill-descriptions-mijtx>
- <https://ml-digest.com/?p=4225>

## 验收要求

- 改完跑本仓库门禁：`cd skill-workshop; python scripts/skill_cli.py spec|validate|consistency <技能目录>`（三个都须 PASS；`consistency` 查旧术语残留）。
- 若改了 description 相关判据，须同步回归 `skill-workshop` 自身与至少一个被审技能的 description，确认判定结果符合新口径、无自相矛盾。
- 本仓库**当前无单元测试**（原测试随已废弃技能 `skill-reviewer` 一并删除），故不能靠测试兜底——改动必须靠上述 CLI 门禁 + 人工交叉核对。
- **`CHANGELOG.md` 不要动**：该文件变更会触发 `.github/workflows/release.yml` 发布流程；如需记录，由用户决定。

## 卡点与已知取舍

- 三处冲突**不是笔误**，而是「评审链」与「创建/重构链」两套风格长期并存留下的口径漂移（前者裁判角色、后者构建者角色）。修的时候要一次对齐，别逐处打补丁，否则会再造新的漂移。
- 本仓库为**公开仓库**，改动不得写入私密信息：私有仓库名、本地绝对路径、私有项目名、凭据。写示例一律用泛化表述。

## 待用户拍板

1. 待修 1 的取向：边界**留在** `description`（倾向）还是**下沉** `body`？
2. 待修 3 是否连带把 §9 的 200–400 字符区间一并改掉？改会影响所有既有技能的合规判定。
3. 是否引入官方评测协议（需新建评测集与脚本），还是继续用干跑推演。
