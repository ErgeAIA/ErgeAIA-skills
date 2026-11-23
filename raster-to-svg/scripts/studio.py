#!/usr/bin/env python3
"""Font studio: preview a system font, then generate the SVG on demand.

Static HTML cannot enumerate fonts or run the tracer, so this small local server
does both. Preview is pure CSS (no rasterising, no tracing); the CLI runs only
when you press "生成".

  python scripts/studio.py --list-fonts          # JSON of CJK-capable fonts
  python scripts/studio.py                       # serve http://127.0.0.1:8765
  python scripts/studio.py --port 9000
"""
import argparse
import contextlib
import io
import json
import os
import sys
import tempfile
import threading
import uuid
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from PIL import Image, ImageDraw, ImageFont

CACHE = os.path.join(tempfile.gettempdir(), "raster2svg-fonts-v2.json")
RUNS = {}


def font_dirs():
    dirs = []
    if sys.platform.startswith("win"):
        dirs += [os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
                 os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts")]
    elif sys.platform == "darwin":
        dirs += ["/System/Library/Fonts", "/Library/Fonts", os.path.expanduser("~/Library/Fonts")]
    else:
        dirs += ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts"),
                 os.path.expanduser("~/.local/share/fonts")]
    return [d for d in dirs if d and os.path.isdir(d)]


def _render_pair(font):
    """Two CJK glyphs; a font that draws tofu produces identical bitmaps."""
    out = []
    for ch in ("织", "音"):
        im = Image.new("L", (44, 44), 255)
        ImageDraw.Draw(im).text((3, 3), ch, font=font, fill=0)
        out.append(im.tobytes())
    return out


def _probe(path):
    """First TTC index that really draws CJK glyphs, plus (family, style)."""
    for idx in range(6):
        try:
            f = ImageFont.truetype(path, 24, index=idx)
        except Exception:
            return None
        a, b = _render_pair(f)
        ink = max(255 - min(a), 255 - min(b))
        if ink > 55 and a != b:  # real glyphs differ; tofu boxes do not
            try:
                family, style = f.getname()
            except Exception:
                family, style = os.path.basename(path), ""
            return {"family": family, "style": style, "path": path, "index": idx}
    return None


def scan(cache=True):
    if cache and os.path.isfile(CACHE):
        try:
            with open(CACHE, encoding="utf-8") as fh:
                data = json.load(fh)
            stamp = max((os.path.getmtime(d) for d in font_dirs()), default=0)
            if data.get("stamp") == stamp and data.get("fonts"):
                return data["fonts"]
        except Exception:
            pass
    found, seen = [], set()
    for d in font_dirs():
        for root, _dirs, files in os.walk(d):
            for name in files:
                if not name.lower().endswith((".ttf", ".otf", ".ttc", ".ttf")):
                    continue
                item = _probe(os.path.join(root, name))
                if not item:
                    continue
                key = (item["family"], item["style"])
                if key in seen:
                    continue
                seen.add(key)
                item["label"] = item["family"] + ((" · " + item["style"]) if item["style"] else "")
                found.append(item)
    found.sort(key=lambda x: (x["family"].lower(), x["style"]))
    if cache:
        try:
            stamp = max((os.path.getmtime(d) for d in font_dirs()), default=0)
            with open(CACHE, "w", encoding="utf-8") as fh:
                json.dump({"stamp": stamp, "fonts": found}, fh, ensure_ascii=False)
        except Exception:
            pass
    return found


def generate(text, font, size, gap):
    import raster2svg as R
    outdir = tempfile.mkdtemp(prefix="r2s-studio-")
    buf = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            R.main(["--text", text, "--font", font["path"], "--font-index", str(font["index"]),
                    "--size", str(size), "--gap", str(gap), "-o", outdir, "--check"])
        except SystemExit as exc:
            code = int(exc.code or 0)
        except Exception as exc:  # noqa: BLE001 - surfaced to the page
            code = 2
            buf.write("\n" + repr(exc))
    log = buf.getvalue()
    stem = R.safe_stem(text)
    html = os.path.join(outdir, stem + ".html")
    run = uuid.uuid4().hex[:12]
    RUNS[run] = outdir
    return {"ok": code == 0, "code": code, "log": log[-4000:], "run": run, "stem": stem,
            "url": "/out/%s/%s.html" % (run, stem),
            "svg": "/out/%s/%s.svg" % (run, stem),
            "thumb": "/out/%s/%s.svg" % (run, stem),
            "thumb_src": "/out/%s/%s_source.png" % (run, stem)}


