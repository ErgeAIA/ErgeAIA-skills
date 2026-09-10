---
name: init-env-checks
description: vibe-init 的环境检查契约：Git 仓库检测与初始化、codegraph 索引检测与集成、终端命令白名单与失败处理。
trigger-when: 执行 vibe-init 走到 Git 检查或 Codegraph 集成步骤时
role: workflow
reads-from:
  - <project>/.codegraph/（索引存在性）
writes-to:
  - <project>/.git/（仅 git init）
  - <project>/.codegraph/（仅 codegraph init）
---

# init 环境检查 · Git 与 Codegraph

## 终端命令白名单

本技能默认不运行终端命令；`vibe-init` 只放开下表命令，其余一律禁止。

| 命令 | 用途 | 性质 |
| ---- | ---- | ---- |
| `git rev-parse --is-inside-work-tree` | 判断是否已在 Git 仓库内 | 只读 |
| `git rev-parse --show-toplevel` | 定位仓库根，判断是本项目还是父项目 | 只读 |
| `codegraph --version` | 判断 codegraph 是否已安装 | 只读 |
| `codegraph status` | 补充索引信息，**不作判定依据** | 只读 |
| `git init` | 本项目非仓库时初始化 | 写 |
| `codegraph init` | 已安装且本项目无索引时建索引 | 写 |

**仍然禁止**：构建、测试、格式化、依赖安装、`git add` / `commit` / `push`，以及 `codegraph install` / `uninstall`（会改写各 agent 的配置与指令文件，属外部工具安装，只给建议不代做）。

执行规则：写操作执行前声明意图与目标路径；执行后如实记录退出码、关键输出与实际耗时；任何一条失败都不中断后续步骤，记入报告后继续。

## 一、Git 检查

| 判定 | 动作 |
| ---- | ---- |
| 返回假或报错 | 执行 `git init`，报告写「已初始化仓库，默认分支 <分支名>」 |
| 返回真，且 `--show-toplevel` == 项目根 | 跳过，报告写「本项目已是仓库，跳过」 |
| 返回真，但 `--show-toplevel` 在项目之上 | 跳过，报告写「位于父仓库 `<根路径>` 内，跳过」，**不建嵌套仓库** |

- 不做 `git add` / `commit`：是否提交由用户或其他技能决定。
- 不盲跑：先检测再决定，`git init` 只在判定为本项目非仓库时执行。
- 初始化后若需忽略索引产物，只在报告「建议」小节提示，不擅自改 `.gitignore`。

## 二、Codegraph 集成

判定顺序：先查是否安装，再查**本项目**是否已建索引。

- 安装检测：跑 `codegraph --version`，退出码 0 视为已安装；非 0 视为未安装
- 索引检测：只看**项目根下**是否存在 `.codegraph/`。codegraph 会向上取最近的索引，祖先目录的索引属于父项目，**不算本项目已有索引**
- 「项目有代码」的判据复用生成规范 §2 的「既有代码」信号（源码目录、依赖清单或锁定文件、有提交）
- 幂等：已有索引时不重复建；`codegraph index` 是全量重建，本步骤不调用
- `codegraph status` 只在需要展示索引统计时调用，其退出码不参与判定

| 是否安装 | 本项目是否已有索引 | 动作 |
| -------- | ------------------ | ---- |
| 是 | 否，且项目有代码 | 执行 `codegraph init`，报告写「已建索引，耗时 <N>」 |
| 是 | 是 | 跳过，报告写「本项目已有索引，跳过」 |
| 是 | 否，但项目尚无代码 | 跳过，报告写「无代码可索引，跳过」 |
| 否 | — | 不执行；在报告「建议」小节写清用途、安装命令、初始化命令与风险提示 |

**未安装时的建议文案**（写入报告，按此要点成文）：

- 用途：本地代码知识图谱，把代码库转成可查询的图，经 MCP 供 AI agent 调用；提供符号级检索、调用链浏览、改动影响面分析
- 安装命令：`npx @colbymchenry/codegraph`
- 初始化命令：`codegraph init`（在项目目录执行，建 `.codegraph/` 索引；每个项目各跑一次）
- 风险提示：`npx` 会下载并执行第三方安装器；安装器会改写各 agent 的 MCP 配置与指令文件（含 `AGENTS.md`、`CLAUDE.md` 的标记区块）、可选修改 `PATH`、为 Claude Code 写入 auto-allow 权限列表。执行前自行确认来源可信
- 留痕提醒：安装器若改动了 `AGENTS.md`，须在 `docs/.ai/agents-changelog.md` 补一行
- 忽略建议：若本项目已纳入 Git，考虑把索引目录 `.codegraph/` 加入 `.gitignore`（本技能不代改）

## 失败处理

| 触发条件 | 处理 |
| -------- | ---- |
| 本项目非仓库且 `git init` 失败 | 记「失败 + 原因」，继续后续步骤，不阻塞 |
| `git rev-parse --show-toplevel` 失败 | 按「项目根」处理，不阻塞 |
| `codegraph --version` 非 0 退出 | 视为未安装，走建议分支 |
| `codegraph init` 失败或超时 | 记「失败 + 原因 + 已耗时」，不自动重试，在报告建议里提示手动执行 |
| 命令输出含密钥或敏感路径 | 报告中脱敏或截断，只留结论 |
