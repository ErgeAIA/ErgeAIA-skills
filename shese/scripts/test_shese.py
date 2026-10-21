"""shese 计算层单测：官方锚定 + 边界条件 + CLI 退出码。

运行：python ErgeAIA-skills/shese/scripts/test_shese.py
（或 python -m unittest discover -s ErgeAIA-skills/shese/scripts -p "test_*.py"）
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "shese.py"


def load_module():
    spec = importlib.util.spec_from_file_location("shese", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


shese = load_module()


def run_cli(*argv):
    proc = subprocess.run([sys.executable, str(SCRIPT), *argv], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout, proc.stderr


class TestHexParsing(unittest.TestCase):
    def test_three_digit_expands_nibbles(self):
        self.assertEqual(shese.parse_color("#abc"), ([0xaa, 0xbb, 0xcc], 1.0))

    def test_four_digit_alpha_is_nibble_over_15(self):
        rgb, alpha = shese.parse_color("#0006")
        self.assertEqual(rgb, [0, 0, 0])
        self.assertAlmostEqual(alpha, 6 / 15, places=12)

    def test_eight_digit_alpha_is_byte_over_255(self):
        rgb, alpha = shese.parse_color("#11223344")
        self.assertEqual(rgb, [0x11, 0x22, 0x33])
        self.assertAlmostEqual(alpha, 0x44 / 255, places=12)

    def test_case_and_whitespace_tolerated(self):
        self.assertEqual(shese.parse_color("  #AABBCC ")[0], [0xaa, 0xbb, 0xcc])

    def test_rejects_non_hex_and_bad_length(self):
        for bad in ("rgb(1,2,3)", "red", "#12345", "#gggggg", "123456"):
            with self.assertRaises(shese.InputError):
                shese.parse_color(bad)

    def test_allow_alpha_false_rejects_translucent(self):
        with self.assertRaises(shese.InputError):
            shese.parse_color("#00000080", allow_alpha=False)


class TestApcaOfficialVectors(unittest.TestCase):
    """官方测试向量取自 apca-w3/test/index.js，容差 1e-9。"""

    VECTORS = [
        ("#888", "#FFF", 63.056469930209424),
        ("#FFF", "#888", -68.54146436644962),
        ("#000", "#aaa", 58.146262578561334),
        ("#aaa", "#000", -56.24113336839742),
        ("#123", "#def", 91.66830811481631),
        ("#def", "#123", -93.06770049484275),
        ("#123", "#444", 8.32326136957393),
        ("#444", "#123", -7.526878460278154),
        ("#0006", "#fff", 54.62184067441377),
    ]

    def test_vectors_match(self):
        for text, bg, want in self.VECTORS:
            with self.subTest(text=text, bg=bg):
                trgb, ta = shese.parse_color(text)
                brgb, _ba = shese.parse_color(bg)
                self.assertAlmostEqual(shese.apca_calc(trgb, ta, brgb), want, delta=1e-9)


class TestOkLabAnchors(unittest.TestCase):
    def test_white_is_1_0_0(self):
        L, a, b = shese.hex_to_oklab([255, 255, 255])
        self.assertAlmostEqual(L, 1.0, delta=1e-7)
        self.assertAlmostEqual(a, 0.0, delta=1e-6)
        self.assertAlmostEqual(b, 0.0, delta=1e-6)

    def test_black_is_origin(self):
        L, a, b = shese.hex_to_oklab([0, 0, 0])
        self.assertAlmostEqual(L, 0.0, delta=1e-12)
        self.assertAlmostEqual(a, 0.0, delta=1e-12)
        self.assertAlmostEqual(b, 0.0, delta=1e-12)

    def test_grays_stay_neutral(self):
        for v in (1, 51, 128, 200, 254):
            L, a, b = shese.hex_to_oklab([v, v, v])
            self.assertLess(abs(a), 1e-6)
            self.assertLess(abs(b), 1e-6)

    def test_roundtrip_is_lossless(self):
        for value in ("#000000", "#ffffff", "#ff0000", "#00ff00", "#0000ff",
                      "#7a5cff", "#0d1117", "#f5f5f5", "#c23e12"):
            with self.subTest(value=value):
                rgb, _a = shese.parse_color(value)
                back, _c = shese.oklch_to_hex(*shese.hex_to_oklch(rgb))
                self.assertEqual(back, value)

    def test_out_of_gamut_chroma_is_clipped(self):
        _hex_value, clipped = shese.oklch_to_hex(0.7, 0.9, 40.0)
        self.assertLess(clipped, 0.9)


class TestApcaFontMatrix(unittest.TestCase):
    def test_required_lc_anchors(self):
        self.assertAlmostEqual(shese.apca_required_lc(16, 400)[0], 90.0, delta=1e-9)
        self.assertAlmostEqual(shese.apca_required_lc(24, 400)[0], 60.0, delta=1e-9)
        self.assertAlmostEqual(shese.apca_required_lc(32, 400)[0], 50.0, delta=1e-9)

    def test_min_size_anchors(self):
        self.assertAlmostEqual(shese.apca_min_size(90, 400), 16.0, delta=1e-9)
        self.assertAlmostEqual(shese.apca_min_size(60, 700), 16.0, delta=1e-9)

    def test_rejects_unknown_weight(self):
        with self.assertRaises(shese.InputError):
            shese.apca_required_lc(16, 450)


class TestComposite(unittest.TestCase):
    def test_black_40pct_over_white_is_999999(self):
        trace, final, alpha = shese.composite_chain([("textDim", [0, 0, 0], 0.4)], [255, 255, 255])
        self.assertEqual(shese.fmt_hex(final), "#999999")
        self.assertEqual(trace[0]["composited"], "#999999")
        self.assertAlmostEqual(alpha, 1.0, places=12)

    def test_multi_layer_chain_accumulates(self):
        layers = [("hover", [255, 255, 255], 0.1), ("surface", [0, 0, 0], 0.2)]
        _trace, final, alpha = shese.composite_chain(layers, [255, 255, 255])
        self.assertAlmostEqual(alpha, 1.0, places=12)
        self.assertLess(shese.rel_luminance(final), shese.rel_luminance([255, 255, 255]))

    def test_translucent_without_base_is_rejected_by_cli(self):
        code, _out, err = run_cli("composite", "#00000066")
        self.assertEqual(code, 2)
        self.assertIn("不透明基准面", err)


class TestColorVisionDeficiency(unittest.TestCase):
    def test_grays_stay_neutral(self):
        for kind in ("protan", "deutan", "tritan"):
            sim = shese.simulate_cvd([128, 128, 128], kind)
            self.assertLess(max(abs(v - 128) for v in sim), 1.0, msg=kind)

    def test_deutan_collapses_red_green(self):
        normal = shese.delta_e_ok([255, 0, 0], [0, 255, 0])
        red = shese.parse_color(shese.fmt_hex(shese.simulate_cvd([255, 0, 0], "deutan")))[0]
        green = shese.parse_color(shese.fmt_hex(shese.simulate_cvd([0, 255, 0], "deutan")))[0]
        self.assertLess(shese.delta_e_ok(red, green), normal * 0.6)

    def test_tritan_keeps_blue_yellow_distinct(self):
        blue = shese.parse_color(shese.fmt_hex(shese.simulate_cvd([0, 0, 255], "tritan")))[0]
        yellow = shese.parse_color(shese.fmt_hex(shese.simulate_cvd([255, 255, 0], "tritan")))[0]
        self.assertLess(shese.delta_e_ok(blue, yellow), shese.delta_e_ok([0, 0, 255], [255, 255, 0]))


class TestCliExitCodes(unittest.TestCase):
    def test_selftest_passes(self):
        code, out, _err = run_cli("selftest")
        self.assertEqual(code, 0)
        self.assertIn("selftest", out)

    def test_help_exits_zero(self):
        code, out, _err = run_cli("--help")
        self.assertEqual(code, 0)
        self.assertIn("contrast", out)

    def test_no_command_is_input_error(self):
        code, _out, _err = run_cli()
        self.assertEqual(code, 2)

    def test_contrast_fails_under_official_table(self):
        code, out, _err = run_cli("contrast", "#777777", "#ffffff", "--size", "16", "--weight", "400")
        self.assertEqual(code, 1)
        self.assertIn("不通过", out)
        self.assertIn("Lc +71.11", out)

    def test_contrast_passes_under_official_table(self):
        code, out, _err = run_cli("contrast", "#000000", "#ffffff", "--size", "16", "--weight", "400")
        self.assertEqual(code, 0)
        self.assertIn("通过", out)
        self.assertNotIn("不通过", out)
        self.assertIn("Lc +106.04", out)

    def test_aux_role_uses_lower_floor(self):
        code, _out, _err = run_cli("contrast", "#959595", "#ffffff", "--role", "aux")
        self.assertEqual(code, 0)

    def test_translucent_background_rejected(self):
        code, _out, err = run_cli("contrast", "#ffffff", "#00000080")
        self.assertEqual(code, 2)
        self.assertIn("不透明", err)

    def test_unknown_token_name_is_input_error(self):
        code, _out, err = run_cli("matrix", "--text", "nope=#ffffff", "--surface", "bg=#000000")
        self.assertEqual(code, 2)
        self.assertIn("未知 token", err)

    def test_bad_hex_is_input_error(self):
        code, _out, err = run_cli("oklch", "#zzz")
        self.assertEqual(code, 2)
        self.assertIn("非法字符", err)

    def test_oklch_json_shape(self):
        code, out, _err = run_cli("oklch", "#7a5cff", "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(len(data[0]["oklch"]), 3)

    def test_matrix_marks_worst_surface(self):
        code, out, _err = run_cli("matrix", "--text", "textDim=#8a8a8a", "--surface", "bg=#101014",
                                  "--surface", "card=#2a2a33", "--role", "hint", "--json")
        data = json.loads(out)
        self.assertEqual(len(data["cells"]), 2)
        self.assertLessEqual(abs(data["failed"][0]["apca_lc"]),
                             max(abs(c["apca_lc"]) for c in data["cells"]))
        self.assertIn(code, (0, 1))

    def test_matrix_per_token_role_beats_global(self):
        # 同一色值、同一承载面，只换角色：body 档 60 不通过，hint 档 30 通过
        spec = {"role": "body", "surface": {"bg": "#101014"},
                "text": {"text": {"hex": "#8a8a8a", "role": "body"},
                         "textDim": {"hex": "#8a8a8a", "role": "hint"}}}
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "tokens.json"
            path.write_text(json.dumps(spec), encoding="utf-8")
            code, out, _err = run_cli("matrix", "--tokens", str(path), "--json")
        data = json.loads(out)
        req = {t["text"]: t["required_lc"] for t in data["texts"]}
        self.assertEqual(req, {"text": 60.0, "textDim": 30.0})
        verdict = {c["text"]: c["pass"] for c in data["cells"]}
        self.assertEqual(verdict, {"text": False, "textDim": True})
        self.assertEqual(code, 1)
        self.assertEqual(data["failed"][0]["required_lc"], 60.0)

    def test_matrix_per_token_size_weight_overrides_role(self):
        # 同一色值 #bfbfbf 在 #101014 上 |Lc| = 67.58：24px/400 要求 60 通过，16px/400 要求 90 不通过
        spec = {"surface": {"bg": "#101014"},
                "text": {"text": {"hex": "#bfbfbf", "size": 24, "weight": 400},
                         "textMuted": {"hex": "#bfbfbf", "size": 16, "weight": 400}}}
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "tokens.json"
            path.write_text(json.dumps(spec), encoding="utf-8")
            code, out, _err = run_cli("matrix", "--tokens", str(path), "--json")
        data = json.loads(out)
        req = {t["text"]: t["required_lc"] for t in data["texts"]}
        self.assertEqual(req, {"text": 60.0, "textMuted": 90.0})
        verdict = {c["text"]: c["pass"] for c in data["cells"]}
        self.assertEqual(verdict, {"text": True, "textMuted": False})
        self.assertEqual(code, 1)

    def test_matrix_string_value_keeps_global_default(self):
        spec = {"role": "hint", "surface": {"bg": "#101014"}, "text": {"textDim": "#8a8a8a"}}
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "tokens.json"
            path.write_text(json.dumps(spec), encoding="utf-8")
            code, out, _err = run_cli("matrix", "--tokens", str(path), "--json")
        data = json.loads(out)
        self.assertEqual(data["texts"][0]["required_lc"], 30.0)
        self.assertEqual(code, 0)
        self.assertTrue(all(c["pass"] for c in data["cells"]))

    def test_matrix_unknown_role_is_input_error(self):
        spec = {"surface": {"bg": "#101014"}, "text": {"text": {"hex": "#ffffff", "role": "nope"}}}
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "tokens.json"
            path.write_text(json.dumps(spec), encoding="utf-8")
            code, _out, err = run_cli("matrix", "--tokens", str(path))
        self.assertEqual(code, 2)
        self.assertIn("未知角色", err)

    def test_matrix_human_output_prints_per_token_requirement(self):
        code, out, _err = run_cli("matrix", "--text", "text=#8a8a8a", "--surface", "bg=#101014",
                                  "--role", "hint")
        self.assertEqual(code, 0)
        self.assertIn("各 token 的要求口径", out)
        self.assertIn("30.0", out)

    def test_cvd_collapse_is_flagged(self):
        code, out, _err = run_cli("cvd", "#ff0000", "#00a000", "--json")
        data = json.loads(out)
        self.assertEqual(code, 1)
        self.assertTrue(data["collapsed_pairs"])

    def test_cvd_distinct_colors_pass(self):
        code, _out, _err = run_cli("cvd", "#1b3a6b", "#f2c14e", "#8a5cf6")
        self.assertEqual(code, 0)

    def test_token_alias_normalizes(self):
        self.assertEqual(shese.normalize_token("text-muted"), "textMuted")
        self.assertEqual(shese.normalize_token("background"), "bg")

    def test_themevault_names_normalize(self):
        for src, want in (("bg-surface", "surface"), ("bg-elevated", "elevated"), ("ok", "success"),
                          ("ok-fill", "success"), ("warn", "warning"), ("error", "danger"),
                          ("danger-fill", "danger"), ("info-fill", "info"), ("dim", "textDim")):
            with self.subTest(src=src):
                self.assertEqual(shese.normalize_token(src), want)

    def test_unmapped_themevault_name_is_still_refused(self):
        for bad in ("bg-hover", "accent-foreground", "syntax-keyword"):
            with self.subTest(bad=bad):
                with self.assertRaises(shese.InputError):
                    shese.normalize_token(bad)


class TestPreviewInjection(unittest.TestCase):
    TEMPLATE = ':root{ --bg: #000000; --text: #ffffff; }\n<div data-mode="dark"></div>\n'

    def test_injects_only_declared_variables(self):
        with tempfile.TemporaryDirectory() as tmp:
            tpl = Path(tmp) / "tpl.html"
            out = Path(tmp) / "out.html"
            tpl.write_text(self.TEMPLATE, encoding="utf-8")
            code, _stdout, _err = run_cli("preview", "--tokens", "bg=#101014", "--tokens", "text=#e6e6e6",
                                          "--template", str(tpl), "--out", str(out), "--mode", "light")
            self.assertEqual(code, 0)
            text = out.read_text(encoding="utf-8")
            self.assertIn("--bg: #101014;", text)
            self.assertIn("--text: #e6e6e6;", text)
            self.assertIn('data-mode="light"', text)

    def test_alpha_token_keeps_alpha_hex(self):
        with tempfile.TemporaryDirectory() as tmp:
            tpl = Path(tmp) / "tpl.html"
            out = Path(tmp) / "out.html"
            tpl.write_text(self.TEMPLATE, encoding="utf-8")
            code, _stdout, _err = run_cli("preview", "--tokens", "bg=#10101466",
                                          "--template", str(tpl), "--out", str(out))
            self.assertEqual(code, 0)
            self.assertIn("--bg: #10101466;", out.read_text(encoding="utf-8"))

    def test_unknown_variable_in_template_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            tpl = Path(tmp) / "tpl.html"
            out = Path(tmp) / "out.html"
            tpl.write_text(self.TEMPLATE, encoding="utf-8")
            code, _stdout, err = run_cli("preview", "--tokens", "border=#333333",
                                         "--template", str(tpl), "--out", str(out))
            self.assertEqual(code, 2)
            self.assertIn("没有 --border", err)
            self.assertFalse(out.exists())

    def test_real_template_pins_brand_shell(self):
        text = shese.DEFAULT_TEMPLATE.read_text(encoding="utf-8")
        # 选择器不带引号，才不会与脚本对 data-mode="…" 的单次替换撞车
        self.assertIn(":root[data-mode=dark] {", text)
        self.assertIn(":root[data-mode=light] {", text)
        self.assertIn("--shell-bg: #1A1714;", text)       # ThemeVault #001 themes/erge/dark
        self.assertIn("--shell-accent: #F2570F;", text)
        self.assertIn("--shell-bg: #FAF1E9;", text)       # ThemeVault #002 themes/erge/light
        self.assertIn("--shell-accent: #FF6A2B;", text)
        for name in shese.TOKEN_NAMES:
            with self.subTest(token=name):
                self.assertEqual(text.count("--" + name + ":"), 1)

    def test_real_template_derives_states_in_oklab(self):
        text = shese.DEFAULT_TEMPLATE.read_text(encoding="utf-8")
        # 派生状态底（按钮、徽章、选中行）统一在 oklab 混色：同一比例跨色相的明度 / 彩度变化才一致
        self.assertNotIn("color-mix(in srgb", text)
        self.assertGreaterEqual(text.count("color-mix(in oklab"), 8)

    def test_shell_pins_survive_injection(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.html"
            code, _stdout, _err = run_cli("preview", "--tokens", "bg=#101014",
                                          "--tokens", "accent=#7a5cff",
                                          "--out", str(out), "--mode", "dark")
            self.assertEqual(code, 0)
            text = out.read_text(encoding="utf-8")
            self.assertEqual(text.count("--bg:"), 1)
            self.assertIn("--bg: #101014;", text)
            self.assertIn("--shell-bg: #1A1714;", text)
            self.assertIn("--shell-accent: #F2570F;", text)
            self.assertIn("--shell-accent: #FF6A2B;", text)

    def test_polarity_mismatch_warns_but_exit_stays_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.html"
            code, stdout, err = run_cli("preview", "--tokens", "bg=#FAF1E9",
                                        "--out", str(out), "--mode", "dark", "--json")
            self.assertEqual(code, 0)
            self.assertIn("极性提醒", err)
            payload = json.loads(stdout)
            self.assertEqual(payload["polarity"]["detected"], "light")
            self.assertEqual(payload["polarity"]["declared"], "dark")
            self.assertFalse(payload["polarity"]["match"])

    def test_polarity_match_is_silent(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.html"
            code, stdout, err = run_cli("preview", "--tokens", "bg=#1A1714",
                                        "--out", str(out), "--mode", "dark", "--json")
            self.assertEqual(code, 0)
            self.assertNotIn("极性提醒", err)
            self.assertTrue(json.loads(stdout)["polarity"]["match"])

    def test_missing_template_is_input_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, _stdout, err = run_cli("preview", "--tokens", "bg=#101014",
                                         "--template", str(Path(tmp) / "nope.html"),
                                         "--out", str(Path(tmp) / "out.html"))
            self.assertEqual(code, 2)
            self.assertIn("找不到模板", err)


class DeltaTests(unittest.TestCase):
    def test_delta_flags_collapsed_layers(self):
        code, out, _err = run_cli("delta", "#1c2128", "#161b22", "#0d1117", "--json")
        data = json.loads(out)
        self.assertEqual(code, 1)
        self.assertEqual(len(data["pairs"]), 2)
        self.assertTrue(all(not p["pass"] for p in data["pairs"]))

    def test_delta_passes_on_visible_steps(self):
        code, out, _err = run_cli("delta", "#0d1117", "#2b323c", "--json")
        data = json.loads(out)
        self.assertEqual(code, 0)
        self.assertTrue(data["pairs"][0]["pass"])

    def test_delta_needs_two_colors(self):
        code, _out, err = run_cli("delta", "#c9d1d9")
        self.assertEqual(code, 2)
        self.assertIn("至少给两个", err)

    def test_delta_rejects_alpha(self):
        code, _out, err = run_cli("delta", "#ffffff80", "#101014")
        self.assertEqual(code, 2)
        self.assertIn("composite", err)


class MixTests(unittest.TestCase):
    def test_mix_space_changes_midpoint(self):
        code, out, _err = run_cli("mix", "#000000", "50", "#ffffff", "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["result"], "#636363")
        code, out, _err = run_cli("mix", "#000000", "50", "#ffffff", "--space", "srgb", "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["result"], "#808080")

    def test_mix_with_transparent_returns_alpha_hex(self):
        code, out, _err = run_cli("mix", "#7a5cff", "22", "transparent", "--json")
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["result"], "#7a5cff38")
        self.assertAlmostEqual(payload["alpha"], 0.22, places=6)

    def test_mix_weight_symmetry(self):
        a = shese.parse_color("#7a5cff")
        b = shese.parse_color("#1c2128")
        m1 = shese.mix_colors(a, b, 0.3)[0]
        m2 = shese.mix_colors(b, a, 0.7)[0]
        self.assertLess(shese.delta_e_ok(m1, m2), 1e-9)

    def test_mix_rejects_two_alpha_colors(self):
        code, _out, err = run_cli("mix", "#ffffff80", "50", "#000000")
        self.assertEqual(code, 2)
        self.assertIn("composite", err)

    def test_mix_rejects_endpoint_weight(self):
        for weight in ("0", "100"):
            code, _out, err = run_cli("mix", "#000000", weight, "#ffffff")
            self.assertEqual(code, 2)
            self.assertIn("0,100", err)


if __name__ == "__main__":
    unittest.main(verbosity=2)
