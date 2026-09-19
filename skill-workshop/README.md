# skill-workshop

<p align="center">
  <img src="assets/banner.svg" alt="skill-workshop" width="100%">
</p>

**v2.1.0** · 轻量 Skill 质量工作站：创建 → 评审 → 重构 → 合规校验。

设计原则：最低审查成本发现致命缺陷；**Fast/Deep/Eval**（≡ L0/L1/L2）风险驱动分级；判断框架见 `core-method.md`（Core Task、证据链、规则生命周期、删除优先）；规则 HARD / CONDITIONAL / HEURISTIC / EXPERIMENTAL / ARCHIVED。

## 四种意图

| 意图 | 路径 | 产出 |
| --- | --- | --- |
| 创建 | `references/creation.md` + CLI `init` | SKILL.md 骨架 |
| 评审 | Fast/Deep + `references/review.md` | 报告（证据化 findings） |
| 重构 | 审计 → Rule Compression → validate | 改进后的技能 |
| 校验 | CLI `spec` + `validate` | PASS/FAIL |

Eval/评测为条件路径，工具在 `docs/archive/`。

## CLI

```bash
python scripts/skill_cli.py validate /path/to/skill
python scripts/skill_cli.py spec /path/to/skill
python scripts/skill_cli.py init my-skill --path ./output
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
| [references/core-method.md](references/core-method.md) | 审计判断框架（Core Task、生命周期、删除优先） |
| [references/creation.md](references/creation.md) | 极简创建规范与模板 |
| [references/review.md](references/review.md) | Fast/Deep/Eval、T/E/C、P0/P1/P2、报告结构 |
| [references/validation.md](references/validation.md) | 格式与安全闸门、N/A |
| [CHANGELOG.md](CHANGELOG.md) | 版本史 |
| [docs/integration-2026-09-19.md](docs/integration-2026-09-19.md) | 方法论整合记录与 Before/After |
| [docs/archive/README.md](docs/archive/README.md) | 归档说明（非运行时） |

## 版本对齐

`SKILL.md metadata.version` = `CHANGELOG.md` 顶部 = 仓库根 README 技能索引版本。
