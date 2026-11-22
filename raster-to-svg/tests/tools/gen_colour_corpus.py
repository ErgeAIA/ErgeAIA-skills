#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministic generator for the colour-mode corpus (no external assets, no fonts).

    python tests/tools/gen_colour_corpus.py <outdir>

Every image is drawn with OpenCV primitives only, so the corpus is reproducible on
any machine with numpy + opencv. Used by references/evidence.md section 8.
"""
import os
import sys

import cv2
import numpy as np


def canvas(w=320, h=240):
    return np.full((h, w, 3), 255, np.uint8)


def flat_icon_5(o):
    img = canvas()
    cv2.rectangle(img, (20, 20), (120, 120), (238, 160, 58), -1, cv2.LINE_AA)
    cv2.circle(img, (200, 70), 48, (120, 200, 95), -1, cv2.LINE_AA)
    cv2.fillPoly(img, [np.array([[40, 220], [110, 150], [180, 220]], np.int32)], (90, 120, 230), cv2.LINE_AA)
    cv2.rectangle(img, (215, 140), (300, 225), (200, 90, 190), -1, cv2.LINE_AA)
    cv2.putText(img, "OK", (24, 60), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.imwrite(os.path.join(o, "flat_icon_5.png"), img)


def flat_icon_lines(o):
    img = canvas()
    for i in range(4):
        y = 40 + i * 50
        cv2.line(img, (30, y), (290, y), (60, 60, 60), 2, cv2.LINE_AA)
        cv2.circle(img, (30, y), 6, (60, 60, 60), 2, cv2.LINE_AA)
    cv2.rectangle(img, (150, 30), (290, 200), (60, 60, 60), 2, cv2.LINE_AA)
    cv2.imwrite(os.path.join(o, "flat_icon_lines.png"), img)


def ui_panel(o):
    img = np.full((240, 320, 3), (247, 247, 249), np.uint8)
    cv2.rectangle(img, (0, 0), (319, 27), (32, 34, 40), -1)
    cv2.putText(img, "Settings", (10, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 240, 240), 1, cv2.LINE_AA)
    cv2.rectangle(img, (12, 40), (308, 120), (255, 255, 255), -1)
    cv2.rectangle(img, (12, 40), (308, 120), (222, 222, 226), 1, cv2.LINE_AA)
    cv2.putText(img, "Theme", (24, 66), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (40, 40, 44), 1, cv2.LINE_AA)
    cv2.rectangle(img, (24, 80), (150, 104), (59, 130, 246), -1)
    cv2.putText(img, "Dark", (36, 99), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.rectangle(img, (160, 80), (286, 104), (230, 230, 234), -1)
    cv2.putText(img, "Light", (178, 99), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (60, 60, 64), 1, cv2.LINE_AA)
    cv2.rectangle(img, (12, 140), (308, 200), (255, 255, 255), -1)
    cv2.rectangle(img, (12, 140), (308, 200), (222, 222, 226), 1, cv2.LINE_AA)
    cv2.putText(img, "Sync across devices", (24, 166), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (40, 40, 44), 1, cv2.LINE_AA)
    cv2.circle(img, (285, 170), 10, (59, 130, 246), -1, cv2.LINE_AA)
    cv2.imwrite(os.path.join(o, "ui_panel.png"), img)


def badge_logo(o):
    img = canvas(240, 240)
    cv2.circle(img, (120, 105), 76, (36, 41, 56), -1, cv2.LINE_AA)
    cv2.circle(img, (120, 105), 60, (255, 255, 255), -1, cv2.LINE_AA)
    cv2.putText(img, "AI", (84, 128), cv2.FONT_HERSHEY_DUPLEX, 1.4, (36, 41, 56), 3, cv2.LINE_AA)
    cv2.putText(img, "VAULT", (76, 205), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (36, 41, 56), 1, cv2.LINE_AA)
    cv2.imwrite(os.path.join(o, "badge_logo.png"), img)


def ui_dense(o):
    img = np.full((240, 320, 3), (250, 250, 252), np.uint8)
    cols = [(59, 130, 246), (16, 185, 129), (245, 158, 11), (239, 68, 68),
            (139, 92, 246), (20, 184, 166), (244, 63, 94), (132, 204, 22)]
    for i, c in enumerate(cols):
        x = 10 + (i % 4) * 78
        y = 10 + (i // 4) * 60
        cv2.rectangle(img, (x, y), (x + 68, y + 44), c, -1, cv2.LINE_AA)
        cv2.putText(img, str(i + 1), (x + 6, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(img, "12 tasks", (12, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (40, 40, 44), 1, cv2.LINE_AA)
    cv2.rectangle(img, (12, 175), (308, 230), (255, 255, 255), -1)
    cv2.rectangle(img, (12, 175), (308, 230), (222, 222, 226), 1, cv2.LINE_AA)
    cv2.rectangle(img, (22, 190), (150, 212), (59, 130, 246), -1)
    cv2.putText(img, "Run all", (34, 206), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.imwrite(os.path.join(o, "ui_dense.png"), img)


def flat_holes(o):
    img = canvas()
    cv2.rectangle(img, (30, 30), (290, 210), (52, 86, 200), -1, cv2.LINE_AA)
    cv2.circle(img, (160, 120), 70, (255, 255, 255), -1, cv2.LINE_AA)   # hole of a second colour
    cv2.circle(img, (160, 120), 70, (52, 86, 200), 6, cv2.LINE_AA)
    cv2.rectangle(img, (70, 80), (110, 160), (255, 255, 255), -1, cv2.LINE_AA)
    cv2.imwrite(os.path.join(o, "flat_holes.png"), img)


def grad_linear(o):
    img = canvas()
    for x in range(320):
        img[:, x] = (int(30 + x * 0.55), int(60 + x * 0.35), int(200 - x * 0.45))
    cv2.circle(img, (80, 80), 46, (255, 255, 255), -1, cv2.LINE_AA)
    cv2.putText(img, "grad", (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.imwrite(os.path.join(o, "grad_linear.png"), img)


def grad_radial(o):
    img = canvas()
    yy, xx = np.mgrid[0:240, 0:320]
    r = np.sqrt((xx - 160) ** 2 + (yy - 120) ** 2) / 160.0
    t = np.clip(1 - r, 0, 1) ** 1.4
    base = np.array([40, 60, 190], np.float32)
    hot = np.array([250, 210, 90], np.float32)
    for i in range(3):
        img[:, :, i] = (base[i] * (1 - t) + hot[i] * t).astype(np.uint8)
    cv2.rectangle(img, (20, 20), (100, 60), (255, 255, 255), -1, cv2.LINE_AA)
    cv2.putText(img, "radial", (28, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (40, 40, 44), 1, cv2.LINE_AA)
    cv2.imwrite(os.path.join(o, "grad_radial.png"), img)


def main(out):
    os.makedirs(out, exist_ok=True)
    for fn in (flat_icon_5, flat_icon_lines, ui_panel, badge_logo, ui_dense,
               flat_holes, grad_linear, grad_radial):
        fn(out)
    print("wrote 8 images to %s" % os.path.abspath(out))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
