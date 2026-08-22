---
trigger-when: 校验 skill-workshop 自身路由完整性、修改任何 workflow 或 SKILL.md 路由表前
name: routing-table
description: skill-workshop 9 个 authoring 文件 × 5 个 workflow reads-from 块的全量引用关系真相源。本表是路由一致性硬校验（versioning-and-validation.md §4.4）的唯一判定依据，SKILL.md "渐进式披露"路由表与各 workflow `reads-from:` 块必须与本表保持一致。
version: 1.0.0
---

# skill-workshop 路由表（Routing Table）

<!-- @类型: 索引表 -->
<!-- @目的: 防止"有规范但用不上"——把分散在 SKILL.md 路由表 + 各 workflow reads-from 块 + 各 references 文件 frontmatter `trigger-when` 中的引用关系收敛到单一真相源 -->
<!-- @场景: 路由完整性审计、workflow 调整、SKILL.md 路由表改写、authoring 文件新增/删除 -->
<!-- @后置验证: 本表与 SKILL.md 路由表、5 个 workflow 的 reads-from 块、9 个 authoring 文件的 trigger-when 块三处一致 -->

> **一句话**: 任何 routing 信息（SKILL.md 路由表、workflow 的 `reads-from`、references 的 `trigger-when`）必须与本表一致；不一致即为路由失配，需 P1 修复

---

## 1. 9 个 authoring 文件 × 引用方

| 文件 | SKILL.md 路由表 | W0-W7 workflow reads-from | 直接 trigger-when |
|------|----------------|---------------------------|-------------------|
| `authoring/skill-foundations.md` | ✅ 创建 Skill | — | ✅ |
| `authoring/progressive-disclosure-patterns.md` | ✅ 渐进披露模式 | ✅ **W7**（Step 6 6.2） | ✅ |
| `authoring/naming-and-ownership.md` | ✅ 命名与归属 | — | ✅ |
| `authoring/versioning-and-validation.md` | ✅ 版本一致性（V0 硬校验 + 规范指南） | ✅ **V0**（reads-from 必读）+ ✅ **W3**（S6 升级依据） | ✅ |
| `authoring/skill-markup-guide.md` | ✅ 语义标记规范 | — | ✅ |
| `authoring/workflow-patterns.md` | ✅ 工作流模式 | — | ✅ |
| `authoring/business-to-workflow-mapping.md` | ✅ 业务到工作流映射 | — | ✅ |
| `authoring/skill-refactoring-workflow.md` | ✅ 重构指引 | — | ✅ |
| `authoring/skill-evaluation-workflow.md` | ✅ 评测方法 | — | ✅ |

> 上述 9 个文件已全部被 SKILL.md 路由表直接引用，达成 100% 覆盖（修复前仅 4/9 = 44%）。v1.18.0 删除了与 specs/best-practices.md 职责重复的旧写作方法论文件。

## 2. 4 个 specs 文件 × 引用方

| 文件 | SKILL.md 路由表 | W0-W7 workflow reads-from | 直接 trigger-when |
|------|----------------|---------------------------|-------------------|
| `specs/spec.md` | ✅ 规范校验 | ✅ V0 | ✅ |
| `specs/validate.md` | ✅ 规范校验 | ✅ V0 | ✅ |
| `specs/best-practices.md` | ✅ 软性建议补充 | ✅ W3 | ✅ |
| `specs/frontmatter-style-guide.md` | ✅ frontmatter 字段过度工程化判定 | ✅ **W3**（S6）+ ✅ **W7**（Step 6 6.1） | ✅ |

## 3. 4 个 rubrics 文件 × 引用方

| 文件 | SKILL.md 路由表 | W0-W7 workflow reads-from | 直接 trigger-when |
|------|----------------|---------------------------|-------------------|
| `rubrics/review-checklist.md` | ✅ 优点/问题扫描 | ✅ W3 | ✅ |
| `rubrics/intent-calibration.md` | ✅ description 审计 | ✅ W7 | ✅ |
| `rubrics/complexity-rubric.md` | ✅ 复杂度判定 | — | ✅ |
| `rubrics/weighted-scoring.md` | ✅ 快速评分 | — | ✅ |

