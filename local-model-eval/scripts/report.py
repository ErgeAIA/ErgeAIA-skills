#!/usr/bin/env python3
"""把 scores.jsonl / summary.json 渲染成单文件静态 HTML 报告。

原则：
- 报告是派生视图，唯一事实源是 raw.jsonl 与 scores.jsonl
- 不依赖任何外部 CDN、字体、脚本（本地离线可开）
- 每个数字都能下钻到判分理由与原始响应
- 分数必须带区间；总分在任维度失效时标注「不完整」
"""

from __future__ import annotations

import html
import json
import os

DIM_ORDER = ["math", "ifollow", "factual", "tools"]
DIM_LABELS = {"math": "数学推理", "ifollow": "指令遵循",
              "factual": "事实性与幻觉", "tools": "工具调用"}

# 维度局限：每维必须写清「这个数字不代表什么」，防止过度解读
DIM_CAVEATS = {
    "math": "只测单步到三步的数值推理，高分不代表多步规划或形式化证明能力。",
    "ifollow": "只覆盖可用代码验证的约束；「语气自然」「避免术语」这类不可验证要求不在测量范围内。",
    "factual": "题目数量不足以给出稳定的校准结论；ECE 仅在置信度样本充足时展示。",
    "tools": "工具清单由提示词注入，未使用模型原生 function calling 模板；实际接入效果可能不同。",
}


def esc(s) -> str:
    return html.escape(str(s if s is not None else ""))


def pct(v: float | None, digits: int = 1) -> str:
    if v is None:
        return "—"
    return f"{v * 100:.{digits}f}%"


