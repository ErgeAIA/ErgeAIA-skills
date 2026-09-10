---
name: vibe-buddy
description: "当用户要为项目建立或更新 AI 协作契约、跨会话交接上下文、接管新会话、沉淀可复用经验时，替他读写项目根 AGENTS.md 与 docs/.ai/ 下的记忆文档。触发词：'初始化项目'、'生成 AGENTS.md'、'vibe-init'、'同步进度'、'更新项目进度'、'vibe-sync'、'交接上下文'、'写交接文档'、'vibe-handoff'、'接管项目'、'接手上下文'、'vibe-resume'、'经验蒸馏'、'沉淀经验'、'vibe-distill'。哪怕用户没提技能名也触发。不适用于：任务计划与待办拆解、需求转译成 PRD、代码生成与重构、运行构建或测试命令、规范文档生命周期管理。"
compatibility: 纯文件读写型技能；无网络、无第三方依赖、不运行终端命令。产物落在目标项目自身的 AGENTS.md 与 docs/.ai/ 下，不写入技能仓库。
metadata:
  author: ErgeAIA
  version: "1.0.0"
---

# vibe-buddy

## 核心原则

把项目的 AI 协作记忆当成**可审计的文本资产**：规则留在 `AGENTS.md`，长期记忆留在 `docs/.ai/`，交接靠**自包含文档**而不是对话历史。

四条不可让步的底线：

1. **不覆盖** —— 已有文件只追加；需要新文件时先扫描目录再取新序号，永不重写既有内容。
2. **不猜测** —— 读不到的事实写占位符，绝不编造版本号、路径、命令、结论。
3. **不越界** —— 只读写 `AGENTS.md`、`CLAUDE.md` 与 `docs/.ai/`，不碰源码、不跑命令、不发布。
4. **不静默** —— 任何删除或改写都要留下「旧值 → 处置 → 新值」的可见记录。

## 路由与硬规则

### @步骤1: 路由决策

| 场景 | 命中信号 | 跳转到 |
|---|---|---|
| 项目首次接入 AI 协作记忆 | 说「初始化项目」「生成 AGENTS.md」「vibe-init」；或项目根缺 `AGENTS.md` 却需要协作契约 | `references/init-agents-md.md` |
| 功能落地、决策达成、踩坑之后沉淀稳定事实 | 说「同步进度」「更新项目进度」「vibe-sync」「沉淀一下」 | `references/sync-progress.md` |
| 换窗口、换 agent、上下文将满，要把活交出去 | 说「交接上下文」「写交接文档」「vibe-handoff」 | `references/handoff-context.md` |
| 新会话开始，要先弄清项目现状 | 说「接管项目」「接手上下文」「vibe-resume」「继续上次的活」 | `references/resume-context.md` |
| 会话里攒下可复用的经验或踩坑 | 说「经验蒸馏」「沉淀经验」「把这次踩的坑记下来」「vibe-distill」 | `references/distill-lessons.md` |

### @步骤2: 强规则摘要

- **先确认再执行**：识别触发词后先回一行路由确认（触发词 / 将读的参考文件 / 待做的前置检查），用户确认才动手。
- **写入前声明**：操作类型 / 目标路径 / 是否覆盖 / 风险等级。同一触发词内多次写入只需声明一次。
- **一次只走一个触发词**：用户说「同步并交接」时拆成两轮，各自独立确认，不自动串联。
- **前置缺失即停**：例如 `vibe-sync` 找不到 `AGENTS.md` 时，回复缺失项并引导先跑 `vibe-init`，绝不代建。
- **歧义先反问**：只说「交接」而方向不明时，反问是生成交接文档还是接管，不自行判定。
- **全程不运行终端命令**：构建、测试、Git、包管理一律不做，需要时交给用户或其他技能。
- **产物必须脱敏**：密钥、token、账号凭据、连接串、个人隐私信息一律不落盘；无法脱敏则拒绝写入并说明。
- **不重复已有产物**：规格、计划、决策记录、提交、diff 里已有的内容用路径引用，不复述。

## 产物布局

| 产物 | 路径 | 写入者 |
|---|---|---|
| AI 协作契约 | `<project>/AGENTS.md` | `vibe-init` |
| Claude Code 镜像（可选，指针非副本） | `<project>/CLAUDE.md` | `vibe-init` |
| 项目进度专用文档 | `<project>/docs/.ai/progress.md` | `vibe-init` 建骨架，`vibe-sync` 追加 |
| 决策与变更日志 | `<project>/docs/.ai/decisions.md` | `vibe-init` 建骨架，`vibe-sync` 追加 |
| 踩坑与经验档案 | `<project>/docs/.ai/lessons.md` | `vibe-init` 建骨架，`vibe-distill` 追加 |
| 上下文交接文档 | `<project>/docs/.ai/handoffs/YYYYMMDD-NN.md` | `vibe-handoff` |
| 项目概览 | `<project>/docs/.ai/project-overview.md` | `vibe-init`（可选） |

