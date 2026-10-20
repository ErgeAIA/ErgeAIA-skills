# rea-pilot 版本记录

> 只记录版本号、核心变更与修改文件。设计取舍见 README，生成规范见 references。

---

## v1.0.1 (2026-10-20)

### 路由补丁与工具表字符数口径修正

**背景**：对 v1.0.0 的路由去重跑了一轮回归（`test-prompts.json` 同批 3 条只读 prompt，与去重前 dim8 湿评同题同约束）。三条都自证「工作流文件路径取自「何时使用」表第三列」并引用原文行，无断链、无退化。回归暴露出两个既有问题（都不是去重引入的）。

**变更**

- **复合意图路由**（`SKILL.md` 步骤 1，新增一段）：一条请求同时含两个意图时（例：「装好没 + 能不能做原生反编译」），原文只写「一次只进一条，不并列」，模型只能自行即兴（回归中 p1 取 W-INSTALL 为主 + 引用 W-ROUTE 的引擎前置小节）。现明确：主路由完整跑完，其它意图只在需要前置判定时引用对应工作流的对应小节并写明引用了哪条、为什么——仍不并列展开两条工作流。
- **工具表字符数口径**（`references/specs/toolset-generation.md`、`references/toolset/rea-6.7.0.md`）：`rea --llms` 的行数与字符数随计法摆动（本机一手实测：`@(rea --llms).Count`=161 行、LF 拼接 17,216 字符、CRLF 拼接 17,376 字符、`Out-String` 17,378 字符），三条回归子 agent 都在这处对账上花了工夫、各自判了一次「是否漂移」。口径改为：**判漂移看命令条数（153）、工具数（207/6）与目录摘要，字符数只作参考并给出实测区间**。

**修改文件**：`SKILL.md`、`CHANGELOG.md`、`README.md`、`test-prompts.json`、`references/specs/toolset-generation.md`、`references/toolset/rea-6.7.0.md`、`../README.md`、`../README.en.md`

## v1.0.0 (2026-10-19)

### 首次发布：REA 接入、选路与逆向反推防护

**背景**：REA 自带技能 `reverse-engineer-anything` 覆盖「连上之后怎么调查」，但没覆盖「怎么装、怎么接进用户自己的助手、怎么验证真的连上、升级后怎么同步、怎么卸载还原」，也没有官方的加固建议流程。本技能补的正是这一段。

**变更**

- 六条工作流：W-INSTALL 接入与验证 / W-HOST 宿主自接入 / W-ROUTE 目标选路 / W-HARDEN 逆向反推防护 / W-SYNC 版本同步 / W-ROLLBACK 回滚。
- 硬规则：改配置前先出计划、不确认不执行、`--yes` 不写默认、「连上了」必须三问分开答（mcp doctor / registration state / 重启后工具出现）。
- 版本锚定为实测：`rea --version`、`rea doctor`、`rea mcp doctor`、`rea --llms`；工具清单**生成**而非手抄。
- 生成 `references/toolset/rea-6.7.0.md`：207 个 MCP 工具（按 12 个域分组，每条含用途与副作用/可用性）+ 6 个官方 prompt + 153 条 CLI 命令，并写明 CLI 名与 MCP 名不是一一对应。
- 所有 `references/**/*.md` 带 YAML 头（`name` / `description` / `version` / `trigger-when` / `reads-from` / `writes-to`），由 AI 判断「何时读这个文件、读完写去哪」。
- W-HARDEN 定位为「把 REA 的攻击面清单反过来当开发者加固方法论」，并用 REA 复跑验收；三条禁令（不输出真实密钥值 / 不承诺不可破解 / 不提供绕过他人保护的方法）。

### 门面与文档补做（2026-10-20，未升版）

- **门面**：README 顶部挂 tupu 横版技能图谱 `assets/banner.svg`（1920×1200，theme=coding）；源产物留 `Doc-Depot/Inbox/tupu/rea-pilot/`，不写回技能目录。
- **README 扩写**：93 → 215 行——补快速开始（前置要求 / 安装技能 / 装完三问自检）、六条工作流表、目标类型 × 引擎前置表、加固建议摘要与常见卡点，并补「不适用」边界；原「触发词」与「怎么用」两张重复表合并为一张；命令逐条标注验证状态。细项归子库 git log。

### 事实纠错与评测集（2026-10-20，未升版）

- **纠错**：曾把 `rea doctor` 的 `scope_checks` 里 `registration:<client>`（**未对齐子集**，本机 15 项）当成完整客户端清单，据此写坏 `README.md`（宿主行 + 卡点行）并一度改错 `SKILL.md:109`。真值：`identity.registrations[]` 共 **20 个**适配器，`dsh` 与 `claude_code` 均在列且本机 `aligned`。现 `SKILL.md:109` 与 README 两处统一以 `identity.registrations[]` 为判据。
- **新增 `test-prompts.json`**：3 条只读评测 prompt（版本与引擎体检 / Electron asar 选路 / 加固建议），供 darwin-skill dim8 实测与后续回归复用。

### 审查后结构优化（2026-10-20，未升版）

- **路由表去重**：原先「用户说 → 工作流」「工作流 → 文件」「何时读 → 文件 → 用途」三张表各写一遍六条工作流，读者要跨表拼接；现在「何时使用」一张表直接给「用户说 / 工作流 / 读这个文件」，步骤 1 只留三问与指针，资源节只列非工作流参考文件。三张表 → 两张，路由一跳到位。
- **交付格式补示例**：步骤 3 补「命令 + 原始输出要点」的回执格式示例（三问验证示例，值明确标注为示意、以本机实测为准），回应 darwin dim5「格式偏抽象、无示例块」。

**修改文件**：`SKILL.md`、`README.md`、`CHANGELOG.md`、`references/workflows/*.md`（6）、`references/specs/*.md`（2）、`references/config/engines-and-providers.md`、`references/toolset/rea-6.7.0.md`、`assets/banner.svg`、`test-prompts.json`。
