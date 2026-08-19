"""
skill-reviewer 裁判师版自检脚本 v5.2 — thin wrapper

所有校验逻辑已迁移至 review_ops.py（API 化版本）。
本文件仅保留独立运行入口（python -m scripts._impl.validate_review），
委托 review_ops 的公开函数执行实际校验。

迁移原因：validate_review.py 与 review_ops.py 约 80% 代码重复，
合并后消除正则重复编译、缓存不一致等性能问题。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .review_ops import (
    clear_cache,
    review_report,
    checklist_scan,
    spec_check,
    consistency_check,
    _load_external_rules,
    CONSISTENCY_RULES,
)

_VERSION = "5.2"


def main():
    parser = argparse.ArgumentParser(
        description="skill-reviewer 裁判师版自检工具",
        epilog="模式说明：默认=评审产物校验  --checklist=仓库快速扫描  --spec=官方规范校验  --consistency=术语一致性检查\n可组合：--checklist --consistency 同时运行多个模式"
    )
    parser.add_argument("target", help="目标文件或目录")
    parser.add_argument("--checklist", action="store_true", help="运行仓库快速扫描模式（覆盖 M/T/P/V/B 关键项）")
    parser.add_argument("--spec", action="store_true", help="运行官方 Spec 模式")
    parser.add_argument("--consistency", action="store_true", help="运行术语一致性检查（检测 v4.0 重构后的旧术语残留）")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出结果")
    parser.add_argument("--offset", type=int, default=0, help="跳过前 N 条错误（用于输出截断）")
    parser.add_argument("--output", type=int, default=0, help="最多输出 N 条错误（0=全部）")
    parser.add_argument("--quiet", action="store_true", help="静默模式：只输出 PASS/FAIL，不输出错误详情")
    parser.add_argument("--verbose", action="store_true", help="详细模式：输出每个模式的检查过程")
    parser.add_argument("--version", action="version", version=f"%(prog)s {_VERSION}")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"错误：找不到路径 {args.target}", file=sys.stderr)
        sys.exit(2)

    clear_cache()

    external_rules = _load_external_rules(Path(__file__).resolve().parent)
    if external_rules:
        CONSISTENCY_RULES.extend(external_rules)

    modes_requested = []
    if args.spec:
        modes_requested.append("spec")
    if args.checklist:
        modes_requested.append("checklist")
    if args.consistency:
        modes_requested.append("consistency")
    if not modes_requested:
        modes_requested.append("review")

    all_results: dict[str, dict] = {}
    overall_status = "PASS"

    for mode in modes_requested:
        mode_result = {"status": "PASS", "errors": []}
        if args.verbose:
            print(f"[{mode.upper()}] 开始检查...", file=sys.stderr)

        if mode == "spec":
            result = spec_check(target_path)
            mode_result["status"] = result["status"]
            mode_result["errors"] = result["errors"]
        elif mode == "consistency":
            result = consistency_check(target_path)
            mode_result["status"] = result["status"]
            mode_result["errors"] = result["errors"]
        elif mode == "checklist":
            result = checklist_scan(target_path)
            mode_result["status"] = result["status"]
            mode_result["errors"] = result["errors"]
        elif mode == "review":
            result = review_report(target_path)
            mode_result["status"] = result["status"]
            mode_result["errors"] = result["errors"]

        if mode_result["status"] == "FAIL":
            overall_status = "FAIL"

        mode_result["total"] = len(mode_result["errors"])
        errors = mode_result["errors"]
        if args.offset:
            errors = errors[args.offset:]
        if args.output:
            errors = errors[:args.output]
        mode_result["displayed"] = len(errors)
        mode_result["errors"] = errors
        all_results[mode] = mode_result

    if args.json:
        print(json.dumps({"status": overall_status, "modes": all_results}, ensure_ascii=False, indent=2))
    else:
        if args.quiet:
            print(overall_status)
        else:
            for mode, mode_result in all_results.items():
                if mode_result["status"] == "FAIL":
                    for e in mode_result["errors"]:
                        print(f"- [{mode.upper()}] {e}", file=sys.stderr)
                    if args.offset or args.output:
                        print(f"（[{mode.upper()}] 显示 {mode_result['displayed']}/{mode_result['total']} 条，使用 --offset / --output 翻页）", file=sys.stderr)
                else:
                    print(f"[{mode.upper()}] {args.target} 通过校验")

    sys.exit(1 if overall_status == "FAIL" else 0)

if __name__ == "__main__":
    main()
