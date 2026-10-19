---
name: "宿主 MCP 注册字段"
description: "宿主 MCP 配置的通用字段、宿主自探索提示词、各家配置路径与格式差异、写入前检查项与校验动作。"
version: 1.0.0
trigger-when: 要给宿主写 REA 的 MCP 注册、或宿主不在 rea setup 支持列表时
reads-from: SKILL.md, references/workflows/host-registration.md
writes-to: 用户宿主自己的 MCP 配置文件（由宿主 Agent 插入，本技能不代写）
---
# 宿主 MCP 注册字段

## 先确认要不要自己写

```bash
rea setup --dry-run --format json   # 看 plannedActions[] 里有没有 configure_client:<你的宿主>
```

有 → 走 `references/workflows/install-and-verify.md`，**不要**手写。没有 → 用下面的字段与提示词，让**宿主自己**去改自己那份配置。

## 让宿主自己找配置（把这三句原样交给它）

1. 在你的宿主里找 MCP 服务器配置：文件可能叫 `mcp.json` / `settings.json` / `config.toml` / `config.yaml` / `cordis.patch.yml`，字段可能叫 `mcpServers` / `mcp.servers` / `servers` / `tools.mcp`。
2. 读出你**已有的一条 stdio 服务器条目**，照它的形状抄字段名 —— 不要自创结构、不要把别的宿主的格式搬过来。
3. 插入下面这份通用条目，重启宿主，然后在会话里列出工具确认 REA 工具出现。

## 通用字段（只给形状）

| 字段 | 值 | 备注 |
| --- | --- | --- |
| 服务器键名 | `rea` | 宿主实际键名以它已有条目为准（可能是 `mcpServers.rea` 之类） |
| transport | `stdio` | REA 是 stdio MCP server |
| command | `npx`；Windows PowerShell 环境下用 `npx.cmd`；或 Node 可执行文件绝对路径 | 绝对路径最稳（不受 PATH 影响） |
| args | `["-y","rea-agents@<版本>","mcp"]`，或 `["<rea-agents 根>/scripts/rea.mjs","mcp"]` | 钉版本比 `@latest` 可复现 |

- 包根与版本以实测为准：`rea doctor --format json` → `identity.installations.paths`、`identity.cli_package_version`；本机观测包根形如 `%APPDATA%\npm\node_modules\rea-agents`（Windows）。
- 官方口径：**支持本地 MCP 服务器的助手都可以用**；官方不给逐宿主的路径表，所以路径与格式必须由宿主自己探索。

## 为什么必须让宿主自己找（本机实测差异）

| 客户端 id | 配置路径（本机 Windows 观测） | 格式 |
| --- | --- | --- |
| `cursor` | `~/.cursor/mcp.json` | JSON |
| `copilot_cli` | `~/.copilot/mcp-config.json` | JSON |
| `droid` | `~/.factory/mcp.json` | JSON |
| `gemini_cli` | `~/.gemini/settings.json` | JSON |
| `antigravity` | `~/.gemini/config/mcp_config.json` | JSON |
| `kimi` | `~/.kimi-code/mcp.json` | JSON |
| `omp` | `~/.omp/agent/mcp.json` | JSON |
| `qwen_code` | `~/.qwen/settings.json` | JSON |
| `vscode` | `%APPDATA%\Code\User\mcp.json` | JSON |
| `workbuddy` | `~/.workbuddy/mcp.json` | JSON |
| `zcode` | `~/.zcode/cli/config.json` | JSON |
| `claude_desktop` | `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json` | JSON |
| `codex` | `~/.codex/config.toml` | **TOML** |
| `grok_build` | `~/.grok/config.toml` | **TOML** |
| `hermes` | `%LOCALAPPDATA%\hermes\config.yaml` | **YAML** |

这张表只是**一次观测**：JSON / TOML / YAML 三种格式并存、路径随平台与版本变。照抄这张表去改别的机器，就是拿用户的配置冒险。

## 写入前必须做

1. **备份**原文件（`<配置>.bak-<日期>`）。
2. **先给人看**要插入的片段与插入位置，等人同意再写。
3. **只改自己那一段**：保留用户其它 MCP 服务器条目，不要重排、不要格式化整份文件。
4. **不猜格式**：拿不准字段名就先读宿主已有条目；仍不确定就问用户。

特例：Claude Desktop 在运行中会按内存重写自己的配置、把注册丢掉 —— 官方 remediation 要求**先完全退出 Claude Desktop 再刷新注册，然后重新启动**。

## 校验动作

1. 重启宿主。
2. 宿主列出工具，确认 REA 工具出现（通常形如 `mcp__rea__<tool>`）；再调一个最轻的只读工具（如 `binary_session`）。
3. `rea mcp doctor --json` —— 证明 **server 侧**能起来（用于区分「宿主没读到配置」与「server 起不来」）。
4. `rea doctor --format json` —— 若宿主受支持，看该 `registration:*` 的 `state` 是否 `aligned`。

@验证点：贴出「插入后的片段」+「重启后真实看到的 REA 工具名」。只贴片段不算接入成功。
