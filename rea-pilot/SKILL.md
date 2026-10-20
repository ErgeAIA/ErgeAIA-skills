---
name: rea-pilot
description: "把 REA（逆向工程与证据分析工具）装进用户当前的编程助手并让它真正连接可用，再按目标给出逆向选路、卸载回滚与加固建议。Use when 用户要安装或配置 REA、把它接到自己的 Agent 或 MCP 宿主、检查环境与连接是否正常、更新或卸载它、想知道某个逆向目标该走哪条最小路径，或要给自己拥有的应用补加密、混淆、加壳与完整性防护。Not for: 目标已连上后会话内怎么用 REA 调查（交 REA 自带技能 reverse-engineer-anything）、纯源码仓库的架构分析。"
metadata:
  author: ErgeAIA
  version: "1.0.2"
---

# rea-pilot

## 定位

REA（<https://rea.tools/>）自带技能 `reverse-engineer-anything` 已经占了「会话里怎么用 REA 干活」。本技能只占它**前面和外面**：

| 谁 | 管什么 |
| --- | --- |
| REA 自带技能 | 目标已连上后，用哪条命令取哪类证据、怎么解释证据 |
| **rea-pilot（本技能）** | 装好 → 接上 → 验证 → 选路 → 排障 → 回滚，外加官方没有的**加固建议** |

一句话：**引航员——登你的船、把船引进港、出港即离，不替你开船。**

Core Task：

```text
用户要装/接/验/更/卸 REA，或问「我该怎么逆向」「我该怎么加固」时：
  先判归属（装接类 / 用 REA 类）→ 按决策矩阵进唯一一条工作流文件
  → 全程守硬规则：改配置前先出计划、不确认不执行、结论必须带实测输出。
```

## 何时使用

这就是**唯一的路由表**（一次只进一条，不并列）：

| 用户说 | 工作流 | 读这个文件 |
| --- | --- | --- |
| 装 REA / 接到我的助手 / 配 MCP / 看看装好没 | W-INSTALL 接入与验证 | `references/workflows/install-and-verify.md` |
| 我的助手不在官方列表 / setup 没识别到我的宿主 | W-HOST 宿主自接入 | `references/workflows/host-registration.md` |
| 我要逆这个文件（App / 网站 / 固件），该怎么下手 | W-ROUTE 目标选路 | `references/workflows/route-target.md` |
| 我该怎么给自己的应用加密、加壳、防逆向 | W-HARDEN 逆向反推防护 | `references/workflows/hardening-advice.md` |
| REA 升级了 / 工具对不上 / 要刷新工具清单 | W-SYNC 版本同步 | `references/workflows/version-sync.md` |
| 卸载 REA / 装坏了要还原 | W-ROLLBACK 回滚 | `references/workflows/rollback.md` |

表里六条都是工作流。「REA 有哪些工具 / 某个能力能干什么」不是工作流，不进本表——按下面「资源」节的工具面快照回答，先比对本机 `rea --version`。

Not for：
- 目标已接上后的具体调查步骤与证据解释 —— 读 REA 自带技能，本技能不重写调查方法。
- 纯源码仓库的架构阅读与重构 —— 那不需要 REA。
- 未授权资产的破解、绕过他人保护、真实密钥提取。

## 工作步骤

### 步骤 1：路由

先答三问，再按上节「何时使用」的路由表进**唯一一条**工作流文件（一次只进一条，不并列）：

1. 用户要的是「装/接/验/更/卸」还是「用 REA 做事」？
2. 会改本机已有配置吗？（会 → 必须先出计划 + 等确认）
3. 目标是用户自己拥有或已获授权的资产吗？

一条请求含多个意图时（例：「装好没 + 能不能做原生反编译」）：**主路由完整跑完**，其它意图只在需要前置判定时引用对应工作流的对应小节，并写明引用了哪条、为什么——仍不并列展开两条工作流。

### 步骤 2：守硬规则（不读文件也要守）

🔴 CHECKPOINT（每条都是停点，停住等人）：

- `rea setup`（含 `--yes`）、`rea mcp add`、`rea uninstall`、`--purge-data`：先跑 `--dry-run` 把人读计划原样给人，**等明确同意**再执行。
- 引擎安装（`--install-hopper`）与引擎环境变量：先说清装什么、装到哪、谁下载。REA 不下载 JADX / Kuna。
- 有真实副作用的工具调用（Frida 插桩、`capture_*` 场景、adb 安装/推送/启停、调试器会话）：先说明它会动什么、怎么收尾。

🛑 STOP 条件：

- 用户未确认就问「装好了吗」→ 先跑三问验证，不许口头保证。
- 加固建议要落到具体项目而资产归属不明 → 先确认所有权。
- 本文档与官方命令实测输出冲突 → 以实测为准，并触发 W-SYNC。

### 步骤 3：交付可核对回执

每条工作流结束都要给「命令 + 原始输出要点」，格式见各文件的 `@验证点`。禁止只给结论。

回执长这样（值是**示意**，实际一律以本机实测输出为准）：

```text
① 命令：rea mcp doctor --json
   输出要点：healthy=true；tools expected=207 observed=207；missing/unexpected/duplicates 全空
② 命令：rea doctor --format json
   输出要点：registrations[] 里 <宿主 id> → state="aligned"，package_reference="rea-agents@<版本>"
③ 重启宿主后：工具列表里出现 mcp__rea__<tool>

结论：三问全绿 / 卡在第几问（附原始错误）
未做与未验证：<明确列出，不省略>
```

