---
name: skill-failure-modes
description: skill-workshop 路由/评估/重构的失败模式与兜底处理（从 SKILL.md 主路由层下沉，按需加载）
version: 1.0.0
trigger-when: 路由/评估/重构遇到失败症状需查兜底处理时（按需加载，不在主路由层常驻）
---

# 失败模式编码（if-then 三段式）

> 本文件从 SKILL.md §3 下沉而来。路由/评估/重构过程中遇到以下症状，按"一线修复 → 仍失败兜底"两段处理。所有失败最终都收敛到 W0-clarify 重新路由。

| 症状 | 一线修复 | 仍失败兜底 |
|------|----------|------------|
| 决策矩阵无明确命中（模糊请求如"我有个 skill 问题"） | 默认路由 W0-clarify 询问深度 | 引导到 weighted-scoring 快速通道 |
| 路径冲突（同时命中"创建"和"评审"） | 按优先级：创建 > 重构 > 评测；后到的进 backlog | 🔴 CHECKPOINT 询问用户 |
| 命中 C1-create 但 skill 目录已存在 | 切到 C3-refactor | 询问"覆盖/重命名/合并" |
| 命中 V0-validate 但脚本报错 | 检查 `skill_path.resolve().name` 误判（Gotchas #8） | 手动跑 `quick_validate.py` 替代 |
| W7 判定 T1-T5 时无 rubric 支撑 | 引用 [intent-calibration.md](rubrics/intent-calibration.md) 标尺 | 委托独立 judge agent |
| results.tsv 损坏/列数不匹配 | 备份 `.bak.YYYYMMDD-HHMM` 后重建 | 询问用户是否继续 |
| subagent 不可用 | dim8 降级 dry_run，results.tsv 标注 `eval_mode=dry_run` | 提示用户需要 full_test 环境 |
| 优化后体积 > 原 × 1.5 | 强制精简（删冗余/合并重复） | 询问用户是否接受扩展 |
| test-prompts.json 已存在 | 复用并展示，问"复用/重写/追加" | 默认复用 |
| SKILL.md 找不到 | 该 skill 终止，results.tsv 记 `status=error` | 继续下一个 |

**P-V-H 关键决策点**：
- **🔴 CHECKPOINT**：所有"询问用户"路径都是 P-V-H 强制守关
- **🛑 STOP**：失败兜底收敛到 W0-clarify，禁止越权处理
