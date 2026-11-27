#!/usr/bin/env python3
"""硬件适配报告生成器：读 hardware.json + 模型清单，算容量矩阵，出单文件 HTML。

普通引擎与 PolyStrata+KVMem 分开核算；实机响应优先于参考文档。
所有数字带来源标注；无依据不编造 Token/s。
"""

from __future__ import annotations

import argparse
import html
import json
import os
import sys
import time

GIB = 1024 ** 3
MIB = 1024 ** 2

# ThemeVault #001 夜灯：固定色值，不得修改
TV_TOKENS = {
    "--tv-bg": "#16120e", "--tv-surface": "#201a15", "--tv-surface-2": "#2c2620",
    "--tv-elevated": "#2e2823", "--tv-hover": "#322a24", "--tv-card": "#241f1b",
    "--tv-border": "#3a342d", "--tv-border-strong": "#4a4339", "--tv-focus": "#d95c1e",
    "--tv-text": "#ede4d8", "--tv-muted": "#c0b7a9", "--tv-dim": "#a39d93",
    "--tv-accent": "#f2570f", "--tv-accent-hover": "#c2460b", "--tv-accent-deep": "#9e3a08",
    "--tv-accent-2": "#ffb380", "--tv-accent-fg": "#171614",
    "--tv-ok": "#257552", "--tv-ok-fill": "#2e8a5f", "--tv-warn": "#8a6410",
    "--tv-warn-fill": "#b2820b", "--tv-danger": "#c2382e", "--tv-danger-fill": "#e0564a",
    "--tv-info": "#4353b8", "--tv-info-fill": "#6478d9",
    "--tv-queued": "#8d73e3", "--tv-queued-fill": "#8b6fe0",
}

# 四态
STATE_GPU = "显存内"
STATE_OFFLOAD = "部分卸载"
STATE_CPU = "仅 CPU"
STATE_NO = "放不下"
STATE_UNKNOWN = "数据不足，暂不判定"
STATE_ORDER = [STATE_GPU, STATE_OFFLOAD, STATE_CPU, STATE_NO, STATE_UNKNOWN]

STATE_CLASS = {
    STATE_GPU: "ok", STATE_OFFLOAD: "info", STATE_CPU: "warn",
    STATE_NO: "bad", STATE_UNKNOWN: "unknown",
}

# 量化 → 每参数字节数（估算，不是精确位宽）
QUANT_BPB = {
    "Q4_K_M": 0.55, "Q5_K_M": 0.65, "Q6_K": 0.82, "Q8_0": 1.05, "F16": 2.0,
}
CONTEXTS = [4096, 8192, 16384, 32768]


def esc(s) -> str:
    return html.escape(str(s if s is not None else ""))


def val(d, key="value", default=None):
    if not isinstance(d, dict):
        return default
    v = d.get(key)
    return default if v is None else v


def src(d) -> str:
    return d.get("source", "缺失") if isinstance(d, dict) else "缺失"


def fmt_gib(x) -> str:
    return "—" if x is None else f"{x:.2f} GiB"


def fmt_mib(x) -> str:
    return "—" if x is None else f"{x:.0f} MiB"


def num(v, digits=1) -> str:
    return "—" if v is None else f"{v:.{digits}f}"


def kv_gib(model: dict, context: int, batch: int = 1) -> float | None:
    """KV = 2 × L × H_kv × D × C × B。

    只看注意力结构：MoE 描述的是 FFN，不是注意力，标准注意力仍可套公式。
    MLA / sliding-window / 混合结构必须给 attention 字段，否则不硬套。
    """
    attention = model.get("attention", "standard")
    if attention != "standard":
        return None
    L = model.get("layers")
    H = model.get("kv_heads")
    D = model.get("head_dim")
    B = model.get("kv_bytes", 2)
    if None in (L, H, D):
        return None
    n = 2 * int(L) * int(H) * int(D) * int(context) * int(batch) * float(B)
    return n / GIB


def estimate_weight_gib(params_b, quant) -> float | None:
    bpb = QUANT_BPB.get(quant)
    if params_b is None or bpb is None:
        return None
    return float(params_b) * 1e9 * bpb / GIB


