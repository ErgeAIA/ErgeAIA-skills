# 更新日志

skill-workshop 所有值得注意的变更都记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

> 早期（v1.21.0 之前）的详细变更历史见 `git` 提交记录；本文件仅保留近期若干版本的精简记录。

## [2.3.0] - 2026-09-22 · Optimize 独立工作模式 + description 语义化（废除词法评分）

> 审查留痕 —— **【SFA】** 本质 = 把「会审计」升级为「会优化」；**杠杆** = ① Optimize 与 Audit 深度分离（前者必须全量读运行时资产并真正改文件）② validator 只判结构、语义交评审 ③ 自身回归测试锁住这条边界；**目标** = 简单技能更快结束、复杂技能被真正理解、有问题的技能被真正改掉，且 workshop 自身不长成更复杂的治理系统。
> **双向钢人（FOR/AGAINST）** —— 议题「是否删除 description 词法判据（意图词表 / 触发词计数 / 引号词阈值 / Pushy 句式正则）」：**FOR** = 实测反向：`%TEMP%/sw-audit` 三夹具中，规范推荐句式 A 被判「核心意图关键词偏少（建议 ≥2）」、裸词表 B 拿到「11 个触发词、5 个核心意图关键词」的合规高分、自然中文 C（讲 Markdown 转公众号 HTML）被判 **硬 FAIL**「找到 0 个，需 ≥1」——判据与目标（路由准确）背离，且直接激励作者往 description 里塞词；**AGAINST（最强形态）** = 删掉后 `npx skills add` 分发场景再无自动把关，「Helps with PDFs.」式描述将无人拦，且 v2.2.0 正是为解决词表化才加的引号阈值，删除等于承认上一版方向错误并让那轮全仓 description 改写运动失去依据。**取舍** = 反方第一点成立但兜底方式选错：能拦「空/超长/多行/占位符」的结构检查保留，「差到无人会用」属语义判断，改由 AUDIT/OPTIMIZE 的 Description 语义评审 + Trigger Quality 用例（正/负/相邻误触发）承担；反方第二点成立，v2.2.0 的引号阈值确属错方向，本轮一并删除并记录，不做沉默覆盖。**关键变量** = 「validator 输出是否含可被优化的计数」；只要计数可见，模型就会为把数字变大而改写文本，因此选择彻底删除而非降级为 INFO。**成立条件** = 若未来出现「无人评审即可分发」的自动化通道，需重估是否补回结构化的最低信息要求（例如强制含一句场景描述）。
> **对抗式审查（发现并修复）** = ① `spec_check` 把「字段顺序」当 FAIL，而官方缓存 spec 通篇无顺序条款、本仓文档只写「建议顺序」→ 伪官方 HARD，降为 advisory；② 斜杠与半角冒号在双引号内无解析风险，却与真实风险项（未引号、反斜杠）同为硬错，会逼作者把「GitHub Actions: 部署」这类正常文本改拧 → 降 advisory，并规定「结构不合法时不再叠加风格建议」以免噪音；③ `validate` 与 `spec` 各有一份 description 解析路径，降级只做一处会出现两命令结论打架 → 两文件同步改并加断言；④ 「禁止默认全量预读」与 Optimize 的「必须全量读」直接冲突 → 在 `core-method.md`、`review.md` 两处同时限定该禁令只约束审计；⑤ 反向激励风险（本技能最容易犯）：为证明升级有效而膨胀新文档 → `optimization.md` 限 169 行、只引用 `core-method.md` 判据不复制、CLI 不新增子命令。
> **三轮 Review 发现并修复（第 2 轮由独立审查代理给出，每条先复现再修）** = ⑥ **P0** `SKILL.md` 核心约束 1 仍无条件禁止全量预加载，而 OPTIMIZE 要求全量读——主文档优先级最高，等于让 agent 继续重复 2.2.0 的失效（复现于 SKILL.md:57）→ 改为「审计路径禁止、优化路径必须」。⑦ **P1** 未加引号且含 `: ` 的 description（正是文档宣称的 HARD 用例）触发 YAML 解析失败时，`main()` 以三元组解包二元组 → `ValueError` 崩溃（quick_validate.py:1159/1164）→ 补全返回值，并把修复建议写进 `message`（非 `--json` 路径只渲染 message，只塞 findings 等于没报）。⑧ **P1** 超 1024 字符时其余结构检查被 `else` 短路跳过 → 改并列检查。⑨ **P1** 同一条 description 在 `spec` 与 `validate` 结论不同（PASS vs FAIL）——判明是分工而非缺陷：`spec` 只对官方契约负责，项目级 YAML 稳健性归 `validate`；已在 `validation.md` 写清并规定交付以 `validate` 为准。⑩ **P1** `creation.md` 模板用尖括号占位符，而尖括号本身是硬约束，自家模板自检即失败 → 改方括号。⑪ **P1** 测试在 cp936 控制台下与乱码比较，`assertNotIn` 类断言「因为读不到而通过」→ 子进程固定 `PYTHONIOENCODING=utf-8`，并补「反斜杠必须读得到」的正向对照与崩溃回归。⑫ **P1 多重权威**：新文档把 `core-method.md` 已有判据另写一份且漂移（Core Task 五项 vs 六项、四元组 vs 五元组、`CONDITIONALIZE` vs `CONDITIONAL`、把 OPTIMIZE 列成第四级深度）→ 处置标记与证据格式统一收归 `core-method.md`（五元组补 `Confidence`、枚举补 `REWRITE`），另两处改为引用；OPTIMIZE 移出深度表并说明它不是深度层级。⑬ **P2 反身膨胀**：SKILL.md 137→155 行且与 `review.md` 的 Fast 清单逐条重复 → 删重复段回压；`optimization.md` 一度写死「10 节不多不少」与用例配额（≥3/≥3/≥2），正是本轮刚删掉的「计数即质量」激励 → 改为默认骨架 + 按复杂度定，不设配额。

