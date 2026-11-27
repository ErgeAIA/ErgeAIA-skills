#!/usr/bin/env python3
"""端点探测：确认本地服务可用，并抓取评测所需的运行时事实。

为什么必须先探测再评测：本地模型的分数离开「模型文件 + 量化 + 运行时 build +
上下文长度 + 聊天模板」这些事实就无法复现，也就无法比较。探测失败必须显式
报错并给出启动命令，禁止静默降级（否则会拿一个猜的模板跑完整套题）。
"""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request

START_HINTS = {
    "llama.cpp": (
        "llama-server -m <model.gguf> --host 127.0.0.1 --port 8080 "
        "--jinja --parallel 1 --ctx-size 8192 -ngl 999"
    ),
    "lmstudio": "LM Studio → Developer → Start Server（默认 127.0.0.1:1234）",
    "ollama": "ollama serve",
}


def _get(url: str, timeout: float = 5.0) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        return 0, f"{type(exc).__name__}: {exc}"


def probe(base_url: str, timeout: float = 5.0) -> dict:
    """返回 {ok, base_url, backend, models, props, problems}。"""
    base = base_url.rstrip("/")
    if base.endswith("/v1"):
        root = base[:-3]
    else:
        root = base
    out = {
        "ok": False,
        "base_url": base,
        "backend": "unknown",
        "models": [],
        "props": {},
        "problems": [],
    }

    # /v1/models 是 OpenAI 兼容端点的最小公约数
    status, body = _get(f"{base}/v1/models" if not base.endswith("/v1") else f"{base}/models", timeout)
    if status == 200:
        try:
            data = json.loads(body)
            out["models"] = [m.get("id") for m in data.get("data", []) if m.get("id")]
        except Exception:  # noqa: BLE001
            out["problems"].append("/v1/models 返回非 JSON")
    else:
        out["problems"].append(f"/v1/models 不可用（status={status}）")

    # /props 只有 llama.cpp 有，能拿到模板、上下文、build
    status_p, body_p = _get(f"{root}/props", timeout)
    if status_p == 200:
        try:
            props = json.loads(body_p)
        except Exception:  # noqa: BLE001
            props = {}
        out["backend"] = "llama.cpp"
        defaults = props.get("default_generation_settings", {}) or {}
        out["props"] = {
            "build_info": props.get("build_info", ""),
            "model_path": props.get("model_path", ""),
            "n_ctx": props.get("total_slots") and defaults.get("n_ctx", props.get("n_ctx")),
            "total_slots": props.get("total_slots"),
            "chat_template_present": bool(props.get("chat_template")),
            "chat_template_sha": _sha(props.get("chat_template", "")),
            "modalities": props.get("modalities"),
        }
        if not props.get("chat_template"):
            out["problems"].append("服务未加载 chat 模板：llama-server 需加 --jinja，否则工具调用与对话格式都会失真")
    else:
        out["backend"] = "openai-compatible"
        out["problems"].append("/props 不可用（非 llama.cpp 或未开启），模板与 build 信息缺失，复现性下降")

    # chat 模板是硬门槛：缺了它，工具维与对话格式都失真，不允许判 ok
    no_template = any("chat 模板" in p for p in out["problems"])
    out["ok"] = (bool(out["models"])
                 and not any("不可用（status=" in p for p in out["problems"])
                 and not no_template)
    return out


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def probe_or_fail(base_url: str) -> dict:
    """探测失败时抛出带启动命令的异常。"""
    info = probe(base_url)
    if not info["ok"]:
        hint = START_HINTS["llama.cpp"]
        raise RuntimeError(
            f"无法连接本地模型服务 {base_url}\n"
            f"问题：{'；'.join(info['problems']) or '未知'}\n"
            f"请先启动服务，例如：\n  {hint}\n"
            f"启动后用同一 base_url 重跑。"
        )
    return info
