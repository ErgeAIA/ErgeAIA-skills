---
name: "rea-6.7.0 工具面快照"
description: "REA 6.7.0 的完整工具面：207 个 MCP 工具、6 个官方 prompt、153 条 CLI 命令，逐条给用途与副作用/可用性，并写明 CLI 名与 MCP 名不是一一对应。"
version: 6.7.0
generated-at: 2026-10-19T23:40:07+08:00
generated-by: "rea mcp doctor --json --full-output；MCP stdio initialize + tools/list + prompts/list；rea --llms；rea capabilities --format json"
trigger-when: 需要查「REA 有哪些工具」「某个能力用哪个工具」「这个工具有什么副作用或前置」时
reads-from: SKILL.md
---

# REA 6.7.0 工具面快照

## 版本锚

| 项 | 值 | 来源 |
| --- | --- | --- |
| REA CLI 版本 | 6.7.0 | `rea --version` |
| 包 / 协议 | rea-agents@6.7.0 / MCP 2025-11-25 | `rea mcp doctor --json` |
| MCP 工具 | 207（expected=observed，missing/unexpected/duplicates 全空） | 同上 |
| 官方 prompt | 6 | 同上 |
| 目录摘要 | `96d8f6e6ea1b1ba13557216624a3461c738729d53c79b4b0100d1f3a3a32441c` | 同上 |
| 工具目录摘要 | `af39310c9591bb981893ec0d2188b1bcf6e9cc8ba3ac513d5bbefc8ddcb85639` | `rea capabilities --format json` → `server_identity.catalog.digests.tools_sha256` |
| prompt 目录摘要 | `7152916ab48bd2a9677a5ad9cdbde0a51dc53c113934952ad096e93f5f18aa7e` | 同上 → `prompts_sha256` |
| CLI 命令 | 153 条（`rea --llms` 17,378 字符；`rea --llms-full` 82,487 字符） | `rea --llms` |

**有效期**：官方近 30 天发布 13 个版本、近 90 天 18 个（`npm view rea-agents time --json`）。本文件平均约 2 天过期一次 —— **升级后按 `references/workflows/version-sync.md` 重新生成，不要手改本文件**。

## 名称映射（先读这段，别按名字猜工具）

宿主里的 REA 工具通常以 `mcp__rea__<tool>` 出现；**CLI 命令名与 MCP 工具名不是一一对应**，同一能力两侧可能叫不同名字：

| CLI 命令 | 对应 MCP 工具（示例） |
| --- | --- |
| `rea function <path> <symbol>` | `analyze_function` |
| `rea instructions` | `read_function_instructions` |
| `rea search` | `search_strings` / `search_procedures` |
| `rea inspect <path>` | `binary_overview`（总览）/ `inspect_analysis_view`（读已保留证据） |
| `rea trace <literal>` | `trace_feature` |
| `rea evidence-export` / `evidence-import` | `export_evidence_bundle` / `import_evidence_bundle` |
| `rea analyze-javascript-application` | `analyze_javascript_application` |

要确认当前真实工具名，用宿主自己的工具列表或 `rea mcp doctor --json --full-output`（会给 expected/observed 计数与目录摘要），**不要凭本文件的手工推断去调工具**。

## MCP 工具（207）

### 会话与目标（27）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `address_name` | Resolve the primary analyzed name at a code or data address. | — |
| `address_to_file_offset` | Map one provider-normalized virtual address to its original nonnegative file offset. | — |
| `binary_overview` | Return the bound document and exhaustive procedure/string counts, plus every segment and segment_count when the provider supports segment enumeration. | — |
| `binary_session` | Report the complete current target, provider, capability availability, client-feature, analysis, and server-identity status without starting analysis. | — |
| `close_binary` | When the investigation is finished, drain earlier provider requests, optionally write a provider-neutral analysis snapshot atomically to the caller-s… | — |
| `comment` | Read the regular analysis comment at an address, defaulting to the current cursor. | 只读 / 不执行目标 |
| `current_address` | Return Hopper's current cursor address for the selected document. | — |
| `current_document` | Return the document currently selected by REA's Hopper bridge. | — |
| `current_procedure` | Return the analyzed procedure containing Hopper's current cursor. | — |
| `get_navigation_context` | Return the selected document, current address, and containing/current procedure in one provider-neutral result. | — |
| `goto_address` | Move Hopper's GUI cursor to a mapped address and return the observed cursor address. | — |
| `inline_comment` | Read the inline instruction comment at an address, defaulting to the current cursor. | — |
| `inspect_address_context` | Inspect one explicit reproducible address for its analyzed name, containing procedure, regular and inline comments, and matching bookmarks. | — |
| `list_bookmarks` | List every bookmark in the selected Hopper document as address and name pairs; unnamed bookmarks retain a null name. | — |
| `list_documents` | List provider program or document identities. | — |
| `next_address` | Return the next analyzed object address after an explicit address or current cursor. | — |
| `open_binary` | Open a local executable, application bundle, archive, JavaScript, source map, plist, or analysis database after validation. | — |
| `prev_address` | Return the previous analyzed object start before an explicit address or current cursor. | — |
| `read_bytes` | Read analyzed bytes from one provider-normalized virtual address. | — |
| `resolve_containing_procedure` | Resolve an arbitrary address, including an interior instruction or exact external entry, to its provider-analyzed containing procedure. | — |
| `search_bytes` | Find masked byte signatures in initialized analyzed memory. | — |
| `set_address_name` | Assign an analyst name to one mapped hexadecimal address and report whether the native edit succeeded and exact readback matched. | 改写分析元数据 |
| `set_addresses_names` | Assign analyst names to multiple mapped addresses in one call and return per-address edit/readback success booleans. | 改写分析元数据 |
| `set_bookmark` | Create or replace a bookmark at a mapped hexadecimal address and report success. | 改写分析元数据 |
| `set_comment` | Write a regular analysis comment at a hexadecimal address and return whether readback matched. | 改写分析元数据 |
| `set_inline_comment` | Write an inline instruction comment at a hexadecimal address and return whether readback matched. | 改写分析元数据 |
| `unset_bookmark` | Remove the bookmark at a mapped hexadecimal address and return whether it is absent. | 改写分析元数据 |

