"""Plan-gate helper for write-path CLI commands (init/package --write).

Design (see references/validation.md):
- Scripts do not block work; missing plan is emitted as structured
  decision_required (exit 2) for the AI/user to supply --plan.
- `--plan-text` is a one-line lane for humans only; AI must pass a five-section
  plan file (目标 / 范围与边界 / 参数 / 停止条件 / 回滚).
- No input(), no network, no import-time side effects; stdlib only.
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
    """Emit one-line checkpoint JSON on stderr (optional for loop-style drivers).

    stderr keeps stdout reserved for machine-readable results.
    Agents that receive checkpoint output must relay done/next/risks to the user
    (see references/validation.md plan-gate notes).
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
