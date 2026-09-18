# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Unified CLI entrypoint for skill-workshop v2 (validate / package / init / spec)."""

from __future__ import annotations

import difflib
import sys
from pathlib import Path

scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(scripts_dir))


def _lazy(name: str):
    module = __import__("_impl." + name, fromlist=["main"])
    return getattr(module, "main")


COMMANDS = {
    "validate": {
        "loader": lambda: _lazy("quick_validate"),
        "description": "Static SKILL.md validation (structure, links, version SSOT)",
        "aliases": ["quick-validate"],
    },
    "package": {
        "loader": lambda: _lazy("package_skill"),
        "description": "Validate and package a skill (.skill zip; default dry-run)",
        "aliases": [],
    },
    "init": {
        "loader": lambda: _lazy("init_skill"),
        "description": "Initialize a pure-Markdown skill skeleton (default dry-run)",
        "aliases": ["init-skill"],
    },
    "spec": {
        "loader": lambda: _lazy("spec_check"),
        "description": "Official Agent Skills frontmatter whitelist/order/name checks",
        "aliases": [],
    },
}

ALIAS_TO_COMMAND = {
    alias: name for name, config in COMMANDS.items() for alias in config["aliases"]
}

ARCHIVED_HINT = (
    "该子命令已在 skill-workshop v2 归档。运行时仅保留 "
    "validate / package / init / spec；历史实现在 docs/archive/scripts/。"
)


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
                print(f"未知命令: '{argv[1]}'。{hint} {ARCHIVED_HINT}", file=sys.stderr)
                return 2
            return command["loader"]()(["--help"])
        return print_help()

    command_name, command = resolve_command(argv[0])
    if command is None:
        suggestion = _suggest_command(argv[0])
        hint = f" Did you mean '{suggestion}'?" if suggestion else ""
        print(f"未知命令: '{argv[0]}'。{hint} {ARCHIVED_HINT}", file=sys.stderr)
        return 2
    return command["loader"]()(argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
