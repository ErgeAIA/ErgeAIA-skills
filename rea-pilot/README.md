# rea-pilot

<p align="center">
  <img src="assets/banner.svg" alt="rea-pilot" width="100%">
</p>

> REA 的引航员：把 REA 装进你当前的编程助手、验证真的连上，再按目标给你选路、排障、回滚与加固建议——不替你开船。

## 它解决什么问题

REA（<https://rea.tools/>）是一个跑在本地、把逆向证据喂给助手的工具。它的官方技能教「连上之后怎么调查」，但真装过的人会卡在前面的三件事：

1. **装不上或接不上**：Node 版本、PowerShell 拦 `npx`、宿主配置格式、注册写在哪、要不要重启，全靠猜。
2. **不知道装好没有**：`rea mcp doctor` 绿了不等于你的会话里已经有工具。
3. **装完不会用**：手上一堆工具（207 个 MCP 工具 / 153 条命令），不知道面对一个具体目标该走哪条最小路径；也不知道自己写的东西该怎么加固。

rea-pilot 把这三件事变成流程：**先体检、再出计划、人确认、再执行、最后三问验证**；选路与加固都落到具体命令与判据上。

## 触发词

| 场景 | 你说的话 |
| --- | --- |
| 安装与接入 | 帮我装一下 REA / 把 REA 接到我的 Cursor（或 Claude Code / DSH / Codex…） |
| 环境体检 | REA 装好了吗 / 帮我看看 REA 的环境有没有问题 |
| 宿主不在列表 | 我的助手 setup 认不出来，怎么手动接 MCP |
| 选路 | 我有一个 exe（或 asar / apk / 网站），想逆向，该怎么下手 |
| 加固建议 | 我该怎么做加密和加壳，才能防住这种逆向 |
| 更新 | REA 升级了，工具清单对不上 |
| 卸载回滚 | 把 REA 卸掉 / 装坏了想还原 |

## 怎么用

| 能力 | 一句话方法 | 示例提示词 |
| --- | --- | --- |
| 安装与接入 | 先跑 `rea doctor` 体检，再把 `rea setup --dry-run` 的计划翻译成人话给你确认，确认后才执行 | `帮我在这台机器上装 REA，先给我看它准备改哪些文件` |
| 连接验证 | 三问分开答：`rea mcp doctor` / 注册 `state=aligned` / 重启后工具真出现 | `REA 装了吗？我怎么确认它真的连上了我的助手` |
| 宿主手动接入 | 让你的助手自己去探索自己的 MCP 配置位置和格式，只给通用字段 | `我的助手不在 REA 支持列表里，你教我怎么手动加 MCP 服务器` |
| 目标选路 | 先说目标类型，再说要哪类证据，最后给 3–5 条最小路径命令 | `我有一个 Electron 应用（app.asar），想搞清它的剪贴板行为，该怎么查` |
| 逆向反推防护 | 先讲通用方法论，再落到你的项目：每条建议都给代价和 REA 复跑验收判据 | `看完我的 Android 应用能拿到什么，我该怎么加密和加壳` |
| 版本同步 | 读官方 CHANGELOG → 重新生成工具表 → 四处版本对齐 | `REA 更新了，把工具清单刷新一下` |
| 卸载回滚 | 先取证会动哪些文件，再 `rea uninstall`，必要时用备份路径还原 | `把 REA 卸干净，别动我的其他 MCP 配置` |

## 设计取舍

| 取舍 | 选择 | 为什么 |
| --- | --- | --- |
| 与官方自带技能的关系 | 互补窄定位，不重写调查方法 | 自带技能已经覆盖「怎么用 REA 取证据」，重写只会互相打架；本技能只占它前面和外面 |
| 工具清单 | 生成带版本号的 `references/toolset/rea-<版本>.md`，不手写进 SKILL.md | 官方近 30 天发 13 个版本，手抄清单约 2 天过期一次 |
| 宿主配置 | 只给通用字段 + 探索提示词，由宿主自己插入自己的配置 | 各宿主配置格式不同（JSON / JSONC / TOML），替它猜路径最容易写坏别人的配置 |
| 「装好了」的判据 | 三问分开答，缺一不算 | `mcp doctor` 绿只证明 server 能启动，不证明你的会话里已经有工具 |
| 加固建议 | 逆向反推防护（REA 能拿到什么 → 你该补什么），并要求用 REA 复跑验收 | 通用扫描器式建议没有验收闭环；反过来用攻击面清单才可验证 |

## 与相邻技能的边界

| 相邻 | 边界 |
| --- | --- |
| REA 自带技能 `reverse-engineer-anything` | 它管「连上之后怎么调查」；本技能管「怎么连上、连上没有、该查什么、怎么加固、怎么退回」 |
| 通用逆向/安全技能 | 本技能只做 REA 的接入与选路，不替代漏洞扫描、代码审计 |
| 项目协作类技能（vibe-*） | 本技能不写项目契约、不碰进度与交接 |

## 目录结构

```text
rea-pilot/
├── SKILL.md                        # 路由与硬边界（细节在 references）
├── README.md                       # 本文件：人读门面
├── CHANGELOG.md
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

## 安装

```bash
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill rea-pilot
```

## 版本

当前版本：**v1.0.0**，详见 [CHANGELOG.md](CHANGELOG.md)。
