---
name: "rea-6.10.1 工具面快照"
description: "REA 6.10.1 的完整工具面：263 个 MCP 工具、6 个官方 prompt、204 条 CLI 命令，逐条给用途与副作用/可用性，并写明 CLI 名与 MCP 名不是一一对应。"
version: 6.10.1
generated-at: 2026-11-26T00:08:03+08:00
generated-by: "rea mcp doctor --json；rea-agents@6.10.1 包内 dist/mcp-catalog.json（tools/prompts）；rea --llms；rea capabilities --format json"
trigger-when: 需要查「REA 有哪些工具」「某个能力用哪个工具」「这个工具有什么副作用或前置」时
reads-from: SKILL.md
---

# REA 6.10.1 工具面快照

## 版本锚

| 项 | 值 | 来源 |
| --- | --- | --- |
| REA CLI 版本 | 6.10.1 | `rea --version` |
| 包 / 协议 | rea-agents@6.10.1 / MCP 2025-11-25 | `rea mcp doctor --json` |
| MCP 工具 | 263（expected=263 observed=263，missing/unexpected/duplicates 全空） | 同上 |
| 官方 prompt | 6 | 同上 |
| 目录摘要 | `62c90a6f14e5bca55fd374cf47de20008f65d740f3d3c631fb0821905fc46744` | 同上 → `identity.observed_catalog_digest` |
| 工具目录摘要 | `ce195f28c7f286af9ee1a4174e5a9d54eda490e95a913c48592316740bd34bf1` | `rea capabilities --format json` → `server_identity.catalog.digests.tools_sha256` |
| prompt 目录摘要 | `60078bd8ef8bd152b51440e7579fba2059beec18fec5148dd0ec10ef013213fe` | 同上 → `prompts_sha256` |
| CLI 命令 | 204 条（`rea --llms` 表格行数；判漂移看命令条数与版本锚，别看字符数） | `rea --llms` |

**有效期**：本文件按 REA 版本生成；官方发布节奏快，升级后按 `references/workflows/version-sync.md` 重新生成，**不要手改本文件**。

## 名称映射（先读这段，别按名字猜工具）

宿主里的 REA 工具通常以 `mcp__rea__<tool>` 出现；**CLI 命令名与 MCP 工具名不是一一对应**，同一能力两侧可能叫不同名字：

| CLI 命令 | 对应 MCP 工具（示例） |
| --- | --- |
| `rea function <path> <symbol>` | `analyze_function` |
| `rea instructions` | `read_function_instructions` |
| `rea search` | `search_strings / search_procedures` |
| `rea inspect <path>` | `binary_overview（总览）/ inspect_analysis_view（读已保留证据）` |
| `rea trace <literal>` | `trace_feature` |
| `rea evidence-export / evidence-import` | `export_evidence_bundle / import_evidence_bundle` |
| `rea analyze-javascript-application` | `analyze_javascript_application` |

要确认当前真实工具名，用宿主自己的工具列表或 `rea mcp doctor --json --full-output`，**不要凭本文件的手工推断去调工具**。

## MCP 工具（263）

