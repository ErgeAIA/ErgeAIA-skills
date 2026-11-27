#!/usr/bin/env python3
"""local-model-eval 判分器。纯标准库、无网络、无第三方依赖。

四维判分全部程序化，不引入 LLM 裁判：

- math      数值抽取 + 容差比较（含「信息不足」陷阱判定）
- ifollow   可验证约束逐条判定，给部分得分 + 全通过率
- factual   三分类（答对 / 答错 / 弃答）+ 置信度校准（ECE）
- tools     调用解析 + 结构化比对（含无关请求的「拒调」判定）

每个判分函数都返回 (score, reason, detail) 三元组，reason 会写进
scores.jsonl，是报告下钻时给人看的判分理由，也是判分器 debug 的唯一依据。
"""

from __future__ import annotations

import json
import math
import re

# ---------------------------------------------------------------------------
# 文本工具
# ---------------------------------------------------------------------------

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
LATIN_RE = re.compile(r"[A-Za-z]")
FENCE_RE = re.compile(r"```(?:json|JSON)?\s*\n?(.*?)```", re.S)

ABSTAIN_RE = re.compile(
    r"无法(确定|确认|回答|判断|核实|得知|给出|提供|获取|查到)"
    r"|没有(可靠|足够|相关|公开|权威)的?(信息|资料|数据|来源|记录)"
    r"|不在(我的)?(知识|训练|能力)(范围|库)?"
    r"|不清楚|不得而知|无从得知|无从查证|不掌握|未收录|尚无(定论|公开|记录)"
    r"|不存在|并无此|查无|未公开|不予公开"
    r"|不知道|不能确定|无法作答|信息不足|缺少(必要)?信息"
    r"|i\s*(?:do\s*n[o']?t|don't)\s*know|not\s+sure|cannot\s+be\s+(determined|verified)"
    r"|insufficient\s+information|there\s+is\s+no\s+such|does\s+not\s+exist|fictional",
    re.I,
)


def strip_fences(text: str) -> str:
    """剥掉 markdown 代码围栏，只留内容。"""
    m = FENCE_RE.search(text)
    if m:
        return m.group(1).strip()
    return text.strip()


def norm_text(s: str) -> str:
    """归一化用于别名比对：去空白、标点、大小写。"""
    s = s.lower()
    s = re.sub(r"[\s，。、,.!?！？:：;；\"'“”‘’()（）\[\]【】<>《》/\\|~`*_\-]", "", s)
    return s


def count_chars(text: str) -> int:
    """计「字」：去空白后的字符数（中英统一口径）。"""
    return len(re.sub(r"\s+", "", text))


def count_words(text: str) -> int:
    """计「词」：按空白切分。"""
    return len(text.split())


def split_sentences(text: str) -> list[str]:
    return [s for s in re.split(r"[。！？!?]+", text) if s.strip()]


def split_paragraphs(text: str) -> list[str]:
    return [p for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]


def count_bullets(text: str) -> int:
    n = 0
    for line in text.splitlines():
        if re.match(r"^\s*(?:[-*•]|\d+[.)])\s+\S", line):
            n += 1
    return n


def _positional_numbers(text: str) -> list[tuple[int, float]]:
    """按出现位置返回 [(start, value)]。分数先匹配并遮罩，避免 1/6 被拆成 1 和 6。"""
    found: list[tuple[int, float]] = []
    covered: list[tuple[int, int]] = []
    for m in re.finditer(r"(-?\d+)\s*/\s*(\d+)", text):
        try:
            den = float(m.group(2))
            if den:
                found.append((m.start(), float(m.group(1)) / den))
                covered.append((m.start(), m.end()))
        except ValueError:
            continue
    for m in re.finditer(r"-?\d[\d,]*\.?\d*", text):
        if any(a <= m.start() < b for a, b in covered):
            continue
        try:
            found.append((m.start(), float(m.group(0).replace(",", ""))))
        except ValueError:
            continue
    found.sort(key=lambda x: x[0])
    return found


def extract_numbers(text: str) -> list[float]:
    """抽取所有数值，支持千分位、负号、小数、分数。"""
    return [v for _, v in _positional_numbers(text)]


CONCLUSION_RE = re.compile(
    r"所以|因此|故|答案|应为|等于|合计|总计|总共|共|需要|得到|结果|应是|即"
)


