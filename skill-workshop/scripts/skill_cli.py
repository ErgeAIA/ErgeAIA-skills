# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Unified CLI entrypoint for skill-workshop."""

from __future__ import annotations

from pathlib import Path
import sys
import difflib

scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(scripts_dir))

from _impl import (
    aggregate_benchmark,
    analyze_requirements,
    eval_set_editor,
    generate_report,
    generate_scenario_templates,
    improve_description,
    init_skill,
    package_skill,
    quick_validate,
    review,
    review_ops,
    routing_check,
    run_eval,
    run_loop,
    selfheal,
)


def _add_output_args(p):
    p.add_argument("--offset", type=int, default=0, help="跳过前 N 条错误")
    p.add_argument("--output", type=int, default=0, help="最多输出 N 条错误（0=全部）")


def _slice_errors(errors, offset, limit):
    sliced = errors[offset:] if offset else errors
    if limit:
        sliced = sliced[:limit]
    return sliced


def _print_review_result(result, args, label):
    errors = result["errors"]
    sliced = _slice_errors(errors, args.offset, args.output)
    if args.json:
        import json as _json
        out = dict(result)
        out["errors"] = sliced
        out["displayed"] = len(sliced)
        out["total"] = len(errors)
        print(_json.dumps(out, ensure_ascii=False, indent=2))
    else:
        for e in sliced:
            print(f"- {e}", file=sys.stderr)
        if args.offset or args.output:
            print(f"[{label}] 显示 {len(sliced)}/{len(errors)} 条", file=sys.stderr)
        print(result["status"])
    return 1 if result["status"] == "FAIL" else 0


def _review_report_cmd(argv: list[str]) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="skill_cli.py review", description="评审报告 8 段校验")
    p.add_argument("target", help="评审报告文件路径")
    p.add_argument("--json", action="store_true", help="JSON 输出")
    _add_output_args(p)
    args = p.parse_args(argv)
    result = review_ops.review_report(args.target)
    return _print_review_result(result, args, "REVIEW")


def _checklist_cmd(argv: list[str]) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="skill_cli.py checklist", description="仓库 Checklist 快速扫描")
    p.add_argument("target", help="Skill 仓库目录")
    p.add_argument("--json", action="store_true", help="JSON 输出")
    _add_output_args(p)
    args = p.parse_args(argv)
    result = review_ops.checklist_scan(args.target)
    return _print_review_result(result, args, "CHECKLIST")


def _spec_cmd(argv: list[str]) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="skill_cli.py spec", description="官方 Spec 校验")
    p.add_argument("target", help="Skill 仓库目录")
    p.add_argument("--json", action="store_true", help="JSON 输出")
    _add_output_args(p)
    args = p.parse_args(argv)
    result = review_ops.spec_check(args.target)
    return _print_review_result(result, args, "SPEC")


def _consistency_cmd(argv: list[str]) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="skill_cli.py consistency", description="术语一致性检查")
    p.add_argument("target", help="Skill 仓库目录")
    p.add_argument("--json", action="store_true", help="JSON 输出")
    _add_output_args(p)
    args = p.parse_args(argv)
    result = review_ops.consistency_check(args.target)
    return _print_review_result(result, args, "CONSISTENCY")


def _routing_check_cmd(argv: list[str]) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="skill_cli.py routing-check", description="路由一致性校验")
    p.add_argument("target", help="Skill 仓库目录")
    args = p.parse_args(argv)
    sys.argv = ["routing_check", args.target]
    return routing_check.main()


