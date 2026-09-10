---
name: vibe-buddy
description: "当用户要为项目建立或更新 AI 协作契约、跨会话交接上下文、接管新会话、沉淀进度决策与调试经验时，替他读写项目根 AGENTS.md、docs/.ai/ 与 docs/handoff/。触发词：'初始化项目'、'生成 AGENTS.md'、'vibe-init'、'同步进度'、'更新项目进度'、'vibe-sync'、'交接上下文'、'写交接文档'、'vibe-handoff'、'接管项目'、'接手上下文'、'vibe-resume'、'经验蒸馏'、'沉淀经验'、'vibe-distill'。哪怕用户没提技能名也触发。不适用于：任务计划与待办拆解、需求转译成 PRD、代码生成与重构、运行构建或测试命令、规范文档生命周期管理。"
compatibility: 纯文件读写型技能；无网络、无第三方依赖、不运行终端命令。产物落在目标项目自身的 AGENTS.md、docs/.ai/ 与 docs/handoff/ 下，不写入技能仓库。
metadata:
  author: ErgeAIA
  version: "1.0.0"
---

# vibe-buddy

## 核心原则

把项目的 AI 协作记忆当成**可审计的文本资产**：规则留在 `AGENTS.md`，长期记忆留在 `docs/.ai/`，会话交接留在 `docs/handoff/`。

1. **不覆盖** —— 已有文件只追加；需要新文件时先扫描目录再取名，永不重写既有内容。
2. **不猜测** —— 读不到的事实写占位符，绝不编造版本号、路径、命令、结论。
3. **不越界** —— 只读写协作契约与过程文档区（路径见下方产物布局），不碰源码、不跑命令、不发布。
4. **不静默** —— 删除或改写必须留下「旧值 → 处置 → 新值」的可见记录。

## 路由与硬规则

### @步骤1: 路由决策

| 场景 | 命中信号 | 跳转到 |
|---|---|---|
| 项目首次接入协作记忆，或补齐缺失的过程文档 | 「初始化项目」「生成 AGENTS.md」「vibe-init」；或项目缺 `AGENTS.md` 与 `docs/.ai/` | `references/init-agents-md.md` |
| 任务完成，要沉淀进度、决策或 bug 经验 | 「同步进度」「更新项目进度」「vibe-sync」 | `references/sync-progress.md` |
| 换会话、换 agent、上下文将满 | 「交接上下文」「写交接文档」「vibe-handoff」 | `references/handoff-context.md` |
| 新会话开始，要先弄清现状 | 「接管项目」「接手上下文」「vibe-resume」 | `references/resume-context.md` |
| 反复调试的问题定位到根因，要沉淀 | 「经验蒸馏」「沉淀经验」「vibe-distill」 | `references/distill-lessons.md` |

### @步骤2: 强规则摘要

- **先确认再执行**：识别触发词后先回一行路由确认，用户确认才动手。
- **写入前声明**：操作类型 / 目标路径 / 是否覆盖 / 风险等级；同一触发词内只声明一次。
- **一次只走一个触发词**：「同步并交接」拆成两轮各自确认，不自动串联。
- **前置缺失即停**：如 `vibe-sync` 找不到 `docs/.ai/` 时引导先跑 `vibe-init`，绝不代建。
- **歧义先反问**：只说「交接」而不明方向时，反问是生成交接还是接管。
- **全程不运行终端命令**：构建、测试、Git、包管理一律不做。
- **产物必须脱敏**：密钥、token、凭据、连接串、个人隐私一律不落盘；无法脱敏则拒绝写入。
- **不重复已有产物**：规格、计划、决策、提交、diff 已有的内容，用路径引用。

## 产物布局

| 产物 | 路径 | 写入者 |
|---|---|---|
| AI 协作契约 | `<project>/AGENTS.md` | `vibe-init` |
| Claude Code 镜像（可选，指针非副本） | `<project>/CLAUDE.md` | `vibe-init` |
| 项目进度，实时更新 | `<project>/docs/.ai/project-progress.md` | `vibe-init` 建骨架，`vibe-sync` 维护 |
| 决策日志，优先级高于 PRD（层 C 约定处置并入其 `## Layer C` 小节） | `<project>/docs/.ai/decision-log.md` | `vibe-init` 建骨架，`vibe-sync` 追加 |
| bug 修复经验 | `<project>/docs/.ai/debug-log.md` | `vibe-init` 建骨架，`vibe-distill` 追加 |
| 项目概览（可选） | `<project>/docs/.ai/project-overview.md` | `vibe-init` |
| 会话交接文档 | `<project>/docs/handoff/handoff-YYYY-MM-DD.md` | `vibe-handoff` |