## 何时读 references

- 要建或改 `AGENTS.md`、判定路由模式、执行决策保全 → `references/init-agents-md.md`
- 要执行 `AGENTS.md` 的生成规范本身（句式契约、黑名单、自检门） → `references/agents-md-generator.md`
- 要把稳定增量沉淀到进度文档 → `references/sync-progress.md`
- 要生成交接文档 → `references/handoff-context.md`
- 新会话要弄清现状并汇报 → `references/resume-context.md`
- 要提炼可复用经验与踩坑 → `references/distill-lessons.md`
- 改过 description 要回归触发 → `references/trigger-test-set.md`

## 失败模式与兜底

| 触发条件 | 一线修复 | 仍失败兜底 |
|---|---|---|
| 前置文件缺失（如无 `AGENTS.md` 却要 sync） | 回复缺失项，引导先跑 `vibe-init` | 用户坚持从零建立 → 转 `vibe-init` 流程，不就地代建 |
| 触发词歧义（「交接」未分方向） | 反问：生成交接文档还是接管上下文 | 用户仍不明确 → 停下，不动任何文件 |
| 目标文件已存在（同名交接文档 / 已有 `AGENTS.md`） | 交接文档取下一个序号；已有 `AGENTS.md` 走增量维护 | 序号仍无法确定 → 停下请用户指定路径 |
| 本次会话无稳定增量 | 明说「本次无可同步的稳定增量」，不写文件 | 用户要求留痕 → 追加一行说明性占位，不编造内容 |
| 会话里没有可提炼的经验 | 明说没有可复用经验，不编造 | 用户坚持 → 只写有对话依据的条目，宁缺勿造 |
| 待写内容含密钥 / 凭据 / 隐私 | 脱敏为占位符后写入 | 无法安全脱敏 → 拒绝写入并说明原因 |
| 参考文件缺失或读不通 | 报告缺失路径，停止执行 | 用户要求硬做 → 拒绝，缺规则不做 |

## Gotchas

- `AGENTS.md` 是**规则契约**，不是进度板。进度写 `docs/.ai/progress.md`；任务计划与待办交给计划类技能，不塞进契约。
- `CLAUDE.md` 是**指针**不是副本。整份复制会在两轮维护后与原文件漂移。
- 交接文档写给**另一个 agent**，不是写给下一个窗口。凡是对方能从 `git log`、diff、规格文档里读到的，写路径，不要复述。
- 层 B 项目概览的落点是 `docs/.ai/project-overview.md`，不是项目根的 `references/` 目录——生成规范里的原始写法按本技能的产物布局落盘。
- 取序号永远先扫描目录再取，别信记忆里的编号，也别信上次会话的编号。
- `docs/.ai/` 是**记忆区**不是文档区。人类的项目文档（README、设计稿）不放这里。

## 非目标

- 不做任务拆解、排期、待办追踪。
- 不把模糊需求转译成 PRD 或结构化指令。
- 不写代码、不重构、不运行构建测试 Git 命令。
- 不管理规格与变更的生命周期（OpenSpec 一类规范体系不在范围内）。
- 不做对外发布，不代发内容。
- 不实现跨项目共享的个人记忆库。

## 验证

| 触发词 | 成功判定 |
|---|---|
| `vibe-init` | `AGENTS.md` 已成文并通过生成规范的自检门；`docs/.ai/` 骨架存在；未覆盖任何既有文件 |
| `vibe-sync` | 进度文档有新条目（或明确回复「无可同步的稳定增量」）；未改动 `AGENTS.md` |
| `vibe-handoff` | 交接文档落入 `docs/.ai/handoffs/`；编号未覆盖既有文件；含建议调用的技能段 |
| `vibe-resume` | 输出结构化汇报；未创建或修改任何文件 |
| `vibe-distill` | 经验条目追加到 `lessons.md`（或明确回复无可提炼经验）；条目均带症状 / 根因 / 预防规则 |

## 参考

- 人类使用说明与设计取舍：[`README.md`](README.md)
- 版本演进：[`VERSION.md`](VERSION.md)
