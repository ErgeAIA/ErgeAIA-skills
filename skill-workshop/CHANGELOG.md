# 更新日志

skill-workshop 所有值得注意的变更都记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

> 早期（v1.21.0 之前）的详细变更历史见 `git` 提交记录；本文件仅保留近期若干版本的精简记录。

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
