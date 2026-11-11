# shese 版本历史

shese 所有值得注意的变更都记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。分类标题按 Keep a Changelog 六类（新增 / 变更 / 弃用 / 移除 / 修复 / 安全），只记录影响外部行为的变更。

## [Unreleased]

### 变更

（暂无）

### 移除

- 仓库内的历史预览产物（`preview-001.html`、`preview-002.html`、`preview-001-002-audit-compare.html`，约 86KB 生成副本）与本地测试草稿目录 `local-tests/` 一并清理；预览页改由 `preview` 子命令按需现生成。`audit-001-002` 内指向这些 html 的三处说明同步改写，不再留悬空指针；`theme-001.json` / `theme-002.json`（14 token 实测产物）保留作证据。

## [1.2.1] - 2026-11-11 · 门面两段式与入参收口

### 变更

- 色值入参不再只收十六进制：`rgb()` / `rgba()` / `hsl()` / `hsla()` 均可直接传入（逗号或空格分隔、alpha 作第 4 参数或 `/` 后、通道可用百分比），所有收色值的子命令与 `--tokens name=…`、spec 的 `hex` 字段共用同一解析器。通道越界报 exit 2 而不按 CSS 静默夹取；命名色与 `lab()`、`oklch()` 等其它函数式写法仍拒收。
- 边界表述收紧：明确「不生成无角色的 50–950 整条色阶」（有角色与承载面的阶梯用 `mix --space oklab` 逐档推、逐档判），明确「不在 Display P3 下判定」（先转 sRGB 再判并声明偏差），补在 `README.md` 与 `references/generate.md`；`references/tool-usage.md` 增入参写法表。
- 单测 89 → 93 项：新增 rgb/hsl 与 hex 等价、alpha 三种写法一致、越界报错、未知函数拒收四类用例。
- 门面 description 改为两段式（按 skill-workshop v2.8 现行规范）：`[审查一套配色在指定场景下的可读性，给出最小改动值与预览页、主题包；也能按名称与故事生成配色] + Use when [用户何时会想到它]`。边界句「不适用于物理可视化色阶…」按规范从 description 移除，改由正文 `## Non-Goals` 的 `Not for（何时不接）` 承载；description 补入真实用户话术（读着累、看着刺眼、色阶塌了、改暗、改亮）与英文触发（palette、contrast、theme），删掉实现细节（入参写法、子命令名）。同步清理 SKILL.md 三处重复指针与元叙述（机制点名句、命令旗标重复句、`references/` 罗列句），正文 20825B → 20617B。
- `TestSkillFacade` 改为机检两段式门面：description 必须含 `Use when`、不得出现「不适用于 / Not for」、覆盖故障词与英文触发与命名轨、长度 ≤500 字符；另加一例机检边界确在正文 Non-Goals 节。单测 95 → 96。

## [1.2.0] - 2026-11-11 · 命名轨与可复算出口

### 新增

- 命名轨：先给名称与故事时，按 `references/story.md` 落故事卡（底色明度区间、彩度上限、色相窗、基本色相数、对比上限、色觉间隔），再走生成轨；名称只是入口，判据仍是机制。SKILL.md 增加轨道入口、输入第 6 项、步骤 3 回读与交付项「命名主题包」。
- `solve`：保色相在 L 轴二分到刚达标，输出原值 / 新值 / ΔL / ΔE-OK / 色相漂移 / 彩度收缩 / 端点风险；仅端点可解判失败，不再靠人反复试。
- `story`：按故事卡逐项验收一套 token，逐项给目标与实测，含正文档 APCA、对比软上限、逐角色彩度上限、色相窗、基本色相数、语义色三类色觉最小间隔。
- `export`：命名主题导出 JSON / CSS vars / Tailwind `@theme`，名称与故事一并写入。
- `matrix` 端点守卫：纯黑大底、深色纯白正文、浅色纯黑正文，命中即 exit 1；此前只在文字规则里、靠人眼。
- `assets/story-cards/`：夜灯、晨光两张故事卡与对应 token 示例，可原样跑 `story`。
- `test-prompts.json` 增 3 组命名轨用例（含「只给名字不给故事」的反向用例），合计 20 组；单测 89 项。
- `references/evidence.md`：实现核验记录——字号-字重矩阵 250 格与官方 `fontMatrixAscend` 逐格相同、反查 183 格无过严、942 对不透明组合与官方 `apca-w3` 的 Lc 零差异、8 条官方测试向量与 1 条 alpha 向量命中、`solve`/`story`/`export` 确定性口径；并单列「真实色板召回与误报未测」。新增 `TestDeterminism` 把「同输入两次输出逐字节相同」变成机检。