def final_number(text: str) -> float | None:
    """取模型给出的最终数值。优先级：#### / boxed / 结论标记后的数值 / 末尾数值。"""
    m = re.search(r"####\s*(-?[\d,]+\.?\d*)", text)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            pass
    m = re.search(r"\\boxed\{\s*(-?[\d,]+\.?\d*)\s*\}", text)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            pass

    nums = _positional_numbers(text)
    if not nums:
        return None

    markers = [mm.start() for mm in CONCLUSION_RE.finditer(text)]
    if markers:
        after = [v for pos, v in nums if pos > markers[-1]]
        if after:
            return after[-1]
    return nums[-1][1]


def looks_abstain(text: str) -> bool:
    return bool(ABSTAIN_RE.search(text))


# ---------------------------------------------------------------------------
# 1. 数学推理
# ---------------------------------------------------------------------------

def score_math(task: dict, response: str) -> tuple[float, str, dict]:
    gold = task["gold"]
    gtype = gold.get("type", "number")

    if gtype == "insufficient":
        if looks_abstain(response):
            return 1.0, "识别出信息不足并拒答", {"kind": "insufficient", "abstained": True}
        return 0.0, "题目信息不足，模型仍给出具体数值（编造）", {"kind": "insufficient", "abstained": False}

    got = final_number(response)
    if got is None:
        return 0.0, "响应中抽不到任何数值", {"kind": "number", "extracted": None}

    want = float(gold["value"])
    tol = float(gold.get("tolerance", 1e-6))
    if math.isclose(got, want, rel_tol=tol, abs_tol=tol):
        return 1.0, f"数值匹配：{got:g}", {"kind": "number", "extracted": got, "expected": want}
    return 0.0, f"数值不符：抽到 {got:g}，应为 {want:g}", {"kind": "number", "extracted": got, "expected": want}


# ---------------------------------------------------------------------------
# 2. 指令遵循（可验证约束）
# ---------------------------------------------------------------------------

def _check_constraint(text: str, c: dict) -> tuple[bool, str]:
    kind = c["kind"]
    v = c.get("value")

    if kind == "max_chars":
        n = count_chars(text)
        return n <= int(v), f"{n}/{v} 字"
    if kind == "min_chars":
        n = count_chars(text)
        return n >= int(v), f"{n}/{v} 字"
    if kind == "max_words":
        n = count_words(text)
        return n <= int(v), f"{n}/{v} 词"
    if kind == "sentences_eq":
        n = len(split_sentences(text))
        return n == int(v), f"{n}/{v} 句"
    if kind == "paragraphs_eq":
        n = len(split_paragraphs(text))
        return n == int(v), f"{n}/{v} 段"
    if kind == "bullets_eq":
        n = count_bullets(text)
        return n == int(v), f"{n}/{v} 条"
    if kind == "lines_eq":
        n = len([ln for ln in text.strip().splitlines() if ln.strip()])
        return n == int(v), f"{n}/{v} 行"
    if kind == "each_line_chars":
        lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
        bad = [ln for ln in lines if count_chars(ln) != int(v)]
        return (not bad and bool(lines)), f"{len(bad)} 行字数不等于 {v}"
    if kind == "contains_all":
        missing = [w for w in v if w not in text]
        return not missing, f"缺 {missing}" if missing else "全部包含"
    if kind == "contains_none":
        hit = [w for w in v if w in text]
        return not hit, f"出现了禁词 {hit}" if hit else "无禁词"
    if kind == "starts_with":
        return text.strip().startswith(v), f"开头={'是' if text.strip().startswith(v) else '否'}"
    if kind == "ends_with":
        return text.strip().endswith(v), f"结尾={'是' if text.strip().endswith(v) else '否'}"
    if kind == "no_cjk":
        return not CJK_RE.search(text), "含中文" if CJK_RE.search(text) else "无中文"
    if kind == "no_latin":
        return not LATIN_RE.search(text), "含字母" if LATIN_RE.search(text) else "无字母"
    if kind == "no_digits":
        return not re.search(r"\d", text), "含数字" if re.search(r"\d", text) else "无数字"
    if kind == "all_upper":
        letters = "".join(LATIN_RE.findall(text))
        return bool(letters) and letters.isupper(), f"字母串={letters[:24]}"
    if kind == "only_number":
        core = strip_fences(text).strip().strip("。.，,")
        return bool(re.fullmatch(r"-?\d+(?:\.\d+)?", core)), f"内容={core[:24]}"
    if kind == "equals_number":
        got = final_number(strip_fences(text))
        ok = got is not None and math.isclose(got, float(v), rel_tol=1e-6, abs_tol=1e-6)
        return ok, f"抽到 {got}"
    if kind == "json_object":
        try:
            obj = json.loads(strip_fences(text))
        except Exception as exc:  # noqa: BLE001
            return False, f"JSON 解析失败：{type(exc).__name__}"
        if not isinstance(obj, dict):
            return False, "不是对象"
        missing = [k for k in v if k not in obj]
        return not missing, f"缺键 {missing}" if missing else "键齐全"
    if kind == "json_array_ints":
        try:
            arr = json.loads(strip_fences(text))
        except Exception as exc:  # noqa: BLE001
            return False, f"JSON 解析失败：{type(exc).__name__}"
        if not isinstance(arr, list):
            return False, "不是数组"
        if len(arr) != int(v):
            return False, f"长度 {len(arr)}/{v}"
        if not all(isinstance(x, int) and not isinstance(x, bool) for x in arr):
            return False, "元素非整数"
        return arr == sorted(arr), "已升序" if arr == sorted(arr) else "未升序"
    return False, f"未知约束类型 {kind}"


