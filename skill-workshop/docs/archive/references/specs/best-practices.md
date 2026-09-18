---
version: 2026-06
purpose: Claude Skill 最佳实践（reference for AI consumption; download-cached mirror of https://agentskills.io/skill-creation/best-practices — VERIFIED 2026-06-18）
source: https://agentskills.io/skill-creation/best-practices
audience: AI agents
role: official-spec
consumed-by: W3 / W7 / review-checklist / all workflow files
not-consumed-by: human-only-decisions
trigger-when: W3 问题扫描 / W7 description 审计 / C-series 创建重构
last-fetched: 2026-06-18
last-verified: 2026-06-18 (VERIFIED — 全文来自真实官方源)
---

# Best practices for skill creators

> **真实来源**: https://agentskills.io/skill-creation/best-practices
> **本文件**: 2026-06-18 拉取的真实内容缓存（v1.6 整改重写）

How to write skills that are well-scoped and calibrated to the task.

## Start from real expertise

A common pitfall in skill creation is asking an LLM to generate a skill without providing domain-specific context — relying solely on the LLM's general training knowledge. The result is vague, generic procedures ("handle errors appropriately," "follow best practices for authentication") rather than the specific API patterns, edge cases, and project conventions that make a skill valuable.

Effective skills are grounded in real expertise. The key is feeding domain-specific context into the creation process.

### Extract from a hands-on task

Complete a real task in conversation with an agent, providing context, corrections, and preferences along the way. Then extract the reusable pattern into a skill. Pay attention to:

- **Steps that worked** — the sequence of actions that led to success
- **Corrections you made** — places where you steered the agent's approach (e.g., "use library X instead of Y," "check for edge case Z")
- **Input/output formats** — what the data looked like going in and coming out
- **Context you provided** — project-specific facts, conventions, or constraints the agent didn't already know

### Synthesize from existing project artifacts

When you have a body of existing knowledge, you can feed it into an LLM and ask it to synthesize a skill. A data-pipeline skill synthesized from your team's actual incident reports and runbooks will outperform one synthesized from a generic "data engineering best practices" article, because it captures *your* schemas, failure modes, and recovery procedures.

The key is project-specific material, not generic references. Good source material includes:

- Internal documentation, runbooks, and style guides
- API specifications, schemas, and configuration files
- Code review comments and issue trackers (captures recurring concerns and reviewer expectations)
- Version control history, especially patches and fixes (reveals patterns through what actually changed)
- Real-world failure cases and their resolutions

## Refine with real execution

The first draft of a skill usually needs refinement. Run the skill against real tasks, then feed the results — all of them, not just failures — back into the creation process. Ask: what triggered false positives? What was missed? What could be cut?

Even a single pass of execute-then-revise noticeably improves quality, and complex domains often benefit from several.

Read agent execution traces, not just final outputs. If the agent wastes time on unproductive steps, common causes include instructions that are too vague (the agent tries several approaches before finding one that works), instructions that don't apply to the current task (the agent follows them anyway), or too many options presented without a clear default.

For a more structured approach to iteration, including test cases, assertions, and grading, see [Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills).

## Spending context wisely

Once a skill activates, its full `SKILL.md` body loads into the agent's context window alongside conversation history, system context, and other active skills. Every token in your skill competes for the agent's attention with everything else in that window.

### Add what the agent lacks, omit what it knows

Focus on what the agent *wouldn't* know without your skill: project-specific conventions, domain-specific procedures, non-obvious edge cases, and the particular tools or APIs to use. You don't need to explain what a PDF is, how HTTP works, or what a database migration does.

Ask yourself about each piece of content: "Would the agent get this wrong without this instruction?" If the answer is no, cut it. If you're unsure, test it. And if the agent already handles the entire task well without the skill, the skill may not be adding value. See [Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills) for how to test this systematically.

### Design coherent units

Deciding what a skill should cover is like deciding what a function should do: you want it to encapsulate a coherent unit of work that composes well with other skills. Skills scoped too narrowly force multiple skills to load for a single task, risking overhead and conflicting instructions. Skills scoped too broadly become hard to activate precisely. A skill for querying a database and formatting the results may be one coherent unit, while a skill that also covers database administration is probably trying to do too much.

### Aim for moderate detail

Overly comprehensive skills can hurt more than they help — the agent struggles to extract what's relevant and may pursue unproductive paths triggered by instructions that don't apply to the current task. Concise, stepwise guidance with a working example tends to outperform exhaustive documentation. When you find yourself covering every edge case, consider whether most are better handled by the agent's own judgment.

