# VERSION.md — skill-workshop

## v1.18.0 (2026-08-22)

### 三段式评审元框架注入 + 冗余文档清理

> **问题来源**：用户实战审查（zhubi/suoyin）发现清单式评审只能发现格式与结构缺陷，发现不了"方向错误的技能"（如 frontmatter 全合规但以过程式指导为主、违背结果导向的第一性设计）。裁判缺第一性原理/双向钢人论证/对抗式审查三种高阶思维，则产出的评审结论不配做判定依据。

- **A 三段式评审元框架**：`review-checklist.md` 使用契约后新增「三段式评审元框架」——W2/W3 逐项扫描前必须先做①第一性锚定（第一性问题/不可违背约束/边界，一句话锚定）→②可疑设计双向钢人论证→③对抗式审查（D 系列）。锚定产出「方向判断：错位」时优先于清单问题。
- **B 新增 D 设计对抗维度**（D1-D4，对抗式审查固化）：D1 非破坏约束是否被强制（仅靠 LLM 自觉=P0）/ D2 价值权重是否错配 / D3 输入契约是否有缺口 / D4 是否与其他技能抢字段。体系从 9 维 48 项扩为 **10 维 52 项**，SKILL.md §6 与 README 双评估表同步口径。
- **C 报告模板升级**：`evaluation-template.md` §2 新增「第一性结论」（方向判断：对齐/错位，错位时方向性修正优先）；§5 显式扫描四类扩为六类（加 D 系列四坑 + 方向性错误）。
- **D W2/W3/W5 联动**：W2 优点须是对第一性约束的正向贡献（钢人确认后才写入）；W3 契约加三段式前置 + P0/P1 清单加 D 系列条目；W5 生成规则加"方向性整改须附 FOR/AGAINST 钢人提炼"，映射表加 D 类四行。
- **E 冗余文档删除**（5 文件，git 可回滚）：`templates/skill-evaluation-template.md` 与 `templates/output-template.md`（v1.1 已宣布废弃的兼容残渣）、`workflows/skill-creator-workflow-guide.md`（217 行面向人总览，与 README 职责重复）、`authoring/writing-a-good-skill.md`（179 行通识方法论，与官方 specs/best-practices.md 重复）、`templates/skill-evaluation-checklist.md`（换算规则并入 `rubrics/weighted-scoring.md`「评分前复核」节）。
- **F 过期术语与引用修复**：`templates/trigger-test-set.md` 的"转交 skill-creator"改为"转交本技能 C2 评测链"（skill-creator 已合并进本技能）；routing-table/README/naming-and-ownership/eval-loop/skill-evaluation-workflow 全部悬挂引用清除。
- **G SKILL.md 硬规则新增**：三段式元框架条目（含 Why：清单式扫描发现不了方向错误的技能）。
- **H 深度瘦身（LLM 已掌握/冗余内容清除，共约 210 行）**：`skill-markup-guide.md` §10 完整 Dash 示例（5 步 120 行）压缩为最小可用示例（2 步，仅示范必填标记形态，280→213 行）；`business-to-workflow-mapping.md` 删 9 个 @步骤 HTML 注释块 + §2 集中确认压缩为一段 + §4 复杂度判断门改为复用 complexity-rubric（消除与 W1 标尺的重复，187→110 行）；`eval-loop.md` 与 `skill-evaluation-workflow.md` 批量清除独立 HTML 注释行（共 121 行）。保留所有非显然知识（三层边界/映射表字段/决策矩阵衔接条件/评测断言设计）。
- 版本同步：SKILL.md metadata.version 1.17.0 → 1.18.0。

---

## v1.17.0 (2026-08-19)

### 版本号统一三段式 + 版本规范固化

