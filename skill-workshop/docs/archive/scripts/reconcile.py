# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Intra-skill fact-anchor reconcile for skill-workshop (C5 machine assist).

Extracts declaration sites of shared fact anchors and flags value conflicts.
Does NOT replace semantic C5 review — supplies evidence for W3.

Exit codes: 0=PASS (no conflict), 1=FAIL (conflicts), 2=ERROR.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# Skip history / packaging noise
SKIP_NAMES = {"CHANGELOG.md", "CHANGELOG.en.md"}
SKIP_DIRS = {"__pycache__", ".git", "node_modules"}

# Numeric threshold anchors: (context_key, regex)
# Field-specific char limits are distinct facts — do not merge description vs compatibility.
NUM_RULES = [
    ("lines", re.compile(r"(?:≤|<=|不超过|上限)\s*(\d+)\s*行", re.I)),
    ("tokens", re.compile(r"(?:≤|<=|不超过|上限)\s*(\d+)\s*Token", re.I)),
    ("desc_chars", re.compile(r"description[^\n]{0,50}?(?:≤|<=|Max|max|上限|不超过)\s*(\d+)", re.I)),
    ("compat_chars", re.compile(r"compatibility[^\n]{0,50}?(?:≤|<=|Max|max|上限|不超过)\s*(\d+)", re.I)),
    ("trigger_min", re.compile(r"(?:≥|>=|至少)\s*(\d+)\s*(?:个)?(?:触发|trigger)", re.I)),
]

# Lines that describe examples / provenance, not live load instructions.
EXAMPLE_MARKERS = (
    "旧术语", "溯源", "示例", "例如", "e.g.", "for example",
    "坏：", "好：", "placeholder", "占位", "如果", "if the",
)

SEMVER_RE = re.compile(r"\b(\d+\.\d+\.\d+)\b")
VERSION_HEAD_RE = re.compile(r"^##\s+\[?v?(\d+\.\d+\.\d+)\]?")  # 兼容 VERSION.md `## vX.Y.Z` 与 CHANGELOG.md `## [X.Y.Z]`
FM_VERSION_RE = re.compile(r"^\s*version:\s*[\"']?(\d+\.\d+\.\d+)", re.M)
README_VER_RE = re.compile(r"当前版本：\*\*v?(\d+\.\d+\.\d+)\*\*")
REF_PATH_RE = re.compile(r"references/[A-Za-z0-9_./-]+\.(?:md|yaml|yml|json|html)")


def _iter_md(skill_path: Path, include_version: bool = False):
    for md in sorted(skill_path.rglob("*.md")):
        rel = md.relative_to(skill_path).as_posix()
        parts = rel.split("/")
        if any(p in SKIP_DIRS for p in parts):
            continue
        if parts[-1] in SKIP_NAMES:
            continue
        if parts[-1] in {"VERSION.md", "CHANGELOG.md"} and not include_version:
            continue
        # skip root planning docs except SKILL/README/version records
        if len(parts) == 1 and parts[0] not in {"SKILL.md", "README.md", "VERSION.md", "CHANGELOG.md"}:
            continue
        yield md, rel


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def extract_version_sites(skill_path: Path) -> dict[str, list[str]]:
    """Skill-level version anchors only (not per-reference frontmatter versions).

    Sources:
    - SKILL.md frontmatter metadata.version
    - README.md「当前版本」
    - 版本记录（CHANGELOG.md / VERSION.md）的 `## vX.Y.Z` 或 `## [x.y.z]` 标题（历史；仅用于库存，不参与 active 冲突）
    """
    sites: dict[str, list[str]] = defaultdict(list)

    skill_md = skill_path / "SKILL.md"
    if skill_md.is_file():
        lines = _read(skill_md).splitlines()
        for i, line in enumerate(lines[:40], 1):
            m = FM_VERSION_RE.match(line)
            if m:
                sites[m.group(1)].append(f"SKILL.md:{i}")
                break

    readme = skill_path / "README.md"
    if readme.is_file():
        for i, line in enumerate(_read(readme).splitlines(), 1):
            m = README_VER_RE.search(line)
            if m:
                sites[m.group(1)].append(f"README.md:{i}")

    version_md = skill_path / "VERSION.md"
    if version_md.is_file():
        text = _read(version_md)
        for m in VERSION_HEAD_RE.finditer(text):
            line_no = text[: m.start()].count("\n") + 1
            sites[m.group(1)].append(f"VERSION.md:{line_no}")

    changelog_md = skill_path / "CHANGELOG.md"
    if changelog_md.is_file():
        text = _read(changelog_md)
        for m in VERSION_HEAD_RE.finditer(text):
            line_no = text[: m.start()].count("\n") + 1
            sites[m.group(1)].append(f"CHANGELOG.md:{line_no}")

    return {k: list(dict.fromkeys(v)) for k, v in sites.items()}


def extract_numeric_sites(skill_path: Path) -> dict[str, list[tuple[int, str, str]]]:
    """context -> list of (value, file:line, snippet)."""
    out: dict[str, list[tuple[int, str, str]]] = defaultdict(list)
    for md, rel in _iter_md(skill_path):
        text = _read(md)
        lines = text.splitlines()
        for i, line in enumerate(lines, 1):
            for key, rx in NUM_RULES:
                for m in rx.finditer(line):
                    val = int(m.group(1))
                    snippet = line.strip()[:120]
                    out[key].append((val, f"{rel}:{i}", snippet))
    return out


