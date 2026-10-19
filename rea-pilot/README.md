# rea-pilot

<p align="center">
  <img src="assets/banner.svg" alt="rea-pilot" width="100%">
</p>

> REA 的引航员：把 REA 装进你当前的编程助手、验证真的连上，再按目标给你选路、排障、回滚与加固建议——不替你开船。

## 它解决什么问题

REA（<https://rea.tools/>）是一个跑在本地、把逆向证据喂给助手的工具。它的官方技能教「连上之后怎么调查」，但真装过的人会卡在前面的三件事：

1. **装不上或接不上**：Node 版本、PowerShell 拦 `npx`、宿主配置格式、注册写在哪、要不要重启，全靠猜。
2. **不知道装好没有**：`rea mcp doctor` 绿了不等于你的会话里已经有工具。
3. **装完不会用**：手上一堆工具（REA 6.7.0 实测 207 个 MCP 工具 / 153 条 CLI 命令 / 6 个官方 prompt，见[工具面快照](references/toolset/rea-6.7.0.md)），不知道面对一个具体目标该走哪条最小路径；也不知道自己写的东西该怎么加固。

rea-pilot 把这三件事变成流程：**先体检、再出计划、人确认、再执行、最后三问验证**；选路与加固都落到具体命令与判据上。

## 快速开始

### 前置要求

| 项 | 要求 | 怎么确认 |
| --- | --- | --- |
| 运行环境 | Node.js `^22.19.0 \|\| ^24.11.0 \|\| >=26.0.0`（REA 6.7.0 的 `engines.node`） | `node -v`；`rea doctor` 的 `node` 检查为 healthy（本机 24.13.0 通过） |
| 宿主 | 任何支持本地 **MCP stdio** 的编程助手 | 判据是 `rea doctor --format json` 的 `identity.registrations[]`——本机 6.7.0 收录 **20 个**适配器：`dsh`（`~/.dsh/cordis.patch.yml`）、`claude_code`（`~/.claude.json`）、`opencode`、`qoder`、`trae` 已 `aligned`；其余 15 个（antigravity、claude_desktop、codex、copilot_cli、cursor、droid、gemini_cli、grok_build、hermes、kimi、omp、qwen_code、vscode、workbuddy、zcode）需跑 `rea setup` 对齐。注意 `scope_checks` 里的 `registration:<client>` 是**未对齐子集**，不是完整清单。REA 没有适配器的宿主走下面的「宿主手动接入」 |
| 分析引擎 | 可选，用户自备（Ghidra / IDA / JADX / Kuna / tshark 等）；REA 不下载、不安装 | `rea doctor --format json` 里 `missing_analysis_engine` 的条目；缺引擎时归档与载荷、Android 清单、JavaScript/Electron、托管程序、已保留证据类工作仍可做 |
| 权限 | 会修改你**已有**的 MCP 配置文件（改前留备份） | 先跑 `rea setup --dry-run`，看 `plannedActions[].backupPath` |

### 安装技能

```bash
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill rea-pilot
```

命令原文来自本仓[根 README](../README.md)。[未经运行验证]：本次未在本机执行该命令（技能是否就绪可用 `npx skills list` 自查）。

装好后对助手说一句即可：

```text
用 rea-pilot 把 REA 接到我这个助手，先给我看安装计划再执行
```

### 装完怎么自己确认（三问，缺一不算）

| # | 问什么 | 命令 | 通过判据 | 验证状态 |
| --- | --- | --- | --- | --- |
| ① | server 起得来吗 | `rea mcp doctor --json` | `healthy: true`，`inventory.tools.expected == observed`，missing / unexpected / duplicates 为空 | [已运行验证] 本机 6.7.0 |
| ② | 宿主注册对齐了吗 | `rea doctor --format json` | 该宿主的 `registrations[].state == "aligned"` | [已运行验证] 本机 6.7.0 |
| ③ | 会话里真有工具吗 | 重启宿主后看工具列表 | 出现 `mcp__rea__<tool>` | [未经运行验证] 取决于你的宿主 |

