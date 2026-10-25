# .gitignore 维护参考

purpose: 新增或修正项目忽略规则，只追加不重写
sources:
  - gitignore(5) 官方语义（git-scm.com/docs/gitignore）
  - GitHub 官方 gitignore 模板（github/gitignore），按语言 / 框架组合取用
  - 项目实际的未跟踪文件与已追踪文件清单
hard-rules:
  - 只追加，不重写用户已有条目与顺序
  - 写入后必须做已追踪碰撞检查
  - 不自动 untrack 任何文件

## 0 语义判据（写规则前先过）

依据：`gitignore(5)` 官方文档（git-scm.com/docs/gitignore）。

| 判据 | 实际语义 | 常见误写 |
| --- | --- | --- |
| 已追踪不可忽略 | ignore 只作用于未跟踪文件；停止追踪须 `git rm --cached` | 以为加了规则就会自动移出仓库 |
| 否定不穿透父目录 | 父目录被整体排除时，`!` 对其中的文件无效；须先 `dir/*` 再 `!dir/file` | `dist/` + `!dist/app.js`（实测仍被忽略） |
| 末尾斜杠 | `dir/` 只匹配目录；`dir` 同时匹配文件与目录 | 用 `build/` 想排除同名文件，或用 `build` 误伤同名目录 |
| 前导斜杠 | `/x` 锚定本 `.gitignore` 所在目录；无斜杠则任意层级生效 | `node_modules` 与 `/node_modules` 混用 |
| 顺序 | 同一文件内**最后命中的规则**生效 | 把 `!` 例外写在忽略规则之前 |
| 双星 | `**/x` 任意层级；`a/**` 目录内全部；`a/**/b` 任意深度 | 用 `a/*/b` 以为能递归 |
| 大小写 | 受 `core.ignorecase` 影响（Windows / macOS 默认不敏感） | 以为 `Dist/` 与 `dist/` 一定不同 |
| 规则层级 | 命令行 > `.gitignore` > `.git/info/exclude` > 全局 `core.excludesFile` | 把个人 OS / IDE 偏好写进仓库 `.gitignore` |

## 0b 策略判据（该写哪些）

- 仓库 `.gitignore` 只收与项目本身有关、需要团队共享的规则；个人 OS / IDE 偏好进全局 excludes。
- 必忽略：依赖目录、构建产物、本地环境与密钥、工具产物（如 `.codegraph/`）。
- 必保留追踪：`.env.example` / `.env.sample`、lockfile（团队未明确不追踪时）、迁移脚本、示例资产。
- 不写宽泛通配：`*`、`*.json`、`*.md` 这类会误伤未来文件。
- 模板只作起点：按栈取 GitHub 官方模板，落盘前用 `git check-ignore -v` 逐条抽验。

## 1 前置判定

| 检查 | 处理 |
| --- | --- |
| 是否在 Git 仓库内（`git rev-parse --is-inside-work-tree`） | 否 → 不建文件，报告「无仓库」 |
| `git rev-parse --show-toplevel` 是否等于项目根 | 在父仓库内 → 用父仓库的 `.gitignore`，不建嵌套仓库 |
| 是否 monorepo | 是 → 子包各自 `.gitignore`；根只放跨包通用项（OS / IDE / 密钥） |

## 2 采集证据（只读）

| 证据 | 命令 / 来源 | 用途 |
| --- | --- | --- |
| 栈信号 | `package.json` / `pnpm-lock.yaml` / `pyproject.toml` / `uv.lock` / `Cargo.toml` / `go.mod` 等原文 | 选官方模板组合 |
| 未跟踪文件 | `git status --porcelain` | 发现该忽略却没忽略的路径 |
| 已追踪碰撞 | `git ls-files -ci --exclude-standard` | 现有规则已命中的已追踪文件 |
| 现有规则 | 读 `.gitignore` 全文 | 去重、保留顺序与 `!` 例外 |

## 3 选规则

- 按栈取 GitHub 官方模板，不凭记忆手写语言规则。
- 合并顺序：沿用用户已有条目 → 追加缺失条目 → 必要时用注释标注用途。
- 应覆盖：
  - 依赖与构建产物（按栈取，如 `node_modules/`、`dist/`、`build/`、`target/`、`__pycache__/`）
  - 本地环境与密钥（`.env`、`.env.*`、`*.pem`、`*.key`、凭据与连接串文件）
  - 工具产物（`.codegraph/`、`.impeccable/` 等按项目实际）
  - OS / 编辑器临时文件
- 必须保持可追踪（模板会误伤时加 `!` 例外；父目录被整体忽略时 `!` 不穿透，须用 `dir/*` + `!dir/file`）：
  - `.env.example` / `.env.sample`
  - lockfile（团队未明确不追踪时）
  - 迁移脚本、示例数据、示例资产

## 4 写入纪律

1. 写前声明：将追加 N 条、跳过 M 条已存在条目、是否新增 `!` 例外。
2. 只追加，不排序、不删除、不改写既有行。
3. 目标文件不存在 → 新建；存在 → 追加。

## 5 碰撞检查（必做）

写入后：

1. 跑 `git ls-files -ci --exclude-standard`。
2. 结果为空 → 通过。
3. 非空 → 逐条列出路径交用户裁决：
   - 保留追踪 → 加 `!<path>` 例外；**父目录整体被忽略时 `!` 无法穿透**（如 `dist/` 之后写 `!dist/app.js` 仍被忽略），须改为 `dist/*` + `!dist/app.js`
   - 停止追踪 → 需用户显式确认后执行 `git rm --cached <path>`（历史仍保留）
4. **禁止自动 untrack**；发现已被追踪的密钥文件只报告并建议轮换凭据，不改写历史。

## 6 验收

| 检查 | 判据 |
| --- | --- |
| 碰撞 | `git ls-files -ci --exclude-standard` 为空 |
| 规则生效 | `git check-ignore -v <path>` 能指出来源行 |
| 状态干净 | `git status --porcelain` 不再出现应忽略的路径 |
| 幂等 | 同一栈二次执行 0 条新增 |

## 7 失败处理

| 触发条件 | 一线修复 | 仍失败兜底 |
| --- | --- | --- |
| 不是 Git 仓库 | 不建文件，报告「无仓库」 | 用户要求先建 → 转 `git init` 流程 |
| 栈无法判定 | 只加通用项（OS / IDE / 密钥），报告「栈未识别」 | 用户提供栈 → 再补 |
| 已有规则与模板冲突 | 保留用户规则，只追加不冲突项，报告冲突项 | 用户要求替换 → 显式确认后按用户指定改 |
| 碰撞检查命中已追踪文件 | 逐条报告，等裁决 | 用户要求全部 untrack → 显式确认后逐条执行 |
| 文件不可写 | 报告路径与权限 | 提示用户手动创建 |
