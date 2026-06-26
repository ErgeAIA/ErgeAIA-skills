---
name: changelog-manager
description: "维护项目更新日志（Changelog）。当用户提到 更新日志/changelog/变更记录/发版记录/release notes/版本历史，或需要创建、更新、初始化 CHANGELOG 时调用。基于 Keep a Changelog 规范，支持从 git 提交记录自动生成、手动追加条目、版本发布归档。内置双语言支持，同时维护中文 CHANGELOG.md 和英文 CHANGELOG.en.md。不适用于：非 Keep a Changelog 格式的自定义日志、git commit message 规范制定、自动创建 git tag/GitHub Release。"
metadata:
  author: ErgeAIA
  version: "2.0.0"
---

# changelog-manager

## 角色

项目更新日志维护助手。帮助个人开发者规范化地记录和管理项目每个版本的显著变动。

## 核心目标

1. 让开发者不再纠结"更新日志怎么写"
2. 自动从 git 提交记录中提取有价值的变更信息
3. 生成符合 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 规范的更新日志
4. 支持语义化版本（SemVer）管理
5. 同时维护中文（CHANGELOG.md）和英文（CHANGELOG.en.md）双语文档

## 触发条件

**CRITICAL: 当用户出现以下情况时，必须立即调用本技能：**
- 提到"更新日志"、"changelog"、"变更记录"、"发版记录"、"release notes"、"版本历史"
- 需要创建或初始化 CHANGELOG.md
- 准备发布新版本，需要生成版本更新说明
- 想要从 git 提交记录生成变更摘要
- 需要追加新的变更条目到现有更新日志

## 快捷操作（Shortcuts）

| 快捷命令    | 说明                          | 示例                                            |
| ----------- | ----------------------------- | ----------------------------------------------- |
| `+init`     | 初始化双语言 CHANGELOG        | `+init` 或 `+init 我的项目名`                   |
| `+add`      | 追加变更条目到 Unreleased     | `+add 新增了用户登录功能`                       |
| `+release`  | 发布新版本（归档 Unreleased） | `+release 1.2.0` 或 `+release 1.2.0 2024-01-15` |
| `+generate` | 从 git 提交记录生成变更       | `+generate` 或 `+generate v1.0.0..v1.1.0`       |
| `+check`    | 检查更新日志规范性            | `+check`                                        |
| `+lang`     | 切换主语言模式                | `+lang zh` 或 `+lang en`                        |

**注意**：`+init` 默认创建 CHANGELOG.md 和 CHANGELOG.en.md 两个文件；其他快捷命令默认同时更新两个文件。

## 执行原则

### 1. 人类可读优先
> 更新日志是写给*人*看的，不是给机器看的。

- 使用清晰、简洁的自然语言描述变更
- 避免直接堆砌 git commit message
- 每条变更应该让用户一眼看懂"发生了什么"

**verify**: 变更条目使用自然语言，非原始 commit hash 或缩写

### 2. 规范化分类
> 同类改动必须分组放置。

严格使用以下分类（按 Keep a Changelog 规范）：
- `Added` — 新添加的功能
- `Changed` — 对现有功能的变更
- `Deprecated` — 即将移除的功能
- `Removed` — 已经移除的功能
- `Fixed` — Bug 修复
- `Security` — 安全性改进

**verify**: 每个版本的变更按上述分类分组，不使用自定义分类

### 3. 语义化版本对齐
> 版本号应遵循 SemVer 规范。

根据变更类型建议版本号：
- `Added`（新功能）→ 通常为 minor 版本升级
- `Changed`（破坏性变更）→ 通常为 major 版本升级
- `Fixed`（Bug 修复）→ 通常为 patch 版本升级
- `Security`（安全修复）→ 通常为 patch 版本升级

**verify**: 发布时提供版本号建议及理由

### 4. 渐进式记录
> 在 Unreleased 区块持续记录，发布时归档。