def score_ifollow(task: dict, response: str) -> tuple[float, str, dict]:
    checks = task["gold"]["checks"]
    results = []
    for c in checks:
        ok, detail = _check_constraint(response, c)
        results.append({"kind": c["kind"], "value": c.get("value"), "ok": ok, "detail": detail})
    passed = sum(1 for r in results if r["ok"])
    total = len(results)
    score = passed / total if total else 0.0
    failed = [f"{r['kind']}({r['detail']})" for r in results if not r["ok"]]
    reason = f"{passed}/{total} 条约束通过" + ("；未过：" + "，".join(failed) if failed else "")
    return score, reason, {"checks": results, "all_pass": passed == total}


# ---------------------------------------------------------------------------
# 3. 事实性与幻觉（三分类 + 校准）
# ---------------------------------------------------------------------------

def _alias_hit(text: str, aliases: list[str]) -> bool:
    body = norm_text(text)
    for a in aliases:
        na = norm_text(a)
        if not na:
            continue
        if na in body:
            return True
        if re.fullmatch(r"-?\d+(?:\.\d+)?", na):
            for n in extract_numbers(text):
                if math.isclose(n, float(na), rel_tol=1e-4, abs_tol=1e-4):
                    return True
    return False


def parse_confidence(text: str) -> float | None:
    """取模型自报置信度（0-100 或 0-1），转成 0-1。"""
    m = re.search(r"置信度\s*[:：]?\s*(\d{1,3}(?:\.\d+)?)\s*%?", text)
    if not m:
        m = re.search(r"confidence\s*[:：]?\s*(\d{1,3}(?:\.\d+)?)\s*%?", text, re.I)
    if not m:
        return None
    try:
        v = float(m.group(1))
    except ValueError:
        return None
    if v > 1.0:
        v = v / 100.0
    return max(0.0, min(1.0, v))


def score_factual(task: dict, response: str) -> tuple[float, str, dict]:
    gold = task["gold"]
    kind = gold.get("type", "answer")
    abstained = looks_abstain(response)
    conf = parse_confidence(response)

    if kind == "unanswerable":
        if abstained:
            return 1.0, "不可回答问题，模型正确弃答", {
                "verdict": "abstain_correct", "abstained": True, "confidence": conf}
        return 0.0, "不可回答问题，模型仍给出具体答案（幻觉）", {
            "verdict": "hallucinated", "abstained": False, "confidence": conf}

    if kind == "premise":
        ok = _alias_hit(response, gold["aliases"])
        return (1.0 if ok else 0.0), (
            "指出前提错误并给出正确事实" if ok else "未纠正错误前提"
        ), {"verdict": "premise_ok" if ok else "premise_missed",
            "abstained": abstained, "confidence": conf}

    # kind == "answer"：先看有没有命中答案，命中即正确。
    # 弃答词只用于「没命中」时区分「过度保守」与「答错」——否则
    # 「巴黎是法国首都，这不存在争议」会被误判成弃答。
    if _alias_hit(response, gold["aliases"]):
        return 1.0, "答案命中", {
            "verdict": "correct", "abstained": False, "confidence": conf}
    if abstained:
        return 0.0, "可回答问题，模型过度弃答", {
            "verdict": "over_abstain", "abstained": True, "confidence": conf}
    return 0.0, "答案未命中标准答案（错误）", {
        "verdict": "incorrect", "abstained": False, "confidence": conf}


