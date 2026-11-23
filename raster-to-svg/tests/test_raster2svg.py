# -*- coding: utf-8 -*-
"""Self-checks for raster2svg.py.

Run from the skill directory:
    uv run --with numpy --with opencv-python-headless --with resvg-py \
        python -m unittest discover -s tests -v
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
SCRIPT = os.path.join(SKILL, "scripts", "raster2svg.py")
FIX = os.path.join(HERE, "fixtures")


def run(*args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, SCRIPT] + list(args),
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env)


def run_studio(*args):
    studio = os.path.join(SKILL, "scripts", "studio.py")
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, studio] + list(args),
                          capture_output=True, text=True, encoding="utf-8", env=env)


def have_renderer():
    try:
        import resvg_py  # noqa: F401
        return True
    except Exception:
        import shutil as sh
        return bool(sh.which("rsvg-convert"))


class TestCli(unittest.TestCase):
    def test_help_lists_core_flags(self):
        r = run("--help")
        self.assertEqual(r.returncode, 0, r.stderr)
        for flag in ("--mode", "--ss", "--min-area", "--check", "--colors"):
            self.assertIn(flag, r.stdout)

    def test_version(self):
        r = run("--version")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("0.1.0", r.stdout)

    def test_missing_input_is_error_exit_2(self):
        r = run("-i", os.path.join(FIX, "does-not-exist.png"))
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("cannot read image", r.stderr)


class TestMono(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _trace(self, name, *extra):
        src = os.path.join(FIX, name)
        out = os.path.join(self.tmp.name, name[:-4])
        r = run("-i", src, "-o", out, *extra)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        svg = os.path.join(out, name[:-4] + ".svg")
        js = os.path.join(out, name[:-4] + "_coords.json")
        with open(js, encoding="utf-8") as f:
            meta = json.load(f)
        return svg, meta, r

    def test_grouped_svg_and_coordinates(self):
        svg, meta, r = self._trace("kou_96.png")
        with open(svg, encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn('<g id="glyph-01"', text)
        self.assertIn("fill-rule=\"evenodd\"", text)
        self.assertEqual(len(meta["components"]), 1)
        comp = meta["components"][0]
        self.assertEqual(comp["engine"], "polygon")          # 口 is rectilinear
        self.assertTrue(comp.get("holes"), "口 must keep its counter as a hole")
        self.assertTrue(comp["vertices_xy"])
        self.assertIn("iou_rendered", meta)
        self.assertFalse(meta["surrogate_metric"], "a renderer must be present in CI")

    @unittest.skipUnless(have_renderer(), "needs resvg-py or rsvg-convert")
    def test_rendered_iou_meets_gate(self):
        _svg, meta, r = self._trace("kou_96.png", "--check")
        self.assertGreaterEqual(meta["iou_rendered"], 0.95, meta)
        self.assertAlmostEqual(meta["ink_ratio"], 1.0, delta=0.06)

    def test_small_dot_is_not_deleted(self):
        # regression: the old default --min-area 300 ate the 189 px dot of 之 at 128 px em
        svg, meta, r = self._trace("zhi_128.png")
        self.assertEqual(len(meta["components"]), 2, meta["components"])

    @unittest.skipUnless(have_renderer(), "needs resvg-py or rsvg-convert")
    def test_low_contrast_ink_is_traced(self):
        # regression: a fixed 127.5 coverage level traced nothing at all on #999 ink
        _svg, meta, r = self._trace("grey60_yong.png")
        self.assertGreaterEqual(meta.get("iou_rendered", 0), 0.85, meta)
        self.assertLessEqual(meta["ink_ratio"], 1.10)

    def test_svg_ids_are_unique(self):
        # regression: one <g> per component produced duplicate id="glyph-02" x N
        import re as _re
        svg, meta, r = self._trace("zhi_128.png")
        with open(svg, encoding="utf-8") as fh:
            text = fh.read()
        ids = _re.findall(r'id="([^"]+)"', text)
        self.assertEqual(len(ids), len(set(ids)), "duplicate ids: %s" % ids)

    def test_deterministic_bytes(self):
        src = os.path.join(FIX, "kou_96.png")
        digests = []
        for i in (1, 2):
            out = os.path.join(self.tmp.name, "det%d" % i)
            r = run("-i", src, "-o", out)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(os.path.join(out, "kou_96.svg"), "rb") as f:
                digests.append(hashlib.sha256(f.read()).hexdigest())
        self.assertEqual(digests[0], digests[1])


class TestTextAndReport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_text_mode_writes_svg_and_report(self):
        font = None
        for cand in ("C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf",
                     "/System/Library/Fonts/PingFang.ttc",
                     "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
            if os.path.exists(cand):
                font = cand
                break
        if font is None:
            self.skipTest("no system font to render text with")
        r = run("--text", "口A", "--font", font, "--size", "96", "-o", self.tmp.name)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        html = os.path.join(self.tmp.name, "口A.html")
        svg = os.path.join(self.tmp.name, "口A.svg")
        self.assertTrue(os.path.exists(svg), "text mode must emit an SVG")
        self.assertTrue(os.path.exists(html), "text mode must emit the HTML report")

    def test_unicode_input_path(self):
        # regression: cv2.imread cannot open non-ASCII paths, so 桌面/截图.png used to fail
        src = os.path.join(self.tmp.name, "中文 截图.png")
        with open(os.path.join(FIX, "kou_96.png"), "rb") as a, open(src, "wb") as b:
            b.write(a.read())
        r = run("-i", src, "-o", self.tmp.name)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.tmp.name, "中文 截图.svg")))

    def test_report_is_self_contained(self):
        src = os.path.join(FIX, "kou_96.png")
        r = run("-i", src, "-o", self.tmp.name)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        html = os.path.join(self.tmp.name, "kou_96.html")
        with open(html, encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn("<svg", text)
        self.assertIn("data:image/png;base64,", text)
        self.assertIn("滚轮缩放", text)
        self.assertLess(os.path.getsize(html), 3 * 1024 * 1024)

    def test_report_hides_node_overlay(self):
        src = os.path.join(FIX, "kou_96.png")
        r = run("-i", src, "-o", self.tmp.name)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        with open(os.path.join(self.tmp.name, "kou_96.html"), encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn('<g id="r2s-nodes" style="display:none"', text,
                      "node overlay must start hidden or the vector view shows stray dots")
        self.assertIn('"夜灯"', text, "theme palette should be embedded")

    def test_report_is_editable(self):
        src = os.path.join(FIX, "kou_96.png")
        r = run("-i", src, "-o", self.tmp.name)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        with open(os.path.join(self.tmp.name, "kou_96.html"), encoding="utf-8") as fh:
            text = fh.read()
        for marker in ('id="ed-mode"', 'id="ed-spacing"', 'id="ed-weight"',
                       'id="ed-undo"', 'id="ed-export"', 'r2s-edit-nodes',
                       "paintOrder", "ed-palette", "normHex", "ed-labels",
                       "r2s-edit-labels"):
            self.assertIn(marker, text, "missing editor marker: " + marker)

    def test_no_html_flag_skips_report(self):
        r = run("-i", os.path.join(FIX, "kou_96.png"), "-o", self.tmp.name, "--no-html")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, "kou_96.html")))


class TestColour(unittest.TestCase):
    def _run_icon(self, k):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        r = run("-i", os.path.join(FIX, "icon_flat.png"), "-o", tmp.name,
                "--colors", str(k))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        with open(os.path.join(tmp.name, "icon_flat.svg"), encoding="utf-8") as fh:
            text = fh.read()
        return text, r

    def test_flat_icon_layers(self):
        text, r = self._run_icon(6)
        self.assertIn("<rect", text)
        self.assertIn("<path", text)
        self.assertEqual(text.count("<path"), 4)          # 4 shapes over 1 background
        self.assertIn("layers", r.stdout)

    def test_high_k_does_not_lose_layers(self):
        # K is an upper bound: antialiasing fringe clusters are folded, so K=12 must
        # not end up with fewer real layers than K=6 (this regressed once).
        low, _ = self._run_icon(6)
        high, _ = self._run_icon(12)
        self.assertGreaterEqual(high.count("<path"), low.count("<path"))

    @unittest.skipUnless(have_renderer(), "needs resvg-py or rsvg-convert")
    def test_flat_icon_psnr(self):
        _text, r = self._run_icon(6)
        line = [l for l in r.stdout.splitlines() if l.startswith("psnr_rendered")][0]
        self.assertGreaterEqual(float(line.split(":")[-1].split()[0]), 30.0, r.stdout)


if __name__ == "__main__":
    unittest.main()


class TestStudio(unittest.TestCase):
    """The font studio must list real CJK faces, not tofu-only ones."""

    def test_list_fonts_is_json(self):
        r = run_studio("--list-fonts")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0, "no font found on this machine")
        self.assertTrue(any(f.get("cjk") for f in data), "no CJK-capable font found")
        for item in data[:5]:
            self.assertTrue(os.path.isfile(item["path"]), item["path"])
            self.assertTrue(item["label"])

    def test_font_index_reaches_the_renderer(self):
        fonts = json.loads(run_studio("--list-fonts").stdout)
        cjk = [f for f in fonts if f.get("cjk")] or fonts
        pick = cjk[0]
        with tempfile.TemporaryDirectory() as tmp:
            r = run("--text", "织", "--font", pick["path"], "--font-index",
                    str(pick["index"]), "--size", "96", "-o", tmp, "--no-html")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertTrue(os.path.isfile(os.path.join(tmp, "织.svg")))
