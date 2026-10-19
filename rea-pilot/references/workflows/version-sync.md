---
name: "W-SYNC 版本同步"
description: "REA 升级后重新生成版本化工具表，并完成四处版本对齐。"
version: 1.0.0
trigger-when: REA 升级、工具清单对不上、或 toolset 文件版本与本机 version 不一致时
reads-from: SKILL.md, references/specs/toolset-generation.md
writes-to: references/toolset/rea-<新版本>.md, SKILL.md 资源表, CHANGELOG.md, 根 README 双语
---
# @工作流: W-SYNC 版本同步

## @步骤1: 确认本机版本与官方变更

```bash
rea --version                                # 本机版本（工具表的版本锚）
rea update                                   # 需要时先升级
rea mcp doctor --json                        # 升级后确认 server 身份与工具计数
```

官方变更日志：<https://raw.githubusercontent.com/morluto/rea/main/CHANGELOG.md>（条目形如 `## 6.7.0 (2026-10-18)`，版本号上带官方 compare 链接；小节为 `### Highlights` / `### Changes` / `### Fixes`）。**先看 Fixes**：与接入直接相关的改动常写在那里（6.7.0 的 Fixes 就是「Setup 编辑最后一条重复 JSON/JSONC 成员」「Setup 与 uninstall 拒绝会复活被遮蔽成员的删除」）。

版本号陷阱：官方可能**打了 tag 但没发 npm**（6.6.0 即如此）。判断本机版本只认 `rea --version` 与实际安装的包，不认 tag。

## @步骤2: 判断要不要重生成

| 条件 | 动作 |
| --- | --- |
| `references/toolset/rea-<本机版本>.md` 不存在 | 生成新版本文件 |
| 存在但内容与 `rea mcp doctor` 的计数或目录摘要对不上 | 重新生成同名文件（覆盖） |
| 版本号相同但官方有 Changes 提到工具改名/新增 | 重新生成同名文件 |

## @步骤3: 重新生成工具表

按 `references/specs/toolset-generation.md` 执行（命令、列口径、分组、版本锚都在那里）。要点：

- 输入只有三样：MCP stdio 的 `tools/list` + `prompts/list`、`rea --llms`、`rea capabilities`。
- **不手改**生成出来的文件；要改口径就改生成规范。
- 旧版本文件**保留**，用于回溯「当时这个工具叫什么」。

## @步骤4: 四处版本对齐（缺一处不许收尾）

| 位置 | 内容 |
| --- | --- |
| `SKILL.md` frontmatter | `metadata.version` |
| 根 `CHANGELOG.md` | 顶部最新版本条目 + 技能索引 |
| 根 `README.md` / `README.en.md` | 技能索引行的版本列 |
| 本技能 `README.md` 末尾 | 「当前版本：**vX.Y.Z**」 |

另外：本技能 `CHANGELOG.md` 追加一条「工具面同步到 <版本>：新增 N / 删除 M / 改名 K」。

@验证点：贴出四处版本字符串 + `rea mcp doctor` 的计数与目录摘要；四处不一致 → 不许提交。
