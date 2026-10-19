# rea-pilot 版本记录

> 只记录版本号、核心变更与修改文件。设计取舍见 README，生成规范见 references。

---

## v1.0.0 (2026-10-19)

### 首次发布：REA 接入、选路与逆向反推防护

**背景**：REA 自带技能 `reverse-engineer-anything` 覆盖「连上之后怎么调查」，但没覆盖「怎么装、怎么接进用户自己的助手、怎么验证真的连上、升级后怎么同步、怎么卸载还原」，也没有官方的加固建议流程。本技能补的正是这一段。

**变更**

- 六条工作流：W-INSTALL 接入与验证 / W-HOST 宿主自接入 / W-ROUTE 目标选路 / W-HARDEN 逆向反推防护 / W-SYNC 版本同步 / W-ROLLBACK 回滚。
- 硬规则：改配置前先出计划、不确认不执行、`--yes` 不写默认、「连上了」必须三问分开答（mcp doctor / registration state / 重启后工具出现）。
- 版本锚定为实测：`rea --version`、`rea doctor`、`rea mcp doctor`、`rea --llms`；工具清单**生成**而非手抄。
- 生成 `references/toolset/rea-6.7.0.md`：207 个 MCP 工具（按 12 个域分组，每条含用途与副作用/可用性）+ 6 个官方 prompt + 153 条 CLI 命令，并写明 CLI 名与 MCP 名不是一一对应。
- W-HARDEN 定位为「把 REA 的攻击面清单反过来当开发者加固方法论」，并用 REA 复跑验收；三条禁令（不输出真实密钥值 / 不承诺不可破解 / 不提供绕过他人保护的方法）。

**修改文件**：`SKILL.md`、`README.md`、`CHANGELOG.md`、`references/workflows/*.md`（6）、`references/specs/*.md`（2）、`references/config/engines-and-providers.md`、`references/toolset/rea-6.7.0.md`。
