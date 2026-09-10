# ErgeAIA-skills

A curated collection of production-grade Agent Skills following the official [Agent Skills Specification](https://agentskills.io/).

## Skills

| Skill | Description | Version |
|-------|-------------|---------|
| [skill-workshop](skill-workshop/) | Skill lifecycle workstation: create, review, refactor & evaluate Agent Skills | v1.21.0 |
| [changelog-manager](changelog-manager/) | Keep a Changelog-based changelog maintenance assistant | v2.0.0 |
| [vibe-buddy](vibe-buddy/) | Project AI collaboration memory: AGENTS.md contract, docs/.ai/ progress/decision/lesson archive, self-contained cross-session handoff, and distillation of reusable domain-scoped experience (vibe-init / vibe-sync / vibe-handoff / vibe-distill) | v1.0.0 |

## Getting Started

### Install Skills

```bash
# Install all skills from this repository
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills

# Install specific skill (using --skill flag)
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill changelog-manager
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill skill-workshop

# List available skills in the repository
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --list
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
