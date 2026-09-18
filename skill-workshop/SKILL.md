---
name: skill-workshop
description: "Skill 质量工作站：创建 / 评审 / 重构 / 合规校验 Agent Skill——L0 轻查默认、L1 疑点展开；CLI：validate/package/init/spec。Use this skill to create, review, refactor, or validate an Agent Skill, or when another skill hands off a Skill project for quality review. Invoke on '做个新 skill'/'帮我看看这个 skill'/'audit skill'/'重构 skill'/'校验 skill 规范'. Not for: 通用代码调试、非 Skill 文档、Agent 框架、应用类项目代码审查."
metadata:
  author: ErgeAIA
  version: "2.0.1"
---

# skill-workshop

## 定位

轻量 **Skill 质量工作站**（v2）。第一性目标：用最低审查成本，可靠发现会导致**触发错误、执行错误、非破坏契约破坏、上下文膨胀**的缺陷。

```text
低成本发现高风险问题 → 有证据的整改方向 → 必要时才深度诊断
```

不是治理系统：不默认跑固定 W1–W7 全量流水线；不强制凑优点、强制拆分、固定收尾套话；不要求每个 Skill 都具备脚本或评测集。

**不可违背**：① 不破坏用户已有 skill 产物；② 遵守 Agent Skills 官方 frontmatter 约束；③ 机械问题交给 CLI，不靠模型记忆；④ 每条问题必须落到文件证据。

**边界**：只处理 Agent Skill（含其他技能转交的 Skill 路径）；不替代人类最终业务判断；评审路径默认只出报告。

## 路由

| 用户意图 | 进入 | 产出 |
| --- | --- | --- |
| 创建 / 做一个 / 封装 skill | 读 `references/creation.md`；需要骨架时 CLI `init` | SKILL.md + 目录 |
| 帮我看看 / 评审 / 审计 | **L0 默认**；疑点或显式深度 → **L1**（`references/review.md`） | 短报告 |
| 校验 / 合规 / validate | CLI `spec` + `validate` | PASS/FAIL |
| 重构 / 优化 / 整理结构 | L0/L1 找问题 → 按 `creation.md` + `validation.md` 整改 → 再校验 | 改进后的技能 |
| 评测 / benchmark / 触发率 | **L2 条件**：用户明确要求才进入；工具在 `docs/archive/` | 评测结论 |
| 他技转交 Skill 审查 | 同「评审」入口（默认 L0） | 短报告 |
| 意图模糊 | 只澄清必要信息；不默认追问三连 | 路由决策 |

命中清晰信号即直接进入；不要先问「您要哪一种工作流编号」。

### L0 / L1 / L2（摘要）

- **L0**（默认）：frontmatter、description、主职责内聚、主文档体量、references 结构、明显冲突、输出契约。读取预算：SKILL.md + 最多 1–3 份相关文件。
- **L1**：第一性锚定、T/E/C 三轴证据化 findings、CONDITIONAL 项、非破坏与脚本纪律（若有）、方向性争议才上钢人。按疑点扩展读取，禁止默认全量预读。
- **L2**：触发率/回归/基准实测；从 `docs/archive/` 启用历史评测链并在报告标明。

详细分级与反膨胀四问 → `references/core-method.md`；评审判据与报告结构 → `references/review.md`。

## 核心约束

1. **主文档只做路由与硬边界**；细节按需读 references；禁止全量预加载目标技能的全部 references/scripts。
2. **规则分级**：HARD 阻塞「通过」；CONDITIONAL 无对应能力则 N/A；HEURISTIC 有证据才报，不升格 P0。
3. **废除硬凑**：无优点则省略；无职责耦合则写「无需拆分」；不写固定收尾套话。
4. **版本 SSOT**：`metadata.version` + 根目录 `CHANGELOG.md`；不默认要求正文三处版本块一致。
5. **脚本与评测非必须**：无 `scripts/` 的指令型 Skill 可以优秀；有脚本才查无交互/`--help`/退出码/流分离；评测仅 L2、高风险或显式要求。
6. **新建产物纯净**：不注入步骤级 `@` 标记；路径用标准 Markdown 相对链接或自然语言描述。
7. **写文件走 plan-gate**：`init` / `package --write` 默认 dry-run；AI 必须先出示计划；脚本 `decision_required` 必须转述给用户。
8. **验证闭环**：创建/重构后必须跑 `validate`（建议同时 `spec`）；脚本 FAIL 不得宣称通过。
9. **证据纪律**：结论能指到文件；无产物的步骤视为未执行；未跑命令不得写「已验证」。
10. **裁判边界**：评审不直接改用户文件；构建路径才写盘，且非破坏。