判据出处与失败分流 → [references/workflows/install-and-verify.md](references/workflows/install-and-verify.md)。注意 `rea doctor` 退出码非 0 是正常的**状态报告**（缺引擎 / 有漂移），不是命令失败。

## 怎么用

| 你说的话（触发示例） | 一句话方法 | 示例提示词 |
| --- | --- | --- |
| 帮我装一下 REA / 把 REA 接到我的 Cursor | 先 `rea doctor` 体检并按 classification 分流，再把 `rea setup --dry-run` 的计划翻成人话给你确认，确认后才执行 | `帮我在这台机器上装 REA，先给我看它准备改哪些文件` |
| REA 装好了吗 / 我怎么确认它真连上了 | 三问分开答（见上面自检表）：`rea mcp doctor` / 注册 `state=aligned` / 重启后工具真出现 | `REA 装了吗？我怎么确认它真的连上了我的助手` |
| 我的助手 setup 认不出来，怎么手动接 MCP | 走宿主手动接入：只给通用字段与探索提示词，由宿主自己去定位并插入自己的配置，再验证 | `我的助手不在 REA 支持列表里，你教我怎么手动加 MCP 服务器` |
| 我有一个 exe（或 asar / apk / 网站），想逆向，该怎么下手 | 先定目标类型，再定证据需求，最后给 3–5 条带判据的最小路径 | `我有一个 Electron 应用（app.asar），想搞清它的剪贴板行为，该怎么查` |
| 我该怎么做加密和加壳，才能防住这种逆向 | REA 能拿到什么，你就在哪层补什么；每条都给代价与 REA 复跑验收判据 | `看完我的 Android 应用能拿到什么，我该怎么加密和加壳` |
| REA 升级了，工具清单对不上 | 读官方 CHANGELOG → 重新生成带版本号的工具表 → 四处版本对齐 | `REA 更新了，把工具清单刷新一下` |
| 把 REA 卸掉 / 装坏了想还原 | 先取证会动哪些文件，再 `rea uninstall`，必要时用备份路径还原 | `把 REA 卸干净，别动我的其他 MCP 配置` |

路由只看三件事：是「装接类」还是「用 REA 类」／会不会改本机配置／目标是否自有或已授权。

## 它怎么工作（六条工作流）

| 工作流 | 什么时候走 | 必须产出 |
| --- | --- | --- |
| W-INSTALL 接入与验证 | 装、接、验 | 环境体检结论（按 classification 分流）+ 人读安装计划（改哪些文件、备份在哪）+ 执行结果 + 三问验证回执 |
| W-HOST 宿主自接入 | `setup` 认不出你的宿主 | 通用字段与探索提示词（宿主自己插入）+ 重启后的验证方法 |
| W-ROUTE 目标选路 | 问「这个目标怎么逆、用哪些工具」 | 目标类型 → 证据需求 → 引擎前置 → 3–5 条最小路径；无引擎时给替代路径 |
| W-HARDEN 逆向反推防护 | 问「我该怎么加密、加壳、防逆向」 | 通用方法论（算法 / 密钥 / 完整性 / 混淆 / 加壳 / 运行时）→ 该项目该补哪几层 → 每条给代价与 REA 复跑验收判据 |
| W-SYNC 版本同步 | REA 升级、工具清单对不上 | 新的 `references/toolset/rea-<版本>.md` + 指向更新 + 四处版本对齐 |
| W-ROLLBACK 回滚 | 要卸载 REA，或配置被改坏 | 取证 → 卸载 → 还原三步 + 为什么这么做 |

六条工作流的完整步骤、检查点与验证点都在 [references/workflows/](references/workflows/)；SKILL.md 只做路由与硬边界。

## 能逆什么（目标类型 × 前置）