def expected_calibration_error(pairs: list[tuple[float, float]], bins: int = 5) -> float | None:
    """pairs = [(confidence, hit01)]；返回 ECE，样本不足返回 None。"""
    if len(pairs) < bins:
        return None
    buckets: list[list[tuple[float, float]]] = [[] for _ in range(bins)]
    for conf, hit in pairs:
        idx = min(bins - 1, int(conf * bins))
        buckets[idx].append((conf, hit))
    ece = 0.0
    n = len(pairs)
    for b in buckets:
        if not b:
            continue
        avg_conf = sum(c for c, _ in b) / len(b)
        avg_hit = sum(h for _, h in b) / len(b)
        ece += (len(b) / n) * abs(avg_conf - avg_hit)
    return ece


# ---------------------------------------------------------------------------
# 4. 工具调用
# ---------------------------------------------------------------------------

def _balanced_json_chunks(text: str) -> list[str]:
    """从任意文本中捞出平衡的 JSON 片段。"""
    chunks = []
    depth = 0
    start = -1
    in_str = False
    esc = False
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch in "{[":
            if depth == 0:
                start = i
            depth += 1
        elif ch in "}]":
            if depth:
                depth -= 1
                if depth == 0 and start >= 0:
                    chunks.append(text[start:i + 1])
                    start = -1
    return chunks


PY_CALL_RE = re.compile(
    r"([A-Za-z_][A-Za-z0-9_]*)\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)"
)


def _coerce_args(pairs: list[tuple[str, object]]) -> dict:
    return {k: v for k, v in pairs}


def _parse_py_args(argstr: str) -> dict | None:
    """解析 name(a=1, b="x") 里的参数。失败返回 None。"""
    if not argstr.strip():
        return {}
    args: dict = {}
    # 按顶层逗号切
    parts = []
    buf = ""
    depth = 0
    in_str = False
    quote = ""
    for ch in argstr:
        if in_str:
            buf += ch
            if ch == quote:
                in_str = False
            continue
        if ch in "\"'":
            in_str = True
            quote = ch
            buf += ch
        elif ch in "([{":
            depth += 1
            buf += ch
        elif ch in ")]}":
            depth -= 1
            buf += ch
        elif ch == "," and depth == 0:
            parts.append(buf)
            buf = ""
        else:
            buf += ch
    if buf.strip():
        parts.append(buf)
    for p in parts:
        if "=" not in p:
            return None
        k, _, raw = p.partition("=")
        k = k.strip().strip("\"'")
        raw = raw.strip()
        try:
            args[k] = json.loads(raw)
        except Exception:  # noqa: BLE001
            if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
                args[k] = raw[1:-1]
            else:
                args[k] = raw
    return args


def parse_calls(text: str) -> tuple[list[dict], list[str]]:
    """解析模型输出里的工具调用。返回 (calls, notes)。

    支持三种形态：OpenAI 风格 JSON（含 <tool_call> 包裹）、JSON 数组、
    BFCL 风格的 Python 调用语法 name(arg=val)。
    """
    notes: list[str] = []
    body = strip_fences(text)

    # 形态 1/2：JSON
    for chunk in _balanced_json_chunks(body):
        try:
            obj = json.loads(chunk)
        except Exception:  # noqa: BLE001
            continue
        items = obj if isinstance(obj, list) else [obj]
        calls = []
        for it in items:
            if not isinstance(it, dict):
                calls = []
                break
            name = it.get("name") or (it.get("function") or {}).get("name")
            raw_args = it.get("arguments", it.get("parameters", (it.get("function") or {}).get("arguments")))
            if not name:
                calls = []
                break
            if isinstance(raw_args, str):
                try:
                    raw_args = json.loads(raw_args)
                except Exception:  # noqa: BLE001
                    raw_args = {}
            calls.append({"name": name, "args": raw_args or {}})
        if calls:
            notes.append("json")
            return calls, notes

    # 形态 3：Python 调用
    calls = []
    for m in PY_CALL_RE.finditer(body):
        name = m.group(1)
        if name in {"print", "len", "range", "str", "int", "float", "list", "dict", "json"}:
            continue
        args = _parse_py_args(m.group(2))
        if args is None:
            continue
        calls.append({"name": name, "args": args})
    if calls:
        notes.append("pycall")
        return calls, notes

    notes.append("none")
    return [], notes


