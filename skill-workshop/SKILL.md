---
name: skill-workshop
description: "Skill 质量工作站：创建 / 评审 / 重构 / 合规校验 Agent Skill——L0 轻查默认、L1 疑点展开；CLI：validate/package/init/spec。Use this skill to create, review, refactor, or validate an Agent Skill, or when another skill hands off a Skill project for quality review. Invoke on '做个新 skill'/'帮我看看这个 skill'/'audit skill'/'重构 skill'/'校验 skill 规范'. Not for: 通用代码调试、非 Skill 文档、Agent 框架、应用类项目代码审查."
metadata:
  author: ErgeAIA
  version: "2.1.0"
---

# skill-workshop

## 定位

轻量 **Skill 质量工作站**。第一性目标：用最低审查成本，可靠发现会导致**触发错误、执行错误、非破坏契约破坏、上下文膨胀**的缺陷。

```text
Core Task 锚点 → 风险驱动分级 → 证据化 findings → Rule Compression 方向
```

不是治理系统：不默认固定 W1–W7 全量流水线；不强制凑优点/拆分/收尾套话；不要求每个 Skill 都有脚本或评测集。

**不可违背**：① 不破坏用户已有 skill 产物；② 遵守 Agent Skills 官方 frontmatter 约束；③ 机械问题交给 CLI；④ 问题必须落到文件证据；⑤ **单一审计主流程**——方法论是判断框架，不是第二套并行流程。

**边界**：只处理 Agent Skill；不替代人类最终业务判断；评审路径默认只出报告。

## 路由

| 用户意图 | 进入 | 产出 |
| --- | --- | --- |
| 创建 / 做一个 / 封装 skill | 读 `references/creation.md`；CLI `init` | SKILL.md + 目录 |
| 帮我看看 / 评审 / 审计 | **Fast Review（L0）**默认；疑点或显式深度 → **Deep Review（L1）** | 报告（`references/review.md`） |
| 校验 / 合规 / validate | CLI `spec` + `validate` | PASS/FAIL |
| 重构 / 优化 / 整理结构 | 先审计 → 按 Rule Compression 整改 → `spec`+`validate` | 改进后的技能 |
| 评测 / benchmark / 触发率 | **Eval Review（L2）**条件；工具在 `docs/archive/` | 评测结论 |
| 他技转交 Skill 审查 | 同评审入口（默认 Fast） | 报告 |
| 意图模糊 | 只澄清必要信息 | 路由决策 |

命中清晰信号即进入；不要先问「您要哪一种工作流编号」。

### Fast / Deep / Eval（摘要）

- **Fast（L0）**：默认。目录清单 + SKILL + 1–3 份相关文件；六段短报告。  
- **Deep（L1）**：Core Task 五问、Evidence-First、规则生命周期、结构膨胀、Rule/File Disposition（按需）。  
- **Eval（L2）**：条件实测；归档工具须标明。  

判断框架（五问/六类/生命周期/删除优先/HARD 防火墙）→ `references/core-method.md`；评审步骤与报告结构 → `references/review.md`。

## 核心约束

1. **主文档只做路由与硬边界**；细节按需读 references；禁止全量预加载目标技能全部 references/scripts。  
2. **规则生命周期**：HARD / CONDITIONAL / HEURISTIC / EXPERIMENTAL / ARCHIVED；CONDITIONAL 条件不成立 = N/A。  
3. **删除优先**：删除 > 合并 > 条件化 > 迁移 > 重写 > 最后才新增；HARD 需真实失败证据。  
4. **废除硬凑**：无优点则省略；无职责耦合则「无需拆分」；不写固定收尾套话。  
5. **版本 SSOT**：`metadata.version` + 根 `CHANGELOG.md`。  
6. **脚本与评测非必须**：无 scripts 可优秀；评测仅 Eval/高风险/显式要求。  
7. **纯净 Markdown**：不注入步骤级 `@` 标记；不建第二套 DSL。  
8. **Runtime/Governance 分离**：治理规则不注入被审计 Skill 运行时。  
9. **plan-gate**：`init`/`package --write` 默认 dry-run；`decision_required` 必须转述用户。  
10. **验证闭环**：创建/重构后跑 `validate`（建议 `spec`）；FAIL 不得宣称通过。  
11. **证据纪律**：结论能指到文件；无产物=未执行。  
12. **裁判边界**：评审不直接改用户文件；构建路径才写盘且非破坏。  
13. **反治理膨胀**：workshop 自身不得因整合方法论而长出第二流程或巨型 checklist。