- 全 erge-private 技能版本号统一三段式（X.Y → X.Y.0），涉及本技能（1.16 → 1.16.0）与 prompt-workshop / qiao / yibi / memory-restore，共 34 处；复扫 0 残留。
- `versioning-and-validation.md` §1 显式固化「版本号强制三段式 X.Y.Z，禁止两段式 v1.1」，并修复其 frontmatter/头部版本漂移（升至 1.18.0）。
- 本技能版本 1.16.0 → 1.17.0（references 变更同步）。
- 分发链路约定（2026-08-19 用户明确）：AI 只保证 erge-private 最新，`~/.workbuddy/skills` / `~/.agents/skills` 软连接由用户工具链管理，AI 不碰（作废 v1.16.0 段的"分发修复待办"）。

---

## v1.16.0 (2026-08-19)

### 优化流程固化「内容三层分层 + 访问性核实」

> **问题来源**：用户反馈内容分层（人类可读→README、AI 专属→SKILL.md、按需→references）与访问性核实是技能优化的必做项，但 skill-workshop 的重构流程只把它们当成"模式/手工清单"，未固化为强制门禁，导致每次都要显式下指令；且 `validate` 的链接检查只覆盖 Markdown 链接语法、漏掉代码块/裸路径引用。

- **A 内容三层分层（强制）**：`C3-refactor.md` 步骤 3 改为三层模型（AI 专属 SKILL.md / 人类可读 README / 按需 references），明确人类可读内容禁止留在 SKILL.md；新增步骤 4「访问性核实（强制门禁）」含路径存在性 + references trigger-when + README 存在性。
- **B 重构指引强化**：`skill-refactoring-workflow.md` §4 重构顺序加入 README 层与三层模型；§5/§6 把访问性核实列为强制项（非可选清单），并说明 `validate` 已自动覆盖。
- **C 渐进披露补 README 层**：`progressive-disclosure-patterns.md` §1 改为三层落点（含 README），§4 验收标准强化为「所有引用路径（含代码块/裸路径）真实存在 + 新增 references 带 trigger-when」。
- **D validate 治本（quick_validate.py）**：新增 `validate_referenced_asset_paths`（引用路径存在性，覆盖代码块/裸路径，根相对解析→硬错误）与 `validate_reference_trigger_when`（references 缺 trigger-when→警告），并在 `validate_skill()` 接线。
- **版本一致性**：SKILL.md frontmatter `1.15 → 1.16`；`C3-refactor.md` `1.2.0 → 1.3.0`；`skill-refactoring-workflow.md` `1.1.1 → 1.2.0`；`progressive-disclosure-patterns.md` `1.8.0 → 1.9.0`。
- **待办（用户决策）**：erge-private 副本当前未挂到运行态（junction 指向旧公共库 `.agents` 版），分发修复稍后单独处理。

---

## v1.15.0 (2026-06-26)

### Darwin 自动化优化（9 维 48 项评审 + 3 轮迭代）

> **问题来源**：用 darwin-skill 跑 9 维加权评估，基线分 68.0（最低项 dim3 失败模式编码 4/10、dim4 检查点设计 3/10）。

- **R1 dim3 失败模式编码（4 → 8）**：新增 `## 3. 失败模式编码（if-then 三段式）` 章节，10 条 fallback 表覆盖路由/路径冲突/V0 报错/results.tsv 损坏/subagent 不可用/体积膨胀/test-prompts 复用等真实场景
- **R1 HL-3 联动**（关联簇效应）：dim4 检查点设计 3 → 5（🔴 CHECKPOINT ×2 + 🛑 STOP ×1）；dim9 反例黑名单 8 → 9（失败模式表本身扩展反例清单）
- **R2 dim5 可执行具体性（6 → 8）**：3 处软化措辞改动作短语——`@目的` "指导创建…" → "创建…"；`@场景` "用户需要…" → "用户要…"；P-V-H 硬规则"强制适用" → "强制使用"
- **R3 dim4 检查点设计（5 → 6）**：决策矩阵路由表后加 1 处 🔴 CHECKPOINT（"路由决策前必须把待选 workflow 展示给用户确认"），HL-4 触顶信号触发（Δ=+0.6 < 2），见好就收
- **P2 runtime 修复**：`scripts/_impl/improve_description.py:57` 写死 "Claude Code skill" 改为 "Agent Skill"，避免输出风格被运行时平台锁死
- **R0 既有 broken link 修复**：恢复 `references/specs/optimizing-descriptions.md`（baseline 缺失，R0-R3 误判 PASS；恢复后 V0 真实 PASS）
- **VERSION 一致性**：SKILL.md frontmatter `version: "1.14" → "1.15"`（同步 v1.15 段）

