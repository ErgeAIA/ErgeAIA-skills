# vibe-buddy Changelog

> [中文版](CHANGELOG.md) · Records user-visible changes only. Design rationale lives in the README; generation rules live in `references/`.

---

## [Unreleased]

### Fixed

- Archive paths are no longer hard-coded to `docs/agents/`: the target project's `AGENTS.md` decides (`docs/agents/` or `docs/.ai/`); archives go under `archive/` in the same root.
- Routing and hard rules now expose an explicit "archive / shard" entry: archive before writing past a threshold and report counts in the final reply — previously archiving was hidden inside the sync contract.

## v1.12.0 (2026-11-27)

### Added

- Ninth trigger `vibe-req`: EARS requirement clarification. Its core is the "four elevation questions" — what a top professional would do that you did not ask, the rawest material, the concrete methods and tools, and what besides you or the model would prove the result right. Deeper, not bigger. EARS' five sentence patterns are only the output form; empty categories are omitted.
- `vibe-audit` gained changeset mode and `mode=security`; `vibe-check` (read-only archive checkup); `vibe-release` (release governance contract).

### Changed

- All workflows now share `references/workflow-protocol.md`; `SKILL.md` shrank from 196 to 184 lines.
- Archive boundaries for process documents (300 lines progress, 200 decisions, etc.): archive before writing past the limit; numbering stays unique across active and archived entries.
- Git allowlist expanded to per-file forensics; bare `diff`, `log -p`, and `show` are forbidden; limits are 30 files / 400 lines / 80 KB.

### Fixed

- Templates no longer reference skill-internal paths (target projects do not have those files); the security checklist now states "no stack critique".

---

## v1.11.0 (2026-11-27)

### Added

- `references/workflow-protocol.md`: shared workflow protocol (trigger order, fact sources, write ownership, reason codes, archive thresholds, three task tiers); six references point to it.
- `references/audit-checklist.md` (10 code smells + 12 security checks), `references/release-checklist.md` (six release gates), `references/check-artifacts.md` (10 read-only checkup items).
- Seventh trigger `vibe-check`; eighth `vibe-release`; `vibe-audit` gained changeset mode and `mode=security`.
- Archive boundaries for eight process artifacts; numbering stays unique across archives.
- `vibe-sync` execution ledger (`produced` / `skipped` / `level` machine-readable line).

### Changed

- `SKILL.md` 196 → 185 lines; redaction, five-state disposition, and reason codes each consolidated to one source; `project-overview.md` upgraded to an architecture baseline with four sections.
- Git allowlist expanded to per-file forensics; bare `diff` / `log -p` / `show` forbidden.

### Fixed

- Templates no longer reference skill-internal paths; corrected a section reference in `check-artifacts.md`; unified trigger counts in the README.

---

## v1.10.0 (2026-11-16)

### Changed

- `description` reduced to two parts (job + use-when); triggers corrected against the self-test set; boundaries moved to Non-Goals.

---

## v1.9.0 (2026-11-15)

### Added

- `vibe-wrap` (finish): after one self-review, run sync → distill → handoff in sequence; skipped artifacts carry reason codes.
- Distillation deduplication moved to `experience/.distill-index.json` (by commit SHA); `changelog.md` became a one-line-per-round human ledger.

### Changed

- Semantic checks (noise rules N1–N6, measured line counts) downgraded from gates to review hints.
- Environment handling deduplicated: empty Git output and zero-commit states are now explained only in `command-policy.md`.

---

## v1.8.0 (2026-10-10)

### Added

- Initialization gained repository hygiene checks: detect `.gitignore` / `CHANGELOG.md` / `README.md`, delegate to git-manager / changelog-manager / shuxu by ownership, then verify.

---

## v1.7.0 (2026-10-06)

### Changed

- Initialization state machine A–E refined; half-initialized projects only get missing documents, never a rewrite.

---

## v1.6.1 (2026-09-27)

### Fixed

- "Latest handoff" rule for multiple files on the same date: parse the date from the filename, then compare frontmatter `updated`.

---

## v1.6.0 (2026-09-27)

### Added

- `vibe-init`: creates `AGENTS.md` and the full `docs/agents/` set, including controlled CLAUDE → AGENTS migration with a safe-delete gate.
- `vibe-audit`: read-only review of development projects (code quality / architecture / stack), every finding bound to `path:line`; Skill projects go to skill-workshop.
- `vibe-handoff`: self-contained handoff documents covering only the four kinds of information not available elsewhere.
- `vibe-distill`: extracts reusable experience by domain (five required elements, three levels).

### Changed

- "Take over" is no longer a trigger: reading project archives and restating status is an `AGENTS.md` obligation, not a skill entry point.
- Terminal commands moved to an allowlist: no commands by default; only Git detection / init and codegraph detection / index creation.

---

## v1.5.1 (2026-09-26)

### Fixed

- Decision and bug numbering: read the maximum number and add one, zero-padded to three digits.

---

## v1.5.0 (2026-09-25)

### Added

- `vibe-sync`: writes progress, decisions, and debugging records; fills the `AGENTS.md` fact tables when needed.
- Objective fact sources for process documents: read-only Git > latest handoff > existing process documents > session context; conflicts resolve to the objective source.

---

## v1.4.1 (2026-09-24)

### Fixed

- Resolved the contradiction between contract and fact areas: the `AGENTS.md` contract area is written only by init; the fact area is filled by sync.

---

## v1.4.0 (2026-09-24)

### Added

- `references/command-policy.md`: single source of truth for the terminal allowlist, with allowed subsets per trigger.

---

## v1.3.0 (2026-09-24)

### Added

- YAML frontmatter for all process documents (`title` / `type` / `project` / `updated` / `description`), with `updated` synced on every edit.
- `docs/agents/init-report.md`: append-only initialization report.

### Changed

- Templates externalized to `assets/docs/` to eliminate drift between templates and specifications.

---

## v1.2.0 (2026-09-13)

### Added

- `vibe-init` Git check (read-only detection, init if absent) and codegraph integration (index only when installed and missing).

---

## v1.1.0 (2026-09-13)

### Added

- Experience tiers in `vibe-distill` (🔴 red line / 🟡 preference / 🟢 parameter) and dual ledgers (`changelog.md` + `.distill-index.json`).

---

## v1.0.0 (2026-09-10)

### Added

- First release: `vibe-init` + `vibe-sync`, establishing `AGENTS.md` as the single contract source and `docs/agents/` as the process archive area.