## CLI（运行时仅此四项）

```bash
python scripts/skill_cli.py validate <skill-dir>
python scripts/skill_cli.py spec <skill-dir>
python scripts/skill_cli.py init <skill-name> --path <parent> [--write]
python scripts/skill_cli.py package <skill-dir> [out-dir] [--write]
```

退出码：`0=PASS`，`1=FAIL`，`2=ERROR`。诊断写 stderr。PowerShell 用 `;` 串联。

已归档子命令见 `docs/archive/scripts/`。

## 构建路径（创建 / 重构）

1. 路由确认意图（创建 vs 重构 vs 只评审）。  
2. 读 `references/creation.md` 与 `references/validation.md`；判断框架见 `core-method.md`。  
3. 落盘前：创建用 `init` dry-run；重构只动权威源，不碰运行态目录。  
4. 落盘后：`spec` + `validate`；需要时再 `package --write`。  
5. 升版：`metadata.version`、`CHANGELOG.md`、根 README，跑 Skills-Depot 索引同步。  

评审路径不要跳到第 3–4 步，除非用户明确授权写文件。用户已提供**完整重构执行指令**时，按指令执行 + 本技能闸门，不另起平行流程。

## Fast 检查清单（默认）

- [ ] frontmatter：`name`/`description` 合规  
- [ ] description：做什么 + 何时 + 边界  
- [ ] Core Task 能否一句话说清  
- [ ] 职责是否连贯用户任务单元  
- [ ] 主文档体量、是否只路由  
- [ ] references 存在性与加载时机、明显死链  
- [ ] 已打开文件间明显冲突  
- [ ] 输出契约  
- [ ] 明显职责漂移 / 模板化信号  

疑点再升 Deep；不在 Fast 扩大读取面。

## 资源指引（按需读取）

| 文件 | 何时读 |
| --- | --- |
| `references/core-method.md` | 判断框架：Core Task、五问、六类、生命周期、删除优先、证据预算 |
| `references/creation.md` | 创建/脚手架、纯净模板、description 写法 |
| `references/review.md` | Fast/Deep/Eval、T/E/C、风险 P0/P1/P2、报告结构 |
| `references/validation.md` | 格式 HARD、版本 SSOT、CLI/plan-gate、N/A 与安全 |

`docs/archive/`：历史工具与评测链——仅条件诊断，不写回默认报告模板。

## 默认输出（评审）

Fast：六段短报告（结论 / 第一性判断按需 / 可保留设计 / 问题清单 / ≤3 动作 / 是否继续重构）。

Deep：在短报告上附证据化 findings；复杂重构再附 Rule/File Disposition 等扩展字段（见 `review.md`）。

## Gotchas

- `description` 禁止尖括号；`name` 必须等于目录名且 hyphen-case。  
- `validate` 建议传显式路径。  
- `package`/`init` 不带 `--write` 不落盘（plan-gate）。  
- 不要把 `docs/archive/` 旧 W 流水线或巨型 checklist 默认套到新报告上。  
- 升版同步：`metadata.version` = CHANGELOG 顶部 = 根 README，并跑 `sync_skills_browser.py`。  
- **评审 ≠ 重构指令**；执行重构须用户授权；已有完整指令则按指令 + 闸门执行。

## 非目标

- 通用代码/应用项目审查、Agent 框架开发  
- 默认重建全量 W 流水线、巨型 checklist、并行第二审计流程  
- 评审路径未授权写文件  
- 修改运行态目录（`~/.agents/skills` 等）  
- 为 workshop 自身引入 `@` DSL 或治理规则注入目标 Skill

## 验证闭环

- 交付前：`spec` + `validate` 均应 PASS（advisory 不阻塞，FAIL 阻塞）。  
- 本技能：版本三处对齐 + 用户验证后方可宣称重构/整合完成。
