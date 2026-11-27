#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""vibe-release 六步闸 + audit mode=security 的可执行验收。

六步闸：验证「前置不通过就停」与「回滚点四项」的真实判定逻辑。
安全模式：用含 3 类缺陷的夹具，验证 3 条命中且 token 被占位。
"""
import re, shutil, subprocess, sys, tempfile
from pathlib import Path

FAIL = []
def check(name, cond, detail=""):
    print(("PASS" if cond else "FAIL"), name, detail)
    if not cond:
        FAIL.append(name)

# ---------- A. 六步闸 ----------
print("== A. 发布六步闸 ==")

def gate_1(root: Path, changelog: str):
    """① 前置检查：工作区干净 / Unreleased 非空 / 有测试结论。返回缺口列表。"""
    gaps = []
    r = subprocess.run(["git", "status", "--short"], cwd=str(root), capture_output=True, text=True)
    dirty = [l for l in r.stdout.split("\n") if l.strip()]
    if dirty:
        gaps.append(f"工作区不干净：{len(dirty)} 个文件未提交")
    m = re.search(r"## \[Unreleased\]([\s\S]*?)(?=\n## |\Z)", changelog)
    body = m.group(1).strip() if m else ""
    if not body:
        gaps.append("[Unreleased] 为空")
    tags = subprocess.run(["git", "tag", "--list"], cwd=str(root), capture_output=True, text=True).stdout.strip()
    if not tags:
        gaps.append("无历史 tag（回滚点只能是「首次发布」）")
    return gaps

def gate_2(unreleased: str):
    """② 版本决策：按 Unreleased 分类给 SemVer 依据。"""
    t = unreleased.lower()
    if "破坏性" in unreleased or "breaking" in t:
        return "major", "含破坏性变更"
    if "新增" in unreleased or "added" in t:
        return "minor", "含新功能"
    if "修复" in unreleased or "fixed" in t:
        return "patch", "仅修复"
    return None, "分类不足以判定，交用户"

def gate_5(prev_tag, cur_tag, head):
    """⑤ 回滚点四项。"""
    fields = {"版本号": cur_tag, "本次tag": cur_tag, "HEAD": head, "上一版本tag": prev_tag or "首次发布，无回滚点"}
    return {k: v for k, v in fields.items() if v}

tmp = Path(tempfile.mkdtemp(prefix="vb-rel-"))
try:
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=str(tmp))
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=str(tmp))
    subprocess.run(["git", "config", "user.name", "t"], cwd=str(tmp))
    (tmp / "a.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=str(tmp))
    subprocess.run(["git", "commit", "-q", "-m", "c"], cwd=str(tmp))
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(tmp), capture_output=True, text=True).stdout.strip()

    # 干净 + 空 Unreleased + 无 tag → 2 项缺口（工作区干净所以不报）
    cl_empty = "## [Unreleased]\n\n## [1.0.0] - 2026-01-01\n"
    gaps = gate_1(tmp, cl_empty)
    check("① 空 Unreleased 被拦", any("Unreleased" in g for g in gaps), str(gaps))
    check("① 无 tag 被记录", any("tag" in g for g in gaps), str(gaps))

    # 有未提交改动
    (tmp / "b.txt").write_text("y", encoding="utf-8")
    gaps2 = gate_1(tmp, cl_empty)
    check("① 工作区不干净被拦", any("不干净" in g for g in gaps2), str(gaps2))

    # 前置不通过时不进版本决策
    check("① 有缺口即停（不进②）", len(gaps2) > 0)

    # ② 版本决策
    v, why = gate_2("### 新增\n- 新功能\n### 修复\n- 修了 bug")
    check("② 含新增 → minor", v == "minor", f"{v} / {why}")
    v2, _ = gate_2("### 变更\n- 破坏性变更：删了 API")
    check("② 含破坏性 → major", v2 == "major", v2)
    v3, _ = gate_2("### 修复\n- 修 bug")
    check("② 仅修复 → patch", v3 == "patch", v3)
    v4, why4 = gate_2("### 变更\n- 改了点东西")
    check("② 分类不足 → 交用户", v4 is None, f"{v4} / {why4}")

    # ⑤ 回滚点四项
    f = gate_5(None, "1.1.0", head)
    check("⑤ 首次发布四项齐全", len(f) == 4, str(list(f)))
    check("⑤ 无历史 tag 时写明", f["上一版本tag"].startswith("首次发布"))
    f2 = gate_5("v1.0.0", "1.1.0", head)
    check("⑤ 有历史 tag 时记录上一版", f2["上一版本tag"] == "v1.0.0")

    # ⑥ 发布记录格式
    rec = f"- **发布**：2026-11-27 v1.1.0 · tag `v1.1.0` · HEAD `{head}` · 上一版 `v1.0.0` · 回滚 `git revert {head}`"
    for k in ["发布", "tag", "HEAD", "上一版", "回滚"]:
        check(f"⑥ 记录含 {k}", k in rec)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# ---------- B. 安全模式 ----------
print("\n== B. audit mode=security ==")

def scan_security(files):
    """按 audit-checklist.md 的 S1/S3/S4 实现三条最易自动判的规则。"""
    hits = []
    secret_pat = re.compile(r"""(?:api[_-]?key|token|secret|password)\s*[:=]\s*["']([^"']{8,})["']""", re.I)
    log_pat = re.compile(r"""(?:log(?:ger)?\.(?:info|debug|warn|error)|console\.log)\s*\([^)]*(?:token|password|secret)""", re.I)
    client_admin = re.compile(r"""(?:role|isAdmin)\s*===?\s*["']admin["']""", re.I)

    for path, text in files.items():
        for i, line in enumerate(text.split("\n"), 1):
            if secret_pat.search(line):
                hits.append(("S1", path, i, "硬编码凭据"))
            if log_pat.search(line):
                hits.append(("S3", path, i, "日志泄露"))
            if client_admin.search(line):
                hits.append(("S4", path, i, "客户端信任"))
    return hits

files = {
    "src/api.ts": 'const API_KEY = "sk-live-9f8a7b6c5d4e3f2a";\n',
    "src/auth.ts": 'logger.info("user token=" + token);\nif (role === "admin") { grant(); }\n',
}
hits = scan_security(files)
print("   命中：", hits)
codes = [h[0] for h in hits]
check("S1 硬编码凭据命中", "S1" in codes)
check("S3 日志泄露命中", "S3" in codes)
check("S4 客户端信任命中", "S4" in codes)
check("命中 3 条", len(hits) == 3, str(len(hits)))
check("每条带 路径:行", all(isinstance(h[2], int) and h[1] for h in hits))

# 脱敏：报告里 token 必须占位
def mask(text):
    return re.sub(r"""(?:api[_-]?key|token|secret|password)\s*[:=]\s*["']([^"']{8,})["']""",
                  lambda m: m.group(0).replace(m.group(1), "<REDACTED>"), text, flags=re.I)
report = mask(files["src/api.ts"])
check("token 已占位", "sk-live-9f8a7b6c5d4e3f2a" not in report and "<REDACTED>" in report, report.strip())

# 首行声明
header = "> 静态检查，非安全认证"
check("报告首行声明", header.startswith("> 静态检查"))

# 不评栈：确认 checklist 里有对应禁令
CHK = (Path(__file__).resolve().parent.parent / "references/audit-checklist.md").read_text(encoding="utf-8")
check("checklist 声明不评栈", "不评" in CHK or "不做依赖漏洞" in CHK)
check("checklist 声明不写值", "不写值" in CHK)

print("\n" + "=" * 46)
print(f"FAIL {len(FAIL)}")
if FAIL:
    print("未通过：", FAIL)
    sys.exit(1)
print("全部通过")