### 评价指标

| 维度         | 权重 | R0  | R3  | Δ   | 主要改动                                 |
| ------------ | ---- | --- | --- | --- | ---------------------------------------- |
| dim1 Frontmatter | 7  | 9   | 9   | -   | 已接近顶                                |
| dim2 工作流清晰度 | 12 | 9   | 9   | -   | 已接近顶                                |
| dim3 失败模式编码 | 12 | 4   | 8   | +4  | R1 if-then 三段式 10 条 fallback       |
| dim4 检查点设计   | 6  | 3   | 6   | +3  | R1 联动 +2 + R3 决策矩阵守关 +1        |
| dim5 可执行具体性 | 17 | 6   | 8   | +2  | R2 软化措辞清零（17 分档见效最大）     |
| dim6 资源整合度   | 4  | 9   | 9   | -   | 未改                                    |
| dim7 整体架构     | 12 | 8   | 8   | -   | 无花叔禁用词                            |
| dim8 实测表现     | 23 | 7   | 7   | -   | dry_run 限制（需 subagent 才能 full_test）|
| dim9 反例与黑名单 | 6  | 8   | 9   | +1  | R1 联动                                  |
| **总分**          |100 |**68.0**|**78.6**|**+10.6**| 3 轮 R1-R3，无回滚                     |

### 设计决策

| # | 决策                       | 选择                                                         | 备选                                       |
|---|----------------------------|--------------------------------------------------------------|--------------------------------------------|
| 1 | 优化目标优先级             | HL-3 关联簇优先（修 dim3 触发 dim4/dim9 联动）              | 独立维度优先（无杠杆）                     |
| 2 | R3 触顶信号处理            | Δ=+0.6 < 2，break 进 Phase 3                                | 继续堆砌 🔴 标记（违反反例 #3 "为凑分增冗余"） |
| 3 | results.tsv 存储位置       | `.darwin/results.tsv`（darwin 流程产物，独立于 skill）       | 放在 skill 自身目录（污染 skill 工作区）   |

### 经验教训

- **R0 baseline 校验误判**：之前认为"passed with warnings" = PASS，实际 V0 报 "validation failed"（broken link）。教训：必须看完整 output，warnings ≠ pass。
- **dim5 17 分档是 9 维中权重最大**：软化措辞看似"无关紧要"，实则撬动空间最大。R2 改 3 处换 +3.4 分，远超 R3 单点改动。
- **HL-3 关联簇验证**：理论预期"R1 改 dim3 触发 dim4/dim9 联动"在实操中得到验证（+2/+1），可复用于其他 skills 优化。

---

## v1.13.0 (2026-06-19)

### 自审查整改（P0-P3 全量执行）

> **问题来源**：skill-workshop 自审查（W1-W7 全流程），发现自身存在硬规则与 V0 校验器行为不一致、路径解析 bug、frontmatter 冗余字段等问题。

