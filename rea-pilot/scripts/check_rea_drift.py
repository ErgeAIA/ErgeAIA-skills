#!/usr/bin/env python3
"""Check REA tool/CLI/anchor drift between a baseline snapshot and the installed package.

Read-only. No network, no writes.
Exit codes: 0 = no drift, 1 = drift found, 2 = error.
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from difflib import SequenceMatcher
from pathlib import Path

EFFECT_LABELS = {
    "launches_process": "启动进程",
    "may_show_ui": "可能弹窗",
    "may_access_network": "可能联网",
    "may_write_filesystem": "可能写盘",
}


def run(cmd: str) -> str:
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError(f"command failed ({p.returncode}): {cmd}\n{p.stderr.strip()[:400]}")
    return p.stdout


def parse_snapshot(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    mcp = re.search(r"## MCP 工具（(\d+)）(.*?)(?=\n## CLI 命令)", text, re.S)
    cli = re.search(r"## CLI 命令（(\d+)）(.*?)(?=\n## 官方 prompt)", text, re.S)
    if not mcp or not cli:
        raise ValueError("snapshot missing MCP/CLI sections")

    tools: dict[str, dict[str, str]] = {}
    for line in mcp.group(2).splitlines():
        mm = re.match(r"\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|", line)
        if mm:
            tools[mm.group(1)] = {"description": mm.group(2), "effect": mm.group(3).strip()}

    cmds: dict[str, str] = {}
    for line in cli.group(2).splitlines():
        mm = re.match(r"\|\s*`rea\s+([^`]+)`\s*\|\s*(.*?)\s*\|\s*$", line)
        if mm:
            cmds["rea " + mm.group(1).split()[0]] = mm.group(2)

    def anchor(label: str) -> str | None:
        mm = re.search(r"\|\s*" + re.escape(label) + r"\s*\|\s*([^|]+?)\s*\|", text)
        return mm.group(1).strip() if mm else None

    def digest(label: str) -> str | None:
        mm = re.search(r"\|\s*" + re.escape(label) + r"\s*\|\s*`([^`]+)`", text)
        return mm.group(1) if mm else None

    return {
        "version": anchor("REA CLI 版本"),
        "tools": tools,
        "cli": cmds,
        "declared_tool_count": int(mcp.group(1)),
        "declared_cli_count": int(cli.group(1)),
        "digest": digest("目录摘要"),
        "tools_digest": digest("工具目录摘要"),
    }


def parse_live(package_root: Path) -> dict:
    cat = json.loads((package_root / "dist" / "mcp-catalog.json").read_text(encoding="utf-8"))
    caps = json.loads(run("rea capabilities --format json"))
    llms = run("rea --llms")
    doc = json.loads(run("rea mcp doctor --json"))

    raw_eff: dict[str, set[str]] = {}
    for provider in caps.get("capabilities", []):
        for group in provider.get("groups", []):
            for op in group.get("operations", []):
                raw_eff.setdefault(op, set()).update(group.get("effects", []))

    tools: dict[str, dict[str, str]] = {}
    for tool in cat["tools"]:
        name = tool["name"]
        effects = sorted(EFFECT_LABELS[e] for e in raw_eff.get(name, []) if e in EFFECT_LABELS)
        effect_text = ", ".join(effects) if effects else "—"
        for provider in caps.get("capabilities", []):
            for group in provider.get("groups", []):
                if name in group.get("operations", []) and not group.get("available", True):
                    effect_text += "；不可用：" + str(group.get("availability_code") or "unavailable")
                    break
        tools[name] = {
            "description": " ".join(tool.get("description", "").split()),
            "effect": effect_text,
        }

    cli: dict[str, str] = {}
    for line in llms.splitlines():
        mm = re.match(r"\|\s*`rea\s+([^`]+)`\s*\|\s*(.*?)\s*\|\s*$", line)
        if mm:
            cli["rea " + mm.group(1).split()[0]] = mm.group(2).strip()

    pkg = json.loads((package_root / "package.json").read_text(encoding="utf-8"))
    identity = doc.get("identity", {})
    catalog = caps.get("server_identity", {}).get("catalog", {})
    return {
        "version": pkg.get("version"),
        "tools": tools,
        "cli": cli,
        "doctor_tools": doc.get("inventory", {}).get("tools", {}),
        "digest": identity.get("observed_catalog_digest"),
        "tools_digest": catalog.get("digests", {}).get("tools_sha256"),
        "counts": catalog.get("counts", {}),
    }


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Check REA tool/CLI/anchor drift against a baseline toolset snapshot (read-only).")
    ap.add_argument("--base", required=True,
                    help="baseline toolset markdown, e.g. references/toolset/rea-6.8.0.md")
    ap.add_argument("--package-root",
                    help="installed rea-agents root; default from npm root -g")
    ap.add_argument("--format", choices=["json", "md"], default="md",
                    help="output format (default: md)")
    ap.add_argument("--offset", type=int, default=0,
                    help="skip first N delta rows in md output")
    ap.add_argument("--limit", type=int, default=100,
                    help="max delta rows in md output (0 = all)")
    args = ap.parse_args()

    try:
        base = parse_snapshot(Path(args.base))
        root = (Path(args.package_root) if args.package_root
                else Path(run("npm root -g").strip().splitlines()[-1]) / "rea-agents")
        live = parse_live(root)

        added_tools = sorted(set(live["tools"]) - set(base["tools"]))
        removed_tools = sorted(set(base["tools"]) - set(live["tools"]))
        added_cli = sorted(set(live["cli"]) - set(base["cli"]))
        removed_cli = sorted(set(base["cli"]) - set(live["cli"]))

        renamed = []
        for old in removed_tools:
            pairs = sorted(
                ((SequenceMatcher(None, norm(base["tools"][old]["description"])[:180],
                                  norm(live["tools"][new]["description"])[:180]).ratio(), new)
                 for new in added_tools), reverse=True)
            if pairs and pairs[0][0] >= 0.55:
                renamed.append({"from": old, "to": pairs[0][1],
                                "similarity": round(pairs[0][0], 2)})

        desc_changed = []
        for name in sorted(set(base["tools"]) & set(live["tools"])):
            a = norm(base["tools"][name]["description"])[:100]
            b = norm(live["tools"][name]["description"])[:100]
            if a != b:
                desc_changed.append({
                    "name": name,
                    "similarity": round(SequenceMatcher(None, a, b).ratio(), 2),
                })

        effect_changed = []
        for name in sorted(set(base["tools"]) & set(live["tools"])):
            before = base["tools"][name]["effect"]
            after = live["tools"][name]["effect"]
            if after and before != after:
                effect_changed.append({"name": name, "from": before, "to": after})

        digest_changed = {
            "catalog": base["digest"] != live["digest"],
            "tools": base["tools_digest"] != live["tools_digest"],
        }
        material = bool(added_tools or removed_tools or added_cli or removed_cli
                        or renamed or effect_changed or any(digest_changed.values())
                        or any(x["similarity"] < 0.60 for x in desc_changed))
        drift = material or bool(desc_changed)

        data = {
            "base": {"path": args.base, "version": base["version"],
                     "tools": base["declared_tool_count"], "cli": base["declared_cli_count"]},
            "live": {"version": live["version"], "tools": len(live["tools"]),
                     "cli": len(live["cli"]), "counts": live["counts"]},
            "added_tools": [{"name": n, "description": live["tools"][n]["description"],
                             "effect": live["tools"][n]["effect"]} for n in added_tools],
            "removed_tools": removed_tools,
            "rename_candidates": renamed,
            "description_changed": desc_changed,
            "effect_changed": effect_changed,
            "added_cli": added_cli,
            "removed_cli": removed_cli,
            "digest_changed": digest_changed,
            "material_drift": material,
            "drift": drift,
        }

        if args.format == "json":
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"REA drift: {'DRIFT' if drift else 'NO DRIFT'} | "
                  f"base={base['version']} live={live['version']}")
            print(f"MCP +{len(added_tools)}/-{len(removed_tools)} | "
                  f"CLI +{len(added_cli)}/-{len(removed_cli)} | "
                  f"rename={len(renamed)} | description={len(desc_changed)} | "
                  f"effect={len(effect_changed)} | material={'yes' if material else 'no'}")
            rows = []
            rows += [("ADDED_TOOL", x["name"], x["description"][:160]) for x in data["added_tools"]]
            rows += [("REMOVED_TOOL", n, "") for n in removed_tools]
            rows += [("RENAME?", x["from"] + " -> " + x["to"], str(x["similarity"]))
                     for x in renamed]
            rows += [("DESC", x["name"], str(x["similarity"])) for x in desc_changed]
            rows += [("EFFECT", x["name"], x["from"] + " -> " + x["to"])
                     for x in effect_changed]
            rows += [("ADDED_CLI", n, "") for n in added_cli]
            rows += [("REMOVED_CLI", n, "") for n in removed_cli]
            end = None if args.limit == 0 else args.offset + args.limit
            for kind, name, detail in rows[args.offset:end]:
                print(f"- {kind}: {name}" + (f" :: {detail}" if detail else ""))
            if material:
                print("Intent review required: for each ADDED_TOOL, decide (a) what it does, "
                      "(b) which user intent triggers it, (c) whether rea-pilot should route/call it.")
        return 1 if drift else 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