### 变更

- 故障处置十二类（高频五类 + 其余七类）统一收进 `references/troubleshooting.md`，SKILL.md 只留四类分诊；正文由 21037B 压回 20836B，重新守进 20849B 上限。
- README 预览页描述改为实际能力：色板 + 三级文字 + 深浅双模式 + 三档字号 + 三色觉模拟 + 角色说明表，**不给判定结论**；命令速查补 `solve` / `story` / `export`，场景表补命名轨示例。
- `references/tool-usage.md` 补三个子命令签名、故事卡字段与四条配方。

### 修复

- 预览页页脚把 Python 函数名 `apca_required_lc` 当成 CLI 子命令，用户照做必报错；改为可执行的 `contrast "#TEXT" "#BG" --size N --weight W`，并加单测防止回退。
- CHANGELOG 1.1.2 条目称「守在 20849B 内」，实测 21037B；本轮实测 20836B。

## [1.1.2] - 2026-10-22 · 门面触发与边界声明补全

### 变更

- description 触发句补三类输入：故障式表述（主题改暗、主题改亮、色阶塌了、对比不够、看着刺眼）、英文提问（palette、contrast），并声明不适用范围（数据可视化色阶、插画摄影印刷配色、整套设计系统）——此前门面只认「做配色」正向请求，用户带着症状来时要靠正文兜底。
- 判定链共用句（三条轨道共用一条判定链）由定位节并入「执行步骤」开头；删两处重复的命令细注（`--mode light` 只改标签、`cvd` 只管色觉塌陷）与一处重复的 PowerShell 引号说明，正文守在自设上限 20849B 内。

### 新增

- `test-prompts.json` 增 2 组：故障表述入口（整体改暗后色阶塌陷）、英文入口（13px 正文可读性）。合计 17 组。
- 单测扩至 74 项：断言 description 覆盖故障式触发词、英文触发词与边界声明，防止门面回退。

### 修复

- 用例组数口径校正：1.1.1 记「16 组」，实际文件为 15 条；本轮补 2 条后按实测记 17 组。

## [1.1.1] - 2026-10-22 · 判定链补强：意境判读、轨道确认点与对照页交付

### 新增

- 判定链新增「意境词→可测目标」环节（SKILL.md 步骤 3）：夜间类＝照度受限（主文 ≤15:1、面层差收敛），晨光类＝亮色须留可书写通路；译出的目标回读验收。
- 审查交付新增「现版 vs 优化版」双栏对照页（步骤 8 + CHECKPOINT 4）；写法与实战正反例落 `references/audit-report.md`（#001 夜灯＝暗底照度受限律，#002 晨光＝#FF6A2B 补 #8C3A12 深橙通路）。
- `references/troubleshooting.md`：审查轨失败分诊（面层 ΔE 过小、语义色塌陷、矩阵连不过等的降级与处置口径）。
- `references/tool-usage.md`：七个子命令的矩阵/字重/混合口径速查。
- CHECKPOINT 5「轨道入口先确认」：生成轨意图卡与取源轨 token 对齐表须用户确认后再走判定链；用户不回按默认档并标【假设】。
- SKILL.md 步骤 4 补无 alpha 分支、步骤 7 补失败出口（改完重跑 4–6 确认无回归）。
- 单测扩至 71 项；`test-prompts.json` 重排为 16 组验收用例。

