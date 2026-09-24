---
description: 六个快捷命令（+init/+add/+release/+generate/+check/+lang）的完整执行步骤、失败处理与 .changelog-manager.json sidecar 字段。
trigger-when: 执行 +init / +add / +release / +generate / +check / +lang 任一快捷命令时，加载完整步骤
---

# 工作流路由（详细步骤）

本文件是 SKILL.md「工作流路由」的按需加载详情。执行对应快捷命令时加载。

## W0: 初始化（+init）

执行前检查：
- [ ] 确认当前目录路径
- [ ] 检查是否已有 CHANGELOG.md 和 CHANGELOG.en.md

执行步骤：
- [ ] 如已有中文文件，询问用户：覆盖 / 合并 / 取消
  🔴 CHECKPOINT · 🛑 STOP：用户未确认前不要创建任何文件
- [ ] 生成标准模板（含项目名称；中文文件用中文头与中文分类头）
- [ ] 创建 CHANGELOG.md（中文模板）
- [ ] 创建 CHANGELOG.en.md（英文模板）
- [ ] 静默创建默认 `.changelog-manager.json`（已存在则不覆盖）
- [ ] 底部链接能发现 `origin` 时自动填入（`tagPrefix` 默认 `v`）
- [ ] 提示用户使用 `+add` 开始记录

**W0 失败处理**：
| 触发条件                  | 一线修复                       | 仍失败兜底       |
| ------------------------- | ------------------------------ | ---------------- |
| 当前目录不是 git 仓库     | 告知用户，继续执行（git 可选） | 无               |
| 文件创建失败（权限/磁盘） | 检查路径和权限                 | 提示用户手动创建 |

## W1: 追加变更（+add）

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

**W1 失败处理**：
| 触发条件                               | 一线修复               | 仍失败兜底           |
| -------------------------------------- | ---------------------- | -------------------- |
| CHANGELOG.md 或 CHANGELOG.en.md 不存在 | 提示用户先执行 `+init` | 无                   |
| `[Unreleased]` 区块缺失                | 自动创建该区块         | 无                   |
| 文件写入失败（权限/磁盘）              | 检查路径和权限         | 提示用户检查文件状态 |

## W2: 发布版本（+release）

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

**W2 失败处理**：
| 触发条件                  | 一线修复               | 仍失败兜底           |
| ------------------------- | ---------------------- | -------------------- |
| `[Unreleased]` 区块为空   | 提示用户并询问是否继续 | 取消发布             |
| 版本号已存在              | 提示用户选择其他版本号 | 取消发布             |
| 文件写入失败（权限/磁盘） | 检查路径和权限         | 提示用户检查文件状态 |

## W3: 从 Git 生成（+generate）

**⚠️ 此工作流涉及批量变更写入，采用 Plan-Validate-Handoff 模式：**

**Plan（计划阶段）**：
- [ ] 读取 sidecar（`.changelog-manager.json`）取得 `primaryLang` / `keepIssueLinks` / `keepMarkers`
- [ ] 执行 `git log` 获取提交记录（指定范围或默认上次 tag 至今）
- [ ] **无 tag**：`git describe` 失败时询问是否使用全部历史（默认 `--max-count=200`），禁止抛裸错误
- [ ] **浅克隆**：存在 `.git/shallow` 时在预览顶 WARN
- [ ] 过滤噪音提交（参考 `references/git-extraction-rules.md`；`perf` 默认**保留**并映射为 Changed）
- [ ] 将 commit message 转写为用户友好描述（内部保留 hash **仅用于去重**，默认不写入正文）
- [ ] **幂等**：与目标 Unreleased/版本已有条目做归一化去重，预览分列「待写入 / 已存在跳过 / 合计」
- [ ] 按分类分组（中文文件用中文分类头，英文文件用英文分类头）
- [ ] 生成中英文双语版本（主语言事实源 → 从语言翻译）
- [ ] 输出预览计划表

**Validate（确认阶段）**：
- [ ] 展示预览内容给用户（包含中英文）
- [ ] 等待用户确认：写入 `[Unreleased]` / 指定版本 / 取消

**Handoff（执行阶段）**：
- [ ] 用户确认后执行写入
- [ ] 同时更新两个文件
- [ ] 输出确认信息

## W4: 规范检查（+check）

执行步骤：
- [ ] 读取 CHANGELOG.md 和 CHANGELOG.en.md
- [ ] 检查格式规范（标题层级、分类名称、日期格式）
- [ ] **分类标题语言**：中文文件英文头 / 英文文件中文头 → Unreleased 与新版本 **FAIL**；仅历史已发布区块 **WARN（历史遗留）**
- [ ] 检查内容质量（空版本、描述清晰度；空分类建议省略标题）
- [ ] 检查双语文档**结构同构**（可判定）：
  - 版本号集合一致
  - 各版本日期一致
  - 各版本分类集合一致（标题经中英映射后）
  - 各（版本×分类）条目数一致
  - 底部 link 的 version key 集合一致
- [ ] 检查链接：能发现 `origin` 时核对 `tagPrefix` 与 compare/release URL；不能发现则 WARN 占位
- [ ] 输出检查报告（参考 `references/output-template.md`）

## W5: 语言模式切换（+lang）

用于指定主语言，影响翻译方向：
- `+lang zh`：主语言为中文，英文由中文翻译生成
- `+lang en`：主语言为英文，中文由英文翻译生成

执行步骤：
- [ ] 将语言模式**落盘**到项目根 `.changelog-manager.json` 的 `primaryLang`（不存在则创建；默认 `zh`）
- [ ] 在后续 `+add` 和 `+generate` 中应用该模式（主语言手写，从语言生成）
- [ ] 输出当前语言模式与配置文件路径

### 项目 sidecar：`.changelog-manager.json`

```json
{
  "primaryLang": "zh",
  "keepIssueLinks": false,
  "tagPrefix": "v",
  "keepMarkers": false
}
```

| 字段 | 默认 | 含义 |
|------|------|------|
| `primaryLang` | `zh` | 翻译方向：主语言事实源，从语言生成 |
| `keepIssueLinks` | `false` | `+generate` 是否保留 `(#123)` |
| `tagPrefix` | `v` | 版本链接 / compare 的 tag 前缀 |
| `keepMarkers` | `false` | 是否在条目尾写 `<!-- cm:hash -->` 供幂等 |

- `+init` 可静默创建默认 sidecar。
- 该文件可不提交（个人偏好）；存在则所有快捷命令优先读取。
