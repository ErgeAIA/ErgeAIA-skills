# 输出模板

> 定义各工作流的输出格式，确保产出物结构一致、可机器判定。

## 1. CHANGELOG.md 和 CHANGELOG.en.md 输出模板

### 中文版 (CHANGELOG.md)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [VERSION] - YYYY-MM-DD

### Added
- 变更描述

### Changed
- 变更描述

### Deprecated
- 变更描述

### Removed
- 变更描述

### Fixed
- 变更描述

### Security
- 变更描述

[Unreleased]: https://github.com/USER/REPO/compare/vVERSION...HEAD
[VERSION]: https://github.com/USER/REPO/releases/tag/vVERSION
```

### 英文版 (CHANGELOG.en.md)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [VERSION] - YYYY-MM-DD

### Added
- Change description

### Changed
- Change description

### Deprecated
- Change description

### Removed
- Change description

### Fixed
- Change description

### Security
- Change description

[Unreleased]: https://github.com/USER/REPO/compare/vVERSION...HEAD
[VERSION]: https://github.com/USER/REPO/releases/tag/vVERSION
```

### 必含字段

| 字段 | 说明 | 格式要求 |
|------|------|----------|
| 标准头部 | Keep a Changelog + SemVer 声明 | 固定文案 |
| `[Unreleased]` | 未发布变更区块 | 必须存在，即使为空 |
| 版本标题 | `## [VERSION] - YYYY-MM-DD` | ISO 8601 日期 |
| 分类标题 | `### Added/Changed/...` | 仅使用6个标准分类 |
| 版本链接 | 底部链接定义 | 格式：`[VERSION]: URL` |

### 分类标题中英文对照

| 英文 | 中文 |
|------|------|
| Added | 新增 |
| Changed | 变更 |
| Deprecated | 弃用 |
| Removed | 移除 |
| Fixed | 修复 |
| Security | 安全 |

---

## 2. 检查报告输出模板（`+check`）

```markdown
# CHANGELOG 检查报告

## 检查结果

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 格式规范 | ✅/⚠️/❌ | 详情 |
| [Unreleased] 区块 | ✅/⚠️/❌ | 详情 |
| 日期格式 (ISO 8601) | ✅/⚠️/❌ | 详情 |
| 分类名称 | ✅/⚠️/❌ | 详情 |
| 版本链接 | ✅/⚠️/❌ | 详情 |

## 双语文档一致性检查

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 文件存在性 | ✅/⚠️/❌ | CHANGELOG.md 和 CHANGELOG.en.md 是否同时存在 |
| 版本区块对应 | ✅/⚠️/❌ | 版本号是否一一对应 |
| 变更条目数量 | ✅/⚠️/❌ | 同一版本的条目数量是否一致 |
| 分类结构一致性 | ✅/⚠️/❌ | 分类分组是否一致 |

## 内容质量

| 版本 | 问题 | 建议 |
|------|------|------|
| [VERSION] | 问题描述 | 改进建议 |

## 总评

- **通过项**：N 项
- **待改进**：N 项
- **建议**：整体建议

## 下一步行动

1. 具体改进建议
2. 具体改进建议
```

---

## 3. Git 生成预览模板（`+generate` Plan 阶段）

```markdown
# Git 提交变更预览

## 提取范围

- **起始**：vSTART 或首次提交
- **结束**：HEAD
- **提交数**：N 条（过滤后 M 条）

## 变更分类预览

### 中文版 (CHANGELOG.md)

### Added
- 变更描述（来源：commit hash 简写）
- 变更描述

### Changed
- 变更描述

### Fixed
- 变更描述

### 英文版 (CHANGELOG.en.md)

### Added
- Change description (source: commit hash)
- Change description

### Changed
- Change description

### Fixed
- Change description

## 确认选项

请选择：
1. 写入 `[Unreleased]`
2. 写入指定版本 `[VERSION]`
3. 取消
```

---

## 4. 发布确认模板（`+release`）

```markdown
# 版本发布确认

## 发布信息

- **版本号**：VERSION
- **发布日期**：YYYY-MM-DD
- **变更条目数**：N 条

## 变更摘要

| 分类 | 条目数 |
|------|--------|
| Added | N |
| Changed | N |
| Fixed | N |

## 版本号建议

根据变更内容，建议版本号：VERSION（理由：...）

## 已完成

✅ CHANGELOG.md 已更新
✅ CHANGELOG.en.md 已更新
✅ `[Unreleased]` 已归档至 [VERSION]
✅ 版本链接已更新

## 建议后续操作

```bash
git tag vVERSION
git push origin vVERSION
# GitHub Release 可手动创建或使用 gh release create
```
```

---

## 5. 初始化确认模板（`+init`）

```markdown
# CHANGELOG 初始化完成

## 创建信息

- **文件路径**：./CHANGELOG.md, ./CHANGELOG.en.md
- **项目名称**：PROJECT_NAME（如有）
- **模板类型**：双语言模板

## 已包含内容

- ✅ Keep a Changelog 格式声明
- ✅ SemVer 版本规范声明
- ✅ `[Unreleased]` 区块
- ✅ 中英文双语模板

## 下一步

使用 `+add` 开始记录变更：
```
+add 新增了XXX功能
```
```

---

## 输出格式验证标准

| 输出类型 | 必含段落 | 可机器判定 |
|----------|----------|------------|
| CHANGELOG.md | 标准头部 + [Unreleased] + 版本区块 | ✅ 正则匹配 |
| CHANGELOG.en.md | 标准头部 + [Unreleased] + 版本区块 | ✅ 正则匹配 |
| 双语一致性 | 版本区块对应 + 条目数量一致 | ✅ 结构化比对 |
| 检查报告 | 检查结果表格 + 双语一致性 + 总评 | ✅ 表格结构 |
| Git 预览 | 提取范围 + 中英文分类预览 + 确认选项 | ✅ 结构化 |
| 发布确认 | 发布信息 + 变更摘要 + 双语已完成 | ✅ 结构化 |
| 初始化确认 | 创建信息 + 双语模板 + 下一步 | ✅ 结构化 |