def load_jsonl(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


CSS = """
:root{
  --bg:#16120E; --surface:#201A15; --surface-2:#2C2620; --card:#241F1B;
  --text:#EDE4D8; --muted:#C0B7A9; --dim:#A39D93;
  --border:#3A342D; --border-strong:#4A4339;
  --accent:#F2570F; --accent-2:#FFB380; --accent-fg:#171614;
  --ok:#257552; --ok-fill:#2E8A5F; --warn:#8A6410; --warn-fill:#B2820B;
  --danger:#C2382E; --danger-fill:#E0564A; --info:#4353B8; --info-fill:#6478D9;
  --ok-on:#a9d8c0; --warn-on:#e2c27a; --danger-on:#f0a49c; --info-on:#a8b6f0;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:var(--bg); color:var(--text);
  font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif;
  -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1180px;margin:0 auto;padding:40px 24px 80px}
header.top{border-bottom:1px solid var(--border);padding-bottom:24px;margin-bottom:32px}
h1{font-size:26px;margin:0 0 8px;letter-spacing:-.01em;font-weight:650}
.sub{color:var(--muted);font-size:13.5px}
.meta-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.chip{
  display:inline-flex;align-items:center;gap:6px;
  background:var(--surface-2);border:1px solid var(--border);
  border-radius:999px;padding:4px 11px;font-size:12px;color:var(--muted);
  font-variant-numeric:tabular-nums;
}
.chip b{color:var(--text);font-weight:600}
.chip.ok{border-color:rgba(46,138,95,.5);color:var(--ok-on)}
.chip.warn{border-color:rgba(178,130,11,.5);color:var(--warn-on)}
.chip.bad{border-color:rgba(224,86,74,.5);color:var(--danger-on)}

section{margin-bottom:44px}
h2{font-size:17px;margin:0 0 4px;font-weight:640;letter-spacing:-.005em}
.h2-sub{color:var(--dim);font-size:12.5px;margin-bottom:18px}

.hero{
  background:linear-gradient(180deg,var(--surface) 0%,var(--card) 100%);
  border:1px solid var(--border);border-radius:14px;padding:26px 28px;
  display:grid;grid-template-columns:minmax(180px,220px) 1fr;gap:32px;align-items:center;
}
.hero-num{font-size:52px;font-weight:680;line-height:1;letter-spacing:-.03em;
  font-variant-numeric:tabular-nums;color:var(--accent-2)}
.hero-num small{font-size:18px;color:var(--dim);font-weight:500;margin-left:2px}
.hero-label{color:var(--dim);font-size:12px;text-transform:uppercase;letter-spacing:.09em;margin-bottom:10px}
.hero-note{color:var(--muted);font-size:13px;margin-top:10px;max-width:56ch}

.dim-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.dim-card{
  background:var(--surface);border:1px solid var(--border);border-radius:12px;
  padding:18px 18px 16px;position:relative;overflow:hidden;
}
.dim-card::before{content:"";position:absolute;inset:0 auto 0 0;width:3px;background:var(--accent);opacity:.75}
.dim-name{font-size:13px;color:var(--muted);margin-bottom:10px;display:flex;justify-content:space-between;gap:8px}
.dim-score{font-size:30px;font-weight:660;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.dim-ci{font-size:11.5px;color:var(--dim);margin-top:4px;font-variant-numeric:tabular-nums}
.bar{height:5px;background:var(--surface-2);border-radius:3px;margin:13px 0 11px;overflow:hidden}
.bar>i{display:block;height:100%;background:var(--accent);border-radius:3px}
.dim-foot{font-size:11.5px;color:var(--dim);display:flex;flex-wrap:wrap;gap:5px 12px}
.dim-foot b{color:var(--muted);font-weight:600;font-variant-numeric:tabular-nums}

table{width:100%;border-collapse:collapse;font-size:13px}
th{
  text-align:left;color:var(--dim);font-weight:600;font-size:11.5px;
  text-transform:uppercase;letter-spacing:.06em;
  padding:9px 12px;border-bottom:1px solid var(--border-strong);white-space:nowrap;
}
td{padding:10px 12px;border-bottom:1px solid var(--border);vertical-align:top}
tr:last-child td{border-bottom:none}
tbody tr:hover{background:var(--surface-2)}
td.num{font-variant-numeric:tabular-nums;white-space:nowrap}
.tbl-wrap{background:var(--surface);border:1px solid var(--border);border-radius:12px;overflow:hidden}

.tag{
  display:inline-block;padding:2px 8px;border-radius:5px;font-size:11px;
  font-weight:600;white-space:nowrap;letter-spacing:.01em;
}
.tag.ok{background:rgba(46,138,95,.16);color:var(--ok-on)}
.tag.warn{background:rgba(178,130,11,.16);color:var(--warn-on)}
.tag.bad{background:rgba(224,86,74,.15);color:var(--danger-on)}
.tag.info{background:rgba(100,120,217,.16);color:var(--info-on)}

details{background:var(--surface);border:1px solid var(--border);border-radius:10px;margin-bottom:8px}
details[open]{border-color:var(--border-strong)}
summary{
  cursor:pointer;padding:12px 16px;display:flex;align-items:center;gap:12px;
  font-size:13px;list-style:none;user-select:none;
}
summary::-webkit-details-marker{display:none}
summary::before{content:"›";color:var(--dim);font-size:16px;transition:transform .15s;display:inline-block}
details[open] summary::before{transform:rotate(90deg)}
summary:hover{background:var(--surface-2)}
.sum-id{font-variant-numeric:tabular-nums;color:var(--muted);min-width:74px;font-size:12px}
.sum-q{color:var(--dim);font-size:12px;overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap;flex:1;min-width:0}
.sum-score{font-variant-numeric:tabular-nums;font-weight:600;font-size:12.5px;
  min-width:46px;text-align:right}
.body{padding:2px 16px 16px;border-top:1px solid var(--border)}
.block{margin-top:14px}
.block-h{font-size:11px;color:var(--dim);text-transform:uppercase;letter-spacing:.07em;margin-bottom:6px}
pre{
  background:var(--bg);border:1px solid var(--border);border-radius:8px;
  padding:12px 14px;overflow-x:auto;font-size:12.5px;line-height:1.6;margin:0;
  font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
  color:var(--muted);white-space:pre-wrap;word-break:break-word;
}
.reason{font-size:12.5px;color:var(--muted);background:var(--bg);
  border-left:2px solid var(--accent);padding:8px 12px;border-radius:0 6px 6px 0}

.caveat{display:grid;gap:10px}
.caveat-item{
  background:var(--surface);border:1px solid var(--border);border-left:2px solid var(--warn-fill);
  border-radius:0 8px 8px 0;padding:11px 14px;font-size:12.5px;color:var(--muted);
}
.caveat-item b{color:var(--text);font-weight:620}

.note{
  background:rgba(67,83,184,.09);border:1px solid rgba(100,120,217,.28);
  border-radius:10px;padding:14px 16px;font-size:13px;color:var(--muted);
}
.note b{color:var(--text)}
.note.danger{background:rgba(194,56,46,.09);border-color:rgba(224,86,74,.3)}
.note.danger b{color:var(--danger-on)}

.empty{color:var(--dim);font-size:13px;padding:18px;text-align:center}
footer{color:var(--dim);font-size:11.5px;border-top:1px solid var(--border);padding-top:18px;margin-top:12px}
@media(max-width:720px){
  .hero{grid-template-columns:1fr;gap:18px}
  .hero-num{font-size:42px}
  .dim-grid{grid-template-columns:1fr}
  .wrap{padding:24px 16px 60px}
}
"""


def verdict_tag(v: str) -> str:
    mapping = {
        "correct": ("ok", "正确"), "no_call_ok": ("ok", "正确未调"),
        "abstain_correct": ("ok", "正确弃答"), "premise_ok": ("ok", "纠正前提"),
        "incorrect": ("bad", "答错"), "hallucinated": ("bad", "幻觉"),
        "spurious_call": ("bad", "误调用"), "unknown_tool": ("bad", "虚构工具"),
        "arg_mismatch": ("bad", "参数错"), "count_mismatch": ("bad", "数量错"),
        "over_abstain": ("warn", "过度弃答"), "premise_missed": ("warn", "未纠前提"),
        "request_failed": ("bad", "请求失败"),
    }
    cls, label = mapping.get(v, ("info", v or "—"))
    return f'<span class="tag {cls}">{esc(label)}</span>'


def render(summary: dict, scores: list[dict], raws: list[dict], title: str) -> str:
    dims = summary.get("dims", {})
    manifest = summary.get("manifest", {})
    cost = summary.get("cost", {})

    raw_by_id = {r["id"]: r for r in raws}
    has_error = any(d.get("errors", 0) > 0 for d in dims.values())
    overall = summary.get("overall", 0.0)

    # 完整性判定：四维齐全且无请求失败
    complete = len(dims) == 4 and not has_error
    integrity_chip = (
        '<span class="chip ok">完整性：四维齐全</span>' if complete
        else '<span class="chip bad">完整性：不完整（总分仅供参考）</span>'
    )

    parts: list[str] = []
    parts.append(f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><style>{CSS}</style></head><body><div class="wrap">""")

    # ---- header ----
    parts.append(f"""
<header class="top">
  <h1>{esc(title)}</h1>
  <div class="sub">本地模型能力评测报告 · 四维程序化判分 · 生成于 {esc(summary.get('generated_at', ''))}</div>
  <div class="meta-row">
    <span class="chip">模型 <b>{esc(manifest.get('model', '—'))}</b></span>
    <span class="chip">端点 <b>{esc(manifest.get('base_url', '—'))}</b></span>
    <span class="chip">温度 <b>{esc(manifest.get('temperature', '—'))}</b> · seed <b>{esc(manifest.get('seed', '—'))}</b></span>
    <span class="chip">题目 <b>{esc(summary.get('n', 0))}</b></span>
    {integrity_chip}
  </div>
</header>""")

    # ---- hero ----
    note = "四维加权均值。" if complete else "存在失效维度或请求失败，该数字不应作为模型能力结论。"
    parts.append(f"""
<section>
  <div class="hero">
    <div>
      <div class="hero-label">综合得分</div>
      <div class="hero-num">{pct(overall)}</div>
      <div class="hero-note">{esc(note)}</div>
    </div>
    <div class="dim-grid">""")

    for dim in DIM_ORDER:
        d = dims.get(dim)
        if not d:
            continue
        ci = d.get("ci") or [0, 0]
        extra = ""
        if dim == "factual":
            extra = (f'<span>幻觉率 <b>{pct(d.get("hallucination_rate"))}</b></span>'
                     f'<span>弃答率 <b>{pct(d.get("abstain_rate"))}</b></span>')
        elif dim == "ifollow":
            extra = f'<span>全通过率 <b>{pct(d.get("all_pass_rate"))}</b></span>'
        elif dim == "tools":
            extra = f'<span>误调用率 <b>{pct(d.get("spurious_call_rate"))}</b></span>'
        err = d.get("errors", 0)
        if err:
            extra += f'<span style="color:var(--danger-on)">失败 <b>{err}</b></span>'
        parts.append(f"""
      <div class="dim-card">
        <div class="dim-name"><span>{esc(DIM_LABELS.get(dim, dim))}</span><span>n={d.get('n')}</span></div>
        <div class="dim-score">{pct(d.get('mean'))}</div>
        <div class="dim-ci">95% CI {pct(ci[0])} – {pct(ci[1])}</div>
        <div class="bar"><i style="width:{min(100, (d.get('mean') or 0) * 100):.1f}%"></i></div>
        <div class="dim-foot">{extra}</div>
      </div>""")
    parts.append("    </div>\n  </div>\n</section>")

    # ---- cost ----
    if cost.get("latency_ms_mean") is not None:
        parts.append(f"""
<section>
  <h2>成本</h2>
  <div class="h2-sub">能力分数必须与运行成本同时看：高分但慢，实际可用性可能更差</div>
  <div class="tbl-wrap"><table><thead><tr>
    <th>指标</th><th>数值</th><th>说明</th>
  </tr></thead><tbody>
    <tr><td>平均延迟</td><td class="num">{cost.get('latency_ms_mean')} ms</td><td>单次请求端到端</td></tr>
    <tr><td>P95 延迟</td><td class="num">{cost.get('latency_ms_p95')} ms</td><td>长尾等待</td></tr>
    <tr><td>生成速度</td><td class="num">{cost.get('tokens_per_sec_mean') or '—'} tok/s</td><td>按 completion_tokens 计算</td></tr>
  </tbody></table></div>
</section>""")

    # ---- dim table ----
    parts.append("""
<section>
  <h2>各维度明细</h2>
  <div class="h2-sub">均值与通过率口径不同：均值含部分得分，通过率为满分题占比</div>
  <div class="tbl-wrap"><table><thead><tr>
    <th>维度</th><th>n</th><th>均值</th><th>95% CI</th><th>通过率</th><th>请求失败</th>
  </tr></thead><tbody>""")
    for dim in DIM_ORDER:
        d = dims.get(dim)
        if not d:
            continue
        ci = d.get("ci") or [0, 0]
        pci = d.get("pass_ci") or [0, 0]
        parts.append(f"""
    <tr>
      <td><b>{esc(DIM_LABELS.get(dim, dim))}</b></td>
      <td class="num">{d.get('n')}</td>
      <td class="num">{pct(d.get('mean'))}</td>
      <td class="num" style="color:var(--dim)">{pct(ci[0])} – {pct(ci[1])}</td>
      <td class="num">{pct(d.get('pass_rate'))} <span style="color:var(--dim)">({pct(pci[0])}–{pct(pci[1])})</span></td>
      <td class="num">{d.get('errors', 0) or '—'}</td>
    </tr>""")
    parts.append("  </tbody></table></div>\n</section>")

    # ---- caveats ----
    parts.append("""
<section>
  <h2>这些数字不代表什么</h2>
  <div class="h2-sub">每维的测量边界。读分数前先读这里，避免过度外推</div>
  <div class="caveat">""")
    for dim in DIM_ORDER:
        if dim in dims:
            parts.append(
                f'<div class="caveat-item"><b>{esc(DIM_LABELS[dim])}</b> — {esc(DIM_CAVEATS[dim])}</div>')
    parts.append("  </div>\n</section>")

    # ---- per-task drilldown ----
    parts.append("""
<section>
  <h2>逐题记录</h2>
  <div class="h2-sub">点开任意一条可看到判分理由与模型原始响应；原始响应是唯一事实源</div>
""")
    for dim in DIM_ORDER:
        items = [s for s in scores if s["dim"] == dim]
        if not items:
            continue
        parts.append(f'<h3 style="font-size:13.5px;color:var(--muted);margin:22px 0 10px;font-weight:600">'
                     f'{esc(DIM_LABELS[dim])} · {len(items)} 题</h3>')
        for it in items:
            raw = raw_by_id.get(it["id"], {})
            content = raw.get("content") or raw.get("reasoning_content") or ""
            if not content and raw.get("error"):
                content = f"[请求失败] {raw.get('error', '')}"
            v = (it.get("detail") or {}).get("verdict")
            sc = it.get("score", 0.0)
            score_color = "var(--ok-on)" if sc >= 1 else ("var(--warn-on)" if sc > 0 else "var(--danger-on)")
            parts.append(f"""
<details>
  <summary>
    <span class="sum-id">{esc(it['id'])}</span>
    {verdict_tag(v)}
    <span class="sum-q">{esc((raw.get('prompt') or '')[:60])}</span>
    <span class="sum-score" style="color:{score_color}">{sc:.2f}</span>
  </summary>
  <div class="body">
    <div class="block"><div class="block-h">判分理由</div>
      <div class="reason">{esc(it.get('reason', ''))}</div></div>
    <div class="block"><div class="block-h">模型原始响应</div>
      <pre>{esc(content[:3000])}</pre></div>
    <div class="block"><div class="block-h">运行事实</div>
      <pre>latency={esc(it.get('latency_ms'))}ms  prompt_sha256={esc(it.get('prompt_sha256'))}  seed={esc(raw.get('seed'))}</pre></div>
  </div>
</details>""")
    parts.append("</section>")

    # ---- integrity ----
    integ = summary.get("integrity", {})
    parts.append(f"""
<section>
  <h2>复现信息</h2>
  <div class="h2-sub">用这些值可以核对两次运行是否真的跑在同一配置上</div>
  <div class="tbl-wrap"><table><tbody>
    <tr><td style="color:var(--dim);width:180px">模型标识</td><td><code>{esc(manifest.get('model'))}</code></td></tr>
    <tr><td style="color:var(--dim)">端点</td><td><code>{esc(manifest.get('base_url'))}</code></td></tr>
    <tr><td style="color:var(--dim)">temperature / seed</td><td><code>{esc(manifest.get('temperature'))} / {esc(manifest.get('seed'))}</code></td></tr>
    <tr><td style="color:var(--dim)">raw.jsonl 哈希</td><td><code>{esc(integ.get('raw_sha256', '—'))}</code></td></tr>
    <tr><td style="color:var(--dim)">开始 / 结束</td><td><code>{esc(manifest.get('started_at'))} → {esc(manifest.get('finished_at'))}</code></td></tr>
    <tr><td style="color:var(--dim)">工具版本</td><td><code>{esc(manifest.get('tool_version'))}</code></td></tr>
  </tbody></table></div>
</section>""")

    parts.append(f"""
<footer>
  本报告由 local-model-eval 从 scores.jsonl 直接渲染，未经过人工改写。
  判分全部程序化，无 LLM 裁判；判分器自身通过 selftest 对抗样例验证。
  单次运行的分数差异小于置信区间宽度时不构成有效差异。
</footer>
</div></body></html>""")

    return "".join(parts)


def build(out_dir: str, title: str | None = None, out_path: str | None = None) -> str:
    summary_path = os.path.join(out_dir, "summary.json")
    scores_path = os.path.join(out_dir, "scores.jsonl")
    raw_path = os.path.join(out_dir, "raw.jsonl")
    if not os.path.exists(summary_path):
        raise RuntimeError(f"缺少 {summary_path}，请先运行 run 子命令")
    with open(summary_path, encoding="utf-8") as fh:
        summary = json.load(fh)
    scores = load_jsonl(scores_path)
    raws = load_jsonl(raw_path)
    model = summary.get("manifest", {}).get("model", "本地模型")
    html_text = render(summary, scores, raws, title or f"{model} · 能力评测报告")
    out = out_path or os.path.join(out_dir, "report.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html_text)
    return out
