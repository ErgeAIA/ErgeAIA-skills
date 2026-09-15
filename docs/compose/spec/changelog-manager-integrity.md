---
feature: changelog-manager-integrity
status: designed
updated: 2026-09-14
branch: compose/changelog-manager-integrity
commits: 
---

# changelog-manager 完整性加固

## Report

## [S1] Problem

`changelog-manager` v2.0.1 的双语 changelog 流程已能跑通主路径，但存在会让 Agent **做错事** 或 **不可预期** 的合同空洞：

1. **中文分类标题自相矛盾**：标准模板两侧都用 `### Added`，`bilingual-guide.md` 却要求译成 `### 新增`。用户已拍板：**中文文件用中文分类头**。
2. **`perf` 提取规则自相矛盾**：`git-extraction-rules.md` 跳过表含 `perf:*`，映射表又把 `perf → Changed`。
3. **`+lang` 无落盘**：翻译方向跨会话丢失。
4. **双写无强一致性手段**：中英两份人工/Agent 双写，`+check` 缺少可判定的条目级比对约定。
5. **`+generate` 不幂等**：同一 range 重复执行会双写；与 `+add` 重叠无去重。
6. **无 tag / 非法 range / 浅克隆** 未覆盖：`git describe --tags --abbrev=0` 失败无回退。
7. **仓库远程与 tag 前缀未工程化**：底部链接模板写死 `github.com/user/repo`，未要求发现 `origin`。
8. **中文文件头部仍为英文** boilerplate，与「中文 CHANGELOG」定位不一致。

不修则：Agent 在真实仓库上生成的双语文档会在分类头、性能变更、翻译方向、重复条目上系统性漂移。

## [S2] Design

### D1. 分类标题（已决）

| 文件 | 分类标题 |
|------|----------|
| `CHANGELOG.md`（中文） | `### 新增` / `### 变更` / `### 弃用` / `### 移除` / `### 修复` / `### 安全` |
| `CHANGELOG.en.md`（英文） | `### Added` / `### Changed` / `### Deprecated` / `### Removed` / `### Fixed` / `### Security` |

- 对照表以 `bilingual-guide.md` 的六行为唯一真相源。
- SKILL 标准格式、`template-examples.md`、`output-template.md` 的「中文版」示例全部改为中文分类头。
- `+check`（W4 / V4）：中文文件出现英文分类头或英文文件出现中文分类头，记为 **FAIL**。
- 既有已发布版本区块不强制改写历史；`+check` 对**历史**英文头可标 **WARN（历史遗留）**，对 **Unreleased 与新写入** 标 **FAIL**。
- 不在条目正文混用另一语言的分类语义（分类以标题为准）。

### D2. `perf` 提取规则（已定，消灭矛盾）

- **默认保留** `perf` → 映射为 `Changed`（用户可见的性能变化值得进 changelog）。
- 从「应跳过」表删除 `perf:*`。
- 仅当用户显式要求「只记功能/修复」时，才在预览阶段过滤 perf；不写进默认跳过表。

### D3. `+lang` 落盘

- 项目根可选 sidecar：`.changelog-manager.json`
  ```json
  { "primaryLang": "zh", "keepIssueLinks": false, "tagPrefix": "v" }
  ```
- 字段：
  - `primaryLang`: `"zh" | "en"`，默认 `"zh"`；决定翻译方向（主语言手写，从语言生成）。
  - `keepIssueLinks`: boolean，默认 `false`；`+generate` 是否保留 `(#123)`。
  - `tagPrefix`: `"v" | ""`，默认 `"v"`；影响版本链接与 compare URL。
- `+lang zh|en` 写入/更新该文件；不存在则创建。
- `+init` 可询问是否创建默认 sidecar（或静默创建默认值，Spec 采用：**静默创建默认**，减少一次问答）。
- `.changelog-manager.json` 应列入技能 README 的产物说明；不要求用户提交该文件（个人偏好可本地）。

### D4. 双语一致性（可判定约定）

- **主语言为事实源**：`+add` / `+generate` 时，先写主语言条目，再生成从语言译文。
- `+check` 比对规则（机器可判定子集）：
  1. 版本号集合一致（中英文件解析出的版本列表）
  2. 每个版本的日期一致
  3. 每个版本下，**分类集合**一致（中文标题集合经映射后 = 英文标题集合）
  4. 每个（版本 × 分类）的条目数一致
  5. 底部 link 定义的 version key 集合一致
- 不要求译文字面回译一致（翻译可改写）；只要求结构同构。
- 分类头语言规则见 D1。

### D5. `+generate` 幂等与去重

- Plan 阶段对候选 commit 建内部清单：`{hash, subject, category}`（hash **仅用于去重，不写入 changelog**）。
- 写入前扫描目标 Unreleased（或指定版本）已有条目：
  - 若条目描述与候选「归一化后」相同（去空白、忽略标点）→ 跳过。
  - 若条目旁存在可匹配的短 hash 注释（可选，见下）→ 跳过。
- **可选内部注释**（默认关闭）：在条目末尾写 `<!-- cm:abc1234 -->`，便于幂等；`+check` 不要求该注释；用户可开 `keepMarkers: true`（sidecar）。
  - Spec 取默认：**关闭 markers**，靠归一化描述去重 + 预览「已存在 N 条」。
- 预览表必须列出：新增 / 跳过（已存在）/ 待写入合计。
- 同一 range 连续两次 `+generate`：第二次应报告 0 条待写入。

### D6. Git 边界状态