### 新增

- **`references/optimization.md`（169 行，唯一新增文档）**：Optimize 模式权威方法论——与 Audit 的职责分界表、核心原则（「优化是用更小的规则系统让原任务完成得更好」）、八步流程（Understand→Inventory→Model→Diagnose→Decide→Rewrite→Validate→Regression）、运行机制建模、只报影响结果的证据（Claim/Evidence/Impact/Action/Confidence + CONFIRMED/INFERRED/UNKNOWN）、规则膨胀与 HARD 七问、目标架构 + 逐项处置（KEEP/MERGE/MOVE/CONDITIONAL/ARCHIVE/DELETE/REWRITE/ADD，各写 why+evidence+user impact）、拆分四独立判据、钢人适用与禁用清单、重写纪律、能力回归、**Description 语义评审 10 问**、**Trigger Quality 四维**、Before/After 八项、10 节最终报告、本模式七种失效模式。
- **`scripts/tests/test_validator.py`（18 用例，`unittest`，零第三方依赖）**：本仓库首个自身测试。锁住结构契约（存在/非空/单行/≤1024/占位符/反斜杠/未引号）与「不判语义」契约（A/B/C 三种风格结构判定一致、输出不得再出现触发词与意图词计数、`INTENT_KEYWORDS` 必须已删除、顺序不阻塞、缺 scripts/eval/Gotchas 不得记缺陷），覆盖 9 类技能原型（简单、单职责、多职责、script-heavy、reference-heavy、仅 SKILL.md、极短描述、长而高质量、关键词堆砌）。

### 删除（校验机制）

- `INTENT_KEYWORDS` 40 词意图动词表、`core_intent_count`（≥1 硬错 / ≥2 软建议）、`trigger_count`、`quoted_tokens`/`quoted_unique`（>4 软建议、≥8 硬 FAIL）、`pushy_patterns` 11 条句式正则，以及 PASS 文案里的「N 个触发词、N 个核心意图关键词」计数展示。`validate_description_format()` 收敛为纯结构校验（severity 由 `warning` 改 `info`，合规时不再刷屏）。

