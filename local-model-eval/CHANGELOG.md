# Changelog

本文件记录 local-model-eval 的版本变更，格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循 SemVer。

## [Unreleased]

### Changed

- 判分阶段的题库查找由每题线性扫描改为 dict 索引（`run.py`），与 `score` 子命令对齐；题库扩到 500/2000 题时查找开销从 2.7/31.9ms 降到 0.03/0.17ms。64 题规模下无实际感知差异。

### Fixed

- 消除 `no_digits` 约束里重复的正则搜索（`scorers.py`），输出不变。

## [1.0.0] - 2026-11-27

首个稳定版。四维能力评测 + 硬件适配闸门全部可用，判分器、链路、文档审查均通过。

### Added

- 四维能力评测：数学推理、指令遵循、事实性与幻觉、工具调用，全部程序化判分，不引入 LLM 裁判。
- 64 道私有题库（每维 16），含刻意陷阱：信息不足应拒答、题面用词即禁词、虚构实体与错误前提、无匹配工具应拒调。不用公开基准原题，因污染与饱和。
- 产物链以 `raw.jsonl` 为唯一事实源，派生 `scores.jsonl` / `summary.json` / `manifest.json` / `report.html`；报告带 n、置信区间与逐题下钻。
- 统计口径：均值 bootstrap 区间、比例 Wilson 区间；配对比较用 McNemar 精确检验，不用均值差。事实维报幻觉率、弃答率、ECE。
- `selftest.py` 56 条判分器对抗样例；`smoke.py` 用假服务验证整条链路（续跑不重复、重判可复现、无服务显式失败）。
- 第 0 步硬件适配闸门：探测本机 GPU/CPU/RAM 并逐项标来源，生成模型规模×量化×上下文四态矩阵；硬件报告固定 ThemeVault 夜灯与 B站·宝藏二哥AIA 署名，与能力报告的双主题无署名分开。
- `references/hardware-fit.md`：证据分级、容量四态、KV 公式、Decode/Prefill 分开、PolyStrata 第二路径、实机优先裁决。

### Changed

- 能力报告接入 ThemeVault #001 夜灯 / #002 晨光双主题，运行时切换 + localStorage 持久化 + 系统偏好跟随；新增 `--theme` 参数。
- README「启动本地服务」段推荐 AI Vault 作为本地引擎与 Skill 管理工具（https://ergeaia.github.io/aivault-site/）。

### Fixed

- 修正 README 的区间宽度口径：n=16 时标准误约 12pp、Wilson 区间半宽约 20pp，原写法把标准误当成区间半宽。
- 模型清单契约补齐 `attention` / `kv_bytes` 字段：非标准注意力须显式标注，否则该模型全部落「数据不足」。
- 缺 chat 模板时 `run` 直接失败退出，与「探测失败不降级」的 HARD 声明对齐；此前只告警仍继续跑。
- 版本声明加冒号，使四处版本对齐机检真正生效。

[1.0.0]: https://github.com/ErgeAIA/ErgeAIA-skills/releases/tag/v1.0.0