日常工作流：
1. 开发过程中随时使用 `+add` 追加变更到 `[Unreleased]` 区块
2. 发布时使用 `+release` 将 `[Unreleased]` 内容归档到新版本

**verify**: CHANGELOG.md 始终包含 `[Unreleased]` 区块

### 5. 智能提取
> 从 git 提交中提取有价值的信息，过滤噪音。

提取规则：
- 跳过合并提交（Merge pull request / Merge branch）
- 跳过纯文档/格式调整（除非用户指定包含）
- 将技术性 commit message 转写为用户友好的描述
- 识别 commit 中的 conventional commit 前缀（feat/fix/refactor 等）并映射到对应分类

**verify**: 生成的变更条目不包含原始 commit hash，描述清晰可读

### 6. 双语言同步原则
> 所有变更必须同时记录在中文和英文文档中。

双语言工作规范：
- 用户输入默认使用中文，英文由技能自动翻译生成
- 如用户使用英文输入，中文由技能自动翻译生成
- 翻译时保留技术术语的准确性（如 API、SDK、CLI 等）
- 分类标题使用中英文对照（Added/新增、Changed/变更 等）
- 版本链接保持一致（指向同一仓库）

**verify**: CHANGELOG.md 和 CHANGELOG.en.md 版本区块内容对应一致

### 7. 双语文档一致性原则
> 同一版本的变更条目必须在两个文档中一一对应。

一致性检查：
- 版本号和日期完全一致
- 变更条目数量一致
- 分类结构一致
- 链接指向一致

**verify**: 两个文件的 `[Unreleased]` 和各版本区块可逐行对照

## CHANGELOG.md 标准格式

### 中文版 (CHANGELOG.md)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2024-01-15

### Added
- 用户登录与注册功能
- 个人资料页面

### Fixed
- 修复首页加载缓慢的问题

[Unreleased]: https://github.com/user/repo/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0
```

### 英文版 (CHANGELOG.en.md)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2024-01-15

### Added
- User login and registration feature
- User profile page

### Fixed
- Fix slow homepage loading issue

[Unreleased]: https://github.com/user/repo/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0
```

### 分类标题中英文对照

| 英文 | 中文 |
|------|------|
| Added | 新增 |
| Changed | 变更 |
| Deprecated | 弃用 |
| Removed | 移除 |
| Fixed | 修复 |
| Security | 安全 |

## 工作流路由

### W0: 初始化（`+init`）

执行前检查：
- [ ] 确认当前目录路径
- [ ] 检查是否已有 CHANGELOG.md 和 CHANGELOG.en.md

执行步骤：
- [ ] 如已有中文文件，询问用户：覆盖 / 合并 / 取消
  🔴 CHECKPOINT · 🛑 STOP：用户未确认前不要创建任何文件
- [ ] 生成标准模板（含项目名称）
- [ ] 创建 CHANGELOG.md（中文模板）
- [ ] 创建 CHANGELOG.en.md（英文模板）
- [ ] 提示用户使用 `+add` 开始记录

### W1: 追加变更（`+add`）

执行前检查：
- [ ] 确认 CHANGELOG.md 和 CHANGELOG.en.md 存在
- [ ] 确认两个文件的 `[Unreleased]` 区块存在

执行步骤：
- [ ] 读取现有 CHANGELOG.md 和 CHANGELOG.en.md
- [ ] 分析用户输入的变更描述
- [ ] 自动判断变更分类（参考 `references/classification-guide.md`）
- [ ] 如无法确定分类，询问用户选择
  🔴 CHECKPOINT · 🛑 STOP：分类不确定时不要猜测，必须询问用户
- [ ] 将条目插入中文版的 `[Unreleased]` 对应分类下
- [ ] 自动翻译为英文，插入英文版的 `[Unreleased]` 对应分类下
- [ ] 写回两个文件
- [ ] 输出确认信息

### W2: 发布版本（`+release`）

执行前检查：
- [ ] 确认 CHANGELOG.md 和 CHANGELOG.en.md 存在
- [ ] 确认两个文件的 `[Unreleased]` 区块存在