- **P0-1** 硬规则 #6 改写："版本三处一致" → "frontmatter.metadata.version 必填；头部版本块和版本历史 section 可选（VERSION.md 存在时 V0 不强校验）"
- **P0-2** `quick_validate.py` L1058 路径解析 bug：`skill_path.name` → `skill_path.resolve().name`，修复 `validate .` 在 Skill 子目录内运行时的 "Name must match parent directory" 误报
- **P1-1** 删除 `compatibility` 字段（非 LLM 决策依赖，浪费上下文）
- **P1-2** frontmatter.version "1.11" → "1.12"（v1.12 整改时漏更新）
- **P1-3** `review-checklist.md` 新增"编号体系"小节：9 维度前缀定义 + 编号引用规则
- **P1-4** SKILL.md 渐进披露表"版本一致性"行澄清 V0 校验器 vs 规范指南双职责
- **P2-1** §5-§9 保留在主文档（硬规则摘要例外，Agent 运行时必须遵守）
- **P2-2** 双风格说明加标题"评审链 vs 创建链"
- **P2-3** 新增 `## 1b. 触发方式` section（显式/隐式/否定触发）
- **P2-4** Non-Goals 加"frontmatter 字段裁剪决策"边界
- **P2-5** description 去重复触发词 "review skill"
- **P3-1** Gotchas 加 G7"路径假设（validate .）"坑点
- **P3-2** `routing-table.md` 新增 §7"加载时机 (Loading Timing)"表

## v1.12.0 (2026-06-19)

### V0 版本约束降级 + zhile 整改联动

> **问题来源**：zhile v1.9.0-r3 整改要求删除 SKILL.md 头部 `> **版本**: vX.Y.Z` 块 + 文末 `## 版本历史` section，理由是"对 LLM 决策无价值"。但 V0 校验器将这两项设为**硬约束**——斧正也仅为过 V0 保留它们。直接删会触发 V0 FAIL。
>
> **核心价值原则**：「V0 校验的"硬约束"必须真的硬；冗余字段占用上下文永远不可取。VERSION.md 是人类维护点，frontmatter 是 LLM 决策点，混在一起就是职责错位。」

- **V0 校验器放宽**：`scripts/_impl/quick_validate.py::validate_version_consistency()` L291-306 + L317-328 改造——当 SKILL.md 同时存在 frontmatter.version + VERSION.md 时，跳过"头部版本块存在性"和"版本历史 section 存在性"硬校验；仅当两者都缺时才 FAIL（确保极简 Skill 仍能写"无 VERSION"形式）
- **3 技能 V0 验证**：zhile / 斧正 / skill-workshop 全部 `Project checks: passed with warnings`（仅 1 description 合规提示），验证 v1.12 校验器兼容性
- **斧正 V0 仍合规**：斧正当前 SKILL.md 仍含 `> **版本**: v0.2.1` + `## 版本历史` section（v1.0.2 自审时为过 V0 强制添加）；新 V0 校验器对斧正形式"宽容"（不再 FAIL），但不**要求**斧正删——斧正后续可自主决定是否同步精简
- **自我纠错**：原 v1.11 文档中描述 compatibility 字段"已淘汰"措辞在 zhile 整改时被澄清——compatibility 并非 Anthropic 官方淘汰字段，而是**非 LLM 决策依赖字段**，删除理由是减少冗余而非跟随规范

### 设计决策

| # | 决策 | 选择 | 备选 |
|---|------|------|------|
| 1 | V0 硬约束降级 | VERSION.md fallback 存在时降级为 warning | 一律要求头部版本块 + 版本历史 section（保留 V0 FAIL 模式）|
| 2 | 斧正 SKILL.md 形式 | 暂不主动改（保持兼容）| 主动同步精简斧正头部版本块 / 版本历史 section |

---

## v1.11.0 (2026-06-19)

### description 联锁规则 + V0 格式校验（修复规范分裂）