## CLI（运行时仅此四项）

```bash
python scripts/skill_cli.py validate <skill-dir>
python scripts/skill_cli.py spec <skill-dir>
python scripts/skill_cli.py init <skill-name> --path <parent> [--write]
python scripts/skill_cli.py package <skill-dir> [out-dir] [--write]
```

退出码：`0=PASS`，`1=FAIL`，`2=ERROR`。诊断写 stderr。PowerShell 下用 `;` 串联命令。

已归档子命令（reconcile / family-diff / checklist / consistency / eval / loop 等）见 `docs/archive/scripts/`，调用旧名会得到归档提示。

## 构建路径（创建 / 重构）

1. 用本文件路由确认意图（创建 vs 重构 vs 只评审）。
2. 读 `references/creation.md`（模板与硬字段）与 `references/validation.md`（闸门）。
3. 落盘前：创建用 `init` dry-run 预览；重构只动目标技能权威源，不碰运行态目录。
4. 落盘后：`spec` + `validate`；需要分发时再 `package --write`。
5. 升版：同步 `metadata.version`、`CHANGELOG.md`、根 README，并跑索引同步脚本。

评审路径不要跳到第 3–4 步，除非用户明确授权写文件。

## L0 检查清单（评审默认扫这些）

- [ ] frontmatter：`name`/`description` 合规，无越权顶层字段  
- [ ] description：做什么 + 何时触发 + 边界是否清楚  
- [ ] 职责：是否一个连贯用户任务单元（不是机械步骤计数）  
- [ ] 主文档：体量、是否只路由、是否全量堆砌  
- [ ] references：该有的 trigger 说明、死链、是否被主文档正确指向  
- [ ] 明显冲突：已打开文件之间同一规则是否打架  
- [ ] 输出契约：是否写清必须产出什么  

有疑点再升 L1，不在 L0 阶段扩大读取面。

## 资源指引（按需读取）

| 文件 | 何时读 |
| --- | --- |
| `references/core-method.md` | 路由分级、证据预算、HARD/CONDITIONAL/HEURISTIC、反膨胀四问 |
| `references/creation.md` | 创建/脚手架、纯净模板、description 轻量写法、目录骨架 |
| `references/review.md` | T/E/C 三轴、L0/L1 判据、条件项速查、默认报告结构 |
| `references/validation.md` | 格式 HARD 项、版本对齐、CLI/plan-gate、安全与失败处理 |

`docs/archive/`：历史 workflows、旧检查脚本、评测 agents——仅条件诊断时查阅，不写回默认报告模板。

## 默认输出（评审短报告）

1. 一句话结论  
2. 第一性判断（方向存疑或 L1 时）  
3. 值得保留的设计（0–N 条，无则整节省略）  
4. 问题清单（P0/P1/P2 + 文件证据 + HARD/CONDITIONAL/HEURISTIC）  
5. 最值得做的 ≤3 个动作  
6. 是否建议继续重构（是/否 + 一句理由）

## Gotchas

- `description` 禁止尖括号；`name` 必须等于目录名且 hyphen-case。
- `validate .` 在子目录内运行时，路径解析以真实目录名为准；显式传路径更稳妥。
- `package`/`init` 不带 `--write` 不会落盘；这是 plan-gate 特性。
- 不要把 `docs/archive/` 里的旧 W 流水线或 54 项清单默认套到新报告上。
- 升版时同步：`metadata.version` = `CHANGELOG.md` 顶部 = 根 README 索引，并跑 Skills-Depot 的 `sync_skills_browser.py`。

## 非目标

- 通用代码/应用项目审查、Agent 框架开发、与 Skill 无关的文档创作  
- 默认重建治理式全量检查或强制 8 维评分  
- 在评审路径中未授权写文件  
- 运行态目录（`~/.agents/skills` 等）的安装与修改  

## 验证闭环

- 交付前：`spec` + `validate` 均应 PASS（advisory 发现不阻塞，FAIL 阻塞）。
- 本技能：版本三处对齐 + 用户验证后方可宣称重构完成。
