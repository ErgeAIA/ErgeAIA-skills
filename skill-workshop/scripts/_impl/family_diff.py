# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Family baseline block-set diff for skill-workshop (D2).

Compares a target skill's structural blocks against a sibling baseline skill
(or auto-discovered siblings in the same parent directory). Reports missing /
extra blocks — structure only, not semantic style unification.

Exit codes: 0=PASS, 1=FAIL (block gaps), 2=ERROR.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Canonical structural blocks for a production skill in this repo family.
# Presence-only: does not judge internal quality.
BLOCK_CHECKS = [
    ("SKILL.md", lambda p: (p / "SKILL.md").is_file()),
    ("README.md", lambda p: (p / "README.md").is_file()),
    ("VERSION.md", lambda p: (p / "VERSION.md").is_file()),
    ("references/", lambda p: (p / "references").is_dir()),
    ("scripts/skill_cli.py or scripts/", lambda p: (p / "scripts").is_dir()),
    (
        "frontmatter name+description",
        lambda p: _has_frontmatter_pair(p / "SKILL.md"),
    ),
    (
        "metadata.version",
        lambda p: _has_metadata_version(p / "SKILL.md"),
    ),
]


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


def _has_frontmatter_pair(skill_md: Path) -> bool:
    if not skill_md.is_file():
        return False
    text = _read(skill_md)
    if not text.startswith("---"):
        return False
    end = text.find("\n---", 3)
    fm = text[3:end] if end != -1 else text[:800]
    return "name:" in fm and "description:" in fm


def _has_metadata_version(skill_md: Path) -> bool:
    if not skill_md.is_file():
        return False
    text = _read(skill_md)
    if not text.startswith("---"):
        return False
    end = text.find("\n---", 3)
    fm = text[3:end] if end != -1 else text[:800]
    return "version:" in fm


def check_blocks(skill_path: Path) -> list[dict]:
    results = []
    for name, fn in BLOCK_CHECKS:
        ok = bool(fn(skill_path))
        results.append({"block": name, "present": ok})
    return results


def discover_siblings(skill_path: Path) -> list[Path]:
    """Sibling skill dirs under the same parent that look like skills."""
    parent = skill_path.parent
    if not parent.is_dir():
        return []
    sibs = []
    for child in sorted(parent.iterdir()):
        if not child.is_dir() or child == skill_path:
            continue
        if child.name.startswith(".") or child.name == "__pycache__":
            continue
        if (child / "SKILL.md").is_file():
            sibs.append(child)
    return sibs


def diff_against_baseline(target: Path, baseline: Path) -> dict:
    t_blocks = {b["block"]: b["present"] for b in check_blocks(target)}
    b_blocks = {b["block"]: b["present"] for b in check_blocks(baseline)}
    missing = [k for k, v in b_blocks.items() if v and not t_blocks.get(k)]
    extra = [k for k, v in t_blocks.items() if v and not b_blocks.get(k)]
    # "extra" vs baseline is informational (baseline may be thinner)
    return {
        "target": str(target),
        "baseline": str(baseline),
        "missing_blocks": missing,
        "present_in_target_not_baseline": extra,
        "target_blocks": t_blocks,
        "baseline_blocks": b_blocks,
    }


def run_family_diff(target: Path, baseline: Path | None, strict: bool) -> dict:
    errors: list[str] = []
    details: dict = {"mode": "single"}

    if baseline is None:
        siblings = discover_siblings(target)
        details["mode"] = "siblings"
        details["siblings"] = [str(s) for s in siblings]
        if not siblings:
            # no baseline: self-check only
            blocks = check_blocks(target)
            details["self_blocks"] = blocks
            missing = [b["block"] for b in blocks if not b["present"]]
            # core three always required
            core_missing = [m for m in missing if m in {"SKILL.md", "frontmatter name+description"}]
            if core_missing:
                errors.append(f"核心块缺失: {core_missing}")
            status = "FAIL" if errors else "PASS"
            return {
                "command": "family-diff",
                "status": status,
                "errors": errors,
                "details": details,
            }
        # union baseline: block present if any sibling has it (family consensus)
        consensus: dict[str, bool] = {name: False for name, _ in BLOCK_CHECKS}
        for sib in siblings:
            for b in check_blocks(sib):
                if b["present"]:
                    consensus[b["block"]] = True
        target_blocks = {b["block"]: b["present"] for b in check_blocks(target)}
        missing = [k for k, v in consensus.items() if v and not target_blocks.get(k)]
        details["consensus_blocks"] = consensus
        details["target_blocks"] = target_blocks
        details["missing_blocks"] = missing
        if missing:
            errors.append(f"相对家族共识缺失块: {missing}")
    else:
        if not baseline.is_dir():
            print(f"基线不存在: {baseline}", file=sys.stderr)
            return {
                "command": "family-diff",
                "status": "ERROR",
                "errors": [f"基线不存在: {baseline}"],
                "details": {},
            }
        diff = diff_against_baseline(target, baseline)
        details = {**details, "mode": "single", **diff}
        if diff["missing_blocks"]:
            errors.append(f"相对基线缺失块: {diff['missing_blocks']}")
        if strict and diff["present_in_target_not_baseline"]:
            errors.append(
                f"目标多出基线没有的块（strict）: {diff['present_in_target_not_baseline']}"
            )

    status = "FAIL" if errors else "PASS"
    return {
        "command": "family-diff",
        "status": status,
        "errors": errors,
        "details": details,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="skill_cli.py family-diff",
        description="家族基线差分：以兄弟技能块集为基线，检出目标技能缺失结构块（仅结构，不做语义统一）",
    )
    parser.add_argument("target", nargs="?", default=".", help="目标 Skill 根目录")
    parser.add_argument(
        "--baseline",
        default=None,
        help="基线 Skill 路径；省略则用同父目录兄弟技能的块集共识",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="目标多出基线没有的块也报 FAIL（默认仅报缺失）",
    )
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args(argv)

    target = Path(args.target).resolve()
    if not target.is_dir():
        print(f"目标不是目录: {target}", file=sys.stderr)
        return 2
    baseline = Path(args.baseline).resolve() if args.baseline else None

    try:
        result = run_family_diff(target, baseline, args.strict)
    except Exception as exc:  # noqa: BLE001
        print(f"family-diff 失败: {exc}", file=sys.stderr)
        return 2

    if result.get("status") == "ERROR":
        for e in result["errors"]:
            print(e, file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["status"])
        for e in result["errors"]:
            print(f"- {e}", file=sys.stderr)
        mode = result["details"].get("mode")
        print(f"mode={mode}", file=sys.stderr)
        if "missing_blocks" in result["details"]:
            print(f"missing={result['details']['missing_blocks']}", file=sys.stderr)

    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