- **P0 规范分裂修复**：frontmatter-style-guide 要求"单行 string"、intent-calibration 要求"Pushy 主动风格"，两者无联动，斧正踩了规范分裂的雷没人拦
- `references/specs/frontmatter-style-guide.md` §9 新增"description 字段联锁规则"：5 条硬/软约束表（单行 string / Pushy 句式 / 触发词 ≥3 / 边界声明 / 字符数 200-400）+ 反例 vs 正例对照
- `references/specs/spec.md` L99-110 补"`description` 格式约束（V0 / W7 强约束）"小节，把联锁规则从设计指南提升到官方规范层级
- `scripts/_impl/quick_validate.py` 新增 `validate_description_format()` 函数：4 条自动校验（YAML 单行 / ≤1024 / Pushy 句式 / 触发词 ≥3），接入 V0 spec_errors 通道
- 斧正 v0.2.1 SKILL.md description 整改：YAML `|` 块 → 单行 string，145 字符 → 211 字符，4 触发词 + 边界声明齐全
- 斧正 v0.2.1 V0 验证从 1 warning 升至 0 warning（"description 格式合规 211 字符 18 触发词"）
- skill-workshop V0 自验：description 367 字符 27 触发词 → 合规
- 三项校验全通过：V0 validate passed (斧正 + skill-workshop) / consistency PASS / routing-check PASS

## v1.10.0 (2026-06-19)

### P1 批量修复

- `scripts/skill_cli.py` 加 PEP 723 内联依赖声明（`# /// script` 块，requires-python >=3.10, dependencies=[]）
- `scripts/_impl/quick_validate.py` 输出统一：状态行（"Skill is valid!"）→ stdout，错误/警告详情 → stderr
- `scripts/_impl/routing_check.py` 输出统一：错误信息 → stderr，状态行 → stdout
- 三项校验全通过：V0 validate passed / consistency PASS / routing-check PASS

## v1.9.0 (2026-06-19)

### V0 校验器 bug 修复 + fuzheng warning 修复

- `scripts/_impl/quick_validate.py` 决策矩阵表头匹配从 `in content` 精确字符串匹配改为正则 `^\|\s*场景\s*\|\s*命中信号\s*\|\s*跳转到\s*\|`（兼容 Markdown 表格对齐空格）
- 同文件 `index.md` 表头匹配也改为正则（`用户常见说法 | 命中矩阵行 | 建议先打开`）
- fuzheng `SKILL.md` `## 强规则摘要` → `### @步骤0: 强规则摘要`（H2→H3+语义标记，符合 V0 校验器期望）
- fuzheng V0 校验从 FAIL → PASS（0 error / 0 warning）
- skill-workshop V0 校验仍 PASS

## v1.8.0 (2026-06-19)

### 自审查整改（P0 + P1）

- **P0** 删除 `references/specs/spec-zh.md` 和 `references/specs/validate-zh.md`（之前声称已删但实际残留，Agent 可能加载过时中文翻译版）
- **P1** description 精简 494→352 字符：移除工具栈声明 "In agent runtimes that support Python 3.10+ with optional PyYAML"（已在 compatibility 字段声明）和边界声明 "Not for: 通用代码调试, 非 skill 文档创作, Agent 框架开发, 通用代码 review"（已在 body §8 Non-Goals）
- 自审查加权总分 83.75，半产品化，剩余 P1×3 + P2×7 留后续迭代
- 三项校验全通过：V0 validate passed / consistency PASS / routing-check PASS

## v1.7.0 (2026-06-19)

### checklist 与 spec 对齐 + routing-check CLI 注册

- `references/rubrics/review-checklist.md` 字段归属表：`specs/spec-zh.md` → `specs/spec.md`；"类型/位置"两列 → "必需/类型约束"两列，补充 name 64 字符、description 1024 字符、compatibility 500 字符、metadata string→string、allowed-tools 空格分隔单字符串
- S6 检查项补充 `compatibility ≤500 字符` + `metadata value 为 string`
- B3 注意段补充 `allowed-tools 类型为空格分隔单字符串（非 array）`
- frontmatter source 引用更新为 `Agent Skills Official Spec (spec.md)`
- `scripts/skill_cli.py` 注册 `routing-check` 子命令（调用 `_impl/routing_check.py`）
- `references/specs/` 下 4 个文件补 `trigger-when` frontmatter 字段（best-practices.md / CHANGELOG.md / spec.md / validate.md）
- P-V-H / P-V-E 术语一致性确认：全仓库无错改，所有 P-V-E 仅出现在旧术语检测规则中
- 三项校验全通过：routing-check PASS / V0 validate passed / consistency PASS

