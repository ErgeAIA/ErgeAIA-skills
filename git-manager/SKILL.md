---
name: git-manager
description: "当用户准备提交代码、创建或切换分支、合并、推送、拉取、rebase，或遇到 Git 错误时使用；负责提供规范的 Git 操作流程，并在删除变更、改写历史或强制推送等高风险操作前要求用户明确确认。"
metadata:
  author: ErgeAIA
  version: 1.3.3
---

# Git 工作流管理

## 描述

提供 Git 工作流管理指导，确保分支命名、提交信息、合并策略符合 Conventional Commits 规范，所有危险操作必须获得用户确认。

## 使用场景

### 触发条件

- 用户提及 Git 相关关键词（commit、branch、merge、rebase、PR、push、pull）
- 询问分支命名或提交信息写法
- 遇到 Git 错误需要帮助解决
- 准备执行危险操作（force push、删除分支、reset --hard）
- 完成代码变更准备提交时

### 不适用场景

- 纯代码编写（不涉及 Git 操作）
- 文件内容编辑或格式化
- 项目架构讨论（不涉及版本控制）

## 指令

### 核心原则

1. **安全第一**：所有危险操作必须获得用户明确确认后才执行
2. **可追溯**：每个提交必须有清晰的提交信息，禁止空信息提交
3. **最小干预**：不修改用户未请求的代码或文件

### 分支管理

- 禁止直接在 main 分支开发
- 从最新 main 分支创建功能分支
- 若用户已在 main 且有未提交改动，先 `git stash` 或 `git switch -c <分支>` 迁出，勿强制丢弃工作区（与下方危险操作闸一致）
- 分支命名格式：`<type>/<description>`（type: feature/fix/docs/refactor/test/chore，常见扩展：hotfix 紧急修复 / release 发布准备；hotfix 从 main 拉取并直接回 main，不可当作普通 feature）

### 提交规范（生成提交流程）

处理"帮我提交"类请求，按四步生成合规提交信息（详细操作与命令见 `references/commit-message-flow.md`）：

1. **分析 diff**：`git status --porcelain` 看变更概览；已暂存看 `git diff --staged`，未暂存看 `git diff`——先明确"改了什么"再写信息
2. **分组暂存**：一个逻辑单元一个提交；用 `git add <路径>` / `git add -p` 交互式选择；**绝不提交密钥**（.env / credentials / 私钥 / 连接串）
3. **判定三要素**：Type（变更类型，见下）→ Scope（影响模块，可选）→ Description（一句话：祈使语气、首字母小写、结尾不加句号、≤50 字符）
4. **执行提交**：单行 `git commit -m "<type>(<scope>): <description>"`；需 body/footer 时用 heredoc 多行

- 破坏性变更两种标注：`<type>!` 感叹号后缀（如 `feat!`），或 footer `BREAKING CHANGE: <说明>`
- 类型完整清单与示例详见 `references/conventional-commits.md`

### 合并策略

- 优先使用 Squash and merge
- 合并前确保分支同步到最新 main

### 危险操作（必须二次确认）

以下操作必须向用户明确说明影响，获得确认后才执行：

- `git push --force`（**禁止向 main/master 强推**）
- `git branch -D`
- `git reset --hard`
- `git rebase -i` / `git commit --amend`（修改提交历史）
- `git commit --no-verify`（跳过 hooks——仅用户明确要求时）
- 修改 `git config`（先说明全局 / 仓库级影响范围）
- 删除未提交的变更（含 `git stash drop` / `git clean -f` / `git checkout --` 等不可逆丢弃）

各危险操作的详细影响说明与恢复预案详见 `references/dangerous-operations.md`；触发词与适用边界详见 `references/trigger-when.md`。

### 执行流程

```
1. 确认当前分支状态（git status / git branch）
2. 根据任务确定操作类型
3. 执行操作前告知用户将要做什么
4. 危险操作：等待用户确认
5. 执行操作
6. 输出操作结果
```

## 示例

### 输入

```
帮我提交这些改动
```

### 输出

```
**操作**：git commit
**分支**：feature/user-login
**变更文件**：3 个

**建议提交信息**：
feat(auth): add JWT token validation

确认提交吗？
```