COMMANDS = {
    "analyze": {
        "main": analyze_requirements.main,
        "description": "Interactive requirements analysis and design doc generation",
        "aliases": ["analyze-requirements"],
    },
    "init": {
        "main": init_skill.main,
        "description": "Initialize a new skill skeleton",
        "aliases": ["init-skill"],
    },
    "generate-templates": {
        "main": generate_scenario_templates.main,
        "description": "Generate scenario input template drafts from SKILL.md workflows",
        "aliases": ["gen-templates", "templates"],
    },
    "validate": {
        "main": quick_validate.main,
        "description": "Run static SKILL.md validation",
        "aliases": ["quick-validate"],
    },
    "package": {
        "main": package_skill.main,
        "description": "Validate and package a skill",
        "aliases": [],
    },
    "eval": {
        "main": run_eval.main,
        "description": "Run trigger evaluation against an eval-set",
        "aliases": ["run-eval"],
    },
    "loop": {
        "main": run_loop.main,
        "description": "Run eval/improve iteration loop",
        "aliases": ["run-loop"],
    },
    "benchmark": {
        "main": aggregate_benchmark.main,
        "description": "Aggregate benchmark runs into summary stats",
        "aliases": ["aggregate-benchmark"],
    },
    "report": {
        "main": generate_report.main,
        "description": "Generate HTML report from run_loop JSON output",
        "aliases": ["generate-report"],
    },
    "improve": {
        "main": improve_description.main,
        "description": "Generate an improved skill description from eval results",
        "aliases": ["improve-description"],
    },
    "review-playback": {
        "main": review.main,
        "description": "Generate or serve the eval review UI",
        "aliases": ["generate-review"],
    },
    "editor": {
        "main": eval_set_editor.main,
        "description": "Preview or export the eval JSON editor page",
        "aliases": ["eval-editor"],
    },
    "review": {
        "main": _review_report_cmd,
        "description": "Review report 8-section validation (from skill-reviewer)",
        "aliases": [],
    },
    "checklist": {
        "main": _checklist_cmd,
        "description": "Repository checklist quick scan (from skill-reviewer)",
        "aliases": [],
    },
    "spec": {
        "main": _spec_cmd,
        "description": "Official spec compliance check (from skill-reviewer)",
        "aliases": [],
    },
    "consistency": {
        "main": _consistency_cmd,
        "description": "Terminology consistency check (from skill-reviewer)",
        "aliases": [],
    },
    "routing-check": {
        "main": _routing_check_cmd,
        "description": "Routing consistency check (SKILL.md table vs workflow reads-from)",
        "aliases": [],
    },
    "selfheal": {
        "main": selfheal.main,
        "description": "Self-heal doc drift & ghost refs (dead-link REF_MAP fix, dry-run default)",
        "aliases": [],
    },
}

ALIAS_TO_COMMAND = {alias: name for name, config in COMMANDS.items() for alias in config["aliases"]}


def print_help() -> int:
    print("Usage: python scripts/skill_cli.py <command> [args...]\n")
    print("Commands:")
    for name, config in COMMANDS.items():
        alias_text = ""
        if config["aliases"]:
            alias_text = f" (aliases: {', '.join(config['aliases'])})"
        print(f"  {name:<10} {config['description']}{alias_text}")
    print("\nUse 'python scripts/skill_cli.py <command> --help' for command-specific options.")
    return 0


def _suggest_command(name: str) -> str | None:
    all_names = list(COMMANDS.keys()) + list(ALIAS_TO_COMMAND.keys())
    matches = difflib.get_close_matches(name, all_names, n=1, cutoff=0.6)
    return matches[0] if matches else None


def resolve_command(name: str):
    canonical = ALIAS_TO_COMMAND.get(name, name)
    return canonical, COMMANDS.get(canonical)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help", "help"}:
        if len(argv) > 1 and argv[0] == "help":
            command_name, command = resolve_command(argv[1])
            if command is None:
                suggestion = _suggest_command(argv[1])
                hint = f" Did you mean '{suggestion}'?" if suggestion else ""
                print(f"未知命令: '{argv[1]}'。{hint} 建议: 运行 --help 查看可用命令。", file=sys.stderr)
                return 2
            entry = command["main"]
            if not callable(entry):
                entry = entry()
            return entry(["--help"])
        return print_help()

    command_name, command = resolve_command(argv[0])
    if command is None:
        suggestion = _suggest_command(argv[0])
        hint = f" Did you mean '{suggestion}'?" if suggestion else ""
        print(f"未知命令: '{argv[0]}'。{hint} 建议: 运行 --help 查看可用命令。", file=sys.stderr)
        return 2

    entry = command["main"]
    return entry(argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
