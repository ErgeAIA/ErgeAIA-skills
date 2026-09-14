# Project Overview — ErgeAIA-skills

> 本文件为深度背景，按需读取。Agent 协作规则以根 `AGENTS.md` 为准，本文件不承载可执行约束。

## 定位

个人能力宝库中的 **生产级 Agent Skill 合集仓库**，遵循 [Agent Skills 官方规范](https://agentskills.io/)，每个子目录是一个独立、可发布的 Agent Skill。仓库通过 GitHub 公开，用于 `npx skills add` 安装分发，不承载外部协作开发流程。

**技能清单与版本**：以根 [`README.md`](../README.md) / [`README.en.md`](../README.en.md) 技能表为**唯一真相源**，本文件不维护副本（同一事实两处存放必然漂移）。

根目录其他文件：`CHANGELOG.md` / `CHANGELOG.en.md`（纯人类文档，不触发 CI）、`LICENSE`（MIT）、`README.md` / `README.en.md`、`.gitignore`。

## 架构与依赖方向

- 纯文档 + Python 脚本，无后端、无数据库、无 `package.json`、无前端框架。
- 每个技能的 `references/` 按职责分层：`workflows/`、`rubrics/`、`specs/`、`config/`、`templates/`。
- `skill-workshop` 为合并产物：评审链（源自早期的 `skill-reviewer`，该技能已于 2026-09-10 删除，能力全部并入）+ 创建/评测链（源自 kz-skill-creator），双评估并存（**10 维 52 项**深度评审 + 8 维加权快速评分；子命令数量以该技能 `README.md` 为准，本文件不复述）。
- 分发链路：`npx skills add https://github.com/ErgeAIA/ErgeAIA-skills` 直读仓库安装，无 CI 发版（原 `release.yml` 发布流程已于 2026-09-12 退役）。

## 既有决策历史（可在决策矩阵 / 校验器中被引用）

| 时间 | 决策 | 原因 / 影响 |
|------|------|------------|
| 2026-08-19 | 版本号统一三段式 `X.Y.Z` | 消除两段式比较歧义；与 V0 校验联动 |
| 2026-08-19 | 内容三层分层 + 访问性核实为强制门禁 | 分离人类/ AI / 按需内容，核验引用路径 |
| 2026-08-19 | 分发链路：AI 只保证仓库最新，软链由用户工具链管理 | 避免 AI 碰运行态配置 |
| 2026-06-19 | V0 版本硬约束降级（有 `VERSION.md` 时放宽头部版本块） | `VERSION.md` 是人类维护点，frontmatter 是 LLM 决策点 |
| 2026-06-19 | CLI 加 PEP 723 内联依赖声明 | 零外部依赖直跑 |
| 2026-06-14 | skill-reviewer 定裁判角色，`P-V-E` → `P-V-H` | 只指方向不写对象文件 |
| 2026-06-14 | skill-workshop 合并双链 | 深度评审 + 快速评分并存 |

## 质量现状

- **测试**：本仓库当前无单元测试——原唯一测试（`skill-reviewer/tests/`，约 30 用例，`unittest`）随该技能删除；`skill-workshop` 一直无 `tests/` 目录。
- **CI**：无（2026-09-12 起；原 `.github/workflows/release.yml` 发布流程退役，push 到 main 不再触发任何自动化）。
- **文档同步度**：各技能 `VERSION.md` / `README.md` 为版本真源；根 README 双语技能表随升版同步（见 AGENTS 提交前自检）。**本文件不再维护技能索引表**。

## 风险与约束

- **平台**：本仓库常在 Windows / PowerShell 执行，`&&` 需换 `;`；脚本内有 Windows 路径假设。
- **覆盖缺口**：本仓库无单元测试；无 CI（校验靠本地运行 `skill-workshop` CLI）。
- **术语一致性**：评审术语锚定 `P-V-H`（Plan-Validate-Handoff）；用 `skill-workshop/scripts/skill_cli.py consistency` 检测旧术语残留。