def budget_from_hw(hw: dict) -> tuple[float | None, float | None, list[str]]:
    """GPU 预算用空闲显存留 10% 余量；RAM 预算用可用物理内存留 1 GiB。"""
    notes = []
    g = hw.get("gpu", {})
    r = hw.get("ram", {})
    vram_free = val(g.get("vram_free_mib"))
    if vram_free is None:
        notes.append("显存空闲量缺失 → GPU 预算不可算")
        gpu_budget = None
    else:
        gpu_budget = max(0.0, (float(vram_free) / 1024.0) * 0.9)
        notes.append(f"GPU 预算 = 空闲 {float(vram_free)/1024:.2f} GiB × 0.9 余量")
    avail = val(r.get("available_gib"))
    if avail is None:
        notes.append("可用物理内存缺失 → RAM 预算不可算")
        ram_budget = None
    else:
        ram_budget = max(0.0, float(avail) - 1.0)
        notes.append(f"RAM 预算 = 可用 {float(avail):.2f} GiB − 1.0 GiB 系统余量")
    notes.append("Windows 共享内存未与独显相加；分页文件不计入物理内存")
    return gpu_budget, ram_budget, notes


def compute_matrix(hw: dict, models: list[dict], contexts: list[int],
                   quants: list[str]) -> dict:
    gpu_budget, ram_budget, budget_notes = budget_from_hw(hw)
    rows = []
    for m in models:
        for quant in quants:
            actual = None
            wq = m.get("weights", {})
            if isinstance(wq, dict):
                actual = wq.get(quant)
            weight = float(actual) if actual is not None else estimate_weight_gib(
                m.get("params_b"), quant)
            w_source = "规格/实测" if actual is not None else "估算"
            for c in contexts:
                kvg = kv_gib(m, c, batch=int(m.get("batch", 1)))
                k_source = "计算" if kvg is not None else "缺失"
                if weight is None or kvg is None or gpu_budget is None or ram_budget is None:
                    rows.append({
                        "model": m.get("name", "未命名"), "params_b": m.get("params_b"),
                        "quant": quant, "context": c, "state": STATE_UNKNOWN,
                        "weight_gib": weight, "kv_gib": kvg, "gpu_budget": gpu_budget,
                        "ram_budget": ram_budget, "source": "缺失",
                        "bottleneck": "缺少权重/KV/预算数据",
                        "detail": "数据不足，暂不判定；不得视为第五种运行状态。",
                    })
                    continue
                runtime = max(0.5, weight * 0.08)
                gpu_need = weight + kvg + runtime
                sources = [w_source, k_source, "估算"]
                overall = "估算" if "估算" in sources else "计算"
                if gpu_need <= gpu_budget:
                    state, bn, detail = STATE_GPU, "无", (
                        f"权重 {weight:.2f} + KV {kvg:.2f} + 运行时 {runtime:.2f} "
                        f"= {gpu_need:.2f} GiB，未超 GPU 预算 {gpu_budget:.2f} GiB")
                elif (weight + kvg + runtime) <= ram_budget:
                    state = STATE_OFFLOAD
                    over = gpu_need - gpu_budget
                    bn = "显存"
                    detail = (f"GPU 侧需 {gpu_need:.2f} GiB，超预算 {over:.2f} GiB；"
                              f"RAM 预算 {ram_budget:.2f} GiB 可承载，需引擎支持部分卸载")
                elif weight <= ram_budget:
                    state = STATE_CPU
                    bn = "显存 + 速度"
                    detail = (f"全部放入系统内存可行（{weight + kvg + runtime:.2f} ≤ "
                              f"{ram_budget:.2f} GiB），但仅代表容量可行，不代表速度实用")
                else:
                    state = STATE_NO
                    miss = weight + kvg + runtime - ram_budget
                    bn = "显存 + 系统物理内存"
                    detail = (f"预计超预算：GPU 需 {gpu_need:.2f} GiB（预算 {gpu_budget:.2f}），"
                              f"RAM 侧缺 {miss:.2f} GiB；预计在权重加载或 KV 分配阶段失败")
                rows.append({
                    "model": m.get("name", "未命名"), "params_b": m.get("params_b"),
                    "quant": quant, "context": c, "state": state,
                    "weight_gib": round(weight, 3), "kv_gib": round(kvg, 3),
                    "runtime_gib": round(runtime, 3), "gpu_budget": round(gpu_budget, 3),
                    "ram_budget": round(ram_budget, 3),
                    "source": overall, "bottleneck": bn, "detail": detail,
                })
    return {"rows": rows, "gpu_budget": gpu_budget, "ram_budget": ram_budget,
            "budget_notes": budget_notes}


