# CHANGELOG 模板示例

## 1. 标准模板（通用项目）

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

[Unreleased]: https://github.com/username/repo/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/username/repo/releases/tag/v0.1.0
```

## 2. Web 应用项目

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.2.0] - 2024-03-15

### Added
- 用户个人中心页面，支持修改头像和昵称
- 数据看板，展示关键业务指标
- 支持暗色模式切换

### Changed
- 首页布局重新设计，提升信息密度
- 列表页默认每页显示数量从 10 调整为 20
- ⚠️ BREAKING: 用户 API 接口鉴权方式从 Session 迁移至 JWT

### Deprecated
- 旧版数据导出接口 `/api/v1/export` 将在 v2.0 移除

### Fixed
- 修复移动端侧边栏无法收起的问题
- 修复上传文件超过 10MB 时进度条卡住的问题
- 修复 Firefox 下表格排序功能异常

### Security
- 修复文件上传路径遍历漏洞（CVE-2024-XXXX）
- 升级 express 至 4.18.3 修复已知安全问题

## [1.1.0] - 2024-02-01

### Added
- 用户注册与登录功能
- 邮箱验证流程
- 忘记密码重置功能

### Fixed
- 修复注册时用户名大小写敏感的问题
- 修复验证邮件链接过期时间不正确的问题

## [1.0.0] - 2024-01-15

### Added
- 项目初始化
- 基础框架搭建
- 用户管理 CRUD

[Unreleased]: https://github.com/username/webapp/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/username/webapp/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/username/webapp/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/username/webapp/releases/tag/v1.0.0
```

## 3. CLI 工具 / 库项目

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [2.1.0] - 2024-03-20

### Added
- 新增 `--watch` 参数，支持文件变化自动重新执行
- 新增 `transform()` 插件接口，支持自定义转换逻辑
- 新增 TypeScript 类型定义文件

### Changed
- 默认输出格式从 JSON 变更为 YAML
- ⚠️ BREAKING: `parse()` 方法签名变更，第二个参数从 `options` 对象改为独立的 `config` 参数
- 最低支持 Node.js 版本从 14 提升至 18

### Deprecated
- `legacyParse()` 方法将在 v3.0 移除，请使用 `parse()`

### Removed
- 移除对 Node.js 12 的支持

### Fixed
- 修复处理大文件（>100MB）时的内存溢出问题
- 修复 Windows 下路径分隔符处理错误

### Security
- 修复依赖 `minimist` 原型污染漏洞

## [2.0.0] - 2024-01-10

### Added
- 全新 API 设计，更简洁的调用方式
- 支持流式处理大文件
- 插件系统

### Changed
- ⚠️ BREAKING: 完全重写 API，不兼容 v1.x
- ⚠️ BREAKING: 配置文件格式从 JSON 变更为 TOML

### Removed
- 移除所有 v1.x 兼容性代码
- 移除 `--old-mode` 参数

[Unreleased]: https://github.com/username/cli-tool/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/username/cli-tool/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/username/cli-tool/releases/tag/v2.0.0
```

## 4. 简约版模板（小型项目）

```markdown
# Changelog

## [Unreleased]

## [0.2.0] - 2024-03-01

### Added
- 新增搜索功能
- 支持键盘快捷键操作

### Fixed
- 修复页面刷新后数据丢失的问题

## [0.1.0] - 2024-02-15

### Added
- 初始版本发布
- 基础 CRUD 功能
```

## 5. 包含 YANKED 版本的模板

```markdown
# Changelog

## [Unreleased]

## [1.2.1] - 2024-04-01

### Fixed
- 修复 v1.2.0 引入的数据库连接池泄漏问题

## [1.2.0] - 2024-03-28 [YANKED]

### Added
- 新增批量导入功能

> ⚠️ 此版本因严重数据损坏问题已被撤回，请升级至 v1.2.1

## [1.1.0] - 2024-03-01

### Added
- 新增数据导出功能

[Unreleased]: https://github.com/username/repo/compare/v1.2.1...HEAD
[1.2.1]: https://github.com/username/repo/compare/v1.1.0...v1.2.1
[1.2.0]: https://github.com/username/repo/releases/tag/v1.2.0
[1.1.0]: https://github.com/username/repo/releases/tag/v1.1.0
```

## 使用建议

- **新项目**：使用标准模板初始化，根据项目类型参考对应示例
- **已有项目**：从最近的版本开始记录，不需要追溯历史版本
- **个人项目**：可以使用简约版模板，减少维护负担
- **开源项目**：建议使用完整模板，包含版本链接
