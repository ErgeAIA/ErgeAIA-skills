# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
_Last updated: 2026-09-25_

### Added

- **moxian skill added to repo**: tacit-knowledge gap externalization, v0.1.0 — surfaces three layers of "thought you understood but never internalized" cognitive gaps in AI-coding conversations (noun layer → word card / expression layer → sharper question / concept layer → micro-lesson), gate defaults to 1-2 cards, saved as a cumulative knowledge card under `docs/moxian/` (moxian / "what did I miss")

- **skill-workshop skill added to repo**: Skill lifecycle workstation (create/review/refactor/evaluate Agent Skills), v1.17.0, with 16 CLI subcommands and the 9-dimension 48-item review system
- **vibe-buddy skill added to repo** (2026-09-10): project AI collaboration memory skill v1.0.0 — collaboration contract in AGENTS.md, progress/decision/lesson archive under docs/.ai/, self-contained cross-session handoff, and experience distillation (vibe-init / vibe-sync / vibe-handoff / vibe-distill)

### Changed

- **vibe-buddy v1.0.0 → v1.5.0** (2026-09-13 ~ 09-25):
  - v1.1.0: added the fifth trigger `vibe-audit` — read-only review of development projects (code quality / architecture / tech stack), reports under `docs/.ai/audit/`; Skill projects are handed off to skill-workshop instead of self-review
  - v1.2.0: `vibe-sync` gained the "update log" capability — appends user-visible changes to an existing root `CHANGELOG.md` in its own format, never creates the file
  - v1.3.0: `References` switched to conditional pointers (generator syntax contract extended from four to five forms; the self-check gate rejects bare `见 <path>` pointers)
  - v1.4.0 / v1.4.1: description de-keyword-stuffed, human-only "references" section removed; `compatibility` de-duplicated against the body
  - v1.5.0 (breaking): **AGENTS.md becomes the single project-level collaboration contract source** — no longer creates / maintains / mirrors `CLAUDE.md`; adds the CLAUDE → AGENTS controlled migration (init state machine A–E, four-state disposal with audit trail, fact-based conflict adjudication, safety deletion gate, AGENTS single-source verification)
- **changelog-manager v2.0.1 → v2.1.2** (2026-09-24): 2.1.1 = re-review cleanup (bilingual section-title single source aligned, README structure completed, description de-stuffed); 2.1.2 = removed the YAML `compatibility` field (constraints merged into "runtime requirements"), W0–W5 detailed steps, failure-handling tables and sidecar fields sunk into `references/workflows.md`, SKILL.md 340 → 200 lines
- **skill-workshop v1.23.1 → v2.4.0** (2026-09-18 ~ 09-22):
  - v2.0.x: rebuilt as a lightweight quality workstation (52 → 4 references, SKILL.md tightened to 120–150 lines, four modes CREATE / AUDIT / OPTIMIZE / VALIDATE with separated duties, CLI converged to validate / package / init / spec, first self-tests)
  - v2.1.0: audit methodology integration (Core Task Definition anchor, five questions + six core problem classes merged into the existing flow)
  - v2.2.0: description validation fixes (removed the counter-incentive "too few trigger words" hint + hard symbol checks + dangling-spec cleanup)
  - v2.3.0: OPTIMIZE as an independent mode + description criteria moved from lexical scoring to semantic review (CLI judges structure only; added the 10-question Description semantic review and the four Trigger Quality dimensions)
  - v2.4.0: criteria graded by source — unsourced dangling HARD rules demoted to advisory; official contracts (string-typed metadata values) kept with defects handed back to the checked skills; degraded environments (no PyYAML) must be declared
- **moxian v0.1.0 → v0.2.0** (2026-09-25): frontmatter cleanup (removed the non-standard `compatibility` field, keeping only `metadata`); Non-Goals now documents the `@session` host-capability dependency; removed the redundant `assets/banner.json`

- **skill-reviewer version normalized to three segments**: `4.6` → `4.6.0`
- **changelog-manager safety enhancements**
  - Added anti-pattern blacklist section with 10 anti-patterns and danger actions subsection
  - Added CHECKPOINT/STOP visual markers at key decision points in W0/W1/W2 workflows
  - Added failure handling fallback tables to W0/W1/W2 workflows