### 会话与目标（43）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `act_on_build_computer` | Act on a running build computer with screenshot, click, drag, scroll, type, type_secret, key, wait, reset; actions can change app state.… | — |
| `address_name` | Resolve the primary analyzed name at a code or data address. Headless providers require an explicit address; GUI providers may default to… | — |
| `address_to_file_offset` | Map one provider-normalized virtual address to its original nonnegative file offset. The mapping is for that address; it does not imply a… | — |
| `binary_overview` | Summarize the bound document, complete provider-inventory procedure/string row counts, and segments when supported. Counts do not establi… | — |
| `binary_session` | Inspect current target, provider capabilities, analysis and server identity without starting analysis. Default summary reports Ghidra che… | — |
| `check_build_task` | Evaluate saved-state task checks or run a screen_judge through its configured model endpoint on a running exported app. Returns per-check… | — |
| `close_binary` | Release the active engine and owned resources while retaining investigation Evidence and complete Unknown history in memory. Drains earli… | — |
| `close_build_computer` | Tear down a build computer and discard its state, cancelling its active call and refusing queued calls. Tries agentenv first, then REA_DO… | — |
| `comment` | Read the regular analysis comment at an explicit address, or the current cursor where supported. Returns null when absent; use set_commen… | — |
| `current_address` | Return Hopper's current cursor address for the selected document. Use only for interactive navigation state; prefer explicit addresses in… | — |
| `current_document` | Return the document currently selected by REA's Hopper bridge. | — |
| `current_procedure` | Return the analyzed procedure containing Hopper's current cursor. This uses GUI cursor state and is not a procedure-name lookup. | — |
| `export_build_environment` | Export the stopped capture and given tasks as an agentenv app bundle, seeded at seed. Each task uses its selected end checkpoint (end by… | — |
| `get_navigation_context` | Return the selected document, current address, and containing/current procedure in one provider-neutral result. The result reflects seque… | — |
| `goto_address` | Move Hopper's GUI cursor to a mapped address and return the observed cursor address. Interior coordinates snap to the containing analyzed… | — |
| `guided_workflows` | List or render REA's existing guided workflows. Rendering returns guidance only; it does not inspect targets, start analysis, or change s… | — |
| `inline_comment` | Read the inline instruction comment at an explicit address, or the current cursor where supported. Returns null when absent; use set_inli… | — |
| `inspect_address_context` | Inspect one explicit reproducible address for its analyzed name, containing procedure, regular and inline comments, and matching bookmark… | — |
| `inspect_analysis_settings` | Inspect REA's editable runtime admission sizes, deadlines and worker heaps, their bounds, launch values and application points. No active… | — |
| `list_bookmarks` | List every bookmark in the selected Hopper document as address and name pairs; unnamed bookmarks retain a null name. Use bookmarks as ana… | — |
| `list_documents` | List provider program or document identities. Hopper may expose several documents; a Ghidra headless session contains exactly its one imp… | — |
| `mark_build_checkpoint` | Checkpoint the running capture under a unique name; returns acknowledged counts and up to 10 changed files. Files named by window titles… | — |
| `measure_build_task` | Measure how hard an exported bundle's task is for a model: run it in fresh agentenv computers on this host, each solve the bundle's own s… | — |
| `next_address` | Return the next analyzed object address after an explicit address or current cursor. This is a navigation primitive, not instruction-flow… | — |
| `open_binary` | Open a validated local artifact or analysis database and bind its analysis provider. Switching target/provider can discard ephemeral Ghid… | — |
| `prev_address` | Return the previous analyzed object start before an explicit address or current cursor. This is a navigation primitive and may fail at do… | — |
| `read_bytes` | Read analyzed bytes from one provider-normalized virtual address. Ghidra reads initialized memory, which can include loader fixups; these… | — |
| `read_guidance_section` | Retrieve a section selected by search_guidance from the installed REA guidance bundle. Reports stale locators and unavailable bundles exp… | — |
| `record_build_consent` | Record a consent the person gave, in their own words, after you asked them: kind licence when they accepted a licence the app or its inst… | — |
| `reset_investigation` | Discard retained Evidence and Unknown revision history, including engine replay/source bindings, while keeping a healthy active engine op… | — |
| `resolve_containing_procedure` | Resolve an arbitrary address, including an interior instruction or exact external entry, to its provider-analyzed containing procedure. A… | — |
| `search_bytes` | Find masked byte signatures in initialized analyzed memory. Hex byte pairs and ?? wildcards are supported; an optional equal-length hex m… | — |
| `search_guidance` | Find installed REA workflow guidance by query words. Returns ranked sections, pages and locators for read_guidance_section; every non-gen… | — |
| `set_address_name` | Assign an analyst name to one mapped hexadecimal address and report whether the native edit succeeded and exact readback matched. Hopper… | — |
| `set_addresses_names` | Assign analyst names to multiple mapped addresses in one call and return per-address edit/readback success booleans. Hopper validates map… | — |
| `set_bookmark` | Create or update a bookmark at a mapped hexadecimal address and report readback success. Omit name to preserve an existing name or create… | — |
| `set_comment` | Write a regular analysis comment at a hexadecimal address and return whether readback matched. An empty comment clears it. This mutates t… | — |
| `set_inline_comment` | Write an inline instruction comment at a hexadecimal address and return whether readback matched. An empty comment clears it; Hopper may… | — |
| `start_build_capture` | Launch the app under capture on a request-built computer and return its open-window screenshot. Downloads package lists as the computer u… | — |
| `start_build_computer` | Start a local agentenv computer, installing/downloading app packages as needed; returns computer_id and a first screenshot. Requires Dock… | — |
| `stop_build_capture` | Close the captured app and finish its capture. Returns checkpoints, package/sources, limitations and a draft between seed and end when bo… | — |
| `unset_bookmark` | Remove the bookmark at a mapped hexadecimal address and return whether it is absent. Hopper also permits removing an existing legacy book… | — |
| `update_analysis_settings` | Atomically set or reset editable runtime defaults for new work. Changes survive target close/open but disappear on REA restart; reset res… | — |

### 原生二进制（53）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `analyze_function` | Inspect one native function by symbol or provider-returned address. Default summary returns identity, pseudocode size, facet counts and v… | — |
| `annotate_native_function` | Atomically rename one function and/or change entry comments, verify readback, and return its refreshed complete dossier. Ghidra resolves… | — |
| `batch_decompile` | Decompile an explicit list of procedure symbols/addresses in input order, with one provider read active per batch. Returns per-item pseud… | — |
| `build_call_path` | Build every shortest direct-callee path from complete analyze_function Evidence supplied inline or by exact retained-evidence references.… | — |
| `compare_functions` | Compare two explicit analyze_function Evidence records or exact retained session references across identity, exact provider text, calls,… | — |
| `decompile_all` | Export pseudocode for all or selected analyzed functions to a directory; returns a manifest/index, with bodies kept in files. Existing ou… | — |
| `find_xrefs_to_name` | Find references to an exact analyzed symbol name: resolves the name, then returns its address and referencing addresses. name_not_found m… | — |
| `get_call_graph` | Traverse the provider-observed caller or callee graph from one symbol/address, returning canonical-address nodes with per-node outcomes.… | — |
| `inspect_analysis_view` | Read summaries, selected facts, or pages from completed Evidence without rerunning analysis. Use the producing tool’s retained-view hando… | — |
| `inspect_binary_hardening` | Inspect static hardening declarations in a local ELF, PE or Mach-O, including every universal slice. Reports PIE/ASLR, NX, RELRO, stack-p… | — |
| `inspect_binary_layout` | Inspect static ELF section/segment, symbol, relocation, linkage and mitigation facts with artifact SHA-256 Evidence, without launching th… | — |
| `inspect_byte_entropy` | Inspect Shannon byte entropy for one explicit local file offline, without execution, extraction or external tools. Returns file-wide SHA-… | — |
| `inspect_desktop_application` | Identify runtime candidates and next probes in a local desktop app directory from bounded listings, headers and metadata. Recognizes .NET… | — |
| `inspect_dwarf_units` | Inspect DWARF 2 through 5 compile-unit headers and the unit DIE in one explicit local ELF, Mach-O, or PE image without executing the imag… | — |
| `inspect_elf_debug_link` | Inspect one explicit local ELF32/ELF64 image for separate debug-file linkage without executing it or opening a disassembler. Returns .gnu… | — |
| `inspect_elf_dependencies` | Inspect one explicit local ELF32/ELF64 ET_EXEC or ET_DYN image's load-time dynamic dependencies without executing it, invoking the dynami… | — |
| `inspect_elf_notes` | Inspect one explicit local ELF32/ELF64 image's PT_NOTE program headers and SHT_NOTE sections without executing it or opening a disassembl… | — |
| `inspect_elf_unwind_ranges` | Inspect ELF32/64 .eh_frame and .eh_frame_hdr for paged FDE function ranges, associated CIE facts, LSDA/personality pointers, symbol match… | — |
| `inspect_go_binary` | Read embedded Go compiler, module, dependency/replacement and build-setting metadata from a local ELF, PE or selected Mach-O slice withou… | — |
| `inspect_kernel_build_config` | Inspect a local Linux kernel image (vmlinux, raw arm64 Image, x86 bzImage/zImage or configs.ko) for the version/builder/compiler banner a… | — |
| `inspect_kernel_module` | Inspect an uncompressed local ELF32/64 ET_REL Linux kernel module for ordered .modinfo entries, symbol CRCs, module/export/init/exit sect… | — |
| `inspect_native_api` | Inspect recovered parameter/return boundary types and jump-table dispatch for one native function selected by symbol or address. Returns… | — |
| `inspect_native_data_type` | Inspect one recovered type by exact database category path or defined typed data address. Returns observed size, alignment, packing, fiel… | — |
| `inspect_native_dispatch_metadata` | Inspect analyzed Objective-C class/method and Swift mangled symbols, with optional exact Objective-C import-pointer binding facts from th… | —；不可用：unsupported_host |
| `inspect_native_exports` | Inspect PE/ELF exports without execution or an analysis engine; use inspect_macho for Mach-O. Returns named/ordinal/forwarded PE exports… | — |
| `inspect_native_initializers` | List declared initializer/finalizer functions in a local ELF32/64 or selected Mach-O slice without execution. Returns paged slots and res… | — |
| `inspect_native_instruction` | Inspect bytes, mnemonic, operand tokens, flow and typed incoming/outgoing references at one code/data address. Ghidra preserves the query… | — |
| `inspect_native_load_image` | Inspect provider source digests, loaded mappings, relocations, entries and register context without executing or changing the target. Ind… | — |
| `inspect_pe_certificates` | Inspect a local PE32/PE32+ certificate directory without executing it or verifying signatures. Returns WIN_CERTIFICATE ranges/types/diges… | — |
| `inspect_pe_imports` | Inspect local PE32/PE32+ standard and delay-load imports without execution. Returns DLL/named/ordinal imports, ILT/IAT RVAs, descriptors… | — |
| `inspect_pe_load_config` | Inspect PE32/PE32+ TLS callbacks and sized load configuration without executing the image. Returns callback VA/RVA/file offsets and secti… | — |
| `inspect_rust_binary` | Read the embedded cargo-auditable crate dependencies of a local ELF, PE, selected Mach-O slice or WebAssembly core module without running… | — |
| `inspect_with_objdump` | Inspect a local artifact with caller-selected objdump and GNU-style arguments; the executable implementation/version is unverified. opera… | — |
| `list_names` | List every analyzed memory and external symbol as address/value pairs. Provider metadata distinguishes Ghidra primary, dynamic, external,… | — |
| `list_procedures` | List every analyzed procedure as address/value pairs after provider analysis. Ghidra metadata distinguishes thunks and external functions… | — |
| `list_segments` | List segments or memory blocks using exclusive end addresses. Ghidra reports block permissions, address space, image base, initialization… | — |
| `list_strings` | List every provider-reported string object or candidate, or filter to one address, as address/value pairs with encoding, terminator statu… | — |
| `match_native_functions` | Pair two retained list_procedures inventories by unique exact symbols, then unique identical observed bytes. Optional same-context name/b… | — |
| `procedure_address` | Resolve an unambiguous procedure symbol name or provider-normalized address to its canonical entry address. External address spaces remai… | — |
| `procedure_assembly` | Return assembly for one analyzed procedure identified by symbol or hexadecimal address. Use when pseudocode loses calling-convention or i… | — |
| `procedure_callees` | Return the provider's resolved direct callees for one procedure identified by symbol or address. Unresolved indirect calls may be absent;… | — |
| `procedure_callers` | Return the provider's resolved direct callers for one procedure identified by symbol or address. Results reflect completed static analysi… | — |
| `procedure_info` | Return provider metadata for one procedure identified by symbol or address: entrypoint, signature, locals, size, block count, and complet… | — |
| `procedure_pseudo_code` | Decompile one analyzed procedure by symbol or provider-normalized address. Returns provider-specific pseudocode or null, never original s… | — |
| `procedure_references` | Return incoming or outgoing reference edges for one procedure. Ghidra preserves detailed reference flags; Hopper preserves native CallRef… | — |
| `read_function_instructions` | Return every raw instruction for one analyzed procedure. Instruction text and body extent are provider-specific. Ghidra terminal-call ass… | — |
| `resolve_native_call_targets` | Resolve one explicit static call site using typed provider call references. Preserves ambiguous targets as candidates and unresolved comp… | — |
| `search_procedures` | Find analyzed procedures by literal name (default) or regex, including accepted secondary names. Returns deterministic provider-inventory… | — |
| `search_strings` | Find provider-reported strings by literal text (default) or regex. Complete results cover that inventory, not all artifact text; packed/u… | — |
| `trace_call_path` | Resolve start and optional goal symbols or addresses, then trace direct callers or callees. Returns observed edges and a shortest path wi… | — |
| `trace_feature` | Search procedure/string inventories for the complete literal query, then query xrefs at matched start addresses. Interior-byte references… | — |
| `trace_native_values` | Trace static value dependencies across resolved calls from one native procedure: high-p-code def-use, constants, operators, memory/branch… | — |
| `xrefs` | Return analyzed references to a code or data address. Hopper may default to its current cursor; headless providers such as Ghidra require… | — |

### 托管代码 PE/CLR（7）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `compare_managed_members` | Compare two authenticated inspect_managed_members Evidence records, inline or retained, using unique exact type/name/signature/CIL or dec… | — |
| `import_managed_reconstruction` | Import decompiler-produced managed reconstruction against authenticated inspect_managed_members Evidence supplied inline or by exact reta… | — |
| `inspect_managed_artifact` | Inspect PE/CLI identity, classification and metadata inventories from an explicit path or selected managed target without loading or exec… | — |
| `inspect_managed_members` | Inspect PE/CLI types, members, signatures, CIL hashes/instruction tuples, exception regions, static calls, field accesses and loaded #US… | — |
| `inspect_managed_native_boundaries` | Inspect PE/CLI ModuleRef, ImplMap/PInvoke declarations, CLI native-header indicators, and non-IL method implementation flags without load… | — |
| `project_managed_application_graph` | Project authenticated managed artifact, member, and native-boundary Evidence, supplied inline or by exact retained reference, into the pr… | — |
| `verify_managed_native_boundaries` | Verify managed P/Invoke/native-boundary declarations against authenticated native export or function Evidence, with inline or exact retai… | — |

### JavaScript 与 Electron（19）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `analyze_javascript_application` | Build a static application graph from a local ASAR or extracted JavaScript app without executing it. Supply input_path, e.g. {input_path:… | — |
| `analyze_web_bundle` | Recover a static chunk graph, route/endpoint candidates, vendor fingerprints and page-declared WebMCP metadata from JavaScript on one sel… | — |
| `capture_electron_scenario` | Launch and exercise an owned Electron app when passive CDP/Inspector observation cannot answer the question. REA owns startup/teardown; s… | — |
| `compare_application_versions` | Compare two authenticated JavaScript Application Graph versions, supplied inline or by exact retained reference. Returns added, removed,… | — |
| `compare_javascript_export_shapes` | Compare static return-property shapes for one exact module/export on each authenticated JavaScript Application Graph, inline or retained.… | — |
| `compare_source_to_bundle` | Map committed historical source to an authenticated JavaScript Application Graph. Supply HistoricalSourceGraph inline or as {kind:"file",… | — |
| `export_web_scripts` | Export JavaScript bytes already retained in one local inspect_web_page or capture_browser_scenario JSON capture (normalized result or com… | — |
| `inspect_electron_fuses` | Inspect packaged Electron fuse bytes in one local macOS app bundle, Electron Framework binary, Windows PE executable, or Linux ELF execut… | — |
| `inspect_electron_page` | Passively inspect one Electron file page by supplying its loopback CDP endpoint and target ID. The provider rechecks that the target curr… | — |
| `inspect_v8_code_cache` | Inspect a local bytenode .jsc or compatible V8 code-cache container as static bytes, without V8, bytenode, child processes or decompilati… | — |
| `list_electron_targets` | List every Electron file:// page target from a selected loopback CDP endpoint. Local file paths are canonicalized after symlink resolutio… | — |
| `list_javascript_runtime_targets` | List every eligible Node/Electron V8 Inspector target from an explicit literal-loopback endpoint. Node discovery file locations that cann… | — |
| `observe_javascript_runtime` | Passively observe loaded-script and execution-context metadata on one loopback Node/Electron V8 Inspector target, selected by inspector_e… | — |
| `reconcile_javascript_runtime` | Reconcile verified static JavaScript application graphs with existing passive web/Electron CDP, passive V8 Inspector, or provider-owned a… | — |
| `recover_javascript_sources` | Recover readable modules from local UTF-8 JavaScript bundles into an absent output_directory, without executing application code. Require… | — |
| `trace_application_feature` | Trace a typed literal seed through every reachable part of an authenticated JavaScript Application Graph supplied as inline Evidence or e… | — |
| `trace_javascript_semantics` | Trace static JavaScript data-flow, direct call/return, and closure relations from inline application Evidence or an exact same-session re… | — |
| `trace_web_module_imports` | Resolve native ES imports/re-exports from one script in a local export_web_scripts manifest. Verifies the selected source digest/size and… | — |
| `trace_web_source_location` | Map one generated position in an exported script through a caller-paired local source map, verifying manifest/script/map byte identities.… | — |

### 浏览器观察与场景录制（12）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `capture_browser_scenario` | Drive a browser scenario when passive observation cannot exercise the app. Launch the selected executable or connect to a loopback CDP ta… | — |
| `capture_web_screenshot` | Capture the current visible viewport of one configured page as an inline, content-addressed PNG artifact. The operation never scrolls, na… | — |
| `compare_static_and_observed_endpoints` | Compare static JavaScript endpoints with requests recorded in HAR Evidence, supplied inline or retained; acquires no files, targets or UR… | — |
| `compare_web_captures` | Compare two passive page inspections or two recorded browser scenarios. For passive captures, pass before/after with each complete inspec… | — |
| `compare_web_screenshots` | Compare two self-verifying PNG screenshot artifacts with local pixel metrics. Returns exact changed-pixel ratios and channel deltas witho… | — |
| `discover_webmcp_tools` | Passively inventory every page-registered WebMCP tool and its complete structural input-schema summary using the experimental CDP WebMCP… | — |
| `inspect_playwright_trace` | Inspect a local Playwright v10 trace ZIP offline, without browser replay or requests to recorded URLs. Returns action boundaries, console… | — |
| `inspect_web_event_listeners` | Inspect listeners registered directly on the first main-document CSS match in one selected CDP page. Returns event flags, native callback… | — |
| `inspect_web_page` | Passively inspect one selected page target through CDP without evaluating JavaScript, navigating, clicking, closing, or mutating the page… | — |
| `list_browser_targets` | List pages exposed by one loopback Chrome DevTools Protocol endpoint, optionally filtered by exact origin. Returns target IDs and URLs; q… | — |
| `observe_web_execution` | Instrument one selected CDP page for a finite, externally driven precise coverage window. Resets execution counters and prevents optimize… | — |
| `observe_web_session` | Arm a CDP observation window of the requested duration while the user operates the page. By default it follows the selected target's curr… | — |

### Android 与移动设备（41）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `capture_adb_screen` | Capture one frame of the device screen as a PNG (`screencap -p` through exec-out, no device-side file) into a caller-selected output dire… | — |
| `collect_adb_bugreport` | Collect one device-generated bugreport archive (`adb bugreport`) into a caller-selected output directory, digesting the zip. The archive… | — |
| `decode_android_resources` | Decode APK resources with apktool d --no-src: readable manifest, version/SDK facts, string resources/locales and decoded file count. Uses… | — |
| `decompile_jeb_item` | Decompile one type or method to engine pseudo-code using its decompiler (Dalvik, Java, or native). item_address comes from the engine's c… | — |
| `identify_flutter_build` | Identify a Flutter app's build facts by pure parsing: observed Dart snapshot hashes from lib/<abi>/libapp.so, per-ABI library digests, th… | — |
| `inspect_adb_client` | Inspect the caller-selected adb client: resolved binary, version, and install path. Never contacts devices and never starts the adb serve… | — |
| `inspect_adb_device` | Inspect one device's build identity through a fixed `getprop` whitelist: Android and SDK versions, security patch, fingerprint, product i… | — |
| `inspect_adb_display` | Read physical and override size/density from `wm size` and `wm density`. Malformed numeric declarations are retained in numeric_issues wi… | — |
| `inspect_adb_package` | Inspect installed-package versions, install times, installer, user id, flags, and requested-permission count through read-only `dumpsys p… | — |
| `inspect_adb_window` | Report the window manager's focus declarations with display context, original lines and explicit summary status. Reads `dumpsys window wi… | — |
| `inspect_android_class` | Inspect one exact Android class's methods, fields, inner classes, DEX prototypes and encoded static final values without generating sourc… | — |
| `inspect_android_jni_bindings` | Link an APK's DEX native declarations to Java_* exports and static JNINativeMethod candidates by ABI and exact library occurrence, withou… | — |
| `inspect_android_method` | Decompile one Android method, with explicit overload_index when names collide and smali fallback when needed. Reports DEX prototype, repr… | — |
| `inspect_android_package` | Inspect APK package/SDK/permission declarations, decoded manifest, static components and class/resource counts without executing it or ve… | — |
| `inspect_apk_signature` | Inspect declared APK v1/v2/v3/v3.1 signers, certificate fingerprints, digests, SDK ranges, rotation lineage and source stamp without exec… | — |
| `inspect_apktool_client` | Inspect the caller-selected apktool launcher: resolved command, selection source, and version. Decodes nothing. REA never installs Apktoo… | — |
| `inspect_dart_aot` | Inspect one APK ABI's Dart AOT snapshot without executing it. Supports legacy split VM/isolate FullAOT kind 3 and unified FullAOT kind 2.… | — |
| `inspect_jeb_client` | Inspect the running JEB client serving MCP: engine version, GUI or headless mode, and startup time. Does not open a target. Requires a ca… | — |
| `install_adb_package` | Install one local APK on the device (`adb install [-r]`), recording the APK's host digest and byte size. A device-mutating tool: `replace… | — |
| `list_adb_devices` | List attached devices exactly as `adb devices -l` reports them: serial, state, transport, model metadata, and an inferred emulator/physic… | — |
| `list_adb_directory` | List the immediate children of one absolute device directory, including hidden entries: names, kinds, permissions, owner, group, sizes, d… | — |
| `list_adb_features` | List the device's declared hardware and software features (`pm list features`) for device fingerprinting. Read-only. | — |
| `list_adb_packages` | List installed packages on one device with each base APK's device path, optionally scoped to third-party or system packages. Paths are de… | — |
| `list_adb_processes` | List running processes exactly as `ps -A` reports them: user, pid, ppid, rss, state, and name. Useful for pairing with instrumentation la… | — |
| `list_adb_services` | List the device's binder services with their interfaces (`service list`). Read-only. | — |
| `list_jeb_units` | List project units by stable unit path and type, with optional wildcard filter, parent restriction, and pagination. The engine caps pages… | — |
| `open_jeb_project` | Open or create a JEB project from an artifact file or existing .jdb2 database on the engine host. Returns the project's input-file digest… | — |
| `project_android_application_graph` | Build a static Android application inventory from the authenticated nested inventory Evidence returned by inspect_artifact for an APK. Re… | — |
| `project_harmony_application_graph` | Build a static HarmonyOS inventory from the authenticated nested inventory Evidence returned by inspect_artifact for a HAP, HSP or App Pa… | — |
| `pull_adb_file` | Pull one absolute device path (a database, shared-preferences XML, or any readable file) into a caller-selected output directory, digesti… | — |
| `pull_adb_package` | Pull one installed package's complete APK set (base plus every split, as `pm path` reports) from the device into a caller-selected output… | — |
| `push_adb_file` | Push one local file to an absolute device path. If the destination is an existing directory, adb places the file inside it under the loca… | — |
| `read_adb_logcat` | Read a bounded dump of the device log (`logcat -d -t`) for one buffer, optionally restricted to a process id. No streaming, no clearing;… | — |
| `read_adb_setting` | Read one settings value (`settings get`) from the system, secure, or global namespace. Absent keys report the device's own null observati… | — |
| `resolve_adb_packages` | Find installed packages by case-insensitive package-name substring and return each base APK device path. Pass an exact returned name to p… | — |
| `search_android_classes` | Search complete top-level decompiler class-name rows in an explicit local APK by case-sensitive substring. Empty query inventories all ro… | — |
| `start_adb_activity` | Start an intent with `am start -W`: one action, optional data URI, optional explicit component, and up to 16 typed extras (string, boolea… | — |
| `start_adb_app` | Start one installed app's resolved launcher activity with `am start -W -n`. A device-mutating tool for dynamic analysis. The full wait re… | — |
| `stop_adb_app` | Force-stop every process of one package (`am force-stop`), ending a dynamic-analysis run. A device-mutating tool; it succeeds whether or… | — |
| `trace_android_references` | Trace incoming static using nodes to an exact Android class or selected method overload. A method target may be an external class directl… | — |
| `uninstall_adb_package` | Request package removal for user 0 (`adb shell pm uninstall --user 0`) without data retention. A device-mutating tool; absent packages re… | — |

### Apple 平台（18）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `analyze_swift_types` | Classify analyzed Swift procedure names into classes, structs, enums, protocols and extensions using manglings or same-address symbol ali… | — |
| `capture_native_ui_scenario` | Interact with one exact native app window through selected-element press, scroll, AXValue text entry and bounded waits. Returns ordered b… | 可能写盘, 可能弹窗, 可能联网, 启动进程；不可用：unsupported_host |
| `decode_interface_builder` | Decode compiled storyboard and nib archives inside the active Apple app bundle, including keyed property lists and NIBArchive object tabl… | — |
| `demangle_swift` | Demangle an ordered list of single-line Swift symbols without Hopper. Returns demangled, unchanged or invalid for every input; invalid en… | 启动进程；不可用：unsupported_host |
| `get_objc_classes` | Find Objective-C class labels, optionally by literal substring. Labels remain separate unless exact selected-image pointer-fixup Evidence… | — |
| `get_objc_protocols` | Discover and deduplicate Objective-C and Swift protocol labels. | — |
| `inspect_apple_ips` | Inspect a local Apple .ips crash report for process, exception/termination, thread, image and lossless register facts with deterministic… | — |
| `inspect_asset_catalog` | Inspect compiled Assets.car metadata in an active Apple app bundle. Returns stable paginated catalog and rendition records with raw asset… | 启动进程；不可用：unsupported_host |
| `inspect_keyed_archive` | Inspect one Foundation NSKeyedArchiver plist in the active app bundle as original object-table nodes, class descriptors, named roots, and… | — |
| `inspect_macho` | Inspect Mach-O slices, load commands, linkage, build metadata, segments/sections and permissions without launching Hopper. Returns comman… | 可能写盘, 启动进程；不可用：unsupported_host |
| `inspect_plist` | Parse Info.plist from an open binary or bundle-resource session, or select path within that session. Use open_binary or open_bundle_resou… | 可能写盘, 启动进程；不可用：unsupported_host |
| `inspect_signature` | Inspect the selected Mach-O slice's signing identity, hashes, authorities, requirement, entitlements and hardened-runtime state from a di… | 可能写盘, 启动进程；不可用：unsupported_host |
| `list_architectures` | List thin/universal Mach-O slices with file offsets, sizes, alignment, coverage and native-tool provenance. native_command_timeout_ms bou… | 启动进程；不可用：unsupported_host |
| `observe_native_calls` | Launch the active Mach-O under LLDB and record selected function/Objective-C method entries; the owned process is killed at max_events or… | 可能写盘, 可能弹窗, 可能联网, 启动进程；不可用：unsupported_host |
| `observe_native_ui` | Observe one already-running native app window by PID/window ID, bound to the active Mach-O target. Returns a bounded accessibility tree a… | 可能写盘, 启动进程；不可用：unsupported_host |
| `project_apple_application_graph` | Build a static Apple application inventory from the authenticated nested inventory Evidence returned by inspect_artifact for an IPA, .app… | — |
| `trace_dylib_resolution` | Trace how dyld would resolve each Mach-O dylib load for the active Mach-O, or for every executable in the active .app bundle (the main ap… | — |
| `trace_native_ui_action` | Trace one unique compiled UI action, object ID, native symbol or exact function address through authored connections, encoded or symboliz… | — |

### 归档·固件·格式（21）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `compare_artifacts` | Compare complete artifact inventories by occurrence path, content identity, metadata and graph relations; root . identifies the outer con… | — |
| `compare_wasm_interfaces` | Compare typed core WASM import/export names, kinds and exact signatures from two authenticated inspect_wasm_artifact Evidence records. Se… | — |
| `extract_artifact` | Write all or selected regular files from the active supported archive to an absent absolute output_root, or a fresh temporary directory i… | 可能写盘, 启动进程 |
| `extract_firmware` | Extract selected local firmware bytes with Unblob 26.6.x (verified with 26.6.4) into an absent output directory. Returns verified child p… | — |
| `extract_uefi_firmware` | Extract FFS bodies and section payloads from a local UEFI image into an absent directory. A volume, file or section selection includes it… | — |
| `inspect_api_contract` | Inspect declared APIs in local OpenAPI JSON or GraphQL SDL without a session, network requests or target execution. OpenAPI 3.0/3.1/3.2 r… | — |
| `inspect_artifact` | Inventory the active archive, app package, firmware container or supported packaged executable without running it. Returns nested content… | 可能写盘, 启动进程 |
| `inspect_devicetree` | Inspect an explicit local flattened devicetree blob (FDT v16/v17) without execution or external tools. Returns validated header, memory r… | — |
| `inspect_evm_interface` | Infer interface candidates from explicit local flat EVM bytecode using bundled EVMole 0.9.3/WASM; select raw or hex encoding. Linux x64 p… | — |
| `inspect_firmware_regions` | Inspect signature candidates in a local firmware file with Binwalk 3.1.x (verified with 3.1.0). Returns offsets, reported lengths, descri… | — |
| `inspect_maven_gradle_metadata` | Inspect a local Maven pom.xml or Gradle .module metadata file as static bytes, without running Maven or Gradle, resolving a dependency tr… | — |
| `inspect_ntfs_journal` | Inspect USN V2/V3/V4 records from a local acquired NTFS journal with a caller-paired MFT from the same volume. Reads at most 64 MiB per f… | — |
| `inspect_nuget_nupkg` | Inspect a local NuGet .nupkg ZIP without restoring, executing, or contacting a feed. Returns package identity (id, version, authors, desc… | — |
| `inspect_pe_resources` | Inspect a local PE32/PE32+ resource tree without execution: type/name/language identities, empty branches, UTF-16 names, payload RVA/file… | — |
| `inspect_recorded_crash` | Inspect a saved Linux ELF64 little-endian amd64/AArch64 core without launching its target or attaching to a live PID. Returns recorded se… | — |
| `inspect_sqlite_database` | Inspect a local SQLite snapshot and sibling WAL without modifying them. Returns their SHA-256 and schema inventory; select an exact ordin… | 可能写盘, 启动进程 |
| `inspect_uefi_firmware` | Map PI firmware volumes, FFS files, section chains, AMD PSP directory candidates and uncovered ranges in a local flash image. Report inte… | — |
| `inspect_uefi_nvram` | Map valid AMI NVAR entries inside a local flash image, including nested factory defaults such as StdDefaults. Reports raw link displaceme… | — |
| `inspect_wasm_artifact` | Validate and inspect local WASM with caller-supplied WABT 1.0.42, without executing it or fetching dependencies. Returns artifact SHA-256… | — |
| `inspect_windows_shortcut` | Inspect a local Windows Shell Link (.lnk) without resolving or executing its target, COM, or network access. Returns header/time/display… | — |
| `open_bundle_resources` | Open a local app bundle for read-only plist, Interface Builder, asset catalog, and keyed archive inspection without resolving or inventin… | — |

### 网络与信号采集（7）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `decode_signal_recording` | Decode a saved logic/signal recording with an explicitly selected sigrok decoder stack, channels and options. Returns literal text, sampl… | — |
| `inspect_packet_capture` | Extract caller-selected TShark fields from a saved packet capture, with display filters, decode-as rules and pass mode preserved. Returns… | — |
| `inspect_packet_fields` | Find protocols or field definitions registered in installed TShark 4.x. kind defaults to protocols; use fields with an optional exact pro… | — |
| `inspect_pcap_capture` | Summarize a saved pcap/pcapng snapshot: exact packet count, SHA-256, IP endpoints, DNS questions/addresses, TLS SNI, protocols and HTTP U… | — |
| `inspect_pcap_client` | Inspect the caller-selected tshark and capinfos binaries: selected commands, selection sources, and versions. Both tools must be usable.… | — |
| `inspect_signal_decoders` | List installed sigrok decoder IDs/names, or supply an exact decoder ID to inspect its channel/option help. Use returned IDs/options with… | — |
| `inspect_web_network_capture` | Inspect a saved local HAR 1.2, mitmproxy, Fiddler SAZ or supported aioquic qlog capture without contacting recorded URLs. Returns source-… | — |

### 调试器与插桩（22）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `capture_process_scenario` | Run a caller-selected command under a PTY and return process capture Evidence and unknowns. It runs with the user's permissions, can chan… | — |
| `close_frida_session` | Unload session scripts and attempt to detach REA's Frida session. Then resume a still-paused spawned process if script cleanup or session… | — |
| `close_gdb_session` | Close the owned GDB process after verifying the inferior state. When one live thread group has a verified durable output TTY, REA automat… | — |
| `close_rizin_debug_session` | Close the REA-owned Rizin debugger only after verifying no inferior remains or detaching one with a verified caller-selected TTY output s… | — |
| `compare_process_captures` | Compare compatible process captures, inline or by {kind:"retained-evidence",evidence_id}, across terminal, interaction, lifecycle, proces… | — |
| `cutter_command` | Run one arbitrary Rizin command in a selected Cutter session; it may persist edits or execute plugin effects. Reports completion uncertai… | — |
| `execute_rizin_command` | Run one caller-selected Rizin command on a local artifact. Commands/plugins can execute code, mutate files, access network and read outsi… | — |
| `frida_session_status` | Read observed Frida session state on each call. Default detail=complete returns queued script messages and capture truncation. detail=sum… | — |
| `gdb_console` | Run one unrestricted command in a persistent GDB session; commands can run shell, change target state, access files and network. Returns… | — |
| `gdb_session_status` | Return the observed lifecycle state and bounded recent MI records and process diagnostics for one persistent REA GDB session; closed_reas… | — |
| `instrument_with_frida` | Run caller-authored Frida JavaScript against a selected process for one observation window, then detach. Scripts can read/change target m… | — |
| `list_cutter_sessions` | Find live REA bridge sessions in Cutter and return document identity and bridge-directory security status. Examines at most 256 descripto… | — |
| `list_frida_devices` | List Frida devices currently available to this host, optionally connecting to the caller-selected remote Frida endpoint. Remote authentic… | — |
| `list_frida_processes` | List processes observed on a selected Frida device or caller-supplied remote endpoint. A remote connection is closed after discovery; aut… | — |
| `load_frida_script` | Load caller-supplied JavaScript into a Frida session. Scripts can read or change target memory and behavior and can access the target pro… | — |
| `resume_frida_session` | Resume the process created by a paused Frida spawn session. Attached processes are already running and cannot be resumed through this ope… | — |
| `rizin_debug_command` | Run one unrestricted command in a persistent Rizin debugger; it can access target state, plugins, shell, files and network. Returns raw/i… | — |
| `rizin_debug_session_status` | Return observed lifecycle state and bounded recent NUL-framed output and process diagnostics for one Rizin debugger session; closed_reaso… | — |
| `start_frida_session` | Attach Frida to one selected process or spawn one selected target. Spawned targets remain paused until resume_frida_session, allowing scr… | — |
| `start_gdb_session` | Start a persistent caller-supplied GDB session and return its session ID. Linux only; detaching a live inferior during close requires a v… | — |
| `start_rizin_debug_session` | Start a persistent Rizin debugger for one selected target/backend. Linux and a caller-selected TTY for inferior stdin/stdout/stderr are r… | — |
| `unload_frida_script` | Unload one caller-selected Frida script from a live session. This removes that script's instrumentation from the target. | — |

### 证据与验证（15）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `audit_release_exposure` | Report what static analysis of a shipped application artifact recovers. Accepts one local .app bundle, installation directory, ASAR, or e… | — |
| `build_reconstruction_obligation_ledger` | Build a deterministic reconstruction-obligation ledger from an authenticated Evidence bundle, reviewed obligations and an explicit recons… | — |
| `compare_bundles` | Compare two canonical Evidence bundles by exact record membership, explicit one-to-one observation pairs, and complete residual-unknown r… | — |
| `correlate_static_and_runtime` | Evaluate every explicit caller-declared hypothesis between static and runtime comparison Evidence supplied inline or by exact retained-ev… | — |
| `evaluate_reconstruction_coverage` | Check evidence-backed reconstruction coverage for one named boundary. Missing ownership or inventory is partial; stale, weak, truncated,… | — |
| `export_environment_bundle` | Write an agent environment bundle from capture_browser_scenario Evidence or HAR inspect_web_network_capture Evidence to an absent absolut… | — |
| `export_evidence_bundle` | Atomically write the session's deterministic Evidence bundle to the requested local path. Existing files require overwrite: true; records… | — |
| `find_changed_behavior` | Aggregate validated process, artifact, and function comparison Evidence, supplied inline or by exact retained-evidence references from th… | — |
| `get_evidence_bundle` | Read retained Evidence and tracked questions without rerunning providers. Default complete returns an importable canonical bundle. detail… | — |
| `import_evidence_bundle` | Read the JSON bundle at the supplied local path, validate every Evidence ID and canonical manifest, then atomically merge it. Imported co… | — |
| `list_unknowns` | List tracked questions' current revisions in deterministic ID order, with exact status/severity/domain filters. Complete inline by defaul… | — |
| `record_unknown` | Create one deterministic residual unknown and immutable mutation evidence. Its scope is the active binary analysis target digest, or null… | — |
| `update_unknown` | Append a full-state revision to one tracked question, with immutable mutation Evidence. Requires exact expected_revision; stale writers f… | — |
| `verify_reconstruction` | Verify a finite typed behavioral, structural, and visual specification against a canonical Evidence bundle. Pass means every declared cla… | — |
| `verify_unknown_resolution` | Check a tracked question's current resolution against bundled Evidence, required authority/confidence/environment and revision integrity.… | — |

### 模型与字节码（5）

| 工具 | 用途 | 副作用 / 可用性 |
| --- | --- | --- |
| `inspect_erlang_beam` | Inspect an Erlang BEAM IFF file without executing bytecode or requiring Erlang. Returns chunk byte ranges/digests, atoms, exports/imports… | — |
| `inspect_gpu_code_objects` | Inspect CUDA/HIP code objects in local ELF/PE, fatbins, CUBIN, PTX or Clang HIP bundles without GPU tools or target execution. Default in… | — |
| `inspect_il2cpp_metadata` | Inspect Unity IL2CPP metadata versions 24/27/29/31/39, optionally linking a selected 64-bit little-endian Mach-O/PE/ELF binary without ex… | — |
| `inspect_model_artifact` | Inspect GGUF v2/v3 or safetensors metadata and tensor declarations without loading weights or running inference. Default hash header comm… | — |
| `inspect_python_pyc` | Inspect local CPython 3.7–3.15 .pyc headers and nested code objects without executing bytecode, invoking Python or recovering source. Ret… | — |

## CLI 命令（204）

| 命令 | 用途 |
| --- | --- |
| `rea address-to-file-offset <path> <address>` | Map one analysis address to a file offset; memory bytes may differ and ranges may not be contiguous |
| `rea analyze <path>` | Get an overview of an app |
| `rea analyze-javascript-application <path>` | Statically reconstruct a local JavaScript/Electron application |
| `rea analyze-web-bundle <endpoint> <targetId>` | Capture and statically analyze a page bundle, defaulting to the selected target origin |
| `rea annotate-native-function <path> <procedure>` | Edit function annotations and return refreshed analysis |
| `rea audit-release-exposure <path>` | Report what static analysis of a shipped artifact recovers. Reads the selected path. When the selection is a file, the parent directory is listed for sibling .pdb, .dSYM, .debug, and .map debug companions. |
| `rea build-reconstruction-obligation-ledger <inputJson>` | Generate a deterministic Evidence-backed reconstruction obligation ledger page |
| `rea capabilities` | List provider capabilities and side effects |
| `rea capture-adb-screen <serial>` | Capture one screen frame as a digested PNG |
| `rea capture-browser-scenario <inputJson>` | Run one bounded Playwright browser scenario and return Evidence |
| `rea capture-desktop-application` | Launch a Linux desktop application, watch it while it is used and record its windows and state at checkpoints read from stdin |
| `rea capture-electron-scenario <inputJson>` | Run one owned Electron scenario with cancellable actions |
| `rea capture-native-ui-scenario <path>` | Run declarative AX actions or waits in one exact native application window |
| `rea capture-process <scenario>` | Capture one caller-selected process scenario |
| `rea capture-web-screenshot <endpoint> <targetId>` | Capture one visible page viewport within the supplied origin scope |
| `rea collect-adb-bugreport <serial>` | Collect and digest one device-generated bugreport archive |
| `rea compare <left> <right>` | Compare two canonical Evidence bundles by record identity; use compare-artifacts for artifact inventory contents |
| `rea compare-application-versions <inputJson>` | Compare two authenticated JavaScript Application Graph versions |
| `rea compare-artifacts <inputJson>` | Compare two artifact inventories, including FIT and legacy uImage firmware components, named as {left, right}: complete Evidence or {kind:"evidence-file",path,evidence_id?}. A one-shot command retains no session Evidence for retained-evidence references. |
| `rea compare-javascript-export-shapes <inputJson>` | Compare exact static JavaScript export return shapes without execution |
| `rea compare-managed-members <leftPath> <rightPath>` | Compare managed PE/CLI member inventories by exact declared type, name, and signature; names alone never form a match |
| `rea compare-process-captures <left> <right> [traceSpec]` | Compare two process capture Evidence JSON files |
| `rea compare-source-to-bundle <inputJson>` | Compare historical source (inline graph or reference {kind:file,path}) with authenticated application Evidence. Save the complete JSON to query with inspect-analysis-view. |
| `rea compare-static-and-observed-endpoints <inputJson>` | Compare static JavaScript endpoints and HAR Evidence JSON offline; --detail summary with --evidence_output saves full facts for selected inspect-analysis-view pages |
| `rea compare-wasm-interfaces <inputJson>` | Compare core WASM interfaces from two exact inspection Evidence records |
| `rea compare-web-captures <beforeJson> <afterJson>` | Compare two normalized passive captures or recorded browser scenarios |
| `rea compare-web-screenshots <beforeJson> <afterJson>` | Compare two self-verifying PNG artifact JSON values |
| `rea cutter-command <sessionId> <expectedGeneration> <command>` | Execute one Rizin command in a selected live Cutter instance |
| `rea debug-with-gdb <command>` | Run one unrestricted GDB console command in an ephemeral MI session; provide an inferior TTY so a live target can be safely detached |
| `rea debug-with-rizin <path> <command>` | Run one unrestricted Rizin debugger command in an ephemeral session |
| `rea decode-android-resources <path>` | Decode one APK's manifest, metadata, and string resources with apktool |
| `rea decode-interface-builder <path>` | Decode compiled storyboard and nib archives from an app bundle |
| `rea decode-signal-recording <path>` | Decode an existing signal recording with caller-supplied sigrok |
| `rea decompile <path> [address]` | Read one part of an app as code. Supply at least one of the positional address or --procedure. Alternatively, use --file-offset alone. Equal positional and --procedure values are accepted; conflicts fail. With Ghidra, a space-qualified address such as ram:0x... avoids file-offset fallback; inspect-native-load-image reports the observed default space. |
| `rea decompile-all <path>` | Write every function's pseudocode into a directory and return a manifest |
| `rea decompile-jeb-item <itemAddress> <itemKind>` | Decompile one JEB type or method to engine pseudo-code |
| `rea demangle-swift <path> <symbols...>` | Demangle Swift symbols without Hopper |
| `rea describe-desktop-application-task <capture>` | Describe how a desktop application capture's files changed from the seed checkpoint to the end, with suggested checks and a task draft to complete for export-desktop-application --task |
| `rea discover-webmcp-tools <endpoint> <targetId>` | Passively discover page-declared WebMCP tools |
| `rea doctor` | Check whether REA is ready |
| `rea environment-build <capture> [directory]` | Build an agent environment bundle from a recorded capture in one offline step: inspect a HAR (or read capture Evidence), project the environment manifest, derive the state, report which tools the environment answers from state, which replay and why each write is withheld, then write the bundle environment-export writes |
| `rea environment-compare <manifest>` | Compare an environment with probe captures of the application it was captured from: each probe is one call sequence recorded against a freshly reset application, answered by the environment from a reset state, with agreement reported per step, tool and probe |
| `rea environment-export <manifest> <directory>` | Export an environment manifest and its capture Evidence as an agent environment bundle folder the agentenv framework runs with agent-env run |
| `rea environment-serve <manifest>` | Serve an environment manifest as an agent environment over streamable HTTP until SIGINT or SIGTERM: read tools, and write tools whose effect the capture confirmed, answer from the state the capture observed, derived at startup, or every tool replays retained capture records with --replay-only or when the state is unavailable |
| `rea evaluate-reconstruction-coverage <inputJson>` | Evaluate inline fail-closed reconstruction coverage |
| `rea evidence-export <source> <output>` | Validate and atomically export canonical Evidence JSON |
| `rea evidence-import <path>` | Validate a standalone Evidence bundle and count records and Unknown revisions; does not retain them in an MCP session |
| `rea execute-rizin-command <path> <command>` | Execute one Rizin command against a local artifact |
| `rea export-desktop-application <capture> <directory>` | Export a desktop application capture folder as an agentenv computer app bundle: class, env.toml, skill and seed |
| `rea export-web-scripts <capturePath> <outputDirectory>` | Export retained website scripts into an absent directory for static JavaScript analysis |
| `rea extract-artifact <path>` | Extract all or selected regular artifact contents safely; DMG extraction is unavailable |
| `rea extract-firmware <path> <outputDirectory>` | Extract selected firmware bytes and return verified files and provenance |
| `rea extract-uefi-firmware <path> <outputDirectory>` | Extract selected UEFI firmware bytes with provenance and decode gaps |
| `rea function <path> [address]` | Analyze one complete function with evidence. Supply at least one of the positional address or --procedure. Equal values are accepted; conflicts fail. |
| `rea guidance ` | Search or read the installed REA workflow guidance |
| `rea guided-workflows` | List or render REA's existing guided workflows |
| `rea identify-flutter-build <path>` | Identify a Flutter build's Dart snapshot hash and engine facts by pure APK parsing |
| `rea import-managed-reconstruction <inputJson>` | Import decompiler-produced managed reconstruction against exact static member evidence |
| `rea import-reference-source <root>` | Import a source tree as historical reference only |
| `rea inspect <path>` | Inspect an app overview with evidence |
| `rea inspect-adb-client` | Inspect the caller-selected adb client without contacting devices |
| `rea inspect-adb-device <serial>` | Inspect one device's build identity through a fixed getprop whitelist |
| `rea inspect-adb-display <serial>` | Report the display's declared size and density |
| `rea inspect-adb-package <serial> <package>` | Inspect one installed package's version, installer, and flags through dumpsys |
| `rea inspect-adb-window <serial>` | Report the window manager's current focus declarations |
| `rea inspect-analysis-view <inputJson>` | Project a selected view of completed Evidence JSON for a supported analysis operation. For inventory rows, use --format csv or --format tsv with --filter-output normalized_result.items and --columns logical_path,artifact_id (if those fields are included in the view). |
| `rea inspect-android-class <path> <className>` | Inspect one exact APK class's member inventory |
| `rea inspect-android-jni-bindings <path>` | Link raw DEX native declarations to static JNI export/table candidates without executing the APK |
| `rea inspect-android-method <path> <className> <methodName>` | Decompile one APK method with explicit overload selection |
| `rea inspect-android-package <path>` | Inspect APK declarations and decoded manifest without executing it |
| `rea inspect-api-contract <path>` | Inspect local OpenAPI JSON or GraphQL SDL declarations and field bindings offline |
| `rea inspect-apk-signature <path>` | Inspect declared APK signing schemes, signers and content digests |
| `rea inspect-apktool-client` | Inspect the caller-selected apktool launcher without decoding anything |
| `rea inspect-apple-ips <path>` | Inspect an Apple .ips crash report without executing a target |
| `rea inspect-artifact <path>` | Inspect one artifact and return all available observations and next probes |
| `rea inspect-asset-catalog <path>` | Inspect compiled Apple asset catalog metadata |
| `rea inspect-binary-hardening <path>` | Inspect ELF, PE, and Mach-O hardening without executing the image |
| `rea inspect-binary-layout <path>` | Inspect binary file/linked layout without executing the selected object |
| `rea inspect-byte-entropy <path>` | Inspect file-wide and block byte entropy without executing the file |
| `rea inspect-dart-aot <path>` | Inspect one ABI's Dart AOT snapshot: sections, headers, and the string pool |
| `rea inspect-desktop-application <path>` | Identify desktop runtime candidates from bounded directory and header observations |
| `rea inspect-desktop-application-state <capture>` | Read a desktop application capture folder into the application's state: roles, typed JSON views of each version and kinds of change |
| `rea inspect-devicetree <path>` | Inspect a flattened devicetree blob without executing it |
| `rea inspect-dwarf-units <path>` | Inspect DWARF compile units without executing the image |
| `rea inspect-electron-fuses <path>` | Inspect packaged Electron fuse bytes without launching the application |
| `rea inspect-electron-page <endpoint> <targetId>` | Passively inspect one Electron file page |
| `rea inspect-elf-debug-link <path>` | Inspect ELF separate debug-file linkage without executing the image |
| `rea inspect-elf-dependencies <path>` | Inspect ELF needed libraries and required symbol versions without executing the image |
| `rea inspect-elf-notes <path>` | Inspect ELF PT_NOTE and SHT_NOTE identities without executing the image |
| `rea inspect-elf-unwind-ranges <path>` | Inspect ELF unwind function ranges without executing the image |
| `rea inspect-erlang-beam <path>` | Inspect Erlang BEAM atoms, exports, imports and Code header without executing bytecode |
| `rea inspect-evidence-bundle <inputJson>` | Inspect a local Evidence bundle completely, as discovery metadata, as a page of selected complete records, or as direct-link and retained-closure membership. |
| `rea inspect-evm-interface <path> <encoding>` | Infer interface candidates from explicit local EVM bytecode |
| `rea inspect-firmware-regions <path>` | Inspect firmware signature candidates without extracting them |
| `rea inspect-go-binary <path>` | Inspect embedded Go compiler, modules, build settings and optional static (ptr, len) string literals without target execution |
| `rea inspect-gpu-code-objects <path>` | Inspect embedded CUDA/HIP targets and selected static kernel metadata |
| `rea inspect-il2cpp-metadata <path>` | Inventory IL2CPP global-metadata.dat names, owners and string literals, optionally linking method addresses from the native binary |
| `rea inspect-jeb-client` | Inspect the running JEB MCP client without opening a target |
| `rea inspect-kernel-build-config <path>` | Inspect a Linux kernel image's version banner and embedded build config without executing it |
| `rea inspect-kernel-module <path>` | Inspect Linux kernel module metadata without executing the module |
| `rea inspect-keyed-archive <path> [archive]` | Inspect a Foundation keyed archive as an object-reference graph |
| `rea inspect-macho <path>` | Run inspect_macho without launching Hopper |
| `rea inspect-managed-artifact <path>` | Inspect PE/CLI identity without loading target code |
| `rea inspect-managed-members <path>` | Inspect PE/CLI metadata members, signatures, CIL anchors, and ldstr string literals without loading target code |
| `rea inspect-managed-native-boundaries <path>` | Inspect PE/CLI PInvoke and native implementation boundary declarations without loading target code |
| `rea inspect-maven-gradle-metadata <path>` | Inspect a Maven POM or Gradle module-metadata document without running Maven or Gradle |
| `rea inspect-model-artifact <path>` | Inspect GGUF or safetensors headers without loading model weights |
| `rea inspect-native-api <path> [address]` | Reconstruct one native function API boundary with evidence. Supply at least one of the positional address or --procedure. Equal values are accepted; conflicts fail. |
| `rea inspect-native-data-type <path>` | Inspect one recovered database type or typed data object. Supply exactly one of --type or --address. |
| `rea inspect-native-dispatch-metadata <path>` | Inspect typed Objective-C and Swift dispatch metadata |
| `rea inspect-native-exports <path>` | Inspect a PE or ELF image's export table without executing it |
| `rea inspect-native-initializers <path>` | List ELF and Mach-O initializer and finalizer functions without executing the image |
| `rea inspect-native-instruction <path> <address>` | Inspect a code or data address, its containing Ghidra listing object, and typed incoming references where supported |
| `rea inspect-native-load-image <path>` | Inspect native load observations and supported snapshot verification |
| `rea inspect-ntfs-journal <mftPath> <journalPath>` | Inspect paired offline NTFS MFT and USN journal acquisitions |
| `rea inspect-nuget-nupkg <path>` | Inspect NuGet .nupkg identity, dependency groups and ZIP contents without restore or network |
| `rea inspect-packet-capture <path>` | Inspect an existing packet capture with caller-supplied TShark |
| `rea inspect-packet-fields` | Search installed TShark protocol and field definitions |
| `rea inspect-pcap-capture <path>` | Inspect one pcap/pcapng capture: endpoints, DNS, TLS SNI, and protocol distribution |
| `rea inspect-pcap-client` | Inspect the caller-selected tshark and capinfos binaries without reading a capture |
| `rea inspect-pe-certificates <path>` | Inspect PE Authenticode certificate table identities without verifying signatures |
| `rea inspect-pe-imports <path>` | Inspect PE import and delay-load table identities without executing the image |
| `rea inspect-pe-load-config <path>` | Inspect PE TLS callbacks and load configuration without executing the image |
| `rea inspect-pe-resources <path>` | Inspect PE resource identities, payload ranges, hashes and icon-group relationships |
| `rea inspect-playwright-trace <path>` | Inventory local saved Playwright v10 trace ZIP events offline without launching a browser |
| `rea inspect-plist <path>` | Parse app plist metadata without launching Hopper |
| `rea inspect-python-pyc <path>` | Inspect a supported CPython 3.7–3.15 pyc header and marshal code objects without executing bytecode |
| `rea inspect-recorded-crash <path>` | Inspect supplied core registers/signals and optional debugger mapping evidence |
| `rea inspect-rust-binary <path>` | Inspect an embedded cargo-auditable Rust dependency list without target execution |
| `rea inspect-signal-decoders` | Search installed sigrok decoders or selected decoder help |
| `rea inspect-signature <path>` | Run inspect_signature without launching Hopper |
| `rea inspect-sqlite-database <path>` | Inspect SQLite schema and optional ordinary-table rows from a local snapshot |
| `rea inspect-uefi-firmware <path>` | Map UEFI firmware volumes, FFS files and sections of a flash image |
| `rea inspect-uefi-nvram <path>` | Map AMI NVRAM variable stores (for example StdDefaults) of a flash image |
| `rea inspect-v8-code-cache <path>` | Inspect a V8 code cache header and its embedded printable byte patterns without executing it |
| `rea inspect-wasm-artifact <path>` | Inspect an explicit local WASM artifact with WABT |
| `rea inspect-web-event-listeners <endpoint> <targetId> <selector>` | Inspect native listener source locations on the first main-document CSS match |
| `rea inspect-web-network-capture <capturePath> <format>` | Inspect retained HAR, native mitmproxy, Fiddler SAZ or aioquic qlog records without fetching recorded URLs |
| `rea inspect-web-page <endpoint> <targetId>` | Passively inspect one page through CDP, defaulting to its current origin |
| `rea inspect-windows-shortcut <path>` | Inspect a Windows Shell Link (.lnk) without resolving or executing the target |
| `rea inspect-with-objdump <path> <operation>` | Inspect a local artifact using GNU-style objdump arguments and retain the selected command output as Evidence |
| `rea install-adb-package <serial> <apk-path>` | Install one local APK; --replace requests reinstall mode to keep existing app data |
| `rea instructions <path> [address]` | Read every raw instruction without decompiling. Supply at least one of the positional address or --procedure. Equal values are accepted; conflicts fail. |
| `rea instrument-with-frida <mode> <target>` | Run one Frida script against a selected process and detach. Provide exactly one of --script or --script-file. |
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
| `rea list-objdump-architectures` | Capture the selected objdump command response to -i |
| `rea match-native-functions <inputJson>` | Match two observed native function inventories without executing targets |
| `rea observe-javascript-runtime <endpoint> <targetId>` | Passively observe one exact Node/Electron Inspector target |
| `rea observe-native-calls <path> <inputJson>` | Launch a Mach-O under LLDB and record entries into selected functions or Objective-C methods |
| `rea observe-native-ui <path>` | Observe one already-running native application window by PID and window ID |
| `rea observe-web-execution <endpoint> <targetId>` | Observe precise page execution; resets counters and temporarily disables optimization |
| `rea observe-web-session <endpoint> <targetId>` | Observe user-driven page navigation during a chosen window |
| `rea open-jeb-project <path>` | Open or create a JEB project from an artifact or .jdb2 database |
| `rea procedure-references <path> [procedure]` | Inspect incoming or outgoing references for one native procedure. Supply at least one of the positional address or --procedure. Equal values are accepted; conflicts fail. |
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
| `rea read-bytes <path> <address>` | Read provider memory bytes; Ghidra memory may include loader fixups and differ from file bytes |
| `rea reconcile-javascript-runtime <inputJson>` | Reconcile static application and passive runtime Evidence JSON |
| `rea recover-javascript-sources <path> <outputDirectory>` | Recover readable JavaScript modules with source provenance and verified files |
| `rea resolve-adb-packages <serial> <query>` | Find installed packages by case-insensitive name substring |
| `rea resolve-native-call-targets <path> <address>` | Resolve one static native call site |
| `rea search <path> [pattern]` | Search every analyzed string or procedure name. Supply at least one of the positional pattern or --pattern. Equal values are accepted; conflicts fail. |
| `rea search-android-classes <path> <query>` | Search APK class names; empty query inventories all classes |
| `rea search-bytes <path> <pattern>` | Find masked bytes; unbounded searches skip unloaded blocks and overlays |
| `rea setup` | Configure agent integrations and optional analysis providers |
| `rea start-adb-activity <serial> <action>` | Start an intent with am start (action, URI, component, extras) |
| `rea start-adb-app <serial> <package>` | Start one installed app by resolving and launching its launcher activity |
| `rea stop-adb-app <serial> <package>` | Force-stop every process of one package |
| `rea trace <path> [query]` | Trace a literal feature through analyzed references. Supply at least one of the positional query or --query. Equal values are accepted; conflicts fail. |
| `rea trace-android-references <path> <className>` | Trace APK using nodes for a defined class/method or an externally invoked DEX method |
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
| `rea validate-browser-scenario <inputJson>` | Validate one browser scenario without launching or attaching to a browser |
| `rea verify-managed-native-boundaries <inputJson>` | Verify managed P/Invoke declarations against authenticated native Evidence |
| `rea xrefs <path> [address]` | List bounded, untyped references to an analyzed address. For typed incoming references, use inspect-native-instruction at the target address where supported. Supply at least one of the positional address or --address. Equal values are accepted; conflicts fail. |

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
- 旧版本文件（如 `rea-6.7.0.md`、`rea-6.8.0.md`）**保留不删**，用于回溯「当时这个工具叫什么」。
- 2026-11-25：从 6.8.0 同步到 6.10.1，新增 34 个工具（含构建计算机族、UEFI、ELF/DWARF、API 契约、JNI 等）与 29 条 CLI，旧工具零删除、零改名候选。
