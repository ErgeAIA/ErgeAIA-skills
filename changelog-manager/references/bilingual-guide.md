# 双语言处理指南

> 定义中文和英文变更描述之间的翻译规则，确保双语文档一致性。

## 翻译原则

### 1. 保留技术术语

以下术语在翻译时保持原文，不翻译：

| 英文术语 | 中文说明 |
|----------|----------|
| API | API |
| SDK | SDK |
| CLI | CLI |
| REST | REST |
| GraphQL | GraphQL |
| JSON | JSON |
| XML | XML |
| YAML | YAML |
| URL | URL |
| HTTP | HTTP |
| HTTPS | HTTPS |
| WebSocket | WebSocket |
| WebRTC | WebRTC |
| OAuth | OAuth |
| JWT | JWT |
| SQL | SQL |
| NoSQL | NoSQL |
| CI/CD | CI/CD |
| Git | Git |
| GitHub | GitHub |
| Docker | Docker |
| Kubernetes | Kubernetes |
| Linux | Linux |
| macOS | macOS |
| Windows | Windows |
| iOS | iOS |
| Android | Android |
| Vue | Vue |
| React | React |
| Angular | Angular |
| Node.js | Node.js |
| Python | Python |
| Java | Java |
| Go | Go |
| Rust | Rust |
| TypeScript | TypeScript |
| JavaScript | JavaScript |
| HTML | HTML |
| CSS | CSS |
| SEO | SEO |
| UI | UI |
| UX | UX |
| MVP | MVP |
| POC | POC |
| PR | PR |
| Issue | Issue |
| Bug | Bug |
| Feature | Feature |

### 2. 分类标题翻译

| 英文 | 中文 |
|------|------|
| Added | 新增 |
| Changed | 变更 |
| Deprecated | 弃用 |
| Removed | 移除 |
| Fixed | 修复 |
| Security | 安全 |

### 3. 常用动词翻译对照

| 中文 | 英文 |
|------|------|
| 新增 | Add |
| 添加 | Add |
| 支持 | Support |
| 引入 | Introduce |
| 修复 | Fix |
| 解决 | Resolve |
| 修正 | Correct |
| 优化 | Optimize |
| 改进 | Improve |
| 调整 | Adjust |
| 升级 | Upgrade |
| 更新 | Update |
| 移除 | Remove |
| 删除 | Delete |
| 废弃 | Deprecate |
| 弃用 | Deprecate |
| 迁移 | Migrate |
| 重构 | Refactor |

### 4. 常用名词翻译对照

| 中文 | 英文 |
|------|------|
| 功能 | Feature |
| 模块 | Module |
| 组件 | Component |
| 服务 | Service |
| 接口 | Interface / API |
| 配置 | Configuration / Config |
| 文档 | Documentation / Docs |
| 测试 | Test |
| 错误 | Error |
| 异常 | Exception |
| 警告 | Warning |
| 性能 | Performance |
| 安全性 | Security |
| 兼容性 | Compatibility |
| 可用性 | Availability |
| 依赖 | Dependency |
| 版本 | Version |
| 发布 | Release |
| 迁移 | Migration |

## 翻译模式

### 主语言为中文（默认）

- 用户输入中文变更描述
- 自动翻译为英文
- 英文版使用翻译结果

### 主语言为英文

- 用户输入英文变更描述
- 自动翻译为中文
- 中文版使用翻译结果

## 翻译模板

### 功能新增

| 中文 | 英文 |
|------|------|
| 新增了 XXX 功能 | Add XXX feature |
| 添加了 XXX | Add XXX |
| 支持 XXX | Support XXX |
| 引入了 XXX | Introduce XXX |

### Bug 修复

| 中文 | 英文 |
|------|------|
| 修复了 XXX 问题 | Fix XXX issue |
| 修复了 XXX 的 Bug | Fix bug in XXX |
| 解决了 XXX | Resolve XXX |
| 修复 XXX | Fix XXX |

### 功能变更

| 中文 | 英文 |
|------|------|
| 优化了 XXX | Optimize XXX |
| 改进了 XXX | Improve XXX |
| 调整了 XXX | Adjust XXX |
| 升级了 XXX 到 YYY | Upgrade XXX to YYY |
| 更新了 XXX | Update XXX |

### 功能移除

| 中文 | 英文 |
|------|------|
| 移除了 XXX | Remove XXX |
| 删除了 XXX | Delete XXX |
| 废弃了 XXX | Deprecate XXX |

### 安全修复

| 中文 | 英文 |
|------|------|
| 修复了 XXX 安全漏洞 | Fix security vulnerability in XXX |
| 提升了 XXX 的安全性 | Enhance XXX security |

## 特殊处理

### 1. 破坏性变更

翻译时保留 "BREAKING" 标注：

| 中文 | 英文 |
|------|------|
| BREAKING: XXX | BREAKING: XXX |

### 2. 版本号和日期

保持原文，不翻译：

```
v1.0.0 -> v1.0.0
2024-01-15 -> 2024-01-15
```

### 3. 链接和引用

保持链接不变：

```
[Unreleased]: https://github.com/...
[1.0.0]: https://github.com/...
```

### 4. 占位符

保留占位符格式：

| 格式 | 说明 |
|------|------|
| `{xxx}` | 占位符，如 `{username}` |
| `<xxx>` | 占位符，如 `<api_key>` |
| `xxx` | 实际值，如 `v1.2.3` |

## 一致性检查清单

翻译完成后，检查以下项目：

- [ ] 版本号在两个文件中完全一致
- [ ] 日期格式相同（ISO 8601）
- [ ] 分类标题正确对应
- [ ] 条目数量一致
- [ ] 链接指向一致
- [ ] 技术术语保持原文
- [ ] 无截断或遗漏

## 示例

### 示例 1：功能新增

**用户输入：**
```
+add 新增了用户登录功能，支持手机号和邮箱登录
```

**中文版 (CHANGELOG.md)：**
```markdown
### Added
- 新增了用户登录功能，支持手机号和邮箱登录
```

**英文版 (CHANGELOG.en.md)：**
```markdown
### Added
- Add user login feature, support phone number and email login
```

### 示例 2：Bug 修复

**用户输入：**
```
+add 修复了 Safari 浏览器下页面布局错位的问题
```

**中文版 (CHANGELOG.md)：**
```markdown
### Fixed
- 修复了 Safari 浏览器下页面布局错位的问题
```

**英文版 (CHANGELOG.en.md)：**
```markdown
### Fixed
- Fix page layout misalignment issue in Safari browser
```

### 示例 3：破坏性变更

**用户输入：**
```
+add BREAKING: 重命名 getUser 为 fetchUser
```

**中文版 (CHANGELOG.md)：**
```markdown
### Changed
- BREAKING: 重命名 getUser 为 fetchUser
```

**英文版 (CHANGELOG.en.md)：**
```markdown
### Changed
- BREAKING: Rename getUser to fetchUser
```

### 示例 4：安全修复

**用户输入：**
```
+add 修复了 XSS 跨站脚本攻击漏洞
```

**中文版 (CHANGELOG.md)：**
```markdown
### Security
- 修复了 XSS 跨站脚本攻击漏洞
```

**英文版 (CHANGELOG.en.md)：**
```markdown
### Security
- Fix XSS cross-site scripting vulnerability
```

## 参考资源

- [Keep a Changelog (English)](https://keepachangelog.com/en/1.0.0/)
- [Keep a Changelog (中文)](https://keepachangelog.com/zh-CN/1.0.0/)
- [Semantic Versioning](https://semver.org/)
