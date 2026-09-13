[Switch to English](README.en.md)

# ErgeAIA-skills

遵循 [Agent Skills 官方规范](https://agentskills.io/) 的生产级 Agent Skill 合集。

## 技能列表

| 技能 | 说明 | 版本 |
|------|------|------|
| [skill-workshop](skill-workshop/) | Skill 全生命周期工作站：创建、评审、重构、评测 Agent Skill（含 Google 5 模式基线） | v1.25.0 |
| [changelog-manager](changelog-manager/) | 基于 Keep a Changelog 规范的更新日志维护助手 | v2.0.1 |
| [zuiti](zuiti/) | 嘴替：替你生成骂人不带脏字的文明怼人回复（默认六风格每风格 3 条全到齐；引经据典 / 名人名言多来源、三层禁区、人工闸） | v0.3.9 |
| [vibe-buddy](vibe-buddy/) | 项目 AI 协作记忆管理：把协作契约写进 AGENTS.md，把进度、决策、踩坑沉淀到 docs/.ai/，跨会话交接靠自包含文档，并把开发过程蒸馏成按领域组织的可复用经验；另可只读审查开发类项目的代码质量与技术栈（vibe-init / vibe-sync / vibe-handoff / vibe-distill / vibe-audit） | v1.1.0 |

## 快速开始

### 安装技能

```bash
# 安装本仓库中的所有技能
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills

# 安装指定技能（使用 --skill 参数）
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill changelog-manager
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill skill-workshop
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill zuiti
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill vibe-buddy

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
