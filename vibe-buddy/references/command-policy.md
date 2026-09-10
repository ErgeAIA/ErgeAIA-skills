---
name: command-policy
description: vibe-buddy 的终端命令策略：全局白名单、各触发词允许的命令子集、执行纪律与失败处理。
trigger-when: 任何触发词准备运行终端命令前
role: spec
consumed-by: references/init-env-checks.md、references/sync-progress.md、references/handoff-context.md、references/distill-experience.md
---

# 命令策略

## 默认

本技能默认不运行终端命令。只有白名单内的命令可执行，且必须落在**当前触发词允许的子集**内；子集外的命令即使安全也不跑。

## 白名单

| 命令 | 用途 | 性质 | 允许的触发词 |
| ---- | ---- | ---- | ------------ |
| `git rev-parse --is-inside-work-tree` | 判断是否在 Git 仓库内 | 只读 | `vibe-init`、`vibe-sync`、`vibe-handoff`、`vibe-distill` |
| `git rev-parse --show-toplevel` | 定位仓库根 | 只读 | `vibe-init`、`vibe-sync`、`vibe-handoff`、`vibe-distill` |
| `git status --short` | 核对工作区改动（未提交改动的主力） | 只读 | `vibe-sync`、`vibe-handoff`、`vibe-distill` |
| `git log --oneline -n <N>` | 核对已有提交 | 只读 | `vibe-sync`、`vibe-handoff`、`vibe-distill` |
| `git diff --stat` | 核对**已跟踪**文件的未提交改动（不含未跟踪文件） | 只读 | `vibe-sync`、`vibe-handoff`、`vibe-distill` |
| `codegraph --version` | 判断是否已安装 | 只读 | `vibe-init` |
| `codegraph status` | 补充索引信息，不作判定依据 | 只读 | `vibe-init` |
| `git init` | 本项目非仓库时初始化 | 写 | `vibe-init` |
| `codegraph init` | 已装且本项目无索引时建索引 | 写 | `vibe-init` |

## 禁止

构建、测试、格式化、依赖安装、`git add` / `commit` / `push` / `checkout` / `reset` / `stash`、`codegraph install` / `uninstall`、以及任何会改动文件或系统配置的命令。

## 执行纪律

- 写操作执行前声明意图与目标路径；只读命令直接跑，不额外确认
- 执行后如实记录退出码与关键输出；写操作另记实际耗时
- 任何一条失败都不中断后续步骤，记入报告或回复后继续
- 输出含密钥或敏感路径时脱敏或截断，只留结论
- 本项目不是 Git 仓库时，跳过全部 `git` 命令，视为「无此事实源」，不报错
