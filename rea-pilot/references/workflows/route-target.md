---
name: "W-ROUTE 目标选路"
description: "按目标类型给出证据需求、引擎前置与最小路径命令；无引擎时给替代路径。"
version: 1.0.0
trigger-when: 用户问某个目标该怎么逆向、该用哪些工具时
reads-from: SKILL.md, references/toolset/rea-<版本>.md, references/config/engines-and-providers.md
writes-to: 无（只读建议）
---
# @工作流: W-ROUTE 目标选路

本工作流**只选路**：告诉用户该按什么顺序取哪类证据、前置是什么、最小路径是哪几条命令，**不重写 REA 的调查方法**（那属于 REA 自带技能）。

## @步骤1: 判定目标类型

| 目标 | 典型形态 | 主要证据面 |
| --- | --- | --- |
| 原生可执行 / 库 | exe、dll、so、dylib、App 主二进制 | 函数伪代码、调用图、字符串与常量、段权限 |
| 托管程序 | .NET PE / CLR 程序集 | 类型与成员、CIL、P/Invoke 边界 |
| Electron / JavaScript 应用 | `app.asar`、应用目录、bundle | 模块图、IPC handler 配对、暴露 API、fuses |
| 打包移动应用 | apk / aab / ipa / hap | 清单与组件、资源、类与方法、AOT 快照 |
| 归档与载荷 | zip / pkg / dmg / 安装包 | 嵌套清单、内部结构、签名 |
| 固件 | 镜像 / 分区 / 嵌入式包 | 固件区段、提取出的文件系统与二进制 |
| 运行中的浏览器 | 本地 CDP 端点 | 页面结构、脚本、事件监听、网络 |
| 运行中的原生应用 | 本机进程 | 调用观测、UI 观测、内存与插桩 |
| 抓包与信号 | pcap / pcapng / 逻辑采样 | 端点、DNS/TLS SNI、协议、HTTP URI |
| 数据库与本地存储 | sqlite / 偏好文件 | 表结构、行样本 |
| WASM / EVM | .wasm / 字节码 | 导入导出接口、函数选择器 |

## @步骤2: 定证据需求

先问清用户要回答**什么问题**，再选面：

| 用户想要 | 证据需求 | 首选入口 |
| --- | --- | --- |
| 「这个功能是怎么实现的」 | 静态结构 | `binary_overview` → `search_strings` → `analyze_function` / 应用图 |
| 「运行时它做了什么」 | 运行时行为 | `open_binary` + `capture_process_scenario`，或 CDP 的 `inspect_web_page` |
| 「两个版本差在哪」 | 版本对比 | `compare_application_versions` / `compare_artifacts` |
| 「为什么崩」 | 崩溃 + 调用/引用 | `inspect_recorded_crash` + `trace_call_path` |
| 「谁引用了这个字符串/地址」 | 引用图 | `search_strings` → `xrefs` |

## @步骤3: 查引擎前置（决定可行性）

读 `references/config/engines-and-providers.md`，先回答「这台机器能不能做这件事」：

- 原生反编译需要 Ghidra 12.1.x（+ 64 位 JDK 21+）或 Hopper（仅 macOS）；Windows 上 Ghidra 官方标注实验性。
- 托管、JavaScript/Electron、归档、Android 清单、已有证据类：**不需要外部反编译器**，缺引擎也能做。
- 固件、抓包、信号解码：需要 Linux 与用户自备的外部工具（如 tshark/capinfos/sigrok）与对应环境变量。
- 运行观测：浏览器走 CDP；原生调用观测在 macOS 由 LLDB 承担；Android 走 adb。

## @步骤4: 给最小路径（3–5 条，按顺序）

`rea doctor --format json` 看 `provider` 与 `classification` 决定走哪条；命令形如：

```bash
npx -y rea-agents@latest analyze <目标> --format json          # 先拿总览，确认打的是对的文件
npx -y rea-agents@latest search <目标> "<关键字>" --format json  # 用字符串/符号把范围缩到一个点
npx -y rea-agents@latest function <目标> <符号> --provider ghidra --json   # 再深挖一个函数
```

- 每一步给「看什么、什么算命中、命中后下一步是什么」。
- 目标很大时先给范围收缩策略（先字符串/符号定位，再函数/模块），不要一上来全量反编译。
- 证据要留痕：用 `evidence-export` / `export_evidence_bundle` 存下来，后续对比与复跑都靠它。

## @步骤5: 无引擎时的替代路径

| 缺什么 | 还能做什么 |
| --- | --- |
| Ghidra/Hopper | JavaScript/Electron 应用图、归档与包清单、Android 清单与资源、字符串/符号级检索、已有证据包的重读与对比 |
| JADX | Android 清单、资源、类与方法级结构仍可用；源码级反编译需用户自备 JAR |
| 全部外部工具 | 只做「读已保留证据」类工作（`inspect_analysis_view`、`compare_bundles`） |

@验证点：交付里必须出现① 目标类型判定② 证据需求③ 前置结论（能不能做、缺什么）④ 3–5 条带判据的命令。缺任一项就是没选完路。

## 案例参照（官方 showcase）

官方展示集可作为选路样本：aegis（Android）、ctf（flag checker）、dx-ball（声像）、notion（剪贴板桥）、th04（环形弹幕）。来源：<https://rea.tools/zh-CN/showcase/>