def _norm_arg(v) -> tuple[str, object]:
    if isinstance(v, bool):
        return ("bool", v)
    if isinstance(v, (int, float)):
        return ("num", round(float(v), 6))
    if isinstance(v, str):
        s = v.strip()
        try:
            return ("num", round(float(s), 6))
        except ValueError:
            return ("str", s.lower().replace(" ", ""))
    return ("json", json.dumps(v, sort_keys=True, ensure_ascii=False))


def _args_match(pred: dict, gold: dict, strict: bool = True) -> tuple[bool, list[str]]:
    """strict=True：键集必须完全相等，pred 多余键视为幻觉参数。
    strict=False：只要求 gold 的键都在 pred 里且值等价，多余键不罚（用于正文类自由字段）。
    """
    problems = []
    if strict and set(pred) != set(gold):
        extra = set(pred) - set(gold)
        miss = set(gold) - set(pred)
        if miss:
            problems.append(f"缺参数 {sorted(miss)}")
        if extra:
            problems.append(f"多参数 {sorted(extra)}")
        return False, problems
    if not strict:
        miss = set(gold) - set(pred)
        if miss:
            return False, [f"缺参数 {sorted(miss)}"]
    for k, gv in gold.items():
        if _norm_arg(pred[k]) != _norm_arg(gv):
            problems.append(f"{k}={pred[k]!r} 应为 {gv!r}")
    return not problems, problems


def score_tools(task: dict, response: str) -> tuple[float, str, dict]:
    gold = task["gold"]
    calls, notes = parse_calls(response)

    if gold.get("type") == "no_call":
        if not calls:
            return 1.0, "无匹配工具时正确未发起调用", {"verdict": "no_call_ok", "calls": []}
        return 0.0, f"无匹配工具却发起了调用：{[c['name'] for c in calls]}", {
            "verdict": "spurious_call", "calls": calls}

    gold_calls = gold["calls"]
    known = {t["name"] for t in task.get("tools", [])}
    unknown = [c["name"] for c in calls if c["name"] not in known]
    if unknown:
        return 0.0, f"调用了不存在的工具：{unknown}", {
            "verdict": "unknown_tool", "calls": calls, "unknown": unknown}

    if len(calls) != len(gold_calls):
        return 0.0, f"调用数量 {len(calls)}/{len(gold_calls)}", {
            "verdict": "count_mismatch", "calls": calls}

    remaining = list(calls)
    matched = 0
    problems_all: list[str] = []
    for gc in gold_calls:
        strict = gc.get("strict", True)
        hit = None
        for pc in remaining:
            if pc["name"] != gc["name"]:
                continue
            ok, problems = _args_match(pc["args"], gc["args"], strict=strict)
            if ok:
                hit = pc
                break
            problems_all.extend([f"{gc['name']}: {p}" for p in problems])
        if hit is None:
            return 0.0, "未匹配到标准调用；" + "；".join(problems_all[:3]), {
                "verdict": "arg_mismatch", "calls": calls, "problems": problems_all}
        remaining.remove(hit)
        matched += 1

    return 1.0, f"{matched} 个调用全部匹配", {
        "verdict": "correct", "calls": calls, "matched": matched}


# ---------------------------------------------------------------------------
# 分发
# ---------------------------------------------------------------------------

SCORERS = {
    "math": score_math,
    "ifollow": score_ifollow,
    "factual": score_factual,
    "tools": score_tools,
}

DIM_LABELS = {
    "math": "数学推理",
    "ifollow": "指令遵循",
    "factual": "事实性与幻觉",
    "tools": "工具调用",
}


def score_task(task: dict, response: str) -> dict:
    fn = SCORERS.get(task["dim"])
    if fn is None:
        return {"id": task["id"], "dim": task["dim"], "score": 0.0,
                "reason": f"未知维度 {task['dim']}", "detail": {}, "error": True}
    score, reason, detail = fn(task, response)
    return {"id": task["id"], "dim": task["dim"], "score": round(score, 4),
            "reason": reason, "detail": detail, "error": False}