### 原生二进制（36）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `analyze_function` | Build a dossier for one native function identified by symbol or provider-returned address. | — |
| `annotate_native_function` | Atomically update one function name and/or entry comments, read them back, and return a refreshed complete function dossier. | — |
| `batch_decompile` | Decompile each explicit procedure symbol or address concurrently. | — |
| `build_call_path` | Build every shortest direct-callee path inline from complete analyze_function Evidence records using exact canonical addresses. | — |
| `compare_functions` | Compare two explicit sets of analyze_function Evidence across identity, exact provider text, calls, references, strings, and address-normalized CFG t… | — |
| `find_xrefs_to_name` | Resolve an exact name against the bound provider's name inventory and return a resolved or unresolved result. | — |
| `get_call_graph` | Resolve one symbol or address to its canonical procedure entry, then traverse the bound provider's caller or callee relationships until the reachable… | — |
| `inspect_analysis_view` | Inspect selected views of completed binary-layout, JavaScript application, native analyze_function, inspect_artifact, inventory_artifact, inspect_was… | — |
| `inspect_binary_layout` | Inspect an explicit local binary without launching it as a host process. | — |
| `inspect_go_binary` | Inspect embedded Go compiler version, main module, dependency/replacement versions and build settings in an explicit local ELF, PE or thin Mach-O ima… | — |
| `inspect_native_api` | Analyze a native API boundary in one function identified by symbol or provider-returned address. | — |
| `inspect_native_data_type` | Inspect one recovered type by exact database category path or defined typed data address. | — |
| `inspect_native_dispatch_metadata` | Inspect the bound provider's name inventory for Objective-C class/method symbols and Swift mangled symbols, returning at most max_records decoded nam… | — |
| `inspect_native_instruction` | Inspect one exact code or data address: decoded bytes, mnemonic, ordered operand tokens, flow, outgoing instruction references and typed incoming ref… | — |
| `inspect_native_load_image` | Verify the provider's loaded DOS MZ or explicitly selected COM image against its immutable target snapshot: complete original/modified source-byte di… | 只读 / 不执行目标 |
| `inspect_rust_binary` | Inspect the cargo-auditable crate dependency list embedded in an explicit local ELF, PE or thin Mach-O image. | 只读 / 不执行目标 |
| `inspect_with_objdump` | Run caller-selected GNU objdump inspection against a local artifact, or request operation=architectures without a path to list BFD targets advertised… | — |
| `list_names` | List every analyzed memory and external symbol as address/value pairs. | — |
| `list_procedures` | List every analyzed procedure as address/value pairs after provider analysis. | — |
| `list_segments` | List segments or memory blocks using exclusive end addresses. | — |
| `list_strings` | List every provider-reported string object or candidate, or filter to one address, as address/value pairs with encoding, terminator status, and byte… | — |
| `procedure_address` | Resolve an unambiguous procedure symbol name or provider-normalized address to its canonical entry address. | — |
| `procedure_assembly` | Return assembly for one analyzed procedure identified by symbol or hexadecimal address. | — |
| `procedure_callees` | Return the provider's resolved direct callees for one procedure identified by symbol or address. | — |
| `procedure_callers` | Return the provider's resolved direct callers for one procedure identified by symbol or address. | — |
| `procedure_info` | Return provider metadata for one procedure identified by symbol or address: entrypoint, signature, locals, size, block count, and complete inclusive… | — |
| `procedure_pseudo_code` | Decompile one analyzed procedure by symbol name or provider-normalized address. | — |
| `procedure_references` | Return every raw incoming or outgoing reference edge for one procedure. | — |
| `read_function_instructions` | Return every raw instruction for one analyzed procedure. | — |
| `resolve_native_call_targets` | Resolve one explicit static call site using typed provider call references. | 只读 / 不执行目标 |
| `search_procedures` | Search every analyzed procedure name using literal matching by default or regex when requested. | — |
| `search_strings` | Search every provider-reported string object or candidate using literal matching by default or regex when requested. | — |
| `trace_call_path` | Resolve start and optional goal symbols or addresses to canonical procedure entries, then trace direct callers or callees until the graph is exhauste… | — |
| `trace_feature` | Trace the complete literal query, preserving spaces, through every matching string and procedure, their xrefs, and truthful containing-procedure reso… | — |
| `trace_native_values` | Trace a bounded static dependency graph from one explicit native procedure. | — |
| `xrefs` | Return analyzed references to a code or data address. | — |

### 托管代码 PE/CLR（7）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `compare_managed_members` | Compare two authenticated inspect_managed_members Evidence records using unique-only tiers: exact declared type, name, and CIL/signature; exact decla… | — |
| `import_managed_reconstruction` | Import decompiler-produced managed reconstruction against authenticated inspect_managed_members Evidence. | — |
| `inspect_managed_artifact` | Inspect an explicit PE/CLI path, or the selected managed target, without loading or executing target code. | — |
| `inspect_managed_members` | Inspect PE/CLI metadata members, signatures, raw CIL hashes, decoded-instruction-tuple hashes, separately reported exception regions, call edges, fie… | — |
| `inspect_managed_native_boundaries` | Inspect PE/CLI ModuleRef, ImplMap/PInvoke declarations, CLI native-header indicators, and non-IL method implementation flags without loading or execu… | — |
| `project_managed_application_graph` | Project authenticated managed artifact, member, and native-boundary Evidence into the provider-neutral application graph without executing managed co… | 只读 / 不执行目标 |
| `verify_managed_native_boundaries` | Verify managed P/Invoke/native-boundary declarations against authenticated native export or function Evidence without executing managed code or trans… | 只读 / 不执行目标 |