### Structure large skills with progressive disclosure

The [specification](https://agentskills.io/specification#progressive-disclosure) recommends keeping `SKILL.md` under 500 lines and 5,000 tokens — just the core instructions the agent needs on every run. When a skill legitimately needs more content, move detailed reference material to separate files in `references/` or similar directories.

The key is telling the agent *when* to load each file. "Read `references/api-errors.md` if the API returns a non-200 status code" is more useful than a generic "see references/ for details." This lets the agent load context on demand rather than up front, which is how [progressive disclosure](https://agentskills.io/specification#progressive-disclosure) is designed to work.

## Calibrating control

Not every part of a skill needs the same level of prescriptiveness. Match the specificity of your instructions to the fragility of the task.

### Match specificity to fragility

**Give the agent freedom** when multiple approaches are valid and the task tolerates variation. For flexible instructions, explaining *why* can be more effective than rigid directives — an agent that understands the purpose behind an instruction makes better context-dependent decisions. A code review skill can describe what to look for without prescribing exact steps.

**Be prescriptive** when operations are fragile, consistency matters, or a specific sequence must be followed:

```
## Database migration
Run exactly this sequence:
python scripts/migrate.py --verify --backup
Do not modify the command or add additional flags.
```

Most skills have a mix. Calibrate each part independently.

### Provide defaults, not menus

When multiple tools or approaches could work, pick a default and mention alternatives briefly rather than presenting them as equal options.

### Favor procedures over declarations

A skill should teach the agent *how to approach* a class of problems, not *what to produce* for a specific instance.

This doesn't mean skills can't include specific details — output format templates (see [Templates for output format](#templates-for-output-format)), constraints like "never output PII," and tool-specific instructions are all valuable. The point is that the *approach* should generalize even when individual details are specific.

## Patterns for effective instructions

These are reusable techniques for structuring skill content. Not every skill needs all of them — use the ones that fit your task.

### Gotchas sections

The highest-value content in many skills is a list of gotchas — environment-specific facts that defy reasonable assumptions. These aren't general advice ("handle errors appropriately") but concrete corrections to mistakes the agent will make without being told otherwise.

Keep gotchas in `SKILL.md` where the agent reads them before encountering the situation. A separate reference file works if you tell the agent when to load it, but for non-obvious issues, the agent may not recognize the trigger.

When an agent makes a mistake you have to correct, add the correction to the gotchas section. This is one of the most direct ways to improve a skill iteratively (see [Refine with real execution](#refine-with-real-execution)).

### Templates for output format

When you need the agent to produce output in a specific format, provide a template. This is more reliable than describing the format in prose, because agents pattern-match well against concrete structures. Short templates can live inline in `SKILL.md`; for longer templates, or templates only needed in certain cases, store them in `assets/` and reference them from `SKILL.md` so they only load when needed.

### Checklists for multi-step workflows

An explicit checklist helps the agent track progress and avoid skipping steps, especially when steps have dependencies or validation gates.

### Validation loops

Instruct the agent to validate its own work before moving on. The pattern is: do the work, run a validator (a script, a reference checklist, or a self-check), fix any issues, and repeat until validation passes.

A reference document can also serve as the "validator" — instruct the agent to check its work against the reference before finalizing.

### Plan-validate-execute

For batch or destructive operations, have the agent create an intermediate plan in a structured format, validate it against a source of truth, and only then execute.

The key ingredient is the validation step: a validation script that checks the plan against the source of truth. Errors like "Field 'signature_date' not found — available fields: customer_name, order_total" give the agent enough information to self-correct.

### Bundling reusable scripts

When iterating on a skill, compare the agent's execution traces across test cases. If you notice the agent independently reinventing the same logic each run — building charts, parsing a specific format, validating output — that's a signal to write a tested script once and bundle it in `scripts/`.

For more on designing and bundling scripts, see [Using scripts in skills](https://agentskills.io/skill-creation/using-scripts).

## Next steps

Once you have a working skill, two guides can help you refine it further:

- [**Evaluating skill output quality**](https://agentskills.io/skill-creation/evaluating-skills) — Set up test cases, grade results, and iterate systematically.
- [**Optimizing skill descriptions**](https://agentskills.io/skill-creation/optimizing-descriptions) — Test and improve your skill's `description` field so it triggers on the right prompts.
