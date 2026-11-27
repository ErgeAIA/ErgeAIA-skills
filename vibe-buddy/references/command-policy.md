---
name: command-policy
description: vibe-buddy 的终端命令策略：全局白名单、各触发词允许的命令子集、执行纪律与失败处理。
trigger-when: 任何触发词准备运行终端命令前
role: spec
consumed-by: references/init-env-checks.md、references/sync-progress.md、references/handoff-context.md、references/distill-experience.md、references/audit-project.md
known-limits: 白名单是文档自律，无运行时拦截；不覆盖各 IDE 的原生权限机制
---

# 命令策略

公共段（写入唯一性 / 高风险四类 / 失败处理）见 `references/workflow-protocol.md`；本文件是终端命令白名单的单一真源。

## 默认

本技能默认不运行终端命令。只有白名单内的命令可执行，且必须落在**当前触发词允许的子集**内；子集外的命令即使安全也不跑。

## 白名单

| 命令 | 用途 | 性质 | 允许的触发词 |
| ---- | ---- | ---- | ------------ |
| `git rev-parse --is-inside-work-tree` | 判断是否在 Git 仓库内 | 只读 | `vibe-init`、`vibe-sync`、`vibe-handoff`、`vibe-distill`、`vibe-audit` |
| `git rev-parse --show-toplevel` | 定位仓库根 | 只读 | `vibe-init`、`vibe-sync`、`vibe-handoff`、`vibe-distill`、`vibe-audit` |
| `git status --short` | 核对工作区改动（未提交改动的主力） | 只读 | `vibe-sync`、`vibe-handoff`、`vibe-distill`、`vibe-audit` |
| `git log --oneline -n <N>` / `git log --oneline <base>..HEAD` | 核对已有提交；区间形态用于取变更集 | 只读 | `vibe-sync`、`vibe-handoff`、`vibe-distill`、`vibe-audit` |
| `git diff --stat` | 核对**已跟踪**文件的未提交改动（不含未跟踪文件） | 只读 | `vibe-sync`、`vibe-handoff`、`vibe-distill`、`vibe-audit` |
| `git diff --numstat` | 变更集规模判定（增删行数 / 是否二进制），**不暴露内容** | 只读 | `vibe-sync`、`vibe-audit` |
| `git diff --name-status` | 变更集范围与变更类型（A/M/D/R） | 只读 | `vibe-sync`、`vibe-audit` |
| `git diff -U3 -- <path>` | 逐文件取证，**必须带路径** | 只读 | `vibe-audit` |
| `git diff --cached -- <path>` | 已暂存改动的逐文件取证，**必须带路径** | 只读 | `vibe-audit` |
| `git merge-base HEAD <base>` | 用户指定基线分支时解析基线 | 只读 | `vibe-audit` |
| `git status --ignored --porcelain` | 核对忽略状态与未跟踪文件 | 只读 | `vibe-init` |
| `git ls-files -ci --exclude-standard` | 查已追踪且被忽略规则命中的文件 | 只读 | `vibe-init` |
| `git check-ignore -v <path>` | 追溯单条忽略规则的来源行 | 只读 | `vibe-init` |
| `git tag --list` | 判断是否已有发布 tag（决定 CHANGELOG 能否归档） | 只读 | `vibe-init` |
| `codegraph --version` | 判断是否已安装 | 只读 | `vibe-init` |
| `codegraph status` | 补充索引信息，不作判定依据 | 只读 | `vibe-init` |
| `git init` | 本项目非仓库时初始化 | 写 | `vibe-init` |
| `codegraph init` | 已装且本项目无索引时建索引 | 写 | `vibe-init` |

### diff 取证的边界（必须遵守）

`git diff` 家族只允许上表列出的形态。**显式禁止**：

- 裸 `git diff`（不带路径、不带 `--stat` / `--numstat` / `--name-status`）——输出无边界；
- `git log -p`、`git show`（含 patch）——历史 patch 无上限，审历史不是本技能场景。

**三重上限**（超限时按 P5 降级，不静默截断）：

| 维度 | 上限 | 超限处置 |
|---|---|---|
| 文件数 | 30 | 按 `--numstat` 增删总量取前 30 个，产物里写明「未覆盖 N 个」 |
| 单文件 diff | 400 行 | 该文件只取前 400 行并在证据里标「已截断」 |
| 总输出 | 80 KB | 停止读取后续文件，写明已覆盖与未覆盖清单 |

取证纪律：

- 先 `--numstat` 判规模，再 `--name-status` 定范围，最后才逐文件 `-U3`——顺序反了会在超大改动上先撑爆上下文；
- 命中密钥模式（`.env*`、`*.pem`、`*_key*`、`credentials*`、`*secret*`）的文件**整文件跳过**，只记路径不读内容；
- 报告只引 `路径:行` 与一句描述，**不贴 diff 原文**。

## 禁止

构建、测试、格式化、依赖安装、`git add` / `commit` / `push` / `checkout` / `reset` / `stash`、`codegraph install` / `uninstall`、以及任何会改动文件或系统配置的命令。

## 执行纪律

- 写操作执行前声明意图与目标路径；只读命令直接跑，不额外确认
- 执行后如实记录退出码与关键输出；写操作另记实际耗时
- 任何一条失败都不中断后续步骤，记入报告或回复后继续；但**先判它是不是「正常状态」而非失败**——零提交仓库里 `git log` 返回 128 并报 `does not have any commits yet`，属正常状态，记「尚无提交」
- **「空输出」同理，判据只在这里定义一次**：`git diff --stat` 不显示未跟踪文件，为空**不等于**没有改动，应以 `git status --short` 为准；仓零提交时 git 只能给出「全部未跟踪」，属正常状态而非失败。各 references 需要时引用本条，不再复述
- 输出含密钥或敏感路径时脱敏或截断，只留结论
- 本项目不是 Git 仓库时，跳过全部 `git` 命令，视为「无此事实源」，不报错
