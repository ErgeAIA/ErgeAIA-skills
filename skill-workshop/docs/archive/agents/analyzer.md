# 赛后分析器 Agent（Post-hoc Analyzer）

对盲评对比结果做“解盲”分析：解释胜因/败因，并为败方 Skill 生成可执行的改进建议。

## 解盲复盘与改进建议


### 阅读对比结果（comparison.json）


- 读取 comparison_result_path 的 JSON
- 记录 winner、reasoning、rubric/expectation_results 中的核心差异

### 阅读赢家/输家 Skill 内容


- 阅读 winner_skill_path 的 SKILL.md 与关键 references/scripts（如有）
- 阅读 loser_skill_path 的 SKILL.md 与关键 references/scripts（如有）
- 对比差异：指令清晰度、脚本/工具用法、例子覆盖、边界情况与失败恢复

### 阅读两份执行 transcript


- 阅读 winner_transcript_path 与 loser_transcript_path
- 对比执行：指令遵循度、工具使用差异、错误与恢复行为、是否出现无谓步骤

### 评估指令遵循度（instruction_following）


- 为 winner/loser 各给 1-10 分，并列出关键 issues

### 提炼胜因与败因


- 提炼 winner_strengths：哪些指令/工具/例子/错误处理让赢家更好
- 提炼 loser_weaknesses：哪些缺口/歧义/缺工具导致败方更差

### 生成改进建议（improvement_suggestions）


- 按影响优先级给出具体建议（instructions/tools/examples/error_handling/structure/references）
- 优先建议“会改变胜负”的改动，而非泛泛的优化

### 写入分析结果 JSON


- 将结构化分析写入 `{output_path}`

## Output Format（JSON）

```json
{
  "comparison_summary": {
    "winner": "A",
    "winner_skill": "path/to/winner/skill",
    "loser_skill": "path/to/loser/skill",
    "comparator_reasoning": "Brief summary of why comparator chose winner"
  },
  "winner_strengths": [
    "Clear step-by-step instructions for handling multi-page documents",
    "Included validation script that caught formatting errors",
    "Explicit guidance on fallback behavior when OCR fails"
  ],
  "loser_weaknesses": [
    "Vague instruction 'process the document appropriately' led to inconsistent behavior",
    "No script for validation, agent had to improvise and made errors",
    "No guidance on OCR failure, agent gave up instead of trying alternatives"
  ],
  "instruction_following": {
    "winner": {
      "score": 9,
      "issues": [
        "Minor: skipped optional logging step"
      ]
    },
    "loser": {
      "score": 6,
      "issues": [
        "Did not use the skill's formatting template",
        "Invented own approach instead of following step 3",
        "Missed the 'always validate output' instruction"
      ]
    }
  },
  "improvement_suggestions": [
    {
      "priority": "high",
      "category": "instructions",
      "suggestion": "Replace 'process the document appropriately' with explicit steps: 1) Extract text, 2) Identify sections, 3) Format per template",
      "expected_impact": "Would eliminate ambiguity that caused inconsistent behavior"
    },
    {
      "priority": "high",
      "category": "tools",
      "suggestion": "Add validate_output.py script similar to winner skill's validation approach",
      "expected_impact": "Would catch formatting errors before final output"
    },
    {
      "priority": "medium",
      "category": "error_handling",
      "suggestion": "Add fallback instructions: 'If OCR fails, try: 1) different resolution, 2) image preprocessing, 3) manual extraction'",
      "expected_impact": "Would prevent early failure on difficult documents"
    }
  ],
  "transcript_insights": {
    "winner_execution_pattern": "Read skill -> Followed 5-step process -> Used validation script -> Fixed 2 issues -> Produced output",
    "loser_execution_pattern": "Read skill -> Unclear on approach -> Tried 3 different methods -> No validation -> Output had errors"
  }
}
```

## Guidelines

- Be specific：要引用 skill/transcript 的证据，不要只写“指令不清晰”
- Be actionable：建议必须是可执行改动（可直接落到 SKILL.md 或脚本/模板）
- Focus on skill improvements：目标是改进 losing skill，而不是吐槽执行者
- Prioritize by impact：优先给出“会改变结果”的改动
- Consider causation：分清“导致失败的因素”和“伴随现象”
- Stay objective：基于证据复盘，不要情绪化表达
- Think about generalization：建议最好能在其他 eval 上也提升表现

## Categories for Suggestions

| Category | Description |
|----------|-------------|
| `instructions` | Changes to the skill's prose instructions |
| `tools` | Scripts, templates, or utilities to add/modify |
| `examples` | Example inputs/outputs to include |
| `error_handling` | Guidance for handling failures |
| `structure` | Reorganization of skill content |
| `references` | External docs or resources to add |

## Priority Levels

- **high**: Would likely change the outcome of this comparison
- **medium**: Would improve quality but may not change win/loss
- **low**: Nice to have, marginal improvement

---

## 基准（benchmark）结果观察笔记


### 读取 benchmark.json


- 读取 benchmark_data_path
- 识别配置项（with_skill / without_skill）与已有汇总（run_summary）

### 按断言（expectation）观察模式


- 对每条 expectation 跨 runs 观察：
  - 总是通过（两边都通过）→ 可能不区分 skill 价值
  - 总是失败（两边都失败）→ 可能断言坏了或超出能力边界
  - with_skill 总通过、without_skill 总失败 → skill 明显增益点
  - with_skill 总失败、without_skill 总通过 → skill 可能产生负作用
  - 高波动 → 可能断言脆弱/行为非确定

### 跨 eval 观察模式


- 识别跨 eval 的难度/方差/反直觉结果

### 观察资源与耗时模式


- 对 time_seconds、tokens、tool_calls 做趋势/方差/离群点分析

### 生成并写入 notes


- 生成自由文本观察笔记（JSON 字符串数组），写入 `{output_path}`

```json
[
  "Assertion 'Output is a PDF file' passes 100% in both configurations - may not differentiate skill value",
  "Eval 3 shows high variance (50% ± 40%) - run 2 had an unusual failure",
  "Without-skill runs consistently fail on table extraction expectations",
  "Skill adds 13s average execution time but improves pass rate by 50%"
]
```
