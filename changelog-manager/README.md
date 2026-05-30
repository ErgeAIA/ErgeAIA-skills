# changelog-manager

项目更新日志（Changelog）维护助手，帮你规范化地记录和管理每个版本的显著变动。

## 核心功能

- 基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 规范
- 支持语义化版本（SemVer）
- 从 git 提交记录自动生成变更
- 手动追加条目 + 版本发布归档
- **双语言支持**：同时维护中文 CHANGELOG.md 和英文 CHANGELOG.en.md
- 规范化检查

## 快速开始

### 初始化（创建双语言文档）

```
+init 我的项目
```

生成 CHANGELOG.md 和 CHANGELOG.en.md。

### 日常记录

```
+add 新增了用户登录功能
+add 修复了首页加载慢的问题
```

自动分类写入 `[Unreleased]` 区块，同时更新中英文文档。

### 发布版本

```
+release 1.0.0
```

将 `[Unreleased]` 归档到新版本，自动填充日期和链接，同时更新中英文文档。

### 从 Git 生成

```
+generate
```

提取上次 tag 至今的提交，过滤噪音，按分类整理后预览确认写入，自动生成中英文双语版本。

### 检查规范性

```
+check
```

检查格式、日期、分类、链接，**检查双语文档一致性**，输出改进建议。

## 双语言模式

### 快捷命令

| 命令 | 说明 |
|------|------|
| `+init` | 初始化双语言 CHANGELOG |
| `+add` | 追加变更（同时更新中英文） |
| `+release` | 发布版本（同时更新中英文） |
| `+generate` | 从 Git 生成（双语预览） |
| `+check` | 检查规范性（含双语一致性） |
| `+lang zh` | 设置主语言为中文（默认） |
| `+lang en` | 设置主语言为英文 |

### 分类标题对照

| 英文 | 中文 |
|------|------|
| Added | 新增 |
| Changed | 变更 |
| Deprecated | 弃用 |
| Removed | 移除 |
| Fixed | 修复 |
| Security | 安全 |

## 工作流

```
日常开发 → +add 追加到 [Unreleased] → 发布时 +release 归档 → 循环
       ↓
   同时更新中英文文档
```

## 变更分类

| 分类 | 用途 | 示例 |
|------|------|------|
| Added | 新功能 | 支持 GitHub OAuth 登录 |
| Changed | 功能变更 | 升级 React 17 → 18 |
| Deprecated | 即将移除 | `legacyLogin()` 下版本移除 |
| Removed | 已移除 | 移除 v1.x API |
| Fixed | Bug 修复 | 修复 Safari 布局错位 |
| Security | 安全改进 | 修复 XSS 漏洞 |

## 适用场景

- 个人开发者维护多个项目
- 开源项目发布 release notes
- 小团队没有专门的 release manager
- 任何"每次发版都说下次一定写 changelog"的人

## 项目结构

```
changelog-manager/
├── SKILL.md                      # 技能定义
├── examples/
│   └── basic-usage.md           # 基础使用示例
└── references/
    ├── classification-guide.md  # 变更分类详细指南
    ├── git-extraction-rules.md   # Git 提交提取规则
    ├── bilingual-guide.md        # 双语言处理指南
    ├── output-template.md        # 输出模板
    ├── template-examples.md      # CHANGELOG 模板示例
    └── trigger-test-set.md       # 触发测试集
```

## 相关规范

- [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)
- [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
- [Conventional Commits](https://www.conventionalcommits.org/)

## License

MIT
