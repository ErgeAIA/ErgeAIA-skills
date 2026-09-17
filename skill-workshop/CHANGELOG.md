# 更新日志

skill-workshop 所有值得注意的变更都记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

> 早期（v1.21.0 之前）的详细变更历史见 `git` 提交记录；本文件仅保留近期若干版本的精简记录。

## [Unreleased]

## [1.25.0] - 2026-09-13

### 新增
- `reconcile` 子命令：抽取版本 / 数值阈值 / references 路径事实锚点，检出多值冲突与幽灵路径（C5 机检辅助，不替代语义裁决）
- `family-diff` 子命令：相对指定 baseline 或同父目录兄弟技能块集共识，检出结构块缺失（新增 F1 检查项）

### 变更
- 报告编号对齐：8 段报告自「一句话结论」至「总评」（`## 1`–`## 8`），消除 `## 9. 总评` 双轨
- description 增加 `another skill hands off a Skill project` 与应用类项目 Not for 边界
- CLI 子命令 18 → 20

### 修复
- checklist V4/V5 假阴性收紧：V4 须有测试集文件或正/负集描述且非否定句；V5 须「可机器判定」类措辞且具体机检信号（退出码 / validate·checklist PASS）

## [1.24.0] - 2026-09-12

### 变更
- 脚本柔性化 Phase 2：`validate` findings 化（标注 `rule_class`）、`script-profiles.yaml` 迁为代码消费、`review_ops` 系接入 `--profile`

## [1.23.1] - 2026-09-12

### 修复
- `routing-check` 通用化：去除 skill-workshop 9 个工作流文件硬编码清单，扁平 `references/` 布局技能不再误报

## [1.23.0] - 2026-09-11

### 新增
- 脚本柔性化 Phase 1：`_gate.py` 的 plan-gate / checkpoint / `--profile` / dry-run 默认
- `plan-gate-template.md` 五节计划模板

### 变更
- `init` / `package` / `generate-templates` 默认 dry-run（仅预览），`--write` 才实际落盘

## [1.22.0] - 2026-09-11

### 变更
- description 口径对齐：消除 6 处自相矛盾，校验器分级调整，官方源收敛（新增 `claude-platform-best-practices.md` 缓存）

[Unreleased]: https://github.com/ErgeAIA/ErgeAIA-skills/compare/v1.25.0...HEAD
[1.25.0]: https://github.com/ErgeAIA/ErgeAIA-skills/releases/tag/v1.25.0
[1.24.0]: https://github.com/ErgeAIA/ErgeAIA-skills/releases/tag/v1.24.0
[1.23.1]: https://github.com/ErgeAIA/ErgeAIA-skills/releases/tag/v1.23.1
[1.23.0]: https://github.com/ErgeAIA/ErgeAIA-skills/releases/tag/v1.23.0
[1.22.0]: https://github.com/ErgeAIA/ErgeAIA-skills/releases/tag/v1.22.0
