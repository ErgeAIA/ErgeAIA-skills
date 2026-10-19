---
name: "引擎与 Provider 前置"
description: "REA 的分析引擎与外部工具前置：四个 provider 的启用方式、其余外部工具环境变量、平台限制、无引擎时还能做什么、副作用词表。"
version: 1.0.0
trigger-when: 判断这台机器能不能做某类逆向、或用户问缺什么引擎时
reads-from: SKILL.md
writes-to: 无（只读说明）
---
# 引擎与 Provider 前置

## 数据来源

| 来源 | 取什么 |
| --- | --- |
| `rea doctor --format json` | `scope_checks[]`（`name` / `ok` / `classification` / `detail` / `remediation`）、`providerInspections[]` |
| `rea capabilities --format json` | `analysis_provider_candidates[].availability{status,code,reason,diagnostics}`、`server_identity` |

本页为 **2026-10-19 在 REA 6.7.0 / Node 24.13.0 / win32 x64 上的一次实测**，不是官方承诺。版本或平台一变就重取，不要照抄。`rea providers --format json` 与 `rea capabilities` 输出同一个 envelope。

## 四个分析 Provider

| id | 名称 | 启用方式 | 本机状态 | 说明 |
| --- | --- | --- | --- | --- |
| `ghidra` | Ghidra | `GHIDRA_INSTALL_DIR` 指向解压后的 Ghidra 12.1.x 目录 | `unavailable / not_configured` | 诊断逐项给 configuration / platform / architecture / installation / version / headless / native_decompiler / java；Windows 上 `java` 探针要求 **绝对路径**（实测 `java.exe` 报 `ERR_REA_WINDOWS_NATIVE`、Win32 87），且 Ghidra 在 Windows 为官方标注的实验性平台 |
| `hopper` | Hopper Disassembler | 仅 macOS：`rea setup --install-hopper` 或 `HOPPER_LAUNCHER_PATH` | `unavailable / unsupported_host` | 非 macOS 无解，不要建议用户装 |
| `ida` | IDA MCP adapter | `REA_IDA_MCP_CONFIG` 指向上游 IDA MCP 注册 JSON | `unavailable / not_configured` | 见官方 `docs/ida-provider.md` |
| `kuna` | Kuna | `REA_KUNA_COMMAND` 指向自备 kuna 可执行文件绝对路径 | `unavailable / not_configured` | 官方以 1.833 验证；**REA 不下载、不安装、不更新** |

## 其余外部工具（不是 provider，按需自备）

| 环境变量 | 工具 | 用途域 | 要求 |
| --- | --- | --- | --- |
| `REA_JADX_MCP_JAR` | jadx-headless-mcp 0.7.1 JAR | Android 源码级反编译 | 需 JDK；REA 不下载 |
| `REA_APKTOOL_COMMAND` | apktool | Android 资源解码 | REA 不安装 |
| `REA_ADB_PATH` | adb（platform-tools） | 设备类工具 | REA 不安装；可能需要真实设备 |
| `REA_TSHARK_COMMAND` + `REA_CAPINFOS_COMMAND` | tshark 4.x / capinfos | 抓包分析 | 需绝对路径；Linux 侧依赖 util-linux `prlimit` |
| `REA_SIGROK_COMMAND` | sigrok-cli 0.7.2 | 逻辑采样解码 | Linux |
| `REA_WABT_BIN_DIRECTORY` | WABT 1.0.42 | WASM 校验 | 绝对目录 |
| `REA_BROWSER_EXECUTABLE` | Chromium | 网站模块导入解析 | 本地可执行文件 |
| `REA_JEB_MCP_URL` | JEB（默认 `http://127.0.0.1:8425/mcp`） | Android 反编译 | 用户自己启动 JEB |
| `REA_PROCESS_RUN_ID` | — | **REA 保留变量，勿占用** | — |

## 平台与版本限制（本机实测）

- `native-macos` provider 整族不可用（`unsupported_host`）：`inspect_macho`、`inspect_signature`、`inspect_plist`、`list_architectures`、`demangle_swift`、`observe_native_calls`、`observe_native_ui`、`capture_native_ui_scenario`、`inspect_native_dispatch_metadata`。
- `inspect_asset_catalog` 需 macOS `assetutil`。
- `sqlite` provider 需 **Node 24.x >= 24.15 或 26+**；本机 24.13.0 → `unsupported_version`，故 `inspect_sqlite_database` 不可用（升级 Node 后再试）。
- Android 设备类工具需 adb 与真实设备/模拟器；`list_adb_devices` 首次使用可能启动本地 adb server。
- 固件提取、信号解码、抓包分析依赖 Linux 工具链与上表环境变量。
- Kuna 的平台支持面窄：官方 6.6.0 变更说明记录「以 Kuna 1.833 在 Linux 上做真实 provider 覆盖；**Windows、PE 与 universal Mach-O 不受支持**」。

## 无引擎时还能做什么

实测**不依赖外部引擎**的两个 provider（`rea-artifact-graph` / `rea-dotnet-static`）：

| provider | 可用能力 | 副作用 |
| --- | --- | --- |
| `rea-artifact-graph`（REA 自带 v1） | `inspect_artifact`、`extract_artifact`、`decode_interface_builder`、`inspect_keyed_archive`、`trace_dylib_resolution` | `launches_process`、`may_write_filesystem` |
| `rea-dotnet-static`（REA 自带 v1） | `inspect_managed_artifact`、`inspect_managed_members`、`inspect_managed_native_boundaries` | — |

另有不需要上述 provider 的内建能力（如 JavaScript 应用图、归档清单、读已保留证据、证据包对比）。**依据**：`rea doctor` 的引擎检查只有 hopper / ghidra / ida-registration / jadx / kuna-installation 五项，缺引擎时这些能力族不报 `not_configured`。[推测] 其余平台（macOS/Linux）的可为集合更大，以本机实取为准。

## 副作用词表（出现即先向用户声明）

| effect | 含义 |
| --- | --- |
| `launches_process` | 会启动子进程 |
| `may_show_ui` | 可能弹出界面 |
| `may_access_network` | 可能联网 |
| `may_write_filesystem` | 可能写文件 |

Frida 插桩、`capture_*_scenario`、adb 写操作（install / push / uninstall / start / stop）、调试器会话属于**真实副作用**：执行前必须声明会改什么，且禁止把「用户没反对」当成同意。
