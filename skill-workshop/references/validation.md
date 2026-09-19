---
trigger-when: 运行 validate/spec/package、编写校验相关步骤、或需要基础格式与核心安全规范时
name: validation
description: 基础格式、版本 SSOT、链接与脚本安全闸门；CLI validate/spec/package 用法与退出码。
---

# 验证规范（validation）

## 机器闸门（运行时 CLI）

| 命令 | 检查什么 | 退出码 |
| --- | --- | --- |
| `python scripts/skill_cli.py spec <path>` | 官方 frontmatter：白名单、字段顺序、name 目录一致与格式、description 有无/尖括号/长度 | 0 PASS / 1 FAIL / 2 ERROR |
| `python scripts/skill_cli.py validate <path>` | 结构静态校验：frontmatter、引用路径、版本等（详见 `--help` 与 findings） | 同上 |
| `python scripts/skill_cli.py init <name> --path <dir>` | 纯 Markdown 骨架；默认 dry-run；`--write` 落盘（plan-gate） | 0/1/2 |
| `python scripts/skill_cli.py package <path> [out]` | 校验后打包 `.skill`；默认 dry-run；`--write` 才落盘（plan-gate） | 0/1/2 |

约定：错误与诊断写 **stderr**，状态/数据写 **stdout**；禁止 `input()` 交互。

## HARD 格式与安全

1. **目录**：技能目录存在 `SKILL.md`。
2. **Frontmatter**：YAML 块完整；必含 `name`、`description`。
3. **name**：与父目录名一致；`[a-z0-9-]`；长度 ≤64；无首尾连字符；无 `--`。
4. **description**：非空；≤1024；不含尖括号 `<` `>`。
5. **顶层字段白名单**：仅 `name` / `description` / `license` / `compatibility` / `metadata` / `allowed-tools`；建议顺序与之一致；`triggers`/`tags` 等禁止顶层。
6. **版本 SSOT**：`metadata.version`（三段式 `X.Y.Z`）为机器事实；变更史在技能根 `CHANGELOG.md`。**不要求** SKILL 正文头部版本块与文末版本历史（有 CHANGELOG 时可省略）。
7. **引用**：主文档与保留 references 中的相对路径必须真实存在。
8. **非破坏**：重构/归档不得覆盖用户未授权的技能产物；写文件走 plan-gate。
9. **脚本（CONDITIONAL）**：存在 `scripts/` 时——无 `input()` 交互；支持 `--help`；退出码 0=PASS/1=FAIL/2=ERROR；错误走 stderr。**无 `scripts/` → 本组检查 = N/A，不记缺陷。**
10. **密钥**：任何配置/文档不得写入 token、密码、连接串。
11. **Runtime/Governance 分离**：不得把 skill-workshop 治理条文写入被审计技能的运行时文档。
12. **无平行流程**：整合方法论后不得出现「旧流程 + 新流程」双跑；单一审计主路径。

## 条件检查 N/A（不把不适用判成缺陷）

| 无此能力时 | 对应检查 |
| --- | --- |
| 无 `scripts/` | 脚本纪律 / P 系列 |
| 无 eval 且不要求评测 | V4/V5、Eval Review |
| 无家族 baseline 指定 | family-diff 类 |
| 无编排共享字段 | 字段争用 |
| 无已知 recurring gotcha | 不强制 Gotchas 章 |

## 版本与发布对齐（本仓库）

推送前核对：

```text
SKILL.md metadata.version = CHANGELOG.md 顶部版本 = 根 README 索引版本
```

技能增删或升版后，在 `Skills-Depot` 执行：

```bash
uv run --no-project python scripts/sync_skills_browser.py
```

## validate 使用注意

- 建议传显式路径：`validate path/to/skill-dir`。
- `validate` findings 可能含 advisory；**FAIL 才阻塞**「通过」结论。
- `spec` 与 `validate` 职责不同；交付前两者都跑。
- 重构/方法论整合后：对**本技能自身**也跑 `spec` + `validate`，并记录 Before/After 体量。

## package 注意

- 默认 **dry-run**；`--write` 生成 `.skill` 且须 plan-gate。
- 打包跳过 `dist/`、`__pycache__/`、评测运行目录及 `docs/archive/` 等。

## 报告中的验证表述

- 机器 FAIL → 不得写「校验通过」。
- 未跑命令 → 不得写「已验证」；写「未验证」。
- 归档工具链结果不得伪装成运行时 CLI 结果。

## 失败处理顺序

1. 读 stderr 具体条目（含修复建议）。
2. 改源文件，不改断言来「让测试变绿」。
3. 重跑 `spec` + `validate` 至 PASS。
4. 涉及版本变更 → 同步 CHANGELOG 与根 README → 跑 sync 脚本。