def pick_conclusion(matrix: dict, hw: dict) -> dict:
    rows = matrix["rows"]
    known = [r for r in rows if r["state"] != STATE_UNKNOWN]
    if not known:
        return {"device": "未知设备", "bottleneck": "—", "first": "暂不能可靠判定",
                "second": "—", "confidence": "数据不足",
                "note": "缺少显存/内存或模型权重数据，首屏不下结论。"}
    good = [r for r in known if r["state"] == STATE_GPU]
    best = good[-1] if good else (known[-1] if known else None)
    gpu = hw.get("gpu", {})
    name = val(gpu.get("name"), default="未知设备")
    free = val(gpu.get("vram_free_mib"))
    bottleneck = (f"显存空闲 {free/1024:.1f} GiB（实测）" if free is not None else "显存数据缺失")
    if best:
        first = f"{best['model']} · {best['quant']} · {best['context'] // 1024}k（{best['state']}）"
    else:
        first = "暂无可运行档位"
    alt = [r for r in known if r is not best and r["state"] in (STATE_GPU, STATE_OFFLOAD)
           and r["model"] != best["model"]]
    if not alt:
        alt = [r for r in known if r is not best and r["state"] in (STATE_GPU, STATE_OFFLOAD)]
    second = (f"{alt[-1]['model']} · {alt[-1]['quant']} · {alt[-1]['context']//1024}k"
              f"（{alt[-1]['state']}）" if alt else "无备选")
    missing_fields = []
    for path, label in [("gpu.vram_free_mib", "显存空闲"), ("ram.available_gib", "可用内存"),
                        ("gpu_specs.memory_bandwidth_gbs", "有效带宽"),
                        ("cpu.sustained_freq", "持续频率")]:
        d = hw
        for k in path.split("."):
            d = d.get(k, {}) if isinstance(d, dict) else {}
        if src(d) == "缺失" or val(d) is None:
            missing_fields.append(label)
    conf = "中" if len(missing_fields) <= 2 else "低"
    return {
        "device": str(name), "bottleneck": bottleneck, "first": first, "second": second,
        "confidence": conf,
        "note": "首选取预算内最大可用配置；备选取次一档。速度未实测，档位仅代表容量可行性。",
        "missing_fields": missing_fields,
    }


