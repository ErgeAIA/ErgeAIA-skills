# ErgeAIA-skills

遵循 [Agent Skills 官方规范](https://agentskills.io/) 的生产级 Agent Skill 合集。

## 技能列表

| 技能 | 说明 | 版本 |
|------|------|------|
| [skill-reviewer](skill-reviewer/) | 九维 48 项结构化评审与合规校验 | v4.6 |
| [changelog-manager](changelog-manager/) | 基于 Keep a Changelog 规范的更新日志维护助手 | v1.1.0 |

## 快速开始

### 安装技能

```bash
# 安装本仓库中的所有技能
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills

# 或安装指定技能
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills/tree/main/skill-reviewer
```

### 使用 skill-reviewer

```bash
# 评审一个技能目录
npx skill-reviewer /path/to/your-skill

# 仅做合规校验
npx skill-reviewer --spec /path/to/your-skill

# 完整审计（合规 + 检查清单 + 术语一致性）
npx skill-reviewer --spec --checklist --consistency /path/to/your-skill
```

## 规范合规

本仓库中的所有技能均符合以下要求：

- ✅ frontmatter 包含 `name` 和 `description` 字段
- ✅ 渐进式披露（SKILL.md < 500 行）
- ✅ 脚本无交互式提示
- ✅ CLI 工具支持 `--help`
- ✅ 结构化退出码（0=PASS, 1=FAIL, 2=ERROR）
- ✅ 单元测试覆盖

## 开发

```bash
# 克隆仓库
git clone https://github.com/ErgeAIA/ErgeAIA-skills.git
cd ErgeAIA-skills

# 运行 skill-reviewer 测试
cd skill-reviewer
uv run python -m unittest tests.test_validate_review -v
```

## 许可证

MIT License — 详见 [LICENSE](LICENSE)。

## 贡献

欢迎贡献！请：
1. Fork 本仓库
2. 创建功能分支
3. 确保测试通过
4. 提交 Pull Request

## 致谢

本项目参考了 [base44/skills](https://github.com/base44/skills) 项目的资源。具体来说，文件 `skill-reviewer/references/specs/spec-zh.md` 改编自 [spec.md](https://github.com/base44/skills/blob/ec420cf2edd2c7e9a523d5afe2e71498a6357fa4/.claude/skills/review-skills/references/spec.md)。我们衷心感谢原作者的开源贡献。

## 相关链接

- [Agent Skills 规范](https://agentskills.io/)
- [ErgeAIA 组织](https://github.com/ErgeAIA)
