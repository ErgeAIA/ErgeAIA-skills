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

解释、背景、动机、教程、欢迎语一律禁止写入。过程文档模板不受本条约束。

## 1 触发词黑名单（终稿前逐行扫描，命中即删或改写为句式 1-4）

因为 / 所以 / 这是由于 / 通常 / 一般 / 建议 / 旨在 / 用于描述 /
可以理解为 / 简单来说 / 换句话说 / 这意味着 / 我们 / 本文件将 / 为了确保

## 2 路由（写文件前判定一次，并在产物头部注明模式）

只认可观测信号，逐项查证后按下表判定：

| 信号 | 判为「有」的条件 |
| ---- | ---------------- |
| 既有契约 | 项目根存在 AGENTS.md / CLAUDE.md / .cursorrules 之一 |
| 既有代码 | 存在源码目录、依赖清单或锁定文件；或 `git log` 有提交 |
| 既有项目文档 | 存在 PRD / CONTEXT / 设计稿等面向项目的文档 |

| 既有契约 | 既有代码 | 既有项目文档 | 模式 |
| -------- | -------- | ------------ | ---- |
| 无 | 无 | 无 | 全新初始化 |
| 无 | 无 | 有 | 半程合成 |
| 无 | 有 | 任意 | 半程合成 |
| 有 | 任意 | 任意 | 已初始化优化 |

- 全新初始化 → 空仓起建，直接生成
- 半程合成 → 先执行 §3 再生成
- 已初始化优化 → 增量维护，禁止整体重写
- 三个信号互相矛盾或无法查证 → 停下问用户，不自行归类

产物头部写一行 HTML 注释，只填三者之一：`<!-- mode: 半程合成 -->`。**改动这行本身也算一次 AGENTS.md 改动，须留痕。**

判为开源（存在 LICENSE/CONTRIBUTING）→ 层 B 追加许可限制与贡献约定。

## 3 决策保全（半程合成/已初始化优化必做）

1. 摘录既有契约文件全部条目；无契约文件时，摘录代码、提交、配置中可识别的现存约定 → 既有约定清单
2. 逐条四态处置：keep 原样继承 / update 以代码现状为准改写 / drop 删除 / merge 合并去重
3. 铁律：update 与 drop 必须写入层 C 变更日志 `docs/.ai/agents-changelog.md`（旧值 → 处置 → 新值/原因），禁止静默丢失
4. 旧位置残留：旧日志类文件（如项目根 `references/` 下的决策或变更日志）内容合并进新落点，旧文件按 drop 处理并留痕；禁止新旧两处并存

全新初始化跳过四态处置，但仍建 `docs/.ai/agents-changelog.md` 并写一行兜底：`<无旧约定> → 全新初始化 → 直建当前 AGENTS.md`。

## 4 证据采集（只收非可推断事实）

- 目录骨架；一级目录 >12 或单目录 >50 文件 → 分层抽样并标注"已抽样"
- 运行时痕迹：AGENTS.md / CLAUDE.md / .cursorrules / `.claude/` 是否存在
- 工程标识：用户指定优先；否则取依赖清单的 name；再取不到用项目根目录名
- 工具链精确版本及锁定文件
- 安装/测试/lint/构建/部署/运行命令原文（含 flags、环境要求、来源）
- 反直觉约定：非默认布局、自定义命名、专用测试器
- 权限边界：可做 / 需确认 / 禁止
- monorepo → 各子包独立 AGENTS.md，根文件只留全局标准
- **采集不到关键事实**（项目定位、命令、权限边界）→ 停下问用户；用户未答则写占位，并在终止回复列入待确认项，禁止编造

## 4b 项目文档结构生成（与 AGENTS.md 同时产出）

缺口补齐，已存在的一字不动：

````text
<project>/docs/
├── .ai/
│   ├── project-progress.md     # 进度，每次会话更新
│   ├── decision-log.md         # 开发决策，优先级高于 PRD
│   ├── debug-log.md            # bug 记录
│   ├── agents-changelog.md     # AGENTS.md 约定处置，仅初始化/维护时写
│   ├── init-report.md          # 初始化执行报告，每次 init 追加一节
│   └── project-overview.md     # 可选，层 B
└── handoff/                    # 交接文档，handoff-YYYY-MM-DD-*.md
````

