# skill-workshop description 口径对齐 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **本计划已获用户方向确认（4 项裁决），但执行须等用户明确指令；每个任务的 commit 步骤仅在用户逐任务批准后执行。**

**Goal:** 消除 skill-workshop 内 description 判据的 6 处自相矛盾，把 description 口径统一为「意图优先、边界留 description、触发词防堆砌」，并同步机器校验器与评测协议模板。

**Architecture:** 以 `references/specs/spec.md` §description 格式约束为唯一机器判据真源；`frontmatter-style-guide.md §9` 降级为引用式设计参考；`W7` 评审反模式与 `W5` 整改映射随真源对齐；`quick_validate.py` 校验器按新口径调整严重度分级（Pushy 保持硬、触发词 ≥3 降软、核心意图关键词 ≥2 升硬）；评测协议落模板不新增脚本。

**Tech Stack:** Python >=3.10（PEP 723 零第三方依赖）、Markdown + YAML frontmatter、PowerShell（Windows，`&&` 需替换为 `;`）。

**Spec:** 交接文档 `handoff-2026-09-10-skill-workshop-fixes.md`（临时目录，要点已固化到本计划 Global Constraints 与各任务）+ 2026-09-10 会话逐文件核对结论（`.codebuddy/memory/2026-09-10.md`）+ **2026-09-11 references 全量审查报告**（官方源已在线重新核实，新发现 5 处问题，已并入各 Task）。

## Global Constraints

- 范围：只改 `skill-workshop/` 目录 + 本计划文件；不顺手改其他技能（changelog-manager / zuiti 仅作回归对象，不改其文件）。
- **根 `CHANGELOG.md` 禁改**：该文件变更会触发 `.github/workflows/release.yml` 发布流程。
- 版本纪律：版本号强制三段式 `X.Y.Z`；`frontmatter.metadata.version` 与 `VERSION.md` 须同步（本次 1.21.x → 1.22.0）；references 文件各自 frontmatter version 同步 bump。
- 本仓库为公开仓库：示例一律泛化表述，不写私有仓库名、本地绝对路径、私有项目名、凭据。
- 脚本纪律：无 `input()`；CLI 支持 `--help`；退出码 `0=PASS, 1=FAIL, 2=ERROR`；错误写 stderr、数据写 stdout。
- commit message 遵循 Conventional Commits；**所有 commit 须用户明确批准后执行**。
- 本仓库当前无单元测试：验证靠 CLI 门禁（`spec` / `validate` / `consistency` / `checklist` / `routing-check`）+ 临时 fixture 人工核对（用后即删）。
- 已锁定的裁决（2026-09-11 用户确认）：① 边界声明留在 description；② §9 的 200–400 区间删除，改「≤1024 硬 + 软建议几句话到短段落」；③ 评测协议走低风险档（只落模板与规范，不新增脚本，实跑需 `claude` CLI 环境）；④ 「触发词 ≥3」从硬 FAIL 降为软建议，硬判据改为「≥2 个核心意图关键词」；⑤ **Pushy 不保留硬校验**（降为软建议，以最新官方最佳实践为准——用户二次确认，覆盖最初④中「Pushy 保持硬」的表述）；⑥ VERSION.md 私密信息泛化确认执行。
- **来源收敛原则（2026-09-11 审查新增）**：三源分层——官方（platform.claude.com《Skill 编写最佳实践》，已在线核实：硬约束 4 条＝非空 / ≤1024 / 无 XML 标签 / 描述功能+何时使用；**始终第三人称**；触发句式 `Use when…`；无建议字数区间；全文无 Pushy）＞ 社区（agentskills.io：祈使句 / 聚焦意图 / 宁可 pushy / 简洁 + 评测协议）＞ 本地自定义扩展（单行 string / 意图词 ≥2 / 边界推荐）。冲突以官方为准；每条规范须标注来源；**本地规范此前把社区源误标为 `role: official-spec`，须随本次修正**。
- **目标驱动原则（2026-09-11 用户指示，修订原裁决④）**：现代 AI 已内化基础写法，规范应以目标驱动而非强指引——风格类正则（Pushy 句式、触发词数量、动词开头）降为软建议/目标式判定；硬校验仅保留「有事故背书或错一次就坏」的约束（官方 4 条、单行 string、意图词 ≥2、非破坏护栏、版本一致）。判据：①目标是触发准确与非破坏，风格正则只是代理；②VERSION.md 事故记录证明单行/版本一致有真实失效史（保硬），Pushy/触发词 ≥3 无事故史（降软）；③官方「Add what the agent lacks, omit what it knows」同样适用于本技能的规范自身。

## File Structure（改动地图）

| 文件 | 动作 | 职责 |
|---|---|---|
| `skill-workshop/references/specs/claude-platform-best-practices.md` | **新建** | Anthropic 官方 best-practices 缓存（仓内此前只有社区源被误标 official-spec） |
| `skill-workshop/references/specs/spec.md` | 修改 | **机器判据唯一真源**（§description 格式约束重写 + 三层来源声明） |
| `skill-workshop/references/specs/frontmatter-style-guide.md` | 修改 | §9 降级为引用式，删孤儿 200–400 区间；§6 观察性快照收缩（Task 9） |
| `skill-workshop/references/workflows/W7-description-audit.md` | 修改 | Step 6.1 / 6.2 反模式判据修正；契约引用错位修正；T1/T3 目标式化；转交措辞 |
| `skill-workshop/references/workflows/V0-validate.md` | 修改 | 第 5 步补联锁校验描述（消除文档与 `quick_validate.py` 实现的漂移） |
| `skill-workshop/references/rubrics/intent-calibration.md` | 修改 | 新增 §8「意图句 vs 裸词表」对照 + §2 人称注记 |
| `skill-workshop/scripts/_impl/quick_validate.py` | 修改 | `validate_description_format()` 严重度分级 + `pushy_patterns` 补官方 `Use when` 句式 |
| `skill-workshop/references/config/eval-set-template.md` | 新建 | 评测集模板（JSON 结构 + 字段约束 + 协议唯一真源指针，不复制协议正文） |
| `skill-workshop/references/specs/optimizing-descriptions.md` | 修改 | §2 祈使句 vs 官方第三人称冲突注记 + §8 模板指针 |
| `skill-workshop/references/workflows/C2-evaluate.md` | 修改 | 步骤 1 补模板指针 |
| `skill-workshop/references/workflows/W5-recommendations.md` | 修改 | T5 转交措辞去旧术语 `skill-creator` |
| `skill-workshop/references/templates/trigger-test-set.md` | 修改 | frontmatter `trigger-when` 去旧术语（consistency 检不出裸 `skill-creator`，须人工清） |
| `skill-workshop/references/authoring/skill-foundations.md` | 修改 | L84 顶层 `version` → `metadata.version`（version 域口径归一） |
| `skill-workshop/references/rubrics/review-checklist.md` | 修改 | 顶部加「判级原则」（手段类不优先于目标类，Task 9） |
| `skill-workshop/SKILL.md` | 修改 | `metadata.version` → 1.22.0 |
| `skill-workshop/VERSION.md` | 修改 | 顶部新增 v1.22.0 条目；私密仓技能名泛化（Task 9，已拍板） |
| `docs/superpowers/plans/2026-09-11-skill-workshop-description-alignment.md` | 修改 | 本计划（2026-09-11 审查后更新） |

明确不改（审查结论）：`specs/best-practices.md` 与 `specs/validate.md`（与官方一致，本地扩展不进缓存文件）；`config/consistency-rules.yaml`（不加裸 `skill-creator` 规则——`anthropics-skills/skill-creator` 是真实 upstream 溯源，加规则会误伤）；`references/templates/trigger-test-set.md` 与 `references/config/trigger-test-set.md` 职责不同不重复（前者通用模板、后者本技能实例，仅前者改 frontmatter 一行）；`progressive-disclosure-patterns.md` §1 本就不含「Not for 下沉 body」规则；`examples/input-template-skill-creator-main.md` 文件名保留（溯源价值，改名断链）。

