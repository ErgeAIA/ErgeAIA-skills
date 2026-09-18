---
feature: skill-workshop-v2
status: delivered
updated: 2026-09-18
branch: compose/skill-workshop-v2
commits: 7f77f6d..main@2.0.1
---

# skill-workshop v2 重构与瘦身

## Report

**What was built** — skill-workshop 在 `compose/skill-workshop-v2` 上完成 v2.0.0 轻量重构：设计从「治理系统」收回「最低成本发现致命缺陷」。运行时 `references/` 收敛为 4 份（core-method / creation / review / validation）；`SKILL.md` 重写为 133 行、无步骤级 `@` 标记；CLI 仅保留 `validate` / `package` / `init` / `spec`（lazy import）；`init` 模板改为纯 Markdown。旧 52 份 references、16 个归档脚本、评测 agents 与 eval HTML 迁入 `docs/archive/`。`validate` 将语义化 `@` 标记从硬失败改为 advisory，使纯 Markdown 技能可通过机器闸门。版本 SSOT：`metadata.version=2.0.0` = CHANGELOG 顶部 = 根 README / README.en；`sync_skills_browser.py` alignment OK。

**Verification** — 已执行并观察到：

| 命令 | 结果 |
| --- | --- |
| `python scripts/skill_cli.py --help` | 仅 validate/package/init/spec |
| `python scripts/skill_cli.py spec .`（skill-workshop） | PASS (exit 0) |
| `python scripts/skill_cli.py validate .` | Skill is valid! (exit 0) |
| `python scripts/skill_cli.py validate ../changelog-manager` | Skill is valid! (exit 0) |
| `python scripts/skill_cli.py spec ../changelog-manager` | PASS |
| `python scripts/skill_cli.py init demo-skill --path %TEMP%` | dry-run 预览 OK |
| `python scripts/skill_cli.py package .` | dry-run validation PASS |
| `python scripts/skill_cli.py checklist .` | 未知命令 + 归档提示 (exit 2) |
| `py_compile` 保留模块 | 0 |
| `sync_skills_browser.py` | scanned 46 skills, alignment OK |
| SKILL.md 行数 | 133（目标 120–150） |

**未验证范围**（须用户确认）：真实 `--write` 落盘的 init/package；归档脚本单独可运行性；他技对已删 CLI 子命令的外部调用方；本分支 git commit/push。

**Journey log** — ① `@` 清理脚本误伤 `quick_validate.py` 检测正则 → 恢复 `@工作流` 识别并把 markup 校验改为 v2 advisory。② 独立审查指出：归档 `@` 未清干净且 README 表述过满；`validate` 在「无正文版本块 + 有 CHANGELOG」时跳过 SSOT 比对；`init` 预建空 `references/scripts/assets` 与 creation 契约矛盾；`spec_check` 漏检 `>`。③ 已修：归档 residual `@`=0；validate 比对 `metadata.version` vs CHANGELOG 顶部（故意漂移样本 exit=1）；init 只建三文件；尖括号双侧检测；根 README 文案对齐 v2；CHANGELOG compare 链至 v2.0.0。

**Files** — 运行时核心：`skill-workshop/SKILL.md`、`references/{core-method,creation,review,validation}.md`、`scripts/skill_cli.py`、`scripts/_impl/{init_skill,spec_check,package_skill,quick_validate,utils,_gate}.py`、`docs/archive/`。

## [S1] Problem

`skill-workshop` 当前已从「技能质量工作站」膨胀为小型治理系统：`SKILL.md` 198 行且满布 `@工作流/@步骤/@动作` 标记；`references/` 52 份；`scripts/` 23 个 py 且 `skill_cli.py` 顶层硬 import 全部 `_impl`；评审默认走固定 W1–W7、全量预读、强制优点/拆分/收尾句、脚本与评测硬门槛。第一性问题被偏离：应「用最低审查成本可靠发现高风险缺陷」，而非「每次跑完整检查流水线」。

用户硬约束（最高优先级）：全仓清理步骤级 `@` 标记；工具链仅保留核心验证与打包（+ 创建入口/规范轻检）；52 份 references 收敛为最多 4 份权威文档；`SKILL.md` 压至 120–150 行并视为全新重构。

## [S2] Design

### 已拍板决策

| 决策点 | 结论 |
| --- | --- |
| Workspace | ErgeAIA-skills 原仓目录，新开 `compose/skill-workshop-v2`，**不建 worktree**；基线 `7f77f6d` |
| 版本 | **2.0.0**（架构断裂）；SSOT：`SKILL.md metadata.version` + `CHANGELOG.md` 顶部 + 根 `README.md` / `README.en.md` |
| CLI 保留 | `validate` + `package` + `init` + `spec`；其余子命令与高额脚本归档 |
| `@` 范围 | **运行时全清 + 归档件也清**（`@references/` / `@templates/` / `@阶段名` / `@工作流` 等步骤级标记） |

