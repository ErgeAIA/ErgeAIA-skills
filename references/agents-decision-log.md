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

## 2026-09-10 删除已废弃技能 skill-reviewer

该技能早前已标废弃（README 索引划线、release 流程移除），本次按用户指令**物理删除目录**，并同步清理全部引用：

| # | 既有决策（旧值） | 处置 | 新值 / 原因 |
|---|------------------|------|------------|
| 1 | `skill-reviewer/`（v4.6.0，九维 48 项评审，36 文件 / 170.9 KB） | 删 | 能力已全部并入 `skill-workshop` 评审链；发布流程早已移除该技能 |
| 2 | `README.md` / `README.en.md` 技能索引的 skill-reviewer 行（原已划废弃线） | 删 | 目录不存在，索引行成悬空链接 |
| 3 | 根 `AGENTS.md` 命令表「跑 skill-reviewer 测试」行 | 删 | 对象目录已删除，命令不可执行 |
| 4 | 根 `AGENTS.md` 工具链「`skill-reviewer` 校验脚本：`PyYAML` 可选依赖」 | 改 | 改指 `skill-workshop` 校验脚本——实测 `skill-workshop/scripts/_impl/{review_ops,utils}.py` 仍 `import yaml`，依赖归属随之转移且描述继续成立 |
| 5 | 根 `AGENTS.md` 与 `references/project-overview.md` 的「测试」段 | 改 | 如实改写为「本仓库当前无单元测试」（原唯一测试随该技能删除），避免留下失效路径 |
| 6 | `references/project-overview.md` 目录索引的 skill-reviewer 行 | 删 | 同上；其「评审链源自 skill-reviewer」的溯源描述**保留**（历史属实） |
| 7 | `references/project-overview.md` 风险段「见 skill-reviewer Gotchas」括注 | 删 | 指向目标已不存在；Windows 路径假设的表述本身保留 |
| 8 | `references/project-overview.md` 术语一致性段引用的 `validate_review.py --consistency` | 改 | 该脚本随技能删除；改为 `skill-workshop/scripts/skill_cli.py consistency`（功能等价） |

**未同步的位置（有意保留）**：`CHANGELOG.md` / `CHANGELOG.en.md` 中提及 skill-reviewer 的历史条目**按原样保留**——它们记录「当时发生了什么」（标废弃、移出发布流程），属史实，改写即失真；后续变更应新增条目而非修改旧条目。`skill-workshop/scripts` 内若干 `(from skill-reviewer)` 字符串标注亦保留，用作源码溯源。

**本次未落 CHANGELOG 条目**：`CHANGELOG.md` 由 `changelog-manager` 技能按其规范维护，且该文件变更会触发 `release.yml` 发布流程；本次为目录删除与引用清理，是否补条目由用户决定。
## 2026-09-12 退役 CI 发布流程（release.yml）

用户确认仓库定位为纯技能集合，分发走 `npx skills add` 直读仓库，Release 附件无消费方，CI 发版属遗留物（workflow 内 skill-reviewer 打包步骤已随技能删除失效）。经用户明示授权（方案 A）执行：

| # | 既有决策（旧值） | 处置 | 新值 / 原因 |
|---|------------------|------|------------|
| 1 | `.github/workflows/release.yml`（push main + `changelog-manager/` 或 `CHANGELOG.md` 触发 → 打 tag / zip 打包 / 建 Release） | 删 | 目录定位无 CI 发版需求；git 历史可恢复 |
| 2 | `AGENTS.md` 工具链「CI/发布：GitHub Actions」条 | 删 | 并入「无」清单：CI/发布流程（附退役日期） |
| 3 | `AGENTS.md` 命令表「发布新版本」行 | 删 | 触发源已不存在 |
| 4 | `AGENTS.md` PowerShell 注意中 `release.yml` 括注 | 删 | 对象已删除，仅保留 `&&` → `;` 提示 |
| 5 | `AGENTS.md` 质量与文档指针「CI」条 | 改 | 改为「无」+ 退役留痕 + CHANGELOG 降级说明 |
| 6 | `references/project-overview.md` 发布链路 / 根目录文件 / CI / 覆盖缺口四处 | 改 | 改为分发链路（npx skills add 直读仓库）+ CI 无；顺带修正技能表（补 zuiti / vibe-buddy 两行，skill-workshop v1.21.0→v1.23.1，16→18 子命令） |
| 7 | `CHANGELOG.md` / `CHANGELOG.en.md` 与 CI 的关联 | 改 | 降级为纯人类文档；Unreleased 一次性补记至 2026-09-12，此后不再有自动化关联，更新时机随缘 |

**顺带同步**：README.md / README.en.md 版本列（skill-workshop v1.21.0→v1.23.1、changelog-manager v2.0.0→v2.0.1、zuiti v0.3.8→v0.3.9；README.en 补齐缺失的 zuiti 行）。

**保留不改**：CHANGELOG 双语文件中提及 release.yml 的历史条目、`docs/handoff/` 与 `docs/superpowers/plans/` 归档文档、本日志 2026-09-10 条目中的 release.yml 表述——均属史实记录，改写即失真。

## 2026-09-12 评审后自动 commit+push 免二次确认

用户明示：任务完成且评审通过后，普通 `git commit` + `git push`（非 `--force`）自动执行，不再等待单独的「确认推送」信号。AGENTS.md `Permissions` 新增「常态工作流（已授权免二次确认）」条款。

| # | 既有决策（旧值） | 处置 | 新值 / 原因 |
|---|------------------|------|------------|
| 1 | 提交/推送默认需等待用户显式确认（全局 guardrail + AGENTS.md `需确认` 心智模型） | 改 | AGENTS.md `Permissions` 新增「常态工作流（已授权免二次确认）」：review 通过或用户已发起任务后，`git commit`+`git push`（非 `--force`）自动执行，不再发「确认推送」提示 |
| 2 | 高风险 git 操作（`push --force`/`rebase`/`reset --hard`）确认门槛 | 存 | 维持不变，仍需显式授权 |

**保留**：破坏性 git 操作、全局安装、对外发布、依赖/包管理器变更等的确认门槛不降低。

## 2026-09-12 自维护协议补充「提交前自检清单」

用户要求：删除双语文档的「贡献指南 / Contributing」章节，并在 AGENTS.md 自维护协议第 3 条补充提交前自检清单（覆盖技能升版时根 README 版本号易滞后的教训，见本日 README 重写）。

| # | 既有决策（旧值） | 处置 | 新值 / 原因 |
|---|------------------|------|------------|
| 1 | 自维护协议第 3 条：「提交前自检：命令更名、重构、规范变更后核对本文件准确性，有过期示例立即更新。」 | 改 | 扩展为「提交前自检清单（每次提交前逐项核对）」三项：① 命令/重构/规范变更后核对本文件；② 技能升版时同步根 `README.md`/`README.en.md` 技能列表版本号；③ 双语文档章节平行、互链存在、外链连通、不引用已删除路径（如 `skill-reviewer/`） |
| 2 | 根 `README.md` 的「贡献指南」章节 | 删 | 用户要求移除（非开源协作项目，Contributing 内容不适用） |
| 3 | 根 `README.en.md` 的「Contributing」章节 | 删 | 同上，保持双语文档章节平行 |

**顺带同步**：双语文档删除 Contributing/贡献指南 后，章节仍平行（技能列表 / 快速开始 / 作者信息 / 许可证 / 致谢 / 相关链接）。