执行步骤：
- [ ] 读取两个文件的 `[Unreleased]` 内容
- [ ] 如为空，提示并询问是否继续
- [ ] 确定版本号（用户提供或根据变更类型建议）
- [ ] 确定发布日期（ISO 8601 格式）
  🔴 CHECKPOINT · 🛑 STOP：展示变更摘要，等用户确认版本号后再归档
- [ ] 将中文版的 `[Unreleased]` 内容归档到新版本区块
- [ ] 将英文版的 `[Unreleased]` 内容归档到新版本区块
- [ ] 创建新的空 `[Unreleased]` 区块（两个文件）
- [ ] 更新底部链接（两个文件）
- [ ] 写回两个文件
- [ ] 输出发布确认信息

### W3: 从 Git 生成（`+generate`）

**⚠️ 此工作流涉及批量变更写入，采用 Plan-Validate-Handoff 模式：**

**Plan（计划阶段）**：
- [ ] 执行 `git log` 获取提交记录（指定范围或默认上次 tag 至今）
- [ ] 过滤噪音提交（参考 `references/git-extraction-rules.md`）
- [ ] 将 commit message 转写为用户友好描述
- [ ] 按分类分组
- [ ] 生成中英文双语版本
- [ ] 输出预览计划表

**Validate（确认阶段）**：
- [ ] 展示预览内容给用户（包含中英文）
- [ ] 等待用户确认：写入 `[Unreleased]` / 指定版本 / 取消

**Handoff（执行阶段）**：
- [ ] 用户确认后执行写入
- [ ] 同时更新两个文件
- [ ] 输出确认信息

### W4: 规范检查（`+check`）

执行步骤：
- [ ] 读取 CHANGELOG.md 和 CHANGELOG.en.md
- [ ] 检查格式规范（标题层级、分类名称、日期格式）
- [ ] 检查内容质量（空版本、描述清晰度）
- [ ] 检查双语文档一致性（版本区块对应、条目数量一致）
- [ ] 输出检查报告（参考 `references/output-template.md`）

### W5: 语言模式切换（`+lang`）

用于指定主语言，影响翻译方向：
- `+lang zh`：主语言为中文，英文由中文翻译生成
- `+lang en`：主语言为英文，中文由英文翻译生成

执行步骤：
- [ ] 记录用户选择的语言模式
- [ ] 在后续 `+add` 和 `+generate` 中应用该模式
- [ ] 输出当前语言模式确认

## 参考文档（按需加载）

| 参考文件                             | 何时加载                                                         | 类型         |
| ------------------------------------ | ---------------------------------------------------------------- | ------------ |
| `references/classification-guide.md` | 无法确定变更分类时，加载详细分类指南和边界案例                   | 规则库       |
| `references/git-extraction-rules.md` | 从 git 提交生成变更时，加载提取规则和 conventional commit 映射表 | 规则库       |
| `references/bilingual-guide.md`      | 双语言模式工作时，加载翻译规则和技术术语对照表                     | **规则库**   |
| `references/template-examples.md`    | 输出 CHANGELOG.md 时，加载输出模板和格式规范                     | **输出模板** |
| `references/output-template.md`      | 需要生成 release-notes 或检查报告时，加载对应输出模板            | **输出模板** |

## Gotchas

- 日期格式必须使用 ISO 8601（`YYYY-MM-DD`），不要使用区域性格式
- 不要将 git log 直接作为更新日志，必须经过人工/智能筛选和转写
- `[Unreleased]` 区块应始终存在，即使为空
- 版本链接应指向正确的 compare 或 release 页面
- 被撤回（YANKED）的版本应标注 `[YANKED]` 标签
- 如果用户没有使用 git，应支持纯手动模式（不依赖 git log）
- 双语言模式下，两个文件的 `[Unreleased]` 区块应同步更新
- 翻译时保留技术术语原文（如 API、SDK、CLI、REST、JSON 等）

## 操作反例黑名单

