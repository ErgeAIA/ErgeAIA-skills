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
            "svg": "/out/%s/%s.svg" % (run, stem)}


PAGE = """<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>字体与生成 · raster-to-svg</title>
<style>
:root{--bg:#0f1419;--panel:#161d25;--line:#243040;--fg:#e6edf3;--dim:#8b98a5;--accent:#f0a03c}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.6 -apple-system,'Segoe UI','Microsoft YaHei',sans-serif}
header{padding:20px 28px;border-bottom:1px solid var(--line)}
h1{font-size:18px;margin:0 0 4px}
.sub{color:var(--dim);font-size:13px}
main{display:grid;grid-template-columns:340px 1fr;gap:0;height:calc(100vh - 82px)}
aside{padding:20px 24px;border-right:1px solid var(--line);overflow:auto}
.stage{display:flex;align-items:center;justify-content:center;background:#f7f7f5;position:relative}
.pv{color:#000;white-space:nowrap;line-height:1.4;text-align:center}
label{display:block;color:var(--dim);font-size:12px;margin:14px 0 6px}
input[type=text],select{width:100%;background:var(--panel);color:var(--fg);border:1px solid var(--line);
  border-radius:7px;padding:8px 10px;font:inherit}
input[type=range]{width:100%;accent-color:var(--accent)}
button{width:100%;margin-top:18px;background:var(--accent);color:#111;border:0;border-radius:8px;
  padding:11px;font:inherit;font-weight:600;cursor:pointer}
button:disabled{opacity:.5;cursor:progress}
.row{display:flex;gap:10px}
.row>div{flex:1}
.hint{color:var(--dim);font-size:12px;margin-top:12px}
pre{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px;
  font-size:11px;max-height:180px;overflow:auto;color:#c8d3dd;white-space:pre-wrap}
.tag{display:inline-block;background:var(--panel);border:1px solid var(--line);border-radius:6px;
  padding:2px 8px;font-size:12px;color:var(--dim);margin-left:8px}
</style></head><body>
<header><h1>字体与生成 <span class="tag">raster-to-svg</span></h1>
<div class="sub">预览是纯 CSS，不描摹；只有点「生成」才跑脚本。字体来自本机已安装字体。</div></header>
<main>
<aside>
  <label>文字</label><input type="text" id="text" value="织音">
  <label>字体（本机 CJK 字体 __COUNT__ 个）</label>
  <input type="text" id="q" placeholder="过滤：输入字体名，如 思源 / PuHui / 宋">
  <select id="font"></select>
  <div class="row"><div><label>字号</label><input type="range" id="size" min="60" max="300" step="2" value="160"></div>
  <div><label>字距</label><input type="range" id="gap" min="0" max="120" step="1" value="18"></div></div>
  <div class="row"><div><span class="hint" id="sizeV">160 px</span></div><div><span class="hint" id="gapV">18 px</span></div></div>
  <button id="go">生成 SVG 与可编辑报告</button>
  <div class="hint" id="state">选好字体，右侧预览确认后再生成。</div>
  <pre id="log"></pre>
</aside>
<div class="stage"><div class="pv" id="pv">织音</div></div>
</main>
<script>
var FONTS = __FONTS__;
var fonts = document.getElementById('font'), pv = document.getElementById('pv'), face = null;
FONTS.forEach(function(f, i){
  var o = document.createElement('option'); o.value = i; o.textContent = f.label; fonts.appendChild(o);
});
function loadFace(i){
  var name = 'R2S_' + i;
  if(!face){ face = document.createElement('style'); document.head.appendChild(face); }
  face.textContent = '@font-face{font-family:' + name + ';src:url(/font/' + i + ')}';
  pv.style.fontFamily = name + ', sans-serif';
}
function render(){
  var s = +document.getElementById('size').value, g = +document.getElementById('gap').value;
  pv.textContent = document.getElementById('text').value || '织音';
  pv.style.fontSize = s + 'px';
  pv.style.letterSpacing = g + 'px';
  document.getElementById('sizeV').textContent = s + ' px';
  document.getElementById('gapV').textContent = g + ' px';
}
document.getElementById('q').addEventListener('input', function(){
  var q = this.value.trim().toLowerCase();
  [].slice.call(fonts.options).forEach(function(o){
    o.style.display = (!q || o.textContent.toLowerCase().indexOf(q) >= 0) ? '' : 'none';
  });
  var first = [].slice.call(fonts.options).filter(function(o){ return o.style.display !== 'none'; })[0];
  if(first){ fonts.value = first.value; loadFace(+first.value); render(); }
});
fonts.addEventListener('change', function(){ loadFace(+fonts.value); render(); });
document.getElementById('text').addEventListener('input', render);
document.getElementById('size').addEventListener('input', render);
document.getElementById('gap').addEventListener('input', render);
document.getElementById('go').addEventListener('click', function(){
  var btn = this, st = document.getElementById('state');
  btn.disabled = true; st.textContent = '正在描摹……';
  document.getElementById('log').textContent = '';
  fetch('/generate', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({text: document.getElementById('text').value,
      font: +fonts.value, size: +document.getElementById('size').value,
      gap: +document.getElementById('gap').value})})
  .then(function(r){ return r.json(); })
  .then(function(d){
    btn.disabled = false;
    document.getElementById('log').textContent = d.log || '';
    if(d.ok){
      st.textContent = '生成完成，正在打开报告。';
      window.open(d.url, '_blank');
      var a = document.createElement('a'); a.href = d.svg; a.textContent = '下载 SVG';
      a.style.cssText = 'display:block;margin-top:8px;color:#f0a03c'; st.appendChild(a);
    } else { st.textContent = '生成失败，看下面的日志。'; }
  })
  .catch(function(e){ btn.disabled = false; st.textContent = '请求失败：' + e; });
});
loadFace(0); render();
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
                    "__FONTS__", json.dumps([{"label": f["label"]} for f in fonts], ensure_ascii=False))
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
