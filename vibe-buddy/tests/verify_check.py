#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""vibe-check 的 C1–C10 体检项可执行验收。

造一个有 5 处缺陷的档案，验证体检规则能逐项命中；
再造一个健康档案，验证不误报。
"""
import json, re, shutil, sys, tempfile
from pathlib import Path

FAIL = []
def check(name, cond, detail=""):
    print(("PASS" if cond else "FAIL"), name, detail)
    if not cond:
        FAIL.append(name)

def read(p): return p.read_text(encoding="utf-8") if p.exists() else ""

def checkup(root: Path):
    """按 check-artifacts.md 的 C1–C10 实现体检，返回问题列表 [(项号, 证据, 修复入口)]。"""
    issues = []
    agents = root / "AGENTS.md"
    da = root / "docs" / "agents"

    # C1 AGENTS.md 存在且六节完整
    if not agents.exists():
        issues.append(("C1", "AGENTS.md 不存在", "vibe-init"))
    else:
        t = read(agents)
        for sec in ["Permissions", "Toolchain", "Commands", "Conventions", "References"]:
            if sec not in t:
                issues.append(("C1", f"AGENTS.md 缺 {sec} 节", "vibe-init"))

    # C2 体量 ≤500
    if agents.exists():
        n = read(agents).count("\n")
        if n > 500:
            issues.append(("C2", f"AGENTS.md {n} 行 > 500", "vibe-init"))

    # C3 References 指针形态
    if agents.exists():
        t = read(agents)
        m = re.search(r"## References\n(.*?)(?=\n## |\Z)", t, re.S)
        if m:
            for line in m.group(1).split("\n"):
                if line.startswith("- ") and "→ 见" not in line:
                    issues.append(("C3", f"References 非条件式指针: {line[:40]}", "vibe-init"))

    # C4 引用路径存在
    if agents.exists():
        for p in re.findall(r"`([^`]+\.md)`", read(agents)):
            if p.startswith("docs/") and not (root / p).exists():
                issues.append(("C4", f"引用路径不存在: {p}", "vibe-init"))

    # C5 updated 滞后
    for f in da.glob("*.md"):
        t = read(f)
        m = re.search(r"^updated:\s*(\d{4}-\d{2}-\d{2})", t, re.M)
        if m:
            dates = re.findall(r"(\d{4}-\d{2}-\d{2})", t)
            if dates:
                newest = max(dates)
                if newest > m.group(1):
                    issues.append(("C5", f"{f.name}: updated={m.group(1)} 但内容有 {newest}", "vibe-sync"))

    # C6 编号连续（含 archive/）
    ids = []
    for f in list(da.glob("decision-log.md")) + list((da / "archive").glob("decision-*.md")):
        ids += [int(x) for x in re.findall(r"^## DEC-(\d{3}):", read(f), re.M)]
    if ids:
        ids.sort()
        for a, b in zip(ids, ids[1:]):
            if b != a + 1:
                issues.append(("C6", f"DEC 编号断号: {a} → {b}", "vibe-sync"))
        if len(ids) != len(set(ids)):
            issues.append(("C6", "DEC 编号重号", "vibe-sync"))

    # C7 双台账一致
    cl = da / "experience" / "changelog.md"
    idx = da / "experience" / ".distill-index.json"
    if cl.exists() and idx.exists():
        ranges_cl = set(re.findall(r"(\w{7}\.\.[\w\u4e00-\u9fa5]+)", read(cl)))
        try:
            j = json.loads(read(idx))
            ranges_idx = set(str(r.get("range")) for r in j if isinstance(r, dict))
        except Exception:
            ranges_idx = set()
        if ranges_cl and ranges_idx and ranges_cl != ranges_idx:
            issues.append(("C7", "changelog 与 .distill-index 区间不一致", "vibe-distill"))

    # C8 超阈值
    lim = {"project-progress.md": ("lines", 300), "decision-log.md": ("entries", 200), "debug-log.md": ("entries", 100)}
    for name, (kind, cap) in lim.items():
        f = da / name
        if f.exists():
            t = read(f)
            v = t.count("\n") if kind == "lines" else len(re.findall(r"^## (DEC|BUG)-\d{3}:", t, re.M))
            if v > cap:
                issues.append(("C8", f"{name} {v} > {cap}", "vibe-sync"))
    hd = root / "docs" / "handoff"
    if hd.exists():
        n = len(list(hd.glob("*.md")))
        if n > 30:
            issues.append(("C8", f"handoff {n} 份 > 30", "vibe-handoff"))

    # C9 交接可取最新（archive 不参与）
    if hd.exists():
        for p in hd.glob("*.md"):
            if not re.search(r"handoff-\d{4}-\d{2}-\d{2}", p.name):
                issues.append(("C9", f"命名不合规: {p.name}", "vibe-handoff"))

    # C10 写者边界：agents-changelog 出现非契约变更记录
    ac = da / "agents-changelog.md"
    if ac.exists():
        for line in read(ac).split("\n"):
            if line.startswith("- ") and "→" not in line:
                issues.append(("C10", f"agents-changelog 条目缺处置箭头: {line[:40]}", "人工判断"))
    return issues

# ---------- 缺陷夹具 ----------
tmp = Path(tempfile.mkdtemp(prefix="vb-chk-"))
try:
    (tmp / "docs/agents/archive").mkdir(parents=True)
    (tmp / "docs/agents/experience").mkdir(parents=True)
    (tmp / "docs/handoff").mkdir(parents=True)

    # 缺陷 1：AGENTS.md 缺 Conventions 节 + References 有裸指针 + 引用不存在路径
    (tmp / "AGENTS.md").write_text("""# AGENTS.md