### 定位与运行时模型

- **定位**：轻量 Skill 质量工作站，核心是「最低成本发现致命缺陷」。
- **规则分级**（写入 `core-method.md` / `review.md`）：
  - **HARD**：破坏性或导致失效（非破坏、平台字段、`metadata.version` + CHANGELOG、主文档体量、证据落点）。
  - **CONDITIONAL**：有对应能力才查（脚本 → P 系列；评测集 → 高风险/显式要求；家族差分 → 显式要求；编排字段争用 → 有 orchestrator）。
  - **HEURISTIC**：经验建议，有证据才报，不阻塞。
- **审查深度路由**（废除默认 W1–W7 全量链）：
  - **L0 默认**：Frontmatter / description / 主职责 / 主文档体量 / references 结构 / 明显冲突 / 输出契约。
  - **L1 展开**：出现结构性疑点或用户显式要求深度时，按需读对应 reference。
  - **L2 评测**：仅触发率/benchmark/回归显式要求；对应脚本与 agents 已归档，文档只留「条件触发 + 归档路径」指引。
- **证据驱动**：禁止默认全量预读目标技能的 `references/` 与 `scripts/`；先目录清单与机械事实，疑点再打开相关文件。
- **版本契约**：唯一机器事实 `metadata.version`；变更史 `CHANGELOG.md`；取消「三处版本块」默认硬约束。
- **废除项**（必须在 review 文档与 CLI 行为中消失）：强制 3–5 条优点；中等复杂度强制拆分；W6 固定收尾句；脚本必须存在（I2）；评测集默认必查；family-diff 默认必跑。

### 目标目录形态

```text
skill-workshop/
├── SKILL.md                 # 120–150 行，无步骤级 @
├── README.md
├── CHANGELOG.md             # 2.0.0 顶部
├── references/
│   ├── core-method.md       # 路由分级 / 按需读取 / 证据驱动 / 规则分级
│   ├── creation.md          # 极简创建规范与纯净模板（无 @）
│   ├── review.md            # T/E/C 三轴 + L0/L1 + HARD/CONDITIONAL/HEURISTIC
│   └── validation.md        # 基础格式与核心安全规范
├── scripts/
│   ├── skill_cli.py         # 仅 validate | package | init | spec
│   └── _impl/
│       ├── __init__.py      # 只导出保留模块
│       ├── utils.py
│       ├── _gate.py         # init/package 写操作 plan-gate
│       ├── quick_validate.py
│       ├── package_skill.py
│       ├── init_skill.py    # 模板去 @，改为纯 Markdown
│       └── spec_check.py    # 从 review_ops 抽出的官方规范轻检
├── assets/banner.*          # 保留品牌横幅
└── docs/archive/
    ├── README.md            # 归档说明（不参与运行时）
    ├── references/          # 原 52-4 份 references + 旧 config/templates 等
    ├── scripts/             # reconcile/family-diff/review*_ops/eval/loop/…
    └── agents/              # analyzer/comparator/grader + eval HTML
```

### CLI 契约（重构后）

| 子命令 | 行为 | 保留原因 |
| --- | --- | --- |
| `validate <path>` | 结构/frontmatter/链接等静态校验；退出码 0/1/2 | 核心机器闸门 |
| `package <path> [out]` | 打包 `.skill`；沿用 plan-gate | 分发交付 |
| `init <name> --path` | 纯 Markdown 脚手架（无 `@`） | 创建流入口 |
| `spec <path>` | 官方 Agent Skills 字段/规范轻检 | 合规硬校验 |

实现要求：`skill_cli.py` **禁止**顶层 import 已归档模块；按子命令 lazy import。归档前从 `review_ops.py` 抽出 `spec_check` 落到 `spec_check.py`，避免 CLI 依赖整个评审实现。

### `@` 清理规则

- 删除：`@工作流` / `@步骤N` / `@动作` / `@验证点` / `@验证方式` / `@类型` / `@目的` / `@场景` / `@ID` / `@后置验证` / `@优先级` / `@references/...` / `@templates/...` 等步骤级与路径注入式标记。
- 替代：标准 Markdown 相对路径 + 自然语言（例：「需要扩展时，读取 `references/creation.md`」）。
- 范围：`SKILL.md`、4 份 references、保留脚本/模板（尤其 `init_skill.py`）、`README.md`、以及 `docs/archive/**` 内全部 md/py/html/yaml/json 中的上述标记。
- 新 `SKILL.md` 不得出现任何步骤级 `@`。

### 文档同步（版本与索引）