CSS = """
:root{
""" + "\n".join(f"  {k}:{v};" for k, v in TV_TOKENS.items()) + """
  --tv-radius:12px;
  --tv-font-heading:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif,"PingFang SC","Microsoft YaHei","Noto Sans SC";
  --tv-font-body:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif,"PingFang SC","Microsoft YaHei","Noto Sans SC";
  --tv-font-code:ui-monospace,SFMono-Regular,Menlo,monospace,"PingFang SC","Microsoft YaHei","Noto Sans SC";
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--tv-bg);color:var(--tv-text);
  font:15px/1.75 var(--tv-font-body);-webkit-font-smoothing:antialiased}
.topbar{position:sticky;top:0;z-index:20;background:rgba(22,18,14,.94);
  border-bottom:1px solid var(--tv-border);padding:10px 24px;
  display:flex;align-items:center;gap:16px;backdrop-filter:blur(6px)}
.brand{font-size:12px;color:var(--tv-muted);letter-spacing:.02em}
.brand b{color:var(--tv-accent-2);font-weight:600}
.navlinks{margin-left:auto;display:flex;gap:14px;font-size:12px;color:var(--tv-dim)}
.navlinks a{color:var(--tv-dim);text-decoration:none}
.navlinks a:hover{color:var(--tv-text)}
.page{max-width:1200px;margin:0 auto;padding:44px 28px 80px;display:grid;
  grid-template-columns:repeat(12,1fr);gap:22px 26px}
section{grid-column:1/-1}
h1,h2,h3{font-family:var(--tv-font-heading);font-weight:650;margin:0;letter-spacing:-.01em}
h1{font-size:30px;line-height:1.3}
h2{font-size:17px;color:var(--tv-text)}
h3{font-size:14px;color:var(--tv-muted)}
.eyebrow{font-size:11px;letter-spacing:.12em;color:var(--tv-accent-2);text-transform:uppercase}
.lead{font-size:12.5px;color:var(--tv-dim)}
.hero{display:grid;grid-column:1/-1;grid-template-columns:7fr 5fr;gap:26px;
  background:var(--tv-surface);border:1px solid var(--tv-border);
  border-radius:var(--tv-radius);padding:28px 30px}
.hero-main{min-width:0}
.hero-kicker{font-size:11px;color:var(--tv-dim);margin-bottom:10px}
.bottleneck{font:600 30px/1.2 var(--tv-font-heading);color:var(--tv-accent-2);
  font-variant-numeric:tabular-nums;margin-bottom:10px}
.bottleneck-label{font-size:12.5px;color:var(--tv-muted);margin-bottom:20px}
.tier{margin-top:8px;padding:12px 14px;background:var(--tv-card);
  border-left:3px solid var(--tv-accent);border-radius:0 8px 8px 0}
.tier-label{font-size:11px;color:var(--tv-dim);margin-bottom:4px}
.tier-value{font:600 15px var(--tv-font-body)}
.hero-side{display:flex;flex-direction:column;gap:12px}
.fact{background:var(--tv-card);border:1px solid var(--tv-border);border-radius:8px;padding:14px}
.fact-k{font-size:11px;color:var(--tv-dim);margin-bottom:5px}
.fact-v{font:600 14px var(--tv-font-body);font-variant-numeric:tabular-nums}
.pill{display:inline-block;padding:2px 9px;border-radius:6px;font-size:11px;
  font-weight:600;border:1px solid var(--tv-border)}
.pill.ok{color:#a9d8c0;border-color:rgba(37,117,82,.5)}
.pill.info{color:#a8b6f0;border-color:rgba(67,83,184,.5)}
.pill.warn{color:#e2c27a;border-color:rgba(138,100,16,.5)}
.pill.bad{color:#f0a49c;border-color:rgba(194,56,46,.5)}
.pill.unknown{color:var(--tv-muted)}
.sec-head{grid-column:1/-1;display:flex;align-items:baseline;gap:12px;
  border-bottom:1px solid var(--tv-border);padding-bottom:9px;margin-top:14px}
.sec-num{font:600 12px var(--tv-font-code);color:var(--tv-accent)}
.filters{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:18px;margin-bottom:4px}
.fgroup{display:flex;flex-direction:column;gap:7px}
.fgroup>span{font-size:11px;color:var(--tv-dim)}
.fbtns{display:flex;flex-wrap:wrap;gap:6px}
.fbtn{background:var(--tv-surface);color:var(--tv-muted);border:1px solid var(--tv-border);
  border-radius:6px;padding:5px 11px;font-size:12px;cursor:pointer}
.fbtn[aria-pressed="true"]{background:var(--tv-accent);color:var(--tv-accent-fg);
  border-color:var(--tv-accent);font-weight:600}
.matrix-wrap{grid-column:1/-1;overflow-x:auto;border:1px solid var(--tv-border);
  border-radius:var(--tv-radius);background:var(--tv-surface)}
.scroll-hint{font-size:11px;color:var(--tv-dim);margin:8px 0 0}
table{border-collapse:collapse;width:100%;min-width:780px;font-size:12.5px}
th{text-align:left;color:var(--tv-dim);font-size:11px;font-weight:600;
  padding:11px 13px;border-bottom:1px solid var(--tv-border-strong);white-space:nowrap}
td{padding:11px 13px;border-bottom:1px solid var(--tv-border);vertical-align:top}
tr:last-child td{border-bottom:none}
tbody tr{cursor:pointer}
tbody tr:hover{background:var(--tv-hover)}
td.num{font-variant-numeric:tabular-nums;white-space:nowrap}
.detail{grid-column:1/-1;background:var(--tv-card);border:1px solid var(--tv-border);
  border-radius:var(--tv-radius);padding:18px 20px;font-size:13px}
.detail h4{margin:0 0 10px;font-size:14px}
.kv{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:12px 0}
.kv>div{background:var(--tv-surface);border-radius:6px;padding:10px 12px}
.kv .k{font-size:11px;color:var(--tv-dim)}
.kv .v{font-variant-numeric:tabular-nums;font-size:14px;margin-top:3px}
.bar{height:9px;background:var(--tv-surface-2);border-radius:5px;position:relative;margin:9px 0}
.bar>i{position:absolute;left:0;top:0;bottom:0;background:var(--tv-accent-2);border-radius:5px}
.bar>u{position:absolute;top:-3px;bottom:-3px;width:2px;background:var(--tv-text)}
details{grid-column:1/-1;background:var(--tv-surface);border:1px solid var(--tv-border);
  border-radius:var(--tv-radius);padding:0}
summary{cursor:pointer;padding:14px 18px;font-size:13.5px;list-style:none}
summary::-webkit-details-marker{display:none}
summary::before{content:"+";color:var(--tv-accent);margin-right:9px;font-family:var(--tv-font-code)}
details[open] summary::before{content:"−"}
.dbody{padding:0 18px 18px;border-top:1px solid var(--tv-border);font-size:13px;color:var(--tv-muted)}
.dbody ul{margin:10px 0;padding-left:20px}
.src{font-size:10.5px;color:var(--tv-dim);border:1px solid var(--tv-border);
  border-radius:4px;padding:1px 6px;margin-left:6px}
.src.实测{color:#a9d8c0}.src.估算{color:#e2c27a}.src.缺失{color:#f0a49c}
.src.规格,.src.计算{color:#a8b6f0}
.note{grid-column:1/-1;background:var(--tv-surface);border-left:3px solid var(--tv-warn);
  border-radius:0 8px 8px 0;padding:13px 16px;font-size:12.5px;color:var(--tv-muted)}
footer{grid-column:1/-1;border-top:1px solid var(--tv-border);margin-top:26px;
  padding-top:16px;font-size:11.5px;color:var(--tv-dim);display:flex;
  justify-content:space-between;gap:12px;flex-wrap:wrap}
.printbtn{background:none;border:1px solid var(--tv-border);color:var(--tv-muted);
  border-radius:6px;padding:5px 12px;font-size:12px;cursor:pointer}
@media(max-width:860px){
  .page{padding:24px 16px 60px;grid-template-columns:1fr}
  .hero{grid-template-columns:1fr}
  .bottleneck{font-size:24px}
}
@media print{
  .topbar,.printbtn,.filters{display:none!important}
  body{background:#fff;color:#000}
  .page{max-width:none;padding:0}
  details{border:none}
  details .dbody{display:block!important}
  section{break-inside:avoid}
  table{min-width:0}
}
"""

