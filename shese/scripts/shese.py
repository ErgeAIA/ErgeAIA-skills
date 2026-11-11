# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""shese 计算层：把配色判定里可精确计算的部分做成可复现的命令。

数据来源（逐字对齐公开标准与参考实现，非本技能自创）：
  OKLab / OKLCH        Björn Ottosson 2020，M1 / M2 取自原文
  WCAG 相对亮度比        W3C WCAG 2.x relative luminance
  APCA Lc              SAPC APCA-W3 0.1.9 W3（G-4g，2022-07-03）；常量与算法取自 apca-w3/src/apca-w3.js
  APCA 字号-字重矩阵     同上 fontLookupAPCA 的 fontMatrixAscend（Public Beta 0.1.7 G，2022-05-28）
  色觉模拟              DaltonLens libDaltonLens.c（公有领域）：protan / deutan 用 Viénot 1999，
                       tritan 用 Brettel 1997（Viénot 对 tritan 不准）；severity 1.0 取全色盲最坏情况

命令：
  oklch      HEX... | --to-hex "L C h"
  contrast   TEXT BG [--size N] [--weight W] [--role body|aux|hint]
  composite  [--on BASE] LAYER...        每个 LAYER 为 #rrggbb[aa]，自顶向下
  matrix     --text name=HEX ... [--surface name=HEX ...] [--size N] [--weight W] [--role R]
  cvd        HEX... [--min-delta 0.10]
  delta      HEX...              相邻颜色 / 层级的 ΔE-OK，按传入顺序两两相邻
  mix        A PCT B [--space oklab|srgb]
             A 占 PCT%（0<PCT<100），B 占其余；一端可写 transparent（= 该色带 alpha）
  preview    --tokens name=HEX ... [--template PATH] --out PATH [--mode dark|light]
             （注入的 bg 与 data-mode 极性不符时 stderr 提醒，不影响退出码）
  solve      TEXT BG [--size N] [--weight W] [--role R]
             保色相求最小改动：在 L 轴上二分到刚达标，端点解判失败
  story      --card CARD.json --tokens TOKENS.json
             按故事卡逐项验收：明度区间 / 彩度上限 / 色相窗 / 色相数 / 对比上限 / 色觉
  export     --tokens TOKENS.json --name 名称 [--story 一句话] --out DIR [--slug S]
             命名主题导出 JSON / CSS vars / Tailwind @theme
  selftest

alpha 一律按浏览器口径在 sRGB 空间沿叠加链合成后判定；未给不透明基准面即报错。
退出码：0 = 通过；1 = 有硬底线不通过；2 = 输入或环境错误。stdout 出数据，stderr 出诊断。
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- OKLab / OKLCH
# M1: CIE XYZ(D65) -> LMS；M2: LMS' -> Lab。逐字取自 Björn Ottosson "A perceptual color space
# for image processing" (2020) 原文矩阵；白点归一化为 D65 白 -> (1, 0, 0)。
OKLAB_M1 = (
    (0.8189330101, 0.3618667424, -0.1288597137),
    (0.0329845436, 0.9293118715, 0.0361456387),
    (0.0482003018, 0.2643662691, 0.6338517070),
)
OKLAB_M2 = (
    (0.2104542553, 0.7936177850, -0.0040720468),
    (1.9779984951, -2.4285922050, 0.4505937099),
    (0.0259040371, 0.7827717662, -0.8086757660),
)
# 线性 sRGB -> LMS（M1 与 sRGB->XYZ_D65 的合成，广泛使用的公开数值）。
# 其行和均为 1.0 —— 这正是灰度色在 OKLab 中 a = b = 0 的充要条件，selftest 对此设锚。
LIN_SRGB_TO_LMS = (
    (0.4122214708, 0.5363325363, 0.0514459929),
    (0.2119034982, 0.6806995451, 0.1073969566),
    (0.0883024619, 0.2817188376, 0.6299787005),
)

# ---------------------------------------------------------------- APCA (SAPC APCA-W3 0.1.9 W3)
APCA = {
    "mainTRC": 2.4,
    "sRco": 0.2126729, "sGco": 0.7151522, "sBco": 0.0721750,
    "normBG": 0.56, "normTXT": 0.57, "revTXT": 0.62, "revBG": 0.65,
    "blkThrs": 0.022, "blkClmp": 1.414,
    "scaleBoW": 1.14, "scaleWoB": 1.14,
    "loBoWoffset": 0.027, "loWoBoffset": 0.027,
    "deltaYmin": 0.0005, "loClip": 0.1,
}

# APCA fontMatrixAscend：行 = Lc，列 = 字重 100..900，格值 = 该 Lc 下该字重的最小可用字号(px)。
# 999 = 禁止（对比过低）；777 = 仅非文本 / 点状文本可用。取自官方 fontLookupAPCA。
APCA_FONT_MATRIX = (
    (0, 999, 999, 999, 999, 999, 999, 999, 999, 999),
    (10, 999, 999, 999, 999, 999, 999, 999, 999, 999),
    (15, 777, 777, 777, 777, 777, 777, 777, 777, 777),
    (20, 777, 777, 777, 777, 777, 777, 777, 777, 777),
    (25, 777, 777, 777, 120, 120, 108, 96, 96, 96),
    (30, 777, 777, 120, 108, 108, 96, 72, 72, 72),
    (35, 777, 120, 108, 96, 72, 60, 48, 48, 48),
    (40, 120, 108, 96, 60, 48, 42, 32, 32, 32),
    (45, 108, 96, 72, 42, 32, 28, 24, 24, 24),
    (50, 96, 72, 60, 32, 28, 24, 21, 21, 21),
    (55, 80, 60, 48, 28, 24, 21, 18, 18, 18),
    (60, 72, 48, 42, 24, 21, 18, 16, 16, 18),
    (65, 68, 46, 32, 21.75, 19, 17, 15, 16, 18),
    (70, 64, 44, 28, 19.5, 18, 16, 14.5, 16, 18),
    (75, 60, 42, 24, 18, 16, 15, 14, 16, 18),
    (80, 56, 38.25, 23, 17.25, 15.81, 14.81, 14, 16, 18),
    (85, 52, 34.5, 22, 16.5, 15.625, 14.625, 14, 16, 18),
    (90, 48, 32, 21, 16, 15.5, 14.5, 14, 16, 18),
    (95, 45, 28, 19.5, 15.5, 15, 14, 13.5, 16, 18),
    (100, 42, 26.5, 18.5, 15, 14.5, 13.5, 13, 16, 18),
    (105, 39, 25, 18, 14.5, 14, 13, 12, 16, 18),
    (110, 36, 24, 18, 14, 13, 12, 11, 16, 18),
    (115, 34.5, 22.5, 17.25, 12.5, 11.875, 11.25, 10.625, 14.5, 16.5),
    (120, 33, 21, 16.5, 11, 10.75, 10.5, 10.25, 13, 15),
    (125, 32, 20, 16, 10, 10, 10, 10, 12, 14),
)
APCA_WEIGHTS = (100, 200, 300, 400, 500, 600, 700, 800, 900)

# 色觉模拟：线性 sRGB 空间的投影矩阵（DaltonLens libDaltonLens.c，公有领域）。
CVD_VIENOT = {
    "protan": ((0.11238, 0.88762, 0.00000),
               (0.11238, 0.88762, -0.00000),
               (0.00401, -0.00401, 1.00000)),
    "deutan": ((0.29275, 0.70725, 0.00000),
               (0.29275, 0.70725, -0.00000),
               (-0.02234, 0.02234, 1.00000)),
}
CVD_BRETTEL_TRITAN = {
    "plane1": ((1.01277, 0.13548, -0.14826),
               (-0.01243, 0.86812, 0.14431),
               (0.07589, 0.80500, 0.11911)),
    "plane2": ((0.93678, 0.18979, -0.12657),
               (0.06154, 0.81526, 0.12320),
               (-0.37562, 1.12767, 0.24796)),
    "normal": (0.03901, -0.02788, -0.01113),
}

ROLE_FLOOR = {"body": 60.0, "aux": 45.0, "hint": 30.0}