- `skill-workshop/SKILL.md` `metadata.version: "2.0.0"`。
- `skill-workshop/CHANGELOG.md` 顶部新增 `[2.0.0] - 2026-09-18`（归档/契约断裂说明）。
- 根 `README.md` / `README.en.md` 技能列表版本改为 2.0.0。
- 执行 `uv run --no-project python scripts/sync_skills_browser.py`（Skills-Depot 根）对齐三索引。
- **不在本任务修改**：`ErgeAIA-skills/AGENTS.md` 中关于语义化 `@` 标记的架构偏好条文（仓库级契约另议）；`references/project-overview.md` 中对已归档 `consistency` 子命令的指针——在变更报告中披露为后续项。

### 审查三件套（设计定稿）

1. **第一性原理**：最小充分路径 = 归档非核心 + 4 references + 纯 SKILL.md + 收窄 CLI + 清 `@` + 版本同步 + `validate` 自检。不引入新框架、不加新检查体系。
2. **双向钢人**：全量 W 流水线更强在「默认覆盖」；L0/L1 更强在「成本与风险对齐」且保留条件深度——按用户裁决与审计结论选后者。
3. **对抗**：CLI 顶层 import、`spec` 依赖 `review_ops`、`init` 模板注入 `@`、validate 对 builder `@工作流` 的历史逻辑、根 README 版本漂移、他技引用旧子命令——均在任务与验收中显式覆盖。

### Out of Scope 边界（见 S3）内的验证策略

对保留 CLI：`validate`/`spec`/`init`/`package` 对 skill-workshop 自身与至少 1 个兄弟技能（如 `changelog-manager` 或 `zuiti`）跑通；不重跑已归档 `checklist`/`reconcile`/`family-diff`。

## [S3] Out of Scope

- 修改 `ErgeAIA-skills/AGENTS.md` 架构偏好（语义化 `@` 标记）与全库其他技能内容。
- 恢复/迁移 W1–W7 默认流水线、8 维评分与 54 项 checklist 作为运行时默认路径。
- `references/project-overview.md` 中过期 CLI 指针的改写（披露即可，本分支不顺手扩权）。
- 闭源仓 `erge-private`、Skills-Depot 运行态目录、`~/.agents/skills` 等。
- 为归档脚本补单元测试或重建 eval 基准集。
- git push / PR / merge（Finish 阶段由用户决定）。

## Tasks

- [ ] T1: 建 `docs/archive/` 并归档非核心资产 — acceptance: 原 workflows/rubrics/authoring/specs/templates/config/evaluation/examples 中除 4 核心外的 references、非保留 scripts、`agents/`、eval HTML 均在 `docs/archive/` 下；`docs/archive/README.md` 说明归档原因与「不参与运行时」 (covers: S2)
- [ ] T2: 抽出 `spec_check` 并重写 CLI 为四子命令 — acceptance: `skill_cli.py --help` 仅含 validate/package/init/spec；顶层不 import reconcile/review/family_diff/eval/loop 等；`python scripts/skill_cli.py spec|validate|init|package --help` 均可运行 (covers: S2; depends: T1)
- [ ] T3: 重写 `init` 模板与 `references/creation.md` 为纯净 Markdown — acceptance: `init` 产出与 `creation.md` 无步骤级 `@`；创建规范覆盖职责/输入输出契约/基础结构/`metadata.version`+CHANGELOG (covers: S2; depends: T2)
- [ ] T4: 写作 4 份核心 references — acceptance: `references/core-method.md|creation.md|review.md|validation.md` 存在且分别覆盖路由分级与证据驱动、极简创建、T/E/C+L0/L1+规则分级、基础格式与核心安全；无死链指向已归档运行时路径（历史归档路径仅在 archive 说明中出现） (covers: S2; depends: T1)
- [ ] T5: 重写 `SKILL.md` 为 120–150 行轻量主文档 — acceptance: 行数在 120–150；含 name/description/metadata.version=2.0.0；定位/L0-L1 路由/硬约束（无强制优点、无强制拆分、无脚本硬约束）/4 references 使用时机；全文无步骤级 `@` (covers: S2; depends: T3 T4)
- [ ] T6: 全仓 `@` 清理 — acceptance: 对 `skill-workshop/**` 扫描步骤级 `@标记` 与 `@references/`、`@templates/` 为 0（归档件同样）；运行时文档改用 Markdown 相对路径与自然语言 (covers: S2; depends: T1 T2 T3 T5)
- [ ] T7: 版本与索引同步 — acceptance: `metadata.version`=CHANGELOG 顶部=根 README/README.en 为 2.0.0；`sync_skills_browser.py` alignment OK (covers: S2; depends: T5)
- [ ] T8: 验证与变更报告 — acceptance: 在 skill-workshop 目录跑通 `validate`/`spec`/`init`+`validate`/`package`；对兄弟技能 `validate` PASS；输出归档清单与行数/体量缩减摘要；不宣称用户侧已验证完毕 (covers: S2 S3; depends: T2 T5 T6 T7)