| 状态 | 行为 |
|------|------|
| 无任何 tag | 范围退化为：若存在首个 commit，提示「将使用全部历史」；用户确认后 `git log --pretty` 全量（或 `--max-count` 保护，默认 200，超出则提示收窄） |
| `git describe` 失败 | 不抛裸错误；进入无 tag 分支 |
| range 反向/不存在 | `+generate` 一线修复：列出本地 tags 供选择；仍失败则取消，不写入 |
| 非 git 仓库 | `+generate` 明确失败并提示可用 `+add` 手动模式（与 W0 一致） |
| 浅克隆（`.git/shallow` 存在） | 预览顶部 WARN：历史可能不完整 |

### D7. 远程链接与 tag 前缀

- `+init` / `+release` 更新底部链接前：
  1. `git remote get-url origin` → 归一化为 https 形式（处理 `git@github.com:owner/repo.git`）
  2. 非 GitHub 主机时，compare/release URL 模板按主机启发式：GitHub/GitLab/Gitee 用各自常见路径；未知主机则只用 tag 锚点本地链接或询问
  3. `tagPrefix` 来自 sidecar（默认 `v`）
- 模板占位 `USER/REPO` 必须在能发现 origin 时替换；不能发现则保留占位并在 `+check` 标 WARN。

### D8. 中文文件头部本地化

中文 `CHANGELOG.md` 推荐头：

```markdown
# 更新日志

本项目所有值得注意的变更都记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。
```

- H1 可用 `# 更新日志` 或 `# Changelog`；**推荐 `# 更新日志`**（与中文读者一致）。
- 英文文件保持英文 KaC boilerplate。
- `+check`：中文文件若仍含 `All notable changes` 且无中文导语 → WARN（历史）；新 `+init` 必须用中文头。

### D9. 文档触点（实现时同步改）

| 文件 | 改动 |
|------|------|
| `SKILL.md` | 标准格式双语示例；原则 2/6/7 与 D1 对齐；Gotchas 补 sidecar、幂等、无 tag；W1/W3/W4 步骤补去重与分类头语言；参考表补 sidecar |
| `references/bilingual-guide.md` | 明确「中文文件分类头用中文」为强制；与模板一致 |
| `references/git-extraction-rules.md` | 删 perf 跳过；补幂等与 hash 仅内部；补无 tag 回退 |
| `references/template-examples.md` | 中文示例分类头改中文；头部改中文 |
| `references/output-template.md` | 同上；检查报告增加分类头语言与结构同构项 |
| `references/classification-guide.md` | 决策树输出分类时注明「中文文件用中文标题」 |
| `README.md` / `README.en.md` | sidecar、`+lang` 持久化、幂等一句 |
| `VERSION.md` | v2.1.0 条目 |
| `SKILL.md` metadata.version | `2.1.0` |
| 根 `README.md` / `README.en.md` 技能索引 | 版本列 → v2.1.0 |

### D10. 版本策略

- 行为变更 + 文档契约收紧 → **v2.1.0**（minor）。
- 不升 major：六分类集合与快捷命令集合不变；中文分类头是执行细节收紧，已有「双语」大版本承诺仍在 v2.0.0。

## [S3] Out of Scope

- 不做 `scripts/` 机器 `+check` CLI（本轮只把规则写成可判定约定；CLI 另议）。
- 不自动 `git tag` / GitHub Release（维持非目标）。
- 不支持超过中英两种语言。
- 不改写用户已有 changelog 的历史英文分类头（只 WARN）。
- 不做 monorepo 多包多 CHANGELOG 路由。
- 不实现 commit body 的深度语义解析 / LLM 外部 API。
- 不处理与 `VERSION.md` 型仓库（如 ErgeAIA-skills 本体）的自动互斥——可在 Gotchas 加一句「目标仓库已有变更记录约定时先询问」，但不做策略引擎。

## Tasks

- [ ] T1: 修订 `git-extraction-rules.md` — perf 默认保留→Changed；补无 tag/浅克隆/range 失败；hash 仅内部去重 — acceptance: 文内无 perf 自相矛盾；含 §无 tag 回退 (covers: S2 D2 D5 D6)
- [ ] T2: 修订 `bilingual-guide.md` — 强制中文文件中文分类头；与六行对照表一致 — acceptance: 无「中文文件用 ### Added」表述 (covers: S2 D1)
- [ ] T3: 重写 SKILL.md 标准格式双语模板与原则/工作流触点 — 中文头 + 中文分类头；W3 幂等预览；+lang 落盘 sidecar；无 tag 行为；Gotchas 补齐 — acceptance: 标准格式示例两侧分类头语言正确；metadata.version=2.1.0 (covers: S2 D1 D3 D5 D6 D8 D9)
- [ ] T4: 更新 `template-examples.md` 与 `output-template.md` 中文侧 — acceptance: 中文示例无英文分类头；检查模板含结构同构项 (covers: S2 D1 D4 D8)
- [ ] T5: 更新 `classification-guide.md` 决策树旁注 + README 双语 — sidecar/幂等/中文分类头 — acceptance: README 提及 `.changelog-manager.json` (covers: S2 D1 D3)
- [ ] T6: `VERSION.md` 增加 v2.1.0 并与根 README 索引版本对齐 — acceptance: SKILL metadata = VERSION 首条 = 根 README 两处 (covers: S2 D9 D10)
- [ ] T7: 按 trigger-test-set 与 V1–V4 口径做文案级自检（无跑 Agent 全量触发则标注未跑项） — acceptance: 自检记录写入本 Spec Report 或提交说明 (covers: S2 D4)

## Decisions log

- 2026-09-14 用户：本轮先出 Spec；**中文文件用中文分类头**；Workspace 因环境禁 `worktree add`，改为在 `main` 检出开分支 `compose/changelog-manager-integrity`。