---
name: "工具表生成规范"
description: "按版本生成 references/toolset/rea-<版本>.md 的采集命令、列口径、分组规则、版本锚与自检判据。"
version: 1.0.1
trigger-when: REA 升级后重新生成工具面快照时
reads-from: SKILL.md, references/workflows/version-sync.md
writes-to: references/toolset/rea-<版本>.md
---
# 工具表生成规范

## 输入（四样）

| 输入 | 提供什么 |
| --- | --- |
| MCP stdio 的 `tools/list` + `prompts/list` | 工具名与 description（207 / 6） |
| `rea --llms` | CLI 命令清单（**153 条命令**；字符数只作参考且随计法变：162 行，按 LF 计 17,217 / 按 CRLF 计 17,378。**判漂移看命令条数、工具数与目录摘要，不看字符数**） |
| `rea capabilities --format json` | 副作用（effects）、可用性、`server_identity.catalog`（计数与摘要） |
| `rea --version` + `rea doctor --format json` | 版本锚与自检计数 |

## 采集命令（本机已跑通）

MCP 侧：用 Node 绝对路径起 stdio server，按 **换行分隔 JSON-RPC**（无分页，一次返回全部）：

```text
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"probe","version":"1"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
{"jsonrpc":"2.0","id":3,"method":"prompts/list"}
```

```bash
node "<rea-agents 根>/scripts/rea.mjs" mcp     # stdin 灌上面四行，stdout 逐行解 JSON
rea --llms                                      # CLI 清单
rea capabilities --format json                  # 副作用与可用性
rea mcp doctor --json                           # 自检计数与目录摘要
```

CLI 行解析正则（`rea --llms` 153 行全部命中）：

```text
^\|\s*`rea\s+([^`]+)`\s*\|\s*(.*?)\s*\|\s*$
```

行形如 `| `rea address-to-file-offset <path> <address>` | Resolve an analysis address to its original file byte offset |`。末尾三行是「Run `rea --llms-full` …」的说明，不是命令。

## 列口径

| 列 | 取值 |
| --- | --- |
| 工具 | 裸名，**不带** `mcp__rea__` 前缀 |
| 用途 | description 的第一句，去末尾句号；超长截断（约 140 字符）并保留可辨识前缀 |
| 副作用 / 可用性 | 见下方判定顺序；都没有写 `—` |

副作用判定顺序：

1. 查 `rea capabilities --format json`：`provider.groups[]` 里 `operations` 含该工具 → 打该组的 effects 中文标签。
2. 否则按 description 关键字命中：写文件/创建目录/落盘 → 可能写盘；启动进程/执行外部命令 → 启动进程；界面/窗口 → 可能弹窗；网络/下载/请求 → 可能联网。
3. 都没有 → `—`。

effects 中文标签：`launches_process`=启动进程 / `may_show_ui`=可能弹窗 / `may_access_network`=可能联网 / `may_write_filesystem`=可能写盘。可用性异常（`available=false`）要标注原因码（如 `not_configured` / `unsupported_host` / `unsupported_version`）。

## 分组规则

按工具名关键字分组，**顺序敏感（先匹配先归）**，共 11 组；分组完成后逐组计数必须与下表一致、总数必须等于 207：

| 分组 | 计数 |
| --- | --- |
| 会话与目标 | 27 |
| 原生二进制 | 36 |
| 托管代码 PE/CLR | 7 |
| JavaScript 与 Electron | 18 |
| 浏览器观察与场景录制 | 10 |
| Android 与移动设备 | 39 |
| Apple 平台 | 17 |
| 归档·固件·格式 | 11 |
| 网络与信号采集 | 7 |
| 调试器与插桩 | 22 |
| 证据与验证 | 13 |

**规则维护要求**：

- Android 组的关键字必须覆盖 `apktool`（2026-10-19 修正：`inspect_apktool_client` 曾因缺此词落进「其他」）。
- **不允许留「其他」组**：出现未归类工具 = 分组规则缺词，去补规则；补不了再考虑新建组，并同步更新计数表与总数判据。
- 计数与总数判据写进校验：207 = 各组之和；不成立就停止发布。

## 版本锚与自检

- frontmatter `version` = `rea --version` 输出（如 `6.7.0`）；`generated-at` 带时区偏移（本仓统一 `+08:00`）。
- 写入三处摘要，便于下次发现漂移：`catalog.digests.tools_sha256` / `prompts_sha256` / `combined_sha256`（来源 `rea capabilities --format json` → `server_identity.catalog.digests`）。
- 自检等式（三者必须一致，否则不许发布）：`rea mcp doctor --json` 的 `inventory.tools.expected == observed` = `catalog.counts.mcp_tools` = 分组总数；另有 `cli_commands`（153）与 `mcp_prompts`（6）。

## 输出与维护

- 路径：`references/toolset/rea-<版本>.md`；**旧版本文件保留不删**，用于回溯「当时这个工具叫什么」。
- frontmatter `description` 必须双引号单行（YAML 可解析、无反斜杠、无尖括号）。
- 生成物**不手改**：要改口径就改本规范再重新生成。
- 生成新版本后，`SKILL.md` 资源表与 `references/workflows/*.md` 里指向 `rea-<版本>.md` 的路径要一起更新（见 `references/workflows/version-sync.md`）。
