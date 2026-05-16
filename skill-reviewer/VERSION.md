# Changelog

> 本文件记录 Skill 的版本演进历史。外置原则：历史信息按需读取，不污染 SKILL.md 上下文预算。

---

## v4.5 (2026-05-15)

### 分享前优化

**去内部化**
- 移除 `metadata.origin` 字段（内部术语，不适合公开分享）
- 用途描述从"评审与校验 Agent Skill 仓库"修正为"评审与校验本地 Agent Skill 仓库（基于目录结构和文件内容）"
- 项目环境描述从"Skill 仓库"修正为"本地 Skill 仓库目录"

**Description 触发率优化**
- 重写 description 为英文主导 + 中文触发词混合格式
- 开头直接描述核心价值（9-dimension checklist, P0/P1/P2, actionable remediation）
- 明确列出触发场景（review/audit/evaluate/validate/diagnose/assess）
- 明确列出触发词（中英文混合，覆盖审查/评审/校验/合规/诊断/质量检查/规范检查）
- 明确列出 Not for 边界（creating skills, optimizing triggers, general code review, writing docs, agent framework dev）

**触发测试集语料优化**
- 去除内部路径，替换为通用语料
- 替换为通用语料，任何用户都能理解

**README 新手友好度提升**
- 新增"为什么需要这个 Skill"引导段落
- 新增"怎么用"快速上手示例
- 新增"评审报告长什么样"产出预览
- 新增"与 SKILL.md 的分工"说明
- 保留技术细节（文件结构、运行时要求、自我遵循）

---

## v4.4 (2026-05-15)

### 自检整改闭环

基于 `examples/skill-reviewer-self-review.md` 评审报告中的整改方向，执行以下修复：

**V4 触发测试集落地**
- 新增 `references/trigger-test-set.md`：skill-reviewer 自身触发测试集（正面 12 条 + 负面 8 条）
- SKILL.md §8 V4 描述补充自身测试集路径
- SKILL.md 文件角色映射表新增 `references/trigger-test-set.md` 条目

**V5 机器可判定断言扩展**
- `validate_review.py --checklist` 新增 6 类机器可判定检查项：
  - S2：结构化标记（H2 标题 + 列表标记）
  - C4：参考文件 trigger-when 加载指引
  - I2：scripts/ 目录可运行脚本存在性
  - P5：脚本错误信息可操作性（含修复建议）
  - P7：脚本输出截断支持（--offset/--output，>50 行脚本）
  - B3：triggers 字段位置（恢复意外删除的检查）
- SKILL.md §8 V5 描述补充已机器化检查项清单

**W3 T 系列裁决权本地约束**
- `workflows/W3-issues.md` 契约段新增"T 系列裁决权禁令"显式声明
- 确保 Agent 即使跳过 SKILL.md 也能遵守 T1–T5 委托 W7 的约束

**compatibility 声明修正**
- SKILL.md frontmatter compatibility 从"No third-party dependencies"改为"PyYAML optional"
- SKILL.md §9 运行时要求补充 PyYAML 可选依赖说明
- README.md 运行时要求同步更新

**frontmatter-style-guide.md 角色边界明确**
- frontmatter 新增 role/consumed-by/not-consumed-by 字段
- trigger-when 扩展为"用户主动询问 frontmatter 风格"时触发
- §8 非审查规则声明新增两条：加载时机约束 + W3 不得引用

**references/ README.md 补全 trigger-when**
- 4 个子目录 README.md（config/rubrics/specs/templates）补充 frontmatter trigger-when 字段

**测试覆盖扩充**（26 → 30 个用例）
- 新增 TestConsistencyMode：W4-OLD 检测、W5-OLD 检测、VERSION.md 忽略、JSON 输出
- 修复中文测试用例编码问题（添加 encoding="utf-8"）

**自检示例更新**
- `examples/skill-reviewer-self-review.md` 更新为整改后版本（v2026-05-r1）
- 反映 V4/V5 已落地、W3 约束已补全、compatibility 已修正、frontmatter-style-guide 角色已明确
- 评审结论从"V4/V5 未落地"调整为"O/S/C/I 维度部分检查项仍依赖 LLM 主观判定"

---

## v4.3 (2026-05-15)

### Skill-Creator 审查修复

**Description 触发优化**
- 修正工作流计数：七工作流契约（W1-W7）→ 九工作流契约（W0-W7 + V0）
- 移除与 skill-creator 竞争的触发词（"Agent Skill 开发"、"skill creator"）
- 补充口语化触发词（skill 诊断、skill audit、帮我看看这个 skill）
- Not for 新增"创建新 Skill（转交 skill-creator）"

