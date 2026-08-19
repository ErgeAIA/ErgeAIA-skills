---
version: 2026-06
purpose: Claude Skill 官方校验流程（reference for AI consumption; download-cached mirror of skills-ref validate source）
source: https://github.com/agentskills/agentskills/tree/main/skills-ref
audience: AI agents
role: official-spec
consumed-by: V0-validate / quick_validate.py
not-consumed-by: human-only-decisions
trigger-when: V0 校验流程 / quick_validate.py 执行
---

# Validate a Skill

> **重要**: 本文件为社区官方校验流程的本地缓存。如与官方源冲突，以官方源为准。

## Overview

The `skills-ref` validator checks that a Skill conforms to the Claude Skill specification. Run it before publishing a Skill to catch structural problems.

## Running the validator

```bash
skills-ref validate <path-to-skill>
```

The validator walks the Skill directory and reports errors and warnings for any issues it finds. Each issue includes a file path, line number, and a human-readable description.

## Validation steps

The validator performs the following checks in order:

### 1. Directory structure

- The Skill must be a directory.
- The directory must contain a `SKILL.md` file.

### 2. SKILL.md frontmatter

The validator parses the YAML frontmatter at the top of `SKILL.md` and checks each field.

#### 2.1 `name` field

- Must be present.
- Must be a string.
- Must be 1-64 characters.
- Must contain only lowercase letters, numbers, and hyphens.
- Must not start or end with a hyphen.
- Must not contain consecutive hyphens.
- Must match the parent directory name.

#### 2.2 `description` field

- Must be present.
- Must be a string.
- Must be 1-1024 characters.

#### 2.3 `license` field (optional)

- If present, must be a string.

#### 2.4 `compatibility` field (optional)

- If present, must be a string.
- Must be 1-500 characters in length.

#### 2.5 `metadata` field (optional)

- If present, must be a map from string keys to string values.
- Keys and values are not validated against any specific schema.

#### 2.6 `allowed-tools` field (optional, experimental)

- If present, must be a list of strings.
- Behavior is experimental and may change.

### 3. File references

The validator parses the body of `SKILL.md` and verifies that any relative-path links resolve to files inside the Skill directory. A reference is considered broken if:

- The target file does not exist
- The target path escapes the Skill directory
- The target path is a URL (external links are not validated)

### 4. Body content

The validator performs a basic sanity check on the body:

- Must be valid Markdown (no unclosed code blocks, unbalanced brackets, etc.)
- Should not be empty

## Reading the output

The validator reports issues in the following format:

```
<file>:<line>: <severity>: <message>
```

Severity levels:

- **error** — Must be fixed before the Skill is valid
- **warning** — Should be fixed; may indicate a problem

A Skill is considered valid when the validator reports no errors. Warnings do not block validity but should be reviewed.

## Failure recovery

If the validator reports errors, follow these steps:

### Frontmatter errors

- Verify the YAML syntax (e.g., proper quoting, no tabs).
- Confirm the field name is spelled correctly.
- Check that the value matches the expected type and length.

### File reference errors

- Confirm that the referenced file exists in the Skill directory.
- Verify the path is relative to `SKILL.md`.
- Check that the path uses forward slashes (even on Windows).

### Body content errors

- Look for unmatched code fences, brackets, or HTML tags.
- Ensure the file is not truncated.

## Continuous validation

Run the validator as part of your CI pipeline to prevent regressions. A typical pre-commit or pre-publish hook runs `skills-ref validate` on every changed Skill.
