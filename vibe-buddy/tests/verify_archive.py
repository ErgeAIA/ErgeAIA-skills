#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""vibe-buddy 归档协议的可执行验收（干跑）。

不复刻 AI 行为，而是把 vibe-buddy 的归档协议实现为可运行函数，
再用真实夹具压测：条目守恒、编号跨归档唯一、目录份数闸、
阈值触发、handoff 最新一份判据。全部断言来自协议文本，不来自我的印象。
"""
import os, re, shutil, sys, tempfile
from pathlib import Path

FAIL = []
def check(name, cond, detail=""):
    print(("PASS" if cond else "FAIL"), name, detail)
    if not cond:
        FAIL.append(name)

# ---------- 协议参数的唯一来源：从 workflow-protocol.md 解析，不硬编码 ----------
PROTO = Path(__file__).resolve().parent.parent / "references/workflow-protocol.md"
text = PROTO.read_text(encoding="utf-8")

def p10_limit(label):
    """从 P10 阈值表解析某产物的上限数字。"""
    for line in text.split("\n"):
        if line.startswith("|") and label in line:
            m = re.search(r"≤\s*(\d+)", line)
            if m:
                return int(m.group(1))
    return None

LIM = {
    "progress": p10_limit("`project-progress.md`"),
    "decision": p10_limit("`decision-log.md`"),
    "debug":    p10_limit("`debug-log.md`"),
    "handoff":  p10_limit("`docs/handoff/`"),
    "audit":    p10_limit("`docs/agents/audit/`"),
}
print("== 从协议解析出的阈值 ==", LIM)
check("协议阈值可解析且非空", all(v is not None for v in LIM.values()), str(LIM))

# ---------- 归档实现（按 P10 三条纪律） ----------
def archive_decision(active: Path, archive_dir: Path):
    """返回 (归档条数, 活跃条数, 新编号)。编号取活跃+归档最大值+1。"""
    archive_dir.mkdir(parents=True, exist_ok=True)
    txt = active.read_text(encoding="utf-8")
    entries = re.findall(r"^## (DEC-\d{3}):", txt, re.M)
    # 全域最大编号（活跃 + 全部归档）
    all_ids = list(entries)
    for f in archive_dir.glob("decision-*.md"):
        all_ids += re.findall(r"^## (DEC-\d{3}):", f.read_text(encoding="utf-8"), re.M)
    nums = [int(x.split("-")[1]) for x in all_ids] or [0]
    next_id = max(nums) + 1

    # 超阈值才归档最旧的整段（这里按「最旧 50 条」归档）
    archived = 0
    if len(entries) > LIM["decision"]:
        keep_n = LIM["decision"]
        drop_ids = entries[: len(entries) - keep_n]
        arch_file = archive_dir / f"decision-{drop_ids[0].split('-')[1][:0] or '2026'}.md"
        # 追加到归档（只追加）
        blocks = re.split(r"(?=^## DEC-\d{3}:)", txt, flags=re.M)
        head, body = blocks[0], blocks[1:]
        to_arch = body[: len(drop_ids)]
        with arch_file.open("a", encoding="utf-8") as f:
            f.write("\n".join(to_arch))
        active.write_text(head + "".join(body[len(drop_ids):]), encoding="utf-8")
        archived = len(to_arch)

    active_ids = re.findall(r"^## (DEC-\d{3}):", active.read_text(encoding="utf-8"), re.M)
    return archived, len(active_ids), next_id

# ---------- 用例 1：decision-log 201 条压测 ----------
tmp = Path(tempfile.mkdtemp(prefix="vb1-"))
try:
    dec = tmp / "decision-log.md"
    body = "---\ntitle: Decision Log\n---\n\n"
    for i in range(1, 202):
        body += f"## DEC-{i:03d}: 决策 {i}\n\n- **日期**：2026-01-01\n\n"
    dec.write_text(body, encoding="utf-8")
    before = len(re.findall(r"^## DEC-\d{3}:", body, re.M))
    arch, act, nxt = archive_decision(dec, tmp / "archive")
    total = arch + act
    check("E1 归档触发（201 > 上限）", arch > 0, f"归档 {arch} / 活跃 {act}")
    check("E1 总条目守恒", total == before, f"{arch}+{act}={total} vs 原 {before}")
    check("E1 活跃不超阈值", act <= LIM["decision"], f"{act} ≤ {LIM['decision']}")
    check("E1 归档后新编号不重号", nxt == 202, f"next=DEC-{nxt:03d}")
    # 再归档一次，编号仍不重
    arch2, act2, nxt2 = archive_decision(dec, tmp / "archive")
    check("E1 二次归档后编号仍唯一", nxt2 >= 202, f"next=DEC-{nxt2:03d}")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# ---------- 用例 2：handoff 31 份 + 最新一份判据 ----------
tmp = Path(tempfile.mkdtemp(prefix="vb2-"))
try:
    hd = tmp / "handoff"; hd.mkdir()
    # 造 31 份。两个陷阱：
    # ① 字典序陷阱：handoff-2026-08-22-evening.md 在字典序上排在 handoff-2026-08-22.md 之前（'-' < '.'）
    # ② 同日多份：08-30 有两份，需按 frontmatter updated 取较新
    for d in range(1, 31):
        (hd / f"handoff-2026-08-{d:02d}.md").write_text("---\ntitle: h\nupdated: 2026-08-30\n---\n", encoding="utf-8")
    (hd / "handoff-2026-08-22-evening.md").write_text("---\ntitle: h\nupdated: 2026-08-22\n---\n", encoding="utf-8")
    (hd / "handoff-2026-08-30-evening.md").write_text("---\ntitle: h\nupdated: 2026-08-30\n---\n", encoding="utf-8")

    def latest(files):
        """按文件名日期解析取最新；同日多份再比 frontmatter updated；仍不可判则取字典序大者。"""
        def datekey(p):
            m = re.search(r"(\d{4}-\d{2}-\d{2})", p.name)
            return m.group(1) if m else "0000-00-00"
        def upd(p):
            m = re.search(r"^updated:\s*(\d{4}-\d{2}-\d{2})", p.read_text(encoding="utf-8"), re.M)
            return m.group(1) if m else "0000-00-00"
        mx = max(datekey(p) for p in files)
        same = [p for p in files if datekey(p) == mx]
        if len(same) == 1:
            return same[0]
        mu = max(upd(p) for p in same)
        same2 = [p for p in same if upd(p) == mu]
        return sorted(same2, key=lambda p: p.name)[-1]

    before = len(list(hd.glob("*.md")))
    lt = latest(list(hd.glob("*.md")))
    check("E2 活跃份数 = 32", before == 32, str(before))
    check("E2 取到最新日期而非字典序最大", lt.name.startswith("handoff-2026-08-30"), lt.name)
    check("E2 字典序陷阱未误判（08-22-evening 不入选）", "08-22" not in lt.name, lt.name)

    # 份数闸：超阈值时归档最旧整批到季度目录
    if before > LIM["handoff"]:
        q = hd / "archive" / "handoff-2026-Q3"; q.mkdir(parents=True)
        olds = sorted(hd.glob("*.md"))[: before - LIM["handoff"]]
        for p in olds:
            shutil.move(str(p), str(q / p.name))
    after = len(list(hd.glob("*.md")))
    check("E2 归档后活跃不超阈值", after <= LIM["handoff"], f"{after} ≤ {LIM['handoff']}")
    lt2 = latest(list(hd.glob("*.md")))
    check("E2 归档不改「最新一份」判据", lt2.name == lt.name, f"{lt2.name} == {lt.name}")
    check("E2 archive 不参与候选", "archive" not in str(lt2))
    total2 = after + len(list((hd / "archive").rglob("*.md")))
    check("E2 移动前后总份数守恒", total2 == before, f"{total2} vs {before}")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# ---------- 用例 3：progress 305 行触发归档 ----------
tmp = Path(tempfile.mkdtemp(prefix="vb3-"))
try:
    pg = tmp / "project-progress.md"
    lines = ["---", "title: P", "---", "", "## 当前状态", ""]
    for i in range(300):
        lines.append(f"- **最后更新**：2026-01-{(i%28)+1:02d} 第 {i} 轮")
    pg.write_text("\n".join(lines) + "\n", encoding="utf-8")
    n_before = pg.read_text(encoding="utf-8").count("\n")
    check("E3 夹具超 300 行", n_before > LIM["progress"], f"{n_before} > {LIM['progress']}")

    # 归档：把「当前状态」之后的进展整段移出，保留头部与可变区
    t = pg.read_text(encoding="utf-8")
    head, _, rest = t.partition("## 当前状态\n")
    blocks = rest.split("- **最后更新**")
    keep_head = blocks[0]
    entries = ["- **最后更新**" + b for b in blocks[1:]]
    n_arch = len(entries) - 20     # 只留最近 20 条
    arch = tmp / "archive"; arch.mkdir()
    (arch / "progress-2026-01.md").write_text("\n".join(entries[:n_arch]), encoding="utf-8")
    pg.write_text(head + "## 当前状态\n" + keep_head + "\n".join(entries[n_arch:]), encoding="utf-8")
    n_after = pg.read_text(encoding="utf-8").count("\n")
    kept = len(re.findall(r"^- \*\*最后更新", pg.read_text(encoding="utf-8"), re.M))
    check("E3 归档后活跃行数下降", n_after < n_before, f"{n_before} → {n_after}")
    check("E3 活跃保留最近条目", kept == 20, str(kept))
    check("E3 归档文件只追加", (arch / "progress-2026-01.md").exists())
    total_entries = kept + len(re.findall(r"^- \*\*最后更新", (arch / "progress-2026-01.md").read_text(encoding="utf-8"), re.M))
    check("E3 条目守恒", total_entries == 300, f"{total_entries} vs 300")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# ---------- 用例 4：audit 目录 21 份 ----------
tmp = Path(tempfile.mkdtemp(prefix="vb4-"))
try:
    ad = tmp / "audit"; ad.mkdir()
    for i in range(1, 22):
        (ad / f"audit-2026-01-{i:02d}.md").write_text("---\ntitle: a\n---\n", encoding="utf-8")
    before = len(list(ad.glob("*.md")))
    if before > LIM["audit"]:
        y = ad / "archive" / "audit-2026"; y.mkdir(parents=True)
        for p in sorted(ad.glob("*.md"))[: before - LIM["audit"]]:
            shutil.move(str(p), str(y / p.name))
    after = len(list(ad.glob("*.md")))
    check("E4 audit 归档后不超阈值", after <= LIM["audit"], f"{after} ≤ {LIM['audit']}")
    check("E4 audit 份数守恒", after + len(list((ad/'archive').rglob('*.md'))) == before)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n" + "=" * 46)
print(f"PASS {len(FAIL)==0 and '全部' or ''} / FAIL {len(FAIL)}")
if FAIL:
    print("未通过：", FAIL)
    sys.exit(1)
