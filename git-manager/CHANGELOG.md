# Changelog

All notable changes to this skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.3] - 2026-09-26

### Added
- `assets/banner.svg`（tupu 一图流横版）接入 README 门面。

## [1.3.2] - 2026-09-22 (description 职责瘦身：Trigger→Job→Safety boundary 路由器式重写)

### Changed
- **description 职责瘦身（Trigger → Job → Safety boundary）**：移除 1.3.1 描述中过载的「是什么 / 能力 / 规则 / 排除项」堆叠，改为路由器式定位——仅在「什么时候叫我」层表达：触发（提交代码 / 创建或切换分支 / 合并 / 推送 / 拉取 / rebase / Git 错误）→ 职责（提供规范的 Git 操作流程）→ 安全边界（删除变更 / 改写历史 / 强制推送等高风险操作前要求用户明确确认）。实现细节（Conventional Commits 规则、force push / reset --hard / branch -D 枚举、二次确认机制）下沉至 SKILL 正文与 references，不再塞进 description。依据外部审查结论「description 方向正确，但职责过载；`trigger-when.md` 已独立承载触发与排除规则」。

### 结论
- v1.3.2：description 职责瘦身（路由器式 Trigger→Job→Safety boundary），无功能回归、无行为变更；维持 `✅ 已审`。

## [1.3.1] - 2026-09-22 (危险操作清单补全 + 分支命名同步 + description 写法对齐最佳实践)

### Fixed
- **R1（dangerous-operations.md 引用漂移）**：SKILL「删除未提交的变更（含 git stash drop / git clean -f / git checkout --）」指向 references 的详细影响说明与恢复预案，但该文件此前仅收录 `git stash drop`，缺 `git clean -f` 与 `git checkout --` 两条；已补两条（impact/risk/alternative 对齐），消除引用权威缺口（skill-workshop Fast L0 审查发现的 P1）。
- **R2（README 分支命名不同步）**：技能 README 分支管理节仍只列 6 种 type，未同步 1.2.1 的 hotfix/release 扩展；已补「常见扩展 hotfix/release」（P2）。
- **D1（description 写法对齐最佳实践）**：原 description 把 6 个触发词裸罗列在引号内，属 skill-workshop 反模式「裸词表 / 同义变体罗列 >3」，且缺 Not for 边界；触发句原为条件式「当你要…时启用」非主动式。已改为——触发词嵌入意图句（≤4 个）、补「不适用」边界、全角冒号合规、双引号单行；触发句定为中文主动祈使式「提交代码、建分支、合并或处理 Git 报错时，用 git-manager 规范提交流程并确认危险操作」。`skill_cli` 的「主动触发句式」探测器仅匹配英文模式，对中文主动句误报软警告，非硬性要求、不阻断。

### 结论
- v1.3.1：修复 1 处 P1 引用漂移 + 1 处 P2 文档不同步 + description 写法对齐最佳实践（含主动祈使句），无功能回归，维持 `✅ 已审`。

---

## [1.3.0] - 2026-08-24 (吸收 git-commit 提交信息生成流程)

### Added
- **提交信息生成四步流程**：分析 diff（`git status --porcelain` / `git diff --staged` / `git diff`）→ 分组暂存（`git add` / `git add -p`，一逻辑单元一提交）→ 判定三要素（Type/Scope/Description，≤50 字符）→ 执行（单行 / heredoc 多行含 body/footer）。详见新增 `references/commit-message-flow.md`。
- 破坏性变更两种标注（`<type>!` 感叹号 / `BREAKING CHANGE:` footer）、issue 引用（`Closes #123` / `Refs #456`）、commit 类型补 build/ci/revert（8 → 11 种）。
- 提交安全协议：绝不提交密钥（.env / credentials / 私钥 / 连接串）、不擅自跳过 hooks（--no-verify 仅用户要求时）、hooks 失败新建提交不 amend、禁止向 main/master force push；git config 修改列入危险操作。

### 第一性原理结论
- 本质矛盾：作为"安全护栏"技能，只告诉执行者"规范是什么"，没告诉"怎么从实际 diff 生成合规提交信息"——提交信息质量取决于执行者临场发挥而非技能本身。**必须做到**：提交信息生成有可复现操作路径（diff → 分组 → 判定 → 执行）；**绝不**：让提交信息质量依赖执行者自由发挥，或为流程完整牺牲既有中文护栏体系（危险操作闸 / 分支管理 / 合并策略）。

