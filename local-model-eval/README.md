# local-model-eval

> 本地模型四维能力评测：启动服务 → 跑题库 → 程序化判分 → 出可交互报告。全程离线。

版本 0.1.1（打磨中，暂不升版）

## 这是什么

给本地部署的模型（GGUF / llama.cpp / LM Studio / Ollama）做一次可复现的能力体检，覆盖四个维度：

| 维度 | 测什么 | 判分方式 |
| --- | --- | --- |
| 数学推理 | 单步到三步数值推理 + **识别信息不足** | 抽取最终数值，容差比较 |
| 指令遵循 | 长度、句数、行数、禁词、JSON 结构等可验证约束 | 逐条约束代码判定，部分得分 |
| 事实性与幻觉 | 稳定事实、不可答问题、错误前提、置信度校准 | 三分类 + ECE |
| 工具调用 | 选工具、填参数、并行调用、**无匹配工具时不调用** | 调用结构化比对（顺序无关） |

产出一份单文件 HTML 报告，每个数字都能下钻到判分理由和模型原始响应。

## 为什么不是「跑一遍 MMLU」

- 公开题集已被训练数据污染，分数虚高且无法察觉
- IFEval 这类基准在 8B 模型上已饱和，测不出本地档位差异
- 本地 16 GB 显存跑全量公开集要几小时，而私有 64 题 20 分钟能给出可决策信号

所以本题库是手写私有题，方法参考公开基准（详见 `references/benchmark-basis.md`）。

## 能跑什么：硬件适配闸门

在跑评测之前，先判断目标配置能不能扛住。这个阶段会生成另一份报告（固定 ThemeVault #001 夜灯主题 + B站·宝藏二哥AIA 署名，与评测报告的双主题无关）：

```bash
python scripts/eval.py probe-hw --out evals/hardware.json
python scripts/eval.py hardware --hardware evals/hardware.json --models <模型清单.json> --out evals/hardware-report.html
```

- `probe-hw` 逐项标注来源：实测 / 规格 / 计算 / 估算 / 缺失，不伪造、不把单次采样当稳定读数
- 模型清单要给出各量化的实际权重文件大小（GiB）；缺了就按参数量估算，报告会标「估算」
- 四态矩阵：显存内 / 部分卸载 / 仅 CPU / 放不下；数据不足写「数据不足，暂不判定」，不伪装成第五种状态
- 三维筛选（规模 × 量化 × 上下文），点行看权重/KV/运行时拆分与瓶颈
- Decode 与 Prefill 分开；没有可靠依据时写「暂无法可靠估算」，不编造 Token/s
- PolyStrata + KVMem 作为第二路线单独核算，实机版本/能力清单优先于参考文档

方法细节见 `references/hardware-fit.md`。

## 怎么用

### 1. 启动本地服务

不想手敲命令的话，可以用 **[AI Vault](https://ergeaia.github.io/aivault-site/)**（本地优先、Agent-centric 的 AI 创作者工作台）管理与启动本地引擎：它内置 llama.cpp 等本地部署方式，同时把 Skill / Prompt / MCP / 模型统一收在本地 Vault 里，可直接分发到各 Agent 的 skills 目录。数据留在本机，不依赖云服务。

手工启动 llama.cpp：

```bash
llama-server -m <model.gguf> --host 127.0.0.1 --port 8080 \
  --jinja --parallel 1 --ctx-size 8192 -ngl 999
```

`--jinja` 必须加：不加则 chat 模板不含工具调用段，工具维度全线失败，且失败原因看起来像「模型不会调工具」。

LM Studio：Developer → Start Server（默认 `127.0.0.1:1234`）。

### 2. 确认服务

```bash
python scripts/eval.py probe --base-url http://127.0.0.1:8080/v1
```

要看到 `ok: true` 且 `props.chat_template_present` 为 true。

### 3. 跑评测

```bash
python scripts/eval.py run --base-url http://127.0.0.1:8080/v1 --out evals/results/q4km
```

默认 64 题、`temperature=0`、`seed=20260101`。中断后重跑同一命令即续跑。

### 4. 看报告

打开 `evals/results/q4km/report.html`。先读「这些数字不代表什么」一节，再看分数。

报告使用你的品牌主题：**ThemeVault #001 夜灯 / #002 晨光**。右上角图标可随时切换；默认跟随系统深浅偏好，手动选择会记到 `localStorage`，下次打开保持。生成时也可用 `--theme yedeng` 或 `--theme chenguang` 固定初始主题。单文件、零外部资源，断网可开。

## 示例提示词

| 场景 | 示例提示词 |
| --- | --- |
| 摸底新模型 | 我刚下了 Qwen2.5-14B 的 Q4_K_M，帮我测一下它的数学、指令遵循、幻觉和工具调用大概什么水平 |
| 量化掉点 | 同一个模型的 Q4_K_M 和 Q8_0 各跑一次，告诉我量化掉了多少分 |
| 换模型决策 | 我现在用 7B，想换 14B，帮我跑配对比较看值不值 |
| 验证评测本身 | 帮我跑个负对照，确认这套题真的能测出模型差异 |
| 只测一维 | 只跑工具调用这一维，我想看看它会不会乱调工具 |

## 关键产物

| 文件 | 内容 |
| --- | --- |
| `raw.jsonl` | 唯一事实源：prompt、哈希、原始响应、耗时、seed |
| `scores.jsonl` | 每题分数 + 判分理由 + verdict |
| `summary.json` | 各维均值/CI/通过率、幻觉率、ECE、成本 |
| `manifest.json` | 端点、模型、seed、时间、raw 哈希（复现核对用） |
| `report.html` | 静态报告，离线可开 |

## 验收标准

声称「评测完成」前必须四项都过：

| 项 | 怎么验 | 不过怎么办 |
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
python scripts/eval.py selftest        # 判分器自检
python scripts/eval.py export-recheck  # 导出人工复判样本
python scripts/eval.py recheck         # 算人机一致率
python scripts/probe_hw.py             # 直接探测硬件（等价 probe-hw）
python scripts/hardware.py             # 直接生成硬件报告（等价 hardware）
python scripts/smoke.py                # 离线链路冒烟
```

退出码：`0=PASS` / `1=FAIL` / `2=ERROR`。

## 已知边界

- 只测可程序化验证的能力。语气、风格、说服力不做，也不假装能做
- 单轮静态工具注入，不代表真实 function calling 模板下的表现
- 16 题/维的置信区间很宽（约 ±12 个百分点），差异小于区间宽度不构成有效差异
- 不做多轮状态模拟、不做沙盒代码执行（成本过高，需要 Docker 级隔离）
- 跨引擎（llama.cpp vs vLLM）分数不可直接比

## 目录

```
local-model-eval/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── assets/tasks/          # 四维题库 jsonl
├── references/
│   ├── measurement-contract.md   # 每维测什么、怎么判、会怎么错
│   ├── task-schema.md            # 加题规范
│   ├── scoring.md                # 判分实现与改判分纪律
│   └── benchmark-basis.md        # 方法来自哪些公开基准
└── scripts/
    ├── eval.py           # CLI 入口
    ├── probe.py          # 端点探测
    ├── run.py            # 运行器 + 统计
    ├── scorers.py        # 四维判分器
    ├── report.py         # HTML 渲染
    ├── compare.py        # 配对比较
    ├── recheck.py        # 人工复判一致率
    ├── selftest.py       # 判分器对抗样例
    └── smoke.py          # 离线链路冒烟
```