JS = """
(function(){
  var state={size:'all',quant:'all',ctx:'all'};
  var rows=Array.prototype.slice.call(document.querySelectorAll('tbody tr'));
  function apply(){
    rows.forEach(function(tr){
      var ok=(state.size==='all'||tr.dataset.size===state.size)&&
             (state.quant==='all'||tr.dataset.quant===state.quant)&&
             (state.ctx==='all'||tr.dataset.ctx===state.ctx);
      tr.hidden=!ok;
    });
    document.getElementById('visible-count').textContent=
      rows.filter(function(r){return !r.hidden}).length;
  }
  document.querySelectorAll('.fbtn').forEach(function(b){
    b.addEventListener('click',function(){
      var g=b.dataset.group; state[g]=b.dataset.value;
      document.querySelectorAll('.fbtn[data-group="'+g+'"]').forEach(function(x){
        x.setAttribute('aria-pressed', String(x===b));
      });
      apply();
    });
  });
  rows.forEach(function(tr){
    tr.addEventListener('click',function(){
      var d=document.getElementById('detail-'+tr.dataset.idx);
      if(d){d.hidden=false;d.scrollIntoView({behavior:'smooth',block:'center'});}
    });
  });
  document.getElementById('print-btn').addEventListener('click',function(){window.print()});
  apply();
})();
"""