### JavaScript 与 Electron（18）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `analyze_javascript_application` | Reconstruct one local ASAR or extracted JavaScript application as an inline application graph without executing it. | 只读 / 不执行目标 |
| `analyze_web_bundle` | Capture JavaScript source from one selected CDP page and statically derive a chunk graph, route and endpoint candidates, vendor fingerprints, page-de… | — |
| `capture_electron_scenario` | Use this for a provider-owned Electron run when passive CDP or Inspector observation cannot exercise application behavior. | — |
| `compare_application_versions` | Compare two authenticated JavaScript Application Graph versions supplied as inline Evidence or exact same-session retained references. | — |
| `compare_javascript_export_shapes` | Compare static return shapes for one exact module/export selector on each authenticated JavaScript Application Graph supplied as inline Evidence or e… | 只读 / 不执行目标 |
| `compare_source_to_bundle` | Compare a cryptographically committed HistoricalSourceGraph with authenticated JavaScript Application Graph Evidence supplied inline or by exact same… | — |
| `export_web_scripts` | Export JavaScript bytes already retained in one local inspect_web_page or capture_browser_scenario JSON capture (normalized result or complete Eviden… | — |
| `inspect_electron_fuses` | Inspect packaged Electron fuse bytes in one local macOS app bundle, Electron Framework binary, Windows PE executable, or Linux ELF executable. | 只读 / 不执行目标 |
| `inspect_electron_page` | Passively inspect one Electron file page by supplying its loopback CDP endpoint and target ID. | — |
| `list_electron_targets` | List every Electron file:// page target from a selected loopback CDP endpoint. | — |
| `list_javascript_runtime_targets` | List every eligible Node/Electron V8 Inspector target from an explicit literal-loopback endpoint. | — |
| `observe_javascript_runtime` | Attach passively to one Node/Electron V8 Inspector target by supplying its loopback Inspector endpoint and target ID. | — |
| `reconcile_javascript_runtime` | Reconcile verified static JavaScript application graphs with existing passive web/Electron CDP, passive V8 Inspector, or provider-owned active Electr… | — |
| `recover_javascript_sources` | Recover readable modules from local UTF-8 JavaScript scripts/bundles into an absent directory, using caller-supplied Wakaru ^1.13.0 (verified with 1.… | — |
| `trace_application_feature` | Trace a typed literal seed through every reachable part of an authenticated JavaScript Application Graph supplied as inline Evidence or exact same-se… | — |
| `trace_javascript_semantics` | Trace static JavaScript data-flow, direct call/return, and closure relations from inline application Evidence or an exact same-session retained refer… | — |
| `trace_web_module_imports` | Trace one exported website script's outgoing native ES imports/re-exports, using exact URL and optional selected import-map context. | — |
| `trace_web_source_location` | Trace one generated position in an exported website script through an explicitly paired local source map. | — |

### 浏览器观察与场景录制（10）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `capture_browser_scenario` | Run a controlled browser scenario when passive observation cannot exercise the application. | — |
| `capture_web_screenshot` | Capture the current visible viewport of one configured page as an inline, content-addressed PNG artifact. | — |
| `compare_web_captures` | Compare passive web captures by providing before and after, each with the complete inspect_web_page normalized_result in inspection and an optional c… | — |
| `compare_web_screenshots` | Compare two self-verifying PNG screenshot artifacts with local pixel metrics. | — |
| `discover_webmcp_tools` | Passively inventory every page-registered WebMCP tool and its complete structural input-schema summary using the experimental CDP WebMCP domain. | — |
| `inspect_web_event_listeners` | Inspect listeners registered directly on the first main-document CSS match in one selected CDP page. | — |
| `inspect_web_page` | Passively inspect one selected page target through CDP without evaluating JavaScript, navigating, clicking, closing, or mutating the page. | — |
| `list_browser_targets` | List page targets exposed by the selected loopback Chrome DevTools Protocol endpoint. | — |
| `observe_web_execution` | Instrument one selected CDP page for a finite, externally driven precise coverage window. | — |
| `observe_web_session` | Arm a CDP observation window of the requested duration while the user operates the page. | — |

### Android 与移动设备（39）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `capture_adb_screen` | Capture one frame of the device screen as a PNG (`screencap -p` through exec-out, no device-side file) into a caller-selected output directory, diges… | — |
| `collect_adb_bugreport` | Collect one device-generated bugreport archive (`adb bugreport`) into a caller-selected output directory, digesting the zip. | 只读 / 不执行目标 |
| `decode_android_resources` | Decode one local APK's resources with `apktool d --no-src` in a provider-owned workspace that is removed after projection: the readable AndroidManife… | — |
| `decompile_jeb_item` | Decompile one type or method to engine pseudo-code using its decompiler (Dalvik, Java, or native). | 只读 / 不执行目标 |
| `identify_flutter_build` | Identify a Flutter app's build facts by pure parsing: the Dart VM snapshot hash from every lib/<abi>/libapp.so AOT section (vm and isolate, cross-che… | — |
| `inspect_adb_client` | Inspect the caller-selected adb client: resolved binary, version, and install path. | — |
| `inspect_adb_device` | Inspect one device's build identity through a fixed `getprop` whitelist: Android and SDK versions, security patch, fingerprint, product identity, CPU… | 只读 / 不执行目标 |
| `inspect_adb_display` | Report the display's physical and any overridden size (`wm size`) and density (`wm density`) as the device declares them. | 只读 / 不执行目标 |
| `inspect_adb_package` | Inspect one installed package through `dumpsys package`: version name/code, install and update times, installer, user id, flags, and the requested-pe… | 只读 / 不执行目标 |
| `inspect_adb_window` | Report the window manager's focus declarations with display context, original lines and explicit summary status. | 只读 / 不执行目标 |
| `inspect_android_class` | Inspect one exact Android class's parsed methods, fields and inner classes, including synthetic members. | — |
| `inspect_android_method` | Decompile one Android method with smali fallback. | — |
| `inspect_android_package` | Inspect a local APK's package, SDK and permission declarations, decoded manifest and class/resource counts. | 只读 / 不执行目标 |
| `inspect_dart_aot` | Inspect one ABI's Dart AOT snapshot inside an APK: the four snapshot symbols located through the ELF dynamic symbol table with their offsets, sizes… | — |
| `inspect_jeb_client` | Inspect the running JEB client serving MCP: engine version, GUI or headless mode, and startup time. | — |
| `install_adb_package` | Install one local APK on the device (`adb install [-r]`), recording the APK's host digest and byte size. | 改写目标设备状态 |
| `list_adb_devices` | List attached devices exactly as `adb devices -l` reports them: serial, state, transport, model metadata, and an inferred emulator/physical kind with… | — |
| `list_adb_directory` | List the immediate children of one absolute device directory, including hidden entries: names, kinds, permissions, owner, group, sizes, dates, and sy… | 只读 / 不执行目标 |
| `list_adb_features` | List the device's declared hardware and software features (`pm list features`) for device fingerprinting. | 只读 / 不执行目标 |
| `list_adb_packages` | List installed packages on one device with each base APK's device path, optionally scoped to third-party or system packages. | 只读 / 不执行目标 |
| `list_adb_processes` | List running processes exactly as `ps -A` reports them: user, pid, ppid, rss, state, and name. | 只读 / 不执行目标 |
| `list_adb_services` | List the device's binder services with their interfaces (`service list`). | 只读 / 不执行目标 |
| `list_jeb_units` | List project units by stable unit path and type, with optional wildcard filter, parent restriction, and pagination. | 只读 / 不执行目标 |
| `open_jeb_project` | Open or create a JEB project from an artifact file or existing .jdb2 database on the engine host. | — |
| `project_android_application_graph` | Project authenticated APK inventory_artifact Evidence into an execution-free Android application inventory. | — |
| `project_harmony_application_graph` | Project authenticated HarmonyOS HAP, HSP, or App Pack inventory Evidence into an execution-free application inventory. | — |
| `pull_adb_file` | Pull one absolute device path (a database, shared-preferences XML, or any readable file) into a caller-selected output directory, digesting it with S… | 只读 / 不执行目标 |
| `pull_adb_package` | Pull one installed package's complete APK set (base plus every split, as `pm path` reports) from the device into a caller-selected output directory… | — |
| `push_adb_file` | Push one local file to an absolute device path. | 改写目标设备状态 |
| `read_adb_logcat` | Read a bounded dump of the device log (`logcat -d -t`) for one buffer, optionally restricted to a process id. | 只读 / 不执行目标 |
| `read_adb_setting` | Read one settings value (`settings get`) from the system, secure, or global namespace. | 只读 / 不执行目标 |
| `resolve_adb_packages` | Find installed packages by case-insensitive substring of the package name (e.g. | 只读 / 不执行目标 |
| `search_android_classes` | Search complete top-level decompiler class-name rows in an explicit local APK by case-sensitive substring. | — |
| `start_adb_activity` | Start an intent with `am start -W`: one action, optional data URI, optional explicit component, and up to 16 typed extras (string, boolean, int, long… | 改写目标设备状态 |
| `start_adb_app` | Start one installed app's resolved launcher activity with `am start -W -n`. | 改写目标设备状态 |
| `stop_adb_app` | Force-stop every process of one package (`am force-stop`), ending a dynamic-analysis run. | 改写目标设备状态 |
| `trace_android_references` | Trace incoming static using nodes to an exact Android class or selected method overload. | — |
| `uninstall_adb_package` | Request package removal for user 0 (`adb shell pm uninstall --user 0`) without data retention. | 改写目标设备状态 |
| `inspect_apktool_client` | Inspect the caller-selected apktool launcher: resolved command, selection source, and version. | — |

### Apple 平台（17）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `analyze_swift_types` | Categorize analyzed Swift procedure names using their manglings or same-address Swift symbol aliases. | — |
| `capture_native_ui_scenario` | Run selected-element press, increment/decrement scroll, AXValue text entry and bounded wait steps in one exact native app window. | 启动进程、可能弹 UI、可能联网、可能写文件（本机不可用） |
| `decode_interface_builder` | Decode compiled storyboard and nib archives inside the active Apple app bundle, including keyed property lists and NIBArchive object tables, into a b… | — |
| `demangle_swift` | Demangle an ordered list of single-line Swift symbols without requiring Hopper. | 启动进程（本机不可用） |
| `get_objc_classes` | Discover and deduplicate Objective-C class labels, optionally filtering by literal substring. | — |
| `get_objc_protocols` | Discover and deduplicate Objective-C and Swift protocol labels. | — |
| `inspect_asset_catalog` | Inspect compiled Assets.car metadata in an active Apple app bundle. | 启动进程（本机不可用） |
| `inspect_keyed_archive` | Inspect one Foundation NSKeyedArchiver plist in the active app bundle as original object-table nodes, class descriptors, named roots, and UID edges. | — |
| `inspect_macho` | Inspect Mach-O slices, load commands, imports, exports, dependencies, build metadata, segments, sections, permissions, and exact command provenance w… | 启动进程（本机不可用） |
| `inspect_plist` | Parse Info.plist from the active artifact by default, or pass any local plist path. | 启动进程（本机不可用） |
| `inspect_signature` | Inspect the active Mach-O executable's code-signing identity, hashes, authorities, requirements, entitlements, hardened-runtime state, and exact comm… | 启动进程（本机不可用） |
| `list_architectures` | List thin or universal Mach-O slices with offsets, sizes, alignment, explicit coverage, and native-tool provenance. | 启动进程（本机不可用） |
| `observe_native_calls` | Launch the active Mach-O as an owned process under LLDB and record each entry into caller-selected functions or Objective-C methods: thread, module… | 启动进程、可能弹 UI、可能联网、可能写文件（本机不可用） |
| `observe_native_ui` | Observe an already-running native app by PID and window ID, bound to the active Mach-O target. | 启动进程、可能写文件（本机不可用） |
| `project_apple_application_graph` | Project authenticated IPA, macOS .app directory, ZIP, or DMG inventory Evidence into an execution-free Apple application inventory. | — |
| `trace_dylib_resolution` | Trace how dyld would resolve each Mach-O dylib load for the active Mach-O, or for every executable in the active .app bundle (the main app, XPC servi… | — |
| `trace_native_ui_action` | Trace one unique compiled UI action, object ID, native symbol or exact function address through authored connections, encoded or symbolized Objective… | — |

### 归档·固件·格式（11）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `compare_artifacts` | Compare complete artifact inventories by logical occurrence path, content identity, metadata, and graph relations. | — |
| `compare_wasm_interfaces` | Compare typed core WASM import/export names, kinds and exact signatures from two authenticated inspect_wasm_artifact Evidence records. | — |
| `extract_artifact` | Extract all regular files from the active archive or application package into a fresh temporary directory chosen by REA. | 启动进程、可能写文件 |
| `extract_firmware` | Extract caller-selected firmware bytes with Unblob 26.6.x (verified with 26.6.4) into an absent output directory. | — |
| `inspect_artifact` | Inspect an active archive or application package in one call. | 启动进程、可能写文件 |
| `inspect_evm_interface` | Inspect explicit local flat EVM bytecode without target execution or chain/RPC access. | — |
| `inspect_firmware_regions` | Inspect signature candidates in a local firmware file with Binwalk 3.1.x (verified with 3.1.0). | — |
| `inspect_pe_resources` | Inspect one explicit local PE32/PE32+ image's complete bounded type/name/language resource tree without executing it or opening a disassembler. | 只读 / 不执行目标 |
| `inspect_recorded_crash` | Inspect a supplied Linux ELF64 amd64 or AArch64 little-endian core without launching its target or attaching to any live PID. | — |
| `inspect_sqlite_database` | Inspect an explicit local SQLite database snapshot and its existing sibling WAL without modifying source files or opening a native analysis provider. | 启动进程、可能写文件（本机不可用） |
| `inspect_wasm_artifact` | Validate an explicit local WASM artifact with caller-supplied WABT 1.0.42. | — |

### 网络与信号采集（7）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `decode_signal_recording` | Decode an existing local logic/signal recording on Linux with sigrok-cli 0.7.2 and util-linux prlimit. | — |
| `inspect_packet_capture` | Inspect caller-selected fields in an existing local packet capture with TShark 4.x. | — |
| `inspect_packet_fields` | Discover protocols or field names/types registered in the installed TShark 4.x. | — |
| `inspect_pcap_capture` | Request detail summary for capture identity/counts, then page retained facts with inspect_analysis_view kind pcap. | — |
| `inspect_pcap_client` | Inspect the caller-selected tshark and capinfos binaries: selected commands, selection sources, and versions. | — |
| `inspect_signal_decoders` | Discover installed sigrok protocol decoders or inspect one decoder's channel/option help on Linux. | — |
| `inspect_web_network_capture` | Request detail summary for capture identity and counts; then page retained records with inspect_analysis_view kind capture (preview or complete), avo… | — |

### 调试器与插桩（22）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `capture_process_scenario` | Run one caller-selected command under a PTY and return process capture Evidence with residual unknowns. | 可能启动进程 / 联网 / 写文件 |
| `close_frida_session` | Unload session scripts and detach REA's Frida session. | — |
| `close_gdb_session` | Close the owned GDB process after verifying the inferior state. | — |
| `close_rizin_debug_session` | Close the REA-owned Rizin debugger only after verifying no inferior remains or detaching one with a verified caller-selected TTY output sink. | — |
| `compare_process_captures` | Compare two compatible process capture observations across terminal, interaction, lifecycle, process, filesystem, command-shim, HTTP, and WebSocket e… | — |
| `cutter_command` | Run one arbitrary Rizin command in a selected live Cutter session. | — |
| `execute_rizin_command` | Execute one caller-selected Rizin command against a local artifact using the Rizin CLI profile that suppresses user settings and scripts while retain… | — |
| `frida_session_status` | Return observed Frida session state and queued script messages. | — |
| `gdb_console` | Run one unrestricted GDB CLI command through MI interpreter-exec console and return raw MI, console, target, and log records inline with Evidence. | — |
| `gdb_session_status` | Return the observed lifecycle state and bounded recent MI records and process diagnostics for one persistent REA GDB session; truncation and invalid-… | — |
| `instrument_with_frida` | Run one caller-authored Frida script against an explicitly selected process and detach when the observation window ends. | — |
| `list_cutter_sessions` | List live REA bridge sessions hosted by upstream Cutter instances, including observed document identity and bridge-directory security status. | — |
| `list_frida_devices` | List Frida devices currently available to this host, optionally connecting to the caller-selected remote Frida endpoint. | — |
| `list_frida_processes` | List processes observed on a selected Frida device or caller-supplied remote endpoint. | — |
| `load_frida_script` | Load caller-supplied JavaScript into a Frida session. | — |
| `resume_frida_session` | Resume the process created by a paused Frida spawn session. | — |
| `rizin_debug_command` | Execute one unrestricted command in a persistent Rizin debugger session. | — |
| `rizin_debug_session_status` | Return observed lifecycle state and bounded recent NUL-framed output and process diagnostics for one Rizin debugger session; truncation fields report… | — |
| `start_frida_session` | Attach Frida to one selected process or spawn one selected target. | — |
| `start_gdb_session` | Start a BYO GDB process in MI3 mode when available, suppress startup files, and disable auto-loading. | — |
| `start_rizin_debug_session` | Start a persistent Rizin debugger session using `-N` to suppress user settings and scripts while retaining plugins, `-0` for NUL framing, and `-d` wi… | — |
| `unload_frida_script` | Unload one caller-selected Frida script from a live session. | — |

### 证据与验证（13）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `build_reconstruction_obligation_ledger` | Generate the complete deterministic ReconstructionObligationLedger from an authenticated Evidence bundle, reviewed obligations, and an explicit recon… | — |
| `compare_bundles` | Compare two canonical Evidence bundles by exact record membership, explicit one-to-one observation pairs, and complete residual-unknown revision hist… | — |
| `correlate_static_and_runtime` | Evaluate every explicit caller-declared hypothesis between exact static comparison findings and runtime comparison dimensions. | — |
| `evaluate_reconstruction_coverage` | Evaluate inline evidence-backed reconstruction coverage against one named boundary. | — |
| `export_evidence_bundle` | Atomically write the session's deterministic Evidence bundle to the requested local path. | — |
| `find_changed_behavior` | Aggregate validated process and artifact comparison Evidence. | — |
| `get_evidence_bundle` | Return every retained Evidence record and residual unknown as a complete canonical bundle by default. | — |
| `import_evidence_bundle` | Read the JSON bundle at the supplied local path, validate every Evidence ID and canonical manifest, then atomically merge it. | — |
| `list_unknowns` | List current residual-unknown heads in deterministic ID order, with optional exact status, severity, and domain filters. | 只读 / 不执行目标 |
| `record_unknown` | Create one deterministic residual unknown and immutable mutation evidence. | — |
| `update_unknown` | Append one immutable full-state revision and mutation evidence. | — |
| `verify_reconstruction` | Verify a finite typed behavioral and structural specification against a canonical Evidence bundle. | — |
| `verify_unknown_resolution` | Revalidate the current residual-unknown head against live bundled evidence, exact authority/confidence/environment requirements, and revision integri… | — |

## CLI 命令（153）

来自 `rea --llms`（156 行表格，此处原样转三列去掉参数细节；参数级细节跑 `rea <command> --schema`）。

| 命令 | 用途 |
| --- | --- |
| `rea address-to-file-offset <path> <address>` | Resolve an analysis address to its original file byte offset |
| `rea analyze <path>` | Get an overview of an app |
| `rea analyze-javascript-application <path>` | Statically reconstruct a local JavaScript/Electron application |
| `rea analyze-web-bundle <endpoint> <targetId>` | Capture and statically analyze a page bundle, defaulting to the selected target origin |
| `rea annotate-native-function <path> <procedure>` | Edit function annotations and return refreshed analysis |
| `rea build-reconstruction-obligation-ledger <inputJson>` | Generate a deterministic Evidence-backed reconstruction obligation ledger page |
| `rea capabilities` | List provider capabilities and side effects |
| `rea capture-adb-screen <serial>` | Capture one screen frame as a digested PNG |
| `rea capture-browser-scenario <inputJson>` | Run one bounded Playwright browser scenario and return Evidence |
| `rea capture-electron-scenario <inputJson>` | Run one owned Electron scenario with cancellable actions |
| `rea capture-native-ui-scenario <path>` | Run declarative AX actions or waits in one exact native application window |
| `rea capture-process <scenario>` | Capture one caller-selected process scenario |
| `rea capture-web-screenshot <endpoint> <targetId>` | Capture one visible page viewport within the supplied origin scope |
| `rea collect-adb-bugreport <serial>` | Collect and digest one device-generated bugreport archive |
| `rea compare <left> <right>` | Compare two canonical Evidence bundles |
| `rea compare-application-versions <inputJson>` | Compare two authenticated JavaScript Application Graph versions |
| `rea compare-javascript-export-shapes <inputJson>` | Compare exact static JavaScript export return shapes without execution |
| `rea compare-managed-members <leftPath> <rightPath>` | Compare managed PE/CLI member inventories by exact declared type, name, and signature; names alone never form a match |
| `rea compare-process-captures <left> <right> [traceSpec]` | Compare two process capture Evidence JSON files |
| `rea compare-source-to-bundle <inputJson>` | Compare committed historical source with authenticated application Evidence |
| `rea compare-wasm-interfaces <input>` | Compare core WASM interfaces from two exact inspection Evidence records |
| `rea compare-web-captures <beforeJson> <afterJson>` | Compare two normalized passive captures or recorded browser scenarios |
| `rea compare-web-screenshots <beforeJson> <afterJson>` | Compare two self-verifying PNG artifact JSON values |
| `rea cutter-command <sessionId> <expectedGeneration> <command>` | Execute one Rizin command in a selected live Cutter instance |
| `rea debug-with-gdb <command>` | Run one unrestricted GDB console command in an ephemeral MI session; provide an inferior TTY so a live target can be safely detached |
| `rea debug-with-rizin <path> <command>` | Run one unrestricted Rizin debugger command in an ephemeral session |
| `rea decode-android-resources <path>` | Decode one APK's manifest, metadata, and string resources with apktool |
| `rea decode-interface-builder <path>` | Decode compiled storyboard and nib archives from an app bundle |
| `rea decode-signal-recording <path>` | Decode an existing signal recording with caller-supplied sigrok |
| `rea decompile <path> [address]` | Read one part of an app as code |
| `rea decompile-jeb-item <item-address> <item-kind>` | Decompile one JEB type or method to engine pseudo-code |
| `rea demangle-swift <path> <symbols...>` | Demangle Swift symbols without Hopper |
| `rea discover-webmcp-tools <endpoint> <targetId>` | Passively discover page-declared WebMCP tools |
| `rea doctor` | Check whether REA is ready |
| `rea evaluate-reconstruction-coverage <inputJson>` | Evaluate inline fail-closed reconstruction coverage |
| `rea evidence-export <source> <output>` | Validate and atomically export canonical Evidence JSON |
| `rea evidence-import <path>` | Validate and import a bounded local Evidence bundle |
| `rea execute-rizin-command <path> <command>` | Execute one Rizin command against a local artifact |
| `rea export-web-scripts <capturePath> <outputDirectory>` | Export retained website scripts into an absent directory for static JavaScript analysis |
| `rea extract-artifact <path>` | Extract all regular artifact contents safely |
| `rea extract-firmware <path> <outputDirectory>` | Extract selected firmware bytes and return verified files and provenance |
| `rea function <path> [address]` | Analyze one complete function with evidence |
| `rea identify-flutter-build <path>` | Identify a Flutter build's Dart snapshot hash and engine facts by pure APK parsing |
| `rea import-managed-reconstruction <inputJson>` | Import decompiler-produced managed reconstruction against exact static member evidence |
| `rea import-reference-source <root>` | Import a source tree as historical reference only |
| `rea inspect <path>` | Inspect an app overview with evidence |
| `rea inspect-adb-client` | Inspect the caller-selected adb client without contacting devices |
| `rea inspect-adb-device <serial>` | Inspect one device's build identity through a fixed getprop whitelist |
| `rea inspect-adb-display <serial>` | Report the display's declared size and density |
| `rea inspect-adb-package <serial> <package>` | Inspect one installed package's version, installer, and flags through dumpsys |
| `rea inspect-adb-window <serial>` | Report the window manager's current focus declarations |
| `rea inspect-analysis-view <inputJson>` | Project a selected view of completed binary-layout, JavaScript application, native function, artifact-inventory, WASM, Mach-O, Interface Builder, EVM, managed, Android package, Dart AOT, web network capture or pcap Evidence JSON |
| `rea inspect-android-class <path> <className>` | Inspect one exact APK class's member inventory |
| `rea inspect-android-method <path> <className> <methodName>` | Decompile one APK method with explicit overload selection |
| `rea inspect-android-package <path>` | Inspect APK declarations and decoded manifest without executing it |
| `rea inspect-apktool-client` | Inspect the caller-selected apktool launcher without decoding anything |
| `rea inspect-artifact <path>` | Inspect one artifact and return all available observations and next probes |
| `rea inspect-asset-catalog <path>` | Inspect compiled Apple asset catalog metadata |
| `rea inspect-binary-layout <path>` | Inspect binary file/linked layout without executing the selected object |
| `rea inspect-dart-aot <path>` | Inspect one ABI's Dart AOT snapshot: sections, headers, and the string pool |
| `rea inspect-electron-fuses <path>` | Inspect packaged Electron fuse bytes without launching the application |
| `rea inspect-electron-page <endpoint> <targetId>` | Passively inspect one Electron file page |
| `rea inspect-evidence-bundle <inputJson>` | Inspect complete or selected discovery metadata from a local Evidence bundle |
| `rea inspect-evm-interface <path> <encoding>` | Infer interface candidates from explicit local EVM bytecode |
| `rea inspect-firmware-regions <path>` | Inspect firmware signature candidates without extracting them |
| `rea inspect-go-binary <path>` | Inspect embedded Go compiler, modules and build settings without target execution |
| `rea inspect-jeb-client` | Inspect the running JEB MCP client without opening a target |
| `rea inspect-keyed-archive <path> [archive]` | Inspect a Foundation keyed archive as an object-reference graph |
| `rea inspect-macho <path>` | Run inspect_macho without launching Hopper |
| `rea inspect-managed-artifact <path>` | Inspect PE/CLI identity without loading target code |
| `rea inspect-managed-members <path>` | Inspect PE/CLI metadata members, signatures, CIL anchors, and ldstr string literals without loading target code |
| `rea inspect-managed-native-boundaries <path>` | Inspect PE/CLI PInvoke and native implementation boundary declarations without loading target code |
| `rea inspect-native-api <path> <address>` | Reconstruct one native function API boundary with evidence |
| `rea inspect-native-data-type <path>` | Inspect one recovered database type or typed data object |
| `rea inspect-native-dispatch-metadata <path>` | Inspect typed Objective-C and Swift dispatch metadata |
| `rea inspect-native-instruction <path> <address>` | Inspect one native instruction with decoded operand facts |
| `rea inspect-native-load-image <path>` | Verify loaded native bytes, source mappings, relocations and entry |
| `rea inspect-packet-capture <path>` | Inspect an existing packet capture with caller-supplied TShark |
| `rea inspect-packet-fields` | Search installed TShark protocol and field definitions |
| `rea inspect-pcap-capture <path>` | Inspect one pcap/pcapng capture: endpoints, DNS, TLS SNI, and protocol distribution |
| `rea inspect-pcap-client` | Inspect the caller-selected tshark and capinfos binaries without reading a capture |
| `rea inspect-pe-resources <path>` | Inspect PE resource identities, payload ranges, hashes and icon-group relationships |
| `rea inspect-plist <path>` | Parse app plist metadata without launching Hopper |
| `rea inspect-recorded-crash <path>` | Inspect supplied core registers/signals and optional debugger mapping evidence |
| `rea inspect-rust-binary <path>` | Inspect an embedded cargo-auditable Rust dependency list without target execution |
| `rea inspect-signal-decoders` | Search installed sigrok decoders or selected decoder help |
| `rea inspect-signature <path>` | Run inspect_signature without launching Hopper |
| `rea inspect-sqlite-database <path>` | Inspect SQLite schema and optional ordinary-table rows from a local snapshot |
| `rea inspect-wasm-artifact <path>` | Inspect an explicit local WASM artifact with WABT |
| `rea inspect-web-event-listeners <endpoint> <targetId> <selector>` | Inspect native listener source locations on the first main-document CSS match |
| `rea inspect-web-network-capture <capturePath> <format>` | Inspect retained HAR, native mitmproxy, Fiddler SAZ or aioquic qlog records without fetching recorded URLs |
| `rea inspect-web-page <endpoint> <targetId>` | Passively inspect one page through CDP, defaulting to its current origin |
| `rea inspect-with-objdump <path> <operation>` | Inspect a local artifact with GNU objdump and retain its raw output as Evidence |
| `rea install-adb-package <serial> <apk-path>` | Install one local APK; --replace requests reinstall mode to keep existing app data |
| `rea instructions <path> [address]` | Read every raw instruction without decompiling |
| `rea instrument-with-frida <mode> <target>` | Run one Frida script against a selected process and detach |
| `rea list-adb-devices` | List attached devices with serial, state, transport, and inferred kind |
| `rea list-adb-directory <serial> <device-path>` | List one device directory with kinds, permissions, and sizes |
| `rea list-adb-features <serial>` | List the device's declared hardware and software features |
| `rea list-adb-packages <serial>` | List installed packages on one device with base APK device paths |
| `rea list-adb-processes <serial>` | List running processes exactly as ps -A reports them |
| `rea list-adb-services <serial>` | List the device's binder services and interfaces |
| `rea list-architectures <path>` | Run list_architectures without launching Hopper |
| `rea list-browser-targets <endpoint>` | List page targets from a selected loopback CDP browser, optionally filtered by origin |
| `rea list-cutter-sessions` | List live Cutter instances connected through the REA Python plugin bridge |
| `rea list-electron-targets <endpoint>` | List local file pages exposed by the selected Electron CDP endpoint |
| `rea list-frida-devices` | List local Frida devices and an optional remote endpoint |
| `rea list-frida-processes` | List processes visible through a Frida device |
| `rea list-javascript-runtime-targets <endpoint>` | List Node/Electron V8 Inspector targets |
| `rea list-jeb-units` | List JEB project units by path and type with optional filter |
| `rea list-objdump-architectures` | List BFD targets advertised by the installed GNU objdump |
| `rea observe-javascript-runtime <endpoint> <targetId>` | Passively observe one exact Node/Electron Inspector target |
| `rea observe-native-calls <path> <inputJson>` | Launch a Mach-O under LLDB and record entries into selected functions or Objective-C methods |
| `rea observe-native-ui <path>` | Observe one already-running native application window by PID and window ID |
| `rea observe-web-execution <endpoint> <targetId>` | Observe precise page execution; resets counters and temporarily disables optimization |
| `rea observe-web-session <endpoint> <targetId>` | Observe user-driven page navigation during a chosen window |
| `rea open-jeb-project <path>` | Open or create a JEB project from an artifact or .jdb2 database |
| `rea project-android-application-graph <inputJson>` | Project authenticated APK inventory Evidence into an Android application graph |
| `rea project-apple-application-graph <inputJson>` | Project authenticated IPA or macOS app inventory Evidence into an Apple application graph |
| `rea project-harmony-application-graph <inputJson>` | Project authenticated HarmonyOS HAP, HSP, or App Pack inventory Evidence into an application graph |
| `rea project-managed-application-graph <inputJson>` | Project authenticated managed static Evidence into an application graph |
| `rea providers` | List configured analysis providers |
| `rea pull-adb-file <serial> <device-path>` | Pull one device file to a local copy with a SHA-256 digest |
| `rea pull-adb-package <serial> <package>` | Pull one installed package's complete APK set with SHA-256 digests |
| `rea push-adb-file <serial> <local-path> <device-path>` | Push one local file to the device; refuses existing targets without --overwrite |
| `rea read-adb-logcat <serial>` | Read a bounded dump of the device log for one buffer |
| `rea read-adb-setting <serial> <namespace> <key>` | Read one settings value from system, secure, or global |
| `rea read-bytes <path> <address>` | Read exact provider memory bytes at one analysis address |
| `rea reconcile-javascript-runtime <inputJson>` | Reconcile static application and passive runtime Evidence JSON |
| `rea recover-javascript-sources <path> <outputDirectory>` | Recover readable JavaScript modules with source provenance and verified files |
| `rea resolve-adb-packages <serial> <query>` | Find installed packages by case-insensitive name substring |
| `rea resolve-native-call-targets <path> <address>` | Resolve one static native call site |
| `rea search <path> [pattern]` | Search every analyzed string or procedure name |
| `rea search-android-classes <path> <query>` | Search APK class names; empty query inventories all classes |
| `rea search-bytes <path> <pattern>` | Find masked byte patterns in initialized provider memory |
| `rea setup` | Configure agent integrations and optional analysis providers |
| `rea start-adb-activity <serial> <action>` | Start an intent with am start (action, URI, component, extras) |
| `rea start-adb-app <serial> <package>` | Start one installed app by resolving and launching its launcher activity |
| `rea stop-adb-app <serial> <package>` | Force-stop every process of one package |
| `rea trace <path> [query]` | Trace a literal feature through analyzed references |
| `rea trace-android-references <path> <className>` | Trace incoming APK using nodes for a class or selected method |
| `rea trace-application-feature <inputJson>` | Trace a typed seed through authenticated application Evidence JSON |
| `rea trace-dylib-resolution <path>` | Trace dyld load-path resolution for a Mach-O or every executable in an app bundle |
| `rea trace-javascript-semantics <inputJson>` | Trace bounded static semantic relations through authenticated application Evidence |
| `rea trace-native-ui-action <path> <action>` | Trace a compiled UI action selector to its native handler and direct callees |
| `rea trace-native-values <path> <procedure>` | Trace bounded native def-use and call dependencies |
| `rea trace-web-module-imports <manifestPath> <scriptIndex>` | Trace one captured script's native imports to URLs and captured source candidates |
| `rea trace-web-source-location <manifestPath> <scriptIndex> <sourceMapPath> <sourceMapUrl> <line> <column>` | Trace one retained script position through an explicitly selected local source map |
| `rea uninstall` | Remove REA-owned agent configuration and skill files |
| `rea uninstall-adb-package <serial> <package>` | Uninstall one package and its data from the device |
| `rea update` | Update this REA installation and verify the installed release |
| `rea verify-managed-native-boundaries <inputJson>` | Verify managed P/Invoke declarations against authenticated native Evidence |
| `rea xrefs <path> [address]` | List bounded references to an analyzed address |

## 官方 prompt（6）

| prompt | 用途 |
| --- | --- |
| `investigate_feature` | Trace a feature through relevant artifact, symbol, and function evidence while distinguishing observations, inferences, and residual unknowns. |
| `compare_application_versions` | Compare two shipped application artifacts through complete inventory and optional static or runtime evidence without equating missing data with unchanged behavior. |
| `verify_reconstruction` | Evaluate a finite reconstruction specification against retained Evidence comparisons without broadening pass results into global equivalence claims. |
| `trace_crash` | Correlate a crash symptom with static call and reference evidence plus optional process capture observations. |
| `audit_residual_unknowns` | Review current residual-unknown heads against retained evidence, revision integrity, and declared authority without silently closing unanswered questions. |
| `prepare_bounded_process_capture` | Choose a command, inputs, observations, and stopping conditions for a process capture that answers the behavioral question. |

## 维护

- 重新生成的完整步骤见 `references/workflows/version-sync.md`（跑命令 → 覆盖本文件 → 旧版本文件保留）。
- 旧版本文件（如 `rea-6.6.0.md`）**保留不删**，用于回溯「当时这个工具叫什么」。
- 2026-10-19 修正：`inspect_apktool_client` 原被归入「其他（1）」（Android 分组规则缺 `apktool`）。已移入 Android 分组，计数 38 → 39，「其他」分组随之撤销；同时补记工具/prompt 子摘要。规则已同步修入 `references/specs/toolset-generation.md`。
