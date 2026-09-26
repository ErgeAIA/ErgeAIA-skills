# 提交信息生成流程（Commit Message Flow）

> 本文件承载 SKILL.md「提交规范」四步流程的详细操作指引。规范以本文件 + `conventional-commits.md` 为单一真相源。

## 四步流程

### 1. 分析 diff（改了什么）

```bash
# 变更概览（机器可读，含未跟踪文件）
git status --porcelain

# 已暂存内容 → 看将提交的 diff
git diff --staged

# 未暂存内容 → 看工作区 diff
git diff

# 变更统计（可选）
git diff --stat
```

判定：**这次改动是一件事还是多件事？** 一件事 → 直接进入第 3 步；多件事 → 按第 2 步分组提交。

### 2. 分组暂存（一次提交 = 一个逻辑变更）

```bash
# 按文件
git add path/to/file1 path/to/file2

# 按模式（如只提测试文件）
git add '*.test.*'

# 交互式选择 hunk（大文件的部分修改）
git add -p
```

原则：

- **一个逻辑单元一个提交**（如"加功能 A"与"修 bug B"分两个提交）
- 混合改动（重构 + 新功能）按逻辑拆分暂存
- **绝不提交密钥**：.env、credentials、私钥、连接串——提交前检查 `git status` 未跟踪清单，发现即停下提醒用户

### 3. 判定三要素（Type / Scope / Description）

**Type**：按 `conventional-commits.md` 类型表判定——新增功能 `feat`、修复 `fix`、文档 `docs`、纯格式 `style`、重构 `refactor`、性能 `perf`、测试 `test`、构建/依赖 `build`、CI `ci`、杂项 `chore`、回滚 `revert`。

**Scope**（可选）：影响模块/领域（如 `feat(auth)`）；无明确模块可不写。

**Description**：

- 祈使语气（"add" 不 "added"、"fix bug" 不 "fixes bug"）
- 首字母小写、结尾不加句号
- ≤50 字符（外部 git-commit 技能建议 <72，本技能从严取 ≤50）
- 一行说清"做了什么"，不写"为什么"（为什么进 body）

### 4. 执行提交

```bash
# 单行（无 body/footer）
git commit -m "<type>(<scope>): <description>"

# 多行（body/footer 用 heredoc）
git commit -m "$(cat <<'EOF'
<type>(<scope>): <description>

<可选 body：为什么改、怎么改>

<可选 footer：BREAKING CHANGE / Closes #123 / Refs #456>
EOF
)"
```

## 破坏性变更（Breaking Changes）

两种标注（择一）：

```text
# 方式一：type/scope 后加感叹号
feat!: remove deprecated v1 API

# 方式二：footer 中 BREAKING CHANGE（推荐——可附详细说明）
feat: allow config to extend other configs

BREAKING CHANGE: `extends` key behavior changed
```

## 引用 issue

- 关闭：`Closes #123`
- 关联：`Refs #456`

## 提交安全协议（Git Safety Protocol）

- **不擅自改 git config**：需改（如 user.name/email）→ 先说明全局 vs 仓库级影响范围，交用户确认
- **不跳过 hooks**：`--no-verify` 仅在用户明确要求时使用，并提示"跳过了 lint/测试门禁"
- **hooks 失败**：先修问题，再**新建提交**——不 `--amend` 改写
- **不向 main/master force push**：改写远端历史一律先确认，优先推荐 `--force-with-lease`
- **amend 改写历史**：已推送的提交禁止 amend（等同改写历史，需用户确认）

## 与既有规范的关系

- 类型 / 格式规则以 `conventional-commits.md` 为单一真相源，本文件不重复列举
- 危险操作闸（--amend / --no-verify / config / force push）详见 `dangerous-operations.md`