## v1.6.0 (2026-06-18)

### spec.md / best-practices.md / validate.md 全套整改
- `references/specs/best-practices.md` 用 https://agentskills.io/skill-creation/best-practices 真实官方源完整重写（17.3 KB / 221 行，version 2026-05 → 2026-06，frontmatter 加 last-verified: VERIFIED 字段）
- 删除 `references/authoring/karpathy-engineering.md`（按用户确认：Karpathy 4 条是给 claude code 等 agent 的工程原则，不属于 skill 创建最佳实践）
- SKILL.md §4 路由表删除 karpathy-engineering.md 引用（karpathy-engineering.md 删除时同步清理路由表）
- `references/specs/CHANGELOG.md` best-practices.md 对齐状态从 UNREACHABLE → VERIFIED
- V0 验证：skill-workshop exit 0 / 0 warning；fuzheng 1 warning（"3+ workflow 应配决策矩阵"——fuzheng 已配，属 validator 误报，留 v1.7 排查）

## v1.5.0 (2026-06-18)

### 路由表与版本一致性闭环
- **P0-1** SKILL.md §4 路由表加 `spec.md` / `validate.md` / `best-practices.md` 三行（role: official-spec 标注）
- **P1-1** VERSION.md 补 v1.3 段（v1.3 整改时只改了 frontmatter，未记入 changelog，v1.5 补齐）
- **P1-2** `references/routing-table.md` §6 增"双写一致演练流程"（3 步：扰动→校验→同步）
- **P1-3** `scripts/_impl/quick_validate.py` 边缘 case 注释 + 边界处理（None / 空字符串 / 非 string key）
- V0 warning 残留 0 个（从 3 warning → 0）

## v1.4.0 (2026-06-18)

### P0-P2 全整改（PUA 模式自审）
- W0-W6 共 6 个 workflow 补 frontmatter name/description/version 三个必填字段（v1.3 PUA 整改时仅修了 W3/W7/V0 三个，本次补齐剩余 6 个）
- C1-C3 共 6 个 workflow 补 frontmatter name/description/version 三个必填字段
- description 精简（1491 → 765 字符）；T3 项目环境维度补 "In agent runtimes that support Python 3.10+"
- P-V-H 硬规则扩展：从仅适用评审模式扩展为适用所有破坏性操作（评审/创建/重构三模式统一）
- 决策矩阵双写合并：删除原 §3 "工作流路由表"（12 行重复信息），决策矩阵已含入口工作流列
- 评审模式 README 增 Output Path 段（"产物路径"）
- V0 校验脚本实装"路由一致性"硬校验（写入 `_impl/quick_validate.py` 路由表交叉验证）
- consistency-rules.yaml 扩充"旧术语"检测 pattern（v1.3 / 优化建议 / 改写建议 / 建议的重构方向）
- scripts/_impl/ spot check：无 input() 残留
- SKILL.md frontmatter version 同步到 v1.4

## v1.3.0 (2026-06-18)

### PUA 模式路由整改
- W3 reads-from 必加 frontmatter-style-guide.md + versioning-and-validation.md
- S6 由 P2 软性建议升级为 P1 硬限（V0 硬校验范畴）
- V0 校验流程必加 versioning-and-validation.md 第 7-8 步（版本三处一致 + frontmatter 字段过度工程化）
- W7 委派链扩展（加 frontmatter-style-guide.md + progressive-disclosure-patterns.md；新增 Step 6 description 自身反模式扫描）
- SKILL.md §4 路由表从 4/9 覆盖扩至 10/10 authoring 文件
- 新建 `references/routing-table.md` 路由一致性真相源

## v1.2.0 (2026-06-14)

