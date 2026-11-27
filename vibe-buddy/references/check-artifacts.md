---
name: check-artifacts
description: vibe-check 的执行契约：只读体检项目协作档案（AGENTS.md 与 docs/agents/ 各产物），报「问题 + 证据 + 修复入口」，不写任何文件、不产待办、不代跑修复。
trigger-when: 用户说「体检」「检查项目档案」「文档是不是过期了」「编号有没有断」，或 vibe-wrap 前想先看档案健康度时
role: workflow
reads-from:
  - <project>/AGENTS.md
  - <project>/docs/agents/ 全部产物（含 archive/）
  - <project>/docs/handoff/
  - references/workflow-protocol.md（P10 阈值、P7 完成判据）
writes-to: []
known-limits: 只读，不写任何文件；不产待办；不代跑修复；不检查代码质量
---

# check · 项目档案体检（只读）

公共段见 `references/workflow-protocol.md`。本文件只写体检项与修复入口。

## 目标

7 个产物落点、3 类编号、2 份台账——用户无法自查「档案还健康吗」。本工作流把这些结构约定变成一次可复核的检查，**只报不修**。

**与 `vibe-audit` 的分工**：check 看**档案**（`docs/agents/`、`AGENTS.md` 的结构与一致性），audit 看**代码**（质量 / 架构 / 技术栈）。两者对象互斥，用户说「检查一下这个项目」这种模糊话时**问一句**「查档案还是查代码」，不自行归类。

## 硬约束

- **只读**：不写任何文件（`writes-to` 为空），连 `updated` 都不改。
- **不产待办、不排期、不整改清单**（沿用 `SKILL.md` 非目标）。
- **不代跑修复**：每个问题只给「该跑哪个触发词」，不给具体命令序列。
- 读不到就写「证据不足」，不猜。

## 体检项（C1–C10）

逐项过，每项只给三态：**通过** / **问题**（带 `路径:行` + 修复入口）/ **证据不足**。

| # | 检查什么 | 判据 | 修复入口 |
|---|---|---|---|
| C1 | `AGENTS.md` 存在且可读 | 文件存在、六节结构完整 | 不存在 → `vibe-init`；结构缺 → `vibe-init` 增量维护 |
| C2 | `AGENTS.md` 体量 | ≤500 行硬上限（目标 ≤250）；超限即报 | `vibe-init` 做杂音清扫与下沉 |
| C3 | `References` 指针形态 | 每条为 `- <何时读> → 见 <path>：<用途>`；出现裸 `见 path` 或无触发条件即报 | `vibe-init` 改写指针 |
| C4 | `References` / `Permissions` 里的路径真实存在 | 逐条核文件是否存在；不存在即报（这是最硬的一类，指针断链） | `vibe-init` 修正或删项 |
| C5 | 各产物 frontmatter `updated` | 与文件内容的最新日期一致；明显滞后（如内容有 2026-11 的条目而 `updated` 是 2026-09）即报 | `vibe-sync` 改 `updated` |
| C6 | 编号连续性 | `DEC-NNN` / `BUG-NNN` 在「活跃 + archive/」全域无跳号、无重号 | 跳号 → `vibe-sync` 补条目或说明；重号 → 先修编号 |
| C7 | 蒸馏双台账一致 | `experience/changelog.md` 与 `.distill-index.json` 的区间集合一致 | `vibe-distill` 修台账（先修台账再蒸） |
| C8 | 产物是否超阈值 | 按 `workflow-protocol.md` P10 的 8 项阈值逐个核；超限即报 | `vibe-sync` / `vibe-handoff` / `vibe-audit` 走归档闸 |
| C9 | 交接文档可取最新 | `docs/handoff/` 有文件时，按文件名日期能唯一定出最新一份；`archive/` 未混入候选 | `vibe-handoff` 规范命名 |
| C10 | 过程文档的写者边界 | 不该被改的文件是否被改（如 `agents-changelog.md` 出现非契约变更记录） | 只报，交用户判断 |

## 不做

- 不检查代码质量、架构、依赖（那是 `vibe-audit`）。
- 不检查 `CHANGELOG.md` 的格式（那是 `changelog-manager`）。
- 不检查 `.gitignore` 规则是否合理（那是 `git-manager`）。
- 不评价内容写得好不好（语义质量属人工项，见 `workflow-protocol.md` P7）。

## 输出

不落盘，直接回话，≤3 行 + 明细：

```text
档案体检：通过 7 项 · 问题 3 项 · 证据不足 0 项
① docs/agents/project-progress.md:3 — updated 滞后（内容含 2026-11 条目，updated 为 2026-09-12）→ 跑 vibe-sync
② docs/agents/decision-log.md:41 — DEC-003 后直接 DEC-005，缺 004 → 跑 vibe-sync 补或说明
③ docs/agents/experience/.distill-index.json — 区间 `a1b2c3..d4e5f6` 与 changelog.md 不一致 → 先修台账再跑 vibe-distill
```

- 全通过时只回一行「档案体检：10 项全通过」。
- 问题多时按「断链 > 编号 > 台账 > 体量 > 日期」排序，先报会让人做错事的。
- **每项必须给修复入口**（哪个触发词），只报问题不给入口等于让人自己找。

## 失败处理

| 触发条件 | 一线修复 | 仍失败兜底 |
|---|---|---|
| `docs/agents/` 不存在 | 明说「未初始化」，指向 `vibe-init` | 用户要求在未初始化项目上体检 → 拒绝，无档案可查 |
| 目标其实是代码项目要审代码 | 停下问一句，或直接转 `vibe-audit` | 用户未答 → 不执行 |
| 目标含 `SKILL.md` 且要审质量 | 转 `skill-workshop` | 用户坚持 → 拒绝，标尺不适用 |
| 某产物读不到（权限/损坏） | 该项标「证据不足」，继续其余项 | 全部读不到 → 中止，只回「档案不可读」 |
