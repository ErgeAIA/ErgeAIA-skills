---
name: agents-md-generator
description: 项目初始化生成规范（句式契约、黑名单、路由、决策保全、证据采集、文档结构、产物模板、写入闸、自检门、自维护协议）。执行 vibe-init 时逐字遵循。
trigger-when: 执行 vibe-init 生成或增量维护 AGENTS.md 与过程文档时必读
role: spec
consumed-by: references/init-agents-md.md
---

# Role：项目初始化生成器

## 0 句式契约（最高优先级，逐行强制）

AGENTS.md 每行必须且仅能命中四种句式之一，越界行删除或改写：

1. 命令原文：仅存在于代码块或表格"命令"列
2. 表格行：`场景 | 命令 | 来源` 或 `现象 | 要求行为`
3. 祈使句：动词开头、无主语、≤25 字
4. 指针：`见 <path/章节>` 单行

解释、背景、动机、教程、欢迎语一律禁止写入。§4b 的过程文档骨架不受本条约束。

## 1 触发词黑名单（终稿前逐行扫描，命中即删或改写为句式 1-4）

因为 / 所以 / 这是由于 / 通常 / 一般 / 建议 / 旨在 / 用于描述 /
可以理解为 / 简单来说 / 换句话说 / 这意味着 / 我们 / 本文件将 / 为了确保

## 2 路由（写文件前判定一次，并在产物头部注明模式）

信号：是否已存在 AGENTS.md/CLAUDE.md；提交历史与既有约定规模。

- 全新初始化：无文件、决策负载低 → 直接生成
- 半程合成：无文件、决策负载高 → 先执行 §3 再生成
- 已初始化优化：有文件 → 增量维护，禁止整体重写

产物头部写一行 HTML 注释注明模式：`<!-- mode: 全新初始化|半程合成|已初始化优化 -->`。

判为开源（存在 LICENSE/CONTRIBUTING）→ 层 B 追加许可限制与贡献约定。

## 3 决策保全（半程/已初始化模式必做）

1. 摘录现有 AGENTS.md/CLAUDE.md 全部条目，加代码/提交/配置中可识别约定 → 既有约定清单
2. 逐条四态处置：keep 原样继承 / update 以代码现状为准改写 / drop 删除 / merge 合并去重
3. 铁律：update 与 drop 必须写入层 C 变更日志（旧值 → 处置 → 新值/原因），禁止静默丢失

## 4 证据采集（只收非可推断事实）

- 目录骨架；一级目录 >12 或单目录 >50 文件 → 分层抽样并标注"已抽样"
- 工具链精确版本及锁定文件
- 安装/测试/lint/构建/部署/运行命令原文（含 flags、环境要求、来源）
- 反直觉约定：非默认布局、自定义命名、专用测试器
- 权限边界：可做 / 需确认 / 禁止
- monorepo → 各子包独立 AGENTS.md，根文件只留全局标准

## 4b 项目文档结构生成（与 AGENTS.md 同时产出）

缺口补齐，已存在的一字不动：

````text
<project>/docs/
├── .ai/
│   ├── project-progress.md     # 进度，每次会话更新
│   ├── decision-log.md         # 开发决策，优先级高于 PRD
│   ├── debug-log.md            # bug 记录
│   └── project-overview.md     # 可选，层 B
└── handoff/                    # 交接文档，handoff-YYYY-MM-DD-*.md
````

层 C 变更日志落在项目根的 `references/decision-log.md`。

过程文档一律带 YAML frontmatter：`title` / `type` / `project` / `updated` / `description`；description 内写明"本文件新增或修改后必须把 `updated` 改为当日日期"。骨架如下。

### docs/.ai/project-progress.md

````markdown
---
title: Project Progress
type: project-progress
project: <工程标识>
updated: YYYY-MM-DD
description: >
  项目开发进度实时记录：阶段、分支、代码状态、最近进展。每次会话更新。
  AI 在本文件新增进展或修改当前状态后，必须同步更新 updated 为当日日期（YYYY-MM-DD）。
---

# Project Progress

> 记录当前任务状态、分支和最近进展。每次会话更新。
> 新进展插在「当前状态」之后、旧「最后更新」之前。

---

## 当前状态

- **当前分支**：
- **阶段**：
- **代码**：
- **工具链**：
- **最后更新**：YYYY-MM-DD
- **下一步**：
````

### docs/.ai/decision-log.md

````markdown
---
title: Decision Log
type: decision-log
project: <工程标识>
updated: YYYY-MM-DD
priority: higher-than-prd
description: >
  开发过程决策日志，优先级高于 PRD；冲突时以本文件最新条目为准并回写 PRD/ADR。
  只追加，不删除或改写历史。AI 在本文件新增或修改任何条目后，必须同步更新 updated 为当日日期。
---

# Decision Log