| 目标 | 典型形态 | 主要证据面 | 引擎前置 |
| --- | --- | --- | --- |
| 原生可执行 / 库 | exe、dll、so、dylib、App 主二进制 | 函数伪代码、调用图、字符串与常量、段权限 | Ghidra 12.1.x（+ 64 位 JDK 21+）或 Hopper（仅 macOS）；Windows 上 Ghidra 官方标注实验性 |
| 托管程序 | .NET PE / CLR 程序集 | 类型与成员、CIL、P/Invoke 边界 | 不需要外部引擎 |
| Electron / JavaScript | `app.asar`、应用目录、bundle | 模块图、IPC handler 配对、暴露 API、fuses | 不需要外部引擎 |
| 打包移动应用 | apk / aab / ipa / hap | 清单与组件、资源、类与方法、AOT 快照 | 清单与资源不需要；源码级反编译需自备 JADX（`REA_JADX_MCP_JAR`） |
| 归档与载荷 | zip / pkg / dmg / 安装包 | 嵌套清单、内部结构、签名 | 不需要外部引擎 |
| 固件 | 镜像 / 分区 / 嵌入式包 | 固件区段、提取出的文件系统与二进制 | Linux + 自备工具链 |
| 运行中的浏览器 | 本地 CDP 端点 | 页面结构、脚本、事件监听、网络 | 需可达的 CDP 端点 |
| 运行中的原生应用 | 本机进程 | 调用观测、UI 观测、内存与插桩 | 调用观测在 macOS 由 LLDB 承担；插桩走 Frida（有真实副作用，先声明） |
| 抓包与信号 | pcap / pcapng / 逻辑采样 | 端点、DNS/TLS SNI、协议、HTTP URI | Linux + 自备 tshark / capinfos / sigrok 与环境变量 |
| 数据库与本地存储 | sqlite / 偏好文件 | 表结构、行样本 | sqlite 需 Node 24.x ≥ 24.15 或 26+ |
| WASM / EVM | .wasm / 字节码 | 导入导出接口、函数选择器 | WASM 校验需自备 WABT |

先想清楚要回答**什么问题**，再选证据面：

| 你想回答 | 证据需求 | 首选入口 |
| --- | --- | --- |
| 这个功能是怎么实现的 | 静态结构 | `binary_overview` → `search_strings` → `analyze_function` / 应用图 |
| 运行时它做了什么 | 运行时行为 | `open_binary` + `capture_process_scenario`，或 CDP 的 `inspect_web_page` |
| 两个版本差在哪 | 版本对比 | `compare_application_versions` / `compare_artifacts` |
| 为什么崩 | 崩溃 + 调用/引用 | `inspect_recorded_crash` + `trace_call_path` |
| 谁引用了这个字符串或地址 | 引用图 | `search_strings` → `xrefs` |

最小路径长这样（示意，按你的目标替换）：

```bash
npx -y rea-agents@latest analyze <目标> --format json                          # 先拿总览，确认打的是对的文件
npx -y rea-agents@latest search <目标> "<关键字>" --format json                 # 用字符串/符号把范围缩到一个点
npx -y rea-agents@latest function <目标> <符号> --provider ghidra --json        # 再深挖一个函数
```

[未经运行验证]：命令形态来自 [references/workflows/route-target.md](references/workflows/route-target.md)，本次未在本机复跑。

无引擎时也有替代路径：缺 Ghidra/Hopper → JavaScript/Electron 应用图、归档与包清单、Android 清单与资源、字符串与符号级检索、已有证据包的重读与对比；缺 JADX → Android 清单、资源、类与方法级结构仍可用；全都缺 → 只做「读已保留证据」类工作。

## 加固建议（逆向反推防护）

不是「扫描你的项目找漏洞」，而是：**REA 能拿到什么，你就在哪一层补什么，然后用同一条 REA 命令验收**。四条原则是：客户端不可信（秘密留在服务端）、分层（静态 → 动态 → 数据 → 密钥 → 服务端）、成本-收益（强度按资产价值定，代价给可测数字）、可验证闭环（加固前能拿到 X → 加固后拿不到）。

