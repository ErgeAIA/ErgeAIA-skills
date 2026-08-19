# 赛后分析器 Agent（Post-hoc Analyzer）

对盲评对比结果做“解盲”分析：解释胜因/败因，并为败方 Skill 生成可执行的改进建议。

## @工作流: 解盲复盘与改进建议

<!-- @类型: 评测子代理提示词 -->
<!-- @目的: 从对比结果、两份 Skill 内容与执行 transcript 中提炼可执行改进建议 -->
<!-- @场景: blind comparator 已给出 winner，需要解释原因并改进 loser skill -->
<!-- @前置条件: comparison_result_path、winner/loser skill 与 transcript 均可读取 -->
<!-- @后置验证: 输出 JSON 满足约定 schema，建议可执行且与败因因果相关 -->
<!-- @输入: winner, winner_skill_path, winner_transcript_path, loser_skill_path, loser_transcript_path, comparison_result_path, output_path -->
<!-- @产物: {output_path} -->
<!-- @ID: wf-posthoc-analyzer -->

### @步骤1: 阅读对比结果（comparison.json）

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @验证点: 理解 comparator 的取舍标准与胜负差距 -->
<!-- @验证方式: 能复述 comparator_reasoning，并指出关键评分差异/缺失项 -->
<!-- @ID: step-read-comparison-result -->

- @动作: 读取 comparison_result_path 的 JSON
- @动作: 记录 winner、reasoning、rubric/expectation_results 中的核心差异

### @步骤2: 阅读赢家/输家 Skill 内容

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @验证点: 能指出两份 Skill 在结构/约束/工具化上的关键差异 -->
<!-- @验证方式: 从 SKILL.md/references/scripts 中引用证据，说明差异如何影响执行 -->
<!-- @ID: step-read-both-skills -->

- @动作: 阅读 winner_skill_path 的 SKILL.md 与关键 references/scripts（如有）
- @动作: 阅读 loser_skill_path 的 SKILL.md 与关键 references/scripts（如有）
- @动作: 对比差异：指令清晰度、脚本/工具用法、例子覆盖、边界情况与失败恢复

### @步骤3: 阅读两份执行 transcript

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @验证点: 能对比两方的执行模式并定位偏离点 -->
<!-- @验证方式: 用 transcript 证据说明“哪里开始走偏/哪里做得更好” -->
<!-- @ID: step-read-both-transcripts -->

- @动作: 阅读 winner_transcript_path 与 loser_transcript_path
- @动作: 对比执行：指令遵循度、工具使用差异、错误与恢复行为、是否出现无谓步骤

### @步骤4: 评估指令遵循度（instruction_following）

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @验证点: winner/loser 的 score(1-10) 有证据支撑，issues 可复现 -->
<!-- @验证方式: 每条 issue 对应 transcript 中的具体片段或缺失证据 -->
<!-- @ID: step-score-instruction-following -->

- @动作: 为 winner/loser 各给 1-10 分，并列出关键 issues

### @步骤5: 提炼胜因与败因

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @验证点: strengths/weaknesses 与 comparison.json 与 transcript 的差异一致 -->
<!-- @验证方式: 每条要点都能对应至少一处证据（skill 或 transcript） -->
<!-- @ID: step-identify-strengths-weaknesses -->

- @动作: 提炼 winner_strengths：哪些指令/工具/例子/错误处理让赢家更好
- @动作: 提炼 loser_weaknesses：哪些缺口/歧义/缺工具导致败方更差

### @步骤6: 生成改进建议（improvement_suggestions）

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @验证点: 建议是“可落地的改动”，且与败因有因果关系 -->
<!-- @验证方式: 每条建议说明 expected_impact，并能解释为何会改变对比结果 -->
<!-- @ID: step-generate-suggestions -->

- @动作: 按影响优先级给出具体建议（instructions/tools/examples/error_handling/structure/references）
- @动作: 优先建议“会改变胜负”的改动，而非泛泛的优化