### 钢人裁决
- FOR：①四步流程补上质量杠杆缺口（"帮我提交"是最常见触发场景）；②所用命令均为稳定 git 标准接口；③git-commit 为 MIT 开源，内容融合无授权问题；④融入后单技能覆盖"分析→暂存→生成→执行"提交全链路。
- AGAINST（最强反方）：①护栏技能掺入操作细节 → 范围膨胀变通用 git 教程；②英文技能内容翻译融入可能文风割裂；③两套字符限制（git-commit <72 vs 本技能 ≤50）造成执行者困惑；④运行态已有 git-commit，两技能功能重叠冗余。
- 关键变量（可测试）：对真实 diff 跑 v1.3.0 流程，验证输出覆盖三要素 + secrets 检查 + hooks 规则。
- **判断（有条件）**：吸收 git-commit 的提交信息生成流程，保留 git-manager 中文护栏定位——细节下沉 references（SKILL 只留流程骨架防范围膨胀），字符限制从严保留 ≤50（在 `commit-message-flow.md` 注明与 git-commit 的差异）。若用户反馈与 git-commit 重叠导致混淆，回到"合并/替代"决策。

### 对抗式审查（风险清单）
- R1 新增 `references/commit-message-flow.md` 引用悬空 → 已跑机器校验 P1-7（validate / routing-check），文件真实存在、SKILL 链接正确。
- R2 SKILL 四步流程与 references 细节不一致 → SKILL 只留骨架、细节单一真相源在 `commit-message-flow.md`，已逐条对照。
- R3 版本三段式漂移 → SKILL metadata.version / VERSION.md / 根 README 索引已同步 1.3.0。
- R4 git-manager README 未链接新 references → 已补 `commit-message-flow.md`。
- R5 description 未动（避免可触发性风险）→ 触发词"提交"已覆盖本能力场景。

### 结论
- v1.3.0：实质能力增强（Added），无破坏性变更，维持 `✅ 已审`。

---

## [1.2.1] - 2026-08-24 (第一性原理 + 双向钢人 + SFA 三关重跑)

### Fixed（三关审查，逐文件交叉核对）
- **S1（分支 type 清单缺口）**：SKILL 分支命名 `<type>/<description>` 的 type 仅列 feature/fix/docs/refactor/test/chore（6 种），生产环境最常见的 `hotfix`（紧急修复）、`release`（发布）无处归类。已补"常见扩展：hotfix/release"，并注明 hotfix 从 main 拉取并直接回 main、不可当普通 feature。
- **S2（main 降级路径缺失）**：SKILL「禁止直接在 main 开发」是硬规则但无退路——用户已在 main 且有未提交改动时无降级指引。已补"先 git stash / git switch -c 迁出，勿强丢工作区"。
- **S3（危险操作语义对齐）**：SKILL「删除未提交变更」与 references/dangerous-operations.md 的 `git stash drop` 措辞不完全等同——已补注"含 git stash drop / git clean -f / git checkout -- 等不可逆丢弃"，与 dangerous-operations 对齐。
- **D17 噪音**：全文件排查无 `@` 标记、无旧技能名残留。无清理项。

### 第一性原理结论
- "危险操作强制二次确认""禁止 main 直开发"两项核心护栏经归谬验证成立；确认机制靠 Agent 自觉（Skill 无法真正阻断 shell）属合理边界。
- "分支 type 6 种 + 提交 type 8 种"是两套体系，此前 SKILL 未显式区分，本次仅在分支侧补 hotfix/release 扩展，提交侧维持 conventional-commits 8 种引用。

### 钢人裁决
- 反方 C1（hotfix/release 缺口）、C2（main 降级缺失）、C3（危险项措辞对齐）均采纳落地；C4（conventional-commits 与 SKILL 标题≤50 重复声明）驳回（重复但一致，非缺陷）。

### 结论
- v1.2.1 维持 `✅ 已审`：修复 3 处真实边界缺口（含 hotfix/release 常见分支无归类），无功能回归。本技能此前因 VERSION 缺 git review 记录被暂标 ⏳（见 README 说明），现已真实走完三关并复位 ✅。

---

## [1.2.0] - 2026-05-14

### Added
- Frontmatter 重构：分离 description 和 name，添加多行 description 结构
- 添加 metadata 字段（version、author、created、updated、origin）
- 新增 Pushy 引导结构（Make sure to use this skill whenever...）
- 新增三维触发结构（意图+技术特征+项目环境）
- Not for 排除域说明

### Fixed
- P0 问题：frontmatter 格式错误（description 和 name 同行）
- P0 问题：缺少 metadata 字段

## [1.1.0] - 2026-04-20

### Added
- 创建 workflows/ 目录
- 创建 references/ 目录
- 新增触发说明文档

## [1.0.0] - 2026-04-20

### Added
- 初始版本
- Git 分支管理指导
- Conventional Commits 提交规范
- 危险操作确认机制