| 攻击者拿到什么（REA 能力） | 你该补什么 |
| --- | --- |
| 硬编码密钥、内部 endpoint、路径与字段名 | 密钥不落客户端（短期令牌或服务端代理）；发布构建 strip 符号 |
| 业务逻辑、算法与协议 | 控制流平坦化与指令替换、JS 混淆、原生加壳（先查商店与杀软政策） |
| 缺 NX / ASLR / RELRO、可写可执行段 | 开启 PIE/ASLR、NX、Full RELRO、Stack Canary、CFG；剥离调试信息 |
| 未签名、宽松 entitlements | 代码签名 + Hardened Runtime + 最小 entitlement |
| asar 可读、fuses 放行 runAsNode | Electron 开 asar integrity、收紧 fuses |
| exported 组件、debuggable、allowBackup、明文资源 | 关非必要 exported、关 debuggable、收紧权限与备份 |
| 明文 HTTP、可读 JSON、固定 API 路径 | TLS 1.3 + HSTS、证书绑定、请求签名 |
| 明文数据库与偏好文件 | 整库加密（SQLCipher 类）、字段级 AEAD、密钥入 Keychain / Keystore |
| 内存明文、解密后明文、注入点 | 反调试与反注入检测、越狱/root 检测、密钥短驻留并零化 |
| 版本差异暴露修复点与旧漏洞 | 服务端能力开关灰度、协议版本化、旧客户端强制下线 |
| 未加密固件、硬编码出厂凭据 | 固件签名与安全启动、每设备唯一密钥、出厂凭据不入镜像 |

算法与实现（通用做法，参数以各自官方文档当前版本为准）：AEAD 用 AES-256-GCM 或 ChaCha20-Poly1305；密钥协商 X25519/ECDH + HKDF，签名 Ed25519 或 ECDSA P-256；口令派生 Argon2id → scrypt → PBKDF2-HMAC-SHA256；完整性 HMAC-SHA256 或 AEAD tag；随机数用平台 CSPRNG；实现用成熟库（libsodium / BoringSSL / Tink 类）；传输 TLS 1.3 + 证书绑定 + 请求签名。

三条禁令：不输出任何真实密钥或凭据值、不承诺「不可破解」、不提供绕过他人保护的方法；且只服务你自己拥有或已获授权的资产。

完整方法论（11 行能力镜像矩阵 + 每条代价与验收判据）→ [references/workflows/hardening-advice.md](references/workflows/hardening-advice.md)。

## 设计取舍

| 取舍 | 选择 | 为什么 |
| --- | --- | --- |
| 与官方自带技能的关系 | 互补窄定位，不重写调查方法 | 自带技能已经覆盖「怎么用 REA 取证据」，重写只会互相打架；本技能只占它前面和外面 |
| 工具清单 | 生成带版本号的 `references/toolset/rea-<版本>.md`，不手写进 SKILL.md | 官方近 30 天发 13 个版本，手抄清单约 2 天过期一次 |
| 宿主配置 | 只给通用字段 + 探索提示词，由宿主自己插入自己的配置 | 各宿主配置格式不同（JSON / JSONC / TOML），替它猜路径最容易写坏别人的配置 |
| 「装好了」的判据 | 三问分开答，缺一不算 | `mcp doctor` 绿只证明 server 能启动，不证明你的会话里已经有工具 |
| 加固建议 | 逆向反推防护（REA 能拿到什么 → 你该补什么），并要求用 REA 复跑验收 | 通用扫描器式建议没有验收闭环；反过来用攻击面清单才可验证 |
| 回滚与安装同权重 | 卸载与还原单独成一条工作流，顺序固定为先取证再动手 | 安装会修改用户已有的 MCP 配置文件，这是全链上唯一的不可逆风险点 |

