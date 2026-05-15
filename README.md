# ErgeAIA-skills

A curated collection of production-grade Agent Skills following the official [Agent Skills Specification](https://agentskills.io/).

## Skills

| Skill | Description | Version |
|-------|-------------|---------|
| [skill-reviewer](skill-reviewer/) | Structured 9-dimension audit & compliance validation for Agent Skills | v4.5 |

## Getting Started

### Install Skills

```bash
# Install all skills from this repository
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills

# Or install a specific skill
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills/tree/main/skill-reviewer
```

### Use skill-reviewer

```bash
# Review a skill directory
npx skill-reviewer /path/to/your-skill

# Check compliance only
npx skill-reviewer --spec /path/to/your-skill

# Full audit with checklist and consistency checks
npx skill-reviewer --spec --checklist --consistency /path/to/your-skill
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

## Related

- [Agent Skills Specification](https://agentskills.io/)
- [ErgeAIA Organization](https://github.com/ErgeAIA)