TOKEN_NAMES = ("bg", "surface", "elevated", "card", "border", "text", "textMuted",
               "textDim", "accent", "brand", "success", "warning", "danger", "info")
TOKEN_ALIASES = {
    # 通用叫法
    "background": "bg", "foreground": "text",
    "text-muted": "textMuted", "text-dim": "textDim", "muted": "textMuted", "dim": "textDim",
    # ThemeVault / VS Code 主题常见命名（只做入参归一，不改变 14 个输出 token 白名单）
    "bg-base": "bg", "bg-surface": "surface", "bg-elevated": "elevated",
    "ok": "success", "ok-fill": "success",
    "warn": "warning", "warn-fill": "warning",
    "error": "danger", "danger-fill": "danger", "info-fill": "info",
}

DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "scene-preview.html"


class InputError(Exception):
    """输入或环境错误 -> 退出码 2。"""


# ---------------------------------------------------------------- 颜色解析与表示
def parse_color(value: str, allow_alpha: bool = True):
    """解析 #rgb / #rgba / #rrggbb / #rrggbbaa，返回 ([r,g,b] 0-255, alpha 0-1)。

    4 位简写的 alpha 按 nibble/15（与 colorParsley 一致），8 位按 byte/255。
    """
    s = value.strip().lower()
    if not s.startswith("#"):
        raise InputError("只接受十六进制颜色，收到：" + value)
    body = s[1:]
    if not re.fullmatch(r"[0-9a-f]+", body):
        raise InputError("十六进制颜色含非法字符：" + value)
    if len(body) == 3:
        rgb = [int(c * 2, 16) for c in body]
        alpha = 1.0
    elif len(body) == 4:
        rgb = [int(c * 2, 16) for c in body[:3]]
        alpha = int(body[3], 16) / 15.0
    elif len(body) == 6:
        rgb = [int(body[i:i + 2], 16) for i in (0, 2, 4)]
        alpha = 1.0
    elif len(body) == 8:
        rgb = [int(body[i:i + 2], 16) for i in (0, 2, 4)]
        alpha = int(body[6:8], 16) / 255.0
    else:
        raise InputError("十六进制长度须为 3 / 4 / 6 / 8 位，收到：" + value)
    if not allow_alpha and len(body) in (4, 8):
        raise InputError("此处需要不透明实色，收到带 alpha 的值：" + value)
    return rgb, alpha


def fmt_hex(rgb) -> str:
    return "#" + "".join("%02x" % max(0, min(255, int(round(c)))) for c in rgb)


def alpha_blend(fg_rgb, fg_alpha, bg_rgb, do_round: bool = True):
    """浏览器口径：在 sRGB 空间合成，逐通道取整（与 alphaBlend(round = true) 一致）。"""
    out = []
    for i in range(3):
        v = bg_rgb[i] * (1.0 - fg_alpha) + fg_rgb[i] * fg_alpha
        out.append(min(255.0, round(v)) if do_round else v)
    return out


def composite_chain(layers, base=None):
    """layers 自顶向下；base 为最底不透明面。返回 (每步记录, 最终 rgb, 最终 alpha)。"""
    if base is not None:
        result, alpha = list(base), 1.0
    else:
        result, alpha = None, 0.0
    trace = []
    for name, rgb, a in reversed(layers):
        if result is None:
            result, alpha = list(rgb), a
        else:
            if a >= 1.0:
                new_rgb, new_alpha = list(rgb), 1.0
            else:
                new_rgb = alpha_blend(rgb, a, result)
                new_alpha = a + alpha * (1.0 - a)
            trace.append({"layer": name, "raw": fmt_hex(rgb), "alpha": round(a, 4),
                          "over": fmt_hex(result), "composited": fmt_hex(new_rgb)})
            result, alpha = new_rgb, new_alpha
    if result is None:
        raise InputError("没有可合成的层")
    return list(reversed(trace)), result, alpha


# ---------------------------------------------------------------- 线性代数与色彩空间
def _mat3_vec(m, v):
    return [sum(m[i][j] * v[j] for j in range(3)) for i in range(3)]


