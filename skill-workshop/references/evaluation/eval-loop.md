---
trigger-when: "运行评测迭代循环时"
name: eval-loop
description: 本技能评测闭环工作流参考。当你需要对目标 Skill 做盲测对比、解盲复盘、汇总回放与迭代优化时使用此参考。
version: 1.8.0
---

# 评测闭环工作流参考（本技能）

> **一句话**: 这是一份面向评测闭环的专项 workflow 参考，说明怎么评、怎么复盘、怎么回放、怎么继续迭代
> **版本**: v1.8.0
> **用途**: 指导评测闭环与迭代优化
> **适用范围**: 本技能的评测工具链

## 1. 文档定位

### @步骤1: 先明确这份文档负责什么

本文档负责的是“评测闭环怎么跑”，不是“本 Skill 的整体业务流程说明”。

### 它主要负责什么

- 说明评测闭环的推荐顺序
- 说明各个评测相关子命令怎么用
- 说明评测产物和回放产物该怎么看
- 指导你从单次评测进入多轮迭代

### 它不负责什么

- 不解释本 Skill 的整体工作流关系
- 不替代创建流程或重构流程
- 不定义目标 Skill 的业务边界

@提示: 若你要修改版本规则或发布要求，请读 [versioning-and-validation.md](../authoring/versioning-and-validation.md)。

## 2. 关键概念

### @步骤2: 统一评测闭环里的术语

- **目标 Skill**：你正在创建、修改或评测的那个 Skill
- **评测闭环**：评测 -> 复盘 -> 汇总 -> 回放 -> 迭代 -> 再评测
- **评测产物目录**：一次 `run_eval` / `run_loop` 运行产生的输出目录，包含对比结果、转录本、报告等

## 3. 评测闭环总览

### @步骤3: 先理解整条评测主链

<!-- @验证方式: 能复述“评测 -> 复盘 -> 汇总 -> 回放 -> 迭代 -> 再评测”的主链 -->

从业务角度看，一次典型的评测闭环通常这样流转：

1. 先确保目标 Skill 至少通过基础校验
2. 跑单次评测，确认触发率和效果
3. 对结果做回放和人工复盘
4. 若做了多轮实验，再做 benchmark 汇总
5. 根据问题修改 `description`、`references/` 或脚本
6. 重新进入下一轮评测

一句话理解这条链：

`验证基础结构 -> 跑评测 -> 看回放 -> 汇总结果 -> 修改 Skill -> 再评测`

## 4. 评测闭环工作流

## @工作流: 运行 Skill 评测闭环

### @步骤4: 先跑单次评测

单次评测用于判断：目标 Skill 当前的触发边界和效果大致如何。

```bash
python scripts/skill_cli.py eval --eval-set <eval.json> --skill-path <skill-dir> --verbose
```

- @动作: 先确认目标 Skill 已通过 `python scripts/skill_cli.py validate <skill-dir>`
- @动作: 若目标 Skill 提供 `scripts/validate_skill.py`，先补跑工程硬校验
- @动作: 若 `eval` 启动即失败，先检查 `eval-set` 是否满足 `query` 唯一且 `should_trigger` 为布尔值

### @步骤5: 回放并人工复盘

回放和人工复盘负责回答：这次评测“为什么好 / 为什么坏”。

```bash
python scripts/skill_cli.py review <workspace-path> --static <report.html>
```

@提示: `assets/eval_review.html` 是 `review` 子命令使用的运行时模板。

### @步骤6: 多轮结果做 benchmark 汇总

当你已经积累了多轮 run，需要比较趋势而不是只看单次结果时，再跑 benchmark。

```bash
python scripts/skill_cli.py benchmark <benchmark-dir> --skill-name <name> --skill-path <skill-dir>
```

### @步骤7: 自动或手动进入下一轮迭代

当你已经知道哪里有问题，可以进入下一轮迭代。

自动闭环：

```bash
python scripts/skill_cli.py loop --eval-set <eval.json> --skill-path <skill-dir> --model <model> --verbose
```

手动闭环：

1. 先修改 `description`、`references/`、`scripts/` 或 `SKILL.md`
2. 再重新运行 `validate`
3. 再进入下一轮 `eval`

### @步骤8: 需要编辑 eval-set 时再打开编辑器

```bash
python scripts/skill_cli.py editor
python scripts/skill_cli.py editor --input <eval.json>
python scripts/skill_cli.py editor --input <eval.json> --static <eval_set_editor.html> --no-open
```

@提示: `assets/eval_set_editor.html` 是 `editor` 子命令可直接预览、导出或通过 `--input` 预加载数据的独立 eval JSON 编辑工具页。

## 5. 常见用法组合

### @步骤9: 记住最常见的执行组合

最常见的执行组合通常是：

1. 先跑 `validate`
2. 再跑一次 `eval`
3. 再用 `review` 做人工回看
4. 若要继续优化，改用 `loop` 或手动修改后再 `eval`
5. 若已经积累多轮，再跑 `benchmark`

## 6. 产物与文件

### @步骤10: 知道评测闭环里该关注哪些产物

评测闭环里最值得关注的部分：

- `agents/`：评测时用到的提示词（对比 / 复盘 / 断言打分）
- `scripts/`：评测与迭代脚本
- `assets/eval_review.html`：评测回放页模板
- `assets/eval_set_editor.html`：离线编辑 eval JSON 的工具页

---

## 版本历史

- **v1.8.0** (2026-05-13) - 重写为 workflow 化的评测闭环参考，补充“做什么 / 不做什么”、主流程步骤与阅读入口
- **v1.7.0** (2026-03-09) - editor 子命令新增 --input，支持预加载标准 eval.json 或编辑器格式 JSON
- **v1.6.0** (2026-03-09) - 新增 editor 子命令，支持直接打开或导出 eval JSON 编辑页
- **v1.5.0** (2026-03-09) - 补充 assets 中两个 HTML 的职责边界：回放模板 vs eval JSON 编辑页
- **v1.4.0** (2026-03-08) - 删除 eval-viewer 目录，回放模板统一收敛到 assets/eval_review.html
