"""
selfheal — skill-workshop 自愈工具

自动检测并修复技能仓库中的「文档漂移 / 幽灵引用」类回归故障：

1. 主动加载引用缺失（reads-from / 以 X 为准 / 见 X / 模板指针）
   指向不存在的 `references/*.md` —— 按 REF_MAP 无歧义映射自动修复。
2. README 文件树声明了不存在的路径（报告，不自动修）。
3. 根目录残留 `examples/`（与 canonical `references/examples/` 冲突，报告）。

设计原则：
- 闭环验证：修复后重跑触发它的检测；未过则回滚 .bak。
- 幂等：干净仓库跑 `selfheal --auto` 零改动。
- 安全默认：默认 `--dry-run`（只报告不落地）；`--auto` 才写文件。
- 仅对「映射明确、无歧义」的修复自动落地；歧义/示例项只报告。

使用：
    python -m scripts._impl.selfheal [SKILL_PATH] [--dry-run] [--auto] [--explain]
    python scripts/skill_cli.py selfheal [SKILL_PATH] [--dry-run] [--auto]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

# 明确映射表：被删/笔误文件 -> 正确替代。仅无歧义项才可自动修复。
REF_MAP: dict[str, str] = {
    "references/specs/spec-zh.md": "references/specs/spec.md",
    "references/specs/validate-zh.md": "references/specs/validate.md",
    # 真实命名笔误：文档写成下划线，实际文件为连字符
    "references/templates/scenario_input_template.md": "references/templates/scenario-input-template.md",
}

# 历史叙述段（版本历史）不扫描，避免把 CHANGELOG 里的旧引用误判为 active dead link。
HISTORY_EXCLUDE_RE = re.compile(r"^##\s+(版本历史|Version History|Changelog)\s*$", re.MULTILINE | re.IGNORECASE)
# 匹配 references/...\.md 形式的引用（链接或裸路径）。
REF_PATH_RE = re.compile(r"references/[A-Za-z0-9_./-]+\.md")
# 示例性散文标记：命中则视为「教学示例」而非真实加载指令，不自动修。
EXAMPLE_MARKERS = ("如果", "示例", "例如", "example", "if the", "see the", "e.g.", "for example", "reference guide")
# 排除扫描的文件（历史叙述 / 自身 / 规划文档）。
SCAN_EXCLUDE = ("CHANGELOG.md", "VERSION.md")


def _iter_scan_md(skill_path: Path):
    for md in sorted(skill_path.rglob("*.md")):
        rel = md.relative_to(skill_path).as_posix()
        leaf = rel.split("/")[-1]
        if leaf in SCAN_EXCLUDE:
            continue
        # 跳过根目录下的规划/报告文档（REVIEW-*.md / SELFHEAL-PLAN-*.md 等），
        # 它们只是叙述，不应被自动改写；SKILL.md 必须扫描。
        if "/" not in rel and rel != "SKILL.md":
            continue
        yield md, rel


def find_active_dead_links(skill_path: Path) -> list[dict]:
    """返回 [{file, missing, context, is_example}]。排除 CHANGELOG/VERSION/根规划文档。"""
    dead: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for md, rel in _iter_scan_md(skill_path):
        text = md.read_text(encoding="utf-8")
        # 仅扫描历史段之前的正文，避免版本叙述里的旧引用误报。
        body = HISTORY_EXCLUDE_RE.split(text)[0]
        for line in body.splitlines():
            for ref in REF_PATH_RE.findall(line):
                if (skill_path / ref).exists():
                    continue
                key = (rel, ref)
                if key in seen:
                    continue
                seen.add(key)
                is_example = any(m.lower() in line.lower() for m in EXAMPLE_MARKERS)
                dead.append({
                    "file": rel,
                    "missing": ref,
                    "context": line.strip()[:80],
                    "is_example": is_example,
                })
    return dead


def _backup_dir() -> Path:
    d = Path.home() / ".workbuddy" / "selfheal-bak"
    d.mkdir(parents=True, exist_ok=True)
    return d


def backup(p: Path) -> Path:
    """复制 p 到带时间戳的备份目录，返回备份路径。

    备份名基于绝对路径生成（替换盘符与分隔符），不依赖当前工作目录，
    因此对临时目录 / 非 cwd 下的文件也能正确备份。
    """
    ts_dir = _backup_dir()
    safe_name = str(p.resolve()).replace(":", "_").replace("/", "__").replace("\\", "__")
    bak = ts_dir / safe_name
    shutil.copy(p, bak)
    return bak


def fix_dead_links(skill_path: Path, dry: bool) -> list[dict]:
    """按 REF_MAP 修复死链。dry=True 时只报告不落地。返回变更清单。"""
    changes: list[dict] = []
    for item in find_active_dead_links(skill_path):
        rel, missing, is_example = item["file"], item["missing"], item["is_example"]
        target = REF_MAP.get(missing)
        # 示例散文 / 无明确映射 -> 只报告，不落地（防误修）。
        if is_example or not target:
            changes.append({
                "file": rel, "missing": missing, "target": target,
                "applied": False,
                "reason": "example-prose" if is_example else "no-unambiguous-map",
            })
            continue
        md = skill_path / rel
        if dry:
            changes.append({"file": rel, "missing": missing, "target": target, "applied": False, "reason": "dry-run"})
            continue
        bak = backup(md)
        text = md.read_text(encoding="utf-8")
        text = text.replace(missing, target)
        md.write_text(text, encoding="utf-8")
        changes.append({"file": rel, "missing": missing, "target": target, "applied": True, "backup": str(bak)})
    return changes


def find_root_examples(skill_path: Path) -> list[str]:
    """检测根目录残留 examples/（canonical = references/examples/）。"""
    root_examples = skill_path / "examples"
    if root_examples.is_dir():
        return [root_examples.relative_to(skill_path).as_posix()]
    return []


def find_readme_tree_drift(skill_path: Path) -> list[dict]:
    """解析 README 文件树块，校验声明的路径是否存在。返回 [{rel, exists}]。"""
    readme = skill_path / "README.md"
    if not readme.exists():
        return []
    text = readme.read_text(encoding="utf-8")
    blocks = re.findall(r"```[^\n]*\n(.*?)```", text, flags=re.DOTALL)
    tree_lines: list[str] = []
    for blk in blocks:
        if "──" in blk or "├──" in blk:
            tree_lines.extend(blk.splitlines())
    if not tree_lines:
        return []

    drift: list[dict] = []
    stack: list[tuple[int, str]] = []
    for raw in tree_lines:
        if "──" not in raw:
            continue
        indent_len = len(raw) - len(raw.lstrip(" │"))
        depth = indent_len // 4
        name = raw.split("──", 1)[1].strip()
        name = re.sub(r"\s*#.*$", "", name).strip()
        if not name:
            continue
        # 跳过分组标签（含空格或 "+"，如 "W0-W7 + V0"）
        if re.search(r"[ +]", name):
            continue
        is_dir = name.endswith("/")
        name = name.rstrip("/")
        while stack and stack[-1][0] >= depth:
            stack.pop()
        if is_dir:
            prefix = stack[-1][1] + "/" if stack else ""
            stack.append((depth, prefix + name))
            rel = prefix + name
        else:
            prefix = stack[-1][1] + "/" if stack else ""
            rel = prefix + name
        if depth == 0 and is_dir:  # 跳过根节点本身
            continue
        if not (skill_path / rel).exists():
            drift.append({"rel": rel, "exists": False})
    return drift


def check_description(skill_path: Path) -> dict:
    """检查 SKILL.md description 是否含平台锁或块标量（报告项，不自修）。"""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return {"ok": True, "notes": []}
    text = skill_md.read_text(encoding="utf-8")
    notes: list[str] = []
    m = re.search(r"^description:\s*(.+)$", text, flags=re.MULTILINE)
    if m:
        val = m.group(1).strip()
        if "Claude" in val:
            notes.append("description 含平台锁 'Claude'")
        if val.startswith("|") or val.startswith(">") or "\n" in val:
            notes.append("description 疑似 YAML 块标量（非单行）")
    return {"ok": len(notes) == 0, "notes": notes}


def self_test(skill_path: Path) -> dict:
    """闭环验证：重跑触发检测，全过则 ok=True。"""
    try:
        from _impl import routing_check, quick_validate  # noqa: F401
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from _impl import routing_check, quick_validate  # noqa: F401

    routing_errors = routing_check.check_routing_consistency(skill_path)
    dead = find_active_dead_links(skill_path)
    desc = check_description(skill_path)
    # 闭环判据：routing 通过，且不存在「仍可自动修却未修」的死链。
    # 示例散文 / 无明确映射项属设计上仅报告、不自动修，不算失败。
    unresolved_fixable = [d for d in dead if (not d["is_example"]) and (d["missing"] in REF_MAP)]
    ok = (not routing_errors) and (not unresolved_fixable)
    return {
        "ok": ok,
        "routing_errors": routing_errors,
        "active_dead_links": dead,
        "unresolved_fixable": unresolved_fixable,
        "description_notes": desc["notes"],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="selfheal", description="skill-workshop 自愈工具")
    ap.add_argument("skill_path", nargs="?", default=".")
    ap.add_argument("--dry-run", action="store_true", help="只报告不落地（默认开启，除非 --auto）")
    ap.add_argument("--auto", action="store_true", help="自动落地无歧义修复")
    ap.add_argument("--explain", action="store_true", help="输出可读性说明")
    args = ap.parse_args(argv)

    sp = Path(args.skill_path).resolve()
    dry = args.dry_run or not args.auto  # 默认 dry-run

    report: dict = {"skill_path": sp.as_posix(), "dry": dry, "fixes": [], "reports": {}}

    fixes = fix_dead_links(sp, dry=dry)
    report["fixes"] = fixes

    report["reports"]["root_examples"] = find_root_examples(sp)
    report["reports"]["readme_tree_drift"] = find_readme_tree_drift(sp)
    report["reports"]["description"] = check_description(sp)

    applied = [f for f in fixes if f.get("applied")]
    pending = [f for f in fixes if not f.get("applied")]
    if args.explain:
        print(f"[selfheal] skill_path={sp}", file=sys.stderr)
        print(f"[selfheal] dry-run={dry} auto={args.auto}", file=sys.stderr)
        print(f"[selfheal] 应用修复 {len(applied)} 项，待人工/报告 {len(pending)} 项", file=sys.stderr)
        for f in applied:
            print(f"  ✓ {f['file']}: {f['missing']} -> {f['target']}", file=sys.stderr)
        for f in pending:
            tag = "示例散文" if f["reason"] == "example-prose" else ("dry" if f["reason"] == "dry-run" else "无映射")
            print(f"  ? {f['file']}: 缺失 {f['missing']}（{tag}）", file=sys.stderr)
        if report["reports"]["root_examples"]:
            print(f"  ! 根目录残留 examples: {report['reports']['root_examples']}", file=sys.stderr)
        if report["reports"]["readme_tree_drift"]:
            print(f"  ! README 树漂移: {[d['rel'] for d in report['reports']['readme_tree_drift']]}", file=sys.stderr)

    if args.auto and not dry:
        st = self_test(sp)
        report["self_test"] = st
        if not st["ok"]:
            print(json.dumps({"status": "FAIL", "self_test": st}, ensure_ascii=False, indent=2))
            return 2

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
