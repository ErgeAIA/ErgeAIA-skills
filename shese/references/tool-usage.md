---
trigger-when: "要在命令里填参数、拼 matrix spec、把 14 个 token 名对应到 --role 三档，或要让预览页渲满 14 个变量时"
name: tool-usage
description: "shese 计算层参数手册：九个（含 selftest）子命令的完整旗标、14 个 token 名与 --role 三档的对应、matrix spec 字段、预览页 14 个变量名与常用配方。"
---

# 参数手册（tool-usage）

SKILL.md 的「工具」表只给用途；本文件给参数、字段与配方。命令一律以 `python scripts/shese.py <子命令>` 调用，`--help` 与本节冲突时以脚本输出为准。

## 一、14 个 token 名 ↔ `--role` 三档

`--role` 只在**没给** `--size` + `--weight` 时兜底，用的是 SKILL.md 工具节列的角色默认下限；给了字号字重就走官方矩阵，`--role` 被忽略。

| token | 建议 role | 说明 |
| --- | --- | --- |
| `text` | body | 正文、长句、表格 |
| `textMuted` | aux | 次级文字、标签、时间戳 |
| `textDim` | hint | 占位、禁用、装饰，不得承载长句 |
| `accent` / `brand` | body | 作文字时按实际字号字重给 `--size`/`--weight`；没给就按 body 兜底 |
| `success` / `warning` / `danger` / `info` | body | 只有当其同时作文字用途时才进文字矩阵；作填充、图标时不套文字判据 |
| `bg` / `surface` / `elevated` / `card` / `border` | — | 承载面，只作 `--surface`；`border` 作可寻址控件边界时按 3:1（thresholds 1.5），作纯分界按 ΔE-OK（thresholds 2.1） |

上表是**建议**不是脚本默认：脚本不会按 token 名自动定档，`--role` 缺省一律 body，要按建议档判就显式给 `--role` 或在 spec 里逐 token 写 `role`。token 名是下游键，与 `--role` 三档是两个轴：名字决定它在界面里的位置，role 决定它在文字矩阵里按哪一档判。别名（`background`、`bg-surface`、`ok`、`muted` …）入参时自动归一到上表 14 个名字，输出始终是标准名。

## 二、子命令参数

| 子命令 | 完整签名 | 要点 |
| --- | --- | --- |
| `oklch` | `oklch HEX... [--to-hex "L C h"] [--json]` | 正向读 L / C / h 与 a / b；反向超色域时收 C 并标 `[超出 sRGB，色度收缩至 …]`，L 须在 0..1 |
| `contrast` | `contrast TEXT BG [--size N --weight W] [--role body｜aux｜hint] [--json]` | 两个位置参数都必须是不透明或可合成实色；`BG` 带 alpha 直接 exit 2；文字带 alpha 自动按 BG 合成后计算 |
| `composite` | `composite LAYER... --on BOTTOM [--json]` | 层**自顶向下**写（第一个最靠上），每层可写 `name=#rrggbbaa`；`--on` 必须不透明；合成后仍半透明即 exit 2，不给结论 |
| `matrix` | `matrix --tokens spec.json [--json]` 或 `matrix --text name=HEX --surface name=HEX ... [--size N --weight W] [--role …]` | spec 顶层可给 `role`/`size`/`weight`；`text` 条目可写成对象逐 token 覆盖；全局 `--size`/`--weight` 一视同仁，别用 |
| `delta` | `delta HEX... [--min-delta 0.10] [--json]` | 按传入顺序两两相邻，低于阈值即塌陷、exit 1 |
| `cvd` | `cvd HEX... [--min-delta 0.10] [--json]` | 三类模拟（protan / deutan / tritan）+ ΔE-OK；只管色觉塌陷，不判对比 |
| `mix` | `mix FIRST PCT SECOND [--space oklab｜srgb] [--json]` | `FIRST` 占 PCT%（0 < PCT < 100，开区间）；一端可写 `transparent` = 该色带 alpha；默认 oklab，srgb 只用于复算既有值 |
| `preview` | `preview --tokens name=HEX ... --out FILE [--template FILE] [--mode dark｜light] [--json]` | `--tokens` 可重复；`--mode` 只改页面 `data-mode` 标签；bg 与 mode 极性不符时 stderr 提醒、退出码不变 |
| `selftest` | `selftest [--json]` | 官方锚定向量；改脚本必跑 |

## 三、matrix spec 完整形状

```json
{"role": "body", "size": 16, "weight": 400,
 "text": {"text": {"hex": "#c9d1d9", "role": "body", "size": 16, "weight": 400},
          "textMuted": {"hex": "#8b949e", "role": "aux", "size": 13, "weight": 400}},
 "surface": {"bg": "#0d1117", "card": "#1c2128"}}
```

- `text` 条目写字符串等于只给色值，沿用顶层或命令行参数；写成对象才能逐 token 给 `role`/`size`/`weight`。
- `surface` 每条写色值字符串即可，也接受 `{"hex": "#…"}`（role/size/weight 对它不生效）；每个面都与每个 text token 配对，输出按 token 给最差面。
- 矩阵结论以最差面为准；某 token 最差面不达标即 exit 1。

## 四、预览页的 14 个变量

模板 `assets/scene-preview.html` 共 35 个自定义属性：14 个 token 变量 + 9 个 `--shell-*` 外壳变量 + 12 个字号 / 字体 / 圆角 / 间距变量。`preview` 的校验是「模板里有没有 `--name`」，所以只该注入下面 14 个 token（写模板没有的名字即 exit 2）：

`bg` `surface` `elevated` `card` `border` `text` `textMuted` `textDim` `accent` `brand` `success` `warning` `danger` `info`

- 值一律 `#rrggbb` 或 `#rrggbbaa`；alpha 值原样注入，页面按浏览器口径合成。
- 未传的变量保留模板默认值；要「渲满 14 变量」就逐个给，缺的角色用同族占位并标【占位·未判定】。
- `bg` 决定极性提醒：注入的 bg 在 OKLab 明度上属浅底而 `--mode dark`，会在 stderr 提醒但不改退出码。

## 五、常用配方

| 场景 | 命令 |
| --- | --- |
| 半透明文字落在卡片上 | `composite "#ffffffb3" --on "#1c2128"`，再把输出实色喂 `contrast` 或 `matrix` |
| 多层浮层链 | `composite "#ff7a3d33" "#00000026" --on "#161b22"`（自顶向下，最底层给 `--on`） |
| 整套矩阵 | 写 spec.json 后 `matrix --tokens spec.json --json`，逐 token 读最差面 |
| 派生 hover / 淡底 | `mix "#7a5cff" 14 "#1c2128" --space oklab`（禁 srgb 派生） |

## 六、退出码与禁止

退出码与故障处置见 `references/troubleshooting.md`。三条硬约束：不把 exit 1 当故障去改判定口径；不手算替代脚本输出；不凭记忆写矩阵数字。
