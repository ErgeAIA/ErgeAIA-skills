# Project Overview — ErgeAIA-skills

> 本文件为深度背景，按需读取。Agent 协作规则以根 `AGENTS.md` 为准，本文件不承载可执行约束。

## 定位

个人能力宝库中的 **生产级 Agent Skill 合集仓库**，遵循 [Agent Skills 官方规范](https://agentskills.io/)，每个子目录是一个独立、可发布的 Agent Skill。仓库通过 GitHub 公开，用于 `npx skills add` 安装分发，不承载外部协作开发流程。

## 目录索引

| 技能目录 | 功能 | 版本 | 入口 |
|---------|------|------|------|
| `skill-reviewer/` | 九维 48 项结构化评审与合规校验（裁判角色：只审不改） | v4.6.0 | `SKILL.md` + `scripts/validate_review.py` |
| `skill-workshop/` | Skill 全生命周期：创建 / 评审 / 重构 / 评测，16 个 CLI 子命令 | v1.17.0 | `SKILL.md` + `scripts/skill_cli.py` |
| `changelog-manager/` | 基于 Keep a Changelog 的更新日志助手，双语言 | v2.0.0 | `SKILL.md` |

根目录其他文件：`.github/workflows/release.yml`（发版）、`CHANGELOG.md` / `CHANGELOG.en.md`、`LICENSE`（MIT）、`README.md` / `README.en.md`、`.gitignore`。

## 架构与依赖方向

- 纯文档 + Python 脚本，无后端、无数据库、无 `package.json`、无前端框架。
- 每个技能的 `references/` 按职责分层：`workflows/`、`rubrics/`、`specs/`、`config/`、`templates/`。
- `skill-workshop` 为合并产物：评审链（源自 skill-reviewer）+ 创建/评测链（源自 kz-skill-creator），双评估并存（9 维 48 项深度评审 + 8 维加权快速评分）。
- 发布链路：`git push` 到 main → `release.yml` 读取 `CHANGELOG.md` 头部版本号 → 打 tag 并 `zip` 打包技能 → 创建 Release。

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

- **测试**：仅 `skill-reviewer/tests/test_validate_review.py`（约 30 用例，`unittest`）；`skill-workshop` 无 `tests/` 目录。
- **CI**：`.github/workflows/release.yml`（main 推送触发，仅覆盖 `changelog-manager/` / `skill-reviewer/` 路径变更）。
- **文档同步度**：各技能 VERSION.md / README 持续更新；`CHANGELOG.md` `[Unreleased]` 处记录 skill-workshop 加入，仍属进行中。

## 风险与约束

- **平台**：本仓库常在 Windows / PowerShell 执行，`&&` 需换 `;`；脚本内有 Windows 路径假设（见 skill-reviewer Gotchas）。
- **覆盖缺口**：`skill-workshop` 缺单元测试；CI 未覆盖 `skill-workshop/` 路径与 `CHANGELOG.en.md`。
- **术语一致性**：评审术语锚定 `P-V-H`（Plan-Validate-Handoff），`validate_review.py --consistency` 用于检测旧术语残留。