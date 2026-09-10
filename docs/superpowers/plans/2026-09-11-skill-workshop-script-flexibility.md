# skill-workshop 脚本柔性化（目标驱动脚本层）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **本计划为独立立项（2026-09-11 新增），执行须等用户明确指令；不依赖 description 口径对齐计划的完成，但建议在其回归后启动。**

**Goal:** 把 skill-workshop 脚本从「规定每一步怎么做」的硬执行者，改造为「给目标、边界条件、可调参数」的引导者——AI 保留策略自主权，脚本只守边界、供证据、设检查点、留人工介入口。

**Architecture:** 三层模型。L1 边界校验（现有 validate/spec/consistency/checklist/routing-check，只查硬约束）；L2 证据输出（findings 模型：事实 + 严重度 + 可选方向，供 AI 权衡而非直接服从）；L3 引导协议（plan-gate 计划门 + checkpoint 转述约定）。不重写现有校验逻辑，只加参数层与输出层。

**Tech Stack:** Python >=3.10 纯 stdlib（无新依赖）；Markdown 模板；PowerShell。

**Spec:** 用户 2026-09-11 四项要求——① 不过度规定具体做法，给目标/边界/可调参数；② 允许 AI 按上下文自行判断调整；③ 关键节点设检查点让 AI 说明思路与下一步；④ 保留人工介入与微调空间。对应 description 口径对齐计划（`2026-09-11-skill-workshop-description-alignment.md`）确立的目标驱动原则。

## Global Constraints

- 脚本纪律不变：无 `input()`；`--help`；退出码 `0=PASS, 1=FAIL, 2=ERROR`（**"需要人工决策"不是错误**——用 JSON 字段 `decision_required` 表达，exit 0）。
- 不引入第三方依赖；`_gate.py` 为纯 stdlib 新文件（新增脚本须用户批准）。
- 兼容性：`init` / `package` / `generate-templates` 改 dry-run 默认（2026-09-11 已拍板），`--write` 落盘；其余命令默认行为不变。
- 本计划只动 `skill-workshop/scripts/`、`skill-workshop/SKILL.md`、`skill-workshop/references/`；版本 bump 到 1.23.0（在 description 对齐计划落地后顺延）。

## 核心设计：五件套

### 1. 脚本守什么（边界条件）

脚本只守三类边界，其余全部降为证据输出：

| 边界类型 | 判据 | 例子 |
|---|---|---|
| 官方硬约束 | agentskills.io / 官方 best-practices | 非空、≤1024、无 XML 标签 |
| 事故背书约束 | VERSION.md 有真实失效史 | 单行 string、版本三处一致、非破坏护栏 |
| 成本/不可逆门槛 | 动作花钱、写文件、不可回滚 | eval/loop 真跑、init/package 写文件 |

不守的：风格正则（Pushy）、形态要求（动词开头、@标记形态——对运行型技能）、步骤顺序、清单覆盖率。这些进 findings（`severity: warn/info`），AI 自行权衡。

### 2. 可调参数（`--profile`）

```python
p.add_argument("--profile", choices=["strict", "standard", "advisory"], default="standard",
               help="strict=历史行为(全判级)；standard=仅 blocker 判 FAIL；advisory=只报不判")
```

- `strict`：保留旧硬行为（兼容 CI 场景）。
- `standard`（默认）：官方硬约束 + 事故背书约束判 FAIL，风格类降 warn/info。
- `advisory`：全部只读输出 findings，不判 PASS/FAIL——AI 探索阶段用。
- profile 与判据的映射外置到 `references/config/script-profiles.yaml`（复用 consistency-rules.yaml 的加载模式），改判级不改代码。

### 3. AI 自主调整（findings 模型）

统一 JSON 输出 schema（`--json`，review/checklist/spec/consistency 已有雏形，补齐其余）：