### 变更

- **四模式分离**：`CREATE / AUDIT / OPTIMIZE / VALIDATE` 职责划清，SKILL.md 路由表把「优化 / 重构 / 改好 / 审查后帮我改 / 为什么不好用」显式送入 Optimization Review（Deep 判断纪律 + 全量读取 + 实际改文件 + 回归），**不再沿用审计的默认深度**；VALIDATE 明确「只判结构，不得冒充语义质量评估」。
- `validate_description_symbols()` 返回 `(硬问题, 风格建议)`：双引号与反斜杠留 HARD（YAML 真实解析风险），斜杠与半角冒号降为 advisory；结构不合法时不叠加风格建议。
- `spec_check.py`：字段顺序由 FAIL 降 advisory（输出以 `~ ` 开头，`--json` 增 `advisories` 字段）；尖括号判据标注为本仓约定，不再冒充官方规范。
- 文档同步：`core-method.md` 路由与深度表加 OPTIMIZE 行、把「禁止默认全量预读」限定为只约束审计；`review.md` 加「Optimize 不是第四深度」的指界说明、P0/P1/P2 按「核心任务失效 / 明显影响质量成本 / 文档小问题」重定义并禁止风格问题挤占报告位、新增 description 与触发质量定级口径；`creation.md` description 写法改为 `Trigger + Job + Boundary` 模型（不再要求同义动词全列、命令名全列、引号关键词，不再设 3-4 个配额）；`validation.md` 更新 CLI 判据范围与「改 validator 必带用例」；README 修 **v2.1.0 → v2.3.0 版本漂移**（README 与 SKILL/CHANGELOG 此前不一致）并改写为四模式说明。
- 自身 description 与门面按用户定稿改为「Agent Skill 全生命周期工作台：用于创建、评审、优化、重构、校验和打包 Skill，从明确任务与边界，到调整结构、规则与实现，再到验证结果，形成完整闭环…」——补回此前遗漏的**打包**环节与生命周期闭环叙事，`Not for` 收敛为「通用代码或应用项目开发与审查」；同步 `SKILL.md` 定位行、技能 README 与根 `README.md` / `README.en.md` 索引行的同名表述。AUDIT/OPTIMIZE 的深度差别仍由 `SKILL.md` 路由表承担（主文档每次加载，不必挤进 description）。

### 实测

- `python scripts/tests/test_validator.py` → **Ran 18 tests, OK**（默认控制台编码下同样通过；含崩溃回归与正向对照各 1 条）。
- 自身 `validate` → `Skill is valid!`，`spec` → PASS；`SKILL.md` 143 行（回到自家 120–150 行目标内）。
- Before/After 五技能（`skill-workshop`、`changelog-manager`、`moxian`、`zuiti`、`huiyi`）：五者的 `Description format: …（N 个触发词，M 个核心意图关键词）` 输出（Before 分别 31/6、29/2、22/5、20/1、**54/3**）After 全部消失，真实缺陷（版本 SSOT 漂移）仍被拦下。
- 全仓回归：两子库 **41 个技能**全量跑 `validate` + `spec` → 无崩溃、`spec` 41/41 PASS、`validate` 10 个 FAIL **无一与 description 相关**（版本漂移、`disable-model-invocation` 类型、坏链、缺 `trigger-when`、路由矩阵头），确认既未误放也未误杀。
- 三夹具复现（`%TEMP%/sw-audit/`）：规范推荐句式、裸词表、无意图动词的自然中文——改前三者分别得到「偏少（建议 ≥2）」/「11 个触发词、5 个核心意图关键词」合规 / **硬 FAIL**；改后三者结构判定一致且无任何计数输出。

## [2.2.0] - 2026-09-21 · description 校验修复（反堆砌 + 符号硬检查 + 规范去悬空）

### 修正（校验机制，有行为变化）