PAGE = """<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>字体对比与生成 · raster-to-svg</title>
<style>
:root{--bg:#0f1419;--panel:#161d25;--line:#243040;--fg:#e6edf3;--dim:#8b98a5;--accent:#f0a03c}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.6 -apple-system,"Segoe UI","Microsoft YaHei",sans-serif}
header{padding:18px 28px;border-bottom:1px solid var(--line)}
h1{font-size:18px;margin:0 0 4px}
.sub{color:var(--dim);font-size:13px}
main{display:grid;grid-template-columns:320px 1fr;height:calc(100vh - 80px)}
aside{padding:18px 22px;border-right:1px solid var(--line);overflow:auto}
.stage{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;padding:14px;background:#f7f7f5;overflow:auto}
.col{background:#fff;border:1px solid #e3e3de;border-radius:10px;display:flex;flex-direction:column;min-width:0}
.hd{font-size:12px;color:#6b6b66;padding:8px 12px;border-bottom:1px solid #eee;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.hd b{color:#111}
.pvwrap{flex:1;display:flex;align-items:center;justify-content:center;padding:10px;overflow:hidden}
.pv{color:#000;white-space:nowrap;line-height:1.35;text-align:center}
.gen{margin:0 10px 10px;background:var(--accent);color:#111;border:0;border-radius:7px;padding:8px;font:inherit;font-weight:600;cursor:pointer}
.gen:disabled{opacity:.5;cursor:progress}
label{display:block;color:var(--dim);font-size:12px;margin:12px 0 5px}
input[type=text],select{width:100%;background:var(--panel);color:var(--fg);border:1px solid var(--line);border-radius:7px;padding:7px 9px;font:inherit}
input[type=range]{width:100%;accent-color:var(--accent)}
.slot{display:flex;gap:8px;align-items:center;margin-bottom:6px}
.slot b{width:16px;color:var(--accent);font-size:13px}
.fav{background:var(--panel);color:var(--accent);border:1px solid var(--line);border-radius:7px;padding:6px 9px;font:inherit;cursor:pointer}
.fav.on{background:var(--accent);color:#111;border-color:var(--accent)}
.hint{color:var(--dim);font-size:12px;margin-top:10px}
.hist{margin-top:6px;display:grid;grid-template-columns:1fr 1fr;gap:8px}
.hitem{display:block;background:var(--panel);border:1px solid var(--line);border-radius:7px;overflow:hidden;text-decoration:none;color:var(--dim);font-size:11px}
.hitem img{width:100%;display:block;background:#fff}
.hitem span{display:block;padding:4px 6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
</style></head><body>
<header><h1>字体对比与生成 <span class="tag" style="background:#161d25;border:1px solid #243040;border-radius:6px;padding:2px 8px;font-size:12px;color:#8b98a5">raster-to-svg</span></h1>
<div class="sub">三栏同屏比字体，预览是纯 CSS（不描摹）；点某一栏的「生成」才跑脚本。</div></header>
<main>
<aside>
  <label>文字</label><input type="text" id="text" value="织音">
  <label>过滤（三栏共用）</label><input type="text" id="q" placeholder="思源 / PuHui / 宋">
  <label>候选字体（本机 CJK 字体 __COUNT__ 个）</label>
  <div class="slot"><b>A</b><select class="fsel" data-slot="0"></select><button class="fav" data-slot="0" title="收藏这款字体">★</button></div>
  <div class="slot"><b>B</b><select class="fsel" data-slot="1"></select><button class="fav" data-slot="1" title="收藏这款字体">★</button></div>
  <div class="slot"><b>C</b><select class="fsel" data-slot="2"></select><button class="fav" data-slot="2" title="收藏这款字体">★</button></div>
  <label>字号 <span id="sizeV" class="hint"></span></label><input type="range" id="size" min="60" max="280" step="2" value="150">
  <label>字距 <span id="gapV" class="hint"></span></label><input type="range" id="gap" min="0" max="120" step="1" value="16">
  <div class="hint" id="state">选好三款字体，右侧对比后再生成。</div>
  <div class="hint" style="margin-top:14px">最近生成</div><div class="hist" id="hist"></div>
</aside>
<div class="stage">
  <div class="col" data-slot="0"><div class="hd"><b>A</b> <span class="nm"></span></div>
    <div class="pvwrap"><div class="pv"></div></div><button class="gen">生成这一栏</button></div>
  <div class="col" data-slot="1"><div class="hd"><b>B</b> <span class="nm"></span></div>
    <div class="pvwrap"><div class="pv"></div></div><button class="gen">生成这一栏</button></div>
  <div class="col" data-slot="2"><div class="hd"><b>C</b> <span class="nm"></span></div>
    <div class="pvwrap"><div class="pv"></div></div><button class="gen">生成这一栏</button></div>
</div>
</main>
<script>
var FONTS = __FONTS__;
var sels = [].slice.call(document.querySelectorAll(".fsel"));
var FAV_KEY = "r2s.favs.v1", PICK_KEY = "r2s.picks.v1";
function load(key, dflt){ try{ var v = JSON.parse(localStorage.getItem(key) || "null"); return v || dflt; }catch(e){ return dflt; } }
function save(key, val){ try{ localStorage.setItem(key, JSON.stringify(val)); }catch(e){} }
var favs = load(FAV_KEY, []);
var faces = sels.map(function(){
  var s = document.createElement("style"); document.head.appendChild(s); return s;
});
function fill(sel, keep){
  var cur = keep !== undefined ? String(keep) : sel.value;
  sel.textContent = "";
  var add = function(parent, list){
    list.forEach(function(i){
      var f = FONTS[i], o = document.createElement("option");
      o.value = i; o.textContent = f.label;
      o.dataset.key = f.keys || f.label.toLowerCase();
      parent.appendChild(o);
    });
  };
  if(favs.length){
    var grp = document.createElement("optgroup"); grp.label = "收藏"; add(grp, favs); sel.appendChild(grp);
  }
  var rest = FONTS.map(function(_f, i){ return i; }).filter(function(i){ return favs.indexOf(i) < 0; });
  var grp2 = document.createElement("optgroup"); grp2.label = "全部字体"; add(grp2, rest); sel.appendChild(grp2);
  if(cur !== undefined && cur !== "") sel.value = cur;
}
// defaults: last session's picks, else the first three distinct families
var fams = [], picks = [];
FONTS.forEach(function(f, i){ if(fams.indexOf(f.family) < 0){ fams.push(f.family); if(picks.length < 3) picks.push(i); } });
var saved = load(PICK_KEY, []);
sels.forEach(function(sel, i){
  var want = (saved[i] !== undefined && FONTS[saved[i]]) ? saved[i] : (picks[i] || 0);
  fill(sel, want);
});
function remember(){ save(PICK_KEY, sels.map(function(sel){ return +sel.value; })); }
function toggleFav(slot){
  var i = +sels[slot].value, at = favs.indexOf(i);
  if(at >= 0) favs.splice(at, 1); else favs.push(i);
  save(FAV_KEY, favs);
  var keep = sels.map(function(sel){ return +sel.value; });
  sels.forEach(function(sel, k){ fill(sel, keep[k]); });
  paintFav(); render();
}
function applyFace(i, slot){
  var name = "R2S_" + slot + "_" + i;
  faces[slot].textContent = "@font-face{font-family:" + name + ";src:url(/font/" + i + ")}";
  return name + ", sans-serif";
}
function render(){
  var txt = document.getElementById("text").value || "织音";
  var size = +document.getElementById("size").value, gap = +document.getElementById("gap").value;
  document.getElementById("sizeV").textContent = size + " px";
  document.getElementById("gapV").textContent = gap + " px";
  sels.forEach(function(sel, i){
    var col = document.querySelector('.col[data-slot="' + i + '"]');
    var pv = col.querySelector(".pv");
    pv.textContent = txt;
    pv.style.fontSize = size + "px";
    pv.style.letterSpacing = gap + "px";
    pv.style.fontFamily = applyFace(+sel.value, i);
    col.querySelector(".nm").textContent = FONTS[+sel.value].label;
  });
}
document.getElementById("q").addEventListener("input", function(){
  var q = this.value.trim().toLowerCase();
  sels.forEach(function(sel){
    [].slice.call(sel.options).forEach(function(o){
      o.style.display = (!q || (o.dataset.key || "").indexOf(q) >= 0) ? "" : "none";
    });
    var vis = [].slice.call(sel.options).filter(function(o){ return o.style.display !== "none"; });
    if(!vis.length){
      [].slice.call(sel.options).forEach(function(o){ o.style.display = ""; });
      document.getElementById("state").textContent = "没有匹配的字体，已恢复全部";
      return;
    }
    if(sel.selectedOptions[0] && sel.selectedOptions[0].style.display === "none") sel.value = vis[0].value;
  });
  render();
});
sels.forEach(function(sel){ sel.addEventListener("change", function(){ remember(); paintFav(); render(); }); });
[].slice.call(document.querySelectorAll(".fav")).forEach(function(b){
  b.addEventListener("click", function(){ toggleFav(+b.dataset.slot); });
});
function paintFav(){
  [].slice.call(document.querySelectorAll(".fav")).forEach(function(b){
    var on = favs.indexOf(+sels[+b.dataset.slot].value) >= 0;
    b.classList.toggle("on", on);
  });
}
["text","size","gap"].forEach(function(id){ document.getElementById(id).addEventListener("input", render); });
var hist = document.getElementById("hist");
function addHistory(entry){
  var a = document.createElement("a");
  a.className = "hitem"; a.href = entry.url; a.target = "_blank";
  var im = document.createElement("img"); im.src = entry.thumb; a.appendChild(im);
  var sp = document.createElement("span"); sp.textContent = entry.label; a.appendChild(sp);
  hist.insertBefore(a, hist.firstChild);
  while(hist.children.length > 10) hist.removeChild(hist.lastChild);
}
[].slice.call(document.querySelectorAll(".gen")).forEach(function(btn){
  btn.addEventListener("click", function(){
    var col = btn.parentNode, slot = +col.getAttribute("data-slot");
    var sel = sels[slot], st = document.getElementById("state");
    btn.disabled = true; st.textContent = "正在描摹 " + FONTS[+sel.value].label + " ……";
    fetch("/generate", {method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({text: document.getElementById("text").value,
        font: +sel.value, size: +document.getElementById("size").value,
        gap: +document.getElementById("gap").value})})
    .then(function(r){ return r.json(); })
    .then(function(d){
      btn.disabled = false;
      if(d.ok){ st.textContent = "生成完成：" + FONTS[+sel.value].label;
        addHistory({url: d.url, thumb: d.thumb, label: FONTS[+sel.value].label});
        window.open(d.url, "_blank"); }
      else { st.textContent = "生成失败（看控制台日志）"; }
    })
    .catch(function(e){ btn.disabled = false; st.textContent = "请求失败：" + e; });
  });
});
render(); paintFav();
</script></body></html>"""


