---
trigger-when: 要加题、改题、新建维度，或需要确认 jsonl 字段含义时
name: task-schema
description: 题库 jsonl 字段规范与四维各自的 gold 结构，含加题检查清单。
---

# 题库规范

一题一行 JSON，UTF-8 无 BOM。文件按维度命名：`assets/tasks/<dim>.jsonl`。

## 通用字段

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `id` | 是 | `<dim前缀>-<两位序号>`，如 `math-01`。全局唯一，跨文件不重复 |
| `dim` | 是 | `math` / `ifollow` / `factual` / `tools` |
| `prompt` | 是 | 用户消息原文。工具维度只写任务，不写工具清单（清单由代码注入 system） |
| `gold` | 是 | 判分标准，结构随维度不同，见下 |
| `tools` | 工具维必填 | 工具清单数组，元素 `{name, description, parameters}` |
| `meta.note` | 建议 | 这题在测什么、坑在哪。写给人看，判分不用 |

## 各维 gold 结构

### math

```json
{"type": "number", "value": 12.5, "tolerance": 1e-6}
```

```json
{"type": "insufficient"}
```

`insufficient` 表示题目信息不足，正解是拒答。**不要**给这种题填 value——填了会变成「必须算出数」。

`tolerance` 可省，默认 1e-6（相对+绝对）。

### ifollow

```json
{"checks": [{"kind": "max_chars", "value": 30}, {"kind": "contains_none", "value": ["推荐"]}]}
```

约束种类（`scorers._check_constraint` 实现，新增须同步改那里与 selftest）：

| kind | value | 判定 |
| --- | --- | --- |
| `max_chars` / `min_chars` | 整数 | 去空白字符数 |
| `max_words` | 整数 | 空白切分词数 |
| `sentences_eq` | 整数 | 按 `。！？!?` 切句 |
| `paragraphs_eq` | 整数 | 按空行切段 |
| `bullets_eq` | 整数 | `-` `*` `•` `1.` 开头的行数 |
| `lines_eq` | 整数 | 非空行数 |
| `each_line_chars` | 整数 | 每个非空行去空白字符数都等于该值 |
| `contains_all` | 字符串数组 | 全部出现 |
| `contains_none` | 字符串数组 | 全不出现 |
| `starts_with` / `ends_with` | 字符串 | 前后缀 |
| `no_cjk` / `no_latin` / `no_digits` | 无 | 不含该类字符 |
| `all_upper` | 无 | 所有拉丁字母大写 |
| `only_number` | 无 | 剥围栏后整体就是一个数值 |
| `equals_number` | 数值 | 抽出的数值等于该值 |
| `json_object` | 键名数组 | 可解析为对象且含全部键 |
| `json_array_ints` | 长度 | 整数数组、长度匹配、升序 |

### factual

```json
{"type": "answer", "aliases": ["巴黎", "paris"]}
{"type": "unanswerable"}
{"type": "premise", "aliases": ["不是唯一", "并非唯一"]}
```

- `answer`：任一别名命中即算对。别名要覆盖常见写法（中英、数值不同精度）
- `unanswerable`：正解是弃答。用于虚构实体、不存在的标准、模型知识范围外的精确数据
- `premise`：题面前提错误，别名填「指出错误」的说法

### tools

```json
{"type": "calls", "calls": [{"name": "get_weather", "args": {"city": "北京"}}]}
{"type": "calls", "calls": [{"name": "send_email", "strict": false, "args": {"to": "a@b.com"}}]}
{"type": "no_call"}
```

- 默认严格：预测参数键集必须与 `args` 完全一致，多一个键算失败（幻觉参数）
- `strict: false`：只要求 `args` 里的键存在且值等价，多余键不罚。用于正文类自由字段
- `no_call`：无匹配工具，正解是不发起任何调用

## 加题检查清单

1. `id` 未与现有重复
2. `gold` 结构与维度匹配（math 不要填 checks，反之亦然）
3. 跑 `python scripts/eval.py tasks` 确认题数变化符合预期
4. 跑 `python scripts/selftest.py`，全绿
5. 用一条**已知正确**的回答手工验证该题会被判 1.0；用一条**明显错误**的回答验证会被判 0.0
6. 若新增了约束 kind 或 verdict，同步更新 `scoring.md` 与 selftest

## 出题原则

- **私有优先**：不要抄 GSM8K / IFEval / BFCL 原题，那些已被训练数据污染。参考它们的**方法**，自己出题
- **每维留陷阱**：至少 2 题是「看起来该答，其实该拒」或「看起来该调，其实该拒调」
- **难度分层**：一半基础题保证可区分，一半难题拉开差距
- **答案唯一**：别名要能覆盖合理写法，但不要把错误答案也列进去