- **删掉反向激励**：`validate_description_format()` 原有软建议「触发词偏少（建议 ≥3）」——该建议把"多堆触发词"当优点，是各技能 description 词表化的机制成因（实证：zuiti 24 组、skill-workshop 自身 10 组仍能通过自家 validate）。现删除。
- **补反堆砌判据**（对齐 spec.md §核心触发词 vs 变体清单）：引号内触发词 `>4` → 软建议「疑堆砌或同义变体罗列」；`>=8` → 硬 FAIL「疑似裸词表」。规范口径：核心触发词嵌入句中、3-4 个以内。
- **新增符号硬检查** `validate_description_symbols()`：未双引号包裹 / 含反斜杠 / 含斜杠 / 含半角冒号（规格标记 `Not for:` 除外）→ 硬 FAIL。此前 `validate` 与 `spec` 两条命令**都不查符号**，是本仓长期无人把关的缺口。

### 文档（规范去悬空）

- `references/creation.md §description 写法` 内联三条反模式（同义变体罗列 >3 / 评测查询词逐条塞入 / 裸词表）与符号硬约束；`validate_description_format()` docstring 的真源路径从已不存在的 `references/specs/spec.md` 改为活文档 `references/creation.md`，并标注完整 spec 存档位置。

### 实测

- 正例：skill-workshop（282 字符 / 6 意图词）、zuiti（已补意图词）→ `Spec checks: passed`，且不再出现「触发词偏少」。
- 反例：斜杠 + 半角冒号 + 8 个引号触发词 → 3 条同时命中；未加引号 → 命中；8 个引号触发词 → 裸词表 FAIL；含反斜杠 → YAML 头解析失败即被拦。

## [2.1.0] - 2026-09-19 · 审计方法论整合（判断框架并入，非第二流程）

### 新增（判断框架，并入现有流程）
- **Core Task Definition** 锚点：审计先写「当用户__时，Skill 负责__」+ Input/Output/Non-Goals/Dependencies/Success。
- 五问 + 六类核心问题（职责漂移/规则膨胀/重复冲突/模板化/多重权威/无证据规则）。
- Evidence-First：`Claim → Evidence → Impact → Recommendation`；规则证据测试。
- 规则生命周期补 **EXPERIMENTAL**；删除优先阶梯 + HARD 防火墙（真实失败证据门槛）。
- 结构性膨胀五类（含**治理膨胀**）；Runtime vs Governance 分离。
- 评审分层对外命名 **Fast / Deep / Eval**（≡ L0/L1/L2）；风险表 P0/P1/P2；Deep 扩展字段（Rule/File Disposition 等）。

### 变更
- `core-method.md` / `review.md` / `SKILL.md` / `validation.md`：吸收通用审计方法论为**唯一主流程的底层判断逻辑**；不新增并行审计流、不恢复默认 W1–W7 门禁、不引入 `@` DSL。
- CLI 仍仅 validate/spec/init/package；reconcile/family-diff/selfheal/eval 保持归档条件诊断。

### 保留
- v2 轻量哲学：短报告默认、优点 0–N、无强制拆分、证据预算、禁止默认全量预读。

### 验证
- 对本技能跑 `spec` + `validate`；Before/After 与整合说明见 `docs/integration-2026-09-19.md`。

## [2.0.1] - 2026-09-18

### 修复（v2 发布前 L0/L1 自审）

- L0 产出口径统一：`core-method.md` 与 `review.md`/`SKILL.md` 默认均为六段短报告
- 创建模板去掉尖括号路径占位，避免链接机检误报
- `_gate.py` checkpoint 说明不再指向已删除的 SKILL 旧 §2
- description 收敛（保留触发词与 Not for 边界）

### 变更（v2 轻量工作站，相对 v1.25.0）

