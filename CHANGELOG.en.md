# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
_Last updated: 2026-08-19_

### Added

- **skill-workshop skill added to repo**: Skill lifecycle workstation (create/review/refactor/evaluate Agent Skills), v1.17.0, with 16 CLI subcommands and the 9-dimension 48-item review system

### Changed

- **skill-reviewer version normalized to three segments**: `4.6` → `4.6.0`
- **changelog-manager safety enhancements**
  - Added anti-pattern blacklist section with 10 anti-patterns and danger actions subsection
  - Added CHECKPOINT/STOP visual markers at key decision points in W0/W1/W2 workflows
  - Added failure handling fallback tables to W0/W1/W2 workflows

### Deprecated

- **skill-reviewer marked as deprecated**: fully superseded by skill-workshop (whose review chain merged all its capabilities: 9-dimension 48-item review, W0-W7+V0 workflows, compliance validation); no longer recommended for triggering, directory kept for archival; root README skill list and skill-reviewer's SKILL.md / README synced
- **skill-reviewer removed from the release pipeline**: `.github/workflows/release.yml` no longer packages / releases skill-reviewer (deleted from trigger paths, packaging step, Release body table and attachment list); only changelog-manager remains on the release path

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