**脚本工程化增强**
- `_load_external_rules`：外部规则改为合并（extend）而非替换，避免内置规则静默消失
- `_load_external_rules`：YAML 解析失败时输出 stderr 警告
- `_is_real_input_call`：增加多行字符串（`"""`/`'''`）内的 input 匹配过滤
- 新增 `--version` 参数
- 脚本版本 v5.1 → v5.2

**Gotchas 更新**
- 正则误报条目：补充 `_is_real_input_call()` 过滤函数方案

**工作流 frontmatter 统一**
- W4：`reads-from` 从逻辑描述改为文件路径
- W5：移除非标准 `contract` 字段，改用 `reads-from`/`writes-to`/`trigger-when`
- W7：`calls` 改为 `reads-from`

**目录结构补全**
- 新增 `references/config/README.md`
- 新增 `examples/README.md`
- README.md 文件树补全 config/、frontmatter-style-guide.md、__init__.py 等

**测试覆盖扩充**（18 → 26 个用例）
- 新增 TestReviewMode：review 模式 PASS/FAIL 测试
- 新增 TestVerboseMode：--verbose 日志级别测试
- 新增 TestOffsetOutput：--offset/--output 分页测试
- 新增 TestVersionCheck：SKILL.md vs VERSION.md 版本一致性测试
- 新增 TestChecklistMode 负面测试：缺少 Gotchas/Non-Goals

**文档一致性修正**
- VERSION.md v4.2 测试计数修正：16 → 18
- review-checklist.md 维度映射表：验证审查 V1-V5 → V1-V7

---

## v4.2 (2026-05-15)

### 合规校验补全（P0 修复）
- **A4**：--spec 模式补全 name 字段 hyphen-case 格式校验（大写/连字符开头/连续连字符/长度≤64）
- **A5**：--spec 模式补全 description 字段长度≤1024 和非空校验

### 术语漂移根除（P1 修复）
- **F2**：CONSISTENCY_RULES 新增缩写形式（P-V-E）和箭头形式（Plan → Validate → Execute）检测规则
- **D1**：W5 M5 "Execute" → "Handoff"
- **D2**：best-practices "P-V-E" → "P-V-H"
- **D3**：review-checklist 映射表 "P-V-E" → "P-V-H"
- **A8**：M8 检查只接受 "Plan-Validate-Handoff"

### 脚本工程化增强（P1 修复）
- **A1**：抽取 _extract_description() 公共函数消除重复
- **A6**：退出码 PASS=0 / FAIL=1 / 参数错误=2
- **A7**：--json total 字段在截断前计算
- **A3**：--checklist 补 V4/V5 检查
- **B2**：errors="ignore" → errors="replace" + stderr 警告
- **C3**：OSError 输出诊断信息到 stderr

### 文档补全（P1 修复）
- **D4**：W3 P1 清单补 M5
- **D5**：SKILL.md V4 补操作指导
- **D6**：W5 映射表补 S6 条目
- **D7**：示例 §5 格式对齐 output-template
- **D8**：W7/V0 职责边界描述修正

### 架构优化（P2 修复）
- **F3**：添加单元测试（tests/test_validate_review.py，18 个测试用例）
- **B1**：splitlines 预计算优化
- **C1**：十六进制转义添加注释
- **C2**：脚本头部声明 dry-run 不适用
- **F1**：验证闭环从 V1-V5 扩展为 V1-V7

---

## v4.1 (2026-05-14)

### 自审查修复：术语漂移与脚本工程化

**起因**：v4.0 自审查发现 4 项 P1 + 6 项 P2 问题，核心痛点为重构后术语漂移与自校验脚本覆盖不完整。

#### 术语漂移修复
- **W2-strengths.md**：将 "Plan-Validate-Execute" 更新为 "Plan-Validate-Handoff"
- **examples/ai-sector-investor-review.md**：段落名同步 output-template.md（"工作流重构建议"→"拆分需求识别"、"优化建议"→"整改方向"、"建议的重构方向"→"结构性问题总结"）
- **review-checklist.md**：头部计数从 "35 项" 修正为 "46 项"

#### 自校验脚本工程化 (validate_review.py v3.3 → v4.0)
- **P5 可操作错误信息**：所有错误信息追加 `| 修复建议：...` 段，Agent 可直接行动
- **P6 stdout/stderr 分离**：错误信息输出到 `sys.stderr`，数据输出到 `stdout`
- **P7 输出截断**：新增 `--offset` / `--output` 参数，支持大量错误翻页
- **V5 --checklist 扩展覆盖**：新增 B3（触发关键词覆盖）、B4（Non-Goals）、P6（stdout/stderr 分离）检查项
- **新增 --consistency 模式**：术语漂移检查机制，扫描全仓库 Markdown 文件，检测 v4.0 重构后的旧术语残留（P-V-E / 工作流拆分 / 优化建议 / 改写建议 / 建议的重构方向）

