---
name: "W-SYNC 版本同步"
description: "REA 升级后用原始材料判漂移、给每个新工具做意图判定，再重生成版本化工具表并完成四处版本对齐。"
version: 1.1.0
trigger-when: REA 升级、工具清单对不上、或 toolset 文件版本与本机 version 不一致时
reads-from: SKILL.md, references/specs/toolset-generation.md, references/config/intent-routing.md
writes-to: references/toolset/rea-<新版本>.md, references/config/intent-routing.md, SKILL.md 资源表, CHANGELOG.md, 根 README 双语
---
# @工作流: W-SYNC 版本同步

W-SYNC 不是「重抄一遍工具表」。它要回答三件事：**上游变了什么 → 这些变化该不该改本技能 → 怎么让下次升级一命令判漂移**。

## @步骤1: 取原始事实（不许从变更日志倒推）

```bash
rea --version                                      # 版本锚；本机装什么就是什么
npm view rea-agents version                         # registry 最新版
npm view rea-agents time --json                     # 发版节奏
npm root -g                                         # 包根；读 package.json 与 dist/mcp-catalog.json
rea doctor --format json                            # 注册、scope、installations
rea mcp doctor --json                               # 工具/ prompt 计数与目录摘要
rea capabilities --format json                      # provider 可用性、副作用、catalog 摘要
rea --llms                                          # CLI 命令面
```

变更日志（本机 IWR/官方 raw 均可）：<https://raw.githubusercontent.com/morluto/rea/main/CHANGELOG.md>。标题新旧格式都要认：旧 `## 6.7.0 (2026-10-18)`，新 `## [6.10.1]` + compare 链接 + ` (2026-11-20)`。先看 **Highlights / Changes**，再看 Fixes；日志只用于**解释**已经从原始面看到的 delta，不替代实测。

版本陷阱：tag ≠ npm 发布；只认本机 `rea --version` 与已装包 `package.json`。

## @步骤2: 一命令判漂移

```bash
python scripts/check_rea_drift.py --base references/toolset/rea-<当前快照版本>.md --format md
# 或 --format json 供程序化处理；退出码 0=无漂移 1=有漂移 2=错误
```

脚本只做机械 diff：新增/删除/改名候选、同名描述变化、副作用标签变化、CLI 增删改、版本与目录摘要变化。**语义判断由人/模型做，不由正则或行数做**。

| 脚本输出 | 动作 |
| --- | --- |
| exit 0 | 只贴计数与摘要，结束；不重生成 |
| exit 1 且只有描述改写 / 计数不变 | 抽查低相似度项，必要时改 Gotchas/参考说明；不无脑重生成 |
| exit 1 且有工具/CLI 增删改、摘要变化、版本变化 | 进入 @步骤3 逐项意图判定，然后重生成快照 |
| exit 2 | 修命令/路径/包根后重跑；不得把错误当「无漂移」 |

## @步骤3: 每个新工具都要做意图判定（核心）

对脚本列出的**每一个**新增 MCP 工具，按 `references/config/intent-routing.md` 的格式回答四问：

1. **它是什么**：读 `mcp-catalog.json` 的完整 description（不是快照里的截断句）与副作用/前置。
2. **用户会怎么说**：写 1–3 条真实意图句（例：「这个 PE 开了哪些加固？」）。
3. **本技能该不该接管**：三选一 —— `ROUTE_AND_CALL`（本技能按意图直接调 MCP）/ `REFERENCE_ONLY`（只更新工具面快照，交给 REA 自带技能）/ `OUT_OF_SCOPE`（明确不碰）。
4. **落点**：`ROUTE_AND_CALL` 必须写进 `references/config/intent-routing.md`，必要时同步改对应工作流与 SKILL.md 资源表；其它两类也要在该文件留一行「已评估、不接管」及原因，避免下次重复讨论。

禁止：只把新工具名字塞进快照就叫「适配完」。**没做意图判定的新增工具 = 本技能触发面有洞**。

## @步骤4: 重生成工具面快照

按 `references/specs/toolset-generation.md` 执行（命令、列口径、分组、版本锚都在那里）。要点：

- 输入是四样，不是三样；MCP 侧直接读包内 catalog，不自起 stdio server。
- **不手改**生成出来的文件；要改口径就改生成规范。
- 旧版本文件**保留**，用于回溯「当时这个工具叫什么」。
- 自检等式：`rea mcp doctor` tools expected==observed == catalog.counts.mcp_tools == 分组总数；CLI 命令数与 prompt 数一致；目录摘要与 capabilities 一致。

## @步骤5: 同步其它受影响文件

- 新工具属 `ROUTE_AND_CALL` → 更新 `intent-routing.md` + 对应工作流（W-ROUTE / W-HARDEN / W-INSTALL 等）+ SKILL.md 资源表。
- 上游改了 setup / mcp add / doctor 的参数或输出结构 → 更新 `install-and-verify.md` / `host-registration.md` / `mcp-registration-fields.md`，并标出「入口以当前版本 `--help` 为准」。
- 引擎版本/外部工具前置变了（如 Ghidra 12.2、Kuna 1.1000、Node engines）→ 更新 `engines-and-providers.md`，仍写判据，不写死会过期的本机绝对值。
- 只改本技能的 CHANGELOG（按 changelog-manager 规范进 `[Unreleased]`）；**不因为一次提交就升版**（版本与提交解耦，切发布才四处对齐）。

## @步骤6: 版本与回执

四处版本对齐只在**切发布**时做：`SKILL.md` frontmatter → 技能 CHANGELOG 顶部版本 → 子库 README 双语索引 → 技能 README 版本行。

| 位置 | 内容 |
| --- | --- |
| `SKILL.md` frontmatter | `metadata.version` |
| 根 `CHANGELOG.md` | 顶部最新版本条目 + 技能索引 |
| 根 `README.md` / `README.en.md` | 技能索引行的版本列 |
| 本技能 `README.md` 末尾 | 「当前版本：**vX.Y.Z**」 |

另外：本技能 `CHANGELOG.md` 追加一条「工具面同步到 <版本>：新增 N / 删除 M / 改名 K」。

@验证点：交付必须贴出 ① `rea --version`/registry 最新版本 ② 脚本退出码与 delta 计数 ③ 每个新增工具的意图判定结论 ④ 重生成后的计数与摘要自检 ⑤ 当前会话工具列表与 CLI 工具面是否一致（注册 `package_reference` 是否等于 `rea --version`，不一致先按 W-INSTALL 验证，不许假装已能调用） ⑥ 若未升版，明确写「版本未动，条目进 `[Unreleased]`」。缺任一项不许收尾。