> 偏离 PRD 或做出重要技术选择时在此追加。只追加，不删除或改写历史。
> **优先级高于 PRD**：冲突时以本文件最新决策为准，并回写 PRD/ADR。
> 格式：`## DEC-NNN: 标题` + 日期/背景/决策/验证。

---
````

### docs/.ai/debug-log.md

````markdown
---
title: Debug Log
type: debug-log
project: <工程标识>
updated: YYYY-MM-DD
description: >
  反复调试的 bug 记录。只追加，不删除或改写历史。
  AI 在本文件新增或修改任何条目后，必须同步更新 updated 为当日日期。
---

# Debug Log

> 反复调试的 bug 记录。只追加，不删除历史。
> 格式：`## BUG-NNN: 标题` + 日期/现象/根因/修复/验证限制/教训。

---
````

### docs/handoff/.gitkeep

空文件，让 Git 追踪空目录。

### references/decision-log.md（层 C）

````markdown
# Decision Log — AGENTS.md

模式：<全新初始化|半程合成|已初始化优化>
来源文件：<旧 AGENTS.md/CLAUDE.md 路径>

## Layer C

<旧值> → keep|update|drop|merge → <新值/去处/原因>
````

## 5 产物模板（严格填空，禁止增删章节）

填充规则：

- `Permissions` 节仅允许 `IMPORTANT:` / `YOU MUST` / `禁止` 开头的行，且必须含文档同步义务
- `References` 只写 `见 <path>` 指针行，用途说明放 `Conventions`
- 空表保留表头；无命令写占位，不写解释
- `<!-- mode: -->` 行保留

````markdown
# AGENTS.md

<!-- mode: 全新初始化|半程合成|已初始化优化 -->

## Permissions

IMPORTANT: <一句话项目定位与最硬边界>
YOU MUST 先读 PRD 与 docs/.ai/decision-log.md 再改码
YOU MUST 每次会话更新 docs/.ai/project-progress.md
禁止 <P0 范围外的事>

## Toolchain

| 工具 | 精确版本 | 锁定位置 |
| ---- | -------- | -------- |

## Commands

| 场景 | 命令原文 | 来源 |
| ---- | -------- | ---- |

## Conventions

| 观察到的现象 | 要求 Agent 的行为 |
| ------------ | ----------------- |
| 会话文档体系固定 | 进度写 docs/.ai/project-progress.md；决策写 docs/.ai/decision-log.md |
| bug 追加 docs/.ai/debug-log.md | 格式 BUG-NNN；只追加不删历史 |
| 交接写 docs/handoff | 命名 handoff-YYYY-MM-DD-*.md |
| 改 docs/.ai 或 handoff 须同步 updated | 改完立刻把 frontmatter updated 改为当日 |

## References

见 docs/.ai/decision-log.md
见 docs/.ai/debug-log.md
见 docs/.ai/project-progress.md
见 docs/handoff/

## Self-Maintenance

<!-- §9 五条原文写入 -->
````

层 B（可选）`docs/.ai/project-overview.md`：目录索引、依赖方向、开源附加分析。

## 6 写入闸（每行过闸，不过闸不写入）

1. 非可推断：删掉此行 Agent 会犯错吗？不会 → 删
2. 去重：README/清单/配置已有 → 换指针，禁止复述
3. 无密钥、无时效信息（sprint/人员/feature flag）

## 7 自检门（草稿 → 扫描 → 终稿；五项全过才输出）

1. 逐行核对句式四选一
2. 逐行扫描 §1 黑名单词
3. 逐行执行 §6 写入闸
4. 行数：目标 ≤250，硬上限 500；近 300 未写尽 → 裁剪，超 500 → 拆层 B 或下沉子包
5. 标题语言全文件统一；命令/路径/版本保持英文原文

另核对：`References` 指针逐条真实存在；`docs/.ai` 与 `docs/handoff` 缺口已补齐且未覆盖既有文件。

## 8 坏行 → 好行对照（唯一示例，生成时模仿右列）

坏：测试使用 vitest，因历史原因未用 jest，注意缓存问题
好：Commands 行 `| 测试 | pnpm test | package.json |`；Conventions 行 `| 测试器为 vitest 非 jest | 直接运行 pnpm test，勿引入 jest |`
坏：我们采用 pnpm 作为包管理器，为了保证 workspace 一致性
好：Toolchain 行 `| 包管理 | pnpm@9 | pnpm-lock.yaml |`；Permissions 行 `YOU MUST 使用 pnpm，禁止 npm/yarn/bun 安装依赖`

## 9 自维护协议（原文写入产物 Self-Maintenance 节）

1. 改变规则的 PR 须同步改本文件，否则视为规则漂移
2. 规则写入错误发生处最近作用域，monorepo 进对应子包
3. 命令更名、重构后，提交前核对本文件并更新过期示例
4. 随发布或固定周期清除失效条目
5. 本文件修改走 PR/Review，与代码同等纪律
