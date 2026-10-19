---
name: "W-HARDEN 逆向反推防护"
description: "把 REA 的攻击面清单反过来当开发者的加固方法论，并给出代价与 REA 复跑验收判据。"
version: 1.0.0
trigger-when: 用户问自己的应用该怎么加密、加壳、防逆向时
reads-from: SKILL.md, references/toolset/rea-<版本>.md
writes-to: 无（只读建议；不修改用户代码）
---
# @工作流: W-HARDEN 逆向反推防护

**这不是「扫描你的项目找漏洞」，而是：REA 能拿到什么，你就在哪一层补什么，然后用同一条 REA 命令验收。**

## @步骤1: 先确认资产归属与目标层级

- 只服务用户**自己拥有或已获授权**的资产；归属不明先问清，不猜。
- 先问「要保护的是什么」：密钥与凭据 / 业务逻辑与算法 / 协议与接口 / 数据与隐私 / 授权与付费。目标不同，层级不同。

## @步骤2: 讲通用方法论（先于任何工具）

四条原则：

1. **客户端不可信**：攻击者拥有设备、二进制与内存，纯客户端的机密最终都能被提取。目标是**提高提取成本 + 把真正的秘密留在服务端**。
2. **分层**：静态（读代码）→ 动态（跑起来看）→ 数据（传输 / 落盘 / 内存）→ 密钥 → 服务端。每加一层都要能回答「挡住哪一类逆向证据」。
3. **成本-收益**：混淆与加壳带来体积、启动耗时、崩溃难定位、杀软与商店误报。强度按资产价值定，代价要给可测数字。
4. **可验证（闭环）**：每条建议都要能用 REA 复跑同一命令验收 ——「加固前能拿到 X → 加固后拿到 Y 或拿不到」。REA 在这里从攻击工具变成**验收工具**。

## @步骤3: 逆向手段 → 攻击者拿到什么 → 你该补什么

| 逆向手段（REA 能力） | 攻击者拿到什么 | 开发者做法 | 代价与验证 |
| --- | --- | --- | --- |
| 字符串与符号提取（`search_strings` / `list_names` / `list_strings`） | 硬编码密钥、内部 endpoint、路径与字段名 | 密钥不落客户端（短期令牌或服务端代理）；发布构建 strip 符号；字符串与常量池加密 | 可诊断性下降；复跑字符串检索不再命中密钥关键字 |
| 反编译与伪代码（`procedure_pseudo_code` / `analyze_function`） | 业务逻辑、算法与协议 | 控制流平坦化与指令替换、JS 混淆、原生加壳（先查商店与杀软政策）、Dart AOT 快照保护 | 体积与启动耗时上升、崩溃定位变难；复跑伪代码看可读性 |
| 段权限与 mitigations（`inspect_binary_layout`） | 缺 NX / ASLR / RELRO、可写可执行段 | 开启 PIE/ASLR、NX、Full RELRO、Stack Canary、CFG；剥离调试信息 | 近乎零成本；复跑 layout facet 应全绿 |
| 签名与 entitlements（`inspect_signature` / `inspect_macho`） | 未签名、宽松 entitlements、未开硬化运行时 | 代码签名 + Hardened Runtime + 最小 entitlements + 公证；Android v2/v3 签名 + Play Integrity | 证书链与流程成本；复跑签名检查 |
| 打包与运行时开关（`inspect_artifact` / `inspect_electron_fuses`） | asar 可读、fuses 放行 runAsNode、asar 完整性关闭 | Electron：开 asar integrity、收紧 fuses、关 `ELECTRON_RUN_AS_NODE`；安装包校验 | 构建链改动；复跑 fuses facet |
| Android 清单与资源（`inspect_android_package` / `decode_android_resources`） | exported 组件、debuggable、allowBackup、明文资源 | 关非必要 exported、`debuggable=false`、`allowBackup=false`、资源字符串加密 | 低；复跑 manifest facet |
| 流量观察（`inspect_pcap_capture` / `analyze_web_bundle` / web capture） | 明文 HTTP、可读 JSON、固定 API 路径 | TLS 1.3 + HSTS；证书绑定；请求签名（HMAC + 时间戳 + nonce 防重放）；字段级 AEAD | 证书绑定与抓包自测冲突（留审计旁路）；抓包只见 TLS |
| 静态存储（`inspect_sqlite_database` / `pull_adb_file`） | 明文数据库与偏好文件 | 整库加密（SQLCipher 类）；字段级 AEAD；口令走强 KDF；密钥入 Keychain / Keystore | 性能与迁移成本；复跑文件不再直读 |
| 运行时插桩（Frida / `capture_process_scenario` / `observe_javascript_runtime`） | 内存明文、解密后明文、注入点 | 反调试与反注入检测、越狱/root 检测、密钥短驻留并零化、必要时白盒密码学 | 与自测可观测性冲突；插桩应记为异常路径 |
| 版本与产物对比（`compare_application_versions` / `compare_artifacts`） | 版本差异暴露修复点与旧漏洞 | 服务端能力开关灰度、协议版本化、旧客户端强制下线；不留「此处修复 X」痕迹 | 低；对比结果不再泄露修复意图 |
| 固件与载荷（`inspect_firmware_regions` / `extract_firmware`） | 未加密固件、硬编码出厂凭据 | 固件签名与安全启动、每设备唯一密钥、出厂凭据不入镜像 | 产线流程与密钥注入；校验签名链 |

## @步骤4: 算法与实现选择（通用做法，参数以各自官方文档当前版本为准）

- 对称加密（数据面）：AES-256-GCM 或 ChaCha20-Poly1305（AEAD 自带完整性）；不用 ECB；nonce 绝不复用。
- 非对称与密钥协商：X25519 / ECDH + HKDF 派生；签名 Ed25519 或 ECDSA P-256；RSA 仅在互操作需要时用且走 OAEP。
- 口令派生：Argon2id 优先，其次 scrypt，再退 PBKDF2-HMAC-SHA256；参数按 OWASP Password Storage Cheat Sheet 当前版本取值（**不写死数字**，避免过期）。
- 完整性：HMAC-SHA256 或 AEAD 自带 tag；不用裸 MD5 / SHA1 做认证。
- 随机数：平台 CSPRNG（getrandom / SecRandomCopyBytes / java.security.SecureRandom）；禁用 `rand()`。
- 实现：用成熟库（libsodium / BoringSSL / Tink 类），不自造算法；密钥管理走 KMS / Keychain / Keystore。
- 传输：TLS 1.3 + 证书绑定 + 请求签名。

## @步骤5: 落到这个项目（用 REA 复跑验收）

1. 先用 REA 取**加固前**的证据（同一命令、同一目标），把「现在能拿到什么」写成一条条事实。
2. 按 @步骤3 挑出这个项目真正该补的 2–4 层（不要一次列十条）。
3. 每条给「改完怎么验」：复跑哪条 REA 命令、期望看到什么变化。
4. 交付时给代价（体积 / 启动 / 可诊断性 / 商店政策），别只给结论。

@验证点：交付必须包含① 资产归属与保护目标② 通用方法论③ 针对该项目的 2–4 条具体做法④ 每条的 REA 复跑验收命令与判据⑤ 代价。

## 三条禁令与边界

- 不输出任何**真实密钥或凭据值**（只给位置与类型）。
- 不承诺「不可破解」。
- 不提供绕过他人保护、破解他人应用的方法。
- 客户端加固只**提高成本**，不提供绝对安全；商店政策、杀软误报、体积与启动代价必须给实测数字。
