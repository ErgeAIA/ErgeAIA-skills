# Git 提交提取规则

## 概述

从 git 提交记录生成更新日志时，需要经过：**过滤 → 分类 → 转写** 三个步骤。

## 第一步：过滤噪音

### 应跳过的提交

| 模式 | 说明 |
|------|------|
| `Merge pull request #*` | GitHub 合并提交 |
| `Merge branch '*' into *` | 分支合并 |
| `Merge remote-tracking branch *` | 远程分支合并 |
| `fix merge conflict` | 冲突解决 |
| `revert *` | 回退提交（除非是独立的用户可见变更） |
| `chore:*` | 杂项（依赖更新除外） |
| `style:*` | 代码格式 |
| `refactor:*` | 内部重构（不影响外部行为） |
| `test:*` | 测试相关（除非新增了重要测试框架） |
| `docs:*` | 文档更新（除非是用户面向文档的重大更新） |
| `ci:*` | CI/CD 配置 |
| `build:*` | 构建系统配置 |
| `perf:*` | 性能优化（可归入 Changed） |
| `Initial commit` | 初始提交 |
| `update readme` | README 更新 |
| `bump version` | 版本号更新 |
| `wip` / `work in progress` | 进行中的工作 |

### 应保留的提交

| 模式 | 映射分类 |
|------|---------|
| `feat:*` / `feature:*` | Added |
| `fix:*` / `bugfix:*` / `bug:*` | Fixed |
| `breaking:*` / `breaking change:*` | Changed (BREAKING) |
| `deprecate:*` | Deprecated |
| `remove:*` / `delete:*` | Removed |
| `security:*` / `vulnerability:*` | Security |
| `change:*` / `update:*` / `improve:*` | Changed |
| `add:*` | Added |

### 特殊处理

- **依赖升级**：如果涉及安全修复（如 `npm audit fix`），归入 `Security`；否则归入 `Changed`
- **无前缀的提交**：根据内容判断分类，无法判断时归入 `Changed`
- **包含 `BREAKING CHANGE` 或 `!` 的提交**：归入 `Changed`，标注为破坏性变更

## 第二步：分类

### Conventional Commit 映射表

| Conventional Commit 类型 | Changelog 分类 |
|------------------------|---------------|
| `feat` | Added |
| `fix` | Fixed |
| `docs` | 跳过（除非用户文档） |
| `style` | 跳过 |
| `refactor` | 跳过（除非影响公共 API） |
| `perf` | Changed |
| `test` | 跳过 |
| `build` | 跳过 |
| `ci` | 跳过 |
| `chore` | 跳过 |
| `revert` | 跳过 |

### 分类优先级

当提交可能属于多个分类时：
1. `Security` > `Fixed` > `Changed` > `Added` > `Deprecated` > `Removed`
2. 如果 commit 中包含 `BREAKING CHANGE` footer，优先归入 `Changed`

## 第三步：转写

### 转写原则

将技术性的 commit message 转写为用户友好的描述：

| 原始 Commit | 转写后 |
|------------|--------|
| `feat(auth): add jwt token refresh` | 支持 JWT Token 自动刷新 |
| `fix(api): handle null response from server` | 修复服务端返回空数据时接口报错的问题 |
| `feat: implement user avatar upload (#42)` | 支持用户上传头像 |
| `fix: resolve memory leak in websocket connection` | 修复 WebSocket 连接的内存泄漏问题 |
| `breaking: rename getUser to fetchUser` | ⚠️ BREAKING: `getUser()` 重命名为 `fetchUser()` |

### 转写规则

1. **去掉技术前缀**：移除 `feat:`, `fix:` 等 conventional commit 前缀
2. **去掉 scope**：移除 `(auth)`, `(api)` 等 scope 标记
3. **去掉 PR/Issue 编号**：移除 `(#123)` 等引用（除非用户要求保留）
4. **转译为用户语言**：将开发者术语转为用户可理解的描述
5. **补充上下文**：必要时补充"为什么"和"影响是什么"
6. **中文项目用中文**：如果项目面向中文用户，使用中文描述

### 转写模板

```
[动词] + [对象] + [补充说明（可选）]
```

**动词参考：**
- 新增：支持、新增、添加、引入
- 修复：修复、解决、修正
- 变更：优化、调整、改进、升级、更新
- 移除：移除、删除、废弃
- 安全：修复...安全漏洞、升级...修复...漏洞

## Git 命令参考

### 获取上次 tag 至今的提交

```bash
git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:"%s"
```

### 获取指定版本范围的提交

```bash
git log v1.0.0..v1.1.0 --pretty=format:"%s"
```

### 获取提交详情（含 body）

```bash
git log --pretty=format:"%s%n%b" --separator="---"
```

### 获取上次 tag

```bash
git describe --tags --abbrev=0
```

## 输出格式

生成后的变更条目应按分类分组，每组内按重要性排序：

```markdown
### Added
- 支持用户上传头像
- 新增数据导出为 Excel 功能

### Changed
- 优化首页加载速度，响应时间减少 40%
- ⚠️ BREAKING: API 响应格式从 `{code, data}` 变更为 `{status, result}`

### Fixed
- 修复 Safari 浏览器下登录页面样式错位
- 修复并发场景下数据不一致的问题
```