## 4. 5 个 workflow 的 reads-from 块全量

### 4.1 W3-issues.md
```
reads-from:
  - references/rubrics/review-checklist.md  # 唯一判定标准源
  - references/specs/best-practices.md      # 软性维度溯源（M/P/V/B）
  - references/specs/frontmatter-style-guide.md  # S 系列 frontmatter 过度工程化判定（S6）
  - references/authoring/versioning-and-validation.md  # S6 版本三处一致性硬校验
calls: workflows/W7-description-audit.md     # T 系列强制委托
```

### 4.2 W7-description-audit.md
```
reads-from:
  - references/rubrics/intent-calibration.md             # T1-T5 示例与阈值标尺
  - references/specs/frontmatter-style-guide.md         # description 字符数 / 字段归属 / 渐进披露定位
  - references/authoring/progressive-disclosure-patterns.md  # description 作为 Tier 1 角色的设计原则
```

### 4.3 V0-validate.md
```
reads-from:
  - references/specs/spec.md             # frontmatter 字段允许表
  - references/specs/validate.md         # 基础硬校验清单
  - references/authoring/versioning-and-validation.md  # 版本三处一致性硬校验
```

### 4.4 W0/W1/W2/W4/W5/W6
无外部 `reads-from` 块（直接消费 W3/W7 报告或本表 §1-§3）

### 4.5 C1/C2/C3
由 C1-create / C2-evaluate / C3-refactor 自己加载 authoring/，不通过 reads-from 块

## 5. 路由失配自检清单

修改任一文件前，先扫一遍下面 3 类失配：

| 失配类型 | 检测方法 | 修复方向 |
|----------|----------|----------|
| **类型 A：authoring 文件未在 SKILL.md 路由表出现** | 遍历 `authoring/` 下 9 个文件名，比对 SKILL.md §4 表格 | 在 §4 补一行 |
| **类型 B：authoring 文件未在任何 workflow `reads-from` 出现** | 遍历 5 个 workflow `reads-from` 块 | 若该文件应被读（如 versioning-and-validation 应被 V0 读），加 `reads-from` |
| **类型 C：workflow 引用了文件但该文件无对应 trigger-when** | 比对 `trigger-when:` 字段 | 补 `trigger-when` 或在 workflow 内联说明触发场景 |

## 6. 路由变更流程

1. **修改前**：先改本表（routing-table.md），锁定"应该被谁引用"
2. **修改中**：同步改 SKILL.md 路由表 + 对应 workflow `reads-from` 块
3. **修改后**：跑 `python scripts/skill_cli.py validate <skill>`，确认路由一致性硬校验通过

## 7. 加载时机 (Loading Timing)

| 文件类别 | 加载时机 | 说明 |
|----------|----------|------|
| SKILL.md 路由表 | Agent 首次识别技能时 | 决定进入哪条 workflow |
| workflow `reads-from` | 进入对应 workflow 时 | 按需加载，不预读 |
| authoring/ 文件 | workflow 步骤引用时 | 仅在步骤明确要求时读取 |
| rubrics/ 文件 | W2/W3/W7 扫描阶段 | 评审流程专用 |
| specs/ 文件 | V0 校验或 W3/W7 需要时 | 规范判定时才加载 |
| routing-table.md | 路由一致性校验时 | 不在运行时加载，仅供维护 |

---

## 版本历史

- **v1.0.0** (2026-06-18) - 初版；修复 PUA 模式发现的 5 类路由失配：W3 补 frontmatter-style-guide/versioning-and-validation、V0 补 versioning-and-validation、W7 补 frontmatter-style-guide/progressive-disclosure、SKILL.md 路由表从 4/9 覆盖扩至 9/9、authoring 0/5 workflow 引用扩至 2/5
