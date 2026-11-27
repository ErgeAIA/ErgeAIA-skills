#!/usr/bin/env python3
"""两个评测结果的配对比较。

本地模型场景里，「这个模型行不行」几乎无法回答，「换它值不值」才有决策意义。
所以比较必须逐题配对，而不是比两个均值——均值差会把不同题目上的胜负抵消掉。
"""

from __future__ import annotations

import json
import os
from math import comb


def load_scores(run_dir: str) -> dict[str, dict]:
    path = os.path.join(run_dir, "scores.jsonl")
    if not os.path.exists(path):
        raise RuntimeError(f"缺少 {path}")
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rec = json.loads(line)
                out[rec["id"]] = rec
    return out


def mcnemar_exact(b: int, c: int) -> float:
    """精确 McNemar（二项检验）。b/c 是「只 A 对」「只 B 对」的题数。"""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    # 双尾精确二项 p
    tail = sum(comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def compare(dir_a: str, dir_b: str, label_a: str, label_b: str) -> dict:
    a = load_scores(dir_a)
    b = load_scores(dir_b)
    common = sorted(set(a) & set(b))
    if not common:
        raise RuntimeError("两组结果没有共同题目，无法配对比较")

    wins_a = wins_b = ties = 0
    rows = []
    by_dim: dict[str, dict] = {}
    for tid in common:
        sa = a[tid]["score"]
        sb = b[tid]["score"]
        dim = a[tid]["dim"]
        d = by_dim.setdefault(dim, {"a": 0, "b": 0, "tie": 0, "n": 0})
        d["n"] += 1
        if sa > sb:
            wins_a += 1
            d["a"] += 1
            verdict = "a"
        elif sb > sa:
            wins_b += 1
            d["b"] += 1
            verdict = "b"
        else:
            ties += 1
            d["tie"] += 1
            verdict = "tie"
        rows.append({"id": tid, "dim": dim, "a": sa, "b": sb, "verdict": verdict,
                     "reason_a": a[tid].get("reason", ""),
                     "reason_b": b[tid].get("reason", "")})

    p = mcnemar_exact(wins_a, wins_b)
    return {
        "label_a": label_a,
        "label_b": label_b,
        "n_common": len(common),
        "wins_a": wins_a,
        "wins_b": wins_b,
        "ties": ties,
        "mcnemar_p": round(p, 4),
        "significant": p < 0.05,
        "by_dim": by_dim,
        "rows": rows,
        "mean_a": round(sum(a[t]["score"] for t in common) / len(common), 4),
        "mean_b": round(sum(b[t]["score"] for t in common) / len(common), 4),
        "only_in_a": sorted(set(a) - set(b)),
        "only_in_b": sorted(set(b) - set(a)),
    }


def render_text(result: dict) -> str:
    lines = []
    lines.append(f"配对比较：{result['label_a']} vs {result['label_b']}")
    lines.append(f"共同题目 {result['n_common']} 道")
    lines.append(f"均值：A={result['mean_a']:.3f}  B={result['mean_b']:.3f}")
    lines.append("")
    lines.append(f"A 胜 {result['wins_a']} / B 胜 {result['wins_b']} / 平 {result['ties']}")
    lines.append(f"McNemar 精确检验 p = {result['mcnemar_p']} "
                 f"({'差异显著' if result['significant'] else '差异不显著'})")
    lines.append("")
    lines.append("按维度：")
    for dim, d in result["by_dim"].items():
        lines.append(f"  {dim:9s} n={d['n']:3d}  A胜={d['a']:3d}  B胜={d['b']:3d}  平={d['tie']:3d}")
    if result["only_in_a"]:
        lines.append(f"\n仅 A 有：{result['only_in_a']}")
    if result["only_in_b"]:
        lines.append(f"仅 B 有：{result['only_in_b']}")
    return "\n".join(lines)
