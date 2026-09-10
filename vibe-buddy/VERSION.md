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

- `project-progress.md`：进度，实时更新；任务开始时先读它。
- `decision-log.md`：决策日志，优先级高于 PRD；编号 `DEC-NN`，冲突时旧条目标 `superseded`。
- `debug-log.md`：bug 修复经验；编号 `BUG-NN`，编号递增。
- 三类文档**只追加**，历史条目永不删除或改写。

**AGENTS.md 契约强化**

- 层 A 模板新增 `## References`（四类文档指针，写明用途）与 `## 收尾同步`（每完成一次任务必须更新哪些文档、未同步不得声称完成）。
- 生成规范的原 §5 模板用 4 反引号围栏承载，避免嵌套代码块渲染异常。

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
