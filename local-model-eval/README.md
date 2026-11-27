# local-model-eval

> 本地模型评测执行器：先判能不能跑，再判跑得怎么样。全程离线，程序化判分，报告可逐题下钻。

版本：1.0.1

## 这是什么

给本地部署模型（llama.cpp / LM Studio / Ollama 等 OpenAI 兼容端点）做可复现的能力体检。四个维度全部程序化判分，**不引入 LLM 裁判**：

| 维度 | 测什么 | 判分方式 |
| --- | --- | --- |
| 数学推理 | 单步到三步数值推理 + 识别信息不足 | 最终数值抽取 + 容差比较 |
| 指令遵循 | 长度、句数、行数、禁词、JSON 结构等可验证约束 | 逐条约束代码判定，部分得分 |
| 事实性与幻觉 | 稳定事实、不可答问题、错误前提、置信度校准 | 三分类 + ECE |
| 工具调用 | 选工具、填参数、并行调用、无匹配工具时不调用 | 调用结构化比对（顺序无关） |

题库为 64 道手写私有题（每维 16 道），不用 GSM8K / IFEval / BFCL 原题——那些已被训练数据污染且部分已饱和。方法来源见 `references/benchmark-basis.md`。

## 怎么用

### 1. 选模型（可选）

还没定模型，或想知道机器能扛住什么，先跑硬件闸门：

```bash
python scripts/eval.py probe-hw --out evals/hardware.json
python scripts/eval.py hardware --hardware evals/hardware.json \
  --models <模型清单.json> --out evals/hardware-report.html
```

模型清单字段：`name` / `params_b` / `layers` / `kv_heads` / `head_dim` / `kv_bytes`，以及各量化的实际权重文件大小（GiB）。MLA / 滑动窗口等非标准注意力须额外给 `attention` 字段（如 `mla`），否则按标准结构算 KV，**不要对这类模型硬套**。

报告给四态矩阵（显存内 / 部分卸载 / 仅 CPU / 放不下），三维筛选（规模 × 量化 × 上下文），每个数字标来源（实测 / 规格 / 计算 / 估算 / 缺失）。速度没有可靠依据时写「暂无法可靠估算」，不编造 Token/s。方法见 `references/hardware-fit.md`。

### 2. 启动本地服务

