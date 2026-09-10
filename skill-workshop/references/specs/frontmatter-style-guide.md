---
version: 2026-09
purpose: SKILL.md frontmatter 风格指南（非审查规则，仅供参考）
trigger-when: 用户主动询问 frontmatter 风格、设计新 Skill 或审视现有 Skill 复杂度时
role: design-reference
consumed-by: skill-creator（设计参考）、用户自检
not-consumed-by: W3（不作为判定依据）
---

# SKILL.md Frontmatter 风格指南

> 本文档为参考指南，不作为审查判定依据。一切以官方规范（spec.md）为准。

## 一、字段分类

### 必需字段（官方硬限）

| 字段 | 含义 | 示例 |
|------|------|------|
| `name` | 技能唯一标识，必须与目录名一致 | `my-skill` |
| `description` | 描述技能用途和触发条件 | `处理 PDF 文件...` |

### 官方可选字段

| 字段 | 含义 | 何时使用 |
|------|------|----------|
| `license` | 开源协议 | 明确需要声明协议时 |
| `compatibility` | 运行环境要求 | 有特定依赖时（如 `Python ≥ 3.10`） |
| `metadata` | 扩展元数据容器 | 需要携带额外结构化信息时 |
| `allowed-tools` | 工具白名单 | 需要限定可用工具时（实验性） |

## 二、metadata 内部字段参考

以下字段可放在 `metadata` 中，**非强制**：

| 字段 | 含义 | 建议 |
|------|------|------|
| `version` | 版本号 | ✅ 建议保留 |
| `author` | 作者/维护者 | ✅ 建议保留 |
| `origin` | 提炼背景 | 可选，解释 Skill 来源 |
| `triggers` | 触发短语列表 | 可选，也可直接写在 description 中 |
| `created` | 创建日期 | 建议放 VERSION.md |
| `updated` | 更新日期 | 建议放 VERSION.md |

## 三、简洁模板（推荐）

适合大部分 Skill，**metadata 可选**：

```yaml
---
name: my-skill
description: 技能用途描述，说明何时触发使用
license: MIT
---
```

### 带 metadata 的稍完整版

```yaml
---
name: my-skill
description: 技能用途描述，说明何时触发使用
metadata:
  version: "1.0"
  author: ErgeAIA
---
```

## 四、精简模板（最简）

适合纯指令型 Skill：

```yaml
---
name: my-skill
description: 简短描述
---
```

## 五、VERSION.md 信息归属

有 VERSION.md 的 Skill，建议将以下信息迁移到该文件：

| 原可能放 frontmatter 的信息 | 迁移到 VERSION.md |
|---------------------------|------------------|
| `created` | CHANGELOG 第一条 |
| `updated` | CHANGELOG 最新条目日期 |
| `origin` | CHANGELOG 或文件注释 |
| `version` | 文件名本身已是来源 |

**理由**：
- VERSION.md 天然携带时间线
- 避免 frontmatter 过度工程化
- 保持 frontmatter 轻量

## 六、热门 Skills 常见模式（观察，2026-09 收缩）

> 对高安装量 Skills 的观察结论：大部分不超过 5 个 frontmatter 字段（极简 = `name` + `description`，至多 + `license` / `metadata.version`）。§7 的「先问必要性」即可覆盖该结论，不再维护会过期的快照表。

## 七、设计原则

1. **先问必要性**：添加每个字段前问"没有它会怎样？"
2. **description 优先**：触发信息优先放在 description 中，而非 triggers 数组
3. **渐进式披露**：复杂信息移到 references/ 或 VERSION.md
4. **官方为准**：本文档与官方规范冲突时，以官方规范为准

## 八、非审查规则声明

本文档：
- ✅ 是参考指南，帮助设计清晰的 frontmatter
- ✅ 仅在用户主动询问 frontmatter 风格或设计新 Skill 时加载
- ❌ 不是审查判定依据
- ❌ 不约束已有 Skill 的结构选择
- ❌ 不在 V0 校验或 W 系列评审中作为 PASS/FAIL 标准
- ❌ W3 问题扫描不得引用本文档作为问题证据

你的 Skill 你做主，简洁或完整都是合理选择。

---

## 九、description 字段联锁规则（引用 spec.md 真源）

> **本节自 2026-09 起为引用式**：判据唯一真源是 [spec.md §description 格式约束](spec.md#description-格式约束（v0-w7-强约束）)，本节不复刻数值、只给设计视角的正反对照。两者冲突时以 spec.md 为准。

| 维度 | 设计视角要点 |
| --- | --- |
| 格式 | YAML 单行 string（禁 `\|` 块）——外部技能管理软件对折叠块有转义风险 |
| 风格 | Pushy 主动触发（功能句 + `Use when…`/`Invoke on…` 触发句两段都要有） |
| 意图 | 聚焦用户意图，不堆实现细节；关键词嵌在触发句内，不做裸词表 |
| 边界 | 声明不适用场景（`Not for: …`）是 description 的合法且推荐成分——它是"何时使用"的镜像 |
| 长度 | 硬限 1024 字符；软建议几句话到一个短段落（无自设区间） |

### 反例（YAML 块 + 无边界声明 + 触发词缺失）

```yaml
description: |
  示例技能 · 中文科技文本事实核查。使用触发词："验真"/"fact-check"/"查证"/"核实"——
  加载后对粘文本/具体数字/产品版本/人物引用/出处归属 跑三步流水线（抽取→联网验证→修复建议）。
```

**违反**：YAML 块（应单行）+ 无 Pushy 句式 + 无 "Not for" 边界。

### 正例（满足全部约束）

```yaml
description: Use this skill whenever the user wants to fact-check concrete claims in Chinese tech text (numbers/dates/versions/attribution). Invoke on "验真"/"fact-check"/"查证"/"核实". Not for style/formatting/compliance/writing.
```

**满足**：单行 string + Pushy "Use this skill whenever" + 触发词嵌入 "Invoke on" 句内 + "Not for" 边界声明；长度在软建议区间内。