### @步骤7: 写入分析结果 JSON

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @验证点: 输出 JSON 字段齐全且类型正确 -->
<!-- @验证方式: comparison_summary/winner_strengths/loser_weaknesses/instruction_following/improvement_suggestions 等均存在 -->
<!-- @ID: step-write-analysis-json -->

- @动作: 将结构化分析写入 `{output_path}`

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

## @工作流: 基准（benchmark）结果观察笔记

<!-- @类型: 评测子代理提示词 -->
<!-- @目的: 在多次运行数据中发现模式/异常，补充 aggregate 指标之外的洞察 -->
<!-- @场景: benchmark.json 持续写入 run 结果，需要生成“人类可读的观察笔记” -->
<!-- @前置条件: benchmark_data_path 指向包含所有 run 结果的 benchmark.json -->
<!-- @后置验证: 输出为 JSON 字符串数组，每条笔记都能回溯到数据证据 -->
<!-- @输入: benchmark_data_path, skill_path, output_path -->
<!-- @产物: {output_path}（JSON array of strings） -->
<!-- @ID: wf-benchmark-notes -->

### @步骤1: 读取 benchmark.json

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @验证点: 理解已计算的 run_summary 与对比配置（with_skill/without_skill） -->
<!-- @验证方式: 能列出测试配置，并指出关键汇总指标与显著差异 -->
<!-- @ID: step-read-benchmark-data -->

- @动作: 读取 benchmark_data_path
- @动作: 识别配置项（with_skill / without_skill）与已有汇总（run_summary）

### @步骤2: 按断言（expectation）观察模式

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @验证点: 能指出“总是通过/总是失败/只在某配置通过/高度波动”的断言 -->
<!-- @验证方式: 每条模式结论都可在 benchmark.json 中定位到 run 证据 -->
<!-- @ID: step-analyze-per-assertion -->

- @动作: 对每条 expectation 跨 runs 观察：
  - 总是通过（两边都通过）→ 可能不区分 skill 价值
  - 总是失败（两边都失败）→ 可能断言坏了或超出能力边界
  - with_skill 总通过、without_skill 总失败 → skill 明显增益点
  - with_skill 总失败、without_skill 总通过 → skill 可能产生负作用
  - 高波动 → 可能断言脆弱/行为非确定

### @步骤3: 跨 eval 观察模式

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @验证点: 能指出“哪些 eval 类型更难/更易/更不稳定” -->
<!-- @验证方式: 结论可回溯到具体 eval 的 run 结果分布 -->
<!-- @ID: step-analyze-cross-eval -->

- @动作: 识别跨 eval 的难度/方差/反直觉结果

### @步骤4: 观察资源与耗时模式

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @验证点: 能指出 time_seconds/tokens/tool_calls 的异常点与离群 run -->
<!-- @验证方式: 结论对应具体 run 的数值与对比 -->
<!-- @ID: step-analyze-metrics -->

- @动作: 对 time_seconds、tokens、tool_calls 做趋势/方差/离群点分析

### @步骤5: 生成并写入 notes

<!-- @类型: 操作步骤 -->
<!-- @优先级: 必须 -->
<!-- @验证点: notes 每条都是具体观察，且避免无证据推测 -->
<!-- @验证方式: 每条 note 都能对应到某个断言/某个 eval/某组 runs -->
<!-- @ID: step-write-benchmark-notes -->

- @动作: 生成自由文本观察笔记（JSON 字符串数组），写入 `{output_path}`

```json
[
  "Assertion 'Output is a PDF file' passes 100% in both configurations - may not differentiate skill value",
  "Eval 3 shows high variance (50% ± 40%) - run 2 had an unusual failure",
  "Without-skill runs consistently fail on table extraction expectations",
  "Skill adds 13s average execution time but improves pass rate by 50%"
]
```