def render(hw: dict, matrix: dict, conclusion: dict, models: list[dict],
           contexts: list[int], quants: list[str], poly: dict | None,
           title: str) -> str:
    rows = matrix["rows"]
    size_vals = sorted({str(r["params_b"]) for r in rows if r["params_b"] is not None})
    ctx_vals = sorted({r["context"] for r in rows})
    q_vals = [q for q in quants if q in QUANT_BPB]

    def fgroup(label, group, values, fmt=lambda x: x):
        btns = [f'<button class="fbtn" data-group="{group}" data-value="all" aria-pressed="true">全部</button>']
        for v in values:
            btns.append(f'<button class="fbtn" data-group="{group}" data-value="{esc(v)}" '
                        f'aria-pressed="false">{esc(fmt(v))}</button>')
        return (f'<div class="fgroup"><span>{esc(label)}</span><div class="fbtns">'
                + "".join(btns) + "</div></div>")

    parts = []
    parts.append(f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="author" content="B站 · 宝藏二哥AIA">
<title>{esc(title)} · 本地推理硬件适配评估</title>
<style>{CSS}</style></head><body>
<div class="topbar">
  <div class="brand"><b>B站 · 宝藏二哥AIA</b> · 本地推理硬件适配评估</div>
  <div class="navlinks">
    <a href="#s1">结论</a><a href="#s2">矩阵</a><a href="#s3">证据</a>
    <a href="#s4">计算</a><a href="#s5">性能与升级</a><a href="#s6">验证</a>
  </div>
</div>
<div class="page">""")

    # 1 结论首屏
    conf = conclusion.get("confidence", "低")
    miss = conclusion.get("missing_fields", [])
    parts.append(f"""
<section class="hero" id="s1">
  <div class="hero-main">
    <div class="eyebrow">01 · 结论</div>
    <div class="hero-kicker">{esc(conclusion['device'])} · 评估于 {esc(time.strftime('%Y-%m-%d'))}</div>
    <div class="bottleneck">{esc(conclusion['bottleneck'])}</div>
    <div class="bottleneck-label">这是当前最能改变档位判断的限制</div>
    <div class="tier"><div class="tier-label">首选档位</div>
      <div class="tier-value">{esc(conclusion['first'])}</div></div>
    <div class="tier"><div class="tier-label">备选档位</div>
      <div class="tier-value">{esc(conclusion['second'])}</div></div>
  </div>
  <div class="hero-side">
    <div class="fact"><div class="fact-k">数据置信度</div>
      <div class="fact-v">{esc(conf)} <span class="pill unknown">未实测 {len(miss)} 项</span></div></div>
    <div class="fact"><div class="fact-k">档位依据</div>
      <div class="fact-v" style="font-size:12.5px;line-height:1.6">{esc(conclusion['note'])}</div></div>
    <div class="fact"><div class="fact-k">未实测字段</div>
      <div class="fact-v" style="font-size:12.5px">{esc('、'.join(miss) if miss else '无')}</div></div>
  </div>
</section>""")

    # 2 矩阵
    parts.append("""
<section class="sec-head" id="s2"><span class="sec-num">02</span><h2>模型能力矩阵</h2>
  <span class="lead">规模 × 量化 × 上下文 · 三维筛选 · 点击行看拆分</span></section>
<section class="filters">""")
    parts.append(fgroup("模型规模", "size", size_vals, lambda v: f"{v}B"))
    parts.append(fgroup("量化", "quant", q_vals))
    parts.append(fgroup("上下文", "ctx", [str(v) for v in ctx_vals],
                        lambda v: f"{int(v)//1024}k"))
    parts.append("</section>")
    parts.append(f"""
<section class="note" style="margin-bottom:6px">
四态判据：<span class="pill ok">{STATE_GPU}</span> 权重+KV+运行时全进显存预算；
<span class="pill info">{STATE_OFFLOAD}</span> 显存放不下但显存+系统内存共同满足，且引擎支持；
<span class="pill warn">{STATE_CPU}</span> 仅系统内存放得下，<b>只代表容量可行、不代表速度实用</b>；
<span class="pill bad">{STATE_NO}</span> 所有受支持方式均超预算。
<span class="pill unknown">{STATE_UNKNOWN}</span> 是数据缺口，<b>不是第五种运行状态</b>。
</section>""")
    parts.append(f"""
<section class="matrix-wrap">
<table><thead><tr><th>模型</th><th>量化</th><th>上下文</th><th>状态</th>
  <th>权重 GiB</th><th>KV GiB</th><th>瓶颈</th><th>来源</th></tr></thead><tbody>""")
    for i, r in enumerate(rows):
        cls = STATE_CLASS.get(r["state"], "unknown")
        parts.append(f"""
<tr data-idx="{i}" data-size="{esc(r['params_b'])}" data-quant="{esc(r['quant'])}"
    data-ctx="{r['context']}">
  <td>{esc(r['model'])}</td><td>{esc(r['quant'])}</td>
  <td class="num">{r['context']//1024}k</td>
  <td><span class="pill {cls}">{esc(r['state'])}</span></td>
  <td class="num">{num(r.get('weight_gib'),2)}</td>
  <td class="num">{num(r.get('kv_gib'),2)}</td>
  <td>{esc(r['bottleneck'])}</td>
  <td><span class="src {esc(r['source'])}">{esc(r['source'])}</span></td>
</tr>""")
    parts.append("</tbody></table></section>")
    parts.append('<p class="scroll-hint">表格可横向滚动查看全部列 →　当前显示 <b id="visible-count">0</b> 行</p>')

    # 点选详情
    parts.append('<section id="details-area">')
    for i, r in enumerate(rows):
        w, k, rt = r.get("weight_gib"), r.get("kv_gib"), r.get("runtime_gib")
        gb, rb = matrix["gpu_budget"], matrix["ram_budget"]
        pct_w = min(100, (w or 0) / (gb or 1) * 100)
        pct_k = min(100 - pct_w, (k or 0) / (gb or 1) * 100)
        parts.append(f"""
<div class="detail" id="detail-{i}" hidden>
  <h4>{esc(r['model'])} · {esc(r['quant'])} · {r['context']//1024}k · {esc(r['state'])}</h4>
  <div class="kv">
    <div><div class="k">权重</div><div class="v">{fmt_gib(w)}</div></div>
    <div><div class="k">KV Cache</div><div class="v">{fmt_gib(k)}</div></div>
    <div><div class="k">运行时估算</div><div class="v">{fmt_gib(rt)}</div></div>
    <div><div class="k">GPU 预算</div><div class="v">{fmt_gib(gb)}</div></div>
    <div><div class="k">RAM 预算</div><div class="v">{fmt_gib(rb)}</div></div>
  </div>
  <div class="bar"><i style="width:{pct_w:.1f}%"></i>
    <i style="left:{pct_w:.1f}%;width:{max(0,pct_k):.1f}%;background:var(--tv-info)"></i>
    <u style="left:100%"></u></div>
  <div>{esc(r['detail'])}</div>
</div>""")
    parts.append("</section>")

    # 3 关键证据
    gpu = hw.get("gpu", {})
    ram = hw.get("ram", {})
    parts.append("""
<section class="sec-head" id="s3"><span class="sec-num">03</span><h2>关键证据</h2>
  <span class="lead">只列改变判定的数字</span></section>
<section class="matrix-wrap"><table><thead><tr><th>数据</th><th>值</th><th>来源</th>
  <th>改变了什么</th></tr></thead><tbody>""")
    evidence = [
        ("显存总量", fmt_mib(val(gpu.get("vram_total_mib"))), src(gpu.get("vram_total_mib")),
         "决定权重+KV 是否能整模型驻留"),
        ("显存空闲", fmt_mib(val(gpu.get("vram_free_mib"))), src(gpu.get("vram_free_mib")),
         "直接决定 GPU 预算，是档位首选的主因"),
        ("GPU 利用率/温度", f"{num(val(gpu.get('util_pct')),0)}% / {num(val(gpu.get('temp_c')),0)}°C",
         src(gpu.get("util_pct")), "单次采样，不代表稳定负载"),
        ("系统可用内存", fmt_gib(val(ram.get("available_gib"))), src(ram.get("available_gib")),
         "决定部分卸载与仅 CPU 是否可行"),
        ("PCIe 链路", f"Gen {val(gpu.get('pcie_gen'),default='—')} x{val(gpu.get('pcie_width'),default='—')}",
         src(gpu.get("pcie_gen")), "影响卸载时主机↔设备传输，不等于有效带宽"),
        ("有效带宽", "未实测", "缺失", "未运行 bandwidthTest/STREAM，速度区间不可给"),
    ]
    for e in evidence:
        parts.append(f"<tr><td>{esc(e[0])}</td><td class='num'>{esc(e[1])}</td>"
                     f"<td><span class='src {esc(e[2])}'>{esc(e[2])}</span></td>"
                     f"<td>{esc(e[3])}</td></tr>")
    parts.append("</tbody></table></section>")

    # 4 计算依据
    parts.append("""
<details id="s4"><summary>04 · 计算依据（展开查看预算与 KV 公式）</summary>
<div class="dbody"><ul>""")
    for n in matrix["budget_notes"]:
        parts.append(f"<li>{esc(n)}</li>")
    parts.append("""
<li>KV = 2 × L × H<sub>KV</sub> × D × C × B；并发按数量计入。MLA 等非标准架构不套公式。</li>
<li>量化标签 Q4/Q5/Q8 不是精确位宽；有实际权重文件时优先用文件，否则按每参数字节估算并标「估算」。</li>
<li>运行时开销按权重 8% 估算，下限 0.5 GiB，不是固定事实。</li>
<li>「放不下」为预计超预算，不是实测崩溃；失败阶段写在矩阵详情。</li>
</ul></div></details>""")

    # 5 性能与升级
    parts.append("""
<section class="sec-head" id="s5"><span class="sec-num">05</span><h2>性能与升级</h2></section>
<section class="note">
Decode 与 Prefill 必须分开。本机未执行负载测试，<b>没有可靠依据给 Token/s 区间</b>：
按纪律写「暂无法可靠估算」，不使用无来源经验系数。要做可靠估算，需固定模型文件/量化、
输入输出长度、上下文、并发、KV 类型与引擎版本，分别记录 Prefill、Decode、首 Token 延迟、
显存峰值与系统内存峰值。</section>
<details><summary>升级判定（先软件路线，再硬件）</summary><div class="dbody">
<ul><li>先核验软件路线：普通引擎换量化/降上下文；再核验 PolyStrata + KVMem 是否改变可行性。</li>
<li>只有某项升级确实改变四态判定才推荐；同时列出未被改变的格。</li>
<li>无可靠报价来源不编造价格；不改变判定就写「不建议购买」。</li></ul>
</div></details>""")

    # PolyStrata
    parts.append('<details><summary>另一条路：PolyStrata + KVMem（普通引擎与它分开核算）</summary>'
                 '<div class="dbody">')
    if poly:
        ref = esc(poly.get("reference_version", "v0.1.45-poly.9"))
        actual = esc(poly.get("actual_version", "未取得实机版本"))
        parts.append(f"<p>参考版本 {ref}；实机 <b>{actual}</b>。")
        if poly.get("conflict"):
            parts.append(f"<p style='color:var(--tv-accent-2)'>版本/能力冲突：{esc(poly['conflict'])}"
                         "——按实机裁决，参考文档只作背景。</p>")
        for k, v in (poly.get("checks") or {}).items():
            parts.append(f"<li>{esc(k)}：{esc(v)}</li>")
        parts.append("</p>")
    else:
        parts.append("<p>未提供 PolyStrata 实机数据。本机 AI Vault / Worker 版本、能力清单、"
                     "模型兼容性均未核验 → <b>不判定</b>。不得把参考文档能力表当本机结论。</p>")
    parts.append("""<p>约束：单 GPU、不支持多 GPU 与 batch MTP；启用 KVMem 不允许 truncate_middle。
完整模型文件大小不等于 GPU 显存占用。host-mib 是 KV 配额，不是 Worker 内存上限。</p>
</div></details>""")

    # 6 验证方法
    parts.append("""
<section class="sec-head" id="s6"><span class="sec-num">06</span><h2>验证方法</h2></section>
<section class="note">固定：模型文件、量化、引擎版本、上下文、并发、卸载参数。
实测：Token/s（Decode 与 Prefill 分开）、首 Token 延迟、显存峰值、系统内存峰值、磁盘 I/O。
目的是验证或推翻本页预测；本页所有「估算」格在实测前都不算结论。</section>

<details><summary>数据缺口与未实测项清单（及其对结论的影响）</summary><div class="dbody"><ul>""")
    for f in (conclusion.get("missing_fields") or ["无"]):
        parts.append(f"<li>{esc(f)}：影响速度判断与卸载临界点精度；不影响容量四态的基本判定</li>")
    parts.append("""<li>稳定区间读数：单次采样可能偏高/偏低，不改变「能不能跑」的判定</li>
<li>有效带宽：缺失 → 不能给速度区间，不能说明「更快」</li>
</ul></div></details>

<footer><span>B站 · 宝藏二哥AIA · 本地推理硬件适配评估</span>
<span>单文件离线报告 · 色值 ThemeVault #001 夜灯 · 生成于 """ +
             esc(time.strftime("%Y-%m-%d %H:%M")) + """</span>
<button class="printbtn" id="print-btn">打印 / 存 PDF</button></footer>
</div><script>""" + JS + """</script></body></html>""")
    return "".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description="生成本地推理硬件适配报告")
    ap.add_argument("--hardware", required=True, help="probe_hw.py 产出的 hardware.json")
    ap.add_argument("--models", required=True,
                    help='模型清单 JSON：{"models":[{"name","params_b","arch","layers",'
                         '"kv_heads","head_dim","kv_bytes","weights":{quant:gib}}]}')
    ap.add_argument("--poly", default=None, help="PolyStrata 实机核验 JSON（可选）")
    ap.add_argument("--contexts", default="4096,8192,16384,32768")
    ap.add_argument("--quants", default="Q4_K_M,Q5_K_M,Q8_0,F16")
    ap.add_argument("--out", default="hardware-report.html")
    ap.add_argument("--title", default="本机硬件适配评估")
    args = ap.parse_args()

    with open(args.hardware, encoding="utf-8") as fh:
        hw = json.load(fh)
    with open(args.models, encoding="utf-8") as fh:
        models_doc = json.load(fh)
    models = models_doc.get("models", models_doc) if isinstance(models_doc, dict) else models_doc
    contexts = [int(x) for x in args.contexts.split(",") if x.strip()]
    quants = [x.strip() for x in args.quants.split(",") if x.strip()]
    poly = None
    if args.poly and os.path.exists(args.poly):
        with open(args.poly, encoding="utf-8") as fh:
            poly = json.load(fh)

    matrix = compute_matrix(hw, models, contexts, quants)
    conclusion = pick_conclusion(matrix, hw)
    html_text = render(hw, matrix, conclusion, models, contexts, quants, poly, args.title)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(html_text)

    print(f"四态分布：")
    for st in STATE_ORDER:
        n = sum(1 for r in matrix["rows"] if r["state"] == st)
        if n:
            print(f"  {st}: {n}")
    print(f"报告：{os.path.abspath(args.out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
