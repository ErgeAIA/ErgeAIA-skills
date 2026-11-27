---
name: release-checklist
description: 发布治理契约：发版前的六步闸、每步的交接口与回滚点字段。只持有契约与记录，不执行命令、不写 CHANGELOG、不打 tag。
trigger-when: 用户说「准备发版」「发版前检查」「记一下这次发布」，或 vibe-wrap / vibe-sync 走到发版边界时
role: workflow
consumed-by: references/sync-progress.md、SKILL.md
known-limits: 不执行任何命令；不写 CHANGELOG；不打 tag；不调发布平台 API
---

# release · 发布治理契约

> **关于入口**：本契约有独立触发词 `vibe-release`（`vibe-init` 之外的第八个入口），但它**不是一个新工作流**——没有自己的产物落点、不执行命令、不写 CHANGELOG。它存在的理由是「发布」这件事跨三个技能且有不可逆步骤，需要一个持有顺序与留痕的地方。计划原文写「不新增触发词」，落地时改为「不新增工作流、但给一个可直达的入口」，因为用户说「发版前检查一下」时若无入口就会被 `changelog-manager` 的「发版」抢走，反而给出半截建议。

## 为什么需要这份契约

发布被切成三块，**没有一方持整链**：

| 环节 | 现在归谁 | 它不做什么 |
|---|---|---|
| 版本归档 | `changelog-manager +release` | 不建 tag、不发 Release（其 SKILL 非目标明写） |
| 分支 / 提交 / 推送 / tag | `git-manager` | 不做版本决策，没有「发布」这个动作 |
| 构建与测试 | 用户或 CI | 本技能白名单外，不跑 |

缺的是「检查 → 版本决策 → 归档 → 打 tag → 回滚点 → 记录」这条**顺序与留痕**。tag 不可逆，回滚点只能在发布前定——这是本契约存在的唯一理由。

## 边界（硬）

- **不执行任何命令**：不 commit、不 tag、不 push、不跑构建。
- **不写 `CHANGELOG.md`**：归档交 `changelog-manager`。
- **不调发布平台 API**。
- **产物只有 `project-progress.md` 一条发布记录**（版本策略有变时另加 `decision-log.md` 一条）。
- 用户说「发版」时，版本归档仍归 `changelog-manager`；本契约只覆盖它不做的环节。

## 六步闸

可整链跑，也可只跑其中一步（用户说「只检查」→ 只跑 ①；说「记一下这次发布」→ 只跑 ⑥）。

| 步 | 动作 | 通过条件 | 不通过时 |
|---|---|---|---|
| ① 前置检查 | 核工作区与产物状态 | 工作区干净（`git status --short` 为空或只有可忽略项）；`[Unreleased]` 非空；构建与测试结论由用户/CI 提供且为通过 | 逐条列出缺口 + 证据，**停止**，不进版本决策 |
| ② 版本决策 | 按 `[Unreleased]` 分类给 SemVer 依据 | major/minor/patch 三选一，各给触发依据（破坏性变更 / 新功能 / 仅修复） | 分类不足以判定 → 列出缺哪类信息，**决策权交用户** |
| ③ 归档 | 交 `changelog-manager +release <version>` | 对方完成，且 `[Unreleased]` 已清空、新版本节已建 | 标「待补」并写明卡点，不算发布完成 |
| ④ 提交与打 tag | 交 `git-manager`（tag 属不可逆，必须二次确认） | 提交已推、tag 已建并指向该提交 | 任一步失败 → 保留现状，不宣称发布 |
| ⑤ 回滚点 | 记录回滚所需四项 | 四项齐全并写入 ⑥ 的记录 | 缺任一项 → 不允许进入 ⑥ |
| ⑥ 发布记录 | 在 `project-progress.md` 追加一条 | 含版本号 / tag / HEAD / 上一版本 tag / 回滚命令 | — |

## 回滚点四项（缺一不可）

| 字段 | 取法 |
|---|---|
| 本次版本号 | ② 的结论 |
| 本次 tag | ④ 建出的 tag 名 |
| 本次 HEAD | 打 tag 时的 commit（`git log --oneline -1`） |
| 上一版本 tag | `git tag --list` 里按版本序的前一个；无历史 tag 时写「首次发布，无回滚点」 |

回滚命令模板（只写进记录，不执行）：

```
git revert <本次 HEAD>        # 保留历史，推荐
# 或（仅本地未推送时）
git reset --hard <上一版本 tag>
```

## 发布记录格式

追加到 `project-progress.md` 的「当前状态」块，一条：

```text
- **发布**：YYYY-MM-DD vX.Y.Z · tag `<tag>` · HEAD `<sha>` · 上一版 `<prev-tag 或「无」>` · 回滚 `git revert <sha>`
```

- 同时写进进度条目（人读），并在该条末尾加机读行（见 `sync-progress.md` 的执行台账）。
- 版本策略有变（如改 SemVer 口径、换 tag 命名规则）→ 另在 `decision-log.md` 记一条 `DEC-NNN`。

## 与其他工作流的分界

| 场景 | 归谁 |
|---|---|
| 「发版」「归档到 1.2.0」「生成 release notes」 | `changelog-manager` |
| 「提交 / 建分支 / 打 tag / 推送」 | `git-manager` |
| 「发版前检查一遍」「这次发布记一下」「回滚点是哪个」 | **本契约** |
| 「这轮收尾」 | `vibe-wrap`（内部可能触发本契约的 ⑥） |

## 失败处理

| 触发条件 | 一线修复 | 仍失败兜底 |
|---|---|---|
| 工作区不干净 | 列出未提交文件，交 `git-manager` 处置 | 用户要求强行发布 → 拒绝，说明 tag 会指向不完整状态 |
| `[Unreleased]` 为空 | 交 `changelog-manager +generate` 从提交提取 | 仍为空 → 停止，不凭记忆补条目 |
| 无历史 tag | 回滚点写「首次发布，无回滚点」 | — |
| `changelog-manager` 未执行 | 标「待补」并写明卡点 | 用户坚持本技能代写 → 拒绝，说明归属 |
| tag 已存在 | 停止，报告冲突 tag 与它指向的 commit | 用户要求覆盖 → 转 `git-manager` 并显式确认 |
