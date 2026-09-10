# vibe-buddy 版本记录

> 只记录版本号、核心变更与修改文件。设计取舍见 README，生成规范见 references。

---

## v1.0.0 (2026-09-10)

### 初始版本

**定位**：通用的项目 AI 协作记忆管理技能，读写项目根 `AGENTS.md` 与 `docs/.ai/`，不绑定任何 IDE 或运行时。

**五个触发词**

| 触发词 | 职责 | 产物 |
|---|---|---|
| `vibe-init` | 建立协作契约与记忆骨架 | `AGENTS.md`、`CLAUDE.md`（可选）、`docs/.ai/*.md` |
| `vibe-sync` | 沉淀稳定增量 | `docs/.ai/progress.md`、`docs/.ai/decisions.md` |
| `vibe-handoff` | 生成自包含交接文档 | `docs/.ai/handoffs/YYYYMMDD-NN.md` |
| `vibe-resume` | 只读并结构化汇报 | 无 |
| `vibe-distill` | 沉淀可复用经验与踩坑 | `docs/.ai/lessons.md` |

**核心契约**

- 不覆盖（仅追加 / 序号递增）、不猜测（读不到写占位符）、不越界（只碰契约与记忆区）、不静默（删除或改写留可见记录）。
- 先确认再执行；写入前声明操作类型 / 路径 / 是否覆盖 / 风险等级；一次只走一个触发词。
- 全程不运行终端命令；产物强制脱敏；不重复已有产物，一律用路径引用。

**设计取舍**

- 触发词从原型的 9 个收敛为 5 个：合并「保存进度 + 会话压缩」（写同一文件同一位置），「记录踩坑」并入经验蒸馏（本属同类），移除低频的「知识整合」与旧「项目初始化后同步」入口。
- 进度与任务计划不进 `AGENTS.md`：契约只承载规则；计划交由计划类技能。
- 完全移除 OpenSpec 及其兼容设计（规范源三模式、优先级链）。
- 移除状态文件与并行工作流目录：不再维护 `.workflow-state.json`；路由信息只保留 SKILL.md 一张决策矩阵表。
- `CLAUDE.md` 定位为指针而非副本，避免与原契约漂移。
- 交接机制继承 `handoff` 参考实现的四项契约：自包含、不重复已有产物、强制脱敏、含建议调用的技能段。

**修改文件**：全部新建 —— `SKILL.md`、`README.md`、`VERSION.md`、`references/init-agents-md.md`、`references/agents-md-generator.md`、`references/sync-progress.md`、`references/handoff-context.md`、`references/resume-context.md`、`references/distill-lessons.md`、`references/trigger-test-set.md`
