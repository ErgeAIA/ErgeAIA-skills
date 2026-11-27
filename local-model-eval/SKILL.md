---
name: local-model-eval
description: "评测本地部署模型（llama.cpp、LM Studio、Ollama 等 OpenAI 兼容端点）的四维能力，按序执行题库、程序化判分并汇总为可交互 HTML 报告。Use when 用户要测本地模型能力、对比两个量化或模型、验证量化掉点、做评测报告、跑 benchmark。"
metadata:
  author: ErgeAIA
  version: "0.1.1"
---

# local-model-eval

## 定位

本地模型能力评测的**执行器**，不是评测方法论读物。用户启动本地服务后，本技能按固定顺序把题库跑成原始响应，用程序化判分器打分，产出可追溯的 HTML 报告。

核心立场：**可复现的产物链优先于分数**。任何分数都必须能追到某一行原始响应、某个提示词哈希、某个模型标识、某个 seed。做不到就不出分。

不是：模型训练/微调工具、通用 benchmark 复现框架（不重跑 MMLU 全量）、LLM 裁判平台。

## 何时使用

- 刚下载一个 GGUF，想知道它在数学、指令遵循、幻觉、工具调用上大概什么水平
- 同一模型的 Q4_K_M 与 Q8_0 对比，判断量化掉了多少点
- 换模型前做一次基线，换完再跑一次做配对比较
- 需要一份能贴给别人看、每个数字都能下钻的报告
- Not for: 训练侧评测（loss/perplexity）、纯吞吐压测（用 `llama-bench`）、需要人工主观打分的开放式创作质量

## 工作步骤

严格按序执行。每步有产物，产物不全不进下一步。

### 第 1 步：确认服务与运行时事实

```bash
python scripts/eval.py probe --base-url http://127.0.0.1:8080/v1
```

**必须看到**：`models` 非空、`backend` 为 `llama.cpp`、`props.chat_template_present` 为 true。

- `chat_template_present` 为 false → 🛑 **STOP**：提示用户给 `llama-server` 加 `--jinja` 后重启。不加的话工具调用与对话格式都失真，测出来的分数没有意义。**等用户确认已重启并重新 probe 通过，才允许进第 2 步。**
- 探测失败 → 🛑 **STOP**：按输出的启动命令提示用户启动服务，**不得**改用猜测的模板继续。等用户确认服务已起并重跑 probe 通过。

→ **verify**: probe 输出 `ok: true`，且记录了 build_info 与 model_path

### 第 2 步：确认题库

```bash
python scripts/eval.py tasks
```

默认四维各 16 题（共 64）。用户要加题就编辑 `assets/tasks/*.jsonl`，格式见 `references/task-schema.md`。

→ **verify**: 四维题数符合预期，无 0 题维度

### 第 3 步：跑评测

```bash
python scripts/eval.py run --base-url http://127.0.0.1:8080/v1 --out evals/results/q4km
```

默认 `temperature=0`、`seed=20260101`、`max_tokens=768`。跑完自动渲染报告。

- 中断后重跑同一命令即续跑，不重复请求已完成题目
- 只跑部分维度加 `--dims math,tools`

→ **verify**: `evals/results/<name>/` 下有 `raw.jsonl`、`scores.jsonl`、`summary.json`、`manifest.json`、`report.html`

### 第 4 步：看分数前先看边界

🔴 **CHECKPOINT**：向用户报告各维分数、n 与区间之前，先确认自己已读完报告里「这些数字不代表什么」一节。读不完就不报分数。

报告里「这些数字不代表什么」一节必须读完再解读。每维的测量边界写在 `references/measurement-contract.md`。

**判读规则**：
- 两次运行的差异小于置信区间宽度 → 不构成有效差异，不要说「A 比 B 强」
- 任一维度 `errors > 0` → 报告标注「不完整」，总分不作结论
- 幻觉率与弃答率要一起看：弃答率 0 且幻觉率高，说明模型在硬猜

→ **verify**: 能说出每个数字的 n、CI、以及它不覆盖什么

### 第 5 步（可选但强烈建议）：负对照

🔴 **CHECKPOINT**：跑负对照前先向用户确认「弱配置」具体指什么（Q2_K / 更小模型 / temperature=2.0 三选一），并保证它与主配置只差这一个变量。两处同时变就无法归因，这一步白跑。

证明这套题真的测得出差异：

```bash
python scripts/eval.py run --base-url ... --out evals/results/negative --dims math
# 用明显更弱的配置（Q2_K 量化 / 更小模型 / temperature=2.0）跑同一批题
python scripts/eval.py compare --a evals/results/q4km --b evals/results/negative
```

弱配置分数**没有显著下降** → 题库或判分器失效，前面所有结论作废，先修题库。