```json
{
  "command": "validate",
  "status": "PASS",
  "profile": "standard",
  "findings": [
    {"id": "desc-pushy", "severity": "warn",
     "goal": "触发准确（目标，不是规则）",
     "evidence": "description 未含 Use when/Invoke on 句式",
     "options": ["补 Use when 触发句", "改用官方第三人称+Use when 形态", "接受现状"],
     "question": null},
    {"id": "sem-markup", "severity": "info",
     "goal": "机器可解析（仅构建者技能需要）",
     "evidence": "未检出 @工作流 头",
     "options": ["补语义标记", "声明运行型豁免"],
     "question": "该技能是否被工具链消费？"}
  ],
  "decision_required": null
}
```

关键点：**脚本报「是什么 + 为什么重要 + 有哪些可选方向」，不报「你必须怎么改」**。`question` 非空时 AI 必须把问题带给用户（人工介入口）。

### 4. 检查点（plan-gate + checkpoint）

**plan-gate**：高成本/写文件命令要求先有计划文件，模板五节：

```markdown
# Plan-Gate：loop <skill-path>
## 目标：<一句话，要达成什么而非跑什么命令>
## 范围与边界：<动什么 / 绝不动什么>
## 参数：<关键参数取值与理由（如 --runs-per-query 3、最多 5 轮）>
## 停止条件：<何时算完成；何时提前中止（如 validation 通过率连续 2 轮无提升）>
## 回滚：<出错如何恢复（如 description 备份原值）>
```

- 适用命令：`eval` / `loop` / `improve`（真实调用 claude，高成本）；`init` / `package` / `generate-templates` / `selfheal`(apply)（写文件）。
- 约定：AI 调用前先把 plan 给用户看（P-V-H 对齐），用户认可后带 `--plan <file>` 执行；人类自用可 `--plan-text "<一句话>"` 快速通道。
- **checkpoint 转述协议**：`loop` 每轮迭代输出一行 JSON：

```json
{"checkpoint": {"iteration": 2, "done": "第2轮 train 17/20，修了误触发边界", "next": "第3轮改用意图句式", "risks": "validation 无提升则按计划停止", "stop_condition_met": false}}
```

  SKILL.md 硬规则补一条：**AI 收到 checkpoint 输出必须向用户转述思路与下一步，用户可随时打断调整**——满足「关键节点让 AI 说明思路」。

### 5. 人工介入（既有先例的推广）

- `selfheal` 已是 dry-run 默认 → `init` / `package` / `generate-templates` 推广为 dry-run 默认 + `--write` 落盘（**默认值变更，待拍板**）。
- `advisory` profile 本身就是人工介入空间：AI 拿不准时主动降 profile 只取证不判断。
- `decision_required` 字段是唯一合法的「脚本喊人」通道；AI 见到必须停下问用户。

## File Structure（改动地图）

| 文件 | 动作 | 职责 |
|---|---|---|
| `skill-workshop/scripts/_impl/_gate.py` | 新建 | `load_plan` / `require_plan` / `emit_checkpoint` 三个纯 stdlib helper |
| `skill-workshop/references/templates/plan-gate-template.md` | 新建 | 五节计划模板 |
| `skill-workshop/references/config/script-profiles.yaml` | 新建 | profile → 判据映射（strictness 外置） |
| `skill-workshop/scripts/_impl/quick_validate.py` | 修改 | `--profile` 参数 + findings JSON 输出 + profile 映射消费 |
| `skill-workshop/scripts/_impl/run_eval.py` / `run_loop.py` / `improve_description.py` | 修改 | plan-gate 接线 + checkpoint 输出（loop） |
| `skill-workshop/scripts/_impl/init_skill.py` / `package_skill.py` / `generate_scenario_templates.py` | 修改 | dry-run 默认 + `--write`（已拍板） |
| `skill-workshop/scripts/skill_cli.py` | 修改 | 透传 `--profile`；无逻辑变更 |
| `skill-workshop/SKILL.md` | 修改 | 硬规则补 2 条（checkpoint 转述义务 / plan-gate 流程）；渐进披露表加模板行 |
| `skill-workshop/SKILL.md` + `VERSION.md` | 修改 | 版本 1.23.0 |

