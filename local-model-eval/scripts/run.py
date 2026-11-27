#!/usr/bin/env python3
"""评测运行器：把题库跑成本地模型的原始响应，再交给判分器。

设计要点：
- 每条请求立刻落盘（raw.jsonl），中断可续跑，不丢已花的算力
- 原始响应是唯一事实源，分数只是它的派生视图
- 默认 temperature=0 + 固定 seed，并记录 seed，便于复现核对
- 只依赖标准库 urllib，不需要 openai SDK
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import scorers  # noqa: E402

DIMS = ["math", "ifollow", "factual", "tools"]


# ---------------------------------------------------------------------------
# 题库
# ---------------------------------------------------------------------------

def load_tasks(tasks_dir: str, dims: list[str] | None = None) -> list[dict]:
    out: list[dict] = []
    wanted = dims or DIMS
    for dim in wanted:
        path = os.path.join(tasks_dir, f"{dim}.jsonl")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
    return out


def build_messages(task: dict) -> list[dict]:
    """按维度拼消息。工具维度把工具清单写进 system，避免依赖各家 function calling 差异。"""
    if task["dim"] == "tools":
        tools_json = json.dumps(task.get("tools", []), ensure_ascii=False, indent=2)
        system = (
            "你可以使用下列工具。若任务需要调用工具，只输出一个 JSON 数组，"
            "每个元素形如 {\"name\": \"工具名\", \"arguments\": {...}}，不要输出其他文字。"
            "若没有任何可用工具能完成任务，直接说明无法完成，不要编造调用。\n"
            f"可用工具：\n{tools_json}"
        )
        return [{"role": "system", "content": system},
                {"role": "user", "content": task["prompt"]}]
    return [{"role": "user", "content": task["prompt"]}]


def prompt_sha(messages: list[dict]) -> str:
    blob = json.dumps(messages, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def chat(base_url: str, messages: list[dict], model: str, seed: int,
         temperature: float, max_tokens: int, timeout: float) -> dict:
    base = base_url.rstrip("/")
    url = f"{base}/chat/completions" if base.endswith("/v1") else f"{base}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "seed": seed,
        "max_tokens": max_tokens,
        "stream": False,
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
            status = resp.status
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        status = exc.code
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "status": 0, "error": f"{type(exc).__name__}: {exc}",
                "latency_ms": int((time.time() - started) * 1000)}
    latency = int((time.time() - started) * 1000)
    if status != 200:
        return {"ok": False, "status": status, "error": body[:500], "latency_ms": latency}
    try:
        obj = json.loads(body)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "status": status, "error": f"JSON 解析失败 {exc}", "latency_ms": latency}
    choice = (obj.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    content = msg.get("content") or ""
    reasoning = msg.get("reasoning_content") or ""
    usage = obj.get("usage") or {}
    return {
        "ok": True,
        "status": status,
        "content": content,
        "reasoning_content": reasoning,
        "finish_reason": choice.get("finish_reason"),
        "usage": usage,
        "latency_ms": latency,
    }


# ---------------------------------------------------------------------------
# 统计
# ---------------------------------------------------------------------------

def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """二项比例的 Wilson 区间。n 小时比正态近似可靠。"""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def mean_ci(values: list[float]) -> tuple[float, float, float]:
    """均值的 bootstrap 区间（百分位法，固定种子）。"""
    import random
    if not values:
        return (0.0, 0.0, 0.0)
    m = sum(values) / len(values)
    if len(values) < 5:
        return (m, m, m)
    rng = random.Random(20260101)
    boots = []
    for _ in range(2000):
        sample = [values[rng.randrange(len(values))] for _ in values]
        boots.append(sum(sample) / len(sample))
    boots.sort()
    lo = boots[int(0.025 * len(boots))]
    hi = boots[int(0.975 * len(boots)) - 1]
    return (m, lo, hi)


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def run(base_url: str, tasks_dir: str, out_dir: str, model: str, seed: int,
        temperature: float, max_tokens: int, timeout: float,
        dims: list[str] | None, resume: bool, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    raw_path = os.path.join(out_dir, "raw.jsonl")
    score_path = os.path.join(out_dir, "scores.jsonl")
    summary_path = os.path.join(out_dir, "summary.json")
    manifest_path = os.path.join(out_dir, "manifest.json")

    tasks = load_tasks(tasks_dir, dims)
    if not tasks:
        raise RuntimeError(f"{tasks_dir} 下没有找到题目（期望 math/ifollow/factual/tools.jsonl）")

    done: set[str] = set()
    if resume and os.path.exists(raw_path):
        with open(raw_path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except Exception:  # noqa: BLE001
                    continue
                if rec.get("ok"):
                    done.add(rec["id"])

    manifest = {
        "base_url": base_url,
        "model": model,
        "seed": seed,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "task_count": len(tasks),
        "dims": sorted({t["dim"] for t in tasks}),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "tool_version": "0.1.1",
    }

    with open(raw_path, "a", encoding="utf-8") as raw_fh:
        for i, task in enumerate(tasks, 1):
            if task["id"] in done:
                continue
            messages = build_messages(task)
            res = chat(base_url, messages, model, seed, temperature, max_tokens, timeout)
            rec = {
                "id": task["id"],
                "dim": task["dim"],
                "prompt": task["prompt"],
                "prompt_sha256": prompt_sha(messages),
                "seed": seed,
                "temperature": temperature,
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                **res,
            }
            raw_fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            raw_fh.flush()
            if verbose:
                flag = "OK " if res.get("ok") else "ERR"
                print(f"[{i}/{len(tasks)}] {flag} {task['id']} {res.get('latency_ms', 0)}ms",
                      file=sys.stderr)

    # 判分
    scored = []
    with open(raw_path, encoding="utf-8") as raw_fh, \
            open(score_path, "w", encoding="utf-8") as sc_fh:
        for line in raw_fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            task = next((t for t in tasks if t["id"] == rec["id"]), None)
            if task is None:
                continue
            if not rec.get("ok"):
                result = {"id": rec["id"], "dim": rec["dim"], "score": 0.0,
                          "reason": f"请求失败：{rec.get('error', '')[:160]}",
                          "detail": {"verdict": "request_failed"}, "error": True}
            else:
                result = scorers.score_task(task, rec.get("content", ""))
            merged = {**result, "prompt_sha256": rec.get("prompt_sha256"),
                      "latency_ms": rec.get("latency_ms"),
                      "usage": rec.get("usage", {})}
            sc_fh.write(json.dumps(merged, ensure_ascii=False) + "\n")
            scored.append(merged)

    summary = summarize(scored, tasks)
    summary["manifest"] = manifest
    manifest["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    manifest["raw_sha256"] = _file_sha(raw_path)
    summary["integrity"] = {"raw_sha256": manifest["raw_sha256"]}

    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    return summary


def _file_sha(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def summarize(scored: list[dict], tasks: list[dict]) -> dict:
    by_dim: dict[str, list[dict]] = {}
    for s in scored:
        by_dim.setdefault(s["dim"], []).append(s)

    dims_out = {}
    for dim in DIMS:
        items = by_dim.get(dim, [])
        if not items:
            continue
        scores = [it["score"] for it in items]
        m, lo, hi = mean_ci(scores)
        n = len(items)
        passed = sum(1 for s in scores if s >= 1.0)
        p_lo, p_hi = wilson(passed, n)
        entry = {
            "n": n,
            "mean": round(m, 4),
            "ci": [round(lo, 4), round(hi, 4)],
            "pass_rate": round(passed / n, 4) if n else 0.0,
            "pass_ci": [round(p_lo, 4), round(p_hi, 4)],
            "errors": sum(1 for it in items if it.get("error")),
            "label": scorers.DIM_LABELS.get(dim, dim),
        }
        if dim == "factual":
            verdicts = {}
            for it in items:
                v = (it.get("detail") or {}).get("verdict", "unknown")
                verdicts[v] = verdicts.get(v, 0) + 1
            entry["verdicts"] = verdicts
            pairs = []
            for it in items:
                d = it.get("detail") or {}
                if d.get("confidence") is not None:
                    hit = 1.0 if it["score"] >= 1.0 else 0.0
                    pairs.append((d["confidence"], hit))
            ece = scorers.expected_calibration_error(pairs)
            entry["ece"] = None if ece is None else round(ece, 4)
            entry["confidence_samples"] = len(pairs)
            halluc = verdicts.get("hallucinated", 0) + verdicts.get("incorrect", 0)
            entry["hallucination_rate"] = round(halluc / n, 4) if n else None
            entry["abstain_rate"] = round(
                (verdicts.get("abstain_correct", 0) + verdicts.get("over_abstain", 0)) / n, 4
            ) if n else None
        if dim == "ifollow":
            entry["all_pass_rate"] = round(
                sum(1 for it in items if (it.get("detail") or {}).get("all_pass")) / n, 4
            ) if n else 0.0
        if dim == "tools":
            verdicts = {}
            for it in items:
                v = (it.get("detail") or {}).get("verdict", "unknown")
                verdicts[v] = verdicts.get(v, 0) + 1
            entry["verdicts"] = verdicts
            entry["spurious_call_rate"] = round(verdicts.get("spurious_call", 0) / n, 4) if n else None
        dims_out[dim] = entry

    total_n = sum(v["n"] for v in dims_out.values())
    overall = (sum(v["mean"] * v["n"] for v in dims_out.values()) / total_n) if total_n else 0.0
    lat = [s["latency_ms"] for s in scored if s.get("latency_ms")]
    tok = []
    for s in scored:
        u = s.get("usage") or {}
        if u.get("completion_tokens") and s.get("latency_ms"):
            tok.append(u["completion_tokens"] / (s["latency_ms"] / 1000.0))

    return {
        "overall": round(overall, 4),
        "n": total_n,
        "dims": dims_out,
        "cost": {
            "latency_ms_mean": round(sum(lat) / len(lat), 1) if lat else None,
            "latency_ms_p95": sorted(lat)[int(0.95 * len(lat)) - 1] if len(lat) >= 20 else (
                max(lat) if lat else None),
            "tokens_per_sec_mean": round(sum(tok) / len(tok), 2) if tok else None,
        },
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
