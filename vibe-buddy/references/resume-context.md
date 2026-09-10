---
name: resume-context
description: vibe-resume 的执行契约：只读项目记忆与最新交接文档，向用户结构化汇报现状，然后停下等指令。
trigger-when: 用户说「接管项目」「接手上下文」「vibe-resume」，或新会话开始需要先弄清现状时
role: workflow
reads-from:
  - <project>/AGENTS.md
  - <project>/docs/.ai/project-progress.md
  - <project>/docs/.ai/decision-log.md
  - <project>/docs/.ai/debug-log.md
  - <project>/docs/handoff/ 中最新一份
  - git status / git log（仅本项目在 Git 仓库内时）
writes-to: 无
---

# resume · 接管上下文

## 目标

新会话的第一次响应：把项目现状压成一份 30 秒能读完的汇报，交给用户判断下一步。**只读，不写，不改。**

## 前置检查

| 检查项 | 不通过时 |
|---|---|
| `<project>/AGENTS.md` 是否存在 | 不存在 → 回复缺失项，引导先跑 `vibe-init` |
| `docs/.ai/project-progress.md` 与 `decision-log.md` 是否存在 | 缺 → 回复缺失项，引导先跑 `vibe-init`；仍按已有文件汇报 |
| `docs/handoff/` 是否有可读交接文档 | 无 → 只依据 `AGENTS.md` 与 `docs/.ai/` 汇报，并说明没有交接文档 |

## 读取顺序

1. `AGENTS.md` —— 规则契约，必读
2. `docs/.ai/project-progress.md` —— 进度，先读它
3. `docs/.ai/decision-log.md` —— 已锁定决策，优先级高于 PRD
4. `docs/.ai/debug-log.md` —— 已知坑与预防规则
5. `docs/handoff/` 中**最新**的一份交接文档
6. `docs/.ai/project-overview.md`（存在时）

"最新"的判法：按文件名日期取最新；同日期存在多份时，读该日期的全部文件、取 frontmatter `updated` 最新者；仍无法判定则列出全部，问用户读哪份。

## 硬性约束

- **不创建、不修改、不删除任何文件**。本触发词没有任何写入动作。
- 除下列只读 Git 命令外不跑任何命令：`git status --short`、`git log --oneline -n <N>`（仅本项目在 Git 仓库内时）。构建、测试、依赖安装与任何写命令都不跑。
- 项目不是 Git 仓库时跳过 Git，如实说明，不报错。
- 不输出代码，不重新设计架构，不提重构建议。
- 汇报完就停下，等用户显式下达任务指令。
- 交接文档缺失时如实说明，不臆造上次进度。
- 读不到的写「未建立」或「未知」，不猜（如空白项目的技术栈、尚为占位的 Toolchain 表）。

## 汇报结构（按此顺序，不增不减）

| 段落 | 内容 |
|---|---|
| 读取确认 | 实际读到的文件清单、最新交接文档的文件名与日期、Git 状态（仓库根、最近提交、工作区是否干净；非 Git 仓库则注明） |
| 项目核心信息 | 定位一句话、技术栈（未建立则写「未建立」）、最容易踩的 2 到 3 条协作规则、已锁定决策 2 到 3 条 |
| 上次进度 | 已完成、进行中与卡点、待用户验证项、交接文档标注的特有风险 |
| 当前阶段定位 | 处于哪个阶段，是否存在阻塞 |
| 下一步建议 | 1 到 3 个可执行选项，各附推荐理由、预计涉及文件、风险级别 |
| 等待指令 | 固定收尾：请用户指定选项或给出新指令；收到明确指令前不做任何文件改动 |

## 终止回复

按上表输出六段，不追加额外解释。最后一句固定落在「等待指令」段。
