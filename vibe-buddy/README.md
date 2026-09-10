# vibe-buddy

> 给项目装上可审计的 AI 协作记忆：规则写进 `AGENTS.md`，进度与决策落在 `docs/.ai/`，会话交接落在 `docs/handoff/`。

## 它解决什么问题

每次新会话，AI 都要重新问一遍"这个项目用什么命令、有什么坑、上次做到哪了"。把它答完，上下文也用掉了一半。

vibe-buddy 把这些答案固化成文件：

- **契约** —— `AGENTS.md`：能做什么、用什么命令、遵守什么约定，以及每完成一次任务要同步哪些文档，每次会话自动加载。
- **进度与决策** —— `docs/.ai/`：进度实时更新，决策日志优先级高于 PRD，bug 根因单独归档，只追加不改写。
- **交接** —— `docs/handoff/` 下一份自包含文档，另一个 agent 不读历史对话就能接手。

## 五个触发词

| 触发词 | 说什么 | 做什么 |
|---|---|---|
| `vibe-init` | 初始化项目 / 生成 AGENTS.md | 建立 `AGENTS.md`、`docs/.ai/` 各过程文档与 `docs/handoff/`；半程项目先做决策保全，再只补齐缺失文档 |
| `vibe-sync` | 同步进度 / 更新项目进度 | 把任务状态、验证结果写进 `project-progress.md`，决策追加到 `decision-log.md` |
| `vibe-handoff` | 交接上下文 / 写交接文档 | 生成 `docs/handoff/handoff-YYYY-MM-DD.md`，含未提交改动、待办与建议调用的技能 |
| `vibe-resume` | 接管项目 / 接手上下文 | 只读项目记忆，结构化汇报现状，然后停下等指令 |
| `vibe-distill` | 经验蒸馏 / 沉淀经验 | 把已定位根因的 bug 与预防规则追加到 `debug-log.md` |

也支持自然语言触发，例如「上下文快满了，写个交接文档给下一个会话」。

**不提供斜杠命令**：全部通过触发词或显式技能调用完成。

## 产物布局

```
项目根/
├── AGENTS.md                        # 规则契约（六节固定，含文档义务与指针）
├── CLAUDE.md                        # 可选，指向 AGENTS.md 的指针
└── docs/
    ├── .ai/
    │   ├── project-progress.md      # 项目进度，每次会话更新；任务开始时先读它
    │   ├── decision-log.md          # 决策日志，优先级高于 PRD；随开发持续更新
    │   ├── debug-log.md             # bug 修复经验，编号递增
    │   ├── agents-changelog.md      # AGENTS.md 变更记录，只在契约改动时写
    │   └── project-overview.md      # 可选，目录索引与依赖方向
    └── handoff/                     # 会话交接文档
        └── handoff-YYYY-MM-DD-*.md
```

过程文档均带 YAML frontmatter；**每次修改都要把 `updated` 改成当日**。前三份随开发持续更新；`agents-changelog.md` 只在 `AGENTS.md` 变更时写入，且**每次变更必须追加一行——无记录视为静默丢失**。

`docs/.ai/` 三类文档**只追加**：决策冲突时旧条目改标 `superseded`，历史条目永不删除或改写。

## 设计取舍

| 取舍 | 原因 |
|---|---|
| 触发词只有 5 个 | 早期版本的 9 个里，「保存进度 / 会话压缩」写同一文件同一位置，「记录踩坑」本是进度同步的子类，「知识整合」只在积累多份经验后才有意义。合并后每个触发词职责唯一，路由无歧义 |
| 进度与决策不进 `AGENTS.md` | 契约只承载规则，过程只承载事实。混在一起会让契约每轮被改写，既不稳定也不可审计 |
| 文档义务写进 `Permissions` 与 `Conventions` | 不写进 `AGENTS.md` 就没人执行；但不新增章节——章节固定，义务落在既有两节里，句式契约才守得住 |
| 过程文档只追加 | 决策与 bug 记录是审计线索；改写历史会让后来的 agent 读到不自洽的结论 |
| 文档命名沿用既有实践 | `project-progress` / `decision-log` / `debug-log` 三件套与 `handoff/` 目录的组织方式与成熟项目保持一致，降低迁移成本 |
| `CLAUDE.md` 是指针不是副本 | 整份复制会在两轮维护后与 `AGENTS.md` 漂移 |
| 不做任务计划 | 待办拆解与排期是计划类技能的正业，塞进来只会让边界模糊 |
| 不兼容规范体系 | 规格生命周期有专门的体系负责；本技能只管记忆与交接，保持单一职责 |
| 全程不运行终端命令 | 本技能只做文件读写。构建、测试、Git 交给用户或专门的技能 |

## 与相邻技能的边界

- **需求转译**：模糊需求 → 结构化 PRD，交给需求侧技能。
- **任务计划**：待办拆解、排期、进度追踪，交给计划类技能。
- **Git 操作**：提交、分支、合并，交给 Git 类技能。
- **文档写作**：README、设计稿等面向人类的文档，交给写作类技能。
- **规格管理**：规格与变更的生命周期，交给对应的规范体系。

## 目录结构

```
vibe-buddy/
├── SKILL.md                              # 入口：路由与共用契约
├── README.md                             # 本文件
├── VERSION.md                            # 版本演进
├── assets/
│   └── docs/                             # 过程文档模板，初始化时原样复制
│       ├── project-progress.md
│       ├── decision-log.md
│       ├── debug-log.md
│       └── agents-changelog.md
└── references/
    ├── init-agents-md.md                 # 初始化执行契约
    ├── agents-md-generator.md            # 生成规范（句式契约 / 自检门 / 文档结构）
    ├── sync-progress.md                  # 进度与决策沉淀契约
    ├── handoff-context.md                # 交接文档契约
    ├── resume-context.md                 # 接管汇报契约
    ├── distill-lessons.md                # 调试经验沉淀契约
    └── trigger-test-set.md               # 触发回归测试集
```

## 版本

当前版本：**v1.0.0**，详见 [VERSION.md](VERSION.md)。
