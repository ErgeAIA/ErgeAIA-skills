#!/usr/bin/env python3
"""人工复判：抽题导出 → 人打分 → 算人机一致率。

这是整套评测的验收闸门之一。没有它，就永远分不清「模型答错」和「判分器判错」。
一致率不达标的维度必须降级为「参考」，不得进总分。
"""

from __future__ import annotations

import csv
import json
import os
import random

DIMS = ["math", "ifollow", "factual", "tools"]
KAPPA_MIN = 0.85


def export(run_dir: str, out_csv: str, per_dim: int = 8, seed: int = 20260101) -> str:
    scores_path = os.path.join(run_dir, "scores.jsonl")
    raw_path = os.path.join(run_dir, "raw.jsonl")
    if not os.path.exists(scores_path):
        raise RuntimeError(f"缺少 {scores_path}")
    scores = {}
    with open(scores_path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rec = json.loads(line)
                scores[rec["id"]] = rec
    raws = {}
    with open(raw_path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rec = json.loads(line)
                raws[rec["id"]] = rec

    rng = random.Random(seed)
    picked = []
    for dim in DIMS:
        ids = sorted(tid for tid, s in scores.items() if s["dim"] == dim)
        # 分层：一半取满分题、一半取非满分题，避免只抽到同一类
        ok = [i for i in ids if scores[i]["score"] >= 1.0]
        bad = [i for i in ids if scores[i]["score"] < 1.0]
        rng.shuffle(ok)
        rng.shuffle(bad)
        take = ok[: per_dim // 2] + bad[: per_dim - per_dim // 2]
        picked.extend(take)

    os.makedirs(os.path.dirname(os.path.abspath(out_csv)), exist_ok=True)
    with open(out_csv, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "dim", "prompt", "response", "auto_score", "auto_reason",
                    "manual_pass_0or1", "note"])
        for tid in picked:
            s = scores[tid]
            r = raws.get(tid, {})
            w.writerow([
                tid, s["dim"], r.get("prompt", ""), (r.get("content") or "")[:1200],
                s["score"], s.get("reason", ""), "", "",
            ])
    return out_csv


def cohen_kappa(pairs: list[tuple[int, int]]) -> float | None:
    """二分类 kappa。pairs = [(auto_pass, manual_pass)]。"""
    n = len(pairs)
    if n == 0:
        return None
    a = sum(1 for x, _ in pairs if x)
    b = sum(1 for _, y in pairs if y)
    agree = sum(1 for x, y in pairs if x == y)
    po = agree / n
    pe = (a / n) * (b / n) + (1 - a / n) * (1 - b / n)
    if pe >= 1.0:
        return 1.0
    return (po - pe) / (1 - pe)


def agree(csv_path: str) -> dict:
    rows = []
    with open(csv_path, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("manual_pass_0or1", "").strip() == "":
                continue
            try:
                manual = int(row["manual_pass_0or1"].strip())
            except ValueError:
                continue
            auto = 1 if float(row["auto_score"]) >= 1.0 else 0
            rows.append({"id": row["id"], "dim": row["dim"], "auto": auto,
                         "manual": manual, "note": row.get("note", ""),
                         "reason": row.get("auto_reason", ""),
                         "response": (row.get("response") or "")[:400]})

    if not rows:
        raise RuntimeError("CSV 里没有已填写 manual_pass_0or1 的行")

    overall = cohen_kappa([(r["auto"], r["manual"]) for r in rows])
    by_dim: dict[str, dict] = {}
    for dim in DIMS:
        sub = [r for r in rows if r["dim"] == dim]
        if not sub:
            continue
        k = cohen_kappa([(r["auto"], r["manual"]) for r in sub])
        mism = [r for r in sub if r["auto"] != r["manual"]]
        by_dim[dim] = {
            "n": len(sub),
            "kappa": None if k is None else round(k, 4),
            "agree_rate": round(sum(1 for r in sub if r["auto"] == r["manual"]) / len(sub), 4),
            "mismatches": len(mism),
            "grade": "可信" if (k is not None and k >= KAPPA_MIN) else "降级为参考",
        }
    return {
        "n": len(rows),
        "kappa": None if overall is None else round(overall, 4),
        "agree_rate": round(sum(1 for r in rows if r["auto"] == r["manual"]) / len(rows), 4),
        "threshold": KAPPA_MIN,
        "by_dim": by_dim,
        "mismatch_rows": [r for r in rows if r["auto"] != r["manual"]],
    }


def render_text(result: dict) -> str:
    lines = [f"人工复判：{result['n']} 题",
             f"总体 kappa = {result['kappa']}  一致率 = {result['agree_rate']*100:.1f}%"
             f"  （阈值 {result['threshold']}）", ""]
    lines.append("按维度：")
    for dim, d in result["by_dim"].items():
        lines.append(f"  {dim:9s} n={d['n']:2d}  kappa={d['kappa']}  "
                     f"一致率={d['agree_rate']*100:.0f}%  不一致={d['mismatches']}  → {d['grade']}")
    if result["mismatch_rows"]:
        lines.append("")
        lines.append("不一致明细（这些是判分器缺陷候选，应转为回归用例）：")
        for r in result["mismatch_rows"]:
            lines.append(f"  - {r['id']} 自动={r['auto']} 人工={r['manual']}  {r['reason'][:60]}")
    return "\n".join(lines)
