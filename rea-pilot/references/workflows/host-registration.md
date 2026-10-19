---
name: "W-HOST 宿主自接入"
description: "宿主不在 setup 客户端列表时，由宿主自己探索并插入 MCP 通用字段，再验证。"
version: 1.0.0
trigger-when: 用户的助手未被 rea setup 识别或不在官方客户端列表时
reads-from: SKILL.md, references/specs/mcp-registration-fields.md
writes-to: 用户宿主自己的 MCP 配置文件（由宿主 Agent 插入，skill 不代写）
---
# @工作流: W-HOST 宿主自接入

## @步骤1: 先确认宿主真的不受支持

```bash
rea setup --dry-run --format json   # 看 plannedActions 里有没有 configure_client:<你的宿主>
```

有 → 回 W-INSTALL，**不要**手写配置。没有 → 继续。

## @步骤2: 让宿主自己找配置（把这三句交给它）

1. 在你的宿主里找 MCP 服务器配置：文件可能叫 `mcp.json` / `settings.json` / `config.toml` / `cordis.patch.yml`，字段可能叫 `mcpServers` / `mcp.servers` / `servers` / `tools.mcp`。
2. 读出它**已有的一条 stdio 服务器条目**，照那个形状抄字段名，不要自创结构。
3. 插入下面这份通用条目，然后重启宿主。

## @步骤3: 通用字段（只给形状，不给路径）

| 字段 | 值 |
| --- | --- |
| serverName / key | `rea` |
| transport | `stdio` |
| command | `npx`（Windows 上宿主若走 PowerShell 则 `npx.cmd`）或 Node 可执行文件绝对路径 |
| args | `["-y","rea-agents@<版本>","mcp"]` 或 `["<...>/rea-agents/scripts/rea.mjs","mcp"]` |

- 钉版本比 `@latest` 好：可复现。版本取 `rea --version`。
- 不替宿主猜路径、不猜格式：官方只承诺「支持本地 MCP 服务器的助手都可以用」，各宿主格式不同，写错会毁掉用户已有配置。

🔴 CHECKPOINT：插入前先备份原文件（`<配置>.bak-<日期>`），并把要插入的片段给人看；用户不同意就不写。

## @步骤4: 验证

1. 重启宿主。
2. 让宿主列出工具，确认 REA 工具出现；再在会话里调一个最轻的只读工具（如 `binary_session`）。
3. 跑 `rea mcp doctor --json` 证明 server 侧没问题（用于区分「宿主没读到配置」和「server 起不来」）。

@验证点：贴出插入后的片段 + 重启后真实看到的 REA 工具名。只贴片段不算通过。
