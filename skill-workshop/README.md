# skill-workshop

<p align="center">
  <img src="assets/banner.svg" alt="skill-workshop" width="100%">
</p>

**v2.0.1** · 轻量 Skill 质量工作站：创建 → 评审 → 重构 → 合规校验。

设计原则：用最低审查成本发现致命缺陷；默认 L0 轻查，疑点再 L1 展开；规则分为 HARD / CONDITIONAL / HEURISTIC。

## 四种意图

| 意图 | 路径 | 产出 |
| --- | --- | --- |
| 创建 | `references/creation.md` + CLI `init` | SKILL.md 骨架 |
| 评审 | L0/L1 + `references/review.md` | 短报告（证据化 findings） |
| 重构 | 评审发现问题 → 按 creation/validation 整改 | 改进后的技能 |
| 校验 | CLI `spec` + `validate` | PASS/FAIL |

评测/benchmark 为 L2 条件路径，工具在 `docs/archive/`。

## CLI

```bash
# 结构静态校验
python scripts/skill_cli.py validate /path/to/skill

# 官方 frontmatter 规范检查
python scripts/skill_cli.py spec /path/to/skill

# 初始化纯净骨架（默认 dry-run）
python scripts/skill_cli.py init my-skill --path ./output

# 打包（默认 dry-run；--write 落盘需 plan-gate）
python scripts/skill_cli.py package /path/to/skill
```

## 用法示例

```text
帮我创建一个处理 PDF 的 Skill
评审一下这个 skill：/path/to/my-skill/
重构一下这个 skill 的结构
校验 skill 规范：/path/to/my-skill/
```

## 文档

| 文件 | 用途 |
| --- | --- |
| [SKILL.md](SKILL.md) | AI 运行时主文档（路由 + 硬约束） |
| [references/core-method.md](references/core-method.md) | 路由分级与规则分级 |
| [references/creation.md](references/creation.md) | 极简创建规范与模板 |
| [references/review.md](references/review.md) | T/E/C 三轴评审标准 |
| [references/validation.md](references/validation.md) | 格式与安全闸门 |
| [CHANGELOG.md](CHANGELOG.md) | 版本史 |
| [docs/archive/README.md](docs/archive/README.md) | 归档说明（非运行时） |

## 版本对齐

`SKILL.md metadata.version` = `CHANGELOG.md` 顶部 = 仓库根 README 技能索引版本。
