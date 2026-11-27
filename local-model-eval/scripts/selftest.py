#!/usr/bin/env python3
"""判分器对抗样例自检。

为什么需要：判分器本身会出错。没有自检，就分不清「模型答错」和「判分器判错」。
每个用例都写清期望的 verdict，判分器行为漂移会立刻暴露。
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import scorers  # noqa: E402

CASES: list[dict] = []


def case(name: str, dim: str, task: dict, response: str, expect_score: float,
         expect_verdict: str | None = None):
    CASES.append({"name": name, "dim": dim, "task": task, "response": response,
                  "expect_score": expect_score, "expect_verdict": expect_verdict})


# ---- math ----
M = lambda v: {"id": "t", "dim": "math", "gold": {"type": "number", "value": v}}
MI = {"id": "t", "dim": "math", "gold": {"type": "insufficient"}}

case("math 正确整数", "math", M(160), "最多的一份是 160 元。", 1.0)
case("math 正确带千分位", "math", M(1024), "答案是 1,024", 1.0)
case("math 正确答案但啰嗦", "math", M(4), "甲 6 天乙 12 天，合起来 1/6+1/12=1/4，所以需要 4 天。", 1.0)
case("math 错误答案", "math", M(160), "答案是 180 元", 0.0)
case("math 抽不到数字", "math", M(5), "无法计算", 0.0)
case("math 陷阱题正确拒答", "math", MI, "题目没有给出前天的数据，无法确定。", 1.0)
case("math 陷阱题编造数值", "math", MI, "前天卖出 13 箱。", 0.0)
case("math 陷阱题缺高度却给体积", "math", MI, "体积是 15 立方厘米。", 0.0)
case("math 小数容差内", "math", M(86.25), "平均分 86.2500", 1.0)
case("math 负号解析", "math", M(-5), "x = -5", 1.0)
case("math boxed 格式", "math", M(42), "所以答案是 \\boxed{42}", 1.0)
case("math #### 格式", "math", M(12.5), "计算得 12.5\n#### 12.5", 1.0)

# ---- ifollow ----
def IF(checks):
    return {"id": "t", "dim": "ifollow", "gold": {"checks": checks}}

case("if 字数超限", "ifollow", IF([{"kind": "max_chars", "value": 5}]), "这是一段明显超过五个字的话", 0.0)
case("if 字数达标", "ifollow", IF([{"kind": "max_chars", "value": 5}]), "五个字啊", 1.0)
case("if 句数正确", "ifollow", IF([{"kind": "sentences_eq", "value": 2}]), "第一句。第二句。", 1.0)
case("if 句数错误", "ifollow", IF([{"kind": "sentences_eq", "value": 2}]), "只有一句。", 0.0)
case("if JSON 带围栏", "ifollow", IF([{"kind": "json_object", "value": ["name"]}]),
     "```json\n{\"name\": \"x\"}\n```", 1.0)
case("if JSON 缺键", "ifollow", IF([{"kind": "json_object", "value": ["name", "version"]}]),
     "{\"name\": \"x\"}", 0.0)
case("if 禁词命中", "ifollow", IF([{"kind": "contains_none", "value": ["推荐"]}]),
     "我推荐这本。", 0.0)
case("if 禁词未命中", "ifollow", IF([{"kind": "contains_none", "value": ["推荐"]}]),
     "这本值得一读。", 1.0)
case("if 全大写失败", "ifollow", IF([{"kind": "all_upper"}]), "The Ocean is deep.", 0.0)
case("if 全大写通过", "ifollow", IF([{"kind": "all_upper"}]), "THE OCEAN IS DEEP.", 1.0)
case("if 中文数字约束", "ifollow", IF([{"kind": "no_digits"}, {"kind": "contains_all", "value": ["十二"]}]),
     "一年有十二个月。", 1.0)
case("if 用了阿拉伯数字", "ifollow", IF([{"kind": "no_digits"}, {"kind": "contains_all", "value": ["十二"]}]),
     "一年有十二个月，共12个月。", 0.5)
case("if 数字约束全失败", "ifollow", IF([{"kind": "no_digits"}, {"kind": "contains_all", "value": ["十二"]}]),
     "一年有12个月。", 0.0)
case("if 每行字数全对", "ifollow",
     IF([{"kind": "lines_eq", "value": 3}, {"kind": "each_line_chars", "value": 5}]),
     "春眠不觉晓\n处处闻啼鸟\n夜来风雨声", 1.0)
case("if 每行字数有错", "ifollow",
     IF([{"kind": "lines_eq", "value": 3}, {"kind": "each_line_chars", "value": 5}]),
     "春眠不觉晓\n处处闻啼鸟啊\n夜来风雨声", 0.5)
case("if 只输出数字但带单位", "ifollow", IF([{"kind": "only_number"}]), "1024 字节", 0.0)
case("if 只输出数字", "ifollow", IF([{"kind": "only_number"}]), "1024", 1.0)
case("if 前缀不符", "ifollow", IF([{"kind": "starts_with", "value": "结论是"}]),
     "我认为结论是：可以。", 0.0)
case("if 数组未排序", "ifollow", IF([{"kind": "json_array_ints", "value": 4}]),
     "[1,3,5,9]", 1.0)
case("if 数组乱序", "ifollow", IF([{"kind": "json_array_ints", "value": 4}]),
     "[5,3,9,1]", 0.0)

# ---- factual ----
def FA(aliases):
    return {"id": "t", "dim": "factual", "gold": {"type": "answer", "aliases": aliases}}

FU = {"id": "t", "dim": "factual", "gold": {"type": "unanswerable"}}
FP = {"id": "t", "dim": "factual", "gold": {"type": "premise", "aliases": ["不是唯一", "并非唯一"]}}

case("fact 命中中文别名", "factual", FA(["巴黎", "paris"]), "法国首都是巴黎。\n置信度: 95", 1.0)
case("fact 命中英文别名大小写", "factual", FA(["paris"]), "PARIS.\nconfidence: 90", 1.0)
case("fact 答案错误", "factual", FA(["巴黎"]), "法国首都是里昂。\n置信度: 90", 0.0)
case("fact 数值别名", "factual", FA(["299792458"]), "约 299792458 m/s\n置信度: 99", 1.0)
case("fact 不可答正确弃答", "factual", FU, "这个数据不在我的知识范围内，无法给出可靠数值。\n置信度: 20", 1.0)
case("fact 不可答却编造", "factual", FU, "2024 年 3 月 15 日上证指数收盘 3054.26 点。\n置信度: 85", 0.0)
case("fact 虚构论文却编造标题", "factual", FU,
     "该论文标题为《Room-temperature superconductivity in hydrogen-rich compounds》。\n置信度: 80", 0.0)
case("fact 过度弃答", "factual", FA(["巴黎"]), "我不确定，无法回答。\n置信度: 10", 0.0)
case("fact 纠正错误前提", "factual", FP, "这个说法不对，地球并非唯一有卫星的行星。\n置信度: 92", 1.0)
case("fact 未纠正前提", "factual", FP, "因为地球的引力适中，所以能留住卫星。\n置信度: 70", 0.0)

# ---- tools ----
def TL(calls, tools=None):
    return {"id": "t", "dim": "tools",
            "tools": tools or [{"name": c["name"]} for c in calls],
            "gold": {"type": "calls", "calls": calls}}

TN = {"id": "t", "dim": "tools",
      "tools": [{"name": "get_weather"}],
      "gold": {"type": "no_call"}}

case("tool JSON 数组正确", "tools", TL([{"name": "get_weather", "args": {"city": "北京"}}]),
     '[{"name": "get_weather", "arguments": {"city": "北京"}}]', 1.0)
case("tool OpenAI 单对象", "tools", TL([{"name": "get_weather", "args": {"city": "北京"}}]),
     '{"name": "get_weather", "arguments": {"city": "北京"}}', 1.0)
case("tool 参数错", "tools", TL([{"name": "get_weather", "args": {"city": "北京"}}]),
     '[{"name": "get_weather", "arguments": {"city": "上海"}}]', 0.0)
case("tool 多编造参数", "tools", TL([{"name": "get_weather", "args": {"city": "北京"}}]),
     '[{"name": "get_weather", "arguments": {"city": "北京", "date": "明天"}}]', 0.0)
case("tool 调用不存在工具", "tools", TL([{"name": "get_weather", "args": {"city": "北京"}}]),
     '[{"name": "book_flight", "arguments": {"city": "北京"}}]', 0.0)
case("tool 数量不足", "tools", TL([{"name": "get_weather", "args": {"city": "上海"}},
                                   {"name": "get_weather", "args": {"city": "广州"}}]),
     '[{"name": "get_weather", "arguments": {"city": "上海"}}]', 0.0)
case("tool 并行两个", "tools", TL([{"name": "get_weather", "args": {"city": "上海"}},
                                   {"name": "get_weather", "args": {"city": "广州"}}]),
     '[{"name":"get_weather","arguments":{"city":"上海"}},{"name":"get_weather","arguments":{"city":"广州"}}]',
     1.0)
case("tool 顺序无关", "tools", TL([{"name": "get_weather", "args": {"city": "上海"}},
                                   {"name": "get_weather", "args": {"city": "广州"}}]),
     '[{"name":"get_weather","arguments":{"city":"广州"}},{"name":"get_weather","arguments":{"city":"上海"}}]',
     1.0)
case("tool 数值字符串等价", "tools", TL([{"name": "calc", "args": {"v": 25}}]),
     '[{"name":"calc","arguments":{"v":"25"}}]', 1.0)
case("tool 应拒调却调用", "tools", TN,
     '[{"name": "get_weather", "arguments": {"city": "北京"}}]', 0.0)
case("tool 应拒调正确未调", "tools", TN,
     "没有可用的翻译工具，无法完成这个任务。", 1.0)
case("tool Python 调用语法", "tools", TL([{"name": "read_file", "args": {"path": "a.txt"}}]),
     "read_file(path='a.txt')", 1.0)
case("tool 松散字段允许多余键", "tools",
     {"id": "t", "dim": "tools",
      "tools": [{"name": "send_email"}],
      "gold": {"type": "calls", "calls": [
          {"name": "send_email", "strict": False,
           "args": {"to": "a@b.com", "subject": "主题"}}]}},
     '[{"name":"send_email","arguments":{"to":"a@b.com","subject":"主题","body":"正文"}}]', 1.0)
case("tool 松散字段仍校验值", "tools",
     {"id": "t", "dim": "tools",
      "tools": [{"name": "send_email"}],
      "gold": {"type": "calls", "calls": [
          {"name": "send_email", "strict": False,
           "args": {"to": "a@b.com", "subject": "主题"}}]}},
     '[{"name":"send_email","arguments":{"to":"c@d.com","subject":"主题","body":"正文"}}]', 0.0)


def main() -> int:
    failures = []
    for c in CASES:
        res = scorers.score_task(c["task"], c["response"])
        ok = abs(res["score"] - c["expect_score"]) < 1e-9
        verdict = (res.get("detail") or {}).get("verdict")
        if c["expect_verdict"] and verdict != c["expect_verdict"]:
            ok = False
        status = "PASS" if ok else "FAIL"
        if not ok:
            failures.append((c, res))
        print(f"[{status}] {c['name']}: got {res['score']} ({res['reason'][:70]})")
    total = len(CASES)
    print(f"\n{total - len(failures)}/{total} 通过")
    if failures:
        print("\n失败明细：", file=sys.stderr)
        for c, res in failures:
            print(f"  - {c['name']}: 期望 {c['expect_score']}，实得 {res['score']}，理由 {res['reason']}",
                  file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
