# skill-reviewer

Performs structured review and compliance validation on local Agent Skill repositories. This Skill itself follows the [Agent Skills Official Specification](https://agentskills.io/).

## Why Do You Need This Skill?

You wrote a Skill, and it runs—but can the Agent actually trigger it correctly? Can others maintain it?

Many Skills remain at the "a document + a few code snippets" stage, with common issues including:
- Main documents mixing rules, knowledge, and implementation, becoming increasingly chaotic
- Execution paths only exist in documentation, no real script entry point in the repository
- Non-standard frontmatter, Agent can't trigger it at all
- Scripts containing interactive prompts, Agent execution hangs immediately
- Time-sensitive baselines embedded in main documents, frequently outdated

skill-reviewer makes these issues explicit as **48 machine-verifiable checklist items**, producing structured review reports and remediation directions, not vague suggestions.

## Two Modes

| Mode | What It Does | Output |
|------|---------------|--------|
| **Review Mode** | Full analysis of Skill structure, triggering, implementation, and validation | 8-section review report (P0/P1/P2 grading + remediation directions) |
| **Compliance Validation Mode** | Quick check if frontmatter and directory structure comply with official specs | PASS / FAIL |

The two modes are mutually exclusive. If unsure which to use, simply say "帮我看看这个 skill", and a clarification process will run first.

## How to Use

**Review**: Tell the Agent you want to review a Skill, just provide the local directory path.
```
Review this skill: /path/to/my-skill/
Help me audit this skill's SKILL.md
```

**Validate**: Quick compliance check.
```
Validate if this skill is compliant: /path/to/my-skill/
```

**Self-Check Script** (no Agent needed, run directly):
```bash
# Compliance validation
python scripts/validate_review.py --spec /path/to/my-skill/

# Repository quick scan
python scripts/validate_review.py --checklist /path/to/my-skill/

# Terminology consistency check
python scripts/validate_review.py --consistency /path/to/my-skill/

# Combined execution
python scripts/validate_review.py --spec --checklist --consistency /path/to/my-skill/
```

## What Does a Review Report Look Like?

The review report contains 8 fixed sections:

1. **One-sentence Conclusion** — Stage judgment + strongest point + biggest weakness
2. **Complexity Assessment** — Light / Medium / Medium-complex / Complex
3. **Key Strengths** — Each item citing specific files as evidence
4. **Key Issues** — P0 (blocking) / P1 (maintenance risk) / P2 (evolution risk)
5. **Split Requirements Identified** — Which file responsibilities need decoupling
6. **Remediation Directions** — Prioritized, each item annotated with checklist numbers
7. **Structural Issue Summary** — Core issues in current structure + optimization directions
8. **Overall Assessment** — Product direction + engineering maturity rating

> Note: skill-reviewer is a **referee**—it only identifies issues, grades them, and produces reports. Actual modifications are executed by skill-creator; referees don't play the game.

## Runtime Requirements

- Python ≥ 3.10
- PyYAML (optional): Required when loading external rules in `--consistency` mode; automatically degrades to using only built-in rules when missing

## File Structure

```
skill-reviewer/
├── SKILL.md              # Main document (Agent execution entry)
├── README.md             # This file (human-oriented)
├── README.zh-CN.md       # Chinese version
├── VERSION.md            # Changelog
├── examples/
│   └── skill-reviewer-self-review.md   # Self-review example
├── workflows/            # Review workflow definitions
│   ├── W0-clarify.md     # Clarification prerequisite
│   ├── W1-complexity.md  # Complexity judgment
│   ├── W2-strengths.md   # Strengths scan
│   ├── W3-issues.md      # Issues scan
│   ├── W4-workflow-split.md  # Split requirements identification
│   ├── W5-recommendations.md # Remediation direction mapping
│   ├── W6-verdict.md     # Overall assessment
│   ├── W7-description-audit.md  # Description sub-audit
│   └── V0-validate.md    # Compliance validation
├── references/           # Judgment criteria and specifications (loaded on demand)
│   ├── config/           # External rule configuration
│   ├── rubrics/          # Checklists and rubrics
│   ├── specs/            # Official specifications and best practices
│   └── templates/        # Report templates and test set templates
├── scripts/
│   └── validate_review.py    # Self-validation script
└── tests/
    └── test_validate_review.py  # Unit tests
```

## Self-Compliance

- This Skill's own `SKILL.md` complies with official frontmatter specifications
- Main document < 500 lines, detailed specifications all下沉到 `references/`
- `scripts/validate_review.py` supports `--help`, exit codes (0=PASS/1=FAIL/2=parameter error), stdout/stderr separation
- Can self-review: `python scripts/validate_review.py --checklist .`
- Unit tests: `python -m unittest tests.test_validate_review -v`

## Division of Labor with SKILL.md

- This file: Human-oriented, explaining value, quick usage, runtime requirements
- SKILL.md: Agent execution-oriented, explaining triggering, mode scheduling, contracts, and validation
