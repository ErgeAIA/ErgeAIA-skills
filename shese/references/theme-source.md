---
name: "theme-source 主题仓库取色规则"
description: "收到外部主题仓库（当前为 ThemeVault）或其编号 / 主题名时的取色路径与只读纪律，以及预览页模板外壳色的来源与改法。"
version: 1.1.0
trigger-when: 用户报主题仓库路径、主题编号（如 #002）或主题名，或要求预览页用上品牌色时
reads-from: 主题仓库根目录的 README.md、INDEX.json 与各主题的 palette.md；assets/scene-preview.html
writes-to: 无（只规定读法与纪律，不改主题仓库）
---

# 主题仓库取色规则

主题仓库是**外部只读资产**，不是本技能的依赖：技能自带计算层与模板，不 import 它、不复制它的脚本。它只在一个地方进来——用户要把某套已归档的配色拿来审、拿来当参考锚点，或者要求预览页套上品牌外观。

## 1 取色三步（每次现读，不许凭记忆）

1. 读主题仓库根目录的 `README.md`（当前：`D:\Workspace\Code\ThemeVault`）。它规定了索引结构、目录约定与「给 AI 读者的快速路径」，是该仓库唯一的读法权威；本文件不复述它的内部细节。
2. 查 `INDEX.json`：按 `families[].themes[].number` 或 `displayName` 定位主题条目，取出 `palettePath` 与 `tokensPath`。
3. 读 `palettePath`（通常是 `themes/<family>/<id>/palette.md`）的**全表**。色值以该文件的原文为准。

取回后把 palette 与 14 个标准 token 的对齐表回给用户确认（SKILL.md CHECKPOINT 5），过闸再进判定链；主题名或用途有歧义时同 CP1 追问；用户不回就按名字最接近的对齐进判定链并标【假设】。

**编号会变。** 仓库主人重排编号后，旧编号会指向别的主题（曾发生：#046 由 wave 变为 dragon）。任何一次作业都必须现读 `INDEX.json`，禁止把编号与主题的对应关系写进结论或凭记忆复用。本文件里出现的编号只作示例，使用前复核。

## 2 只读纪律

- 不改主题仓库的任何文件，不跑它 `scripts/` 下的脚本；`INDEX.json` 由它的生成脚本产出，勿手改。
- 色值原文照用：不改写、不「统一优化」、不强行转成十六进制；背景与文字成对取用，不要跨主题拼。
- 该仓库自报的 `textContrast` / `brand` 只当参考记录；**判定一律用本技能自己的计算层复算**（`scripts/shese.py`），因为它只给数字不给场景与机制。
- 本技能的结论与产物写回用户的项目或技能产物目录，不写回主题仓库。

## 3 token 名对齐

主题仓库的角色名与本技能的 14 个标准 token 不完全同名，靠 `scripts/shese.py` 的 `TOKEN_ALIASES` 归一（`bg-base` → `bg`、`bg-surface` → `surface`、`text-muted` → `textMuted`、`ok` / `ok-fill` → `success`、`warn` → `warning`、`error` → `danger` 等）。未登记的细化名（`bg-hover`、`accent-foreground`、`syntax-*` 等）会被拒绝并报合法名清单——这是有意的：本技能只审 14 个语义位，细化 token 由用户在自己的项目里派生。

## 4 预览页外壳色（品牌外观）

`assets/scene-preview.html` 的**外壳**（页面底、面板、标题、说明文字、按钮、分隔线）固定用品牌主题色，写在模板里两组非注入变量上：

- `:root[data-mode=dark]` 的 `--shell-bg` / `--shell-surface` / `--shell-elevated` / `--shell-border` / `--shell-text` / `--shell-muted` / `--shell-dim` / `--shell-accent` / `--shell-accent-fg`
- `:root[data-mode=light]` 同名另一组

当前 pin 值来源：**#001 `themes/erge/dark`「夜灯」（暗色）与 #002 `themes/erge/light`「晨光」（亮色）**。改品牌外观的路径只有一条：回主题仓库按上节取数，再改模板里这两组变量，同时同步 `scripts/test_shese.py` 的 `test_real_template_pins_brand_shell` 断言。

两条硬约束：

- 选择器必须写成**不带引号**的 `[data-mode=dark]`。注入脚本对 `data-mode="…"` 只替换第一处（`count=1`），带引号的选择器有被误伤的风险。
- 外壳变量名一律加 `--shell-` 前缀。注入脚本按 `--<token>\s*:\s*([^;]+);` 找**首个**匹配，前缀保证 14 个被审 token 永远不会命中外壳块。

**被审查的永远是注入进去的 14 个 token，不是外壳。** 外壳只负责让预览页看起来像用户自己的产品；场景面板（代码编辑器 / 网页长文 / 移动端卡片流）与色板条一律使用注入的候选色。

## 5 不确定性

- 主题仓库的结构由它自己的 README 定义，可能随版本变化；本文件只承诺「先读它的 README 再动手」这一条路径，不承诺字段名长期不变。
- 模板外壳色 pin 的是本次取到的 #001 / #002 快照。仓库主人重排编号或改色后，需要按第 4 节重新同步，本文件不会自动跟随。
