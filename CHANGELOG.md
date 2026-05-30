# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/lang/zh-CN/spec/v2.0.0.html).

## [Unreleased]
_最后更新：2026-05-30_

## [1.1.1] - 2026-05-30

### Changed

- **GitHub Actions workflow 修复**
  - 修复打包方式：使用 `zip -r` 保留目录结构（技能目录作为 zip 根）
  - 修复版本检查逻辑：版本未递增时跳过而非报错
  - 修复步骤 id 引用问题
  - 移除 artifact 上传步骤（直接在 release 中附带）

## [1.1.0] - 2026-05-30

### changelog-manager v2.0.0

- **双语言支持升级**
  - 内置双语言支持，同时维护中文 CHANGELOG.md 和英文 CHANGELOG.en.md
  - 新增 `+lang` 快捷命令切换主语言模式（`+lang zh` / `+lang en`）
  - 新增 bilingual-guide.md 参考文档（60+ 术语对照表）
  - 新增 V4 双语文档一致性验证
  - 全部工作流（W0-W5）更新为同时操作两个文件
  - README.md 和 output-template.md 同步更新

## [1.0.0] - 2026-05-29

### Added

- **skill-reviewer v4.6** - 九维 48 项结构化评审与合规校验
  - 新增指导自由度分级声明（§5），明确三种模式的约束强度
  - 新增评测驱动迭代纪律（V4.1），规范 description 修改后的回归流程
  - 调整段落编号以保持结构一致性

- **changelog-manager v1.1.0** - 基于 Keep a Changelog 规范的更新日志维护助手
  - 支持从 git 提交记录自动生成变更
  - 支持手动追加条目和版本发布归档
  - 内置规范化检查功能

### Changed

- 将中文 README 设为默认版本，英文版更名为 README.en.md
- 同步更新项目根目录和 skill-reviewer 的 README 文件
- skill-reviewer 版本号更新至 v4.6

### Docs

- 添加 README.md（中文）和 README.en.md（英文）
- 添加对 base44/skills 项目的致谢
- 格式化评审检查清单表格并添加扩展字段指南

### Deprecated

- README.zh-CN.md 已合并至 README.md（中文版作为默认）
