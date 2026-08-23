# AGENTS.md 决策变更日志

> 记录 AGENTS.md 的「既有决策处置」凭证。每条一行的表格：既有决策（旧值）→ 处置 → 新值 / 删除原因。
> 语义：**存 keep**=原样继承；**改 update**=以现状为准更新；**删 drop**=移除；**并 merge**=合并去重；**移 move**=下沉到 references。

## 2026-08-19 重构（合作协议规范重组）

本次将上一版解释性 AGENTS.md 重组为「合作协议」格式：规则置顶、解释下沉、命令带来源、版本精确化。

| # | 既有决策（旧值） | 处置 | 新值 / 原因 |
|---|------------------|------|------------|
| 1 | 「禁止擅自修改」小节 | 改 | 置顶为 `Permissions` 区，加 `IMPORTANT:` / `YOU MUST:` 强标识，明确可做/需确认/禁止三元边界 |
| 2 | Project Overview 描述段 | 移 | 下沉至 `references/project-overview.md`（解释性内容不进根契约） |
| 3 | Decision Log 表 | 移 | 下沉至 `references/project-overview.md#既有决策历史` |
| 4 | Current Progress 清单 | 移 | 质量现状并入 `references/project-overview.md#质量现状` |
| 5 | Tech Stack 段 | 改 | 重组为「工具链与精确版本」，补充 Python `>=3.10`、`PyYAML optional`、零依赖 PEP 723 的明确版本约束 |
| 6 | Critical Commands 表 | 改 | 命令表增加「来源」列；`cd ... && ...` 改为 PowerShell 兼容的 `cd ...; ...`（Windows 环境 `&&` 不可用，等价于 README 原命令） |
| 7 | CLI 约定 / Agent Skills 合规 / 命名版本 / 三层分层 | 存 | 原样继承，并入「反直觉约定」章节 |
| 8 | 架构偏好 / .gitignore | 存 | 原样继承至「反直觉约定」 |
| 9 | 无自维护协议 | 新增 | 新增「自维护协议」固定章节（5 条命令性规范） |
| 10 | README.md 中可复述内容（作者信息、价值主张、安装示意） | 删 | 根 AGENTS.md 不复述，改在质量与文档指针指向 README.md |

**未被覆盖的既有决策**：上表 2/3/4 项内容未丢失，均迁移至 `references/project-overview.md`，根文件仅保留指针，符合「解释性内容归 README/背景文档」原则。