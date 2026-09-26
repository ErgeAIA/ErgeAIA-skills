[切换到中文](README.md)

# ErgeAIA-skills

A collection of production-grade Agent Skills following the official [Agent Skills Specification](https://agentskills.io/) — each skill is battle-tested in real workflows and ready to install.

## Skills

| Skill | One-liner | Usage example | Version |
|-------|-----------|---------------|---------|
| [skill-workshop](skill-workshop/) | Full-lifecycle workbench for Agent Skills: create, review, optimize, refactor, validate, package | `Optimize this skill and give me Before/After` | v2.5.0 |
| [vibe-buddy](vibe-buddy/) | Project AI collaboration memory and read-only audit: AGENTS.md contract, progress / handoff / distill, code & architecture review | `vibe-init` | v1.5.1 |
| [git-manager](git-manager/) | Git workflow safety rail: branches, commits, merges by convention; dangerous ops require explicit confirmation | `commit these changes as a conventional commit` | v1.3.3 |
| [changelog-manager](changelog-manager/) | Keep a Changelog maintenance, generate from git commits, bilingual support | `+add Added user login` | v2.1.3 |
| [moxian](moxian/) | Surface the gaps you thought you understood but never internalized — save them as sticky cognition cards | `moxian: show what I did not really get` | v0.2.1 |
| [zuiti](zuiti/) | Civil comeback generator: sharp, profanity-free retorts — 6 styles, 3 each | `zuiti: reply to this comment for me` | v0.3.10 |

## Getting Started

### Install Skills

```bash
# Install all skills from this repository
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills

# Install specific skill (using --skill flag)
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill skill-workshop
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill vibe-buddy
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill git-manager
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill changelog-manager
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill moxian
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill zuiti

# List available skills in the repository
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --list
```

## Author

<table>
<tr>
<td align="center" valign="middle" width="220">
<img src="https://github.com/ErgeAIA.png" width="100" style="border-radius: 50%"><br>
<b>ErgeAIA / 宝藏二哥AIA</b><br>
<sub>Keep tinkering, never stop</sub>
</td>
<td valign="middle" style="padding-left: 18px;">

**About me**: Indie developer / full-stack engineer / ComfyUI enthusiast / Vibe Coding practitioner<br>
**Stack**: Tauri · Rust · React · Python · Claude · ZCode · Workbuddy<br>
**Philosophy**: Sharing without barriers — no gatekeeping, no tricks, no holding back

**Links**:
📺 [Bilibili](https://space.bilibili.com/67221461) · [Zhihu](https://www.zhihu.com/people/meli55a/posts) · WeChat Official Account (ErgeAIA)<br>
🐙 [GitHub](https://github.com/ErgeAIA) · [Gitee](https://gitee.com/ErgeAIA)<br>
📦 Featured projects: [ErgeMD](https://github.com/ErgeAIA/ErgeMD) · [ErgeHash](https://github.com/ErgeAIA/ErgeHash) · [catapult-cn](https://github.com/ErgeAIA/catapult-cn)

</td>
</tr>
</table>

---

<div align="center">

If ErgeAIA-skills helped you, a Star would be much appreciated!

</div>

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

This project's skill-review methodology was originally inspired by [base44/skills](https://github.com/base44/skills) (`spec.md`), which has since been consolidated into `skill-workshop`. We sincerely appreciate the open-source contributions of the original authors.

## Related

- [Agent Skills Specification](https://agentskills.io/)
- [ErgeAIA Organization](https://github.com/ErgeAIA)