## 何时读 references

- 要建 `AGENTS.md`、判定路由模式、补齐缺失文档 → `references/init-agents-md.md`
- 要执行 `AGENTS.md` 的生成规范本身（句式契约、黑名单、自检门） → `references/agents-md-generator.md`
- 要沉淀进度与决策 → `references/sync-progress.md`
- 要生成交接文档 → `references/handoff-context.md`
- 新会话要弄清现状并汇报 → `references/resume-context.md`
- 要沉淀调试经验与 bug 根因 → `references/distill-lessons.md`
- 改过 description 要回归触发 → `references/trigger-test-set.md`

## 失败模式与兜底

| 触发条件 | 一线修复 | 仍失败兜底 |
|---|---|---|
| 前置文件缺失（如无 `docs/.ai/` 却要 sync） | 回复缺失项，引导先跑 `vibe-init` | 用户坚持从零建立 → 转 `vibe-init`，不就地代建 |
| 触发词歧义（「交接」未分方向） | 反问：生成交接文档还是接管上下文 | 用户仍不明确 → 停下，不动任何文件 |
| `vibe-init` 遇到已有文档 | 只补缺失项，已存在的文件一字不动 | 内容冲突且无法判定 → 停下请用户裁决 |
| 同日已有同名交接文档 | 加语义后缀（`handoff-YYYY-MM-DD-<slug>.md`） | 后缀仍冲突 → 停下请用户指定文件名 |
| 本次会话无稳定增量 | 明说「本次无可同步的稳定增量」，不写文件 | 用户要求留痕 → 追加一行说明性占位，不编造内容 |
| 会话里没有可沉淀的经验 | 明说没有可沉淀的经验，不编造 | 用户坚持 → 只写有对话依据的条目，宁缺勿造 |
| 待写内容含密钥 / 凭据 / 隐私 | 脱敏为占位符后写入 | 无法安全脱敏 → 拒绝写入并说明原因 |
| 参考文件缺失或读不通 | 报告缺失路径，停止执行 | 用户要求硬做 → 拒绝，缺规则不做 |

## Gotchas

- `AGENTS.md` 是**规则契约**，不承载进度与待办；进度写 `docs/.ai/project-progress.md`。
- `docs/.ai/` 是**只追加**的过程文档区。决策冲突时把旧条目改标 `superseded`，不删除历史条目。
- `CLAUDE.md` 是**指针**不是副本；整份复制会在下轮维护后与 `AGENTS.md` 漂移。
- 交接文档写给**另一个 agent**：能从 `git log`、diff、规格文档里读到的，写路径，不复述。
- `docs/.ai/` 是**记忆区**不是文档区；人类项目文档（README、设计稿）不放这里。
- 过程文档的 frontmatter `updated` 必须随每次修改同步改当日；漏改等于让 `updated` 说谎。
- `vibe-init` 对半程项目**只补齐缺失文档**，绝不重写已有文件——哪怕内容看起来过时。
- 不新增 `AGENTS.md` 章节：文档义务写进固定的 `Permissions` 与 `Conventions`，不另起段落。

## 非目标

- 不做任务拆解、排期、待办追踪。
- 不把模糊需求转译成 PRD 或结构化指令。
- 不写代码、不重构、不运行构建测试 Git 命令。
- 不管理规格与变更的生命周期。
- 不做对外发布，不代发内容。
- 不实现跨项目共享的个人记忆库。

## 验证

| 触发词 | 成功判定 |
|---|---|
| `vibe-init` | 模式判定有可观测依据；`AGENTS.md` 六节成文且未新增章节；`docs/.ai/` 三件套与 `docs/handoff/` 就位；缺失项已补齐，既有文件未被覆盖 |
| `vibe-sync` | `project-progress.md` 有新增；有决策时 `decision-log.md` 已追加；未改动 `AGENTS.md` |
| `vibe-handoff` | 交接文档落入 `docs/handoff/`，含建议调用的技能段，未覆盖既有文件 |
| `vibe-resume` | 输出结构化汇报；未创建或修改任何文件 |
| `vibe-distill` | `debug-log.md` 有新增条目（或明确回复无可沉淀经验） |

## 参考

- 人类使用说明与设计取舍：[`README.md`](README.md)
- 版本演进：[`VERSION.md`](VERSION.md)