→ **verify**: compare 输出 `差异显著`（p < 0.05），且方向符合预期

### 第 6 步（可选）：人工复判

```bash
python scripts/eval.py export-recheck --out evals/results/q4km
# 打开 recheck.csv，填 manual_pass_0or1 列（1=判对 0=判错）
python scripts/eval.py recheck --csv evals/results/q4km/recheck.csv
```

kappa < 0.85 的维度会被标为「降级为参考」。不一致条目是判分器缺陷候选，应补进 `scripts/selftest.py` 的 `CASES`。

→ **verify**: 输出各维度「可信 / 降级为参考」

### 第 7 步：配对比较（换模型 / 换量化时）

🔴 **CHECKPOINT**：下「A 比 B 好」的结论前，先核对两件事——① 两次运行的 `manifest.json` 除模型/量化外其他字段一致（seed、temperature、题库、端点）；② McNemar 的 p < 0.05。任一不满足，只报观测值，不下结论。

```bash
python scripts/eval.py compare --a evals/results/q4km --b evals/results/q8 --label-a Q4_K_M --label-b Q8_0
```

逐题配对 + McNemar 精确检验。**不要**用两个均值相减代替——均值差会把不同题上的胜负抵消。

→ **verify**: 报告 wins/ties、p 值，以及按维度的胜负分布

## 输出契约

| 产物 | 内容 | 用途 |
| --- | --- | --- |
| `raw.jsonl` | 每题 prompt、prompt_sha256、原始响应、耗时、usage、seed | 唯一事实源，可复核 |
| `scores.jsonl` | 每题分数、判分理由、verdict、判分细节 | 报告数据源，可重判 |
| `summary.json` | 各维均值/CI/通过率、幻觉率、ECE、成本 | 机读汇总 |
| `manifest.json` | 端点、模型、seed、温度、时间、raw 哈希 | 复现核对 |
| `report.html` | 单文件静态报告，离线可开 | 给人看 |

失败时必须报告：探测失败的原始输出 + 启动命令；判分异常时说明是请求失败还是判分失败，不得把请求失败静默算成 0 分而不标注。

## 约束

- **HARD: 不引入 LLM 裁判**。四维全部程序化判分。需要主观判断的维度不做，而不是用裁判糊过去——裁判不可复现且会偏好冗长答案。
- **HARD: 探测失败不降级**。无服务、无 chat 模板时报错退出，不用猜测的模板跑完整套题。
- **HARD: 不虚构分数**。取不到的数据写「未验证」，不写 0 不写估算。
- **HARD: 分数必须带 n 与区间**。单点数字（如「数学 82 分」）不算结论。
- **HARD: 修改题库后必须重跑 selftest**，确认判分器与新题仍然对得上。
- **CONDITIONAL: 负对照**。声称「A 比 B 好」之前必须跑过负对照或配对比较；只是「看看大概水平」可跳过。
- **禁止**: 把 `scores.jsonl` 当事实源改分数——要改就改判分器然后 `score` 重算。
- **禁止**: 用本技能结论替代用户对具体任务的实机验证。

## 资源

| 文件 | 何时读 |
| --- | --- |
| `references/measurement-contract.md` | 想知道每维具体测什么、提示模板长什么样、判分规则、已知失效模式 |
| `references/task-schema.md` | 要加题、改题、新建维度 |
| `references/scoring.md` | 想改判分逻辑、理解某个 verdict 的含义、调 CI 算法 |
| `references/benchmark-basis.md` | 想知道这些维度与方法来自哪些公开基准，以及为什么不用它们的原始题 |

## Gotchas

- **llama-server 必须 `--jinja`**。默认模板不含工具调用段，不加的话工具维度全线失败，且失败原因看起来像「模型不会调工具」。
- **`--parallel 1`**。并发会让部分实现的 logits 不稳定，同 seed 也复现不了。
- **temperature=0 不等于逐字节可复现**。GPU 浮点非结合性会偶发翻转，标准是「同硬件同 build 下 hash 一致」，跨引擎永远不一致。
- **推理模型会把 token 预算烧在思考上**。`max_tokens=768` 对带 `reasoning_content` 的模型可能不够，表现为内容为空、判 0 分。先看 `finish_reason` 是否为 `length`。
- **量化档位会改变指令遵循**。Q4 以下对格式约束（恰好三句、每行五字）的遵守明显变差，这是真实差异，不是判分器 bug。
- **题库会被模型见过**。GSM8K/IFEval 这类公开题已被污染，所以本题库用手写私有题；公开集只作外部锚点参照。
- **不要用均值差代替配对比较**。64 题里 A 赢 10 题、B 赢 10 题，均值可能几乎相等，但这不是「一样好」。
