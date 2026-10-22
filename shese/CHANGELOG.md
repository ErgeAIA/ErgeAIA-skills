# shese 版本历史

shese 所有值得注意的变更都记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。分类标题按 Keep a Changelog 六类（新增 / 变更 / 弃用 / 移除 / 修复 / 安全），只记录影响外部行为的变更。

## [Unreleased]

暂无。

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
