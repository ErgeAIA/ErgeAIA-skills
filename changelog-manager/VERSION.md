# Changelog

> 本文件记录 Skill 的版本演进历史。外置原则：历史信息按需读取，不污染 SKILL.md 上下文预算。

---

## v2.0.0 (2026-05-30)

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

## v1.1.0 (2026-05-29)

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
