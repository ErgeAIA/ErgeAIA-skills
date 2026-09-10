---
name: agents-md-generator
description: AGENTS.md 生成规范（句式契约、黑名单、路由、决策保全、证据采集、产物模板、写入闸、自检门、自维护协议）。生成或维护 AGENTS.md 时逐字执行。
trigger-when: 执行 vibe-init 生成或增量维护 AGENTS.md 时必读
role: spec
consumed-by: references/init-agents-md.md
---

# Role：AGENTS.md 生成器

## 0 句式契约（最高优先级，逐行强制）

产物每行必须且仅能命中四种句式之一，越界行删除或改写：

1. 命令原文：仅存在于代码块或表格"命令"列
2. 表格行：`场景 | 命令 | 来源` 或 `现象 | 要求行为`
3. 祈使句：动词开头、无主语、≤25 字
4. 指针：`见 <path/章节>` 单行

解释、背景、动机、教程、欢迎语一律禁止写入。

## 1 触发词黑名单（终稿前逐行扫描，命中即删或改写为句式 1-4）

因为 / 所以 / 这是由于 / 通常 / 一般 / 建议 / 旨在 / 用于描述 /
可以理解为 / 简单来说 / 换句话说 / 这意味着 / 我们 / 本文件将 / 为了确保

## 2 路由（写文件前判定一次，产物头部注明模式）

信号：是否已存在 AGENTS.md/CLAUDE.md；提交历史与既有约定规模。

- 全新初始化：无文件、决策负载低 → 直接生成
- 半程合成：无文件、决策负载高 → 先执行 §3 再生成
- 已初始化优化：有文件 → 增量维护，禁止整体重写

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

## 5 产物模板（严格填空，禁止增删章节）

层 A 根 AGENTS.md：

````markdown
# AGENTS.md

## Permissions

<!-- IMPORTANT: / YOU MUST 开头，置顶，仅此节允许这两个标识 -->

## Toolchain

| 工具 | 精确版本 | 锁定位置 |
| ---- | -------- | -------- |

## Commands

| 场景 | 命令原文 | 来源 |
| ---- | -------- | ---- |

## Conventions

| 观察到的现象 | 要求 Agent 的行为 |
| ------------ | ----------------- |

## References

- 见 docs/.ai/project-progress.md 项目进度，实时更新
- 见 docs/.ai/decision-log.md 决策日志，优先级高于 PRD
- 见 docs/.ai/debug-log.md bug 修复经验
- 见 docs/handoff/ 会话上下文交接

## 收尾同步

- 更新 docs/.ai/project-progress.md 的任务状态与验证结果
- 决策变化时在 docs/.ai/decision-log.md 顶部追加条目
- 修复 bug 后在 docs/.ai/debug-log.md 追加条目
- 禁止在未同步上述文档时声称任务完成

## Self-Maintenance

<!-- §9 五条原文写入 -->
````

层 B（可选）references/project-overview.md：目录索引、依赖方向、开源附加分析。

层 C 决策变更日志（半程/已初始化必交付）：一行一条 `旧值 → keep/update/drop/merge → 新值/原因`。

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
