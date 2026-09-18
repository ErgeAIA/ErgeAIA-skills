---
name: plan-gate-template
description: "plan-gate 五节计划模板：调用 eval/loop/improve 等高成本命令或写文件命令前，AI 必须先向用户出示本计划。"
version: 2026-09
source: skill-workshop（目标驱动脚本协议，scripts/_impl/_gate.py 消费）
trigger-when: 调用 eval/loop/improve 及写文件类命令（init/package/generate-templates/selfheal apply）前
role: template
---

# Plan-Gate 计划模板

> **使用约定**：
> 1. AI 调用 gate 类命令前，先复制本模板填写五节，**给用户过目**，用户认可后带 `--plan <file>` 执行。
> 2. 人类直接调用 CLI 可用 `--plan-text '<一句话>'` 快速通道；**AI 禁用该通道**（SKILL.md §2 硬规则）。
> 3. 脚本校验五节标题存在性；缺节会输出 `decision_required`（不是报错，是等决策）。

## 模板（复制后填写）

```markdown
# Plan-Gate：<命令> <目标对象>

## 目标
<一句话：要达成什么结果，而非要跑什么命令>

## 范围与边界
<动什么 / 绝不动什么（列出不碰的文件与目录）>

## 参数
<命令关键参数取值与理由（如 --runs-per-query 3、最多 5 轮、--profile）>

## 停止条件
<何时算完成；何时提前中止（如 validation 通过率连续 2 轮无提升）>

## 回滚
<出错如何恢复（如先备份原 description 到 SKILL.md.bak，失败时还原）>
```

## 示例（loop 迭代优化某技能 description）

```markdown
# Plan-Gate：loop 优化 my-skill 的 description

## 目标
把 my-skill 的触发评测通过率从当前值提升到未见数据 ≥90%。

## 范围与边界
只改 my-skill/SKILL.md 的 description 字段；不碰 body、references、scripts。

## 参数
--runs-per-query 3（官方协议）；最多 5 轮；--trigger-threshold 0.5。

## 停止条件
train 全过且 validation 通过率不再提升；或满 5 轮。按 validation 最高分选版。

## 回滚
启动前备份原 SKILL.md 至 SKILL.md.bak；任一轮 validation 退化即停，按历史最高回写。
```

---

## 版本历史

- **v2026.09** (2026-09-11) - 初版：五节计划模板 + 使用约定（AI 走 --plan 五节；人类 --plan-text 快速通道），由 `scripts/_impl/_gate.py` 消费
