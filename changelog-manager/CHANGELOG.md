# Changelog

> 本文件记录 Skill 的版本演进历史。外置原则：历史信息按需读取，不污染 SKILL.md 上下文预算。

---

## 2.1.3 (2026-09-26)

### description 按 Trigger+Job+Boundary 重写

- Trigger 先行；同义词堆改任务句；Not for 不变。

## 2.1.2 (2026-09-24)

### 渐进式披露优化

- 删除 YAML 头 `compatibility` 字段（与正文「运行时要求」重复，且 YAML 头常驻 agent 上下文，属上下文浪费）；其安全约束「git 仅只读、绝不执行 commit/add/push/tag/release」并入「运行时要求」。
- 将 W0–W5 详细步骤、失败处理表与 `.changelog-manager.json` sidecar 字段下沉到新 reference `references/workflows.md`；SKILL.md 仅保留路由摘要 + CHECKPOINT 指针。
- SKILL.md 由 340 行降至约 200 行；触发条件句尾多余 `**` 一并清理。

## 2.1.1 (2026-09-24)

### skill-workshop 复审查清理

- 删除 SKILL.md 内联「分类标题中英文对照」表与中英文标准格式模板（与 `bilingual-guide.md` / `template-examples.md` 重复），改为指向 references 的唯一真相源，降低上下文成本（SSOT）。
- 合并「操作反例黑名单」入 Gotchas（反模式已被执行原则 verify 与危险动作覆盖），补齐「单条单分类」「只记外部行为变更」两条。
- description 精简：去掉文件名实现细节、补「发版记录 / release notes」触发同义词，保留 Not for 边界。
- 触发条件去掉 `CRITICAL` 强制句式；渐进式披露表补 `trigger-test-set.md` 行。
- 删除纯人类向的「角色」小节；新增 `compatibility` 字段说明运行约束（可选 git 只读、无第三方依赖、产物落调用方目录）。
- 技能自身 CHANGELOG 版本号去 `v` 前缀，与 `metadata.version` 对齐。
- README / README.en.md 项目结构树补全 `assets/`、`CHANGELOG.md`、`README.en.md`；分类标题对照改为指向 SSOT。

## 2.1.0 (2026-09-14)

### 完整性加固（审查 Spec：changelog-manager-integrity）

- **中文分类头强制**：中文 `CHANGELOG.md` 使用 `### 新增/变更/弃用/移除/修复/安全`；英文文件保持 `### Added` 等。唯一对照表在 `bilingual-guide.md`；`+check` 对新写入 FAIL、对历史英文头 WARN。
- **消灭 perf 规则矛盾**：`perf` 默认保留并映射为 Changed，不再出现在跳过表。
- **`+lang` 落盘**：`.changelog-manager.json` sidecar（`primaryLang` / `keepIssueLinks` / `tagPrefix` / `keepMarkers`），`+init` 静默创建默认值。
- **`+generate` 幂等**：归一化去重；预览分列待写入 / 已存在跳过；hash 仅内部使用，默认不写入正文。
- **Git 边界**：无 tag 回退、非法 range、浅克隆 WARN、非 git 提示手动模式。
- **中文文件头部本地化**（`# 更新日志` + 中文导语）。
- **`+check` 结构同构**：版本集合/日期/分类集合/条目数/link key 可判定比对。
- 文档触点：SKILL.md、bilingual/git-extraction/template-output/classification、`examples/basic-usage`、双语 README、根索引版本。
- **审查修复**：bilingual-guide 示例与 basic-usage 的中文侧分类头改为中文，消除 SSOT 自相矛盾。

---

## 2.0.1 (2026-09-12)

### references 补 trigger-when 加载指引

- 6 个 `references/` 文件（bilingual-guide / classification-guide / git-extraction-rules / output-template / template-examples / trigger-test-set）补 frontmatter `description` + `trigger-when`——对齐 AGENTS.md「内容三层分层」强约束（references 文件须带 trigger-when），checklist C4 由 6 条 FAIL 清零。
- 加载条件逐条对齐 SKILL.md §渐进式披露表既有表述，纯元数据增补，无行为变更。

## 2.0.0 (2026-05-30)

### 双语言支持升级

**核心变更**：内置双语言支持，同时维护中文 CHANGELOG.md 和英文 CHANGELOG.en.md。

**SKILL.md 升级**

- **description 更新**：新增"内置双语言支持"说明
- **核心目标**：新增第 5 条"同时维护中文和英文双语文档"
- **快捷命令**：新增 `+lang` 切换主语言模式（`+lang zh` / `+lang en`）
- **执行原则**：新增原则 6（双语言同步原则）和原则 7（双语文档一致性原则）
- **标准格式**：新增中英文模板对照和分类标题对照表
- **工作流路由**：全部 5 个工作流（W0-W5）均更新为同时操作两个文件
- **参考文档**：新增 `bilingual-guide.md` 引用
- **验证闭环**：新增 V4 双语一致性验证
- **运行时要求**：新增翻译能力说明

**references/ 升级**

- **output-template.md**：
  - 新增英文版 CHANGELOG.en.md 模板
  - 检查报告模板新增双语文档一致性检查表
  - Git 生成预览、发布确认、初始化确认模板均更新为双语版本
- **bilingual-guide.md**（新建）：
  - 技术术语保留原文对照表（60+ 术语）
  - 常用动词/名词翻译对照
  - 翻译模式和模板
  - 特殊处理规则
  - 4 个完整示例

**README.md 升级**

- 新增"双语言模式"说明章节
- 更新所有工作流说明，强调同步更新
- 新增快捷命令对照表
- 更新项目结构说明

**项目安装说明更新**

- README.md：使用 `--skill` 参数正确指定单个技能安装
- README.en.md：同步更新
- changelog-manager 版本号从 v1.1.0 更新到 v2.0.0

---

## 1.1.0 (2026-05-29)

### 初始版本

**基础功能**

- 基于 Keep a Changelog 规范
- 支持语义化版本（SemVer）管理
- 从 git 提交记录自动生成变更
- 手动追加条目 + 版本发布归档
- 规范化检查

**快捷命令**

| 命令 | 说明 |
|------|------|
| `+init` | 初始化 CHANGELOG.md |
| `+add` | 追加变更条目到 Unreleased |
| `+release` | 发布新版本（归档 Unreleased） |
| `+generate` | 从 git 提交记录生成变更 |
| `+check` | 检查更新日志规范性 |

**参考文档**

- `classification-guide.md`：变更分类详细指南
- `git-extraction-rules.md`：Git 提交提取规则
- `output-template.md`：输出模板
- `template-examples.md`：CHANGELOG 模板示例
- `trigger-test-set.md`：触发测试集
