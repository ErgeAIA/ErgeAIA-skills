#!/usr/bin/env python3
"""local-model-eval CLI。

子命令：
  probe     探测本地服务，打印运行时事实
  tasks     列出题库与题目数
  run       跑评测（探测 → 逐题请求 → 判分 → 汇总）
  score     对已有 raw.jsonl 重新判分（判分器改动后重算，不重跑模型）
  report    渲染静态 HTML 报告
  compare   两个结果的配对比较
  selftest  判分器对抗样例自检
  export-recheck  导出人工复判样本
  recheck   计算人机一致率，给出各维度是否可信

退出码：0=PASS / 1=FAIL / 2=ERROR
"""

from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

DEFAULT_TASKS = os.path.join(ROOT, "assets", "tasks")


def cmd_probe(args) -> int:
    import probe
    info = probe.probe(args.base_url)
    print(json.dumps(info, ensure_ascii=False, indent=2))
    if not info["ok"]:
        print("\n探测失败。启动示例：", file=sys.stderr)
        print(f"  {probe.START_HINTS['llama.cpp']}", file=sys.stderr)
        return 1
    return 0


def cmd_tasks(args) -> int:
    import run
    tasks = run.load_tasks(args.tasks_dir)
    by_dim: dict[str, int] = {}
    for t in tasks:
        by_dim[t["dim"]] = by_dim.get(t["dim"], 0) + 1
    for dim in run.DIMS:
        if dim in by_dim:
            print(f"{dim:9s} {by_dim[dim]:3d} 题")
    print(f"{'合计':9s} {len(tasks):3d} 题")
    return 0


def cmd_run(args) -> int:
    import probe
    import run
    try:
        info = probe.probe_or_fail(args.base_url)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    model = args.model or (info["models"][0] if info["models"] else "local")
    if info["props"]:
        print(f"后端 {info['backend']} · build {info['props'].get('build_info') or '—'}",
              file=sys.stderr)
        if info["props"].get("chat_template_present") is False:
            print("警告：未检测到 chat 模板，llama-server 请加 --jinja", file=sys.stderr)

    dims = [d.strip() for d in args.dims.split(",")] if args.dims else None
    try:
        summary = run.run(
            base_url=args.base_url,
            tasks_dir=args.tasks_dir,
            out_dir=args.out,
            model=model,
            seed=args.seed,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            timeout=args.timeout,
            dims=dims,
            resume=not args.no_resume,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(f"\n综合 {summary['overall']*100:.1f}%  （{summary['n']} 题）")
    for dim, d in summary["dims"].items():
        print(f"  {d['label']:8s} {d['mean']*100:5.1f}%  "
              f"CI {d['ci'][0]*100:.1f}–{d['ci'][1]*100:.1f}  n={d['n']}")
    print(f"\n结果目录：{os.path.abspath(args.out)}")

    if not args.no_report:
        import report
        path = report.build(args.out, args.title)
        print(f"报告：{path}")
    return 0


def cmd_score(args) -> int:
    """只重算分数，不重跑模型。判分器改过之后用这个。"""
    import run
    import scorers
    raw_path = os.path.join(args.out, "raw.jsonl")
    if not os.path.exists(raw_path):
        print(f"缺少 {raw_path}", file=sys.stderr)
        return 2
    tasks = run.load_tasks(args.tasks_dir)
    task_by_id = {t["id"]: t for t in tasks}
    scored = []
    with open(raw_path, encoding="utf-8") as raw_fh, \
            open(os.path.join(args.out, "scores.jsonl"), "w", encoding="utf-8") as sc_fh:
        for line in raw_fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            task = task_by_id.get(rec["id"])
            if task is None:
                continue
            if not rec.get("ok"):
                result = {"id": rec["id"], "dim": rec["dim"], "score": 0.0,
                          "reason": f"请求失败：{rec.get('error', '')[:160]}",
                          "detail": {"verdict": "request_failed"}, "error": True}
            else:
                result = scorers.score_task(task, rec.get("content", ""))
            merged = {**result, "prompt_sha256": rec.get("prompt_sha256"),
                      "latency_ms": rec.get("latency_ms"), "usage": rec.get("usage", {})}
            sc_fh.write(json.dumps(merged, ensure_ascii=False) + "\n")
            scored.append(merged)

    summary_path = os.path.join(args.out, "summary.json")
    old = {}
    if os.path.exists(summary_path):
        with open(summary_path, encoding="utf-8") as fh:
            old = json.load(fh)
    summary = run.summarize(scored, tasks)
    summary["manifest"] = old.get("manifest", {})
    summary["integrity"] = old.get("integrity", {})
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)

    print(f"重判完成：综合 {summary['overall']*100:.1f}%（{summary['n']} 题）")
    return 0


