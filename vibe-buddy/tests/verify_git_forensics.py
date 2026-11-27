#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""vibe-audit 变更集取证的可执行验收（真实 Git 仓库）。

验证：白名单命令可跑、三重上限降级、密钥文件整文件跳过、
禁用的裸命令确实不在白名单里。
"""
import os, re, subprocess, shutil, sys, tempfile
from pathlib import Path

FAIL = []
def check(name, cond, detail=""):
    print(("PASS" if cond else "FAIL"), name, detail)
    if not cond:
        FAIL.append(name)

SKILL = Path(__file__).resolve().parent.parent
POLICY = (SKILL / "references/command-policy.md").read_text(encoding="utf-8")
PROTO = (SKILL / "references/workflow-protocol.md").read_text(encoding="utf-8")

# ---------- A. 白名单文本核对 ----------
print("== A. 白名单与上限文本 ==")
for cmd in ["git diff --numstat", "git diff --name-status", "git diff -U3 -- <path>",
            "git diff --cached -- <path>", "git merge-base HEAD <base>", "git log --oneline <base>..HEAD"]:
    check(f"白名单含 {cmd}", cmd in POLICY)

for forbidden in ["裸 `git diff`", "`git log -p`", "`git show`"]:
    check(f"显式禁止 {forbidden}", forbidden in POLICY)

# 三重上限从文本解析，不硬编码
m_files = re.search(r"文件数 \| (\d+)", POLICY)
m_lines = re.search(r"单文件 diff \| (\d+) 行", POLICY)
m_total = re.search(r"总输出 \| (\d+) KB", POLICY)
CAP_FILES = int(m_files.group(1)); CAP_LINES = int(m_lines.group(1)); CAP_TOTAL = int(m_total.group(1))
print(f"   解析上限：{CAP_FILES} 文件 / {CAP_LINES} 行 / {CAP_TOTAL} KB")
check("上限 = 30/400/80", (CAP_FILES, CAP_LINES, CAP_TOTAL) == (30, 400, 80), f"{CAP_FILES}/{CAP_LINES}/{CAP_TOTAL}")

# ---------- B. 真实仓库 ----------
print("\n== B. 真实仓库取证 ==")
tmp = Path(tempfile.mkdtemp(prefix="vb-git-"))
def run(*args, cwd=None):
    r = subprocess.run(args, cwd=str(cwd or tmp), capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout

try:
    run("git", "init", "-q", "-b", "main")
    run("git", "config", "user.email", "t@t.t")
    run("git", "config", "user.name", "t")

    # 基线：1 个文件
    (tmp / "app.py").write_text("print('v1')\n", encoding="utf-8")
    run("git", "add", "-A"); run("git", "commit", "-q", "-m", "base")

    # 改动：3 个源码文件 + 1 个密钥文件 + 1 个二进制
    (tmp / "app.py").write_text("print('v1')\nAPI_KEY = 'sk-REAL-SECRET-123'\nprint('v2')\n", encoding="utf-8")
    (tmp / "b.py").write_text("x = 1\n", encoding="utf-8")
    (tmp / "c.py").write_text("y = 2\n", encoding="utf-8")
    (tmp / "prod_secret.yaml").write_text("TOKEN=ghp_realsecret\n", encoding="utf-8")  # .env 被全局 gitignore，改用不被忽略的密钥文件名
    (tmp / "logo.bin").write_bytes(b"\x00\x01\x02" * 100)
    run("git", "add", "-A"); run("git", "commit", "-q", "-m", "change")

    # numstat 判规模
    rc, out = run("git", "diff", "--numstat", "HEAD~1..HEAD")
    check("numstat 可跑", rc == 0, f"rc={rc}")
    rows = [l for l in out.strip().split("\n") if l]
    check("numstat 行数 = 改动文件数", len(rows) == 5, f"{len(rows)} 行")
    bin_rows = [l for l in rows if l.startswith("-\t-\t")]
    check("二进制被标为 -\\t-", len(bin_rows) == 1, str(bin_rows))

    # name-status 定范围
    rc, out = run("git", "diff", "--name-status", "HEAD~1..HEAD")
    check("name-status 可跑", rc == 0)
    statuses = {l.split("\t")[-1]: l.split("\t")[0] for l in out.strip().split("\n") if l}
    check("新增文件标 A", statuses.get("b.py") == "A", str(statuses.get("b.py")))
    check("修改文件标 M", statuses.get("app.py") == "M", str(statuses.get("app.py")))

    # 三重上限：造 45 个改动文件，验证降级到前 30
    for i in range(45):
        (tmp / f"bulk_{i}.py").write_text("z=0\n", encoding="utf-8")
    run("git", "add", "-A"); run("git", "commit", "-q", "-m", "bulk")
    rc, out = run("git", "diff", "--numstat", "HEAD~1..HEAD")
    n_changed = len([l for l in out.strip().split("\n") if l])
    check("超上限夹具成立", n_changed == 45, str(n_changed))

    # 按 numstat 增删总量排序取前 CAP_FILES 个
    ranked = []
    for l in out.strip().split("\n"):
        if not l: continue
        add, dele, path = l.split("\t")
        w = (int(add) if add.isdigit() else 0) + (int(dele) if dele.isdigit() else 0)
        ranked.append((w, path))
    ranked.sort(key=lambda x: -x[0])
    selected = ranked[:CAP_FILES]
    check("降级后只取 30 个", len(selected) == CAP_FILES, str(len(selected)))
    uncovered = n_changed - len(selected)
    check("未覆盖数可算（15）", uncovered == 15, str(uncovered))

    # 单文件 400 行上限：造一个 800 行的文件
    (tmp / "big.py").write_text("\n".join(f"line{i}" for i in range(800)) + "\n", encoding="utf-8")
    run("git", "add", "-A"); run("git", "commit", "-q", "-m", "big")
    rc, out = run("git", "diff", "-U3", "HEAD~1..HEAD", "--", "big.py")
    diff_lines = out.count("\n")
    check("单文件 diff 超 400 行", diff_lines > CAP_LINES, f"{diff_lines} 行")
    truncated = "\n".join(out.split("\n")[:CAP_LINES])
    check("截断到 400 行可执行", truncated.count("\n") <= CAP_LINES, f"{truncated.count(chr(10))}")

    # 密钥文件整文件跳过
    secret_pat = re.compile(r"(\.env|\.pem|_key|credentials|secret)", re.I)
    all_files = [p for _, p in ranked] + ["big.py", "prod_secret.yaml"]
    skipped = [p for p in all_files if secret_pat.search(p)]
    check("密钥文件被识别并跳过", "prod_secret.yaml" in skipped, str(skipped))
    # 验证：跳过后读不到 token
    read_content = ""
    for p in all_files:
        if p in skipped: continue
        fp = tmp / p
        if fp.exists() and fp.suffix != ".bin":
            read_content += fp.read_text(encoding="utf-8", errors="replace")
    check("跳过后内容不含真实 token", "ghp_realsecret" not in read_content)

    # 禁止命令：确认裸 diff 输出无边界（说明为何禁）
    rc, out_bare = run("git", "diff", "HEAD~3..HEAD")
    check("裸 diff 输出远大于受控取证", out_bare.count("\n") > CAP_LINES, f"{out_bare.count(chr(10))} 行")

    # 非 Git 仓库：git log 返回 128 属正常状态
    nogit = Path(tempfile.mkdtemp(prefix="vb-nogit-"))
    r = subprocess.run(["git", "log", "--oneline", "-n", "1"], cwd=str(nogit), capture_output=True, text=True)
    check("非 Git 仓库 git log 返回非 0", r.returncode != 0, f"rc={r.returncode}")
    check("该情形被协议定义为正常状态", "非 Git 仓库跳过第一项" in PROTO)
    shutil.rmtree(nogit, ignore_errors=True)

    # merge-base 解析基线
    rc, out = run("git", "merge-base", "HEAD", "main")
    check("merge-base 可跑", rc == 0 and len(out.strip()) >= 7, out.strip()[:8])

finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n" + "=" * 46)
print(f"FAIL {len(FAIL)}")
if FAIL:
    print("未通过：", FAIL)
    sys.exit(1)
print("全部通过")