来自实际维护经验的坑。每条都是**真实踩过的反模式**。

| # | 反模式 | 为什么不要做 | 替代做法 |
|---|---|---|---|
| 1 | **跳过 [Unreleased] 区块** | 导致发布时无缓冲区，被迫临时整理 | 始终维护 `[Unreleased]` 区块，即使为空也保留 |
| 2 | **把 git commit message 直接作为变更条目** | 技术术语（如 `feat(auth): add jwt`）用户看不懂 | 转写为用户友好的自然语言（如"支持 JWT 自动刷新"） |
| 3 | **一个条目混合多个分类** | 导致归类混乱，用户找不到 | 拆分为多个条目，或选择最显著的分类 |
| 4 | **只更新中文或只更新英文** | 双语文档内容不一致，用户困惑 | 每次 `+add` / `+release` 同时更新两个文件 |
| 5 | **使用自定义分类名称**（如"优化"、"改进"） | 破坏 Keep a Changelog 规范，机器无法解析 | 严格使用 Added/Changed/Deprecated/Removed/Fixed/Security |
| 6 | **翻译时过度本地化技术术语**（如把 API 翻译成"应用程序接口"） | 开发者搜索术语时匹配不到 | 保留 API/SDK/CLI/JWT/REST/JSON 等原文 |
| 7 | **+generate 后不预览就直接写入** | 自动生成的内容可能有误或冗余 | 先展示预览计划表，等用户确认后再写入 |
| 8 | **在版本区块中保留 commit hash** | 用户不关心内部引用，只关心发生了什么 | 移除 commit hash，仅保留用户可读的描述 |
| 9 | **忽略 SemVer 版本号建议** | 用户随意填写版本号，破坏版本一致性 | 根据变更类型建议版本号并说明理由 |
| 10 | **把内部重构/CI 调整写入更新日志** | 用户不关心内部实现变更 | 仅记录影响外部行为的变更 |

### 危险动作（需用户确认）

以下操作涉及不可逆变更或批量写入，**必须先停下等用户确认**：

- `+init` 覆盖已有 CHANGELOG.md → 必须询问：覆盖 / 合并 / 取消
- `+release` 归档 [Unreleased] → 必须展示变更摘要，等用户确认版本号
- `+generate` 批量写入 → 必须展示预览，等用户选择写入目标
- 删除或修改已发布版本的条目 → 必须先说明原因，等用户确认

## 验证闭环（自检标准）

- **V1 格式正确**：CHANGELOG.md 和 CHANGELOG.en.md 符合 Keep a Changelog 格式，包含标准头部、`[Unreleased]` 区块、版本链接
- **V2 内容质量**：变更条目使用自然语言、按正确分类分组、每条描述清晰无歧义
- **V3 版本一致性**：版本号遵循 SemVer，发布日期格式正确，链接指向正确
- **V4 双语一致性**：两个文件的版本区块一一对应，条目数量一致，分类结构一致
- **V5 触发测试集**：修改 description 后，执行 `references/trigger-test-set.md` 验证触发行为
- **V6 输出可判定**：输出格式符合 `references/output-template.md`，可机器判定

## 非目标

- 不替代 git commit message 规范（但可从 conventional commit 中提取信息）
- 不自动创建 git tag 或 GitHub Release（但可提供建议命令）
- 不管理多语言版本的更新日志（仅支持中文和英文）
- 不提供人工翻译服务（仅提供机器辅助翻译）

## 运行时要求

- **文件读写**：需要读写项目目录下的 CHANGELOG.md 和 CHANGELOG.en.md
- **git（可选）**：使用 `+generate` 时需要 git 仓库环境
- **网络（可选）**：参考 Keep a Changelog 在线文档时需要网络
- **翻译能力**：内置中英文翻译能力，无需额外 API

## 交付物输出路径

- CHANGELOG.md 输出到当前工作目录
- CHANGELOG.en.md 输出到当前工作目录
- 版本发布时可额外输出 release-notes-[version].md 供 GitHub Release 使用
