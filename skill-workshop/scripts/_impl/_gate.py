"""Plan-gate 与 checkpoint 辅助（目标驱动脚本协议）。

设计原则（见 references/templates/plan-gate-template.md）：
- 脚本守边界不挡路：本模块不阻止任何行动，只把「未附计划」表达为结构化
  decision_required 输出（exit 2），由 AI 转述用户后带 --plan 重跑。
- `--plan-text` 一句话快速通道仅限人类直接调用；AI 必须走五节计划
  （SKILL.md §2 硬规则）。
- 无 input()、无网络、无模块级副作用；纯 stdlib。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PLAN_SECTIONS = ("目标", "范围与边界", "参数", "停止条件", "回滚")


def _emit_decision(topic: str, options: list[str]) -> None:
    print(
        json.dumps({"decision_required": {"topic": topic, "options": options}}, ensure_ascii=False)
    )


def require_plan(plan_file: str | None, plan_text: str | None, command: str) -> str:
    """校验并返回计划文本；缺失/不完整时输出 decision_required 并 exit 2。

    - plan_text：一句话快速通道（仅限人类直接调用，不做五节校验）。
    - plan_file：五节计划文件，逐节校验存在性。
    - 两者皆缺：输出「需先出示计划」的决策请求。
    """
    if plan_text:
        return plan_text.strip()

    if plan_file:
        try:
            text = Path(plan_file).read_text(encoding="utf-8")
        except OSError as e:
            # 审查门 R6：文件不可读输出结构化决策请求，不抛裸 traceback
            _emit_decision(
                f"{command} 计划文件不可读: {e}",
                ["检查路径后重跑", "改用 --plan-text（仅限人类）"],
            )
            raise SystemExit(2)
        missing = [s for s in PLAN_SECTIONS if s not in text]
        if missing:
            _emit_decision(
                f"{command} 计划缺节: {missing}",
                ["补全计划文件后重跑", "改用 --plan-text（仅限人类）"],
            )
            raise SystemExit(2)
        return text

    _emit_decision(
        f"{command} 属高成本/写文件命令，需先出示计划",
        [
            "AI 先给用户看五节计划（目标/范围与边界/参数/停止条件/回滚），确认后带 --plan <file> 重跑",
            "人类自用：--plan-text '<一句话>' 快速通道",
        ],
    )
    raise SystemExit(2)


def emit_checkpoint(done: str, next_step: str, risks: str, **extra) -> None:
    """输出单行 checkpoint JSON 到 stderr（loop 迭代每轮调用）。

    走 stderr 保持 stdout 纯净（stdout 是机器可解析的结果 JSON）。
    SKILL.md §2 硬规则：AI 收到 checkpoint 必须向用户转述思路与下一步。
    """
    print(
        json.dumps(
            {
                "checkpoint": {
                    "done": done,
                    "next": next_step,
                    "risks": risks,
                    "stop_condition_met": False,
                    **extra,
                }
            },
            ensure_ascii=False,
        ),
        file=sys.stderr,
    )
