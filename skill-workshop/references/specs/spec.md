---
version: 2026-06
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

| 约束                              | 强约束? | 违反后影响          |
| --------------------------------- | ------- | ------------------- |
| YAML 单行 string（**禁用 `\|` 块**） | ✅ 必   | W7 标 T1            |
| Pushy 句式（"Use this skill whenever..." / "Make sure to invoke it when..." / "Invoke on..."） | ✅ 必   | W7 标 T1            |
| 至少 3 个核心触发词（中文 / 英文） | ✅ 必   | W7 标 T1            |
| 推荐：边界声明（"Not for: ..."）   | ⚠️ 推荐 | W7 标 T1 推荐项    |

**联锁参考**：[frontmatter-style-guide.md §9](frontmatter-style-guide.md#九、description-字段联锁规则（w7-必读）) 给出"反例 vs 正例"对照。

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
