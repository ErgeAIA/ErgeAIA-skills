[Switch to English](README.en.md)

# ErgeAIA-skills

遵循 [Agent Skills 官方规范](https://agentskills.io/) 的生产级 Agent Skill 合集——每个技能都经过真实工作流打磨，可直接安装使用。

## 技能列表

| 技能 | 一句话 | 使用示例 | 版本 |
|------|------|----------|------|
| [skill-workshop](skill-workshop/) | Agent Skill 全生命周期工作台：创建、评审、优化、重构、校验、打包 | `优化这个 skill：改完给我 Before/After` | v2.5.0 |
| [vibe-buddy](vibe-buddy/) | AI 编程全过程的项目侧协作管理：AGENTS.md 契约、进度 / 交接 / 经验、开发类项目只读审查 | `vibe-init` | v1.6.1 |
| [git-manager](git-manager/) | Git 工作流安全护栏：分支、提交、合并按规范走，危险操作强制二次确认 | `帮我把这些修改提交成一个规范的 commit` | v1.3.3 |
| [changelog-manager](changelog-manager/) | 按 Keep a Changelog 规范维护更新日志，可从 git 提交生成、支持双语 | `+add 新增了用户登录功能` | v2.1.3 |
| [moxian](moxian/) | 照出「以为懂、其实没内化」的认知缺口，落一份可沉淀的认知卡 | `默现：照一下我没懂的` | v0.2.1 |
| [zuiti](zuiti/) | 嘴替：生成不带脏字、句句有杀气的体面回击，六种风格各 3 条 | `嘴替：帮我回这句「你这水平还敢开源？」` | v0.3.10 |

## 快速开始

### 安装技能

```bash
# 安装本仓库中的所有技能
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills

# 安装指定技能（使用 --skill 参数）
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill skill-workshop
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill vibe-buddy
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill git-manager
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill changelog-manager
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill moxian
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill zuiti

# 列出仓库中可安装的技能
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --list
```

## 作者信息

<table>
<tr>
<td align="center" valign="middle" width="220">
<img src="https://github.com/ErgeAIA.png" width="100" style="border-radius: 50%"><br>
<b>宝藏二哥AIA / ErgeAIA</b><br>
<sub>生命不息，折腾不止</sub>
</td>
<td valign="middle" style="padding-left: 18px;">

**关于我**：独立开发者 / 全栈工程师 / ComfyUI 爱好者 / Vibe Coding 实践者<br>
**技术栈**：Tauri · Rust · React · Python · Claude · ZCode · Workbuddy<br>
**理念**：三无分享 — 无门槛、无套路、无保留

**链接**：
📺 [B 站](https://space.bilibili.com/67221461) · [知乎](https://www.zhihu.com/people/meli55a/posts) · 微信公众号(ErgeAIA)<br>
🐙 [GitHub](https://github.com/ErgeAIA) · [Gitee](https://gitee.com/ErgeAIA)<br>
📦 精选项目：[ErgeMD](https://github.com/ErgeAIA/ErgeMD) · [ErgeHash](https://github.com/ErgeAIA/ErgeHash) · [catapult-cn](https://github.com/ErgeAIA/catapult-cn)

</td>
</tr>
</table>

---

<div align="center">

如果 ErgeAIA-skills 帮到了你，欢迎点个 Star 鼓励一下！

</div>

## 许可证

MIT License — 详见 [LICENSE](LICENSE)。

## 致谢

本项目的技能评审方法论最初受 [base44/skills](https://github.com/base44/skills) 的 `spec.md` 启发，相关规范已整合进 `skill-workshop`。感谢原作者的开源贡献。

## 相关链接

- [Agent Skills 官方规范](https://agentskills.io/)
- [ErgeAIA 组织](https://github.com/ErgeAIA)