## 输出契约

| 工作流 | 必须产出 |
| --- | --- |
| W-INSTALL | 环境体检结论（按 classification 分流）+ 人读安装计划（改哪些文件、备份在哪）+ 执行结果 + 三问验证回执 |
| W-HOST | 只给通用字段与探索提示词，**由宿主 Agent 自己插入自己的配置**；再给重启后的验证方法 |
| W-ROUTE | 目标类型 → 证据需求 → 引擎前置 → 最小路径命令；无引擎时给替代路径 |
| W-HARDEN | 通用方法论（算法/密钥/完整性/混淆/加壳/运行时）→ 该项目该补哪几层 → 每条给代价与 REA 复跑验收判据 |
| W-SYNC | 新的 `references/toolset/rea-<版本>.md` + 指向更新 + 四处版本对齐 |
| W-ROLLBACK | 取证 → 卸载 → 还原三步 + 为什么这么做 |

失败或卡住时报告：卡在哪一步、原始错误、已试方案、未验证范围。

## 约束

**HARD**

- 版本锚只能来自实测：`rea --version`、`rea doctor --format json`、`rea mcp doctor --json`、`rea --llms`。禁止凭记忆报版本、工具数、配置路径。
- 工具清单只从 `references/toolset/rea-<当前版本>.md` 取；该文件缺失或版本不等于本机 `rea --version` → 先跑 W-SYNC 重新生成。
- 「连上了」必须三问分开答：① `rea mcp doctor --json` healthy；② `rea doctor --format json` 里该注册 `state=aligned`；③ **重启宿主后**工具真的出现在工具列表里。doctor 通过 ≠ 会话已连上。
- 改用户已有配置文件前必须先出计划；计划里没有备份路径的改动禁止执行。
- 「加固建议」= 逆向反推防护：只服务用户自己拥有或已授权的资产；不输出真实密钥或凭据值；不承诺「不可破解」；不提供绕过他人保护的方法。

**CONDITIONAL**

- 缺分析引擎（`missing_analysis_engine`）时：JavaScript/Electron、归档与包、Android 清单、已保留证据类工作仍可做；固件与抓包类需要 Linux 与外部工具。
- 宿主在 REA 的客户端适配器里（判据 = `rea doctor --format json` 的 `identity.registrations[]` 里存在该宿主 id 且 `state=aligned`）→ 直接走 W-INSTALL；只有 REA 没有适配器、或注册不上时 → 走 W-HOST。`scope_checks` 里的 `registration:<client>` 只是**未对齐子集**，别当完整清单。适配器条数与具体客户端以本机实测为准，别引用别处的快照。
- 引擎由用户自备（Ghidra / IDA / JADX / Kuna / tshark 等）时，给环境变量名与官方要求，别替用户下载。

**禁止**

- 禁止未获确认就 `--yes`；禁止把 `--yes` 写成默认参数。
- 禁止在本技能里手抄工具清单（官方近 30 天发 13 个版本，手抄会立刻过期）。
- 禁止替宿主枚举或猜测 MCP 配置路径与格式。
- 禁止把 200+ 工具全量塞进 SKILL.md。

## 资源

六条工作流文件的入口在「何时使用」路由表（不在此重复）；下面只列非工作流的参考文件：

| 何时读 | 文件 | 用途 |
| --- | --- | --- |
| 要工具名 / 用途 / 副作用，或问「REA 有哪些工具 / 某个能力能干什么」 | `references/toolset/rea-<版本>.md`（`<版本>` = 本机 `rea --version`；现有 6.7.0） | 完整工具面（MCP 工具 / 官方 prompt / CLI 命令，逐条含用途与副作用）；条数不在此照抄，以本机实测为准 |
| 要写宿主 MCP 配置 | `references/specs/mcp-registration-fields.md` | 通用字段 + 探索提示词 + 校验动作 |
| 要重新生成工具表 | `references/specs/toolset-generation.md` | 生成命令、列口径、版本锚 |
| 要引擎与 Provider 前置 | `references/config/engines-and-providers.md` | 引擎矩阵、环境变量、平台限制 |

## Gotchas

- PowerShell 拦脚本时用 `npx.cmd rea-agents@latest setup`；Windows 上 Ghidra 官方标注为实验性。
- `--token-limit` 与 `--format json` 互斥（报 UNSUPPORTED_OUTPUT_COMBINATION）；长 JSON 用 `--filter-output` 取键，别硬 parse 折行文本。
- `rea doctor` 退出码非 0 是**正常的状态报告**（缺引擎/有漂移），不等于命令失败。
- `rea mcp doctor` 不接受 `--token-limit`。
- 宿主配置里钉的是包版本：升级 REA 后不重跑 setup，宿主仍可能调旧版本。`registration.package_reference` 才是真相。
- 长驻会话（Ghidra / Hopper / 调试器 / Frida）用完要 close，否则后续调用可能因会话不一致失败。
- references 与 SKILL.md 的分工：SKILL.md 只做路由与硬边界，细节全在 references；本技能不用步骤级 `@` 标记（该标记只用在 references 的工作流文件里）。
