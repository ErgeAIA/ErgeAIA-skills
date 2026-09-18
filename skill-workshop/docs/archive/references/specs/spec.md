---
version: 2026-09
purpose: Claude Skill 官方规范（reference for AI consumption; download-cached mirror of https://agentskills.io/specification）
source: https://agentskills.io/specification
audience: AI agents
role: official-spec
consumed-by: V0 / W3 / W7 / review-checklist / all workflow files
not-consumed-by: human-only-decisions
trigger-when: V0 frontmatter 校验 / W3 结构审查 / W7 description 审计
last-fetched: 2026-06
---

# Agent Skills Specification

> **重要**: 本文件为社区官方规范的本地缓存，供 AI 消费。如与官方源冲突，以官方源为准。
> **已下载的真实源 URL**: https://agentskills.io/specification
> **结构索引**: https://agentskills.io/llms.txt

## Directory structure

A skill is a directory containing, at minimum, a `SKILL.md` file:

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
└── ...               # Any additional files or directories
```

## SKILL.md format

The `SKILL.md` file must contain YAML frontmatter followed by Markdown content.

### Frontmatter

| Field           | Required | Constraints                                                                                                       |
| --------------- | -------- | ----------------------------------------------------------------------------------------------------------------- |
| `name`          | Yes      | Max 64 characters. Lowercase letters, numbers, and hyphens only. Must not start or end with a hyphen.             |
| `description`   | Yes      | Max 1024 characters. Non-empty. Describes what the skill does and when to use it.                                 |
| `license`       | No       | License name or reference to a bundled license file.                                                              |
| `compatibility` | No       | Max 500 characters. Indicates environment requirements (intended product, system packages, network access, etc.). |
| `metadata`      | No       | Arbitrary key-value mapping for additional metadata.                                                              |
| `allowed-tools` | No       | Space-separated string of pre-approved tools the skill may use. (Experimental)                                    |

**Minimal example:**

```yaml
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

**Example with optional fields:**

```yaml
---
name: pdf-processing
description: Extract PDF text, fill forms, merge files. Use when handling PDFs.
license: Apache-2.0
metadata:
  author: example-org
  version: "1.0"
---
```

### `name` field

The required `name` field:

- Must be 1-64 characters
- May only contain unicode lowercase alphanumeric characters (`a-z`, `0-9`) and hyphens (`-`)
- Must not start or end with a hyphen (`-`)
- Must not contain consecutive hyphens (`--`)
- Must match the parent directory name

### `description` field

The required `description` field:

- Must be 1-1024 characters
- Should describe both what the skill does and when to use it
- Should include specific keywords that help agents identify relevant tasks

**Good example:**

```
description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.
```

**Poor example:**

```
description: Helps with PDFs.
```

### `description` 格式约束（V0 / W7 强约束）

除官方规范的 1-1024 字符上限外，本地校验增加：

| 约束                              | 强约束? | 来源                     | 违反后影响                         |
| --------------------------------- | ------- | ------------------------ | ---------------------------------- |
| 非空、字符串                       | ✅ 必   | 官方硬约束               | V0 硬 FAIL                         |
| 不含 XML 标签（本地实现为不含 `<` `>` 字符，更严） | ✅ 必 | 官方硬约束 + 本地加强 | V0 硬 FAIL                         |
| 字符数 ≤1024                       | ✅ 必   | 官方硬约束               | V0 硬 FAIL                         |
| YAML 单行 string（**禁用 `\|` 块**） | ✅ 必   | 本地扩展（外部技能管理软件转义风险） | V0 硬 FAIL / W7 标 T1              |
| Pushy/主动触发句式（`Use when…` / `Use this skill whenever…` / `Invoke on…` / 中文主动触发句式——含官方 `Use when` 句式） | ⚠️ 软建议（2026-09-11 目标驱动裁决：无事故背书的风格正则不作硬约束） | 社区原则（官方无 Pushy） | V0 warning；W7 T5 判语义质量（P2） |
| ≥1 个核心意图关键词（意图动词或显式触发词，嵌入句中；<2 附软建议——官方模糊反例均为 0 命中） | ✅ 必   | 本地扩展（对齐官方 "include specific keywords"） | V0 硬 FAIL / W7 标 T1              |
| 触发词 ≥3                         | ⚠️ 软建议 | 本地扩展（降级）         | V0 warning，不 FAIL                |
| 边界声明（"Not for: ..."）         | ⚠️ 推荐 | 社区原则（防误触发的镜像） | W7 标 T2（**缺**边界才 P1）；有边界不是反模式 |
| 功能句**始终第三人称**（避免 I can / You can） | ⚠️ 官方要求（语义，非机器判定） | 官方                 | W7 T5/T1 语义判定                  |
| 描述同时含功能 + 何时使用          | ⚠️ 官方要求（语义，非机器判定） | 官方                 | W7 T3 分维判定                     |

