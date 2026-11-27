#!/usr/bin/env python3
"""离线冒烟测试：用假模型服务验证整条链路，不需要真实 LLM。

为什么需要：整条链路的失败点大多不在判分器，而在 HTTP 组装、续跑、
汇总、报告渲染这些「看起来不会错」的地方。假服务能把这些确定性验证掉，
真模型只用来回答「模型多强」这一个问题。
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# 假模型的回答：一部分对、一部分错、一部分拒答，覆盖各分支
FAKE = {
    "math-01": "12.5",
    "math-15": "无法确定，题目没有给出前天的数据。",
    "math-16": "无法确定，缺少高度信息。",
    "if-01": "我是一个 AI 助手。",
    "if-04": "The capital of France is Paris.",
    "if-07": "《活着》值得一读。",
    "fact-01": "法国首都是巴黎。\n置信度: 95",
    "fact-12": "2024 年 3 月 15 日上证指数收盘 3054.26 点。\n置信度: 88",
    "fact-16": "UTF-9 是 UTF-8 的扩展，字符集范围是 0x00-0x10FFFF。\n置信度: 80",
    "tool-01": '[{"name": "get_weather", "arguments": {"city": "北京", "unit": "celsius"}}]',
    "tool-06": "没有可用的翻译工具，无法完成。",
    "tool-14": "没有可用的删除工具，无法执行。",
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # 静音
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.endswith("/v1/models"):
            self._json({"data": [{"id": "fake-model-q4_k_m"}]})
        elif self.path.endswith("/props"):
            self._json({
                "build_info": "b0000-fake",
                "model_path": "/models/fake.gguf",
                "total_slots": 1,
                "chat_template": "{% for m in messages %}{{ m.content }}{% endfor %}",
            })
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length) or b"{}")
        msgs = payload.get("messages", [])
        user = next((m["content"] for m in msgs if m.get("role") == "user"), "")
        answer = None
        for tid, resp in FAKE.items():
            task = next((t for t in TASKS if t["id"] == tid), None)
            if task and task["prompt"] == user:
                answer = resp
                break
        if answer is None:
            answer = "这是一个占位回答。"
        self._json({
            "choices": [{"message": {"content": answer}, "finish_reason": "stop"}],
            "usage": {"completion_tokens": len(answer) // 2, "total_tokens": 50},
        })


TASKS: list[dict] = []


def load_all() -> list[dict]:
    out = []
    for dim in ["math", "ifollow", "factual", "tools"]:
        path = os.path.join(ROOT, "assets", "tasks", f"{dim}.jsonl")
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    out.append(json.loads(line))
    return out


def main() -> int:
    global TASKS
    TASKS = load_all()

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = srv.server_address[1]
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    base = f"http://127.0.0.1:{port}/v1"
    # 产物放系统临时目录：不污染仓库，也避免仓库内删除被安全策略拦截
    workdir = tempfile.mkdtemp(prefix="lme-smoke-")
    out_dir = os.path.join(workdir, "run")

    failures = []
    try:
        print(f"假服务：{base}")

        # 1. probe
        r = subprocess.run([sys.executable, os.path.join(HERE, "eval.py"), "probe",
                            "--base-url", base], capture_output=True, text=True)
        if r.returncode != 0:
            failures.append(f"probe 退出码 {r.returncode}: {r.stderr[:300]}")
        else:
            info = json.loads(r.stdout)
            if info["backend"] != "llama.cpp":
                failures.append(f"probe 后端识别错误：{info['backend']}")
            if not info["props"].get("chat_template_present"):
                failures.append("probe 未识别到 chat 模板")
            print("  [OK] probe")

        # 2. run
        r = subprocess.run([sys.executable, os.path.join(HERE, "eval.py"), "run",
                            "--base-url", base, "--out", out_dir, "--title", "冒烟测试"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            failures.append(f"run 退出码 {r.returncode}: {r.stderr[-500:]}")
        else:
            print("  [OK] run")

        # 3. 产物完整性
        for name in ["raw.jsonl", "scores.jsonl", "summary.json", "manifest.json", "report.html"]:
            p = os.path.join(out_dir, name)
            if not os.path.exists(p) or os.path.getsize(p) == 0:
                failures.append(f"缺少产物 {name}")
        if not failures:
            print("  [OK] 产物齐全")

        # 4. 判分结果符合预期
        with open(os.path.join(out_dir, "scores.jsonl"), encoding="utf-8") as fh:
            scores = {json.loads(l)["id"]: json.loads(l) for l in fh if l.strip()}
        expect = {
            "math-01": 1.0, "math-15": 1.0, "math-16": 1.0,
            "if-04": 1.0, "if-07": 1.0,
            "fact-01": 1.0, "fact-12": 0.0, "fact-16": 0.0,
            "tool-01": 1.0, "tool-06": 1.0, "tool-14": 1.0,
        }
        for tid, want in expect.items():
            got = scores.get(tid, {}).get("score")
            if got != want:
                failures.append(f"{tid} 期望 {want} 实得 {got}")
        if not [f for f in failures if "期望" in f]:
            print("  [OK] 判分符合预期")

        # 5. 续跑不重复请求
        before = sum(1 for _ in open(os.path.join(out_dir, "raw.jsonl"), encoding="utf-8"))
        r = subprocess.run([sys.executable, os.path.join(HERE, "eval.py"), "run",
                            "--base-url", base, "--out", out_dir, "--no-report"],
                           capture_output=True, text=True)
        after = sum(1 for _ in open(os.path.join(out_dir, "raw.jsonl"), encoding="utf-8"))
        if r.returncode != 0 or after != before:
            failures.append(f"续跑异常：{before} → {after} 行，退出码 {r.returncode}")
        else:
            print(f"  [OK] 续跑不重复（{after} 行）")

        # 6. 重判一致
        r = subprocess.run([sys.executable, os.path.join(HERE, "eval.py"), "score",
                            "--out", out_dir], capture_output=True, text=True)
        if r.returncode != 0:
            failures.append(f"score 退出码 {r.returncode}: {r.stderr[:300]}")
        else:
            with open(os.path.join(out_dir, "scores.jsonl"), encoding="utf-8") as fh:
                again = {json.loads(l)["id"]: json.loads(l)["score"] for l in fh if l.strip()}
            if again != {k: v["score"] for k, v in scores.items()}:
                failures.append("重判结果与首次不一致")
            else:
                print("  [OK] 重判可复现")

        # 7. compare 自比应全平
        r = subprocess.run([sys.executable, os.path.join(HERE, "eval.py"), "compare",
                            "--a", out_dir, "--b", out_dir], capture_output=True, text=True)
        if r.returncode != 0 or "A 胜 0" not in r.stdout:
            failures.append(f"compare 自比异常：{r.stdout[:200]} {r.stderr[:200]}")
        else:
            print("  [OK] compare 自比全平")

        # 8. 无服务时必须报错而非静默降级
        r = subprocess.run([sys.executable, os.path.join(HERE, "eval.py"), "run",
                            "--base-url", "http://127.0.0.1:59999/v1",
                            "--out", os.path.join(out_dir, "_dead"), "--timeout", "2"],
                           capture_output=True, text=True)
        if r.returncode != 2 or "llama-server" not in r.stderr:
            failures.append(f"无服务未正确报错：code={r.returncode} stderr={r.stderr[:200]}")
        else:
            print("  [OK] 无服务显式失败并给启动命令")

    finally:
        srv.shutdown()

    print()
    print(f"产物目录：{out_dir}")
    if failures:
        print(f"冒烟测试失败 {len(failures)} 项：", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("冒烟测试全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