## Permissions
YOU MUST 做某事

## Toolchain
| 工具 | 版本 |

## Commands
| 场景 | 命令 |

## References
- 见 docs/agents/project-progress.md
- 要查决策 → 见 `docs/agents/nonexistent.md`：不存在的文件
""", encoding="utf-8")

    # 缺陷 2：updated 滞后
    (tmp / "docs/agents/project-progress.md").write_text("""---
title: P
updated: 2026-09-01
---
## 当前状态
- **最后更新**：2026-11-20 新内容
""", encoding="utf-8")

    # 缺陷 3：DEC 跳号
    (tmp / "docs/agents/decision-log.md").write_text("""---
title: D
updated: 2026-11-27
---
## DEC-001: a
## DEC-002: b
## DEC-004: d
""", encoding="utf-8")

    # 缺陷 4：双台账不一致
    (tmp / "docs/agents/experience/changelog.md").write_text(
        "---\ntitle: C\nupdated: 2026-11-27\n---\n2026-11-20 | aaa1111..bbb2222 | +X | skip:\n", encoding="utf-8")
    (tmp / "docs/agents/experience/.distill-index.json").write_text(
        json.dumps([{"range": "ccc3333..ddd4444"}], ensure_ascii=False), encoding="utf-8")

    # 缺陷 5：handoff 命名不合规
    (tmp / "docs/handoff/2026-11-20-notes.md").write_text("---\ntitle: h\n---\n", encoding="utf-8")

    issues = checkup(tmp)
    codes = [i[0] for i in issues]
    print("== 缺陷夹具体检结果 ==")
    for c, ev, fix in issues:
        print(f"   {c}: {ev}  →  {fix}")
    print()

    for c in ["C1", "C3", "C4", "C5", "C6", "C7", "C9"]:
        check(f"命中 {c}", c in codes)
    check("C1 缺 Conventions 被识别", any("Conventions" in ev for c, ev, _ in issues))
    check("C3 裸指针被识别", any(c == "C3" for c, _, _ in issues))
    check("C4 断链被识别", any("nonexistent" in ev for _, ev, _ in issues))
    check("C5 updated 滞后被识别", any("2026-09-01" in ev for _, ev, _ in issues))
    check("C6 跳号被识别", any("2 → 4" in ev for _, ev, _ in issues))
    check("C9 命名不合规被识别", any("notes" in ev for _, ev, _ in issues))
    check("每条都带修复入口", all(fix for _, _, fix in issues))

    # 体检不写文件
    before = {p: p.stat().st_mtime for p in tmp.rglob("*") if p.is_file()}
    checkup(tmp)
    after = {p: p.stat().st_mtime for p in tmp.rglob("*") if p.is_file()}
    check("体检零写入", before == after)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# ---------- 健康夹具：不误报 ----------
tmp2 = Path(tempfile.mkdtemp(prefix="vb-ok-"))
try:
    (tmp2 / "docs/agents/experience").mkdir(parents=True)
    (tmp2 / "docs/handoff").mkdir(parents=True)
    (tmp2 / "AGENTS.md").write_text("""# AGENTS.md

## Permissions
YOU MUST 做某事

## Toolchain
| 工具 |

## Commands
| 场景 |

## Conventions
| 现象 | 行为 |

## References
- 查进度 → 见 `docs/agents/project-progress.md`：当前阶段
""", encoding="utf-8")
    (tmp2 / "docs/agents/project-progress.md").write_text("---\nupdated: 2026-11-27\n---\n## 当前状态\n", encoding="utf-8")
    (tmp2 / "docs/agents/decision-log.md").write_text("---\nupdated: 2026-11-27\n---\n## DEC-001: a\n## DEC-002: b\n", encoding="utf-8")
    (tmp2 / "docs/handoff/handoff-2026-11-27.md").write_text("---\ntitle: h\n---\n", encoding="utf-8")

    issues2 = checkup(tmp2)
    print("\n== 健康夹具体检结果 ==")
    for c, ev, fix in issues2:
        print(f"   {c}: {ev}")
    check("健康档案零误报", len(issues2) == 0, f"{len(issues2)} 条：{issues2}")
finally:
    shutil.rmtree(tmp2, ignore_errors=True)

print("\n" + "=" * 46)
print(f"FAIL {len(FAIL)}")
if FAIL:
    print("未通过：", FAIL)
    sys.exit(1)
print("全部通过")