各文档按 `assets/docs/` 下同名模板原样复制，替换 `<工程标识>` 并把 `updated` 改为当日：

| 模板 | 落点 | 建立条件 |
| ---- | ---- | -------- |
| `assets/docs/project-progress.md` | `docs/.ai/project-progress.md` | 总是 |
| `assets/docs/decision-log.md` | `docs/.ai/decision-log.md` | 总是 |
| `assets/docs/debug-log.md` | `docs/.ai/debug-log.md` | 总是 |
| `assets/docs/agents-changelog.md` | `docs/.ai/agents-changelog.md` | 总是（全新初始化也建，写兜底行） |
| `assets/docs/init-report.md` | `docs/.ai/init-report.md` | 总是（每次 init 追加一节） |

- `<工程标识>` 取法见 §4；取不到就问用户，不猜
- 模板已含 YAML frontmatter 与"改完必须把 `updated` 改为当日"的约定，不增删字段
- `docs/handoff/` 用空文件 `.gitkeep` 占位，让 Git 追踪空目录
- 同名文件已存在 → 跳过，禁止覆盖，禁止改写历史条目
- 模板中的 `<...>` 占位：初始化时已确知的当场填，未知的原样保留，由首次 `vibe-sync` 补齐
- 层 B `docs/.ai/project-overview.md` **无模板、按需自建**：仅当项目有目录或依赖结构需要索引、且 PRD 未覆盖时建，内容为目录索引、依赖方向、开源附加分析；不需要就不建

## 5 产物模板（严格填空，禁止增删章节）

填充规则：

- `Permissions` 节仅允许 `IMPORTANT:` / `YOU MUST` / `禁止` 开头的行，且必须含文档同步义务
- `References` 只写 `见 <path>` 指针行，用途说明放 `Conventions`
- 占位符指向的文档若项目不存在（如无 PRD）→ **整项删掉，不留空占位**
- 空表保留表头；无命令写占位，不写解释
- `<!-- mode: -->` 只填 §2 判出的那一个值

````markdown
# AGENTS.md

<!-- mode: 全新初始化|半程合成|已初始化优化 -->

## Permissions

IMPORTANT: <一句话项目定位与最硬边界>
YOU MUST 先读 <项目文档，如 PRD.md> 与 docs/.ai/decision-log.md 再改码
YOU MUST 每次会话更新 docs/.ai/project-progress.md
YOU MUST 改 AGENTS.md 前先读、改后追加 docs/.ai/agents-changelog.md
禁止 <P0 范围外的事>
禁止不记录就改动 AGENTS.md 的约定

## Toolchain

| 工具 | 精确版本 | 锁定位置 |
| ---- | -------- | -------- |

## Commands

| 场景 | 命令原文 | 来源 |
| ---- | -------- | ---- |

## Conventions

| 观察到的现象 | 要求 Agent 的行为 |
| ------------ | ----------------- |
| 会话文档体系固定 | 进度写 docs/.ai/project-progress.md；决策写 docs/.ai/decision-log.md；两者只追加不删历史 |
| bug 追加 docs/.ai/debug-log.md | 格式 BUG-NNN；只追加不删历史 |
| 交接写 docs/handoff | 命名 handoff-YYYY-MM-DD-*.md |
| 改 docs/.ai 或 handoff 须同步 updated | 改完立刻把 frontmatter updated 改为当日 |
| 改 AGENTS.md 须留一行变更记录 | 在 docs/.ai/agents-changelog.md 追加「旧值 → 处置 → 去处」，无记录视为静默丢失 |

## References

见 <项目自带文档：PRD.md / CONTEXT.md / docs/adr/ 等，逐条列；无则删本行>
见 docs/.ai/agents-changelog.md
见 docs/.ai/decision-log.md
见 docs/.ai/debug-log.md
见 docs/.ai/project-progress.md
见 docs/handoff/

## Self-Maintenance

<!-- §9 五条原文写入 -->
````

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

另核对（逐条过，缺一不过）：

- `<!-- mode: -->` 只填一个值
- `References` 与 `Permissions` 里出现的**每一条路径**都真实存在
- §4b 各文档已按模板落地且未覆盖既有文件
- `AGENTS.md` 本次若有改动，`docs/.ai/agents-changelog.md` 必须有对应行

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
