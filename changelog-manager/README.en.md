# changelog-manager

A project changelog maintenance assistant that helps developers record and manage notable changes for each version in a standardized way.

## Features

- Based on [Keep a Changelog](https://keepachangelog.com/1.0.0/) specification
- Semantic Versioning (SemVer) support
- Auto-generate changelog from git commit history
- Manual entry addition + version release archival
- Standard compliance checking

## Quick Start

### Initialize

```
+init my-project
```

Generate a standard CHANGELOG.md.

### Daily Recording

```
+add added user login feature
+add fixed slow homepage loading
```

Automatically classified and written to `[Unreleased]` section.

### Release Version

```
+release 1.0.0
```

Archive `[Unreleased]` to new version, auto-fill date and links.

### Generate from Git

```
+generate
```

Extract commits since last tag, filter noise, organize by category, preview and confirm before writing.

### Check Compliance

```
+check
```

Check format, dates, categories, links, and output improvement suggestions.

## Workflow

```
Daily Dev → +add to [Unreleased] → +release at publish → repeat
```

## Change Categories

| Category | Purpose | Example |
|----------|---------|---------|
| Added | New features | GitHub OAuth login support |
| Changed | Feature changes | Upgraded React 17 → 18 |
| Deprecated | Soon to be removed | `legacyLogin()` removed in next version |
| Removed | Already removed | Removed v1.x API |
| Fixed | Bug fixes | Fixed Safari layout issues |
| Security | Security improvements | Fixed XSS vulnerability |

## Use Cases

- Individual developers maintaining multiple projects
- Open source projects writing release notes
- Small teams without a dedicated release manager
- Anyone who says "I'll write the changelog next time" and never does

## Project Structure

```
changelog-manager/
├── SKILL.md                      # Skill definition
├── examples/
│   └── basic-usage.md           # Basic usage examples
└── references/
    ├── classification-guide.md  # Detailed classification guide
    ├── git-extraction-rules.md   # Git commit extraction rules
    ├── output-template.md        # Output templates
    ├── template-examples.md      # CHANGELOG template examples
    └── trigger-test-set.md       # Trigger test set
```

## Related Specifications

- [Keep a Changelog](https://keepachangelog.com/1.0.0/)
- [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
- [Conventional Commits](https://www.conventionalcommits.org/)

## License

MIT
