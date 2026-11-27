#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""vibe-buddy 验收总运行器：一次跑完全部 5 组可执行验收并汇总。"""
import subprocess, sys
from pathlib import Path

HERE = Path(__file__).parent
SUITES = [
    ("归档协议（守恒/编号/份数闸）", "verify_archive.py"),
    ("Git 变更集取证（三重上限/脱敏）", "verify_git_forensics.py"),
    ("档案体检（C1–C10 命中与零误报）", "verify_check.py"),
    ("发布六步闸 + 安全模式", "verify_release_security.py"),
    ("端到端模板初始化", "verify_e2e_templates.py"),
    ("触发集干跑（路由/description/用例）", "verify_triggers.py"),
    ("vibe-req EARS 归类（五类/E-S判别/三问）", "verify_req.py"),
]

results = []
for name, script in SUITES:
    r = subprocess.run([sys.executable, str(HERE / script)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = r.stdout + r.stderr
    # 只统计形如 "PASS 断言名" / "FAIL 断言名" 的行；末尾的 "FAIL 0" 汇总是数字，排除
    lines = [l for l in out.split("\n")
             if (l.startswith("PASS ") or l.startswith("FAIL "))
             and not (len(l.split()) == 2 and l.split()[1].isdigit())]
    npass = sum(1 for l in lines if l.startswith("PASS "))
    nfail = sum(1 for l in lines if l.startswith("FAIL "))
    results.append((name, npass, nfail, r.returncode == 0))

print("\n" + "=" * 62)
print(f"{'验收组':<38} {'PASS':>5} {'FAIL':>5}  结果")
print("-" * 62)
tot_p = tot_f = 0
for name, p, f, ok in results:
    print(f"{name:<38} {p:>5} {f:>5}  {'通过' if ok else '未通过'}")
    tot_p += p; tot_f += f
print("-" * 62)
print(f"{'合计':<38} {tot_p:>5} {tot_f:>5}  {'全部通过' if tot_f == 0 else '有失败'}")
print("=" * 62)
sys.exit(0 if tot_f == 0 else 1)