- 设计哲学：从「过度治理系统」回到「轻量技能工作站」——最低成本发现致命缺陷；审查深度 L0 默认 / L1 疑点展开 / L2 条件评测
- 规则分级：HARD / CONDITIONAL / HEURISTIC；脚本、评测集、家族差分等改为条件触发或归档诊断
- 版本契约：SSOT = `metadata.version` + `CHANGELOG.md`；废除「三处版本块一致」默认硬约束
- `references/`：52 份收敛为 4 份（`core-method` / `creation` / `review` / `validation`）
- `SKILL.md`：轻量主文档（约 133 行）；移除步骤级 `@` 与固定 W1–W7 默认流水线
- CLI：运行时仅 `validate` / `package` / `init` / `spec`；`init` 为纯净 Markdown；`validate` 不再硬性要求 `@` 标记
- 归档：旧 workflows/rubrics/脚本/评测 agents 迁入 `docs/archive/`

### 移除（运行时默认）

- 强制 3–5 条优点、中等复杂度强制拆分候选、W6 固定收尾句
- 评审前强制全量预读目标 `references/` 与 `scripts/`
- 默认 checklist/consistency/routing-check/eval/loop 等子命令

## [2.0.0] - 2026-09-18

> 设计基线（未单独推送 main）；对外发布版本为 **2.0.1**。

## [1.25.0] - 2026-09-13

### 新增
- `reconcile` 子命令：抽取版本 / 数值阈值 / references 路径事实锚点，检出多值冲突与幽灵路径（C5 机检辅助，不替代语义裁决）
- `family-diff` 子命令：相对指定 baseline 或同父目录兄弟技能块集共识，检出结构块缺失（新增 F1 检查项）

### 变更
- 报告编号对齐：8 段报告自「一句话结论」至「总评」（`## 1`–`## 8`），消除 `## 9. 总评` 双轨
- description 增加 `another skill hands off a Skill project` 与应用类项目 Not for 边界
- CLI 子命令 18 → 20

### 修复
- checklist V4/V5 假阴性收紧：V4 须有测试集文件或正/负集描述且非否定句；V5 须「可机器判定」类措辞且具体机检信号（退出码 / validate·checklist PASS）

## [1.24.0] - 2026-09-12

### 变更
- 脚本柔性化 Phase 2：`validate` findings 化（标注 `rule_class`）、`script-profiles.yaml` 迁为代码消费、`review_ops` 系接入 `--profile`

## [1.23.1] - 2026-09-12

### 修复
- `routing-check` 通用化：去除 skill-workshop 9 个工作流文件硬编码清单，扁平 `references/` 布局技能不再误报

## [1.23.0] - 2026-09-11

### 新增
- 脚本柔性化 Phase 1：`_gate.py` 的 plan-gate / checkpoint / `--profile` / dry-run 默认
- `plan-gate-template.md` 五节计划模板

### 变更
- `init` / `package` / `generate-templates` 默认 dry-run（仅预览），`--write` 才实际落盘

## [1.22.0] - 2026-09-11

### 变更
- description 口径对齐：消除 6 处自相矛盾，校验器分级调整，官方源收敛（新增 `claude-platform-best-practices.md` 缓存）

[Unreleased]: https://github.com/ErgeAIA/ErgeAIA-skills/compare/v2.0.1...HEAD
[2.0.1]: https://github.com/ErgeAIA/ErgeAIA-skills/releases/tag/v2.0.1
[2.0.0]: https://github.com/ErgeAIA/ErgeAIA-skills/compare/v1.25.0...v2.0.1
[1.25.0]: https://github.com/ErgeAIA/ErgeAIA-skills/releases/tag/v1.25.0
[1.24.0]: https://github.com/ErgeAIA/ErgeAIA-skills/releases/tag/v1.24.0
[1.23.1]: https://github.com/ErgeAIA/ErgeAIA-skills/releases/tag/v1.23.1
[1.23.0]: https://github.com/ErgeAIA/ErgeAIA-skills/releases/tag/v1.23.0
[1.22.0]: https://github.com/ErgeAIA/ErgeAIA-skills/releases/tag/v1.22.0
