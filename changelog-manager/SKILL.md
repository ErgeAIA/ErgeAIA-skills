---
name: changelog-manager
description: "维护项目的更新日志（Changelog）：按 Keep a Changelog 规范创建、追加、归档版本，并能从 git 提交记录自动生成，同时维护中英双语版本。当用户提到更新日志、changelog、变更记录、版本历史、发版记录或 release notes，或需要创建、更新或初始化 CHANGELOG 时调用。Not for: 非 Keep a Changelog 格式的自定义日志、git commit message 规范制定、自动创建 git tag 或 GitHub Release。"
metadata:
  author: ErgeAIA
  version: "2.1.2"
---

# changelog-manager

## 核心目标

1. 让开发者不再纠结"更新日志怎么写"
2. 自动从 git 提交记录中提取有价值的变更信息
3. 生成符合 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 规范的更新日志
4. 支持语义化版本（SemVer）管理
5. 同时维护中文（CHANGELOG.md）和英文（CHANGELOG.en.md）双语文档

## 触发条件

当用户出现以下情况时，调用本技能：
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

**分类标题语言（强制）**：中文 `CHANGELOG.md` 使用 `### 新增/变更/弃用/移除/修复/安全`；英文 `CHANGELOG.en.md` 使用 `### Added/Changed/Deprecated/Removed/Fixed/Security`。唯一对照见 `references/bilingual-guide.md`。

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

## 标准格式

遵循 [Keep a Changelog](https://keepachangelog.com/zh-Cn/1.0.0/) + [SemVer](https://semver.org/lang/zh-CN/)。中文文件用中文分类头、英文文件用英文分类头（**唯一对照见 `references/bilingual-guide.md`**，禁止中英混用）。完整模板见 `references/template-examples.md`；release-notes / 检查报告模板见 `references/output-template.md`。

## 工作流路由

六个快捷命令（`+init` / `+add` / `+release` / `+generate` / `+check` / `+lang`）的完整步骤、失败处理表与 `.changelog-manager.json` sidecar 字段，**执行对应命令时按需加载** `references/workflows.md`。

关键 CHECKPOINT（不可逆 / 批量写入前必须停）：见下方「危险动作」。

## 参考文档（按需加载）

| 参考文件                             | 何时加载                                                         | 类型         |
| ------------------------------------ | ---------------------------------------------------------------- | ------------ |
| `references/classification-guide.md` | 无法确定变更分类时，加载详细分类指南和边界案例                   | 规则库       |
| `references/git-extraction-rules.md` | 从 git 提交生成变更时，加载提取规则和 conventional commit 映射表 | 规则库       |
| `references/bilingual-guide.md`      | 双语言模式工作时，加载翻译规则和技术术语对照表                   | **规则库**   |
| `references/template-examples.md`    | 输出 CHANGELOG.md 时，加载输出模板和格式规范                     | **输出模板** |
| `references/output-template.md`      | 需要生成 release-notes 或检查报告时，加载对应输出模板            | **输出模板** |
| `references/trigger-test-set.md`     | 修改 description 或做触发回归验证时，加载触发测试集              | 测试集       |
| `references/workflows.md`            | 执行任一快捷命令（+init/+add/+release/+generate/+check/+lang）时，加载完整步骤与失败处理 | 流程       |

## Gotchas

- 日期格式必须使用 ISO 8601（`YYYY-MM-DD`），不要使用区域性格式
- 不要将 git log 直接作为更新日志，必须经过人工/智能筛选和转写
- `[Unreleased]` 区块应始终存在，即使为空
- 版本链接应指向正确的 compare 或 release 页面
- 被撤回（YANKED）的版本应标注 `[YANKED]` 标签
- 如果用户没有使用 git，应支持纯手动模式（不依赖 git log）
- 双语言模式下，两个文件的 `[Unreleased]` 区块应同步更新
- 翻译时保留技术术语原文（如 API、SDK、CLI、REST、JSON 等）
- 中文文件分类头必须是中文（`### 新增` 等），英文文件必须是英文（`### Added` 等）
- `+lang` / 链接 / Issue 保留策略落在 `.changelog-manager.json`，不要只写在对话里
- `+generate` 必须幂等：同一 range 二次执行应 0 条待写入
- 无 tag 仓库不要假设 `git describe` 总会成功
- `perf` 提交默认保留并映射为 Changed，不要当噪音跳过
- 目标仓库若已有变更记录约定（例如只用 `VERSION.md`、禁止 CHANGELOG），**先询问再 `+init`**
- 一条变更只归一个分类，混合多类时拆成多条或选最显著分类
- 只记录影响外部行为的变更；内部重构 / CI 调整不写入更新日志

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
- **V4 双语一致性**：版本集合/日期/分类集合/条目数/link key 结构同构；分类标题语言符合约定（中文文件中文头 / 英文文件英文头）
- **V5 触发测试集**：修改 description 后，执行 `references/trigger-test-set.md` 验证触发行为
- **V6 输出可判定**：输出格式符合 `references/output-template.md`，可机器判定

## 非目标

- 不替代 git commit message 规范（但可从 conventional commit 中提取信息）
- 不自动创建 git tag 或 GitHub Release（但可提供建议命令）
- 不管理多语言版本的更新日志（仅支持中文和英文）
- 不提供人工翻译服务（仅提供机器辅助翻译）

## 运行时要求

- **文件读写**：需要读写项目目录下的 CHANGELOG.md、CHANGELOG.en.md，以及可选 `.changelog-manager.json`
- **git（可选）**：使用 `+generate` 时需要 git 仓库环境
- **git 仅只读**：默认不跑终端命令；`+generate` 仅执行只读 `git log` / `git describe` 比对，**绝不执行 `commit` / `add` / `push` / `tag` / `release`**
- **网络（可选）**：参考 Keep a Changelog 在线文档时需要网络
- **翻译能力**：内置中英文翻译能力，无需额外 API
- **产物落调用方目录**：CHANGELOG.md / CHANGELOG.en.md / `.changelog-manager.json` 均写入当前项目，不写入技能仓库

## 交付物输出路径

- CHANGELOG.md 输出到当前工作目录
- CHANGELOG.en.md 输出到当前工作目录
- 版本发布时可额外输出 release-notes-[version].md 供 GitHub Release 使用