- **changelog-manager v2.0.0 → v2.0.1** (2026-09-12): added `trigger-when` load hints to all 6 `references/` files, aligning with the three-layer content rule
- **skill-workshop v1.17.0 → v1.23.1 evolution** (2026-08-20 ~ 09-12):
  - v1.18.x: three-stage review meta-framework injection, darwin field-test fixes (review scope unified to 10 dimensions / 52 items), 7 defect fixes from full-script audit, V0 semantic markup builder/runtime classification
  - v1.19.0: merged skill-review-process v6.5-v6.8 (0.6 iron rules / C5 cross-check / 5.7 graded gates / 0.5 state machine)
  - v1.20.0: dogfooding self-review fixes (checklist FAIL→PASS, routing-check truth-source three-way comparison, version-scope convergence)
  - v1.21.x: first-principles self-assessment overhaul (Google 5-pattern baseline), version single-sourcing, Chinese Pushy-pattern support in validators
  - v1.22.0: description criteria alignment (6 self-contradictions removed + validator three-state grading + official source cache)
  - v1.23.0: script flexibility Phase 1 (plan-gate / checkpoint / profile / dry-run defaults); version-header regex fix (annotated VERSION.md headers no longer false-positive)
  - v1.23.1: routing-check workflow-list directory gating — no longer false-positives on flat `references/` layouts
- **zuiti v0.2.4 → v0.3.9** (2026-08-31 ~ 09-12): verified quote/meme drawer expansion and six-style system, P0-P2 de-stiffening series (guided prompts replace fill-in templates), validate_skill.py single-pass speedup, pure-Chinese imperative description, validate_skill.py `--offset`/`--output` truncation support

### Deprecated

- **skill-reviewer marked as deprecated**: fully superseded by skill-workshop (whose review chain merged all its capabilities: 9-dimension 48-item review, W0-W7+V0 workflows, compliance validation); no longer recommended for triggering, directory kept for archival; root README skill list and skill-reviewer's SKILL.md / README synced
- **skill-reviewer removed from the release pipeline**: `.github/workflows/release.yml` no longer packages / releases skill-reviewer (deleted from trigger paths, packaging step, Release body table and attachment list); only changelog-manager remains on the release path

### Removed

- **skill-reviewer skill physically deleted** (2026-09-10): the earlier Deprecated item landed — capabilities fully merged into skill-workshop; root README / project-overview / decision log cleaned up in sync
- **GitHub Actions release pipeline retired** (2026-09-12): `.github/workflows/release.yml` deleted. The repo is a pure skill collection distributed via `npx skills add` reading the repo directly; `CHANGELOG.md` / `CHANGELOG.en.md` demoted to purely human documents, no longer tied to any automation

## [1.1.1] - 2026-05-30

### Changed

- **GitHub Actions workflow fixes**
  - Fix packaging: use `zip -r` to preserve directory structure (skill directory as zip root)
  - Fix version check logic: skip instead of error when version not bumped
  - Fix step id reference issue
  - Remove artifact upload step (attached directly in release)

## [1.1.0] - 2026-05-30

### changelog-manager v2.0.0

- **Bilingual support upgrade**
  - Built-in bilingual support, maintaining both Chinese CHANGELOG.md and English CHANGELOG.en.md
  - Added `+lang` shortcut to switch primary language mode (`+lang zh` / `+lang en`)
  - Added bilingual-guide.md reference document (60+ term glossary)
  - Added V4 bilingual document consistency validation
  - All workflows (W0-W5) updated to operate on both files simultaneously
  - README.md and output-template.md synchronized

## [1.0.0] - 2026-05-29

### Added

- **skill-reviewer v4.6** - 9-dimension 48-item structured audit & compliance validation for Agent Skills
  - Added guidance for autonomy level declaration (§5), clarifying constraint strength across three modes
  - Added evaluation-driven iteration discipline (V4.1), standardizing regression workflow after description changes
  - Adjusted section numbering for structural consistency

- **changelog-manager v1.1.0** - Keep a Changelog-based changelog maintenance assistant
  - Support for generating changes from git commit history
  - Support for manual entry appending and version release archival
  - Built-in format validation

### Changed

- Set Chinese README as the default version, English version renamed to README.en.md
- Synchronized README updates across project root and skill-reviewer
- skill-reviewer version updated to v4.6

### Docs

- Added README.md (Chinese) and README.en.md (English)
- Added acknowledgment for base44/skills project
- Formatted review checklist tables and added extended field guidelines

### Deprecated

- README.zh-CN.md has been merged into README.md (Chinese as default)