## 与相邻技能的边界

| 相邻 | 边界 |
| --- | --- |
| REA 自带技能 `reverse-engineer-anything` | 它管「连上之后怎么调查」；本技能管「怎么连上、连上没有、该查什么、怎么加固、怎么退回」 |
| 通用逆向/安全技能 | 本技能只做 REA 的接入与选路，不替代漏洞扫描、代码审计 |
| 项目协作类技能（vibe-*） | 本技能不写项目契约、不碰进度与交接 |

### 不适用

- 目标已经接上之后的**具体调查步骤与证据解释** → 读 REA 自带技能 `reverse-engineer-anything`。
- 纯源码仓库的架构阅读与重构 → 与本技能无关。
- 未授权资产的破解、绕过他人保护、真实密钥提取 → 明确拒绝，不做。
- 漏洞扫描与代码审计 → 本技能不做，只做 REA 的接入、选路、加固建议与回滚。

## 常见卡点

| 现象 | 原因 | 怎么办 |
| --- | --- | --- |
| PowerShell 拦脚本，`npx` 不执行 | 执行策略拦掉了 `.ps1` 垫片 | 改用 `npx.cmd rea-agents@latest setup --dry-run` |
| `rea doctor` 退出码非 0 | 那是状态报告（缺引擎 / 有漂移），不是命令失败 | 看 `scope_checks[].classification`，别当报错 |
| doctor 里没有我的宿主 | REA 的 `identity.registrations[]` 里没有它（那 15 个只是未对齐子集，不是完整清单） | 走「宿主手动接入」；或用 `rea setup --all-detected`（需明确同意） |
| 注册写了，会话里还是没工具 | 宿主没重启，或配置里钉的包版本不对 | 先重启宿主，再看 `registration.state` 与 `package_reference` |
| 配置被写坏 | `rea setup` 改了你已有的文件 | 用 `plannedActions[].backupPath` 还原 |
| 缺分析引擎，算装失败吗 | 不算：接入与引擎是两件事 | 换目标类型，或按需自备引擎 |
| 长驻会话后续调用异常 | Ghidra / Hopper / 调试器 / Frida 会话没关 | 用完 `close_binary` / `close_*_session` |

以上现象与处置来自本技能 references 的实测口径，未逐条在本机复跑；逐条来源见 [references/workflows/install-and-verify.md](references/workflows/install-and-verify.md) 与 [SKILL.md](SKILL.md) 的 Gotchas。

## 目录结构

```text
rea-pilot/
├── SKILL.md                        # 路由与硬边界（细节在 references）
├── README.md                       # 本文件：人读门面
├── CHANGELOG.md
├── assets/
│   └── banner.svg                  # 门面图（tupu 横版）
└── references/
    ├── workflows/                  # 六条工作流（@工作流 / @步骤N / @验证点）
    │   ├── install-and-verify.md
    │   ├── host-registration.md
    │   ├── route-target.md
    │   ├── hardening-advice.md
    │   ├── version-sync.md
    │   └── rollback.md
    ├── specs/
    │   ├── mcp-registration-fields.md   # MCP 通用字段与校验
    │   └── toolset-generation.md        # 工具表生成规范
    ├── config/
    │   └── engines-and-providers.md     # 引擎矩阵与环境变量
    └── toolset/
        └── rea-6.7.0.md                # 带版本号的工具面快照（207 + 6 + 153）
```

## 版本与许可

当前版本：**v1.0.0**，详见 [CHANGELOG.md](CHANGELOG.md)。

工具面快照对应 REA **6.7.0**（207 个 MCP 工具 / 6 个官方 prompt / 153 条 CLI 命令）：[references/toolset/rea-6.7.0.md](references/toolset/rea-6.7.0.md)。

许可：MIT License（[LICENSE](../LICENSE)，Copyright (c) 2026 ErgeAIA）。
