# 基础使用示例

## 场景一：从零开始维护更新日志

### Step 1: 初始化

```
用户: +init 我的博客项目
```

Skill 会创建 `CHANGELOG.md`：

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
```

### Step 2: 日常追加变更

```
用户: +add 新增了文章搜索功能，支持按标题和标签搜索
```

Skill 自动归类为 `Added`，写入 `[Unreleased]`：

```markdown
## [Unreleased]

### Added
- 支持文章搜索功能，可按标题和标签进行搜索
```

```
用户: +add 修复了评论提交后页面不刷新的问题
```

Skill 自动归类为 `Fixed`：

```markdown
## [Unreleased]

### Added
- 支持文章搜索功能，可按标题和标签进行搜索

### Fixed
- 修复评论提交后页面不自动刷新的问题
```

### Step 3: 发布版本

```
用户: +release 0.1.0
```

Skill 将 `[Unreleased]` 归档，使用当天日期：

```markdown
## [Unreleased]

## [0.1.0] - 2024-05-29

### Added
- 支持文章搜索功能，可按标题和标签进行搜索

### Fixed
- 修复评论提交后页面不自动刷新的问题
```

---

## 场景二：从 Git 提交记录生成

```
用户: +generate
```

Skill 执行以下流程：
1. 运行 `git log` 获取上次 tag 至今的提交
2. 过滤噪音（合并提交、chore、style 等）
3. 将 commit message 转写为用户友好描述
4. 按分类分组展示预览：

```
以下是从 git 提交中提取的变更，请确认：

### Added
- 支持用户头像上传功能
- 新增文章草稿自动保存

### Fixed
- 修复移动端导航栏显示异常
- 修复图片上传偶尔失败的问题

### Changed
- 升级 Next.js 从 13 到 14

确认写入 [Unreleased] 吗？(Y/n)
```

用户确认后写入 CHANGELOG.md。

---

## 场景三：发布破坏性更新

```
用户: +release 2.0.0
```

当 `[Unreleased]` 中包含破坏性变更时，Skill 会：
1. 检测到破坏性变更标记
2. 建议使用 major 版本号
3. 在条目中标注 `⚠️ BREAKING`

```markdown
## [Unreleased]

## [2.0.0] - 2024-05-29

### Added
- 全新的插件系统，支持第三方扩展

### Changed
- ⚠️ BREAKING: 配置文件格式从 JSON 迁移至 YAML
- ⚠️ BREAKING: API 鉴权方式从 API Key 变更为 OAuth 2.0

### Removed
- 移除 v1.x 旧版插件接口
```

---

## 场景四：检查现有更新日志

```
用户: +check
```

Skill 读取 CHANGELOG.md 并输出检查报告：

```
✅ 格式检查通过
✅ 包含 [Unreleased] 区块
✅ 日期格式正确（ISO 8601）
✅ 分类名称标准

⚠️ 建议改进：
- [1.0.0] 版本缺少版本链接
- [0.9.0] 的 "Fixed" 分类中有 2 条描述过于简短，建议补充影响说明
```
