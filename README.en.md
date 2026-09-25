[切换到中文](README.md)

# ErgeAIA-skills

A curated collection of production-grade Agent Skills following the official [Agent Skills Specification](https://agentskills.io/).

## Skills

| Skill | Description | Usage example | Version |
|-------|-------------|---------------|---------|
| [skill-workshop](skill-workshop/) | Full-lifecycle workbench for Agent Skills: create, review, optimize, refactor, validate, package (four modes with separated duties; Fast/Deep/Eval ≡ L0/L1/L2; Optimize reads all runtime assets, actually rewrites and regression-checks; the CLI only checks structure and grades each rule by its source — unsourced blockers were demoted to advisory) | `Optimize this skill and give me Before/After` | v2.4.0 |
| [changelog-manager](changelog-manager/) | Keep a Changelog-based changelog maintenance assistant | `+add Added user login` | v2.1.0 |
| [zuiti](zuiti/) | Civil comeback generator: sharp, profanity-free retorts in 6 styles, verified quotes, human-send gate | `zuiti: reply to this comment for me` | v0.3.9 |
| [vibe-buddy](vibe-buddy/) | Project AI collaboration memory: AGENTS.md as the single contract (incl. CLAUDE.md migration), docs/.ai/, handoff, distill, read-only audit | `vibe-init` | v1.5.0 |
| [moxian](moxian/) | Surface tacit cognitive gaps from AI-coding chats; save cards to docs/moxian/ | `moxian: show what I did not really get` | v0.1.0 |

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
