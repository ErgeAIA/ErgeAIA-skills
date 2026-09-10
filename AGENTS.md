# AGENTS.md — ErgeAIA-skills

> 本文件是 Agent 协作协议，将被并入 system prompt 并可公开共享。只写入可强制执行的规则，解释性内容见 [`references/project-overview.md`](references/project-overview.md)。**绝不在此写入密钥、凭据、连接串。**

## Permissions（最高优先级）

**IMPORTANT: 本仓库是个人归档 + 技能分发仓库，非开源协作项目。**

- **YOU MUST**: 遵守 [Agent Skills 官方规范](https://agentskills.io/)；新增/修改技能必须满足合规要求（见「反直觉约定」）。
- **YOU MUST**: commit message 遵循 Conventional Commits（见「工具链」链路规则，详见仓库 `.trae/rules/git-commit-message.md`）。
- **YOU MUST**: 涉及版本变更时遵循三段式 `X.Y.Z`，并同步 `frontmatter.metadata.version` 与 `VERSION.md`。

**需确认（先停下说明影响，等待明确授权再执行）**：
- 删除文件/目录、修改凭据、数据库/数据变更、高风险 git 操作（`push --force` / `rebase` / `reset --hard`）、全局安装、对外发布、引入新框架/重大依赖、切换包管理器。

**禁止（不询问，直接不做）**：
- 触碰运行态软链（`~/.workbuddy/skills` / `~/.agents/skills`）——由用户工具链管理。
- 在任何配置文件 / 文档中写入密钥、token、账号凭据、连接串。
- 新建技能目录时覆盖或改写既有技能无授权的文件。

## 工具链与精确版本

- **运行时**: Python `>=3.10`。
  - `skill-workshop/scripts/skill_cli.py`：PEP 723 内联脚本（`requires-python = ">=3.10"`，`dependencies = []`，零第三方依赖）。
  - `skill-workshop` 校验脚本：`PyYAML` 为可选依赖（非必需）。
- **测试**: Python 内置 `unittest`。
- **包/环境**: `uv`（用于运行测试）。
- **分发/安装**: `npx skills`（Agent Skills CLI）。
- **CI/发布**: GitHub Actions（`.github/workflows/release.yml`）。
- **无**: `package.json`、Node 前端框架、后端、数据库。
- **版本合规约束**: 版本号强制三段式 `X.Y.Z`；`frontmatter.metadata.version` 为唯一必填版本点，技能含 `VERSION.md` 时头部版本块与版本历史 section 可选。

## 命令表

| 场景 | 原文命令 | 来源 |
|------|----------|------|
| 安装全部技能 | `npx skills add https://github.com/ErgeAIA/ErgeAIA-skills` | `README.md` |
| 安装指定技能 | `npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill changelog-manager` | `README.md` |
| 列出可安装技能 | `npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --list` | `README.md` |
| 查看 skill-workshop CLI | `cd skill-workshop; python scripts/skill_cli.py --help` | `scripts/skill_cli.py` |
| 运行 CLI 子命令 | `cd skill-workshop; python scripts/skill_cli.py <subcommand> --help` | `scripts/skill_cli.py` |
| 发布新版本 | `git push` 到 `main`（触发 GitHub Actions 自动打 tag + 打包 + 建 Release） | `.github/workflows/release.yml` |

**PowerShell 注意**: 本仓库在 Windows / PowerShell 环境执行，`&&` 需替换为 `;`；`release.yml` 在学生流程外（CI 内为 `bash`）。

## 反直觉约定

- **脚本纪律**（所有技能通用）: 无交互式输入（不得出现 `input()`）；CLI 支持 `--help`；结构化退出码 `0=PASS, 1=FAIL, 2=ERROR`；错误写 `stderr`、数据写 `stdout`；多数子命令支持 `--offset` / `--output` 截断。
- **Agent Skills 合规**（所有技能必须满足）: frontmatter 含 `name` + `description`；渐进式披露（`SKILL.md` 原则上 `<500` 行）；脚本无交互提示；CLI 支持 `--help`；结构化退出码；单元测试覆盖（新增规则须对应用例）。
- **内容三层分层**（强约束）: `README.md`=人类可读；`SKILL.md`=AI 执行规则（禁放人类可读内容）；`references/`=按需加载（文件须带 `trigger-when`，引用路径必须真实存在）。
- **`VERSION.md` 外置原则**: 版本演进记录放 `VERSION.md`，按需读取，不污染 `SKILL.md` 上下文。
- **命名**: Skill 名 hyphen-case，长度 `<=64`。
- **架构偏好**: `references/` 按 `workflows/` / `rubrics/` / `specs/` / `config/` / `templates/` 分层；工作流文件用语义化标记（`@工作流:` / `@步骤N:` / `@验证点`）与 frontmatter（`name` / `description` / `version` / `reads-from` / `writes-to` / `trigger-when`）；多工作流用「决策矩阵」表路由；关键决策/失败回退加 `🔴 CHECKPOINT` / `🛑 STOP` 标记。
- **.gitignore 要点**: `.trae/`、`.backups/`、`__pycache__/`、`reviews/`、`evals/results/`、`.vscode/`、`.idea/` 不入库；`reviews/`、`evals/results/` 是本地产物。

## 质量与文档指针

- **测试**: 本仓库**当前无单元测试**——原唯一测试（`skill-reviewer/tests/`，约 30 用例，`unittest`）随该技能删除；`skill-workshop` 一直**无** `tests/` 目录，向其前提功能时勿假定有测试覆盖。
- **CI**: `.github/workflows/release.yml`（`push` 到 `main`，仅 `changelog-manager/` 路径或 `CHANGELOG.md` 变更时触发），版本号从 `CHANGELOG.md` 头部提取，`CHANGELOG.en.md` 不触发 CI。
- **文档指针**: 技能入口 `SKILL.md` / `README.md` / `VERSION.md`；背景、决策历史、质量现状、风险 → [`references/project-overview.md`](references/project-overview.md)；顶层 README 仅作对外介绍，不复述规则。

## 自维护协议

1. 视 `AGENTS.md` 为代码：任何改动规则的变更，须在同一提交/任务中同步更新，否则视为规则漂移。
2. 就近更新：规则写入错误发生处最近的作用域；`references/` 内分层补充，不堆根文件。
3. 提交前自检：命令更名、重构、规范变更后核对本文件准确性，有过期示例立即更新。
4. 周期维护：随版本发布或定期审查，清除失效引用、已关闭事项、废弃约定。
5. 变更留痕：对 `AGENTS.md` 的每次规则改动，在 [`references/agents-decision-log.md`](references/agents-decision-log.md) 追加「旧值 → 处置 → 新值」记录，禁止静默覆盖既有决策。