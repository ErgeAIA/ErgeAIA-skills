# vibe-buddy 版本记录

> 只记录版本号、核心变更与修改文件。设计取舍见 README，生成规范见 references。

---

## v1.0.0 (2026-09-10)

### 初始版本

**定位**：通用的项目 AI 协作记忆管理技能，读写项目根 `AGENTS.md`、`docs/.ai/` 与 `docs/handoff/`，不绑定任何 IDE 或运行时。

**五个触发词**

| 触发词 | 职责 | 产物 |
|---|---|---|
| `vibe-init` | 建立协作契约与过程文档；半程项目只补缺失项 | `AGENTS.md`、`CLAUDE.md`（可选）、`docs/.ai/` 三件套、`docs/handoff/` |
| `vibe-sync` | 沉淀进度与决策 | `docs/.ai/project-progress.md`、`docs/.ai/decision-log.md` |
| `vibe-handoff` | 生成自包含交接文档 | `docs/handoff/handoff-YYYY-MM-DD.md` |
| `vibe-resume` | 只读并结构化汇报 | 无 |
| `vibe-distill` | 沉淀 bug 根因与预防规则 | `docs/.ai/debug-log.md` |

**过程文档模型**

- `docs/.ai/project-progress.md`：进度，每次会话更新；任务开始时先读它。
- `docs/.ai/decision-log.md`：开发决策（`DEC-NNN` 三位，优先级高于 PRD，冲突时旧条目标 `superseded`）+ 层 C 小节 `## Layer C — AGENTS.md 约定处置`（一行一条 `旧值 → 处置 → 新值/去处/原因`）。
- `docs/.ai/debug-log.md`：bug 记录；编号 `BUG-NNN`（三位）递增，含现象/根因/修复/验证限制/教训。
- `docs/handoff/`：交接文档，命名 `handoff-YYYY-MM-DD-*.md`。
- 三件套模板外置在 `assets/docs/`（`project-progress.md` / `decision-log.md` / `debug-log.md`），初始化时原样复制，只替换 `<工程标识>` 并把 `updated` 改为当日；§4b 不再内联骨架，消除模板与文档两处漂移。
- 所有过程文档带 YAML frontmatter（`title` / `type` / `project` / `updated` / `description`），**每次修改须把 `updated` 同步为当日**。
- 全部**只追加**，历史条目永不删除或改写。层 C 不另立文件：项目只应有一个决策日志真源。

**状态识别（初始态 vs 开发中）**

- 旧判据「决策负载低/高」不可观测、无法判定，已废除。
- 改用三个可观测信号查表定模式：既有契约（AGENTS.md / CLAUDE.md / .cursorrules）、既有代码（源码目录 / 依赖清单 / 锁定文件 / 有提交）、既有项目文档（PRD / CONTEXT / 设计稿）。任一为「有」即排除全新初始化。
- 信号矛盾或无法查证 → 停下问用户，不自行归类。判据真源在生成规范 §2，init 契约只留动作列，避免两处漂移。

**AGENTS.md 契约强化**

- 章节固定不增删；产物头部写 `<!-- mode: 全新初始化|半程合成|已初始化优化 -->` 注明路由模式。
- 文档义务落在既有两节：`Permissions` 写 `YOU MUST 每次会话更新 docs/.ai/project-progress.md`；`Conventions` 写会话文档体系、bug 追加、交接命名、改文档须同步 `updated` 四条表格行。
- `References` 只写 `见 <path>` 纯指针，用途说明归 `Conventions`。
- 生成规范新增 §4b「项目文档结构生成」，承载目录结构与各文档骨架（单一真源）。
- 生成规范内的模板用 4 反引号围栏承载，避免嵌套代码块渲染异常。

**核心契约**

- 不覆盖（只追加 / 命名递增或加语义后缀）、不猜测（读不到写占位符）、不越界（只碰契约与过程文档区）、不静默（删除或改写留可见记录）。
- 先确认再执行；写入前声明操作类型 / 路径 / 是否覆盖 / 风险等级；一次只走一个触发词。
- 全程不运行终端命令；产物强制脱敏；不重复已有产物，一律用路径引用。

**设计取舍**

- 触发词从早期的 9 个收敛为 5 个：合并「保存进度 + 会话压缩」（写同一文件同一位置），「记录踩坑」并入调试经验沉淀，移除低频的「知识整合」与旧「初始化后同步」入口。
- 进度与决策不进 `AGENTS.md`：契约只承载规则，过程只承载事实。
- 完全移除 OpenSpec 及其兼容设计（规范源三模式、优先级链）。
- 移除状态文件与并行工作流目录：不再维护 `.workflow-state.json`；路由只保留 SKILL.md 一张决策矩阵表。
- `CLAUDE.md` 定位为指针而非副本。
- 交接机制继承 `handoff` 参考实现的四项契约：自包含、不重复已有产物、强制脱敏、含建议调用的技能段。

**修改文件**：全部新建 —— `SKILL.md`、`README.md`、`VERSION.md`、`references/init-agents-md.md`、`references/agents-md-generator.md`、`references/sync-progress.md`、`references/handoff-context.md`、`references/resume-context.md`、`references/distill-lessons.md`、`references/trigger-test-set.md`