### P1 修复

- S2：W0-W7 + V0 共 9 个工作流文件全面添加语义化标记（`@工作流:`/`@步骤N:` + HTML 注释元数据）
- C3：C1 创建工作流拆分为 3 个子步骤文件（C1-requirements.md / C1-scaffold.md / C1-edit.md），C1 降级为路由文件

### P2 修复

- V4：创建 `tests/trigger-test-set.md`（正面 14 条 + 负面 7 条）
- M7：SKILL.md §2 硬规则全部追加 Why 解释
- M4：评估模板标记为已通过自审验证（v2026.07）

### 复审结果

- 复审报告：`reviews/skill-workshop-v1.1-re-review.md`
- 结论：稳定可复用（P0:0 / P1:0 / P2:1 / 总未命中 1 项）
- 8 维加权评分：90/100

## v1.1.0 (2026-06-14)

### 报告模板合并

- 合并 output-template（reviewer）与 skill-evaluation-template（creator）为统一的 `evaluation-template.md`
- 新模板保留 reviewer 的证据链追溯（checklist 编号）+ P0/P1/P2 分级
- 新模板吸收 creator 的 8 维加权评分 + 结构化问题卡片 + 评估范围声明 + 裁剪规则
- 旧模板标注废弃，保留向后兼容

### P1 修复

- P5：`skill_cli.py` 错误信息改为可操作格式，未知命令自动建议最近匹配（`difflib.get_close_matches`）
- P7：review/checklist/spec/consistency 子命令统一加 `--offset`/`--output` 输出截断
- S3：SKILL.md 新增「双风格说明」，声明评审链纯 Markdown 与创建链语义标记共存是设计选择

### 性能优化

- review_ops.py：移除公开 API 中的 `_clear_cache()`，缓存跨调用复用；外部 YAML 规则编译移到模块加载时
- quick_validate.py：`validate_markdown_links` 加 `resolve_cache`，Windows `_getfinalpathname` 调用去重
- checklist_scan x10：0.038s → 0.011s（3.4x）
- quick_validate x5：0.180s → 0.092s（2.0x）

### 文档

- 新增 README.md：价值主张、使用示例、文件结构、CLI 速查、致谢
- SKILL.md 精简：移除运行时要求和详细版本历史（分别移至 README.md 和 VERSION.md）
- 一致性修复：迁移文件旧术语（工作流拆分→拆分需求识别，优化建议→整改方向）
- 21 个 reference 文件补充 `trigger-when` frontmatter
- 自审查报告：`reviews/skill-workshop-self-review.md`，结论为半产品化

## v1.0.0 (2026-06-14)

### 合并来源

| 来源                        | 版本    | 定位                   | 贡献                                                                                                      |
| --------------------------- | ------- | ---------------------- | --------------------------------------------------------------------------------------------------------- |
| skill-reviewer (ErgeAIA)    | v4.6    | 裁判——只审不改         | 9 维 48 项评审体系、W0-W7+V0 工作流、V1-V7 自检闭环、validate_review.py、复杂度标尺、意图校准、合规规范   |
| kz-skill-creator (kingzeus) | v1.40.6 | 构建者——创建+重构+评测 | 创建/重构/评测工作流、语义化标记规范、skill_cli.py 12 子命令、评测闭环（agents/ + assets/）、8 维加权评分 |

### 合并变更

- 统一入口：`skill_cli.py` 16 个子命令（原 12 + 新增 4 个 review/checklist/spec/consistency）
- 双评估并存：9 维 48 项（深度评审）+ 8 维加权（快速评分）
- 新增工作流：C1-create、C2-evaluate、C3-refactor
- validate_review.py 重构为 review_ops.py（API 化，供子命令调用）
- 目录重组：workflows/ → references/workflows/，rubrics/specs/config 独立分层
- 语义化标记强制：新建/重构 Skill 必须使用 @工作流/@步骤N/@动作/@验证点