def cmd_report(args) -> int:
    import report
    try:
        path = report.build(args.out, args.title, args.output)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"报告：{os.path.abspath(path)}")
    return 0


def cmd_compare(args) -> int:
    import compare
    try:
        result = compare.compare(args.a, args.b, args.label_a, args.label_b)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(compare.render_text(result))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2)
        print(f"\nJSON：{os.path.abspath(args.json)}")
    return 0


def cmd_selftest(args) -> int:
    import selftest
    return selftest.main()


def cmd_export_recheck(args) -> int:
    import recheck
    csv_path = args.csv or os.path.join(args.out, "recheck.csv")
    try:
        path = recheck.export(args.out, csv_path, args.per_dim, args.seed)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"已导出待复判样本：{os.path.abspath(path)}")
    print("填写 manual_pass_0or1 列（1=判对，0=判错）后运行 recheck 子命令。")
    return 0


def cmd_recheck(args) -> int:
    import recheck
    try:
        result = recheck.agree(args.csv)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(recheck.render_text(result))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2)
        print(f"\nJSON：{os.path.abspath(args.json)}")
    # 有维度降级即视为未通过验收
    degraded = [d for d, v in result["by_dim"].items() if v["grade"] != "可信"]
    return 1 if degraded else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="local-model-eval",
        description="本地模型四维能力评测：数学推理 / 指令遵循 / 事实性与幻觉 / 工具调用",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("probe", help="探测本地服务并打印运行时事实")
    sp.add_argument("--base-url", default="http://127.0.0.1:8080/v1")
    sp.set_defaults(func=cmd_probe)

    sp = sub.add_parser("tasks", help="列出题库")
    sp.add_argument("--tasks-dir", default=DEFAULT_TASKS)
    sp.set_defaults(func=cmd_tasks)

    sp = sub.add_parser("run", help="跑评测")
    sp.add_argument("--base-url", default="http://127.0.0.1:8080/v1")
    sp.add_argument("--model", default=None, help="模型标识，缺省取 /v1/models 第一个")
    sp.add_argument("--tasks-dir", default=DEFAULT_TASKS)
    sp.add_argument("--out", default="evals/results/run")
    sp.add_argument("--dims", default=None, help="逗号分隔，如 math,tools")
    sp.add_argument("--seed", type=int, default=20260101)
    sp.add_argument("--temperature", type=float, default=0.0)
    sp.add_argument("--max-tokens", type=int, default=768)
    sp.add_argument("--timeout", type=float, default=180.0)
    sp.add_argument("--title", default=None)
    sp.add_argument("--no-report", action="store_true")
    sp.add_argument("--no-resume", action="store_true")
    sp.set_defaults(func=cmd_run)

    sp = sub.add_parser("score", help="对已有 raw.jsonl 重新判分")
    sp.add_argument("--out", required=True)
    sp.add_argument("--tasks-dir", default=DEFAULT_TASKS)
    sp.set_defaults(func=cmd_score)

    sp = sub.add_parser("report", help="渲染 HTML 报告")
    sp.add_argument("--out", required=True, help="结果目录")
    sp.add_argument("--output", default=None)
    sp.add_argument("--title", default=None)
    sp.set_defaults(func=cmd_report)

    sp = sub.add_parser("compare", help="两组结果配对比较")
    sp.add_argument("--a", required=True)
    sp.add_argument("--b", required=True)
    sp.add_argument("--label-a", default="A")
    sp.add_argument("--label-b", default="B")
    sp.add_argument("--json", default=None)
    sp.set_defaults(func=cmd_compare)

    sp = sub.add_parser("selftest", help="判分器对抗样例自检")
    sp.set_defaults(func=cmd_selftest)

    sp = sub.add_parser("export-recheck", help="导出人工复判样本 CSV")
    sp.add_argument("--out", required=True, help="结果目录")
    sp.add_argument("--csv", default=None, help="输出路径，缺省为 <out>/recheck.csv")
    sp.add_argument("--per-dim", type=int, default=8)
    sp.add_argument("--seed", type=int, default=20260101)
    sp.set_defaults(func=cmd_export_recheck)

    sp = sub.add_parser("recheck", help="计算人机一致率（读填好的 CSV）")
    sp.add_argument("--csv", required=True)
    sp.add_argument("--json", default=None)
    sp.set_defaults(func=cmd_recheck)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n已中断", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