def _mat3_inv(m):
    (a, b, c), (d, e, f), (g, h, i) = m
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    if abs(det) < 1e-15:
        raise InputError("矩阵不可逆")
    return (
        ((e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det),
        ((f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det),
        ((d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det),
    )


LMS_TO_LIN_SRGB = _mat3_inv(LIN_SRGB_TO_LMS)


def _srgb_to_linear(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c: float) -> float:
    if c <= 0.0031308:
        v = 12.92 * c
    else:
        v = 1.055 * (c ** (1 / 2.4)) - 0.055
    return max(0.0, min(255.0, v * 255.0))


def _cbrt(x: float) -> float:
    return math.copysign(abs(x) ** (1.0 / 3.0), x)


def hex_to_oklab(rgb):
    lin = [_srgb_to_linear(c) for c in rgb[:3]]
    lms = _mat3_vec(LIN_SRGB_TO_LMS, lin)
    lms_ = [_cbrt(v) for v in lms]
    return _mat3_vec(OKLAB_M2, lms_)


def oklab_to_linear(oklab):
    lms_ = _mat3_vec(_mat3_inv(OKLAB_M2), list(oklab))
    lms = [v ** 3 for v in lms_]
    return _mat3_vec(LMS_TO_LIN_SRGB, lms)


def hex_to_oklch(rgb):
    L, a, b = hex_to_oklab(rgb)
    C = math.hypot(a, b)
    h = 0.0 if C < 1e-9 else math.degrees(math.atan2(b, a)) % 360.0
    return L, C, h


def oklch_to_hex(L, C, h):
    """超出 sRGB 时按色度逐步收缩（每步 ×0.98）直至入色域，并回报收缩后的色度。"""
    clipped = C
    for _ in range(200):
        rad = math.radians(h)
        lin = oklab_to_linear((L, clipped * math.cos(rad), clipped * math.sin(rad)))
        if all(-1e-9 <= v <= 1.0 + 1e-9 for v in lin):
            return fmt_hex([_linear_to_srgb(v) for v in lin]), clipped
        clipped *= 0.98
    raise InputError("OKLCH 无法收缩进 sRGB 色域，请检查 L / C")


def delta_e_ok(rgb_a, rgb_b) -> float:
    a, b = hex_to_oklab(rgb_a), hex_to_oklab(rgb_b)
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def mix_colors(a, b, weight, space="oklab"):
    """a 占 weight（0..1），b 占其余。transparent 一端退化为「该色带 alpha」；
    两端都带 alpha（非 0）时拒绝，必须先 composite 成实色。oklab 为默认空间。"""
    ra, aa = a
    rb, ab = b
    if aa <= 0.0 and ab <= 0.0:
        raise InputError("两个 transparent 没有可判定的实色")
    if aa <= 0.0:
        return [int(round(v)) for v in rb], ab * (1.0 - weight)
    if ab <= 0.0:
        return [int(round(v)) for v in ra], aa * weight
    if aa < 1.0 or ab < 1.0:
        raise InputError("两端都带 alpha 的混色请先 composite 成实色，或把其中一端写成 transparent")
    if space == "srgb":
        rgb = [ra[i] * weight + rb[i] * (1.0 - weight) for i in range(3)]
    else:
        la, lb = hex_to_oklab(ra), hex_to_oklab(rb)
        lab = [la[i] * weight + lb[i] * (1.0 - weight) for i in range(3)]
        rgb = [_linear_to_srgb(max(0.0, min(1.0, v))) for v in oklab_to_linear(lab)]
    return [int(round(v)) for v in rgb], 1.0


def mix_operand(value):
    if value.strip().lower() == "transparent":
        return ([0, 0, 0], 0.0)
    return parse_color(value)


def polarity_of(rgb) -> str:
    """按 OKLab 明度 0.5（感知中灰）把底色分成 dark / light，用于预览页极性自检。"""
    return "light" if hex_to_oklab(rgb)[0] >= 0.5 else "dark"


# ---------------------------------------------------------------- WCAG 相对亮度比
def rel_luminance(rgb) -> float:
    out = 0.0
    for coef, chan in zip((0.2126, 0.7152, 0.0722), rgb[:3]):
        c = chan / 255.0
        out += coef * (c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return out


def contrast_ratio(rgb_a, rgb_b) -> float:
    la, lb = rel_luminance(rgb_a), rel_luminance(rgb_b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# ---------------------------------------------------------------- APCA
def _apca_srgb_to_y(rgb) -> float:
    y = 0.0
    for coef, chan in zip((APCA["sRco"], APCA["sGco"], APCA["sBco"]), rgb[:3]):
        y += coef * ((chan / 255.0) ** APCA["mainTRC"])
    return y


def apca_contrast_from_y(txt_y: float, bg_y: float) -> float:
    txt_y = txt_y if txt_y > APCA["blkThrs"] else txt_y + (APCA["blkThrs"] - txt_y) ** APCA["blkClmp"]
    bg_y = bg_y if bg_y > APCA["blkThrs"] else bg_y + (APCA["blkThrs"] - bg_y) ** APCA["blkClmp"]
    if abs(bg_y - txt_y) < APCA["deltaYmin"]:
        return 0.0
    if bg_y > txt_y:  # 正极性：深字浅底
        sapc = (bg_y ** APCA["normBG"] - txt_y ** APCA["normTXT"]) * APCA["scaleBoW"]
        out = 0.0 if sapc < APCA["loClip"] else sapc - APCA["loBoWoffset"]
    else:  # 负极性：浅字深底
        sapc = (bg_y ** APCA["revBG"] - txt_y ** APCA["revTXT"]) * APCA["scaleWoB"]
        out = 0.0 if sapc > -APCA["loClip"] else sapc + APCA["loWoBoffset"]
    return out * 100.0


def apca_calc(text_rgb, text_alpha, bg_rgb) -> float:
    """与 calcAPCA 同口径：文字带 alpha 时先在背景上合成（逐通道取整）再算 Lc。"""
    if text_alpha < 1.0:
        text_rgb = alpha_blend(text_rgb, text_alpha, bg_rgb)
    return apca_contrast_from_y(_apca_srgb_to_y(text_rgb), _apca_srgb_to_y(bg_rgb))


def apca_weight_column(weight: int):
    if weight not in APCA_WEIGHTS:
        raise InputError("字重须为 100..900 的百位值，收到：" + str(weight))
    return APCA_WEIGHTS.index(weight) + 1


def apca_min_size(lc: float, weight: int):
    """官方矩阵反查：该 Lc 在该字重下的最小可用字号(px)；禁止 / 仅点状文本时返回 None。"""
    col = apca_weight_column(weight)
    lc_abs = abs(lc)
    rows = [(r[0], r[col]) for r in APCA_FONT_MATRIX]
    valid = [(l, s) for l, s in rows if s not in (777, 999)]
    if not valid:
        return None
    if lc_abs <= valid[0][0]:
        return valid[0][1]
    if lc_abs >= valid[-1][0]:
        return valid[-1][1]
    for (l1, s1), (l2, s2) in zip(valid, valid[1:]):
        if l1 <= lc_abs <= l2:
            t = (lc_abs - l1) / (l2 - l1)
            return round(s1 + (s2 - s1) * t, 3)
    return None


def apca_required_lc(size: float, weight: int):
    """官方矩阵正查：该字号 + 字重下所需的最低 |Lc|。"""
    col = apca_weight_column(weight)
    valid = [(r[0], r[col]) for r in APCA_FONT_MATRIX if r[col] not in (777, 999)]
    if not valid:
        return None, "该字重无可用的官方档位"
    if size >= valid[0][1]:
        return float(valid[0][0]), "字号大于官方表最低档，取表内最低 Lc"
    if size <= valid[-1][1]:
        return float(valid[-1][0]), "字号小于官方表最高档，需要更高 Lc 或提字号/加字重"
    for (l1, s1), (l2, s2) in zip(valid, valid[1:]):
        if s2 <= size <= s1:
            t = (s1 - size) / (s1 - s2)
            return round(l1 + (l2 - l1) * t, 2), "按官方矩阵插值"
    return None, "无法插值"


# ---------------------------------------------------------------- 色觉模拟
def _cvd_linear(mat, lin):
    return [sum(mat[i][j] * lin[j] for j in range(3)) for i in range(3)]


def simulate_cvd(rgb, kind: str):
    lin = [_srgb_to_linear(c) for c in rgb[:3]]
    if kind in CVD_VIENOT:
        out = _cvd_linear(CVD_VIENOT[kind], lin)
    elif kind == "tritan":
        n = CVD_BRETTEL_TRITAN["normal"]
        dot = sum(lin[i] * n[i] for i in range(3))
        mat = CVD_BRETTEL_TRITAN["plane1"] if dot >= 0 else CVD_BRETTEL_TRITAN["plane2"]
        out = _cvd_linear(mat, lin)
    else:
        raise InputError("未知的色觉类型：" + kind)
    return [_linear_to_srgb(v) for v in out]


# ---------------------------------------------------------------- token 名
def normalize_token(name: str) -> str:
    key = name.strip()
    key = TOKEN_ALIASES.get(key, key)
    if key not in TOKEN_NAMES:
        raise InputError("未知 token 名（合法名：" + ", ".join(TOKEN_NAMES) + "），收到：" + name)
    return key


def parse_token_args(items):
    out = []
    for item in items or []:
        if "=" not in item:
            raise InputError("token 须写成 name=#rrggbb[aa]，收到：" + item)
        name, value = item.split("=", 1)
        rgb, alpha = parse_color(value)
        out.append((normalize_token(name), rgb, alpha))
    return out


# ---------------------------------------------------------------- 输出辅助
def emit(args, payload, text_lines):
    if getattr(args, "json", False):
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for line in text_lines:
            print(line)


def lc_text(lc: float) -> str:
    return ("+" if lc >= 0 else "") + "%.2f" % lc


# ---------------------------------------------------------------- 子命令
def cmd_oklch(args):
    rows, data = [], []
    if args.to_hex:
        parts = args.to_hex.replace(",", " ").split()
        if len(parts) != 3:
            raise InputError('--to-hex 需要三个数："L C h"')
        L, C, h = (float(x) for x in parts)
        if not (0.0 <= L <= 1.0):
            raise InputError("OKLCH 的 L 须在 0..1")
        hex_value, clipped = oklch_to_hex(L, C, h)
        rows.append("%s  <- oklch(%.4f %.4f %.2f)%s" % (
            hex_value, L, C, h,
            "" if abs(clipped - C) < 1e-9 else "  [超出 sRGB，色度收缩至 %.4f]" % clipped))
        data.append({"oklch": [L, C, h], "hex": hex_value, "chroma_clipped_to": clipped})
    for value in args.colors:
        rgb, alpha = parse_color(value)
        L, C, h = hex_to_oklch(rgb)
        lab = hex_to_oklab(rgb)
        rows.append("%s  L=%.4f  C=%.4f  h=%.2f  |  a=%+.4f b=%+.4f%s" % (
            fmt_hex(rgb), L, C, h, lab[1], lab[2],
            "" if alpha >= 1.0 else "  alpha=%.3f" % alpha))
        data.append({"hex": fmt_hex(rgb), "alpha": alpha, "oklch": [round(L, 6), round(C, 6), round(h, 4)],
                     "oklab": [round(v, 6) for v in lab]})
    if not rows:
        raise InputError("至少给一个 HEX，或用 --to-hex")
    emit(args, data, rows)
    return 0


def cmd_contrast(args):
    text_rgb, text_alpha = parse_color(args.text)
    bg_rgb, bg_alpha = parse_color(args.bg)
    if bg_alpha < 1.0:
        raise InputError("背景必须是不透明实色（alpha 结论只能基于合成后的实色）")
    own = text_rgb
    if text_alpha < 1.0:
        own = alpha_blend(text_rgb, text_alpha, bg_rgb)
    ratio = contrast_ratio(own, bg_rgb)
    lc = apca_calc(text_rgb, text_alpha, bg_rgb)
    required, how, tier = None, "", ""
    if args.size and args.weight:
        required, how = apca_required_lc(args.size, args.weight)
        tier = "目标推导（官方字号-字重矩阵）"
    else:
        required = ROLE_FLOOR[args.role]
        how = "参考锚点（角色默认下限）"
        tier = "参考锚点"
    ok = required is not None and abs(lc) >= required
    payload = {
        "text": fmt_hex(text_rgb), "alpha": text_alpha,
        "composited_text": fmt_hex(own), "bg": fmt_hex(bg_rgb),
        "wcag_ratio": round(ratio, 3), "apca_lc": round(lc, 2),
        "role": args.role, "size": args.size, "weight": args.weight,
        "required_lc": required, "tier": tier, "basis": how, "verdict": "PASS" if ok else "FAIL",
        "min_size_at_this_lc": apca_min_size(lc, args.weight) if args.weight else None,
    }
    lines = [
        "文字 %s%s  承载面 %s" % (fmt_hex(text_rgb),
                              "" if text_alpha >= 1.0 else " (alpha %.3f -> 合成 %s)" % (text_alpha, fmt_hex(own)),
                              fmt_hex(bg_rgb)),
        "WCAG 相对亮度比 %.2f:1（记账口径，仅供跨主题复算）" % ratio,
        "APCA Lc %s（判定口径）" % lc_text(lc),
        "角色 %s  要求 |Lc| >= %s  [%s]" % (args.role, required, tier),
        "依据：%s" % how,
        "结论：%s" % ("通过" if ok else "不通过 —— 需补对比或提字号/加字重/改承载面"),
    ]
    emit(args, payload, lines)
    return 0 if ok else 1


def cmd_composite(args):
    layers_raw = [a.split("=", 1)[1] if "=" in a else a for a in (args.layers or [])]
    if not layers_raw:
        raise InputError("至少给一个层")
    layers = []
    for i, value in enumerate(layers_raw):
        name = (args.layers[i].split("=", 1)[0] if "=" in args.layers[i] else "layer%d" % (i + 1))
        rgb, alpha = parse_color(value)
        layers.append((name, rgb, alpha))
    base = None
    if args.on:
        base, base_alpha = parse_color(args.on)
        if base_alpha < 1.0:
            raise InputError("--on 基准面必须不透明")
    trace, final, final_alpha = composite_chain(layers, base)
    if final_alpha < 1.0 - 1e-9:
        raise InputError("合成后仍为半透明（alpha %.3f）：需要不透明基准面才能给出对比结论" % final_alpha)
    payload = {"base": fmt_hex(base) if base else None, "steps": trace,
               "final": fmt_hex(final), "alpha": round(final_alpha, 4)}
    lines = ["自顶向下合成（sRGB 空间，逐通道取整）"]
    if base:
        lines.append("  基准面 %s" % fmt_hex(base))
    for step in trace:
        lines.append("  %-10s %s @ %.3f  落在 %s 上  ->  %s" % (
            step["layer"], step["raw"], step["alpha"], step["over"], step["composited"]))
    lines.append("最终实色 %s（判定只能基于它）" % fmt_hex(final))
    emit(args, payload, lines)
    return 0


def _text_entry(name, value, g_role, g_size, g_weight):
    """text 条目的值可以是 HEX 字符串，也可以是 {hex, role, size, weight} 对象。"""
    if isinstance(value, dict):
        hexv = value.get("hex")
        if not hexv:
            raise InputError("text 条目 %s 缺少 hex" % name)
        role = value.get("role", g_role)
        size = value.get("size", g_size)
        weight = value.get("weight", g_weight)
    else:
        hexv, role, size, weight = value, g_role, g_size, g_weight
    if role not in ROLE_FLOOR:
        raise InputError("未知角色 %s（可选：%s）" % (role, "、".join(sorted(ROLE_FLOOR))))
    rgb, alpha = parse_color(hexv)
    return {"name": normalize_token(name), "rgb": rgb, "alpha": alpha,
            "role": role, "size": size, "weight": weight}


def _required_for(role, size, weight):
    """逐 token 推要求：给了字号 + 字重走官方矩阵，否则回落到角色锚点。"""
    if size and weight:
        required, how = apca_required_lc(size, weight)
        return required, "目标推导（官方字号-字重矩阵 %gpx/%d）" % (size, weight), how
    return ROLE_FLOOR[role], "参考锚点（角色 %s 默认下限）" % role, "角色档"


def _req_text(required):
    return "%.1f" % required if required is not None else "-"


def cmd_matrix(args):
    texts, surfaces, size, weight, role = [], [], args.size, args.weight, args.role
    if args.tokens:
        path = Path(args.tokens)
        if not path.is_file():
            raise InputError("找不到 tokens 文件：" + str(path))
        spec = json.loads(path.read_text(encoding="utf-8"))
        role = spec.get("role", role)
        size = spec.get("size", size)
        weight = spec.get("weight", weight)
        for name, value in (spec.get("text") or {}).items():
            texts.append(_text_entry(name, value, role, size, weight))
        for name, value in (spec.get("surface") or {}).items():
            if isinstance(value, dict):
                value = value.get("hex")
                if not value:
                    raise InputError("surface 条目 %s 缺少 hex" % name)
            surfaces.append((normalize_token(name),) + parse_color(value))
    for name, rgb, alpha in parse_token_args(args.text):
        texts.append({"name": name, "rgb": rgb, "alpha": alpha, "role": role,
                      "size": size, "weight": weight})
    surfaces += parse_token_args(args.surface)
    if not texts:
        raise InputError("至少给一个 --text name=HEX 或在 --tokens 里给 text")
    if not surfaces:
        raise InputError("至少给一个 --surface name=HEX 或在 --tokens 里给 surface")
    for name, rgb, alpha in surfaces:
        if alpha < 1.0:
            raise InputError("承载面 %s 带 alpha：请先展开为合成后的实色" % name)
    # 同名承载面出现多次时加序号，避免矩阵里出现两列同名、最差面无法指认
    seen, labelled = {}, []
    for item in surfaces:
        name = item[0]
        seen[name] = seen.get(name, 0) + 1
        labelled.append((name if seen[name] == 1 else "%s#%d" % (name, seen[name]),) + item[1:])
    surfaces = labelled

    guards = []
    bg_surface = next((s for s in surfaces if s[0] == "bg" and s[2] >= 1.0), None)
    if bg_surface is not None:
        bg_hex = fmt_hex(bg_surface[1])
        dark = polarity_of(bg_surface[1]) == "dark"
        if bg_hex == "#000000":
            guards.append({"rule": "深色模式不用纯黑作大面积底色", "token": "bg",
                           "value": bg_hex, "pass": False})
        for item in texts:
            if item["alpha"] < 1.0:
                continue
            hexv = fmt_hex(item["rgb"])
            if dark and hexv == "#ffffff":
                guards.append({"rule": "深色模式不用纯白作正文", "token": item["name"],
                               "value": hexv, "pass": False})
            elif (not dark) and hexv == "#000000":
                guards.append({"rule": "浅色模式不用纯黑作正文", "token": item["name"],
                               "value": hexv, "pass": False})

    payload = {"role": role, "size": size, "weight": weight,
               "texts": [], "cells": [], "failed": [], "guards": guards}
    lines = ["文字 × 承载面矩阵（要求按每个文字 token 自己的角色 / 字号 / 字重推出）",
             "%-10s %-10s %-9s %-10s %-8s %-7s %-7s %s" % (
                 "文字token", "承载面", "WCAG", "APCA", "合成实色", "要求", "最差", "判定")]
    notes = []
    for item in texts:
        tname, trgb, talpha = item["name"], item["rgb"], item["alpha"]
        required, tier, how = _required_for(item["role"], item["size"], item["weight"])
        payload["texts"].append({"text": tname, "role": item["role"], "size": item["size"],
                                 "weight": item["weight"], "required_lc": required,
                                 "tier": tier, "basis": how})
        worst = None
        for sname, srgb, _salpha in surfaces:
            own = alpha_blend(trgb, talpha, srgb) if talpha < 1.0 else trgb
            ratio = contrast_ratio(own, srgb)
            lc = apca_calc(trgb, talpha, srgb)
            ok = required is not None and abs(lc) >= required
            cell = {"text": tname, "surface": sname, "wcag_ratio": round(ratio, 3),
                    "apca_lc": round(lc, 2), "composited": fmt_hex(own), "pass": ok,
                    "required_lc": required, "tier": tier, "role": item["role"]}
            if worst is None or abs(lc) < abs(worst["apca_lc"]):
                worst = cell
            payload["cells"].append(cell)
        payload["failed"].append({"text": tname, "worst_surface": worst["surface"],
                                  "apca_lc": worst["apca_lc"], "pass": worst["pass"],
                                  "required_lc": required})
        for cell in payload["cells"]:
            if cell["text"] != tname:
                continue
            lines.append("%-10s %-10s %-9s %-10s %-8s %-7s %-7s %s" % (
                cell["text"], cell["surface"], "%.2f:1" % cell["wcag_ratio"], lc_text(cell["apca_lc"]),
                cell["composited"] + (" @%s" % cell["surface"] if talpha < 1.0 else ""),
                _req_text(required), "<最差" if cell is worst else "",
                "通过" if cell["pass"] else "不通过"))
        notes.append("  · %s：角色 %s%s → 要求 |Lc| >= %s（%s）" % (
            tname, item["role"],
            "，%gpx/%d" % (item["size"], item["weight"]) if (item["size"] and item["weight"]) else "",
            _req_text(required), tier))
    lines.append("各 token 的要求口径：")
    lines += notes
    failed = [f for f in payload["failed"] if not f["pass"]]
    lines.append("结论：%s" % ("全部通过" if not failed else
                            "有 %d / %d 个文字 token 在其最差面上不达标：%s" % (
                                len(failed), len(payload["failed"]),
                                ", ".join("%s@%s(Lc %s，要求 %s)" % (
                                    f["text"], f["worst_surface"], lc_text(f["apca_lc"]),
                                    _req_text(f["required_lc"])) for f in failed))))
    if guards:
        lines.append("硬底线守卫（命中即失败，与数值是否达标无关）：")
        for guard in guards:
            lines.append("  · %s：%s %s" % (guard["rule"], guard["token"], guard["value"]))
    emit(args, payload, lines)
    return 1 if (failed or guards) else 0


def cmd_cvd(args):
    colors = []
    for value in args.colors:
        rgb, _alpha = parse_color(value)
        colors.append((fmt_hex(rgb), rgb))
    if len(colors) < 1:
        raise InputError("至少给一个 HEX")
    sims = {}
    lines = ["色觉模拟（severity 1.0 全色盲最坏情况；ΔE-OK 阈值 %.3f）" % args.min_delta]
    for name, rgb in colors:
        row = {}
        for kind in ("protan", "deutan", "tritan"):
            sim = simulate_cvd(rgb, kind)
            row[kind] = fmt_hex(sim)
        sims[name] = row
        lines.append("  %s -> protan %s  deutan %s  tritan %s" % (name, row["protan"], row["deutan"], row["tritan"]))
    pairs = []
    for i in range(len(colors)):
        for j in range(i + 1, len(colors)):
            a, b = colors[i], colors[j]
            entry = {"pair": [a[0], b[0]], "normal": round(delta_e_ok(a[1], b[1]), 4), "simulated": {}}
            for kind in ("protan", "deutan", "tritan"):
                sa, _ = parse_color(sims[a[0]][kind])
                sb, _ = parse_color(sims[b[0]][kind])
                de = delta_e_ok(sa, sb)
                entry["simulated"][kind] = round(de, 4)
            collapsed = [k for k, v in entry["simulated"].items() if v < args.min_delta]
            entry["collapsed_in"] = collapsed
            failed_in = ([] if entry["normal"] >= args.min_delta else ["normal"]) + collapsed
            entry["fail"] = bool(failed_in)
            entry["fail_in"] = failed_in
            pairs.append(entry)
    for entry in pairs:
        lines.append("  %s vs %s  ΔE-OK 常态 %.3f | protan %.3f deutan %.3f tritan %.3f%s" % (
            entry["pair"][0], entry["pair"][1], entry["normal"],
            entry["simulated"]["protan"], entry["simulated"]["deutan"], entry["simulated"]["tritan"],
            "  <- 塌陷：" + ",".join(entry["fail_in"]) if entry["fail"] else ""))
    bad = [p for p in pairs if p["fail"]]
    lines.append("结论：%s" % ("语义色在常态与三类模拟下均两两可辨" if not bad else
                            "%d 对配色在常态或模拟下塌陷，需补明度差或形态 / 文字冗余编码" % len(bad)))
    payload = {"min_delta": args.min_delta, "colors": sims, "pairs": pairs,
               "collapsed_pairs": [p["pair"] for p in bad]}
    emit(args, payload, lines)
    return 1 if bad else 0


def cmd_delta(args):
    colors = []
    for value in args.colors:
        rgb, alpha = parse_color(value)
        if alpha < 1.0:
            raise InputError("带 alpha 的颜色请先 composite 成实色再比：" + value)
        colors.append((fmt_hex(rgb), rgb))
    if len(colors) < 2:
        raise InputError("至少给两个 HEX")
    lines = ["相邻层级 ΔE-OK（阈值 %.3f；下表相邻即传入顺序）" % args.min_delta]
    payload = {"min_delta": args.min_delta, "pairs": []}
    bad = 0
    for (na, ra), (nb, rb) in zip(colors, colors[1:]):
        de = delta_e_ok(ra, rb)
        ok = de >= args.min_delta
        if not ok:
            bad += 1
        payload["pairs"].append({"a": na, "b": nb, "delta": round(de, 4), "pass": ok})
        lines.append("  %s -> %s  ΔE-OK %.4f  %s" % (na, nb, de, "可辨" if ok else "塌陷"))
    lines.append("结论：%s" % ("相邻层级均可辨" if not bad else
                            "%d 对相邻层级低于阈值，需拉开明度差或改用形态 / 文字冗余" % bad))
    emit(args, payload, lines)
    return 1 if bad else 0

def cmd_mix(args):
    weight = args.weight / 100.0
    if not 0.0 < weight < 1.0:
        raise InputError("权重须在 (0,100) 开区间内，如 14 表示 A 占 14%")
    rgb, alpha = mix_colors(mix_operand(args.first), mix_operand(args.second), weight, args.space)
    value = fmt_hex(rgb) + ("%02x" % int(round(alpha * 255)) if alpha < 1.0 else "")
    payload = {"space": args.space, "weight": args.weight, "a": args.first, "b": args.second,
               "result": value, "rgb": rgb, "alpha": round(alpha, 4)}
    emit(args, payload, ["%s @ %s%% + %s  (%s) -> %s" % (args.first, args.weight, args.second,
                                                          args.space, value)])
    return 0


# ---------------------------------------------------------------- 命名主题：solve / story / export
def _tokens_from_spec(spec):
    """把 matrix 形状的 spec 摊平成 token -> hex；text 条目可为字符串或 {hex, ...}。"""
    out = {}
    for section in ("surface", "text"):
        for name, value in (spec.get(section) or {}).items():
            hexv = value.get("hex") if isinstance(value, dict) else value
            if not hexv:
                raise InputError("%s 条目 %s 缺少 hex" % (section, name))
            rgb, _alpha = parse_color(hexv)
            out[normalize_token(name)] = fmt_hex(rgb) if _alpha >= 1.0 else \
                fmt_hex(rgb) + "%02x" % int(round(_alpha * 255))
    return out


def _hex_at(L, C, h):
    """取 OKLCH 的 hex；极端明度（纯黑/纯白附近）任何彩度都出域时退为中性色。"""
    try:
        return oklch_to_hex(L, C, h)
    except InputError:
        pass
    try:
        return oklch_to_hex(L, 0.0, h)
    except InputError:
        return ("#ffffff" if L >= 0.5 else "#000000"), 0.0


def cmd_solve(args):
    trgb, ta = parse_color(args.text)
    brgb, ba = parse_color(args.bg)
    if ba < 1.0:
        raise InputError("背景必须是不透明实色")
    if ta < 1.0:
        trgb = alpha_blend(trgb, ta, brgb)
    L, C, h = hex_to_oklch(trgb)
    bg_l = hex_to_oklch(brgb)[0]
    if args.size and args.weight:
        required, how = apca_required_lc(args.size, args.weight)
        tier = "目标推导（官方字号-字重矩阵）"
    else:
        required, how = ROLE_FLOOR[args.role], "参考锚点（角色默认下限）"
        tier = "参考锚点"
    if required is None:
        raise InputError("该字号 / 字重没有官方档位，无法求解")
    now = apca_calc(trgb, 1.0, brgb)
    rows = ["求解：文字 %s 承载面 %s" % (fmt_hex(trgb), fmt_hex(brgb)),
            "当前 APCA Lc %s  要求 |Lc| >= %.2f（%s）" % (lc_text(now), required, tier)]

    if abs(now) >= required:
        payload = {"text": fmt_hex(trgb), "bg": fmt_hex(brgb), "required_lc": required,
                   "current_lc": round(now, 2), "verdict": "PASS", "tier": tier}
        rows.append("结论：已达标，余量 %.2f Lc；无需改色" % (abs(now) - required))
        emit(args, payload, rows)
        return 0

    brighten = (L > bg_l) if abs(L - bg_l) > 1e-9 else (bg_l < 0.5)
    end_l = 1.0 if brighten else 0.0
    end_hex, end_clip = _hex_at(end_l, C, h)
    end_lc = apca_calc(parse_color(end_hex)[0], 1.0, brgb)
    if abs(end_lc) < required:
        payload = {"text": fmt_hex(trgb), "bg": fmt_hex(brgb), "required_lc": required,
                   "current_lc": round(now, 2), "max_reachable_lc": round(end_lc, 2),
                   "verdict": "UNSOLVABLE", "tier": tier}
        rows += ["该方向上可达上限 %s（端点 %s），仍低于要求 %.2f" % (
            lc_text(end_lc), end_hex, required),
            "结论：该承载面上无解 —— 问题在字号、字重或承载面，不在色彩；"
            "先提字号 / 加字重，或换更深的承载面"]
        emit(args, payload, rows)
        return 1

    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2.0
        mid_hex, _clip = _hex_at(L + (end_l - L) * mid, C, h)
        if abs(apca_calc(parse_color(mid_hex)[0], 1.0, brgb)) >= required:
            hi = mid
        else:
            lo = mid
    new_l = L + (end_l - L) * hi
    new_hex, clip = _hex_at(new_l, C, h)
    new_rgb, _a = parse_color(new_hex)
    new_lc = apca_calc(new_rgb, 1.0, brgb)
    new_oklch = hex_to_oklch(new_rgb)
    endpoint = new_hex in ("#ffffff", "#000000")
    verdict = "ENDPOINT_ONLY" if endpoint else "SOLVED"
    payload = {"text": fmt_hex(trgb), "bg": fmt_hex(brgb), "required_lc": required,
               "current_lc": round(now, 2), "new_text": new_hex,
               "new_lc": round(new_lc, 2), "delta_l": round(new_l - L, 4),
               "new_oklch": [round(v, 4) for v in new_oklch],
               "hue_drift": round((new_oklch[2] - h + 180) % 360 - 180, 3),
               "delta_e": round(delta_e_ok(trgb, new_rgb), 4),
               "chroma_clipped_to": round(clip, 4), "endpoint": endpoint,
               "verdict": verdict, "tier": tier}
    rows += ["新值 %s  L %+.4f  |Lc| %s（要求 %.2f）  ΔE-OK %.4f" % (
        new_hex, new_l - L, lc_text(new_lc), required, delta_e_ok(trgb, new_rgb)),
        "色相 h %.2f → %.2f（漂移 %.2f°，8 位量化与色域收缩所致）；彩度 %s" % (
            h, new_oklch[2], (new_oklch[2] - h + 180) % 360 - 180,
            "未变" if abs(clip - C) < 1e-9 else "由 %.4f 收缩到 %.4f（超 sRGB）" % (C, clip))]
    if endpoint:
        rows.append("结论：只有端点色可解（%s），违反深浅模式基础色硬底线；"
                    "应改字号 / 字重或承载面，不交付该值" % new_hex)
        emit(args, payload, rows)
        return 1
    rows.append("结论：最小改动可达标；若仍嫌改动大，优先提字号或字重")
    emit(args, payload, rows)
    return 0


def _hue_in(h, windows):
    for pair in windows:
        lo, hi = pair[0], pair[1]
        if lo <= hi:
            if lo <= h <= hi:
                return True
        elif h >= lo or h <= hi:
            return True
    return False


def _hue_clusters(hues, step=30.0):
    """把色相按 30° 分箱，数环形上连续的分箱数（基本色相数）。"""
    total = int(round(360.0 / step))
    bins = sorted({int(h // step) % total for h in hues})
    if not bins:
        return 0
    groups = 1
    for left, right in zip(bins, bins[1:]):
        if right - left > 1:
            groups += 1
    if len(bins) > 1 and bins[0] == 0 and bins[-1] == total - 1:
        groups -= 1
    return groups


def cmd_story(args):
    for path in (args.card, args.tokens):
        if not Path(path).is_file():
            raise InputError("找不到文件：" + str(path))
    card = json.loads(Path(args.card).read_text(encoding="utf-8"))
    spec = json.loads(Path(args.tokens).read_text(encoding="utf-8"))
    tokens = _tokens_from_spec(spec)
    targets = card.get("targets") or {}
    checks = []

    def add(key, target, measured, passed, note=""):
        checks.append({"check": key, "target": target, "measured": measured,
                       "pass": bool(passed), "note": note})

    if "bg_L" in targets and "bg" in tokens:
        lo, hi = targets["bg_L"]
        bg_l = hex_to_oklch(parse_color(tokens["bg"])[0])[0]
        add("底色明度区间", [lo, hi], round(bg_l, 4), lo <= bg_l <= hi,
            "故事卡声明的底色明度骨架")
    if "text_contrast_max" in targets and "bg" in tokens and "text" in tokens:
        ratio = contrast_ratio(parse_color(tokens["text"])[0], parse_color(tokens["bg"])[0])
        add("正文档对比上限", targets["text_contrast_max"], round(ratio, 2),
            ratio <= targets["text_contrast_max"], "经验软上限，非合规线")
    scene = card.get("scene") or {}
    if scene.get("size") and scene.get("weight") and "bg" in tokens and "text" in tokens:
        required, how = apca_required_lc(scene["size"], scene["weight"])
        lc = apca_calc(parse_color(tokens["text"])[0], 1.0, parse_color(tokens["bg"])[0])
        add("正文档 APCA", required, round(abs(lc), 2),
            required is not None and abs(lc) >= required, how)
    for role, cap in (targets.get("chroma_cap") or {}).items():
        if role in tokens:
            chroma = hex_to_oklch(parse_color(tokens[role])[0])[1]
            add("彩度上限 · " + role, cap, round(chroma, 4), chroma <= cap,
                "面积越大可承受彩度越低")
    windows = targets.get("hue_window")
    scoped = targets.get("hue_scope") or list(tokens)
    if windows:
        floor = float(targets.get("hue_min_chroma", 0.02))
        outside = []
        for name in scoped:
            if name not in tokens:
                continue
            value = tokens[name]
            _L, C, h = hex_to_oklch(parse_color(value)[0])
            if C >= floor and not _hue_in(h, windows):
                outside.append("%s(h %.1f)" % (name, h))
        add("色相窗", windows, outside or "全部在窗内", not outside,
            "彩度低于 %.2f 的中性色不参与色相判定" % floor)
    if "max_hues" in targets:
        floor = float(targets.get("hue_min_chroma", 0.03))
        hues = [hex_to_oklch(parse_color(tokens[n])[0])[2] for n in scoped if n in tokens
                and hex_to_oklch(parse_color(tokens[n])[0])[1] >= floor]
        count = _hue_clusters(hues)
        add("基本色相数", targets["max_hues"], count, count <= targets["max_hues"],
            "30° 分箱后环形连续段数；只数 hue_scope 内的 token")
    sem = [name for name in ("success", "warning", "danger", "info") if name in tokens]
    if "cvd_min" in targets and len(sem) >= 2:
        worst, worst_pair = 1.0, ""
        for i in range(len(sem)):
            for j in range(i + 1, len(sem)):
                a, b = sem[i], sem[j]
                for kind in ("protan", "deutan", "tritan"):
                    sa = parse_color(fmt_hex(simulate_cvd(parse_color(tokens[a])[0], kind)))[0]
                    sb = parse_color(fmt_hex(simulate_cvd(parse_color(tokens[b])[0], kind)))[0]
                    de = delta_e_ok(sa, sb)
                    if de < worst:
                        worst, worst_pair = de, "%s×%s@%s" % (a, b, kind)
        add("语义色色觉最小间隔", targets["cvd_min"], round(worst, 4),
            worst >= targets["cvd_min"], "最弱对 " + worst_pair)

    failed = [c for c in checks if not c["pass"]]
    payload = {"name": card.get("name"), "story": card.get("story"),
               "scene": card.get("scene"), "checks": checks,
               "failed": len(failed), "verdict": "PASS" if not failed else "FAIL"}
    lines = ["故事卡验收：%s" % (card.get("name") or "(未命名)")]
    if card.get("story"):
        lines.append("  故事：%s" % card["story"])
    if card.get("scene"):
        lines.append("  场景：%s" % json.dumps(card["scene"], ensure_ascii=False))
    for c in checks:
        lines.append("  [%s] %-22s 目标 %s，实测 %s%s" % (
            "PASS" if c["pass"] else "FAIL", c["check"], c["target"], c["measured"],
            ("（%s）" % c["note"]) if c["note"] else ""))
    lines.append("结论：%s" % ("故事卡声明的数值目标全部满足" if not failed else
                            "%d / %d 项不满足，按差额调骨架参数或改承载面" % (
                                len(failed), len(checks))))
    lines.append("注：名称与故事本身是否贴切属人工判断，本命令只验数值目标")
    emit(args, payload, lines)
    return 1 if failed else 0


def _kebab(name):
    out = "".join(("-" + c.lower()) if c.isupper() else c for c in name)
    return out.strip("-")


def cmd_export(args):
    if not Path(args.tokens).is_file():
        raise InputError("找不到 tokens 文件：" + str(args.tokens))
    spec = json.loads(Path(args.tokens).read_text(encoding="utf-8"))
    tokens = _tokens_from_spec(spec)
    if "bg" not in tokens or "text" not in tokens:
        raise InputError("导出至少需要 bg 与 text 两个 token")
    name = args.name or "theme"
    slug = args.slug or "theme"
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    formats = [f.strip() for f in (args.formats or "json,css,tailwind").split(",") if f.strip()]
    written = []
    if "json" in formats:
        path = out_dir / (slug + ".json")
        data = {"name": name, "story": args.story, "mode": args.mode, "tokens": tokens,
                "meta": {"generator": "shese", "source": str(Path(args.tokens))}}
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        written.append(str(path))
    if "css" in formats:
        path = out_dir / (slug + ".css")
        body = [':root[data-theme="%s"] {' % name]
        body += ["  --%s: %s;" % (k, tokens[k]) for k in TOKEN_NAMES if k in tokens]
        body += ["}", ""]
        path.write_text("\n".join(body), encoding="utf-8")
        written.append(str(path))
    if "tailwind" in formats:
        path = out_dir / (slug + ".tailwind.css")
        body = ["@theme {"]
        body += ["  --color-%s: %s;" % (_kebab(k), tokens[k]) for k in TOKEN_NAMES if k in tokens]
        body += ["}", ""]
        path.write_text("\n".join(body), encoding="utf-8")
        written.append(str(path))
    payload = {"name": name, "story": args.story, "mode": args.mode,
               "tokens": tokens, "files": written}
    emit(args, payload, ["已导出：%s（%d 个 token）" % (name, len(tokens))]
         + ["  %s" % p for p in written])
    return 0


def cmd_preview(args):
    tokens = parse_token_args(args.tokens)
    if not tokens:
        raise InputError("至少给一个 --tokens name=HEX")
    tpl = Path(args.template) if args.template else DEFAULT_TEMPLATE
    if not tpl.is_file():
        raise InputError("找不到模板：" + str(tpl))
    text = tpl.read_text(encoding="utf-8")
    applied = []
    for name, rgb, alpha in tokens:
        value = fmt_hex(rgb) if alpha >= 1.0 else fmt_hex(rgb) + "%02x" % int(round(alpha * 255))
        pattern = re.compile(r"(--" + re.escape(name) + r")\s*:\s*([^;]+)(;)")
        if not pattern.search(text):
            raise InputError("模板里没有 --%s 变量，拒绝注入" % name)
        text = pattern.sub(lambda m: m.group(1) + ": " + value + m.group(3), text, count=1)
        applied.append({"token": name, "value": value})
    if args.mode:
        if args.mode not in ("dark", "light"):
            raise InputError("--mode 只接受 dark 或 light")
        if 'data-mode="' in text:
            text = re.sub(r'data-mode="[^"]*"', 'data-mode="%s"' % args.mode, text, count=1)
    declared = None
    mode_hit = re.search(r'data-mode="([^"]*)"', text)
    if mode_hit:
        declared = mode_hit.group(1)
    bg_token = next((t for t in tokens if t[0] == "bg"), None)
    polarity = None
    if bg_token is not None and bg_token[2] >= 1.0 and declared in ("dark", "light"):
        detected = polarity_of(bg_token[1])
        polarity = {"bg": fmt_hex(bg_token[1]), "detected": detected,
                    "declared": declared, "match": detected == declared}
        if detected != declared:
            print("极性提醒：注入的 bg %s 在 OKLab 明度上属于%s底，而页面 data-mode 是 %s；"
                  "外壳与场景会不同极，确认这是你要的对照。"
                  % (polarity["bg"], "浅" if detected == "light" else "深", declared),
                  file=sys.stderr)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    payload = {"template": str(tpl), "out": str(out), "mode": args.mode, "applied": applied}
    if polarity is not None:
        payload["polarity"] = polarity
    emit(args, payload, ["已注入 %d 个 token -> %s" % (len(applied), out),
                         "模板：%s" % tpl] + ["  --%-10s %s" % (a["token"], a["value"]) for a in applied])
    return 0


def cmd_selftest(args):
    checks = []

    def check(name, got, want, tol):
        ok = (want is None) or (abs(got - want) <= tol)
        checks.append({"check": name, "got": got, "want": want, "tol": tol, "pass": ok})

    # 1) 官方 APCA 测试向量（apca-w3/test/index.js）
    vectors = [
        ("#888", "#FFF", 63.056469930209424), ("#FFF", "#888", -68.54146436644962),
        ("#000", "#aaa", 58.146262578561334), ("#aaa", "#000", -56.24113336839742),
        ("#123", "#def", 91.66830811481631), ("#def", "#123", -93.06770049484275),
        ("#123", "#444", 8.32326136957393), ("#444", "#123", -7.526878460278154),
        ("#0006", "#fff", 54.62184067441377),
    ]
    for text, bg, want in vectors:
        trgb, ta = parse_color(text)
        brgb, _ba = parse_color(bg)
        check("APCA %s on %s" % (text, bg), apca_calc(trgb, ta, brgb), want, 1e-9)

    # 2) OKLab 白点与灰度轴（M2 行和归一化：白 -> (1,0,0)，灰 -> a=b=0）
    L, a, b = hex_to_oklab([255, 255, 255])
    check("OKLab 白 L", L, 1.0, 1e-7)
    check("OKLab 白 a", a, 0.0, 1e-6)
    check("OKLab 白 b", b, 0.0, 1e-6)
    L0, a0, b0 = hex_to_oklab([0, 0, 0])
    check("OKLab 黑 L", L0, 0.0, 1e-12)
    gray_ok = all(abs(hex_to_oklab([v, v, v])[1]) < 1e-6 and abs(hex_to_oklab([v, v, v])[2]) < 1e-6
                  for v in (1, 51, 128, 200, 254))
    check("OKLab 灰度轴 a=b=0", 1.0 if gray_ok else 0.0, 1.0, 0.0)

    # 3) 往返一致性
    ok_round = True
    for value in ("#000000", "#ffffff", "#ff0000", "#00ff00", "#0000ff", "#7a5cff", "#0d1117", "#f5f5f5"):
        rgb, _a = parse_color(value)
        back, _c = oklch_to_hex(*hex_to_oklch(rgb))
        if back != value:
            ok_round = False
    check("OKLCH 往返无损", 1.0 if ok_round else 0.0, 1.0, 0.0)

    # 4) WCAG 不变量
    check("WCAG 黑白 21:1", contrast_ratio([0, 0, 0], [255, 255, 255]), 21.0, 1e-9)
    check("WCAG 对称", contrast_ratio([18, 52, 86], [240, 240, 240]),
          contrast_ratio([240, 240, 240], [18, 52, 86]), 1e-12)

    # 5) alpha 合成与官方向量同口径
    check("alpha #0006 合成 = #999", int(alpha_blend([0, 0, 0], 0.4, [255, 255, 255])[0]), 153, 0)

    # 6) 色觉模拟：灰度必须保持中性（投影矩阵行和 = 1）
    neutral_ok = True
    for kind in ("protan", "deutan", "tritan"):
        sim = simulate_cvd([128, 128, 128], kind)
        if max(abs(v - 128) for v in sim) > 1.0:
            neutral_ok = False
    check("色觉模拟保持灰中性", 1.0 if neutral_ok else 0.0, 1.0, 0.0)
    de_norm = delta_e_ok([255, 0, 0], [0, 255, 0])
    de_deut = delta_e_ok(parse_color(fmt_hex(simulate_cvd([255, 0, 0], "deutan")))[0],
                         parse_color(fmt_hex(simulate_cvd([0, 255, 0], "deutan")))[0])
    check("deutan 红绿分离坍缩（< 常态 60%）", 1.0 if de_deut < de_norm * 0.6 else 0.0, 1.0, 0.0)

    # 7) APCA 官方字号-字重矩阵锚点（直接读表，可手核）
    check("官方表 16px/400 要求 Lc", apca_required_lc(16, 400)[0], 90.0, 1e-9)
    check("官方表 24px/400 要求 Lc", apca_required_lc(24, 400)[0], 60.0, 1e-9)
    check("官方表 Lc 90/400 最小字号", apca_min_size(90, 400), 16.0, 1e-9)
    check("官方表 Lc 60/700 最小字号", apca_min_size(60, 700), 16.0, 1e-9)

    # 8) 混色：端点幂等、权重对称、空间确实生效（oklab 黑白中点不是 srgb 中灰）
    a, b = parse_color("#7a5cff"), parse_color("#1c2128")
    check("混色 A@100-ε 逼近 A", delta_e_ok(mix_colors(a, b, 0.999, "oklab")[0], a[0]), 0.0, 0.02)
    m1 = mix_colors(a, b, 0.3, "oklab")[0]
    m2 = mix_colors(b, a, 0.7, "oklab")[0]
    check("OKLab 混色权重对称", delta_e_ok(m1, m2), 0.0, 1e-9)
    bw = mix_colors((([0, 0, 0], 1.0)), (([255, 255, 255], 1.0)), 0.5, "oklab")[0]
    check("OKLab 黑白中点 != srgb 中灰", 1.0 if fmt_hex(bw) != "#808080" else 0.0, 1.0, 0.0)

    failed = [c for c in checks if not c["pass"]]
    lines = ["shese selftest：%d 项" % len(checks)]
    for c in checks:
        lines.append("  [%s] %-32s got=%s want=%s" % ("PASS" if c["pass"] else "FAIL", c["check"],
                                                      round(c["got"], 6), c["want"]))
    lines.append("结论：%s" % ("全部锚定通过" if not failed else "%d 项未锚定" % len(failed)))
    if getattr(args, "json", False):
        print(json.dumps({"checks": checks, "failed": len(failed)}, ensure_ascii=False, indent=2))
    else:
        for line in lines:
            print(line)
    return 1 if failed else 0


# ---------------------------------------------------------------- CLI
def build_parser():
    parser = argparse.ArgumentParser(prog="shese.py", description="shese 配色计算层（零第三方依赖）")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("oklch", help="十六进制 <-> OKLCH")
    p.add_argument("colors", nargs="*", help="#rrggbb ...")
    p.add_argument("--to-hex", metavar='"L C h"', help="把 OKLCH 转回十六进制（超色域时收色度）")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_oklch)

    p = sub.add_parser("contrast", help="文字 / 承载面对比")
    p.add_argument("text")
    p.add_argument("bg")
    p.add_argument("--size", type=float, help="字号 px（与 --weight 同时给出则用官方矩阵判定）")
    p.add_argument("--weight", type=int, help="字重 100..900")
    p.add_argument("--role", choices=sorted(ROLE_FLOOR), default="body")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_contrast)

    p = sub.add_parser("composite", help="alpha 沿叠加链在 sRGB 空间合成")
    p.add_argument("layers", nargs="*", help="自顶向下：#rrggbb[aa] 或 name=#rrggbb[aa]")
    p.add_argument("--on", help="最底不透明基准面")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_composite)

    p = sub.add_parser("matrix", help="文字 token × 承载面矩阵")
    p.add_argument("--text", action="append", default=[], metavar="name=HEX")
    p.add_argument("--surface", action="append", default=[], metavar="name=HEX")
    p.add_argument("--tokens", help="tokens.json；顶层可给 role / size / weight，text 条目可为 HEX 或 {hex, role, size, weight} 逐 token 覆盖")
    p.add_argument("--size", type=float)
    p.add_argument("--weight", type=int)
    p.add_argument("--role", choices=sorted(ROLE_FLOOR), default="body")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_matrix)

    p = sub.add_parser("cvd", help="三类色觉模拟 + ΔE-OK")
    p.add_argument("colors", nargs="+")
    p.add_argument("--min-delta", type=float, default=0.10)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_cvd)

    p = sub.add_parser("delta", help="相邻颜色 / 层级的 ΔE-OK 可辨性")
    p.add_argument("colors", nargs="+")
    p.add_argument("--min-delta", type=float, default=0.10)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_delta)

    p = sub.add_parser("mix", help="两色按百分比混色（oklab 默认 / srgb），可含 transparent")
    p.add_argument("first", help="A：HEX 或 transparent")
    p.add_argument("weight", type=float, help="A 的百分比权重，0 < PCT < 100")
    p.add_argument("second", help="B：HEX 或 transparent")
    p.add_argument("--space", choices=("oklab", "srgb"), default="oklab")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_mix)

    p = sub.add_parser("preview", help="把 token 注入自包含预览页模板")
    p.add_argument("--tokens", action="append", default=[], metavar="name=HEX")
    p.add_argument("--template")
    p.add_argument("--out", required=True)
    p.add_argument("--mode", choices=("dark", "light"))
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_preview)

    p = sub.add_parser("solve", help="保色相求最小改动，二分 L 到刚达标")
    p.add_argument("text")
    p.add_argument("bg")
    p.add_argument("--size", type=float)
    p.add_argument("--weight", type=int)
    p.add_argument("--role", choices=sorted(ROLE_FLOOR), default="body")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_solve)

    p = sub.add_parser("story", help="按故事卡验收一套 token")
    p.add_argument("--card", required=True, help="故事卡 JSON")
    p.add_argument("--tokens", required=True, help="tokens.json（matrix 同形状）")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_story)

    p = sub.add_parser("export", help="命名主题导出 JSON / CSS / Tailwind")
    p.add_argument("--tokens", required=True)
    p.add_argument("--name", help="主题名称，如 夜灯")
    p.add_argument("--story", help="一句话故事")
    p.add_argument("--mode", choices=("dark", "light"))
    p.add_argument("--slug", default="theme", help="输出文件名（不含扩展名）")
    p.add_argument("--out", required=True, help="输出目录")
    p.add_argument("--formats", default="json,css,tailwind", help="json,css,tailwind 逗号分隔")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("selftest", help="锚定自检")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_selftest)
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 2
    try:
        return args.func(args)
    except InputError as exc:
        print("输入错误：" + str(exc), file=sys.stderr)
        return 2
    except OSError as exc:
        detail = getattr(exc, "filename", None) or getattr(exc, "filename2", None) or ""
        print("输入错误：文件读写失败%s（%s）" % ("：" + str(detail) if detail else "", exc.strerror or exc),
              file=sys.stderr)
        return 2
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("输入错误：" + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
