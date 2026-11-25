---
name: "意图 → REA MCP 工具路由"
description: "用户自然语言意图到 REA MCP 工具的路由表：只登记本技能接管并直接调用的工具，未接管项也留一行已评估。"
version: 0.1.0
trigger-when: 用户想让 REA 直接做某件事、或 W-SYNC 判出新工具需要做意图判定时
reads-from: SKILL.md, references/toolset/rea-<版本>.md, references/specs/toolset-generation.md
writes-to: 无（纯路由规则，不改用户配置）
---
# 意图 → REA MCP 工具路由

用户说人话，Agent 调工具；**不要把命令清单当成交付物**。本文件只登记「本技能接管并直接调用」的意图；工具名与副作用以当前版本工具面快照为唯一来源，本文件不复制描述。

## 硬规则

1. 先用 `rea --version` 找当前工具面快照；快照里没有的工具不许调用，先走 W-SYNC。
2. 调用前先确认目标工具**真的出现在当前会话的工具列表里**。工具面快照来自 CLI 版本，但宿主注册可能钉在旧包（本机实测：CLI 6.10.1 / 会话工具 207 = 6.7.0，`inspect_binary_hardening` 不在会话里）；工具不在会话里就如实报「宿主注册未对齐 / 工具不可用」，**不要偷偷降级成 CLI、不要伪造调用结果**，并按 W-INSTALL 做三问验证。
3. 有真实副作用的工具（写文件、启动进程、改设备状态、重置调查）先按 SKILL.md 的 CHECKPOINT 声明并等确认。
4. 一次只调一条最小路径；拿到证据后再决定是否继续，不许一股脑铺十条。
5. 用户只要结论时，交付「工具 + 原始输出要点 + 结论」；用户明确要命令时才给 CLI 形态。

## 当前接管的意图（6.10.1 起）

| 用户意图（示例） | MCP 工具 | 工作流 | 副作用 / 前置 |
| --- | --- | --- | --- |
| 这个 PE/ELF/Mach-O 开了哪些加固？ | `inspect_binary_hardening` | W-HARDEN | 只读静态；无外部引擎 |
| 发布包暴露了什么？ | `audit_release_exposure` | W-HARDEN | 只读 artifact；无外部引擎 |
| 静态 API 声明和抓到的请求一致吗？ | `compare_static_and_observed_endpoints` | W-HARDEN / W-ROUTE | 需 HAR Evidence；只读 |
| 这个 ELF 依赖哪些库 / 符号版本？ | `inspect_elf_dependencies` | W-ROUTE | 只读；无引擎 |
| ELF 的 debuglink / build-id 指向哪？ | `inspect_elf_debug_link` | W-ROUTE | 只读；无引擎 |
| 这个二进制的 DWARF 编译单元有哪些？ | `inspect_dwarf_units` | W-ROUTE | 只读；无引擎 |
| ELF 的 FDE / unwind 范围能恢复哪些函数？ | `inspect_elf_unwind_ranges` | W-ROUTE | 只读；无引擎 |
| 二进制里有哪些初始化/终止函数？ | `inspect_native_initializers` | W-ROUTE | 只读；无引擎 |
| APK 的 JNI native 方法绑定到了哪些库？ | `inspect_android_jni_bindings` | W-ROUTE | 需 `REA_JADX_MCP_JAR` + JDK |
| 这个 OpenAPI / GraphQL SDL 声明了什么？ | `inspect_api_contract` | W-ROUTE | 只读；无网络、无执行 |
| Maven / Gradle / NuGet 包元数据里有什么？ | `inspect_maven_gradle_metadata` / `inspect_nuget_nupkg` | W-ROUTE | 只读；无网络 |
| 这个 Playwright trace 里发生了什么？ | `inspect_playwright_trace` | W-ROUTE | 只读离线 |
| UEFI 固件卷 / NVRAM 里有什么？ | `inspect_uefi_firmware` / `inspect_uefi_nvram` / `extract_uefi_firmware` | W-ROUTE | extract 会写盘，先确认 |
| Windows 快捷方式指向哪？ | `inspect_windows_shortcut` | W-ROUTE | 只读不解析目标 |
| 这个 V8 code cache / bytenode 是什么？ | `inspect_v8_code_cache` | W-ROUTE | 只读；不等于反编译 |
| REA 有哪些现成工作流 / 这个流程怎么做？ | `guided_workflows` / `search_guidance` / `read_guidance_section` | 资源 | 只读文档，不查目标 |
| 清空当前调查证据重来 | `reset_investigation` | W-ROLLBACK | **丢弃 Evidence**，先确认；建议先 save_path |

## 已评估但不接管（6.10.1）

| 工具族 | 结论 | 原因 |
| --- | --- | --- |
| build computer 全套（`start_build_computer` / `start_build_capture` / `mark_build_checkpoint` / `stop_build_capture` / `export_build_environment` / `act_on_build_computer` / `check_build_task` / `measure_build_task` / `record_build_consent` / `close_build_computer`） | `OUT_OF_SCOPE` | 属 REA 自带技能的「连上后怎么建/测桌面任务」，有下载/安装/写状态/模型调用；本技能是领航员，不把整套构建流程搬进来 |
| `inspect_ntfs_journal` | `REFERENCE_ONLY` | 取证/事件分析，留给 REA 自带技能；本技能只保证能被路由到正确工具面 |

@验证点：新增工具若没有「接管 / 不接管」结论，W-SYNC 不算完成。