def extract_ref_path_sites(skill_path: Path) -> dict[str, list[str]]:
    """references/... path -> declaration sites (skips examples, fences, provenance)."""
    sites: dict[str, list[str]] = defaultdict(list)
    for md, rel in _iter_md(skill_path):
        text = _read(md)
        lines = text.splitlines()
        in_fence = False
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            low = line.lower()
            if any(m.lower() in low for m in EXAMPLE_MARKERS):
                continue
            # pattern library documents other skills' layouts, not this skill's load graph
            if rel.endswith("skill-patterns.md"):
                continue
            for path in REF_PATH_RE.findall(line):
                sites[path].append(f"{rel}:{i}")
    return {k: list(dict.fromkeys(v)) for k, v in sites.items()}


def run_reconcile(skill_path: Path) -> dict:
    errors: list[dict] = []
    inventory: dict = {"versions": {}, "numeric": {}, "ref_paths": {}}

    ver_sites = extract_version_sites(skill_path)
    inventory["versions"] = ver_sites
    # skill-workshop: allow historical versions in external version record (CHANGELOG.md/VERSION.md)
    active_vers = {
        v: sites
        for v, sites in ver_sites.items()
        if any(not (s.startswith("VERSION.md") or s.startswith("CHANGELOG.md")) for s in sites)
    }
    if len(active_vers) > 1:
        errors.append({
            "id": "VER-MULTI",
            "message": "同一技能出现多个非历史版本号声明",
            "sites": {v: s for v, s in active_vers.items()},
            "fix": "以 SKILL.md frontmatter metadata.version 为唯一真源，同步 README 当前版本与版本记录（CHANGELOG.md/VERSION.md）最新版本",
        })

    num_sites = extract_numeric_sites(skill_path)
    for key, items in num_sites.items():
        vals = sorted({v for v, _, _ in items})
        inventory["numeric"][key] = [
            {"value": v, "site": s, "snippet": sn} for v, s, sn in items
        ]
        if len(vals) > 1:
            errors.append({
                "id": f"NUM-{key.upper()}",
                "message": f"同一阈值语义「{key}」出现多个数值 {vals}",
                "sites": [{"value": v, "site": s} for v, s, _ in items],
                "fix": "选定唯一真相源文件，其余文件同步同一数值或改为指针引用",
            })

    ref_sites = extract_ref_path_sites(skill_path)
    inventory["ref_paths"] = ref_sites
    missing = []
    for path, sites in ref_sites.items():
        if not (skill_path / path).exists():
            missing.append({"path": path, "sites": sites})
    if missing:
        errors.append({
            "id": "REF-MISSING",
            "message": f"{len(missing)} 个被声明的 references 路径不存在",
            "sites": missing,
            "fix": "补文件或改声明；selfheal 可修无歧义幽灵引用",
        })

    status = "FAIL" if errors else "PASS"
    return {
        "command": "reconcile",
        "status": status,
        "skill": str(skill_path),
        "errors": [
            f"[{e['id']}] {e['message']}" for e in errors
        ],
        "findings": errors,
        "inventory_counts": {
            "version_values": len(ver_sites),
            "numeric_keys": len(num_sites),
            "ref_paths": len(ref_sites),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="skill_cli.py reconcile",
        description="C5 机检辅助：抽取事实锚点声明位并检出多值冲突（不替代人工语义对账）",
    )
    parser.add_argument("target", nargs="?", default=".", help="Skill 根目录")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--inventory", action="store_true", help="输出完整声明点清单")
    args = parser.parse_args(argv)

    skill_path = Path(args.target).resolve()
    if not skill_path.is_dir():
        print(f"目标不是目录: {skill_path}", file=sys.stderr)
        return 2

    try:
        result = run_reconcile(skill_path)
    except Exception as exc:  # noqa: BLE001 — structured ERROR exit
        print(f"reconcile 失败: {exc}", file=sys.stderr)
        return 2

    if args.json:
        payload = dict(result)
        if not args.inventory:
            payload.pop("inventory", None)
            # run_reconcile stores counts only; full inventory on request
        if args.inventory:
            # re-run extractors for dump
            payload["inventory"] = {
                "versions": extract_version_sites(skill_path),
                "numeric": {
                    k: [{"value": v, "site": s, "snippet": sn} for v, s, sn in items]
                    for k, items in extract_numeric_sites(skill_path).items()
                },
                "ref_paths": extract_ref_path_sites(skill_path),
            }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(result["status"])
        for e in result["errors"]:
            print(f"- {e}", file=sys.stderr)
        print(
            f"锚点计数: versions={result['inventory_counts']['version_values']} "
            f"numeric_keys={result['inventory_counts']['numeric_keys']} "
            f"ref_paths={result['inventory_counts']['ref_paths']}",
            file=sys.stderr,
        )
        if args.inventory:
            print(json.dumps({
                "versions": extract_version_sites(skill_path),
                "ref_paths": extract_ref_path_sites(skill_path),
            }, ensure_ascii=False, indent=2))

    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
