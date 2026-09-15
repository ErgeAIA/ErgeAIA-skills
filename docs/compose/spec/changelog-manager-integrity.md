---
feature: changelog-manager-integrity
status: delivered
updated: 2026-09-14
branch: compose/changelog-manager-integrity
commits: f8be307..5c1ce79
---

# changelog-manager 完整性加固

## Report

**What was built** — `changelog-manager` v2.1.0：中文 `CHANGELOG.md` 强制中文分类头（`### 新增` 等），英文文件保持英文头；`bilingual-guide.md` 为标题语言 SSOT，且其示例与 `examples/basic-usage.md` 已对齐（消除审查发现的 SSOT 自相矛盾）。`perf` 默认保留映射 Changed。`+lang`/链接/Issue 策略落盘 `.changelog-manager.json`。`+generate` 文档化幂等与无 tag/浅克隆边界。中文文件头本地化。`+check` 增加分类头语言与双语结构同构判定。版本三处对齐 2.1.0。

**Verification** — 文本级检查：`perf:*` 跳过行 0；bilingual-guide 中文示例块英文分类头 0；basic-usage `### Added` 0；SKILL `version: 2.1.0` = VERSION 首条 = 根 README 双语索引；sidecar/幂等/W3/W4/Gotchas 关键词存在。独立审查（general-1）：9 项标准中 1 项 critical（SSOT 示例矛盾）已在 `5c1ce79` 修复并复检 bad=0。未跑真实 Agent 全量 `+add/+generate` 联调（本技能无 CLI 测试框架）。

**Journey log** — ① 中文分类头以用户拍板为准，模板/示例/SSOT 必须一次改齐，只改规则句会留下自相矛盾。② `perf` 双表矛盾是纯文档缺陷，但会让 `+generate` 不可预期。③ 环境禁止 `git worktree add` 时，经用户授权改在 main 检出开 compose 分支。④ 审查发现 D9 触点漏了 `examples/`，SSOT 文件的工作示例优先级高于模板。⑤ Preview 用词「待写入/已存在跳过」统一，避免「新增」与「待写入」同义混用。

## [S1] Problem

见历史设计（保持锚点）。

## [S2] Design

见提交 `f8be307` 中的设计正文；交付后行为以本 Report 与 v2.1.0 文档为准。

## [S3] Out of Scope

- 无 scripts CLI；不自动 tag/Release；无第三语言；不强制改写历史英文头；无 monorepo 路由；无与 VERSION.md 型仓库的自动互斥策略引擎。

## Tasks

- [x] T1: 修订 `git-extraction-rules.md` — perf 默认保留→Changed；补无 tag/浅克隆/range 失败；hash 仅内部去重
- [x] T2: 修订 `bilingual-guide.md` — 强制中文文件中文分类头；与六行对照表一致
- [x] T3: 重写 SKILL.md 标准格式双语模板与原则/工作流触点
- [x] T4: 更新 `template-examples.md` 与 `output-template.md` 中文侧
- [x] T5: 更新 `classification-guide.md` + README 双语 sidecar
- [x] T6: `VERSION.md` v2.1.0 与根 README 索引版本对齐
- [x] T7: 文案级自检 + 审查修复（bilingual-guide/basic-usage 示例）+ 本 Report

## Decisions log

- 2026-09-14 用户：本轮先出 Spec；**中文文件用中文分类头**；Workspace 因环境禁 `worktree add`，改为在 `main` 检出开分支 `compose/changelog-manager-integrity`；Spec 通过后实现。