#### 产物路径约定
- **output-template.md**：新增"产物路径约定"段，评审报告保存至 `reviews/<skill-name>-review.md`

---

## v4.0 (2026-05-14)

### 重大变更：裁判角色定位与职责分离

**核心变更**：明确 skill-reviewer 为"裁判"角色，与 skill-creator（"教练"）职责分离。

#### 流程调整
- **§4 做法优于答案**：将"增量建议"改为"优化方向"，裁判只指出方向不给出具体修改片段
- **§5 P-V-E → P-V-H**：将 Execute 阶段改为 Handoff（转交），裁判不执行被评审对象的文件写入
- **W4 工作流拆分 → 拆分需求识别**：从"设计拆分方案"调整为"识别拆分需求"，不设计目标架构
- **W5 优化建议 → 整改方向映射**：从"具体动作模板"调整为"整改方向"，不给出具体修改方案
- **output-template §7**：从"建议的重构方向"改为"结构性问题总结"，不设计目标结构
- **trigger-test-set.md**：标注为"转交 skill-creator"，裁判只识别触发问题不执行测试

#### 规范整合
- **best-practices.md**：融入 Karpathy 四原则（Think Before Coding / Simplicity First / Surgical Changes / Goal-Driven Execution），含审查映射
- **review-checklist.md**：V 维度新增 V4（评估测试集）、V5（评估断言可机器判定）
- **review-checklist.md**：新增维度映射表（Karpathy 四原则映射 + 5 阶段审查映射 + 优先级统一标准）
- **W7**：增加"转交 skill-creator 判定"（T4/T5 命中时输出转交建议）
- **SKILL.md**：新增裁判角色定位声明、更新文件角色映射表、更新路由表名称

#### 基础设施
- **AGENTS.md**：新增技能权威源与分发机制约定

---

## v3.6 (2026-05-14)

### 新增
- **frontmatter-style-guide.md**：SKILL.md frontmatter 风格参考指南
  - 字段分类：必需字段、官方可选字段、metadata 扩展字段
  - 提供简洁/精简两种模板
  - 明确 VERSION.md 信息归属
  - 热门 Skills 常见模式参考
  - **非审查规则**：不干扰官方规范，不作为判定依据

### 优化
- **output-template.md**：第 6 节添加 Frontmatter 简洁化建议位置
- **review-checklist.md**：添加 S6 软性检查项（Frontmatter 字段复杂度）

### 说明
- 起因：发现部分自有技能 frontmatter 过于复杂（如 tauri-review）
- 目的：提供参考而非约束，保持设计灵活性
- 原则：一切以官方规范为准，自有规范不干扰不违反

---

## v3.5 (2026-05-14)

### 修复
- **B3 检查项修正**：移除错误的 triggers 字段要求，改为检查 description 是否包含触发关键词
  - 官方规范无 triggers 字段，触发信息应直接写入 description
  - 检查步骤改为：1) description 是否描述做什么与何时使用 2) 是否包含触发关键词

### 原因
- 官方 `spec.md` 仅定义 6 个 frontmatter 字段，`triggers` 不是官方字段
- 根因：早期错误理解规范，自行添加了 triggers 字段要求

---

## v3.4 (2026-05-14)

### 优化
- **description 三维触发强化**：添加意图关键词列表 + 技术特征维度 + 项目环境维度 + Not for 边界声明
- **Pushy 引导**：加入 "Make sure to use this skill whenever..." 类强引导话术
- **metadata.origin**：添加技能提炼场景追溯字段
- **workflows/ frontmatter**：6 个文件（W0、W1、W2、W4、W6、V0）添加 `trigger-when` 声明

---

## v3.3 (2026-05)

### 优化
- **W5 映射表增强**：补充 O1a（metadata.origin）、O1b（VERSION.md 外置）映射规则
- **review-checklist.md**：添加 O1a、O1b 检查项（P2 优先级）

---

## v3.2 (2026-05)

### 优化
- **九维检查清单**：从 35 项扩展，覆盖 O/S/C/I/T/M/P/V/B 全维度
- **T 系列委托 W7**：description 审计权唯一归属 W7，避免多重判定
- **V4 证据链检查**：评审报告中 W5 每条建议必须包含 checklist 编号标注

---

## v3.1 (2026-05)

### 优化
- **自校验脚本增强**：`validate_review.py` 支持 --checklist / --spec / 默认三种模式
- **Gotchas 段完善**：添加正则误报规避、Windows 路径假设说明