可用 [AI Vault](https://ergeaia.github.io/aivault-site/)（本地优先、Agent-centric 的 AI 创作者工作台）管理本地引擎，并把 Skill / Prompt / MCP 统一收在本地 Vault 分发到各 Agent。数据留在本机。

手工启动 llama.cpp：

```bash
llama-server -m <model.gguf> --host 127.0.0.1 --port 8080 \
  --jinja --parallel 1 --ctx-size 8192 -ngl 999
```

`--jinja` 必须加。缺 chat 模板时 `probe` 会返回失败，工具维度无法运行。

LM Studio：Developer → Start Server（默认 `127.0.0.1:1234`）。

### 3. 确认服务

```bash
python scripts/eval.py probe --base-url http://127.0.0.1:8080/v1
```

需要 `ok: true` 且 `props.chat_template_present` 为 true。

### 4. 跑评测

```bash
python scripts/eval.py run --base-url http://127.0.0.1:8080/v1 --out evals/results/q4km
```

默认 64 题、`temperature=0`、`seed=20260101`。中断后重跑同一命令即续跑，不重复请求。

### 5. 看报告

打开 `evals/results/q4km/report.html`。先读「这些数字不代表什么」，再看分数。

能力报告用 ThemeVault #001 夜灯 / #002 晨光，右上角图标切换，默认跟随系统偏好，手动选择记入 `localStorage`。可用 `--theme yedeng|chenguang|auto` 固定初始主题。单文件、零外部资源。

**硬件报告与能力报告是不同产物**：前者固定夜灯 + B站·宝藏二哥AIA 署名，后者双主题无署名，互不混用。

## 示例提示词

| 场景 | 示例提示词 |
| --- | --- |
| 摸底新模型 | 我刚下了 Qwen2.5-14B 的 Q4_K_M，帮我测一下四维能力 |
| 选型 | 我这台机器适合跑 14B 的哪个量化？先做个硬件评估 |
| 量化掉点 | 同一模型的 Q4_K_M 和 Q8_0 各跑一次，告诉我掉了多少分 |
| 换模型决策 | 我现在用 7B，想换 14B，帮我跑配对比较看值不值 |
| 验证评测本身 | 帮我跑个负对照，确认这套题真的能测出差异 |
| 只测一维 | 只跑工具调用，我想看它会不会乱调工具 |

## 产物

| 文件 | 内容 |
| --- | --- |
| `raw.jsonl` | 唯一事实源：prompt、哈希、原始响应、耗时、seed |
| `scores.jsonl` | 每题分数、判分理由、verdict |
| `summary.json` | 各维均值 / CI / 通过率、幻觉率、ECE、成本 |
| `manifest.json` | 端点、模型、seed、时间、raw 哈希（复现核对） |
| `report.html` | 能力报告，双主题，逐题下钻 |
| `hardware-report.html` | 硬件报告，固定夜灯 + 署名 |

## 验收

| 项 | 命令 / 判据 | 不过怎么办 |
| --- | --- | --- |
| 判分器有效 | `python scripts/selftest.py` 全绿 | 修判分器 |
| 链路可用 | `python scripts/smoke.py` 全绿 | 修链路 |
| 测得出差异 | 负对照分数显著低于主配置 | 题库失效，重出题 |
| 判分可信 | 人工复判 kappa ≥ 0.85 | 该维降级为「参考」 |

## 命令表

```bash
python scripts/eval.py probe           # 探测服务
python scripts/eval.py tasks           # 列题库
python scripts/eval.py run             # 跑评测
python scripts/eval.py score           # 重判（不重跑模型）
python scripts/eval.py report          # 只渲染报告
python scripts/eval.py compare         # 两配置配对比较
python scripts/eval.py probe-hw        # 探测硬件
python scripts/eval.py hardware        # 生成硬件报告
python scripts/eval.py selftest        # 判分器自检
python scripts/eval.py export-recheck  # 导出复判样本
python scripts/eval.py recheck         # 算人机一致率
python scripts/smoke.py                # 离线链路冒烟
```

退出码：`0=PASS` / `1=FAIL` / `2=ERROR`。

## 边界

- 只测可程序化验证的能力；语气、风格、说服力不做
- 单轮静态工具注入，不代表真实 function calling 表现
- n=16 时通过率标准误约 12pp，Wilson 区间半宽约 20pp（通过率接近 50% 时）。差异小于区间宽度不构成有效差异
- 不做多轮状态模拟、沙盒代码执行、跨引擎分数对比

## 目录

```
local-model-eval/
├── SKILL.md                       # 执行规则与硬边界
├── README.md                      # 本文件
├── CHANGELOG.md                   # 版本历史
├── assets/tasks/                  # 四维题库 jsonl
├── references/
│   ├── measurement-contract.md    # 每维测什么、怎么判、会怎么错
│   ├── task-schema.md             # 加题规范
│   ├── scoring.md                 # 判分实现与改判分纪律
│   ├── benchmark-basis.md         # 方法来源与取舍
│   └── hardware-fit.md            # 硬件适配方法论
└── scripts/
    ├── eval.py                    # CLI 入口
    ├── probe.py                   # 服务端点探测
    ├── probe_hw.py                # 本机硬件探测
    ├── hardware.py                # 硬件报告生成
    ├── run.py                     # 评测运行器 + 统计
    ├── scorers.py                 # 四维判分器
    ├── report.py                  # 能力报告渲染
    ├── compare.py                 # 配对比较
    ├── recheck.py                 # 人机一致率
    ├── selftest.py                # 判分器对抗样例
    └── smoke.py                   # 离线链路冒烟
```