### 变更

- 四道 CHECKPOINT 逐一对齐到守护步骤的出口（步骤 1/6/8 挂 CP 锚点），步骤表与闸门不再脱钩。
- 分诊补「一次 ≤3 问」；`generate.md` 候选逐套判定、仅第 8 步汇总对照。
- 参考文件版本随发布对齐 1.1.1（audit-report / theme-source）。


## [1.1.0] - 2026-10-20 · 预览页套品牌外观 + 主题仓库取色规则

### 新增

- `references/theme-source.md`：主题仓库取色的三步路径（读仓库 `README.md` → 现读 `INDEX.json` 定位 → 读 `palette.md` 全表）、只读纪律、token 名对齐规则与外壳色 pin 规则。SKILL.md 的输入节与 References 同步挂上指针。
- `preview` 增加注入后的极性自检：注入的 `bg` 与页面 `data-mode` 不同极时在 stderr 提醒。
- 单测新增 4 项：模板品牌 pin 与不带引号选择器写法、外壳色不被注入覆盖、极性不符告警、极性一致静默。

### 变更

- `assets/scene-preview.html` 外壳套上品牌外观：新增两组非注入的外壳变量（`--shell-*`），暗色 pin ThemeVault #001 `themes/erge/dark`「夜灯」、亮色 pin #002 `themes/erge/light`「晨光」。被审的仍是注入进去的 14 个 token，场景面板与色板条一律用候选色。
- `preview` 的 JSON 输出增加 `polarity` 字段（bg / detected / declared / match）。
- `SKILL.md` 版本 1.0.0 → 1.1.0；根 `README.md` 与 `README.en.md` 索引版本同步。
- 技能 `README.md` 按开源门面重写：补齐安装命令、前置条件、两条可复制的起步命令与实测输出、命令速查表、目录结构、测试与自检节。

### 修复

- 修正 `CHANGELOG.md` 中 v1.1.0 区块误收 v1.0.0 条目、v1.0.0 区块缺失的问题，按版本重新归档。

> 极性自检只提醒不改退出码：退出码仍由注入是否成功决定（0 = 成功 / 2 = 输入或环境错误）。编号重排后的取色纪律与外部仓库只读边界的裁决见 Skills-Depot `docs/.ai/decision-log.md` 的 DEC-052。

## [1.0.0] - 2026-10-20 · 首次发布

### 新增

- 初始版本：设色技能。审查既有配色与从意图生成新配色两条轨道，共用一条判定链——阅读目标先行 → 语义角色还原 → alpha 沿链合成 → 按感知机制逐项判定（硬底线 / 参考锚点 / 目标推导三级标注）→ 最小改动优化。
- 默认交付快档四件：结论、决策摘要、场景预览页（色值填色副本）、token JSON；完整报告降为深档，规范落 `references/audit-report.md`。
- 计算层 `scripts/shese.py`（零第三方依赖）七个子命令：`oklch` / `contrast` / `composite` / `matrix` / `cvd` / `preview` / `selftest`；判定口径取自 APCA 官方字号—字重矩阵，`selftest` 内置 24 项官方数值锚定。
- `references/` 五份：`mechanisms.md`（14 条感知机制）、`scenes.md`（四条场景画像）、`thresholds.md`（数字唯一真相源）、`generate.md`（生成轨意图卡）、`audit-report.md`（深档十二节）。
- 明确的边界：不做数据可视化色阶（顺序 / 发散 / 分类）；不替换品牌色相；与 banxin、ThemeVault 无代码依赖，计算层按公开标准独立实现。

> 定名、轨道与范围裁决见 Skills-Depot `docs/.ai/decision-log.md` 的 DEC-049 与 DEC-050；判定口径裁决见 DEC-051。