def make_handler(fonts):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):  # quiet
            pass

        def _send(self, code, body, ctype="application/json; charset=utf-8"):
            if isinstance(body, str):
                body = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            u = urlparse(self.path)
            if u.path == "/":
                page = PAGE.replace("__COUNT__", str(len(fonts))).replace(
                    "__FONTS__", json.dumps([{"label": f["label"], "family": f["family"],
                                               "keys": (f["label"] + " " + f["path"]).lower()}
                                              for f in fonts], ensure_ascii=False))
                return self._send(200, page, "text/html; charset=utf-8")
            if u.path.startswith("/font/"):
                try:
                    i = int(u.path.split("/")[2])
                    path = fonts[i]["path"]
                except Exception:
                    return self._send(404, b"no")
                try:
                    with open(path, "rb") as fh:
                        return self._send(200, fh.read(), "font/ttf")
                except Exception:
                    return self._send(404, b"no")
            if u.path.startswith("/out/"):
                parts = u.path.split("/")
                if len(parts) < 4 or parts[2] not in RUNS:
                    return self._send(404, b"no")
                name = os.path.basename(parts[3])
                full = os.path.join(RUNS[parts[2]], name)
                if not os.path.isfile(full):
                    return self._send(404, b"no")
                ctype = "text/html; charset=utf-8" if name.endswith(".html") else (
                    "image/svg+xml" if name.endswith(".svg") else "image/png")
                with open(full, "rb") as fh:
                    return self._send(200, fh.read(), ctype)
            return self._send(404, b"no")

        def do_POST(self):
            if urlparse(self.path).path != "/generate":
                return self._send(404, b"no")
            try:
                n = int(self.headers.get("Content-Length") or 0)
                data = json.loads(self.rfile.read(n) or b"{}")
                f = fonts[int(data.get("font", 0))]
                res = generate(str(data.get("text") or "织音"), f,
                               int(data.get("size") or 160), int(data.get("gap") or 18))
            except Exception as exc:  # noqa: BLE001
                return self._send(500, json.dumps({"ok": False, "log": repr(exc)}, ensure_ascii=False))
            return self._send(200, json.dumps(res, ensure_ascii=False))
    return H


def main(argv=None):
    ap = argparse.ArgumentParser(description="Preview a system font, then trace on demand")
    ap.add_argument("--list-fonts", action="store_true", help="print CJK-capable fonts as JSON")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--no-cache", action="store_true")
    args = ap.parse_args(argv)

    fonts = scan(cache=not args.no_cache)
    if args.list_fonts:
        print(json.dumps(fonts, ensure_ascii=False, indent=1))
        return 0
    if not fonts:
        print("no CJK-capable font found", file=sys.stderr)
        return 2
    srv = ThreadingHTTPServer((args.host, args.port), make_handler(fonts))
    print("studio on http://%s:%d  (%d fonts)" % (args.host, args.port, len(fonts)))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())