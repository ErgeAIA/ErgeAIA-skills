[切换到中文](README.md)

# ErgeAIA-skills

A curated collection of production-grade Agent Skills following the official [Agent Skills Specification](https://agentskills.io/).

## Skills

| Skill | Description | Version |
|-------|-------------|---------|
| [skill-workshop](skill-workshop/) | Skill lifecycle workstation: create, review, refactor & evaluate Agent Skills (with the Google 5-mode baseline) | v1.25.0 |
| [changelog-manager](changelog-manager/) | Keep a Changelog-based changelog maintenance assistant | v2.1.0 |
| [zuiti](zuiti/) | Civil comeback generator ("mouth substitute"): crafts sharp, profanity-free retorts in 6 default styles (3 curated entries each), backed by verified quote/meme drawers and a manual-send gate | v0.3.9 |
| [vibe-buddy](vibe-buddy/) | Project AI collaboration memory: AGENTS.md contract, docs/.ai/ progress/decision/lesson archive, self-contained cross-session handoff, and distillation of reusable domain-scoped experience; also read-only audit of dev projects for code quality and stack; appends project CHANGELOG when the file already exists (vibe-init / vibe-sync / vibe-handoff / vibe-distill / vibe-audit) | v1.2.0 |
| [moxian](moxian/) | Surface the tacit knowledge you "thought you understood but never internalized": three layers of cognitive gaps (a term you glossed, an intention you can't articulate, a whole concept you didn't know you lacked), externalized into sharper questions and concept micro-lessons, and saved as a cumulative knowledge card under docs/moxian/ (moxian / "what did I miss") | v0.1.0 |

## Getting Started

### Install Skills

```bash
# Install all skills from this repository
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills

# Install specific skill (using --skill flag)
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill changelog-manager
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill skill-workshop
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill zuiti
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill vibe-buddy
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill moxian

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