**长度软建议**：几句话到一个短段落（社区来源：agentskills.io "Optimizing skill descriptions"）。官方未给建议字数区间，**不设 200-400 之类自设区间**。

**来源分层声明（收敛原则）**：
- **官方** = platform.claude.com《Skill 编写最佳实践》（缓存：[claude-platform-best-practices.md](claude-platform-best-practices.md)）——硬约束与人称要求以此为准。
- **社区** = agentskills.io《Optimizing skill descriptions》（缓存：[optimizing-descriptions.md](optimizing-descriptions.md)）——评测协议与「宁可 pushy」出处；本仓既有文件的 `role: official-spec` 实为社区源，已随本次修正标注。
- **本地扩展** = 单行 string、意图词 ≥2、边界推荐——为本地工程约束，与官方/社区不冲突，保留。
- 冲突裁决：官方 > 社区 > 本地；已知冲突（社区「用祈使句」vs 官方「第三人称」）的功能句以官方为准，触发句 `Use when…` 两源兼容。

**核心触发词 vs 变体清单**：
- 合法：核心触发词**嵌入句中**（如 `Invoke on '验真'/'fact-check'`），3-4 个以内。
- 反模式：同义触发词变体罗列 >3 个（如 `review/audit/check/inspect/examine`）；把失败评测查询里的关键词逐条塞进 description（overfitting，禁）；裸词表无意图句承载。

**角色分层**：本节是机器判据唯一真源（`scripts/_impl/quick_validate.py::validate_description_format` 按此实现）；语义质量判定归 W7（T1-T5，P 级独立分维）。

**联锁参考**：[frontmatter-style-guide.md §9](frontmatter-style-guide.md#九、description-字段联锁规则（引用-specmd-真源）) 给出"反例 vs 正例"对照。

### `license` field

The optional `license` field:

- Specifies the license applied to the skill
- We recommend keeping it short (either the name of a license or the name of a bundled license file)

### `compatibility` field

The optional `compatibility` field:

- Must be 1-500 characters if provided
- Should only be included if your skill has specific environment requirements
- Can indicate intended product, required system packages, network access needs, etc.

Most skills do not need the `compatibility` field.

### `metadata` field

The optional `metadata` field:

- A map from string keys to string values
- Clients can use this to store additional properties not defined by the Agent Skills spec
- We recommend making your key names reasonably unique to avoid accidental conflicts

### `allowed-tools` field

The optional `allowed-tools` field:

- A space-separated string of tools that are pre-approved to run
- Experimental. Support for this field may vary between agent implementations

**Example:**

```
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

> **WARNING**: 之前的 spec-zh.md 翻译将此字段错记为 `array of strings`，本 spec.md 已修正为 `space-separated string`（空格分隔单字符串）。

### Body content

The Markdown body after the frontmatter contains the skill instructions. There are no format restrictions. Write whatever helps agents perform the task effectively.

Recommended sections:

- Step-by-step instructions
- Examples of inputs and outputs
- Common edge cases

Note that the agent will load this entire file once it's decided to activate a skill. Consider splitting longer `SKILL.md` content into referenced files.

## Optional directories

### `scripts/`

Contains executable code that agents can run. Scripts should:

- Be self-contained or clearly document dependencies
- Include helpful error messages
- Handle edge cases gracefully

Supported languages depend on the agent implementation. Common options include Python, Bash, and JavaScript.

### `references/`

Contains additional documentation that agents can read when needed:

- `REFERENCE.md` - Detailed technical reference
- `FORMS.md` - Form templates or structured data formats
- Domain-specific files (`finance.md`, `legal.md`, etc.)

Keep individual reference files focused. Agents load these on demand, so smaller files mean less use of context.

### `assets/`

Contains static resources:

- Templates (document templates, configuration templates)
- Images (diagrams, examples)
- Data files (lookup tables, schemas)

## Progressive disclosure

Agents load skills *progressively*, pulling in more detail only as a task calls for it. Skills should be structured to take advantage of this:

1. **Metadata** (~100 tokens): The `name` and `description` fields are loaded at startup for all skills
2. **Instructions** (< 5000 tokens recommended): The full `SKILL.md` body is loaded when the skill is activated
3. **Resources** (as needed): Files (e.g. those in `scripts/`, `references/`, or `assets/`) are loaded only when required

Keep your main `SKILL.md` under 500 lines. Move detailed reference material to separate files.

## File references

When referencing other files in your skill, use relative paths from the skill root:

```
See [the reference guide](references/REFERENCE.md) for details.
Run the extraction script: scripts/extract.py
```

Keep file references one level deep from `SKILL.md`. Avoid deeply nested reference chains.

## Validation

Use the [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) reference library to validate your skills:

```
skills-ref validate ./my-skill
```

This checks that your `SKILL.md` frontmatter is valid and follows all naming conventions.