明确不改：`review_ops.py`（--json 已达标）、`routing_check.py` / `selfheal.py` / `review.py` / 编辑器类命令、评测阈值本身（已是 CLI 参数）。

---

### Task 1: `_gate.py` helper + 计划模板

**Files:**
- Create: `skill-workshop/scripts/_impl/_gate.py`
- Create: `skill-workshop/references/templates/plan-gate-template.md`

**Interfaces:**
- Produces: `require_plan(args_plan: str | None, args_plan_text: str | None, command: str) -> str`（返回计划文本；两者皆缺则 print 结构化 `decision_required` 到 stdout 并 exit 2）；`emit_checkpoint(done: str, next_step: str, risks: str, extra: dict) -> None`（stdout 单行 JSON）。

- [ ] **Step 1: 写 `_gate.py`（约 60 行，无 input、无网络、纯 stdlib）**

```python
"""Plan-gate 与 checkpoint 辅助（目标驱动脚本协议）。

约定：脚本不阻止 AI 行动，只把「未附计划」表达为结构化 decision_required，
由 AI 转述用户后带 --plan 重跑。人类可用 --plan-text 快速通道。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PLAN_SECTIONS = ("目标", "范围与边界", "参数", "停止条件", "回滚")


def require_plan(plan_file: str | None, plan_text: str | None, command: str) -> str:
    if plan_text:
        missing = [s for s in PLAN_SECTIONS[1:] ]  # 快速通道只要求目标隐含在文本中
        return plan_text
    if plan_file:
        try:
            text = Path(plan_file).read_text(encoding="utf-8")
        except OSError as e:
            # 审查门 R6：文件不可读输出结构化决策请求，不抛裸 traceback
            print(json.dumps({
                "decision_required": {"topic": f"计划文件不可读: {e}",
                                       "options": ["检查路径后重跑", "改用 --plan-text"]}
            }, ensure_ascii=False))
            raise SystemExit(2)
        missing = [s for s in PLAN_SECTIONS if s not in text]
        if missing:
            print(json.dumps({
                "decision_required": {
                    "topic": f"{command} 计划缺节: {missing}",
                    "options": ["补全计划文件后重跑", "改用 --plan-text 一句话计划"],
                }
            }, ensure_ascii=False))
            raise SystemExit(2)
        return text
    print(json.dumps({
        "decision_required": {
            "topic": f"{command} 属高成本/写文件命令，需先出示计划",
            "options": [
                "AI 先给用户看五节计划，确认后带 --plan <file> 重跑",
                "人类自用：--plan-text '<一句话>' 快速通道",
            ],
        }
    }, ensure_ascii=False))
    raise SystemExit(2)


def emit_checkpoint(done: str, next_step: str, risks: str, **extra) -> None:
    print(json.dumps({
        "checkpoint": {"done": done, "next": next_step, "risks": risks,
                       "stop_condition_met": False, **extra}
    }, ensure_ascii=False))
```

- [ ] **Step 2: 写 `plan-gate-template.md`**（frontmatter: `name` / `description` / `version: 2026-09` / `trigger-when: 调用 eval/loop/improve 及写文件类命令前` / `role: template`），正文 = 设计节 4 的五节模板 + 两条使用约定（AI 先示计划给用户；人类 --plan-text 快速通道）。

- [ ] **Step 3: 验证**

Run: `python skill-workshop/scripts/skill_cli.py validate skill-workshop; python skill-workshop/scripts/skill_cli.py routing-check`
Expected: PASS（新文件含 trigger-when；`_gate.py` 无语法错误：`python -c "import sys; sys.path.insert(0,'skill-workshop/scripts'); from _impl import _gate"`）。

- [ ] **Step 4: Commit（待用户批准）**：`feat(skill-workshop): 新增 plan-gate 协议 helper 与计划模板`

---

### Task 2: 高成本/写文件命令接线 plan-gate

