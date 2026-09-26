# git-manager · Git 工作流安全护栏

<p align="center">
  <img src="assets/banner.svg" alt="git-manager" width="100%">
</p>

规范 Git 分支命名、Conventional Commits 提交信息、合并策略，所有危险操作强制二次确认。本文件是给你（人类）看的备忘——忘了 Git 操作规范，扫一眼这里。

## 一句话用法

> 当要提交 / 建分支 / 合并 / 解决 Git 错误 / 执行危险 Git 操作时，调 git-manager。它输出规范建议 + 危险操作闸（不确认不执行）。

常见调用：
- `帮我提交这些改动`
- `这个分支该怎么命名`
- `我要 force push，确认一下`

## 核心原则（备忘）

1. **安全第一**：所有危险操作必须用户明确确认后才执行
2. **可追溯**：每个提交必须有清晰信息，禁空信息
3. **最小干预**：不修改用户未请求的代码/文件

## 分支管理

- 禁直接在 main 开发；从最新 main 建功能分支
- 命名：`<type>/<description>`（feature/fix/docs/refactor/test/chore；常见扩展 hotfix/release）

## 提交规范（速查）

- 格式：`<type>(<scope>): <description>`
- 生成四步：分析 diff → 分组暂存（一逻辑单元一提交）→ 判定 Type/Scope/Description → 执行提交；详细命令 → `references/commit-message-flow.md`
- 祈使语气、首字母小写、结尾无句号、标题 ≤50 字符
- 破坏性变更两种标注：`<type>!` 或 `BREAKING CHANGE:` footer
- 类型完整清单与示例 → `references/conventional-commits.md`

## 危险操作（必须二次确认）

| 操作 | 影响 |
|------|------|
| `git push --force` | 覆盖远端历史 |
| `git branch -D` | 删除分支（不可恢复） |
| `git reset --hard` | 丢弃工作区+暂存区改动 |
| `git rebase -i` | 改写历史 |
| 删除未提交变更 | 丢失未保存工作 |

详细影响说明与恢复预案 → `references/dangerous-operations.md`

## 执行流程

```
确认分支状态 → 确定操作类型 → 告知用户将做什么 → 危险操作等确认 → 执行 → 输出结果
```

## 关联文件

- 主定义：[SKILL.md](./SKILL.md)
- 提交信息生成流程：[references/commit-message-flow.md](./references/commit-message-flow.md)
- 提交规范详解：[references/conventional-commits.md](./references/conventional-commits.md)
- 危险操作恢复预案：[references/dangerous-operations.md](./references/dangerous-operations.md)
- 触发词与边界：[references/trigger-when.md](./references/trigger-when.md)
- 版本：[CHANGELOG.md](./CHANGELOG.md)
