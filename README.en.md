# ErgeAIA-skills

A curated collection of production-grade Agent Skills following the official [Agent Skills Specification](https://agentskills.io/).

## Skills

| Skill | Description | Version |
|-------|-------------|---------|
| [skill-reviewer](skill-reviewer/) | Structured 9-dimension audit & compliance validation for Agent Skills | v4.6 |
| [changelog-manager](changelog-manager/) | Keep a Changelog-based changelog maintenance assistant | v1.1.0 |

## Getting Started

### Install Skills

```bash
# Install all skills from this repository
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills

# Or install a specific skill
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills/tree/main/skill-reviewer
```

## Specification Compliance

All skills in this repository comply with:

- ✅ `name` and `description` frontmatter fields
- ✅ Progressive disclosure (SKILL.md < 500 lines)
- ✅ No interactive prompts in scripts
- ✅ `--help` support for CLI tools
- ✅ Structured exit codes (0=PASS, 1=FAIL, 2=ERROR)
- ✅ Unit tests coverage

## Development

```bash
# Clone the repository
git clone https://github.com/ErgeAIA/ErgeAIA-skills.git
cd ErgeAIA-skills

# Run tests for skill-reviewer
cd skill-reviewer
uv run python -m unittest tests.test_validate_review -v
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Ensure tests pass
4. Submit a pull request

## Acknowledgments

This project references resources from [base44/skills](https://github.com/base44/skills). Specifically, the file `skill-reviewer/references/specs/spec-zh.md` is adapted from [spec.md](https://github.com/base44/skills/blob/ec420cf2edd2c7e9a523d5afe2e71498a6357fa4/.claude/skills/review-skills/references/spec.md). We sincerely appreciate the open-source contributions made by the original authors.

## Related

- [Agent Skills Specification](https://agentskills.io/)
- [ErgeAIA Organization](https://github.com/ErgeAIA)