**Files:**
- Modify: `skill-workshop/scripts/_impl/run_eval.py` / `run_loop.py` / `improve_description.py`（main() 开头加 `require_plan`；loop 迭代循环内加 `emit_checkpoint`）
- Modify: `skill-workshop/scripts/_impl/init_skill.py` / `package_skill.py` / `generate_scenario_templates.py` / `selfheal.py`（写文件动作前加 `require_plan`；selfheal 保持 dry-run 默认，仅 apply 模式 gate）

**Interfaces:**
- Consumes: Task 1 的 `require_plan` / `emit_checkpoint`。

- [ ] **Step 1: 三个高成本命令 main() 加参数与接线**

每个命令 argparse 增：`--plan`（计划文件路径）、`--plan-text`（一句话计划，**仅限人类直接调用**）。main() 在校验通过、即将开跑前调 `require_plan(args.plan, args.plan_text, "loop")`。`run_loop.py` 迭代循环每轮末尾调 `emit_checkpoint(...)`（内容取自当轮 summary：done=本轮 train/test 得分与修改要点，next=下轮策略，risks=停止条件状态）；**loop 首轮开跑前打印将被修改的原 description 全文**，供 AI/用户确认回滚基线（审查门 R9——中途打断的恢复锚点）。

- [ ] **Step 2: 写文件命令 dry-run 默认（已拍板：执行）**

`init` / `package` / `generate-templates` 增 `--write` 标志；默认只打印将要创建的路径树（dry-run）。`selfheal` 的 apply 模式加 `require_plan`。
**已确认（2026-09-11）**：执行默认值变更；VERSION.md 条目记录 breaking 变更提示（人类直接调用需加 `--write`）。

- [ ] **Step 3: 验证**

Run: `python skill-workshop/scripts/skill_cli.py loop --help`，Expected: help 含 `--plan` / `--plan-text`。
Run: 无 `--plan` 直接跑 `eval`（用临时 eval-set），Expected: stdout 输出 `decision_required` JSON，exit 2——**AI 视角这是"该去问用户"的信号而非报错**。
Run: `python skill-workshop/scripts/skill_cli.py eval --help` 等全量 `--help` 巡检，Expected: 全部正常（纪律：--help 不受 gate 影响）。

- [ ] **Step 4: Commit（待用户批准）**：`feat(skill-workshop): 高成本/写文件命令接入 plan-gate 与 checkpoint`

---

### Task 3: validate 类命令 `--profile` + findings JSON

**Files:**
- Create: `skill-workshop/references/config/script-profiles.yaml`
- Modify: `skill-workshop/scripts/_impl/quick_validate.py`（`--profile`；findings 组装；profile 消费）
- Modify: `skill-workshop/scripts/skill_cli.py`（validate 子命令透传，无逻辑变更）

**Interfaces:**
- Produces: `validate ... --json --profile advisory` 输出设计节 3 的 findings schema。

- [ ] **Step 1: 写 `script-profiles.yaml`**

```yaml
# profile → 判据映射。改判级只改此文件，不改代码。
profiles:
  strict:    # 历史行为，兼容 CI
    fail_on: [official-hard, incident-backed, style-regex]
  standard:  # 默认：仅硬边界判 FAIL
    fail_on: [official-hard, incident-backed]
  advisory:  # 只报不判
    fail_on: []
rule_classes:
  official-hard:   [desc-nonempty, desc-length, desc-xml, name-format, dir-match]
  incident-backed: [desc-singleline, version-consistency, link-integrity]
  style-regex:     [desc-pushy, desc-trigger-count, sem-markup, structure-patterns]
```

> **安全默认（审查门 R4）**：新增检查点未在 `rule_classes` 归类时，一律按 `style-regex`（软）处理——漏归类只会 warn，不会误 FAIL。

- [ ] **Step 2: quick_validate 接线**

