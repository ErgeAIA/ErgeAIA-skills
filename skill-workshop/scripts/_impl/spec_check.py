"""Official Agent Skills spec lightweight check (v2 runtime)."""

from __future__ import annotations

import re
from pathlib import Path

FM_BLOCK_RE = re.compile(r"^---\s*(.*?)\s*---\s*", re.S)
FM_KEY_RE = re.compile(r"^(\w+):")
NAME_FIELD_RE = re.compile(r"^name:\s*(.*)", re.M)
DESC_LINE_RE = re.compile(r"description:(.*)")
NEXT_KEY_CANDIDATES = ["license", "compatibility", "allowed-tools", "metadata"]

ALLOWED_ROOT_KEYS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
FORBIDDEN_ROOT_KEYS = {"triggers", "tags"}
EXPECTED_KEY_ORDER = [
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
]
REQUIRED_KEYS = ["name", "description"]


def _err(msg: str, fix: str = "") -> str:
    return f"{msg} | 修复建议：{fix}" if fix else msg


def _extract_description(text: str, fm_content: str) -> tuple[str, bool]:
    desc_m = DESC_LINE_RE.search(text)
    if not desc_m:
        return "", False
    desc_line = desc_m.group(1).strip().strip('"').strip("'")
    fm_match = FM_BLOCK_RE.match(text)
    if fm_match and (
        desc_line.lstrip().startswith(">")
        or desc_line.lstrip().startswith("|")
        or not desc_line.strip()
    ):
        desc_start = fm_content.find("description:")
        if desc_start < 0:
            return desc_line, True
        next_positions = [
            fm_content.find(k + ":", desc_start + 1)
            for k in NEXT_KEY_CANDIDATES
            if fm_content.find(k + ":", desc_start + 1) != -1
        ]
        next_key_pos = min(next_positions) if next_positions else len(fm_content)
        block = fm_content[desc_start:next_key_pos]
        lines = block.splitlines()[1:]
        return "\n".join(line.lstrip() for line in lines if line.strip()), True
    return desc_line, True


def spec_check(path: str | Path, profile: str = "standard") -> dict:
    """Official frontmatter whitelist/order/name/description checks."""
    repo = Path(path)
    skill_md = repo / "SKILL.md"
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        text = ""
    if not text:
        return {
            "status": "FAIL",
            "errors": [_err("SKILL.md 读取失败或为空", f"确认路径存在：{skill_md}")],
            "advisories": [],
            "findings": [],
        }

    fm_match = FM_BLOCK_RE.match(text)
    if not fm_match:
        return {
            "status": "FAIL",
            "errors": [_err("缺少 frontmatter", "添加 YAML frontmatter")],
            "advisories": [],
            "findings": [],
        }

    fm_content = fm_match.group(1)
    top_keys = []
    for line in fm_content.splitlines():
        m = FM_KEY_RE.match(line)
        if m:
            top_keys.append(m.group(1))

    failures = []
    advisories = []
    for key in top_keys:
        if key not in ALLOWED_ROOT_KEYS:
            failures.append(_err(f"未知顶层属性：{key}", f"移除 '{key}' 或移入 metadata"))
        if key in FORBIDDEN_ROOT_KEYS:
            failures.append(_err(f"'{key}' 不能作为顶层属性", f"将 '{key}' 移入 metadata"))
    for key in REQUIRED_KEYS:
        if key not in top_keys:
            failures.append(_err(f"缺少必需字段：{key}", f"添加 '{key}' 字段"))

    # 字段顺序：官方规范无顺序要求（缓存 spec 通篇无 order 条款，本仓文档也只写「建议顺序」），
    # 因此不得作为阻塞项；v2.3.0 由 FAIL 降为 advisory。
    allowed_in_order = [k for k in EXPECTED_KEY_ORDER if k in top_keys]
    if allowed_in_order != top_keys:
        advisories.append(
            _err(
                "字段顺序与仓库建议不一致（非官方约束，不影响加载）",
                "按 name→description→license→compatibility→metadata→allowed-tools 排列",
            )
        )

    name_m = NAME_FIELD_RE.search(fm_content)
    name = name_m.group(1).strip().strip('"').strip("'") if name_m else ""
    repo_name = repo.resolve().name
    if not name:
        failures.append(_err("name 字段缺失", "添加 name 字段"))
    else:
        if name != repo_name:
            failures.append(
                _err(f"目录名 '{repo_name}' 与 name '{name}' 不符", "同步命名")
            )
        if re.search(r"[A-Z]", name):
            failures.append(_err(f"name '{name}' 含大写字符", "改为 hyphen-case"))
        if name.startswith("-") or name.endswith("-"):
            failures.append(_err(f"name '{name}' 以连字符首尾", "移除首尾连字符"))
        if "--" in name:
            failures.append(_err(f"name '{name}' 含连续连字符", "改为单连字符"))
        if len(name) > 64:
            failures.append(_err("name 超过 64 字符", "缩短 name"))

    desc, desc_found = _extract_description(text, fm_content)
    if not desc_found:
        failures.append(_err("description 字段缺失", "添加 description"))
    else:
        if "<" in desc or ">" in desc:
            # 本仓约定（避免被 Markdown 渲染吞掉、避免安装器解析歧义），非官方字段约束。
            failures.append(_err("description 含尖括号（本仓约定）", "移除 < 与 >"))
        if not desc.strip():
            failures.append(_err("description 为空", "填写实际描述"))
        if len(desc) > 1024:
            failures.append(_err("description 超过 1024 字符", "精简至 1024 以内"))

    status = "FAIL" if failures else "PASS"
    if profile == "advisory":
        status = "PASS"
    findings = [
        {"rule_class": "spec", "severity": "blocker", "message": e} for e in failures
    ] + [{"rule_class": "spec-convention", "severity": "advisory", "message": a} for a in advisories]
    return {"status": status, "errors": failures, "advisories": advisories, "findings": findings}


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json
    import sys

    p = argparse.ArgumentParser(
        prog="skill_cli.py spec", description="Official Agent Skills frontmatter spec check"
    )
    p.add_argument("target", help="Skill directory")
    p.add_argument("--json", action="store_true", help="JSON output")
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--output", type=int, default=0, help="Max errors to print (0=all)")
    p.add_argument(
        "--profile",
        default="standard",
        choices=["strict", "standard", "advisory"],
        help="advisory keeps findings but always PASS",
    )
    args = p.parse_args(argv)

    result = spec_check(args.target, profile=args.profile)
    errors = result["errors"]
    sliced = errors[args.offset :] if args.offset else errors
    if args.output:
        sliced = sliced[: args.output]

    if args.json:
        out = dict(result)
        out["errors"] = sliced
        out["displayed"] = len(sliced)
        out["total"] = len(errors)
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        for e in sliced:
            print(f"- {e}", file=sys.stderr)
        for a in result.get("advisories", []):
            print(f"~ {a}", file=sys.stderr)
        print(result["status"])
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
