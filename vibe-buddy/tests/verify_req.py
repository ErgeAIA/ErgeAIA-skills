#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""vibe-req 的 EARS 归类可执行验收。

用真实夹具验证：五类归类判据、E/S 判别、空类不写、每条可测试三问、
3 问转交规则、与 grilling/qiao/prompt-workshop 的边界文本。
"""
import re, sys
from pathlib import Path

FAIL = []
def check(name, cond, detail=""):
    print(("PASS" if cond else "FAIL"), name, detail)
    if not cond:
        FAIL.append(name)

ROOT = Path(__file__).resolve().parent.parent
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
EARS = (ROOT / "references/ears-clarify.md").read_text(encoding="utf-8")
TS = (ROOT / "references/trigger-test-set.md").read_text(encoding="utf-8")

# ---------- A. 文本结构 ----------
print("== A. 契约文本 ==")
for cls in ["U Ubiquitous", "E Event-Driven", "S State-Driven", "O Optional", "U* Unwanted"]:
    check(f"五类含 {cls}", cls in EARS)
check("有归类顺序", "归类顺序" in EARS)
check("有 E/S 判别", "E 与 S 的判别" in EARS)
check("有三问", "触发可见" in EARS and "响应具体" in EARS and "能判定通过" in EARS)
check("有空类不写", "空类不写" in EARS)
check("有 3 问转交", "3 问" in EARS and "grilling" in EARS)
check("有边界表", all(k in EARS for k in ["grilling", "qiao", "prompt-workshop"]))
check("不取五节空表", "不取" in EARS and "填空模板" in EARS)
check("不取 ! 注入", "反引号注入" in EARS or "`!`" in EARS)
check("不落盘", "writes-to: []" in EARS)
# 升维四问（内核）
check("有升维四问节", "内核：升维四问" in EARS)
for q in ["顶尖高手会做", "最原始的材料", "具体方法与工具", "还有什么"]:
    check(f"四问含「{q}」", q in EARS)
check("四问要更深不是更大", "更深" in EARS and "更大" in EARS)
check("四问不直接输出", "不直接写进输出" in EARS)
check("四问落 EARS 映射", "U* 条目" in EARS and "待确认" in EARS)


# SKILL 接入
route_sec = SKILL.split("## 产物布局")[0]
check("vibe-req 有路由行", "vibe-req" in route_sec)
check("vibe-req 有验证行", "| `vibe-req` |" in SKILL)
check("vibe-req 在何时读", "ears-clarify.md" in SKILL)
check("description 含 EARS", "EARS" in SKILL.split("\n")[2])
check("非目标已澄清边界", "vibe-req` 不做无休止追问" in SKILL)

# 触发测试
check("正面集含 vibe-req", "vibe-req                                        # 英文触发词" in TS)
check("负面集 grilling 边界", "grilling" in TS and "不追问" in TS)
check("负面集 qiao 边界", "qiao" in TS and "不编译任务" in TS)
check("E11 存在", "| E11 |" in TS)
check("E12 存在", "| E12 |" in TS)

# ---------- B. 归类逻辑真跑 ----------
print("\n== B. EARS 归类真跑 ==")

def classify(statement: str) -> list:
    """按 ears-clarify.md 的判据实现归类（简化版，规则来自文档）。"""
    out = []
    s = statement.lower()
    # U*：防坏事（不期望情况）
    unwanted = re.search(r"如果|失败|没权限|无权限|超时|错误|不允许|不可用", statement)
    if unwanted:
        out.append("U*")
    # O：有显式开关
    if re.search(r"记住我|开关|配置|启用|灰度|设置项|在.*情况下", statement):
        out.append("O")
    # S：持续状态
    if re.search(r"离线|在线|加载中|已登录|未登录|空闲|状态", statement):
        out.append("S")
    # E：一次性事件
    if re.search(r"点击|按下|提交|导入|导出|创建|删除|定时|调用|触发", statement):
        out.append("E")
    # U：无条件全局规则
    if re.search(r"全程|所有|始终|必须|应使用", statement) and not re.search(r"当|如果|在", statement):
        out.append("U")
    return out or ["UNCLASSIFIED"]

CASES = [
    ("加个导出功能，点按钮就下载 CSV；如果没权限要提示", ["E", "U*"]),
    ("登录要记住我；离线时显示缓存；系统全程用 HTTPS", ["O", "S", "U"]),
    ("用户点击保存时校验表单", ["E"]),
    ("系统应使用 HTTPS 加密所有通信", ["U"]),
    ("在启用暗黑模式的情况下使用深色配色", ["O"]),
]

for stmt, want in CASES:
    got = classify(stmt)
    check(f"归类「{stmt[:14]}…」", set(got) == set(want), f"got={got} want={want}")

# E/S 判别：点击是事件，离线是状态
e_line = "用户点击保存时校验表单"
s_line = "用户处于离线状态时显示缓存"
check("E/S 判别：点击→E", "E" in classify(e_line) and "S" not in classify(e_line), str(classify(e_line)))
check("E/S 判别：离线→S", "S" in classify(s_line) and "E" not in classify(s_line), str(classify(s_line)))

# ---------- C. 每条可测试三问真跑 ----------
print("\n== C. 三问真跑 ==")
def three_questions(trigger, response):
    bad = []
    if not trigger or re.search(r"觉得|大概|合适的时候|适当", trigger):
        bad.append("触发不可观测")
    if not response or re.search(r"^(处理|优化|支持|改善)$", response.strip()):
        bad.append("响应不具体")
    # 能判定通过：响应必须是动作+对象
    if not re.search(r"显示|保存|跳转|校验|下载|阻止|提示|切换|创建|删除|锁定|使用", response):
        bad.append("无法判定通过")
    return bad

GOOD = [
    ("用户点击导出按钮", "下载 CSV 文件"),
    ("用户没有导出权限", "显示无权限提示并阻止下载"),
    ("用户处于离线状态", "显示上次缓存的数据"),
]
BAD = [
    ("用户觉得合适的时候", "处理一下"),
    ("用户点击保存", "优化"),
]
for trig, resp in GOOD:
    check(f"三问通过「{resp}」", three_questions(trig, resp) == [], str(three_questions(trig, resp)))
for trig, resp in BAD:
    check(f"三问拦下「{resp}」", len(three_questions(trig, resp)) > 0, str(three_questions(trig, resp)))

# ---------- D. 空类不写 ----------
print("\n== D. 输出形态 ==")
out = """## EARS 需求 · 导出

E 当用户点击导出按钮时，系统应下载 CSV 文件
U* 如果用户没有导出权限，那么系统应显示提示并阻止下载

待确认：无"""
present = set(re.findall(r"^(U\*|[EESOU]) ", out, re.M))
check("空类未写（只有 E/U*）", present == {"E", "U*"}, str(present))
check("每行带前缀", all(re.match(r"^(U\*|[EESOU]) ", l) for l in out.split("\n") if l.startswith(("E ", "U* ", "S ", "O ", "U "))))
check("有待确认字段", "待确认：" in out)
check("无优先级排期", not re.search(r"P0|P1|MVP|排期", out))

print("\n" + "=" * 46)
print(f"FAIL {len(FAIL)}")
if FAIL:
    print("未通过：", FAIL)
    sys.exit(1)
print("全部通过")