`validate_description_format` 等检查点改为产出 finding 对象（复用现有 message，补 `severity` 已在 description 对齐计划 Task 5 实现——本任务只把 severity 按 profile 折算成 PASS/FAIL 与 findings 列表）。`--json` 输出 findings；非 JSON 模式保持现有人读输出不变。

- [ ] **Step 3: 验证（三态）**

Run: `validate skill-workshop --json --profile strict` / `--profile standard` / `--profile advisory`
Expected: strict 与现行为一致；standard 下 style 类为 warn 不断链；advisory status 恒为 `PASS`（附 findings）且不写任何文件。
Run: `validate zuiti --json --profile advisory`，Expected: 输出 findings 且 exit 0。

- [ ] **Step 4: Commit（待用户批准）**：`feat(skill-workshop): validate 支持 profile 分级与 findings JSON 输出`

---

### Task 4: 协议入文档（SKILL.md 硬规则 + 路由）

**Files:**
- Modify: `skill-workshop/SKILL.md`（§2 硬规则补 2 条；§4 渐进披露表补 `plan-gate-template.md` 行）
- Modify: `skill-workshop/VERSION.md`（v1.23.0 条目）

- [ ] **Step 1: SKILL.md 硬规则补 2 条**

```markdown
- @动作: 调用 eval/loop/improve 或任何写文件命令前，必须先向用户出示 plan-gate 五节计划（目标/范围与边界/参数/停止条件/回滚），用户认可后带 --plan 执行；收到脚本 decision_required 输出 = 脚本在等用户决策，必须转述，不得自行绕过。*Why: 脚本守边界不挡路，但成本与不可逆动作的否决权始终在用户手里。*
- @动作: 收到 checkpoint 输出必须向用户转述「已完成/下一步/风险」，用户可随时打断调整策略；advisory 拿不准时主动降 profile 只取证不判断。*Why: 脚本供证据，AI 做权衡，用户握方向——三者职责不混。*
```

- [ ] **Step 2: 版本与验证**

`metadata.version` → 1.23.0；VERSION.md 条目记录本计划。跑 `validate` / `consistency` / `routing-check` 全 PASS。

- [ ] **Step 3: Commit（待用户批准）**：`docs(skill-workshop): plan-gate 与 checkpoint 协议入硬规则，版本 1.23.0`

---

### Task 5: 全量门禁回归

- [ ] `spec` / `validate` / `consistency` / `checklist` / `routing-check` 全 PASS；changelog-manager / zuiti 回归 PASS。
- [ ] 人工核对：AI 视角走一遍「eval 无 plan → decision_required → 出示计划 → 用户确认 → 带 plan 重跑 → checkpoint 转述」全链路（可用临时 eval-set 干跑，不真调 claude：eval 在 skill 校验失败时即短路，够验证 gate 行为）。
- [ ] Commit（待用户批准）：`chore(skill-workshop): 脚本柔性化回归收尾`

---

## 已拍板决策（2026-09-11 用户确认）

1. **dry-run 默认值变更**：确认改——`init` / `package` / `generate-templates` 默认 dry-run，`--write` 落盘（Task 2 Step 2 执行）。
2. **`_gate.py` 新脚本文件**：已批准（纯 stdlib 约 60 行，Task 1 执行）。
3. **profile 默认值**：standard（`script-profiles.yaml` 默认指向 standard，Task 3 执行）。
4. **Phase 2（判级全面 findings 化重构）**：转为待办 backlog，暂不立项——待本计划回归后按需再议。

## 待办 Backlog（暂不立项）

- Phase 2：`quick_validate.py` 全部检查点改造为 findings 模型；`spec` / `consistency` 等 review_ops 系命令 findings 化与 `--profile` 接入（Phase 1 仅 validate 先行）。
- findings JSON schema 与 review_ops 系命令既有 JSON 字段统一（当前 `status/errors` 与 `findings` 两套并存，Phase 1 靠保留旧字段兼容，审查门 R5）。
- C 档评审链架构收敛（三套评估并存、W0-W7 状态门重量、清单 P 级分配）——见 description 对齐计划待审查项 10。