不改动但需说明：`references/templates/trigger-test-set.md` 与 `references/config/trigger-test-set.md` **不重复**（前者是通用模板，后者是 skill-workshop 自身实例），维持现状；`references/authoring/progressive-disclosure-patterns.md` §1 本就不含「Not for 下沉 body」规则，W7 6.2 引用它是张冠李戴，修正 W7 后无需改它。

---

### Task 1: spec.md 重写 §description 格式约束（立唯一真源）+ 缓存官方源

**Files:**
- Create: `skill-workshop/references/specs/claude-platform-best-practices.md`（Anthropic 官方源缓存——审查发现仓内此前只有社区源且被误标 `role: official-spec`）
- Modify: `skill-workshop/references/specs/spec.md:99-110`（§description 格式约束小节）
- Modify: `skill-workshop/references/specs/spec.md:2`（frontmatter `version: 2026-06` → `2026-09`）

**Interfaces:**
- Produces: 判据表（含来源标注：官方硬约束 / 官方要求 / 社区原则 / 本地扩展）+ 官方源缓存文件。Task 2、3、5 均以该表为引用目标。

- [ ] **Step 1: 替换 §description 格式约束小节**

现状（L99-110）为 4 行表 + 联锁参考一句。整体替换为：

```markdown
### `description` 格式约束（V0 / W7 强约束）

除官方规范的 1-1024 字符上限外，本地校验增加：

| 约束                              | 强约束? | 来源                     | 违反后影响                         |
| --------------------------------- | ------- | ------------------------ | ---------------------------------- |
| 非空、字符串                       | ✅ 必   | 官方硬约束               | V0 硬 FAIL                         |
| 不含 XML 标签（本地实现为不含 `<` `>` 字符，更严） | ✅ 必 | 官方硬约束 + 本地加强 | V0 硬 FAIL                         |
| 字符数 ≤1024                       | ✅ 必   | 官方硬约束               | V0 硬 FAIL                         |
| YAML 单行 string（**禁用 `\|` 块**） | ✅ 必   | 本地扩展（外部技能管理软件转义风险） | V0 硬 FAIL / W7 标 T1              |
| Pushy/主动触发句式（`Use when…` / `Use this skill whenever…` / `Invoke on…` / 中文主动触发句式——**含官方 `Use when` 句式**） | ⚠️ 软建议（2026-09-11 目标驱动裁决，修订原④：无事故背书的风格正则不作硬约束） | 社区原则（官方无 Pushy） | V0 warning；W7 T5 判语义质量（P2） |
| ≥2 个核心意图关键词（意图动词或显式触发词，嵌入句中） | ✅ 必   | 本地扩展                 | V0 硬 FAIL / W7 标 T1              |
| 触发词 ≥3                         | ⚠️ 软建议 | 本地扩展（降级）         | V0 warning，不 FAIL                |
| 边界声明（"Not for: ..."）         | ⚠️ 推荐 | 社区原则（防误触发的镜像） | W7 标 T2（**缺**边界才 P1）；有边界不是反模式 |
| 功能句**始终第三人称**（避免 I can / You can） | ⚠️ 官方要求（语义，非机器判定） | 官方                 | W7 T5/T1 语义判定                  |
| 描述同时含功能 + 何时使用          | ⚠️ 官方要求（语义，非机器判定） | 官方                 | W7 T3 分维判定                     |

**长度软建议**：几句话到一个短段落（社区来源）。官方未给建议字数区间，**不设 200-400 之类自设区间**。

**来源分层声明（收敛原则）**：
- **官方** = platform.claude.com《Skill 编写最佳实践》（缓存：[claude-platform-best-practices.md](claude-platform-best-practices.md)）——硬约束与人称要求以此为准。
- **社区** = agentskills.io《Optimizing skill descriptions》（缓存：[optimizing-descriptions.md](optimizing-descriptions.md)）——评测协议与「宁可 pushy」出处；本仓既有 3 个文件的 `role: official-spec` 实为社区源，随本次修正标注。
- **本地扩展** = 单行 string、Pushy 硬约束、意图词 ≥2、边界推荐——为本地工程约束，与官方/社区不冲突，保留。
- 冲突裁决：官方 > 社区 > 本地；已知冲突（社区「用祈使句」vs 官方「第三人称」）的功能句以官方为准，触发句 `Use when…` 两源兼容。

**长度软建议**：几句话到一个短段落（社区来源：agentskills.io "Optimizing skill descriptions"）。官方未给建议字数区间，**不设 200-400 之类自设区间**。

**核心触发词 vs 变体清单**：
- 合法：核心触发词**嵌入句中**（如 `Invoke on '斧正'/'fact-check'`），3-4 个以内。
- 反模式：同义触发词变体罗列 >3 个（如 `review/audit/check/inspect/examine`）；把失败评测查询里的关键词逐条塞进 description（overfitting，禁）；裸词表无意图句承载。

**角色分层**：本节是机器判据唯一真源（`scripts/_impl/quick_validate.py::validate_description_format` 按此实现）；语义质量判定归 W7（T1-T5，P 级独立分维）。

**联锁参考**：[frontmatter-style-guide.md §9](frontmatter-style-guide.md#九、description-字段联锁规则（w7-必读）) 给出"反例 vs 正例"对照。
```

- [ ] **Step 1b: 新建官方源缓存 `references/specs/claude-platform-best-practices.md`**

frontmatter：

```yaml
---
version: 2026-09
purpose: Anthropic 官方 Skill 编写最佳实践（description 相关章节缓存；全量原文可在线重取）
source: https://platform.claude.com/docs/zh-CN/agents-and-tools/agent-skills/best-practices
audience: AI agents
role: official-spec
consumed-by: W7 / spec.md / W3
trigger-when: W7 description 审计 / spec 收敛裁决 / description 写法争议时
last-fetched: 2026-09-11
last-verified: 2026-09-11 (VERIFIED — 在线逐节核对)
---
```

正文记录 description 相关要点（其余章节给源链接即可，不整页搬运）：

```markdown
# description 字段规范（Anthropic 官方）

## 硬约束（4 条）
1. 必须非空；2. 最多 1,024 字符（无建议字数区间）；3. 不能包含 XML 标签；4. 应描述 Skill 的功能以及何时使用它。每个 Skill 只有一个 description 字段。

## 写法
- 功能句 + `Use when…` 触发句（官方三正例全部如此）。
- **始终第三人称**：好例 "Processes Excel files and generates reports"；避免 "I can help you…" / "You can use this…"（描述注入系统提示，视角不一致会出问题）。
- 关键术语同时分布在功能段与触发段；描述是从 100+ 技能中做选择的唯一依据。
- 反面示例（模糊）：`Helps with documents` / `Processes data` / `Does stuff with files`。
- 全文未提 "Pushy"（该说法出自社区 agentskills.io）。
```

同步：`spec.md` 与 `optimizing-descriptions.md` 的来源声明引用此文件；两个社区缓存文件（spec.md 当前头部 `source: agentskills.io/specification` 属社区规范镜像，保留但 `role` 注记改为 `community-standard` 的事不在本次范围——仅 description 章节收敛，避免扩大化）。

- [ ] **Step 2: bump frontmatter version**

`version: 2026-06` → `version: 2026-09`。

- [ ] **Step 3: 验证**

Run: `cd "d:\Workspace\Capability Vault\Skills-Depot\ErgeAIA-skills"; python skill-workshop/scripts/skill_cli.py validate skill-workshop`
Expected: PASS（此时尚未改校验器与 §9，既有行为不变；若 description 合规 warning 文案变化属预期外，停下核查）。

