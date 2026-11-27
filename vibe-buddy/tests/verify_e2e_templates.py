#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""端到端：用 vibe-buddy 的模板初始化一个真实项目，再跑体检，验证模板可用。

这一步验证的是「模板自包含」的实质：把 5 份模板原样复制进目标项目后，
目标项目里没有任何技能文件，模板仍能独立成立（无断链、无内部路径引用）。
"""
import json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

FAIL = []
def check(name, cond, detail=""):
    print(("PASS" if cond else "FAIL"), name, detail)
    if not cond:
        FAIL.append(name)

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / "assets"

tmp = Path(tempfile.mkdtemp(prefix="vb-e2e-"))
try:
    # ---------- 1. 按 init 的目录树建项目 ----------
    da = tmp / "docs" / "agents"
    (da / "experience").mkdir(parents=True)
    (tmp / "docs" / "handoff").mkdir(parents=True)

    # 原样复制模板，只替换占位符（模拟 init 的真实动作）
    copies = {
        "docs/project-progress.md": da / "project-progress.md",
        "docs/decision-log.md":     da / "decision-log.md",
        "docs/debug-log.md":        da / "debug-log.md",
        "docs/agents-changelog.md": da / "agents-changelog.md",
        "docs/init-report.md":      da / "init-report.md",
        "experience/README.md":     da / "experience" / "README.md",
        "experience/changelog.md":  da / "experience" / "changelog.md",
    }
    for src, dst in copies.items():
        t = (ASSETS / src).read_text(encoding="utf-8")
        t = t.replace("<工程标识>", "demo-app").replace("<域标识>", "ui").replace("YYYY-MM-DD", "2026-11-27")
        dst.write_text(t, encoding="utf-8")

    check("模板全部复制成功", all(p.exists() for p in copies.values()), f"{len(list(copies.values()))} 份")

    # ---------- 2. 目标项目里不得有任何技能内部路径 ----------
    internal = re.compile(r"references/[a-z-]+\.md|workflow-protocol|SKILL\.md|audit-checklist|release-checklist")
    leaks = []
    for p in tmp.rglob("*.md"):
        for i, line in enumerate(p.read_text(encoding="utf-8").split("\n"), 1):
            if internal.search(line):
                leaks.append(f"{p.relative_to(tmp)}:{i}: {line.strip()[:60]}")
    check("目标项目零技能内部引用", not leaks, str(leaks))

    # ---------- 3. 断链检查：模板里引用的相对路径必须存在 ----------
    broken = []
    for p in tmp.rglob("*.md"):
        for link in re.findall(r"\]\(([^)]+\.md)\)", p.read_text(encoding="utf-8")):
            if link.startswith("http"): continue
            target = (p.parent / link).resolve()
            if not target.exists():
                broken.append(f"{p.relative_to(tmp)} → {link}")
    check("模板内相对链接无断链", not broken, str(broken))

    # ---------- 4. frontmatter 可解析（无未引号 ASCII 冒号） ----------
    fm_bad = []
    for p in tmp.rglob("*.md"):
        t = p.read_text(encoding="utf-8")
        lines = t.split("\n")
        if lines[0] != "---": continue
        try:
            e = lines.index("---", 1)
        except ValueError:
            fm_bad.append(f"{p.name}: 未闭合"); continue
        head = lines[1:e]
        for ln in head:
            if ln.startswith("description:") and not ln.startswith("description: ") and ">" not in ln:
                fm_bad.append(f"{p.name}: description 格式可疑")
            # 值里出现未引号 ": " 会破坏 YAML
            if ":" in ln and not ln.startswith(("description", "title", "project", "type", "updated")) and ln.count(": ") > 1:
                if not ln.strip().startswith("-"):
                    fm_bad.append(f"{p.name}: 疑似未引号冒号 → {ln[:40]}")
    check("frontmatter 结构可解析", not fm_bad, str(fm_bad))

    # ---------- 5. 模板里的阈值必须写具体数字（目标项目无协议文件） ----------
    pg = (da / "project-progress.md").read_text(encoding="utf-8")
    check("progress 模板含 300 行阈值", "300 行" in pg)
    check("progress 模板含机读台账示例", "<!-- vibe: produced=" in pg)
    cl = (da / "experience" / "changelog.md").read_text(encoding="utf-8")
    check("蒸馏台账含区间三写法", "已提交" in cl and "未提交" in cl and "HEAD..工作区" in cl)
    check("蒸馏台账含原因码", "no-rule" in cl and "covered-by" in cl)
    check("蒸馏台账含双台账一致性要求", ".distill-index.json" in cl)

    # ---------- 6. 体检：新初始化项目应几乎全通过 ----------
    def checkup(root):
        issues = []
        agents = root / "AGENTS.md"
        if not agents.exists():
            issues.append("C1 AGENTS.md 不存在")
        for f in (root / "docs/agents").glob("*.md"):
            t = f.read_text(encoding="utf-8")
            if "YYYY-MM-DD" in t:
                issues.append(f"C5 {f.name} 仍有未替换的占位日期")
        return issues

    # 模拟 init 生成一个最小 AGENTS.md
    (tmp / "AGENTS.md").write_text("""# AGENTS.md

## Permissions
YOU MUST 会话开始先读 docs/agents/ 三件套

## Toolchain
| 工具 | 版本 |

## Commands
| 场景 | 命令 |

## Conventions
| 现象 | 行为 |

## References
- 查进度 → 见 `docs/agents/project-progress.md`：当前阶段与下一步
""", encoding="utf-8")

    issues = checkup(tmp)
    print("\n== 新初始化项目体检 ==")
    for i in issues:
        print("   ", i)
    check("新项目无占位日期残留", not [i for i in issues if "占位日期" in i], str(issues))
    check("新项目 AGENTS.md 存在", not [i for i in issues if "不存在" in i])

    # ---------- 7. 真实 git init + 首次提交能跑通 ----------
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=str(tmp))
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=str(tmp))
    subprocess.run(["git", "config", "user.name", "t"], cwd=str(tmp))
    subprocess.run(["git", "add", "-A"], cwd=str(tmp))
    r = subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=str(tmp), capture_output=True, text=True)
    check("初始化产物可提交", r.returncode == 0, r.stderr[:80])
    r2 = subprocess.run(["git", "ls-files"], cwd=str(tmp), capture_output=True, text=True)
    n = len([l for l in r2.stdout.split("\n") if l])
    check("提交含 8 个文件", n == 8, str(n))

finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n" + "=" * 46)
print(f"FAIL {len(FAIL)}")
if FAIL:
    print("未通过：", FAIL)
    sys.exit(1)
print("全部通过")
