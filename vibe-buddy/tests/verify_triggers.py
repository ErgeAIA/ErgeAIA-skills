#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""触发集干跑：把 trigger-test-set.md 里的用例与 SKILL.md 的路由表做机械比对。

不模拟 LLM，只验证「每个触发词都有路由与验证行」「负面集的词不被路由表吸收」
「用例里点名的触发词都真实存在」——这是可机检的部分，语义判定仍需人工。
"""
import re, sys
from pathlib import Path

FAIL = []
def check(name, cond, detail=""):
    print(("PASS" if cond else "FAIL"), name, detail)
    if not cond:
        FAIL.append(name)

SKILL = (Path(__file__).resolve().parent.parent / "SKILL.md").read_text(encoding="utf-8")
TS = (Path(__file__).resolve().parent.parent / "references/trigger-test-set.md").read_text(encoding="utf-8")

# 1. 八个触发词在 SKILL 中都有路由行与验证行
VIBE = ["vibe-init", "vibe-sync", "vibe-handoff", "vibe-distill", "vibe-audit", "vibe-check", "vibe-release", "vibe-req", "vibe-wrap"]
route_sec = SKILL.split("## 产物布局")[0]
for v in VIBE:
    check(f"{v} 有路由行", v in route_sec)
    check(f"{v} 有验证行", f"| `{v}` |" in SKILL)

# 2. description 覆盖所有触发词的中文意图词
desc = re.search(r'description:\s*"([^"]+)"', SKILL).group(1)
intents = ["初始化项目", "生成 AGENTS.md", "同步进度", "踩的坑", "交接文档", "经验蒸馏",
           "审查项目", "审这次改动", "只看安全", "发版前检查", "体检", "收尾"]
for i in intents:
    check(f"description 含「{i}」", i in desc)

# 3. 测试集里点名的 vibe- 触发词必须存在
named = set(re.findall(r"vibe-(?:init|sync|handoff|distill|audit|check|release|wrap)", TS))
unknown = named - set(VIBE)
check("测试集无未知触发词", not unknown, str(unknown))

# 4. 负面集覆盖关键边界
for neg in ["待办", "CHANGELOG", "代码质量"]:
    check(f"负面集含「{neg}」", neg in TS)

# 5. 冲突集存在且覆盖模糊场景
check("有冲突集小节", "冲突与模糊集" in TS)
check("模糊场景要求问一句", "问一句查档案还是查代码" in TS)

# 6. 执行维度用例 E1–E10 齐全
es = sorted(set(re.findall(r"\| (E\d+) \|", TS)), key=lambda x: int(x[1:]))
check("执行用例 E1–E12 齐全", es == [f"E{i}" for i in range(1, 13)], str(es))

# 7. 每个 E 用例都有断言列（3 列以上）
rows = [l for l in TS.split("\n") if re.match(r"\| E\d+ \|", l)]
check("每个用例都有断言", all(len(l.split("|")) >= 5 for l in rows), f"{len(rows)} 行")

# 8. 阈值表存在
check("阈值表含命中率", "≥ 90%" in TS)
check("阈值表含误触发", "≤ 10%" in TS)

print("\n" + "=" * 46)
print(f"FAIL {len(FAIL)}")
if FAIL:
    print("未通过：", FAIL)
    sys.exit(1)
print("全部通过")