- [ ] **Step 4: Commit（待用户批准）**

```bash
git add skill-workshop/references/specs/spec.md
git commit -m "docs(skill-workshop): 重写 spec.md description 格式约束为唯一判据真源"
```

---

### Task 2: frontmatter-style-guide.md §9 降级为引用式

**Files:**
- Modify: `skill-workshop/references/specs/frontmatter-style-guide.md:130-159`（§9 整节）
- Modify: `skill-workshop/references/specs/frontmatter-style-guide.md:2`（`version: 2026-05` → `2026-09`）

**Interfaces:**
- Consumes: Task 1 的判据表（引用关系，不复刻数值）。

- [ ] **Step 1: 整节替换 §9**

现状 §9（L130-159）含 5 行联锁表（200-400 区间、假引用「skill-workshop SKILL.md 软约束」）+ 反例/正例。整体替换为：

````markdown
## 九、description 字段联锁规则（引用 spec.md 真源）

> **本节自 2026-09 起为引用式**：判据唯一真源是 [spec.md §description 格式约束](spec.md#description-格式约束v0--w7-强约束)，本节不复刻数值、只给设计视角的正反对照。两者冲突时以 spec.md 为准。

| 维度 | 设计视角要点 |
| --- | --- |
| 格式 | YAML 单行 string（禁 `\|` 块）——外部技能管理软件对折叠块有转义风险 |
| 风格 | Pushy 主动触发（功能句 + `Use when…`/`Invoke on…` 触发句两段都要有） |
| 意图 | 聚焦用户意图，不堆实现细节；关键词嵌在触发句内，不做裸词表 |
| 边界 | 声明不适用场景（`Not for: …`）是 description 的合法且推荐成分——它是"何时使用"的镜像 |
| 长度 | 硬限 1024 字符；软建议几句话到一个短段落（无自设区间） |

### 反例（YAML 块 + 无边界声明 + 触发词缺失）

```yaml
description: |
  斧正 · 中文科技文本事实核查。使用触发词："斧正"/"fact-check"/"验真"/"查证"——
  加载后对粘文本/具体数字/产品版本/人物引用/出处归属 跑三步流水线（抽取→联网验证→修复建议）。
```

**违反**：YAML 块（应单行）+ 无 Pushy 句式 + 无 "Not for" 边界。

### 正例（满足全部约束）

```yaml
description: Use this skill whenever the user wants to fact-check concrete claims in Chinese tech text (numbers/dates/versions/attribution). Invoke on "斧正"/"fact-check"/"验真"/"查证". Not for style/formatting/compliance/writing.
```

**满足**：单行 string + Pushy "Use this skill whenever" + 触发词嵌入 "Invoke on" 句内 + "Not for" 边界声明；长度在软建议区间内。
````

- [ ] **Step 2: bump frontmatter version** `2026-05` → `2026-09`。

- [ ] **Step 3: 验证**

Run: `python skill-workshop/scripts/skill_cli.py validate skill-workshop`
Expected: PASS。人工核对：全文不再出现 `200-400`、`200–400`。
Run: 检索确认 `Select-String -Path "skill-workshop\references\specs\frontmatter-style-guide.md" -Pattern "200-400|200–400"`，Expected: 无输出。

- [ ] **Step 4: Commit（待用户批准）**

```bash
git add skill-workshop/references/specs/frontmatter-style-guide.md
git commit -m "docs(skill-workshop): frontmatter-style-guide §9 降级为引用式，删除自设 200-400 区间"
```

---

### Task 3: W7 Step 6 反模式判据修正 + 转交措辞

**Files:**
- Modify: `skill-workshop/references/workflows/W7-description-audit.md`
  - L4 frontmatter `version: 1.1.0` → `1.2.0`
  - L25（契约节引用错位：「第二节（description 字段约定）」→「第一节（字段分类）」）
  - L72（6.1 阈值来源注「来自 §2」→「来自 §9」——§2 是 metadata 参考，非 description 阈值）
  - L74（6.1 触发短语清单判据）
  - L76（6.1 无断行判据）
  - L82（6.2 Not for 反模式）
  - L109-112（T5 转交建议中 `skill-creator` 旧术语）
  - L149 后（版本历史追加）

**Interfaces:**
- Consumes: Task 1 判据表（6.1/6.2 新判据引用 spec.md）。
- Produces: 新 W7 口径，Task 7 的 W5 映射与 Task 10 交叉核对依赖它。

- [ ] **Step 1: 改 6.1 触发短语判据（L74）**

现状：
```
- ❌ description 列了 3 个以上触发短语清单（应放进 `references/config/trigger-test-set.md`）
```
替换为：
```
- ❌ description 罗列同义触发词变体 >3 个（如 "review/audit/check/inspect/examine"），或触发词以裸词表存在、无意图句承载——核心触发词嵌入 "Invoke on '…'" 句内（≤4 个）属合法形态（判据见 spec.md §description 格式约束「核心触发词 vs 变体清单」）
```

- [ ] **Step 2: 改 6.1 无断行判据（L76）**

现状：
```
- ❌ description 把功能描述（"做什么"）与触发条件（"何时用"）混在同一段，>200 字无断行
```
替换为：
```
- ❌ description 把功能描述（"做什么"）与触发条件（"何时用"）混在一句、无语义分段——单行 string 内应以「。」分成功能句 / 触发句两段（与单行硬约束不冲突）
```

- [ ] **Step 3: 改 6.2 Not for 反模式（L82）**

现状：
```
- ❌ description 写 "Requires X tool" / "Not for Y" 等**工具栈 / 边界**声明—— 应放到 body `Gotchas` / `Non-Goals` 段
```
替换为：
```
- ❌ description 写 "Requires X tool" 等**工具栈**声明—— 应放到 body `Gotchas` 段（注意："Not for Y" 边界声明属 description 合法且推荐成分，见 Step 3 T2 与 spec.md §description 格式约束；**不属本反模式**）
```

- [ ] **Step 3b: 修正契约节引用错位（审查新发现）**

- L25 现状：`**同时**引用 frontmatter-style-guide.md 第二节（description 字段约定）、第七节（description 优先原则）…`——实际 style-guide 第一节才是「字段分类（含 description 字段）」，第二节是「metadata 内部字段参考」。改为：`引用 frontmatter-style-guide.md 第一节（字段分类：description 字段约定）、第七节（description 优先原则）…`。
- L72 现状：`**6.1 description 内省反模式**（阈值来自 frontmatter-style-guide.md §2、§7）`——§2 无 description 阈值。改为：`（判据见 frontmatter-style-guide.md §9 与 spec.md §description 格式约束；description 优先原则见 §7）`。

- [ ] **Step 4: 转交建议去旧术语（L109-112）**

现状 T5 转交建议段中：
```
skill-creator 可通过 scripts/run_eval.py 进行真实环境触发率测试，
并通过 scripts/run_loop.py 进行迭代优化（60/40 train/test 分割，最多5轮）。
```
替换为：
```
转交本技能 C2 评测链执行：scripts/run_eval.py 进行真实环境触发率测试，
scripts/run_loop.py 进行迭代优化（60/40 train/validation 分割，最多 5 轮）。
```

- [ ] **Step 5: bump 版本 + 版本历史**

frontmatter `version: 1.1.0` → `1.2.0`；版本历史追加：
```
- **v1.2.0** (2026-09-11) - 修复与 spec.md 真源的口径矛盾：6.1「无断行」改为「功能句/触发句以「。」语义分段」（单行硬约束下原判据不可满足）；6.1 触发短语判据改为「变体罗列 >3 / 裸词表」；6.2 移除「Not for Y」边界反模式（边界属 description 合法成分，缺边界才由 T2 判 P1）；转交建议措辞去旧术语 skill-creator
```

- [ ] **Step 6: 验证**

Run: `python skill-workshop/scripts/skill_cli.py validate skill-workshop; python skill-workshop/scripts/skill_cli.py routing-check`
Expected: 双 PASS（W7 未新增文件引用）。
人工核对：W7 内不再存在「Not for Y」作为反模式的表述；`skill-creator` 在该文件 0 命中。

- [ ] **Step 7: Commit（待用户批准）**

```bash
git add skill-workshop/references/workflows/W7-description-audit.md
git commit -m "docs(skill-workshop): W7 Step 6 判据对齐 spec.md 真源，移除 Not for 边界反模式"
```

---

### Task 4: intent-calibration.md 补「意图句 vs 裸词表」对照

**Files:**
- Modify: `skill-workshop/references/rubrics/intent-calibration.md`
  - L3 `version: 2026-05` → `2026-09`
  - §2（L26-33，Pushy 风格对照）加人称注记
  - 文末（L83 `## 7. 控制校准参考` 表格之后）新增 §8

**Interfaces:**
- Produces: §8 正反例，供 W7 与 Task 9 交叉核对引用。

- [ ] **Step 1: 文末新增 §8**

```markdown
---

## 8. 意图句 vs 裸词表对照

| 类型 | 示例 |
| --- | --- |
| 裸词表（反例） | `fact-check 验真 查证 核实 斧正 事实核查 边界 校准` |
| 意图句（正例） | `Use this skill whenever the user wants to fact-check concrete claims in Chinese tech text. Invoke on "斧正"/"fact-check".` |
| 变体罗列（反例） | `Invoke on 'review'/'audit'/'check'/'inspect'/'examine'`（同义变体 >3，应收敛为核心触发词） |
| overfitting（反例） | 把失败评测查询里的关键词逐条塞进 description（社区来源明令禁止；应泛化到用户意图类别） |

**判据**：核心触发词必须由意图句承载（功能句 + Use when/Invoke on 触发句）；详见 [spec.md §description 格式约束](../specs/spec.md#description-格式约束v0--w7-强约束)「核心触发词 vs 变体清单」。
```

- [ ] **Step 2: bump frontmatter version** `2026-05` → `2026-09`。

- [ ] **Step 2b: §2 Pushy 风格对照加人称注记（审查新发现）**

在 §2 表格后追加：

```markdown
> **人称注记（2026-09 收敛）**：官方（platform.claude.com best-practices）要求 description **始终第三人称**，社区（agentskills.io）要求「用祈使句」——两者在功能句上冲突，**以官方为准**：功能句用第三人称（如 "Processes Excel files…"），触发句用 `Use when…` / `Use this skill whenever…`（祈使式条件句，两源兼容）。上表反例 `Provides tools for analyzing skills.` 的判定理由是**缺触发句**，而非「被动/非第三人称」——纯第三人称功能句只要补触发句即合法。
```

- [ ] **Step 3: 验证**

Run: `python skill-workshop/scripts/skill_cli.py validate skill-workshop`
Expected: PASS（新增引用路径 `../specs/spec.md` 真实存在；锚点拼写与 Task 1 保留的锚文本一致）。

- [ ] **Step 4: Commit（待用户批准）**

```bash
git add skill-workshop/references/rubrics/intent-calibration.md
git commit -m "docs(skill-workshop): intent-calibration 新增意图句 vs 裸词表正反对照"
```

---

### Task 5: quick_validate.py 校验器严重度分级

**Files:**
- Modify: `skill-workshop/scripts/_impl/quick_validate.py:206-271`（`validate_description_format`）
- Modify: `skill-workshop/scripts/_impl/quick_validate.py:1210-1219`（调用点）
- Modify: `skill-workshop/scripts/_impl/quick_validate.py:229-241`（`pushy_patterns` 补官方 `Use when` 句式——审查发现官方三正例均为 `Use when` 开头，当前正则表完全不含该句式，**按官方正例写的 description 会被 V0 误判 FAIL**）
- Modify: `skill-workshop/references/workflows/V0-validate.md:65-69`（第 5 步 description 检查清单与实现同步）

**Interfaces:**
- Consumes: Task 1 判据表。
- Produces: `validate_description_format(frontmatter) -> tuple[bool, str, str]`，第三元素为 `"error" | "warning"`。调用点据此分流 `append_error` / `append_warning`。

- [ ] **Step 1: 改函数签名与触发词段**

函数签名与 docstring 改为：

```python
def validate_description_format(frontmatter: dict) -> tuple[bool, str, str]:
    """V0/W7 description 联锁校验（见 spec.md §description 格式约束）。

    Returns (ok, message, severity)。severity: "error"（硬 FAIL）| "warning"（软建议）。
    """
```

文件顶部（import 区之后）新增意图关键词表：

```python
# 核心意图关键词（spec.md §description 格式约束：≥2 为硬判据）
INTENT_KEYWORDS = {
    "提取", "合并", "重构", "审计", "部署", "创建", "评审", "校验", "评测", "生成",
    "转换", "处理", "分析", "检查", "修复", "优化", "验证", "翻译", "清理", "监控",
    "create", "review", "refactor", "evaluate", "validate", "analyze", "extract",
    "merge", "convert", "process", "generate", "check", "fix", "optimize",
    "verify", "translate", "clean", "monitor", "audit", "deploy",
}
```

触发词检查段（原 L249-271）替换为：

```python
    # 核心意图关键词（≥2 为硬判据）：显式触发词（引号内）+ 意图动词命中
    quoted_tokens = re.findall(r'[""「\']([^""」\']+)[""」\']', desc)
    chinese_chars = re.findall(r"[\u4e00-\u9fff]{2,}", desc)
    stopwords = {
        "this", "skill", "use", "when", "the", "and", "for", "with", "not", "from",
        "are", "but", "any", "all", "can", "has", "have", "had", "its", "you", "your",
        "whenever", "make", "sure", "invoke", "even", "explicitly", "ask", "mentions",
        "wants", "wants", "should", "would", "could", "should", "says", "want",
    }
    english_words_raw = re.findall(r"\b[A-Za-z][A-Za-z0-9\-_]{2,}\b", desc)
    english_words = [w for w in english_words_raw if w.lower() not in stopwords]
    slash_tokens = re.findall(r"[/、,，;；]\s*([\u4e00-\u9fffA-Za-z][\u4e00-\u9fffA-Za-z0-9\-_]*)", desc)
    trigger_count = len(set(quoted_tokens + chinese_chars + english_words + slash_tokens))

    core_from_quotes = len(set(quoted_tokens))
    core_from_verbs = len(
        (set(chinese_chars) | {w.lower() for w in english_words}) & INTENT_KEYWORDS
    )
    core_intent_count = core_from_quotes + core_from_verbs

    if core_intent_count < 2:
        return False, (
            f"description 缺少核心意图关键词（找到 {core_intent_count} 个，需 ≥2）。"
            "应在句中嵌入意图动词（提取/评审/校验/create/review…）或显式触发词",
        ), "error"
    if trigger_count < 3:
        # 软建议：≥3 触发词不再是硬约束（spec.md 2026-09 口径）
        return True, (
            f"description 格式合规（{len(desc)} 字符，{trigger_count} 个触发词，"
            f"{core_intent_count} 个核心意图关键词）。触发词偏少（建议 ≥3，软建议）"
        ), "warning"

    return True, (
        f"description 格式合规（{len(desc)} 字符，{trigger_count} 个触发词，"
        f"{core_intent_count} 个核心意图关键词）"
    ), "warning"
```

注意：成功路径统一返回 `"warning"` 严重度（与现状一致——现状成功消息就是走 `append_warning` 通道的信息提示），调用点语义不变。

- [ ] **Step 1b: pushy_patterns 补官方 `Use when` 句式（审查新发现，硬冲突）**

在 `pushy_patterns` 列表英文段（`Make sure to use this skill` 之后）追加一行：

```python
        r"Use when\b",  # 官方句式（platform.claude.com best-practices 三正例均为 "Use when ..."）
```

- [ ] **Step 1c: Pushy 检查降软（2026-09-11 目标驱动裁决，修订原④）**

原 pushy 缺失分支返回 `(False, …)` 硬 FAIL，改为软建议：

```python
    if not any(re.search(p, desc, re.IGNORECASE) for p in pushy_patterns):
        # 2026-09-11 目标驱动裁决：Pushy 缺失降为软建议——官方无此要求、句式多样
        # （第三人称正例即反证），正则是触发准确率的代理指标；真目标由触发率评测承担
        return True, (
            "description 缺少主动触发句式（Use when… / Use this skill whenever… / "
            "Invoke on… / 中文主动触发句式）——建议补触发句（软建议，不阻断）"
        ), "warning"
```

同步：Task 1 判据表 Pushy 行已改 ⚠️ 软建议；Task 5 fixture 的 A 用例（无意图词）仍为硬 FAIL（意图词判据不变），B/C/D 用例不变。

- [ ] **Step 2: 改调用点（原 L1210-1219）**

现状：
```python
                # 联锁校验：YAML 单行 + Pushy 句式 + 触发词 ≥ 3
                desc_format_ok, desc_format_message = validate_description_format(frontmatter)
                if not desc_format_ok:
                    append_error(spec_errors, "spec", f"Description format: {desc_format_message}")
                else:
                    append_warning(
                        project_warnings,
                        "project",
                        f"Description format: {desc_format_message}",
                    )
```
替换为：
```python
                # 联锁校验：单行 + Pushy + ≥2 核心意图关键词（硬）；触发词 ≥3（软）
                desc_format_ok, desc_format_message, desc_severity = validate_description_format(
                    frontmatter
                )
                if not desc_format_ok or desc_severity == "error":
                    append_error(spec_errors, "spec", f"Description format: {desc_format_message}")
                else:
                    append_warning(
                        project_warnings,
                        "project",
                        f"Description format: {desc_format_message}",
                    )
```

- [ ] **Step 2b: V0-validate.md 第 5 步与实现对齐（审查新发现的文档-实现漂移）**

现状第 5 步只列 4 项机械检查，但 `quick_validate.py` 实际执行联锁校验。替换为：

```markdown
### 第 5 步：description 字段
- 官方硬校验：存在且为字符串、非空、长度 ≤ 1024、不含 `<` 或 `>` 字符（XML 标签本地加强版）
- 联锁校验（判据真源见 spec.md §description 格式约束，`quick_validate.py::validate_description_format` 实现）：
  - YAML 单行 string（含换行 → FAIL）
  - Pushy/主动触发句式（`Use when…` / `Use this skill whenever…` / `Invoke on…` / 中文主动触发句式 → 缺失 FAIL）
  - ≥2 个核心意图关键词（缺失 FAIL）
  - 触发词 ≥3（不足 → warning，不阻断）
```

- [ ] **Step 3: 临时 fixture 三态验证（用后即删）**

> **执行偏差记录（2026-09-11，fixture D 揭示）**：原「≥2 核心意图关键词」硬判据会误 FAIL 官方正例 D（`Extract text and tables... Use when...`，无引号触发词，意图动词仅 extract 1 个）——与本项目标「官方正例必须 PASS」矛盾。修正为：**硬底线 ≥1**（官方模糊反例 `Helps with documents` / `Processes data` / `Does stuff with files` 均为 0 命中，仍被拦），**<2 附软建议（建议 ≥2）**；中文按子串匹配（`校验并评测` 连续 run 可命中 校验/评测）。spec.md 表格、V0-validate.md 已同步。软建议聚合输出（不提前 return 掩盖硬错误）。

在仓库外临时目录构造最小 fixture 技能（不写入仓库）：

```powershell
$tmp = Join-Path $env:TEMP "v0-fixture"; New-Item -ItemType Directory -Force "$tmp\fx-skill" | Out-Null
# fx-skill/SKILL.md 三个版本依次写入测试：
# A(硬FAIL·无意图词):  description: Provides helper utilities for misc stuff.
# B(软PASS·触发词1个但意图词2个):  description: 校验并评测 Agent Skill。Use this skill whenever the user wants to validate a skill.
# C(全过):  description: 提取 PDF 表格并合并文件。Use this skill whenever the user works with PDFs. Invoke on "提取"/"合并"/"PDF". Not for image editing.
# D(官方正例形态·Use when):  description: Extract text and tables from PDF files. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
python skill-workshop/scripts/skill_cli.py validate "$tmp\fx-skill"
```

Expected：
- A：`Description format: ... 缺少核心意图关键词` 出现在 error 通道，validate FAIL；
- B：validate PASS，warning 通道出现「触发词偏少（建议 ≥3，软建议）」——**旧版会硬 FAIL，新版转 PASS**；
- C：PASS，无触发词 warning。
- D：PASS（Step 1b 生效——`Use when` 句式命中 Pushy 正则；**修复前该官方正例形态会 FAIL**）。
测试后：`Remove-Item -Recurse -Force $tmp`。

- [ ] **Step 3b: 意图词表自愈约定（三道审查门·钢人 D2 新增）**

意图词表是「官方 should 要求的机器化代理」，必然不完备。约定：
- 词表扩充实例登记在 `INTENT_KEYWORDS` 定义处注释（日期、技能、新增词）；
- 回归中真实技能被硬 FAIL 且用户确认意图明确时，处置顺序：**扩词表 > advisory profile 复核 > 改被审技能**；
- 同类误报累计 ≥2 次 → 触发反转阈值，意图词判据降软（进脚本柔性化计划的 profile 配置处置）。

- [ ] **Step 4: 回归既有技能**

Run: `python skill-workshop/scripts/skill_cli.py validate skill-workshop; python skill-workshop/scripts/skill_cli.py validate changelog-manager; python skill-workshop/scripts/skill_cli.py validate zuiti`
Expected: 三者均 PASS（skill-workshop 自身 description 有 6 个引号触发词，core ≥2 满足）。

- [ ] **Step 5: Commit（待用户批准）**

```bash
git add skill-workshop/scripts/_impl/quick_validate.py
git commit -m "fix(skill-workshop): description 校验器分级——触发词≥3降软建议，核心意图关键词≥2升硬判据"
```

---

### Task 6: 评测协议模板落地（低风险档，不新增脚本）

**Files:**
- Create: `skill-workshop/references/config/eval-set-template.md`
- Modify: `skill-workshop/references/specs/optimizing-descriptions.md:114-119`（§8 应用结果，补指针 + 环境声明）
- Modify: `skill-workshop/references/specs/optimizing-descriptions.md:27-33`（§2 原则——加官方第三人称冲突注记）
- Modify: `skill-workshop/references/specs/optimizing-descriptions.md:2,6`（`version: 2026-06` → `2026-09`；`role: official-spec` 注记改为 community-source——审查发现该文件是社区源而非官方）
- Modify: `skill-workshop/references/workflows/C2-evaluate.md:14-18`（步骤 1，补指针）
- Modify: `skill-workshop/references/workflows/C2-evaluate.md:4`（`version: 1.2.0` → `1.3.0`）

**Interfaces:**
- Consumes: 既有脚本 `run_eval.py` / `run_loop.py`（不改动）；CLI 子命令 `eval` / `benchmark` / `improve` / `loop`。

- [ ] **Step 1: 新建 `references/config/eval-set-template.md`**

````markdown
---
version: 2026-09
source: skill-workshop（依据 agentskills.io 官方评测协议）
trigger-when: 为目标 Skill 构建触发评测集、C2 评测迭代前
role: test-set
---

# 触发评测集模板（官方评测协议）

> 复制本文件结构生成 `eval-set.json` 后交由 `skill_cli.py eval / loop` 消费。
> 实跑需要 `claude` CLI 环境；无该环境时本模板仅作规范与干跑推演依据。

## 评测协议要点

协议六要点（20 条 / 60-40 / 跑 3 次 / ≤5 轮 / validation 选版 / 未见数据 ≥90%）**唯一真源**：[optimizing-descriptions.md §4-§7](../specs/optimizing-descriptions.md)。本文件不复制协议正文，避免双源漂移（三道审查门·门1 砍出：同规范两个正文违反 C5）。

## eval-set.json 结构（run_eval.py 消费格式）

```json
[
  { "query": "帮我评审一下这个 skill 的 SKILL.md", "should_trigger": true },
  { "query": "这段 Python 代码有 bug 帮我调试", "should_trigger": false }
]
```

字段约束：`query` 全局唯一；`should_trigger` 必须为布尔值。train/validation 划分在文件名或外部记录中维护（`run_eval.py` 不消费 split 字段）。

## 正/负样本设计维度（每条应触发查询至少覆盖一个变化维度）

- 语气：正式 / casual / 带拼写错误
- 显式度：直接提领域词 / 只描述需求不提领域词
- 详细度：简短 / 带文件路径、背景故事
- 复杂度：单步 / 嵌在更大任务链中
````

- [ ] **Step 2: optimizing-descriptions.md §8 补指针**

现状 §8（L114-119）4 行后追加一行：

```markdown
5. 评测集构建与协议细节见 [eval-set-template.md](../config/eval-set-template.md)；实跑依赖 `claude` CLI（`python scripts/skill_cli.py eval` / `loop`）。
```

同时 frontmatter `version: 2026-06` → `2026-09`。

- [ ] **Step 2b: §2 原则表加官方冲突注记（审查新发现）**

在 §2「**用祈使句**：告诉 Agent 何时行动（"Use this skill when..."），不是描述功能（"This skill does..."）」条目后追加：

```markdown
  - **官方冲突注记（2026-09 收敛）**：Anthropic 官方 best-practices 要求 description **始终第三人称**，与「用祈使句」在功能句上冲突——以官方为准：功能句用第三人称（如 "Extract text and tables from PDF files…"），触发句用 `Use when…`（祈使式条件句，等效满足本条意图）。本条「不是描述功能」的实质是**不要只写功能句而缺触发句**，并非禁止第三人称功能句。
```

并在 frontmatter `role: official-spec` 后追加一行注记：`# 来源澄清（2026-09-11）：本文为社区 agentskills.io 源，非 Anthropic 官方；官方源缓存见 claude-platform-best-practices.md`。

- [ ] **Step 3: C2-evaluate.md 步骤 1 补指针**

现状：
```markdown
## 步骤 1：准备评测集

- 准备 eval-set JSON（参考 `references/evaluation/eval-loop.md`）
- 或使用现有 eval-set
```
替换为：
```markdown
## 步骤 1：准备评测集

- 按 [eval-set-template.md](../config/eval-set-template.md) 的官方评测协议构建 eval-set JSON（20 条、60/40 train/validation、近邻混淆负样本）
- 流程细节参考 `references/evaluation/eval-loop.md`
- 或使用现有 eval-set
```
frontmatter `version: 1.2.0` → `1.3.0`。

- [ ] **Step 4: 验证**

Run: `python skill-workshop/scripts/skill_cli.py validate skill-workshop; python skill-workshop/scripts/skill_cli.py routing-check`
Expected: 双 PASS（新文件含 `trigger-when` frontmatter；两处新引用路径真实存在）。
Run: `python skill-workshop/scripts/skill_cli.py eval --help`
Expected: 正常输出（确认未破坏既有子命令）。

- [ ] **Step 5: Commit（待用户批准）**

```bash
git add skill-workshop/references/config/eval-set-template.md skill-workshop/references/specs/optimizing-descriptions.md skill-workshop/references/workflows/C2-evaluate.md
git commit -m "docs(skill-workshop): 落地官方触发评测协议模板与指针"
```

---

### Task 7: W5 映射表与旧术语清理

**Files:**
- Modify: `skill-workshop/references/workflows/W5-recommendations.md`
  - L73（T5 行旧术语 `skill-creator`）
  - L150（输出格式转交段旧术语）
  - L4 frontmatter `version: 1.3.0` → `1.4.0`
  - L17 改动行同步
- Modify: `skill-workshop/references/templates/trigger-test-set.md:6`（frontmatter `trigger-when: W7 命中 T5 时建议转交 skill-creator 执行触发率测试` → `…建议转交本技能 C2 评测链执行触发率测试`——审查发现 consistency 的 SKILL-OLD-NAME 规则只匹配 `kz-skill-creator`，裸 `skill-creator` 检不出，须人工清；同文件 L5/L13 的 `anthropics-skills/skill-creator` 是真实 upstream 溯源，**保留**）

**Interfaces:**
- Consumes: Task 3 的 W7 新口径（T2 含义不变，T5 措辞对齐）。

- [ ] **Step 1: 改 T5 行（L73）**

现状：
```
| T5       | description 需加强引导性，建议转交 skill-creator 做触发率校准 | 对抗 Agent 的 undertrigger 倾向   |
```
替换为：
```
| T5       | description 需加强引导性，建议转交本技能 C2 评测链做触发率校准 | 对抗 Agent 的 undertrigger 倾向   |
```

- [ ] **Step 2: 改输出格式转交段（L150）**

现状：
```
以下整改方向建议转交 skill-creator 执行具体优化：
- <命中编号>：<方向>（skill-creator 可提供数据驱动的触发率校准与迭代优化）
```
替换为：
```
以下整改方向建议转交本技能 C2 评测链执行具体优化：
- <命中编号>：<方向>（C2 评测链提供数据驱动的触发率校准与迭代优化）
```

- [ ] **Step 3: bump 版本** frontmatter `1.3.0` → `1.4.0`，改动行（L17）追加 `；v1.4.0 - T5 与转交段措辞去旧术语 skill-creator，对齐 C2 评测链`。

- [ ] **Step 3b: 清理 templates/trigger-test-set.md frontmatter 旧术语（审查新发现）**

L6 `trigger-when` 改为：`W7 命中 T5 时建议转交本技能 C2 评测链执行触发率测试`。同文件 L15 裁判角色声明已是「转交本技能 C2 评测链」，无需动；L5/L13 `source`/来源行为 upstream 真实溯源，保留。

- [ ] **Step 4: 验证**

Run: `python skill-workshop/scripts/skill_cli.py consistency skill-workshop`
Expected: PASS，且全仓 `skill-workshop` 范围内裸 `skill-creator`（不含 `anthropics-skills/skill-creator` / `kz-skill-creator` 溯源形态）仅剩豁免行。
Run: `Select-String -Path "skill-workshop\references\workflows\*.md","skill-workshop\references\templates\trigger-test-set.md" -Pattern "转交 skill-creator"`，Expected: 无输出。

- [ ] **Step 5: Commit（待用户批准）**

```bash
git add skill-workshop/references/workflows/W5-recommendations.md skill-workshop/references/templates/trigger-test-set.md
git commit -m "docs(skill-workshop): W5/触发测试集模板转交措辞对齐 C2 评测链，清理旧术语"
```

---

### Task 8: 版本同步与 VERSION.md

**Files:**
- Modify: `skill-workshop/SKILL.md:6`（`version: "1.21.0"` → `"1.22.0"`）
- Modify: `skill-workshop/VERSION.md`（顶部新增条目）
- Modify: `skill-workshop/references/authoring/skill-foundations.md:84`（审查发现的 version 域口径漂移：SKILL.md 至少应含 `version` → `metadata.version`，与 versioning-and-validation.md「顶层 version 非官方字段」对齐）

**Interfaces:**
- Consumes: 全部前序任务。

- [ ] **Step 1: SKILL.md metadata.version → `"1.22.0"`**

注意既有漂移：VERSION.md 顶部已有 v1.21.1（2026-08-31）条目，但 SKILL.md metadata 仍停在 `1.21.0`。本次直接落到 `1.22.0`，漂移随本次归零；不单独发 1.21.2。

- [ ] **Step 2: VERSION.md 顶部插入**

```markdown
# VERSION.md — skill-workshop

## v1.22.0 (2026-09-11) — description 口径对齐（消除 6 处自相矛盾 + 校验器分级）

### 背景
交接审查发现 description 判据在 6 处口径打架（spec.md / frontmatter-style-guide §9 / intent-calibration §3 / W7 6.2 / W5 T2 / optimizing-descriptions §3）——同一套审计链按 §9 写边界会被 W7 6.2 扣 P1；且 §9 的 200-400 字符区间引用来源（SKILL.md 软约束）不存在，属孤儿约束。用户裁决：边界留 description、删自设区间、评测协议落模板、校验器分级调整。

### 改动
- **spec.md**：§description 格式约束重写为唯一机器判据真源（≥2 核心意图关键词硬 / 触发词 ≥3 降软 / 边界缺了才 P1、有边界合法 / ≤1024 硬 + 长度软建议几句话到短段落）；新增**三层来源声明**（官方 / 社区 / 本地）与来源标注列；补 XML 标签行与第三人称行。
- **官方源缓存**：新增 `references/specs/claude-platform-best-practices.md`（platform.claude.com，2026-09-11 在线核实）——此前仓内 3 个 `role: official-spec` 文件实为社区 agentskills.io 源，属来源误标。
- **官方句式兼容**：`quick_validate.py` pushy_patterns 补 `Use when`（官方三正例句式）——修复「按官方正例写的 description 被本地 V0 误判 FAIL」的硬冲突。
- **人称收敛**：社区「用祈使句」与官方「第三人称」在功能句上冲突，以官方为准（功能句第三人称 + `Use when` 触发句）；intent-calibration §2、optimizing-descriptions §2 加冲突注记。
- **V0-validate.md** 第 5 步补联锁校验描述（消除与 `quick_validate.py` 的文档-实现漂移）。
- **W7**：契约节引用错位修正（style-guide 第二节→第一节；6.1 阈值 §2→§9）。
- **frontmatter-style-guide.md §9**：降级为引用式，删除 200-400 孤儿区间与假引用。
- **W7**：6.1「>200 字无断行」改为「功能句/触发句以「。」语义分段」（原判据在单行硬约束下不可满足）；6.1 触发短语判据改为「变体罗列 >3 / 裸词表」；6.2 移除 Not for 边界反模式；转交措辞去旧术语。
- **intent-calibration.md**：新增 §8 意图句 vs 裸词表对照。
- **quick_validate.py**：`validate_description_format` 返回 (ok, message, severity)；「触发词 ≥3」从硬 FAIL 降为 warning，硬判据改为「≥2 核心意图关键词」（显式触发词 + 意图动词命中）；Pushy 保持硬约束。Pushy 在 V0（机器硬下限）与 W7 T5（语义 P2）的分层角色在 spec.md 显式声明。
- **评测协议**：新增 `references/config/eval-set-template.md`（20 条 / 60/40 train-validation / 近邻混淆负样本 / 跑 3 次 / ≤5 轮 / 按 validation 选版 / 未见数据 ≥90%）；optimizing-descriptions 与 C2-evaluate 补指针；不新增脚本（run_eval/run_loop 已存在），实跑需 `claude` CLI。
- **W5**：T5 行与转交段旧术语 `skill-creator` → 本技能 C2 评测链。
- **目标驱动化（2026-09-11 用户指示）**：Pushy 句式硬 FAIL 降为软建议（无事故背书的风格正则不作硬约束）；W7 T1「动词开头」改意图可识别、T3 技术/环境维度降为条件要求；review-checklist 加判级原则（手段类不优先于目标类）；frontmatter-style-guide §6 观察性快照收缩；VERSION.md 私有仓技能名泛化。
- **C 档明确不做**（评审链架构收敛：三套评估并存、W0-W7 状态门重量、清单项 P 级分配）——留作后续独立架构决策，避免与本次 description 收敛混做。
- 版本归零漂移：SKILL.md metadata 1.21.0（实际 VERSION 已 1.21.1）→ 1.22.0。

### 回归
- validate：skill-workshop / changelog-manager / zuiti 三技能 PASS。
- spec / validate / consistency / checklist / routing-check 全 PASS。
- fixture 三态验证：无意图词=硬 FAIL / 触发词 1 个但意图词 2 个=软 PASS / 全过=PASS。

---
```

- [ ] **Step 2b: skill-foundations.md version 口径归一（审查发现，顺带）**

L84 现状 `- version`（SKILL.md 至少应包含清单）改为 `- metadata.version（顶层 version 非官方字段）`，与 versioning-and-validation.md §2 对齐。

- [ ] **Step 3: 验证**

Run: `python skill-workshop/scripts/skill_cli.py validate skill-workshop`
Expected: PASS（版本一致性校验通过）。

- [ ] **Step 4: Commit（待用户批准）**

```bash
git add skill-workshop/SKILL.md skill-workshop/VERSION.md skill-workshop/references/authoring/skill-foundations.md
git commit -m "chore(skill-workshop): 版本 1.22.0，记录 description 口径对齐与官方源收敛"
```

---

### Task 9: 旧规范清理与目标驱动化（2026-09-11 审查新增）

> 依据：用户指示「AI 已进步很多，应目标驱动而非强指引」。判据与分档论证见会话审查报告；本任务只做 A 档（直接清理）与 B 档降级中尚未落地的部分，C 档（评审链架构收敛）明确不做。

**Files:**
- Modify: `skill-workshop/VERSION.md`（私密信息泛化——🔴 待拍板：改写历史条目）
- Modify: `skill-workshop/references/specs/frontmatter-style-guide.md`（删 §6「热门 Skills 常见模式」，结论一句话并入 §7）
- Modify: `skill-workshop/references/workflows/W7-description-audit.md`（Step 2 T1「动词开头」目标式化；Step 1 T3 技术特征/环境维度降为条件要求）
- Modify: `skill-workshop/references/rubrics/review-checklist.md`（顶部加判级原则一句话）

**Interfaces:**
- Consumes: Task 1（来源分层）、Task 5（Pushy 降软）已确立的目标驱动口径。
- Produces: 清理后的规范文本；Task 10 门禁在其后运行。

- [ ] **Step 1: VERSION.md 私密信息泛化（已拍板：执行）**

VERSION.md 中 `erg-private`、`zhile`、`baimiao`、`paizi`、`huiyi`、`fuzheng`、`suoyin`、`xhs-style`、`zhubi`、`斧正` 等私有仓库名 / 私有技能名，统一替换为「私有仓技能（略）」式泛化表述，保留版本号与行为描述的事实内容。
**已确认（2026-09-11）**：执行泛化；历史精确度让位于公开仓合规（AGENTS.md 红线），版本号与行为事实保留。
**审查门补充（对抗式 R1/R2）**：① 逐条人工编辑 + git diff 复核，**禁用批量替换**（「斧正」等词兼任普通词，sed 会误伤叙述语义）；② HEAD 脱敏 ≠ 信息从 git 历史消失——不重写历史（红线操作），脱敏口径为「当前版本不含私密信息」，并在泛化完成处加注「早期历史条目含私有名称，以当前 HEAD 为准」。

- [ ] **Step 2: 删 frontmatter-style-guide §6**

删除 `## 六、热门 Skills 常见模式` 整节（观察性快照，数据会过期且非可执行规范），其结论并入 §7 设计原则第 1 条后：`观察：大部分热门技能的 frontmatter 不超过 5 个字段——先问必要性即可覆盖`。原 §7/§8/§9 编号顺延（§9 变 §8 时须同步 spec.md / V0-validate 等处的锚点引用——**更稳妥的替代：保留节编号，节内替换为一段话**。默认采用替代方案：§6 原地缩为 2 行观察，不引发锚点连锁）。

- [ ] **Step 3: W7 强指引降级（T1/T3）**

- Step 2（T1）现状：`- 是否动词开头？` `- 是否含 ≥ 2 个意图关键词？`。改为：`- 意图是否可识别（官方要求"描述功能 + 何时使用"；动词开头是常见形态而非必要条件——第三人称功能句同样合法）` `- 是否含 ≥ 2 个意图关键词（保留，与 V0 硬判据一致）`。
- Step 1（T3）三维矩阵表格后加一行：`> 降级说明（2026-09-11 目标驱动）：技术特征 / 项目环境维度仅在存在近邻技能竞争（易误触发到相邻技能）时才有判级价值；无竞争场景不因缺失而扣分，官方仅要求功能 + 何时使用 + 关键术语。`

- [ ] **Step 4: review-checklist 加判级原则**

在「编号体系」小节后追加：

```markdown
**判级原则（2026-09-11 目标驱动）**：本清单是发现工具，不是扣分竞赛。手段类检查项（风格 / 格式 / 标记形态）不得优先于目标类检查项（触发准确、非破坏、上下文成本、方向正确）；现代 Agent 已内化的基础写法不再因形态偏差而报 P 级，除非有证据表明会引发真实失效。
```

- [ ] **Step 5: 验证**

Run: `python skill-workshop/scripts/skill_cli.py validate skill-workshop; python skill-workshop/scripts/skill_cli.py consistency skill-workshop; python skill-workshop/scripts/skill_cli.py routing-check`
Expected: 全 PASS（无新增/删除引用文件，无旧术语新增）。
Run: `Select-String -Path "skill-workshop\VERSION.md" -Pattern "erg-private|zhile|fuzheng|baimiao|paizi|huiyi|suoyin|xhs-style|zhubi|斧正"`，Expected: 无输出。

- [ ] **Step 6: Commit（待用户批准）**

```bash
git add skill-workshop
git commit -m "docs(skill-workshop): 旧规范清理与目标驱动化（私密信息泛化/观察性快照收缩/T1T3降级/判级原则）"
```

---

### Task 10: 全量门禁 + 交叉核对验收

**Files:** 无新改动（验收任务；发现问题回对应任务修复后重跑）。

- [ ] **Step 1: 五项门禁**

```powershell
python skill-workshop/scripts/skill_cli.py spec skill-workshop
python skill-workshop/scripts/skill_cli.py validate skill-workshop
python skill-workshop/scripts/skill_cli.py consistency skill-workshop
python skill-workshop/scripts/skill_cli.py checklist skill-workshop
python skill-workshop/scripts/skill_cli.py routing-check
```
Expected: 全部 PASS（checklist 历史基线为 PASS；若出现新 FAIL，定位到对应任务回改）。

- [ ] **Step 2: 交叉回归被审技能**

```powershell
python skill-workshop/scripts/skill_cli.py validate changelog-manager
python skill-workshop/scripts/skill_cli.py validate zuiti
```
Expected: 双 PASS（zuiti 纯中文 242 字符，v1.21.1 起已过 Pushy 中文句式；新意图关键词判据需复核其 description 含 ≥2 意图词/触发词，不满足则属真实口径变化，报告用户裁决，不擅自改 zuiti）。

- [ ] **Step 3: W7 口径人工交叉核对（关键）**

对 skill-workshop 自身 description 逐条走新 W7：
- T2：含 `Not for: 通用代码调试…` → 有边界，不命中（旧口径会命中 6.2 P1——本次修复目标，确认已消除）。
- 6.1 变体判据：6 个引号触发词嵌入 `Invoke on` 句内 ≤ 变体阈值语义 → 不命中（引号词为核心触发词而非同义变体）。
- 6.1 语义分段：功能句（`Skill 质量工作站：…`）与触发句（`Use this skill whenever…`）以「。」分段 → 不命中。
- 6.2 工具栈：description 无 `Requires X` → 不命中。
结论须为「W7 不输出任何内容」；若仍输出，回 Task 3 修判据。

- [ ] **Step 4: 清理与收尾**

- 确认 Task 5 的 `$env:TEMP\v0-fixture` 已删除。
- 确认工作区无本计划外的未跟踪文件（`git status`）。
- **根 `CHANGELOG.md` 0 diff**（`git diff --stat CHANGELOG.md` 无输出）。

- [ ] **Step 5: 最终 Commit（如验收中有回改，待用户批准）**

```bash
git add -A skill-workshop
git commit -m "fix(skill-workshop): 验收回改（description 口径对齐收尾）"
```

---

## 待审查项（用户复核后可调整，均给出了默认取向）

1. **旧术语清理范围**：Task 7 只清 `references/workflows/*.md` 正文中的 `skill-creator`；README 溯源行与 naming-and-ownership 属豁免不动。默认：同意则按计划执行。
2. **skill-workshop 自身 description 是否重写**：新口径下现有 description（367 字符、6 个引号触发词）合规，默认**不动**；若你希望按「意图优先、更短」进一步精简（对标官方正例风格），需单独裁决后再加任务。
3. **zuiti 回归风险**：新「≥2 核心意图关键词」硬判据若 zuiti 不满足，会从 PASS 变 FAIL。默认：如实报告，由你裁决是改 zuiti 还是调判据；本计划不包含改 zuiti 的任务。
4. **eval-set 模板落点**：放在 `references/config/`（与 trigger-test-set 实例同目录）。若你倾向 `references/evaluation/`，移动即可，不影响其他任务。
5. **计划文件入库**：本计划位于 `docs/superpowers/plans/`，默认随实现提交入库留痕；若你只想本地留存，执行时把计划文件加入 `.gitignore` 或不 add。
6. **（2026-09-11 审查新增）社区源的 role 标注范围**：本轮只把 `optimizing-descriptions.md` 的 `role: official-spec` 加来源澄清注记，`spec.md` / `best-practices.md` / `validate.md` 的 `role: official-spec`（实为社区 agentskills.io 镜像）暂不批量改名——改动面大且这三个文件的镜像性质已在头部声明。若你希望全部改为 `community-standard` 并把 `official-spec` 专属保留给 `claude-platform-best-practices.md`，需扩 Task 1（默认：不做，仅注记）。
7. **（2026-09-11 审查新增）官方源缓存范围**：`claude-platform-best-practices.md` 只缓存 description 相关章节 + 源链接，不整页搬运（避免过期缓存面积过大）。默认：同意；若你希望整页缓存，扩 Task 1 Step 1b。
8. **（已拍板 2026-09-11）VERSION.md 私密信息泛化**：确认执行（Task 9 Step 1），历史条目按「版本号与行为事实保留、私有名称泛化」处理。
9. **（已拍板 2026-09-11）Pushy 不保留硬校验**：确认降为软 warning，以最新官方最佳实践为准（Task 1 表格 / Task 5 Step 1c 按此执行，无回退路径）。
10. **C 档（评审链架构收敛）本次不做**：三套评估并存、W0-W7 状态门流程重量、清单项 P 级分配——属于独立架构决策，建议 description 收敛落地并回归后单独立项。
