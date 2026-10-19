---
name: "W-INSTALL 接入与验证"
description: "把 REA 装进用户当前的编程助手并验证真的连上：体检 → 出计划 → 人确认 → 执行 → 三问验证。"
version: 1.0.0
trigger-when: 用户要安装、配置、接入或验证 REA 时
reads-from: SKILL.md, references/config/engines-and-providers.md, references/specs/mcp-registration-fields.md
writes-to: 用户宿主的 MCP 配置文件（仅在用户确认后由 rea setup 写入）
---
# @工作流: W-INSTALL 接入与验证

## @步骤1: 环境体检（先看，不动手）

```bash
rea doctor --format json          # 退出码非 0 是正常状态报告，不是命令失败
```

按 `scope_checks[].classification` 分流，**先看这两项**：

| classification | 含义 | 你该做的 |
| --- | --- | --- |
| `healthy` | 该项正常 | 跳过 |
| `missing_analysis_engine` | 缺分析引擎或外部工具 | 读 `remediation` 字段，按 `references/config/engines-and-providers.md` 说明这是用户自备还是可装 |
| `config_drift` | 有注册但配置与当前版本不符 | 属本工作流范围，出计划时一并处理 |

- `node` 不 healthy：先给安装路线（Windows `winget install --exact --id OpenJS.NodeJS.LTS`；macOS `brew install node`；fnm `fnm install 24` / `fnm use 24` / `fnm default 24`），装完再回来。REA 要求 Node 22.19+ / 24.11+ / 26+。
- `host` 不 healthy：平台不受支持，停止并说明。

🔴 CHECKPOINT：把体检结论按 classification 分类讲清楚，**不要**把缺引擎说成「安装失败」（两者是不同问题）。

## @步骤2: 出计划（把机读计划翻成人话）

```bash
rea setup --dry-run --format md     # 给人读
rea setup --dry-run --format json   # 给机读：status=needs_human + plannedActions[]
```

Windows 上 PowerShell 拦脚本时用 `npx.cmd rea-agents@latest setup --dry-run`。

`plannedActions[]` 每条含 `id` / `kind` / `label` / `target` / `operation` / `backupPath` / `detail`；kind 只有三类：

| kind | 含义 | 给人看时要说明 |
| --- | --- | --- |
| `configure_client` | 往某个宿主的 MCP 配置里写 REA 注册 | **会改用户已有文件**：报出 `target` 路径、`operation`（update/add）、`backupPath` 备份位置 |
| `install_skill` | 安装配套调查技能 | 装到哪、是否覆盖已有技能 |
| `symbolic_link` | 建软链 | 链到哪、是否已存在 |

分类汇报：① 会改哪些文件（逐条列 `target`，强调已有配置是 update 不是新建）② 备份在哪（`backupPath`，形如 `<配置>.rea.backup[.<hash>].recovery`）③ 装哪些技能 ④ 哪些引擎要用户自备。

🔴 CHECKPOINT：**把计划原样给人看并停下**。没有明确同意，禁止执行 `rea setup`；没有明确同意，禁止 `--yes`。

## @步骤3: 执行（仅在被确认的范围内）

```bash
rea setup                                  # 交互式，逐项确认
rea setup --yes --client <id>              # 仅在用户已明确同意该范围时
rea setup --install-hopper                 # 仅当用户要 Hopper 并同意安装时
```

- 只装用户确认过的客户端（`--client`），不要因为「都装上更方便」而扩大范围。
- Ghidra / IDA / JADX / Kuna / tshark 等是**用户自备**：给环境变量名与官方要求即可，REA 不会替用户下载（Hopper 例外，有 `--install-hopper`）。
- 索引用 `--skill-client`；只想装技能不配客户端用 `--skill`；想对全部检测到的客户端下手用 `--all-detected`（范围最大，风险最高，需单独确认）。

## @步骤4: 三问验证（缺一不算装好）

| 问 | 命令 | 通过判据 |
| --- | --- | --- |
| ① server 能不能起来 | `rea mcp doctor --json` | `healthy: true`，`inventory.tools.expected == observed`，`missing`/`unexpected`/`duplicates` 为空，`request_flow.ok: true` |
| ② 宿主注册对齐没有 | `rea doctor --format json` | 该宿主的 `registrations[]` 里 `state == "aligned"` |
| ③ 会话里真的有工具吗 | 重启宿主后看工具列表 | REA 工具出现（通常形如 `mcp__rea__<tool>` 或 CLI/工具菜单里的 REA 条目） |

**三问的差别**：① 只证明 server 能启动；② 只证明配置文件里写对了；③ 才是用户真正要的「能用了」。前两问绿而第三问没验，**不许说装好了**。

@验证点：三问各自贴出原始输出要点（版本号、计数、state、工具名）。任一问失败 → 进下面的分流表，不要重试同一条命令两次以上。

## 失败分流

| 现象 | 归因 | 处理 |
| --- | --- | --- |
| `rea` 命令找不到 | 未安装 / PATH 未刷新 | 用 `npx rea-agents@latest` 走一次，或让用户重开终端 |
| `node` 版本不达标 | 环境 | 回 @步骤1 给安装路线 |
| doctor 里没有我的宿主 | 未检测到配置 | 直接给 `--client <id>` 或用 `--all-detected`（需确认）；确认宿主真的支持本地 MCP |
| 注册写进去了但会话里没工具 | 未重启 / 宿主缓存 / 配置被别的进程覆盖 | 先重启宿主；再看 `registration.state` 与 `package_reference` |
| 配置被写坏 | 罕见，官方 6.7.0 已修「重复成员」语义 | 走 W-ROLLBACK：用 `backupPath` 还原 |
| 引擎缺失 | 与接入无关 | 读 `remediation`，索引到 `references/config/engines-and-providers.md` |
