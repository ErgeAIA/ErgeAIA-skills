#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
raster2svg.py - raster (PNG/JPG/WebP) -> editable SVG contour tracer.

Engines
  polygon : line-only polygons; adjacent fitted lines are intersected so corners
            land sub-pixel. Corner-sharp.
  curve   : cubic Bezier fitting (Schneider, Newton reparameterisation).
  auto    : per contour - polygon when >50% of its corners sit within 18 deg of
            90/45/135, otherwise curve. (A glyph can contain both kinds.)

Accuracy note
  Binary-mask contours returned by OpenCV ride the outer pixel centres, i.e.
  about half a source pixel inside the real 50%-coverage edge. Filled as SVG that
  is a silent 10-25% ink loss on thin strokes. This script therefore supersamples
  the cleaned mask (default 4x), traces there, and divides coordinates back, which
  pulls the inset down to 0.5/ss source px.

Verification note
  IoU is computed on the *shipped SVG rasterised by a real renderer* (resvg, or
  rsvg-convert). If no renderer is present the script says so and falls back to a
  fillPoly proxy - the proxy is optimistic and must not be quoted as fidelity.

Outputs (into --outdir):
  <stem>.svg              grouped editable vector (+ <g id> per component)
  <stem>_coords.json      vertices / interior angles, or cubic control points
  <stem>_coords.txt       human-readable coordinate table
  <stem>_check.png        source | render | diff  + IoU
  <stem>_overlay.png      traced outline + node markers over the source
"""
import argparse, base64, json, os, re, shutil, subprocess, sys
import numpy as np
import cv2

VERSION = "0.1.0"
PATH_MAGIC = "raster2svg"


def _imread(path, flags=cv2.IMREAD_UNCHANGED):
    """cv2.imread cannot open non-ASCII paths on Windows (a 桌面/截图.png fails).
    Read bytes and decode instead."""
    try:
        buf = np.fromfile(path, dtype=np.uint8)
    except Exception:
        return None
    if buf.size == 0:
        return None
    return cv2.imdecode(buf, flags)


def _imwrite(path, img, params=None):
    ext = os.path.splitext(path)[1] or ".png"
    ok, buf = cv2.imencode(ext, img, params or [])
    if ok:
        buf.tofile(path)
    return ok

# ------------------------------------------------------------------ image IO
def parse_hex(h):
    h = h.lstrip("#")
    return (int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16))  # BGR


def load_bgr(path, bg=(255, 255, 255)):
    raw = _imread(path)
    if raw is None:
        raise RuntimeError("cannot read image: %s" % path)
    if raw.ndim == 2:
        return cv2.cvtColor(raw, cv2.COLOR_GRAY2BGR), None
    if raw.shape[2] == 4:
        a = raw[:, :, 3].astype(np.float32)[..., None] / 255.0
        bgv = np.array(bg, np.float32).reshape(1, 1, 3)
        comp = (raw[:, :, :3].astype(np.float32) * a + bgv * (1 - a)).astype(np.uint8)
        return comp, raw[:, :, 3]
    return raw[:, :, :3], None


def make_mask(gray, invert="auto"):
    """Otsu decides polarity only. The traced boundary is the 50%-coverage line,
    which is what a renderer reproduces, not the Otsu level."""
    thr, dark_ink = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    frac = float((dark_ink > 0).mean())
    dark_is_ink = True if invert == "dark" else (False if invert == "light" else frac <= 0.5)
    mask = dark_ink if dark_is_ink else cv2.bitwise_not(dark_ink)
    return mask, thr, frac, dark_is_ink


def ink_level(gray):
    """Midpoint between the paper value and the ink core, not a fixed 127.5.

    Black-on-white gives 127.5, but low-contrast ink (a #999 glyph on white, a
    watermarked scan) sits far above it - a fixed level traces nothing at all.
    Percentiles of the whole image are unusable: when ink is under 2% of the
    pixels the 2nd percentile lands on the antialiasing shoulder (measured: a
    48 px 口 gave p2=191, which would erode the whole glyph)."""
    vals, counts = np.unique(gray, return_counts=True)
    paper = float(vals[int(np.argmax(counts))])
    t, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if paper > t:
        ink_px = gray[gray < t]
        ink = float(np.percentile(ink_px, 5)) if ink_px.size else float(t)
    else:
        ink_px = gray[gray >= t]
        ink = float(np.percentile(ink_px, 95)) if ink_px.size else float(t)
    return 0.5 * (ink + paper)


def coverage_mask(gray, dark_is_ink, ss=1, level=127.5):
    g = gray if ss == 1 else cv2.resize(gray.astype(np.float32), (gray.shape[1] * ss, gray.shape[0] * ss),
                                       interpolation=cv2.INTER_CUBIC)
    ink = (g < level) if dark_is_ink else (g > level)
    return ink.astype(np.uint8) * 255


def clean_mask(mask, close, min_area):
    if close > 0:
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8),
                                iterations=close)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    keep = np.zeros_like(mask)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            keep[lab == i] = 255
    return keep



# ------------------------------------------------------------ geometry utils
def assign_segments(pts, verts):
    m = len(verts)
    ids = np.empty(len(pts), int)
    best = np.full(len(pts), np.inf)
    for i in range(m):
        a, b = verts[i], verts[(i + 1) % m]
        ab = b - a
        L2 = float(ab @ ab)
        if L2 == 0:
            continue
        t = np.clip(((pts - a) @ ab) / L2, 0, 1)
        d = np.linalg.norm(pts - (a + t[:, None] * ab), axis=1)
        upd = d < best
        ids[upd] = i
        best[upd] = d[upd]
    return ids


def fit_line(pts):
    p0 = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - p0, full_matrices=False)
    return p0, vt[0]


def intersect(p1, u1, p2, u2):
    A = np.array([[u1[0], -u2[0]], [u1[1], -u2[1]]])
    b = p2 - p1
    if abs(np.linalg.det(A)) < 1e-9:
        return None
    t = np.linalg.solve(A, b)
    return p1 + t[0] * u1


def interior_angles(v):
    m = len(v)
    out = []
    for i in range(m):
        a, c, b = v[(i - 1) % m], v[i], v[(i + 1) % m]
        u1, u2 = a - c, b - c
        cosv = (u1 @ u2) / (np.linalg.norm(u1) * np.linalg.norm(u2) + 1e-12)
        out.append(float(np.degrees(np.arccos(np.clip(cosv, -1, 1)))))
    return out


def dense_poly(pts, step=0.6):
    out = []
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        n = max(2, int(np.linalg.norm(b - a) / step))
        for k in range(n):
            out.append(a + (b - a) * (k / float(n)))
    return np.array(out)


def dense_curve(segs, step=0.6):
    out = []
    for b in segs:
        approx = np.linalg.norm(b[3] - b[0]) + np.linalg.norm(b[1] - b[0]) + np.linalg.norm(b[2] - b[3])
        n = max(3, int(approx / step))
        out.append(seg_points(b, n))
    return np.vstack(out)


def fit_error(samples, contour, chunk=120):
    """Worst distance (up-sampled px) from a fitted shape to the traced contour."""
    C = contour.reshape(-1, 2).astype(np.float32)
    worst = 0.0
    for i in range(0, len(samples), chunk):
        P = samples[i:i + chunk].astype(np.float32)
        d = np.sqrt(((P[:, None, :] - C[None, :, :]) ** 2).sum(-1)).min(1)
        worst = max(worst, float(d.max()))
    return worst


# ------------------------------------------------------------ polygon engine
def polygon_engine(cnt, dp_eps, max_snap):
    pts = cnt.reshape(-1, 2).astype(np.float64)
    verts = cv2.approxPolyDP(cnt, dp_eps, True).reshape(-1, 2).astype(np.float64)
    if len(verts) < 3:
        return None
    ids = assign_segments(pts, verts)
    m = len(verts)
    lines = []
    for s in range(m):
        a, b = verts[s], verts[(s + 1) % m]
        ab = b - a
        L2 = float(ab @ ab)
        sel = pts[ids == s]
        if L2 > 0 and len(sel) >= 8:
            t = ((sel - a) @ ab) / L2
            core = sel[(t > 0.08) & (t < 0.92)]
            if len(core) >= 8:
                lines.append(fit_line(core))
                continue
        lines.append((a, ab / max(np.linalg.norm(ab), 1e-9)))
    x, y, w, h = cv2.boundingRect(verts.astype(np.int32))
    snap = min(max_snap, 0.25 * max(1.0, float(min(w, h))))
    ref = np.empty_like(verts)
    for v in range(m):
        ip = intersect(lines[(v - 1) % m][0], lines[(v - 1) % m][1], lines[v][0], lines[v][1])
        ref[v] = ip if (ip is not None and np.linalg.norm(ip - verts[v]) <= snap) else verts[v]
    return {"kind": "polygon", "pts": ref}


# -------------------------------------------------------------- curve engine
def _bp(b, u):
    m = 1 - u
    return ((m**3)[:, None] * b[0] + (3 * m * m * u)[:, None] * b[1] +
            (3 * m * u * u)[:, None] * b[2] + (u**3)[:, None] * b[3])


def chord_param(d):
    seg = np.linalg.norm(np.diff(d, axis=0), axis=1)
    u = np.concatenate([[0.0], np.cumsum(seg)])
    return u / u[-1] if u[-1] > 0 else np.linspace(0, 1, len(d))


def gen_bezier(d, u):
    p0, p3 = d[0], d[-1]
    t1 = d[1] - d[0]; t2 = d[-2] - d[-1]
    n1, n2 = np.linalg.norm(t1), np.linalg.norm(t2)
    t1 = t1 / n1 if n1 > 1e-9 else np.array([1.0, 0.0])
    t2 = t2 / n2 if n2 > 1e-9 else np.array([-1.0, 0.0])
    u = u[:, None]
    m = 1 - u
    A0 = t1 * (3 * u * m * m)
    A1 = t2 * (3 * u * u * m)
    C00 = float((A0 * A0).sum()); C01 = float((A0 * A1).sum()); C11 = float((A1 * A1).sum())
    base = (m**3) * p0 + (3 * u * m * m) * p0 + (3 * u * u * m) * p3 + (u**3) * p3
    tmp = d - base
    X0 = float((A0 * tmp).sum()); X1 = float((A1 * tmp).sum())
    det = C00 * C11 - C01 * C01
    a1 = a2 = 0.0
    if abs(det) > 1e-12:
        a1 = (X0 * C11 - X1 * C01) / det
        a2 = (C00 * X1 - C01 * X0) / det
    if a1 < 1e-6 or a2 < 1e-6:
        a1 = a2 = float(np.linalg.norm(p3 - p0)) / 3.0
    return [p0, p0 + a1 * t1, p3 + a2 * t2, p3]


def max_error(d, u, b):
    p = _bp(b, u)
    dist = np.linalg.norm(d - p, axis=1)
    i = int(np.argmax(dist))
    return float(dist[i]), i


def newton(b, p, u):
    m = 1 - u
    q = _bp(b, np.array([u]))[0]
    q1 = 3 * ((m * m) * (b[1] - b[0]) + 2 * m * u * (b[2] - b[1]) + (u * u) * (b[3] - b[2]))
    q2 = 6 * (m * (b[2] - 2 * b[1] + b[0]) + u * (b[3] - 2 * b[2] + b[1]))
    num = float((q - p) @ q1); den = float(q1 @ q1 + (q - p) @ q2)
    if abs(den) < 1e-12:
        return u
    return float(min(1.0, max(0.0, u - num / den)))


def fit_cubic(d, error, depth=0):
    n = len(d)
    if n == 2:
        return [[d[0], d[0] + (d[1] - d[0]) / 3.0, d[0] + 2 * (d[1] - d[0]) / 3.0, d[1]]]
    u = chord_param(d)
    b = gen_bezier(d, u)
    e, split = max_error(d, u, b)
    if e <= error:
        return [b]
    if e < error * 4 and depth < 40:
        for _ in range(4):
            u = np.array([newton(b, d[i], u[i]) for i in range(n)])
            b = gen_bezier(d, u)
            e, split = max_error(d, u, b)
            if e <= error:
                return [b]
    split = min(max(split, 1), n - 2)
    return fit_cubic(d[:split + 1], error, depth + 1) + fit_cubic(d[split:], error, depth + 1)


def curve_engine(cnt, error, simplify):
    P = cnt.reshape(-1, 2).astype(np.float32)
    ap = cv2.approxPolyDP(P, simplify, True).reshape(-1, 2).astype(np.float64)
    if len(ap) < 3:
        return None
    ap = np.vstack([ap, ap[0]])
    return {"kind": "curve", "segs": fit_cubic(ap, error)}


def seg_points(seg, n=18):
    t = np.linspace(0, 1, n)
    return _bp(seg, t)

# ------------------------------------------------------------------ SVG build
def fmt(v):
    return ("%.2f" % v).rstrip("0").rstrip(".")


def poly_d(pts):
    return "M" + " L".join("%s %s" % (fmt(x), fmt(y)) for x, y in pts) + " Z"


def curve_d(segs):
    s = "M %s %s" % (fmt(segs[0][0][0]), fmt(segs[0][0][1]))
    for b in segs:
        s += " C %s %s %s %s %s %s" % (fmt(b[1][0]), fmt(b[1][1]), fmt(b[2][0]),
                                       fmt(b[2][1]), fmt(b[3][0]), fmt(b[3][1]))
    return s + " Z"


def build_svg(W, H, groups, fill, title, grouped=True):
    """groups: list of dict(gid, paths=[dict(d, kind)]) - one path per component,
    holes merged into the component path with fill-rule evenodd."""
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)]
    if title:
        out.append("  <title>%s</title>" % title)
    out.append("  <!-- %s v%s | %d components -->" % (PATH_MAGIC, VERSION, len(groups)))
    for g in groups:
        if grouped:
            out.append('  <g id="%s">' % g["gid"])
        for p in g["paths"]:
            pid = (' id="%s"' % p["id"]) if p.get("id") else ""
            out.append('    <path%s d="%s" fill="%s" fill-rule="evenodd"/>' % (pid, p["d"], fill))
        if grouped:
            out.append("  </g>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


def group_components(items, gap):
    """items: top-level contours with bbox. Split into visual groups by x-gap."""
    if not items:
        return []
    items = sorted(items, key=lambda p: (p["bbox"][0], p["bbox"][1]))
    groups = []
    cur = [items[0]]
    prev_right = items[0]["bbox"][0] + items[0]["bbox"][2]
    for it in items[1:]:
        x0 = it["bbox"][0]
        if x0 - prev_right > gap:
            groups.append(cur); cur = [it]
        else:
            cur.append(it)
        prev_right = max(prev_right, x0 + it["bbox"][2])
    groups.append(cur)
    return groups

# --------------------------------------------------------------- verification
def find_renderer():
    if shutil.which("rsvg-convert"):
        return "rsvg-convert"
    try:
        import resvg_py  # noqa: F401
        return "resvg"
    except Exception:
        return None


def render_svg(svg_path, w, h, renderer):
    if renderer == "resvg":
        import io
        from PIL import Image
        import resvg_py
        b = resvg_py.svg_to_bytes(svg_path=svg_path, background="#ffffff", width=w, height=h)
        rgb = np.array(Image.open(io.BytesIO(b)).convert("RGB"))
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR).astype(np.float64)
    tmp = svg_path + ".render.png"
    subprocess.run(["rsvg-convert", "-w", str(w), "-h", str(h), "-b", "white",
                    "-o", tmp, svg_path], check=True, capture_output=True)
    r = _imread(tmp, cv2.IMREAD_COLOR)
    os.remove(tmp)
    return r.astype(np.float64)


def verify(svg_path, mask, outdir, stem, fill_bgr):
    """IoU of the shipped SVG (rasterised by a real renderer) against source ink."""
    h, w = mask.shape[:2]
    renderer = find_renderer()
    ok = True
    if renderer:
        try:
            rendered = render_svg(svg_path, w, h, renderer)
            rend_ink = cv2.cvtColor(rendered.astype(np.uint8), cv2.COLOR_BGR2GRAY) < 127.5
            surrogate = False
        except Exception as e:
            print("warning: renderer failed (%s); falling back to fillPoly proxy" % e, file=sys.stderr)
            renderer, ok = None, False
    if not renderer:
        rend_ink = np.zeros((h, w), bool)
        surrogate = True
    src = mask > 0
    inter = np.logical_and(src, rend_ink).sum()
    union = np.logical_or(src, rend_ink).sum()
    iou = float(inter) / float(union) if union else 0.0
    ink_ratio = float(rend_ink.sum()) / float(src.sum() or 1)
    return dict(iou=iou, ink_ratio=ink_ratio, renderer=renderer, surrogate=surrogate), rend_ink


def write_check(outdir, stem, mask, rend_ink, iou, note):
    h, w = mask.shape[:2]
    diff = np.full((h, w, 3), 255, np.uint8)
    m = mask > 0
    diff[np.logical_and(m, rend_ink)] = (200, 200, 200)
    diff[np.logical_and(m, ~rend_ink)] = (0, 0, 230)   # red: ink lost
    diff[np.logical_and(~m, rend_ink)] = (0, 200, 0)   # green: ink added
    cv2.putText(diff, "IoU %.4f %s" % (iou, note), (16, 40), cv2.FONT_HERSHEY_SIMPLEX,
                1.0, (0, 0, 0), 2)
    panel = np.concatenate([cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR),
                            cv2.cvtColor((rend_ink * 255).astype(np.uint8), cv2.COLOR_GRAY2BGR),
                            diff], axis=1)
    _imwrite(os.path.join(outdir, stem + "_check.png"), panel)

# ------------------------------------------------------------------ tracing
def fit_contour(c, args, ss):
    """Pick the engine for one contour. auto compares the two fits' worst deviation."""
    if args.mode == "polygon":
        return polygon_engine(c, args.dp_eps * ss, args.max_snap * ss)
    if args.mode == "curve":
        return curve_engine(c, args.error * ss, 0.6 * ss)
    poly = polygon_engine(c, args.dp_eps * ss, args.max_snap * ss)
    curv = curve_engine(c, args.error * ss, 0.6 * ss)
    if poly is not None and curv is not None:
        ep = fit_error(dense_poly(poly["pts"]), c)
        ec = fit_error(dense_curve(curv["segs"]), c)
        if ec < ep * 0.9 or (ec <= ep * 1.1 and len(curv["segs"]) < len(poly["pts"])):
            return curv
        return poly
    return poly if poly is not None else curv


def trace_mono(mask, gray, dark_is_ink, level, args):
    ss = max(1, int(args.ss))
    keep = cv2.resize(mask, (mask.shape[1] * ss, mask.shape[0] * ss), interpolation=cv2.INTER_NEAREST)
    up = cv2.bitwise_and(keep, coverage_mask(gray, dark_is_ink, ss, level)) if ss > 1 else mask

    cnts, hier = cv2.findContours(up, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    if hier is None or not len(cnts):
        raise RuntimeError("no contours found (all components below --min-area?)")
    hier = hier[0]
    min_area_up = max(4.0, float(args.min_area) * ss * ss)
    comps = []
    for i, c in enumerate(cnts):
        if cv2.contourArea(c) < min_area_up:
            continue
        parent = hier[i][3]
        r = fit_contour(c, args, ss)
        if r is None:
            continue
        x, y, w, h = cv2.boundingRect(c)
        if r["kind"] == "polygon":
            r["pts"] = r["pts"] / ss
        else:
            r["segs"] = [[p / ss for p in b] for b in r["segs"]]
        r["bbox"] = [x / ss, y / ss, w / ss, h / ss]
        r["area"] = float(cv2.contourArea(c)) / (ss * ss)
        r["parent"] = parent
        comps.append(r)

    # attach holes to their component path (findContours parent index -> component)
    kept_idx = {i for i in range(len(cnts)) if cv2.contourArea(cnts[i]) >= min_area_up}
    index_to_comp = {}
    k = 0
    for i, c in enumerate(cnts):
        if i in kept_idx:
            k += 1
            index_to_comp[i] = k - 1
    for r, i in zip(comps, [i for i in range(len(cnts)) if i in kept_idx]):
        p = hier[i][3]
        r["parent_comp"] = index_to_comp.get(p, -1)
    roots = [r for r in comps if r["parent_comp"] < 0]
    for r in comps:
        r.setdefault("children", [])
    for r in comps:
        if r["parent_comp"] >= 0:
            comps[r["parent_comp"]]["children"].append(r)
    return roots, comps


def run_mono(args):
    bg = parse_hex(args.bg)
    bgr, alpha = load_bgr(args.input, bg)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    H, W = gray.shape
    mask, thr, frac, dark_is_ink = make_mask(gray, args.invert)
    mask = clean_mask(mask, args.close, args.min_area)
    level = ink_level(gray)
    src_ink = coverage_mask(gray, dark_is_ink, 1, level) > 0
    roots, comps = trace_mono(mask, gray, dark_is_ink, level, args)

    groups_items = []
    for ci, r in enumerate(roots, start=1):
        subpaths = []
        for node in [r] + r["children"]:
            subpaths.append(poly_d(node["pts"]) if node["kind"] == "polygon" else curve_d(node["segs"]))
        # one path per component: outer + its holes, evenodd punches the counters out
        r["pid"] = "c%02d" % ci
        groups_items.append(dict(component=r, paths=[dict(id=r["pid"], d=" ".join(subpaths))]))

    gs = group_components([g["component"] for g in groups_items], args.gap)
    # one <g> per GROUP, not per component: several components of one glyph must share
    # a single wrapper, otherwise the document carries duplicate id="glyph-02" (invalid
    # SVG, and editors silently drop the repeats).
    by_comp = {id(g["component"]): g for g in groups_items}
    groups = []
    for gi, members in enumerate(gs):
        paths = []
        for m in members:
            paths.extend(by_comp[id(m)]["paths"])
        for m in members:
            m["group"] = "glyph-%02d" % (gi + 1)
        groups.append(dict(gid="glyph-%02d" % (gi + 1), paths=paths))

    svg = build_svg(W, H, groups, args.fill, args.title, grouped=not args.no_groups)

    odir = args.outdir or os.path.dirname(os.path.abspath(args.input))
    os.makedirs(odir, exist_ok=True)
    stem = getattr(args, "_stem", None) or os.path.splitext(os.path.basename(args.input))[0]
    svg_path = os.path.join(odir, stem + ".svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)

    meta, rend_ink = verify(svg_path, src_ink, odir, stem, args.fill)
    write_check(odir, stem, src_ink.astype(np.uint8) * 255, rend_ink, meta["iou"],
                "(proxy)" if meta["surrogate"] else "resvg")

    # coordinate tables
    recs = []
    for gi, g in enumerate(groups_items):
        r = g["component"]
        rec = {"component": gi + 1, "group": r.get("group", ""), "pid": r.get("pid", ""),
               "engine": r["kind"], "bbox_xywh": [round(v, 2) for v in r["bbox"]],
               "area_px": round(r["area"], 1)}
        if r["kind"] == "polygon":
            rec["vertices_xy"] = [[round(float(x), 2), round(float(y), 2)] for x, y in r["pts"]]
            rec["interior_angle_deg"] = [round(a, 1) for a in interior_angles(r["pts"])]
        else:
            rec["cubic_segments"] = [[[round(float(v), 2) for v in pt] for pt in b]
                                     for b in r["segs"]]
        holes = []
        for hnode in r["children"]:
            if hnode["kind"] == "polygon":
                holes.append(dict(vertices_xy=[[round(float(x), 2), round(float(y), 2)]
                                               for x, y in hnode["pts"]]))
            else:
                holes.append(dict(cubic_segments=[[[round(float(v), 2) for v in pt] for pt in b]
                                                  for b in hnode["segs"]]))
        if holes:
            rec["holes"] = holes
        recs.append(rec)

    payload = {"image_size": [W, H], "engine": args.mode, "supersample": int(args.ss),
               "invert_frac_dark": round(frac, 3), "otsu_threshold": float(thr),
               "iou_rendered": round(meta["iou"], 4), "ink_ratio": round(meta["ink_ratio"], 3),
               "renderer": meta["renderer"], "surrogate_metric": meta["surrogate"],
               "coords": "image pixel space, y-axis down", "components": recs}
    with open(os.path.join(odir, stem + "_coords.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    L = ["# %s | mode=%s ss=%d canvas %dx%d (y down)" % (stem, args.mode, args.ss, W, H),
         "# components=%d IoU(rendered)=%.4f ink_ratio=%.3f renderer=%s"
         % (len(recs), meta["iou"], meta["ink_ratio"], meta["renderer"] or "proxy"), ""]
    for rec in recs:
        L.append("[%02d] %s %-7s bbox=%s" % (rec["component"], rec["group"],
                                             rec["engine"], rec["bbox_xywh"]))
        if rec["engine"] == "polygon":
            for j, (v, a) in enumerate(zip(rec["vertices_xy"], rec["interior_angle_deg"])):
                L.append("   V%02d (%8.2f,%8.2f) angle=%6.1f" % (j, v[0], v[1], a))
        else:
            for j, b in enumerate(rec["cubic_segments"]):
                L.append("   S%02d P0(%8.2f,%8.2f) C1(%8.2f,%8.2f) C2(%8.2f,%8.2f) P3(%8.2f,%8.2f)"
                         % (j, b[0][0], b[0][1], b[1][0], b[1][1], b[2][0], b[2][1], b[3][0], b[3][1]))
        L.append("")
    with open(os.path.join(odir, stem + "_coords.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))

    # overlay
    mark = cv2.cvtColor(255 - mask, cv2.COLOR_GRAY2BGR)
    for r in roots:
        for node in [r] + r["children"]:
            if node["kind"] == "polygon":
                cv2.polylines(mark, [np.round(node["pts"]).astype(np.int32)], True, (230, 120, 0), 1, cv2.LINE_AA)
                for v in node["pts"]:
                    cv2.circle(mark, (int(round(v[0])), int(round(v[1]))), 3, (0, 0, 255), -1, cv2.LINE_AA)
    _imwrite(os.path.join(odir, stem + "_overlay.png"), mark)

    diff_path = os.path.join(odir, stem + "_diff.png")
    dimg = np.full((H, W, 3), 250, np.uint8)
    dimg[src_ink] = (205, 205, 205)
    dimg[src_ink & ~rend_ink] = (40, 40, 220)
    dimg[~src_ink & rend_ink] = (40, 180, 90)
    _imwrite(diff_path, dimg)

    if args.html:
        nodes_total = sum(len(c.get("vertices_xy") or []) or len(c.get("cubic_segments") or [])
                          for c in recs)
        rmeta = dict(w=W, h=H, score="%.4f" % meta["iou"], ink="%.3f" % meta["ink_ratio"],
                     parts="%d" % len(roots), nodes=str(nodes_total),
                     bytes="%d B" % os.path.getsize(svg_path),
                     source=os.path.basename(args.input), renderer=meta["renderer"],
                     surrogate=meta["surrogate"], mode=args.mode,
                     engine=args.mode, ss=args.ss)
        print("html          : %s" % write_report(odir, stem, rmeta, recs, svg_path,
                                                  args.input, diff_path, args.mode))

    print("engine        : %s (ss=%d)" % (args.mode, args.ss))
    print("image         : %dx%d  50%%-ink fraction %.3f (otsu %g, polarity %s)"
          % (W, H, float(src_ink.mean()), thr, "dark" if dark_is_ink else "light"))
    print("components    : %d  (%d holes)" % (len(roots), len(comps) - len(roots)))
    print("iou_rendered  : %.4f  (%s%s)" % (meta["iou"], meta["renderer"] or "proxy",
                                            ", proxy - not a fidelity claim" if meta["surrogate"] else ""))
    print("ink_ratio     : %.3f" % meta["ink_ratio"])
    print("svg           : %s" % svg_path)
    ink_bad = not (args.ink_min <= meta["ink_ratio"] <= args.ink_max)
    if args.check and (meta["iou"] < args.min_iou or meta["surrogate"] or ink_bad):
        why = []
        if meta["surrogate"]:
            why.append("no renderer")
        if meta["iou"] < args.min_iou:
            why.append("iou %.4f < %.2f" % (meta["iou"], args.min_iou))
        if ink_bad:
            why.append("ink_ratio %.3f outside %.2f-%.2f"
                       % (meta["ink_ratio"], args.ink_min, args.ink_max))
        print("CHECK FAILED (%s)" % "; ".join(why), file=sys.stderr)
        return 1
    return 0


def run_color(args):
    bg = parse_hex(args.bg)
    bgr, _ = load_bgr(args.input, bg)
    H, W = bgr.shape[:2]
    Z = bgr.reshape(-1, 3).astype(np.float32)
    K = max(2, int(args.colors))
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
    cv2.setRNGSeed(0)
    _, labels, centers = cv2.kmeans(Z, K, None, crit, 8, cv2.KMEANS_PP_CENTERS)
    centers = centers.astype(np.float32)
    labels = labels.reshape(H, W)
    raw = sorted([(int((labels == i).sum()), i) for i in range(K)], reverse=True)
    # k-means spends clusters on antialiasing fringe: on a 3-colour badge at K=12,
    # 10 clusters were 100-450 px edge pixels and the real shapes lost their cluster.
    # Rule: a cluster under --merge-share of the canvas that sits within --merge of a
    # bigger cluster is fringe, and is folded into it. Small-but-distinct colours are
    # further than --merge away, so they survive; gradient steps are all >= share, so
    # they survive too. K is an upper bound, never a promise of K layers.
    total_px = float(Z.shape[0])
    share = float(getattr(args, "merge_share", 0.02))
    merge_d = float(getattr(args, "merge", 40.0))
    groups = []                      # list of dict(idx=[...], n=int, c=np.ndarray)
    for n, i in raw:
        if n == 0:
            continue
        col = centers[i]
        target = None
        if n / total_px < share:
            best = None
            for g in groups:
                if g["n"] <= n:
                    continue
                d = float(np.linalg.norm(g["c"] - col))
                if d <= merge_d and (best is None or d < best[0]):
                    best = (d, g)
            target = best[1] if best else None
        if target is None:
            groups.append(dict(idx=[i], n=n, c=col.copy()))
        else:
            target["c"] = (target["c"] * target["n"] + col * n) / (target["n"] + n)
            target["n"] += n
            target["idx"].append(i)
    if len(groups) < len(raw):
        kept = np.stack([g["c"] for g in groups])
        lab = np.empty(Z.shape[0], np.int32)
        for s0 in range(0, Z.shape[0], 200000):
            seg = Z[s0:s0 + 200000]
            lab[s0:s0 + 200000] = ((seg[:, None, :] - kept[None, :, :]) ** 2).sum(-1).argmin(1)
        labels = lab.reshape(H, W)
        centers = kept
    K = len(groups)
    centers = np.round(centers).astype(np.uint8)
    counts = sorted([(int((labels == i).sum()), i) for i in range(K)], reverse=True)
    base = counts[0][1]
    ss = max(1, int(args.ss))
    layers = []
    for cnt_i, i in counts[1:]:
        if cnt_i == 0:
            continue
        m = np.where(labels == i, 255, 0).astype(np.uint8)
        m = clean_mask(m, args.close, args.min_area)
        # quantised labels have no antialiasing, so the 50%-coverage trick does not
        # apply; supersampling only shrinks the half-pixel inset that opens seams
        # between adjacent layers. --grow (in supersampled px) closes the rest.
        up = cv2.resize(m, (W * ss, H * ss), interpolation=cv2.INTER_NEAREST)
        if args.grow > 0:
            up = cv2.dilate(up, np.ones((3, 3), np.uint8), iterations=int(args.grow))
        cs, hh = cv2.findContours(up, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        if hh is None:
            continue
        hh = hh[0]
        ds = []
        for j, c in enumerate(cs):
            if cv2.contourArea(c) < max(4.0, float(args.min_area) * ss * ss):
                continue
            # colour layers share boundaries with their neighbours, so corner
            # snapping must stay tight; the curve engine bulges rectilinear shapes
            # and an auto pick here cost 17 dB on a 5-colour icon (measured).
            r = polygon_engine(c, args.dp_eps * ss, min(args.max_snap, 1.5) * ss)
            if r:
                ds.append(poly_d(r["pts"] / ss))
        if ds:
            layers.append((cnt_i, bgr_hex(*centers[i]), ds))

    parts = ['<rect x="0" y="0" width="%d" height="%d" fill="%s"/>'
             % (W, H, bgr_hex(*centers[base]))]
    for li, (_, col, ds) in enumerate(layers, start=1):
        parts.append('<path id="k%02d" d="%s" fill="%s" fill-rule="evenodd"/>'
                     % (li, " ".join(ds), col))
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
           '  <!-- %s v%s | color K=%d | %d layers -->\n  %s\n</svg>\n'
           % (W, H, W, H, PATH_MAGIC, VERSION, K, len(layers), "\n  ".join(parts)))

    odir = args.outdir or os.path.dirname(os.path.abspath(args.input))
    os.makedirs(odir, exist_ok=True)
    stem = getattr(args, "_stem", None) or os.path.splitext(os.path.basename(args.input))[0]
    svg_path = os.path.join(odir, stem + ".svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)

    renderer = find_renderer()
    rend_bgr = None
    if renderer:
        try:
            rend_bgr = render_svg(svg_path, W, H, renderer).astype(np.uint8)
        except Exception:
            rend_bgr = None
    render_failed = bool(renderer) and rend_bgr is None
    if rend_bgr is None:
        rend_bgr = np.full((H, W, 3), 255, np.uint8)
    # a failed render must never score: comparing the source against a white canvas can
    # pass --check on a light page (measured on a pale UI screenshot before this fix).
    scored = bool(renderer) and not render_failed
    mse = float(np.mean((bgr.astype(np.float32) - rend_bgr.astype(np.float32)) ** 2)) if scored else float("nan")
    psnr = 10 * np.log10(255.0 ** 2 / mse) if scored and mse > 0 else float("nan")
    panel = np.concatenate([bgr, rend_bgr], axis=1)
    _imwrite(os.path.join(odir, stem + "_check.png"), panel)
    if args.html:
        check_png = os.path.join(odir, stem + "_check.png")
        rmeta = dict(w=W, h=H, score=("%.2f dB" % psnr) if scored else "n/a",
                     ink="K=%d" % K, parts="%d 层" % len(layers),
                     nodes="%d 条 path" % svg.count("<path"),
                     bytes="%d B" % os.path.getsize(svg_path),
                     source=os.path.basename(args.input), renderer=renderer,
                     surrogate=not bool(renderer), mode="color", engine="polygon", ss=ss)
        print("html          : %s" % write_report(odir, stem, rmeta, [], svg_path,
                                                  args.input, check_png, "color"))

    print("mode          : color K=%d ss=%d" % (K, ss))
    print("layers        : %d" % len(layers))
    print("psnr_rendered : %s" % ("%.2f dB" % psnr if scored else
                                  ("n/a (render failed)" if render_failed else "n/a (no renderer)")))
    print("svg           : %s" % svg_path)
    if args.check and (not scored or psnr < args.min_psnr):
        print("CHECK FAILED", file=sys.stderr)
        return 1
    return 0


def bgr_hex(b, g, r):
    return "#%02x%02x%02x" % (int(r), int(g), int(b))


# ------------------------------------------------------------------ text input
def safe_stem(text):
    keep = []
    for ch in text:
        if ch.isalnum() or ch in "-_":
            keep.append(ch)
        elif ch.strip():
            keep.append("_")
    s = "".join(keep).strip("_")
    return (s or "text")[:40]


def find_default_font():
    import os
    cands = [
        "C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in cands:
        if os.path.exists(c):
            return c
    return None


def render_text_png(text, font_path, size, out_png, ss=4, pad=None):
    """Render one line of text to an antialiased PNG, then trace that.

    The tracer's whole premise is "the ink boundary is the 50%-coverage line", so
    the text has to arrive as a real rasterisation: 4x supersample, then box-filter
    down. A font file is the true source here - tracing the PNG is a fallback, not
    an upgrade.
    """
    from PIL import Image, ImageDraw, ImageFont
    size = max(12, int(size))
    pad = int(pad if pad is not None else max(8, size // 4))
    font = ImageFont.truetype(font_path, size * ss)
    box = font.getbbox(text)          # already in supersampled pixels
    w = max(1, box[2] - box[0]) + 2 * pad * ss
    h = max(1, box[3] - box[1]) + 2 * pad * ss
    img = Image.new("L", (w, h), 255)
    ImageDraw.Draw(img).text((pad * ss - box[0], pad * ss - box[1]), text,
                              font=font, fill=0)
    img = img.resize((max(1, w // ss), max(1, h // ss)), Image.BOX)
    img.save(out_png)
    return out_png


# ------------------------------------------------------------------ html report
def _data_uri(path, max_side=1600):
    raw = _imread(path)
    if raw is None:
        return ""
    if max(raw.shape[:2]) > max_side:
        k = max_side / float(max(raw.shape[:2]))
        raw = cv2.resize(raw, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode(".png", raw)
    if not ok:
        return ""
    return "data:image/png;base64," + base64.b64encode(buf.tobytes()).decode("ascii")


def _nodes_group(comps):
    parts = ['<g id="r2s-nodes">']
    for c in comps:
        for xy in c.get("vertices_xy") or []:
            parts.append('<circle cx="%s" cy="%s" r="1.6"/>' % (fmt(xy[0]), fmt(xy[1])))
        for seg in c.get("cubic_segments") or []:
            for xy in (seg[1], seg[2]):
                parts.append('<circle cx="%s" cy="%s" r="1.2"/>' % (fmt(xy[0]), fmt(xy[1])))
    parts.append("</g>")
    return "".join(parts)


REPORT_CSS = """
:root{--bg:#0f1216;--panel:#171c22;--line:#262c34;--fg:#e8ecef;--dim:#98a2ad;--accent:#f0a03c;--ok:#4ec9a0;--bad:#f2705a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.7 -apple-system,"Segoe UI","Noto Sans SC",sans-serif}
header{padding:36px 40px 8px}
h1{margin:0 0 4px;font-size:26px;letter-spacing:.01em}
.sub{color:var(--dim);margin:0 0 18px;font-size:13px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));gap:10px;margin:0 0 8px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px 14px}
.card span{color:var(--dim);font-size:12px;display:block}
.card b{font-size:20px;font-weight:600}
main{padding:18px 40px 60px;display:grid;grid-template-columns:minmax(0,1.55fr) minmax(260px,.75fr);gap:22px}
@media(max-width:980px){main{grid-template-columns:1fr}}
.stage{background:#0b0e12;border:1px solid var(--line);border-radius:12px;overflow:hidden;position:relative;height:min(62vh,560px);cursor:grab}
.stage.dragging{cursor:grabbing}
.canvas{position:absolute;top:0;left:0;transform-origin:0 0;will-change:transform}
.canvas img,.canvas .vec{position:absolute;top:0;left:0;width:100%;height:100%}
.canvas .vec svg{display:block;width:100%;height:100%}
#r2s-nodes{display:none;pointer-events:none}
#r2s-nodes circle{fill:none;stroke:var(--accent);stroke-width:.45}
.views{display:flex;gap:6px;margin:0 0 10px}
.views button{background:var(--panel);color:var(--dim);border:1px solid var(--line);border-radius:999px;padding:4px 12px;font:inherit;font-size:13px;cursor:pointer}
.views button.on{color:#111;background:var(--accent);border-color:var(--accent)}
.tools{display:flex;align-items:center;gap:16px;margin:10px 0 0;color:var(--dim);font-size:13px;flex-wrap:wrap}
.tools input[type=range]{width:120px;accent-color:var(--accent)}
.tools label{display:flex;align-items:center;gap:6px}
.hint{margin-left:auto}
aside{min-width:0}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:0 0 14px}
.panel h2{font-size:13px;color:var(--dim);font-weight:600;margin:0 0 10px;letter-spacing:.04em}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:right}
th:first-child,td:first-child{text-align:left}
th{color:var(--dim);font-weight:600}
tbody tr{cursor:pointer}
tbody tr:hover{background:#1d232b}
tr.hl{background:rgba(240,160,60,.12)}
.layer{display:flex;align-items:center;gap:8px;padding:4px 0;font-size:13px;color:var(--fg)}
.layer i{width:14px;height:14px;border-radius:3px;border:1px solid #0004;display:inline-block}
.layer input{accent-color:var(--accent)}
.dl{display:inline-block;margin-top:6px;color:var(--accent);text-decoration:none;font-size:13px}
code{font-family:ui-monospace,Consolas,monospace;font-size:12px;color:#c8d3dd}
.toolbar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:12px 0 0}
.toolbar button{background:var(--panel);color:var(--fg);border:1px solid var(--line);border-radius:7px;padding:6px 11px;font:inherit;font-size:13px;cursor:pointer}
.toolbar button.on{background:var(--accent);color:#111;border-color:var(--accent)}
.toolbar button.primary{background:var(--accent);color:#111;border-color:var(--accent);font-weight:600}
.toolbar input[type=range]{width:110px;accent-color:var(--accent)}
.toolbar label{display:flex;align-items:center;gap:6px;color:var(--dim);font-size:13px}
.ednote{font-size:12px;color:var(--dim);margin:8px 0 0;line-height:1.6}
#r2s-edit-nodes circle{cursor:move;fill:#fff;stroke:#111;stroke-width:.5}
#r2s-edit-nodes circle.h{fill:var(--accent);stroke:#fff;stroke-width:.4}
.colorbtn{width:26px;height:20px;padding:0;border:1px solid var(--line);border-radius:4px;background:none;cursor:pointer}
.hex{width:82px;background:var(--panel);color:var(--fg);border:1px solid var(--line);border-radius:5px;padding:3px 6px;font:inherit;font-size:12px;text-transform:uppercase}
.hex.bad{border-color:var(--bad)}
.palette{display:flex;gap:6px;align-items:center;margin:8px 0 0}
.palette b{font-size:12px;color:var(--dim);font-weight:500}
.palette i{width:18px;height:18px;border-radius:4px;border:1px solid #fff4;cursor:pointer;display:inline-block}
.layer.sel{outline:1px solid var(--accent);outline-offset:-1px}
"""

REPORT_JS = """
(function(){
  var stage=document.getElementById('stage'), canvas=document.getElementById('canvas');
  var src=document.getElementById('src'), vec=document.getElementById('vec'), dif=document.getElementById('diff');
  var scale=1, tx=0, ty=0, drag=null;
  function apply(){canvas.style.transform='translate('+tx+'px,'+ty+'px) scale('+scale+')';canvas.setAttribute('data-scale',scale);}
  function fit(){
    var cw=canvas.offsetWidth||1, ch=canvas.offsetHeight||1;
    scale=Math.min((stage.clientWidth-2)/cw,(stage.clientHeight-2)/ch,4);
    tx=(stage.clientWidth-cw*scale)/2; ty=(stage.clientHeight-ch*scale)/2; apply();
  }
  window.addEventListener('load',fit);
  stage.addEventListener('wheel',function(e){
    e.preventDefault();
    var k=e.deltaY<0?1.12:1/1.12, r=stage.getBoundingClientRect();
    var mx=e.clientX-r.left, my=e.clientY-r.top;
    var nx=(mx-tx)/scale, ny=(my-ty)/scale;
    scale=Math.min(12,Math.max(.15,scale*k));
    tx=mx-nx*scale; ty=my-ny*scale; apply();
  },{passive:false});
  stage.addEventListener('mousedown',function(e){drag={x:e.clientX,y:e.clientY,tx:tx,ty:ty};stage.classList.add('dragging');});
  window.addEventListener('mousemove',function(e){if(!drag)return;tx=drag.tx+(e.clientX-drag.x);ty=drag.ty+(e.clientY-drag.y);apply();});
  window.addEventListener('mouseup',function(){drag=null;stage.classList.remove('dragging');});
  stage.addEventListener('dblclick',fit);
  var meta=JSON.parse(document.getElementById('meta').textContent);
  var views=document.querySelectorAll('.views button');
  views.forEach(function(b){b.addEventListener('click',function(){
    views.forEach(function(x){x.classList.toggle('on',x===b);});
    var v=b.dataset.view;
    src.style.display=(v==='src'||v==='split')?'block':'none';
    vec.style.display=(v==='vec'||v==='split')?'block':'none';
    dif.style.display=(v==='diff')?'block':'none';
    if(op){op.value=(v==='split')?55:100; vec.style.opacity=op.value/100;}
  });});
  var op=document.getElementById('op');
  if(op){ vec.style.opacity=op.value/100;
    op.addEventListener('input',function(){vec.style.opacity=op.value/100;}); }
  var nt=document.getElementById('nodes-toggle');
  var nodes=document.querySelector('#r2s-nodes');
  if(nt&&nodes) nt.addEventListener('change',function(){nodes.style.display=nt.checked?'block':'none';});
  if(nt&&!nodes) nt.parentNode.style.display='none';
  var svg=document.querySelector('#vec svg');
  if(svg){
    var items=svg.querySelectorAll('path[id]');
    items = Array.prototype.slice.call(items);
    var box=document.getElementById('layers');
    if(box) items.forEach(function(el){
      var row=document.createElement('label'); row.className='layer';
      var cb=document.createElement('input'); cb.type='checkbox'; cb.checked=true;
      cb.addEventListener('change',function(){el.style.display=cb.checked?'':'none';});
      var sw=document.createElement('i'); sw.style.background=el.getAttribute('fill')||'#8b96a2';
      var tx2=document.createElement('span'); tx2.textContent=el.id;
      row.appendChild(cb); row.appendChild(sw); row.appendChild(tx2); box.appendChild(row);
    });
    document.querySelectorAll('tbody tr[data-gid]').forEach(function(tr){
      var gid=tr.dataset.gid;
      tr.addEventListener('mouseenter',function(){var g=svg.querySelector('#'+gid); if(g) g.classList.add('hl');});
      tr.addEventListener('mouseleave',function(){var g=svg.querySelector('#'+gid); if(g) g.classList.remove('hl');});
      tr.addEventListener('click',function(){
        var g=svg.querySelector('#'+gid); if(!g) return;
        g.style.stroke='#f0a03c'; g.style.strokeWidth='0.6';
        setTimeout(function(){g.style.stroke=''; g.style.strokeWidth='';},900);
      });
    });
  }
})();
"""


def write_report(outdir, stem, meta, comps, svg_path, src_png, diff_png, mode):
    svg_txt = open(svg_path, encoding="utf-8").read()
    if comps:
        svg_txt = svg_txt.replace("</svg>", _nodes_group(comps) + "</svg>")
    svg_txt = re.sub(r'(<svg[^>]*?)width="\d+"\s+height="\d+"', r'\1width="100%" height="100%"',
                     svg_txt, count=1)
    title = "%s · 描摹报告" % stem
    sub = ("引擎 %s · 画布 %dx%d · 版本 v%s · 渲染器 %s%s"
           % (mode, meta["w"], meta["h"], VERSION, meta["renderer"] or "缺（代评分）",
              " · ⚠ 代理指标" if meta.get("surrogate") else ""))
    cards = [
        ("IoU / PSNR", meta["score"]), ("墨量比", meta["ink"]), ("部件/层", meta["parts"]),
        ("节点/路径", meta["nodes"]), ("SVG 体积", meta["bytes"]), ("源图", meta["source"]),
    ]
    card_html = "".join('<div class="card"><span>%s</span><b>%s</b></div>' % (k, v) for k, v in cards)
    rows = []
    for c in comps:
        n = len(c.get("vertices_xy") or []) or len(c.get("cubic_segments") or []) or len(c.get("holes") or [])
        rows.append("<tr data-gid=\"%s\"><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%d</td></tr>"
                    % (c.get("pid", ""), c.get("pid", c.get("group", "")), c.get("engine", ""),
                       c.get("bbox_xywh", ""), c.get("area_px", ""), n))
    table = ("<table><thead><tr><th>组</th><th>引擎</th><th>bbox</th><th>面积</th><th>节点</th></tr></thead>"
             "<tbody>%s</tbody></table>" % "".join(rows)) if rows else \
            "<p class=\"sub\">彩色模式：每层颜色与顺序见左侧列表；不输出逐部件坐标。</p>"
    json_meta = json.dumps(meta, ensure_ascii=False)
    html = REPORT_TEMPLATE
    for key, val in (("__W__", str(meta["w"])), ("__H__", str(meta["h"])),
                     ("__TITLE__", title), ("__SUB__", sub), ("__CARDS__", card_html),
                     ("__CSS__", REPORT_CSS), ("__SRC__", _data_uri(src_png)),
                     ("__DIFF__", _data_uri(diff_png) if diff_png else ""),
                     ("__SVG__", svg_txt), ("__META__", json_meta), ("__TABLE__", table),
                     ("__JS__", REPORT_JS), ("__EDITOR_JS__", REPORT_EDITOR_JS),
                     ("__STEM__", stem), ("__MODE__", mode)):
        html = html.replace(key, val)
    path = os.path.join(outdir, stem + ".html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return path


REPORT_EDITOR_JS = r"""
(function(){
  var svg=document.querySelector('#vec svg'); if(!svg) return;
  var NS='http://www.w3.org/2000/svg';
  var paths=[].slice.call(svg.querySelectorAll('path[id]'));
  var groups=[].slice.call(svg.querySelectorAll('g[id^="glyph-"]'));
  var hist=[], future=[], nodeMode=false, pending={}, selected=0, rowEls=[];
  function begin(k){ if(!pending[k]){ push(); pending[k]=true; } }
  function end(k){ pending[k]=false; }
  function normHex(v){
    v=(v||'').trim().replace(/^#/,'').replace(/^0x/i,'').replace(/[^0-9a-fA-F]/g,'');
    if(v.length===3) v=v[0]+v[0]+v[1]+v[1]+v[2]+v[2];
    return /^[0-9a-fA-F]{6}$/.test(v) ? '#'+v.toLowerCase() : null;
  }
  function setColor(i,hex){
    var p=paths[i]; if(!p||!hex) return;
    begin('col'+i); p.setAttribute('fill',hex);
    rowEls.forEach(function(row,j){ if(!row) return;
      var c=row.querySelector('.colorbtn'), h=row.querySelector('.hex'), s=row.querySelector('i');
      if(!c||!h) return;
      if(j===i){ c.value=hex; h.value=hex.slice(1).toUpperCase(); h.classList.remove('bad'); if(s)s.style.background=hex; }
    });
    end('col'+i);
  }
  var layer=document.createElementNS(NS,'g'); layer.id='r2s-edit-nodes'; layer.style.display='none';
  svg.appendChild(layer);

  function f2(v){ v=+v; return String(Math.round(v*100)/100); }
  function parse(d){
    var t=(d||'').match(/[MLCZ]|-?\d*\.?\d+(?:e[-+]?\d+)?/gi)||[], out=[], i=0, cur=[0,0], start=[0,0];
    while(i<t.length){
      var op=t[i++];
      if(op==='M'){ cur=[+t[i++],+t[i++]]; start=cur.slice(); out.push({c:'M',p:cur.slice()}); }
      else if(op==='L'){ cur=[+t[i++],+t[i++]]; out.push({c:'L',p:cur.slice()}); }
      else if(op==='C'){ var a=[+t[i++],+t[i++]],b=[+t[i++],+t[i++]],p=[+t[i++],+t[i++]]; out.push({c:'C',c1:a,c2:b,p:p}); cur=p; }
      else if(op==='Z'){ out.push({c:'Z'}); cur=start.slice(); }
      else break;
    }
    return out;
  }
  function write(cmds){
    return cmds.map(function(k){
      if(k.c==='Z') return 'Z';
      if(k.c==='M') return 'M'+f2(k.p[0])+' '+f2(k.p[1]);
      if(k.c==='L') return 'L'+f2(k.p[0])+' '+f2(k.p[1]);
      return 'C'+f2(k.c1[0])+' '+f2(k.c1[1])+' '+f2(k.c2[0])+' '+f2(k.c2[1])+' '+f2(k.p[0])+' '+f2(k.p[1]);
    }).join(' ');
  }
  function snap(){ return {paths:paths.map(function(p){return {d:p.getAttribute('d'),fill:p.getAttribute('fill'),
    stroke:p.getAttribute('stroke'),sw:p.getAttribute('stroke-width'),po:p.style.paintOrder};}),
    trans:groups.map(function(g){return g.getAttribute('transform')||'';})}; }
  function apply(s){
    paths.forEach(function(p,i){var q=s.paths[i]; if(!q)return; p.setAttribute('d',q.d); p.setAttribute('fill',q.fill||'#000');
      if(q.stroke&&q.stroke!=='none'){p.setAttribute('stroke',q.stroke);p.setAttribute('stroke-width',q.sw);} else {p.removeAttribute('stroke');p.removeAttribute('stroke-width');}
      p.style.paintOrder=q.po||'';});
    groups.forEach(function(g,i){var t=s.trans[i]; if(t)g.setAttribute('transform',t); else g.removeAttribute('transform');});
    drawNodes(); syncControls();
  }
  function push(){ hist.push(snap()); if(hist.length>60)hist.shift(); future=[]; }
  function undo(){ if(!hist.length)return; future.push(snap()); apply(hist.pop()); }
  function redo(){ if(!future.length)return; hist.push(snap()); apply(future.pop()); }

  function drawNodes(){
    while(layer.firstChild) layer.removeChild(layer.firstChild);
    if(!nodeMode) return;
    paths.forEach(function(p,pi){
      parse(p.getAttribute('d')).forEach(function(k,ki){
        var pts = k.c==='C' ? [['h',k.c1],['h',k.c2],['a',k.p]] :
                  (k.c==='M'||k.c==='L') ? [['a',k.p]] : [];
        pts.forEach(function(pair){
          var c=document.createElementNS(NS,'circle');
          c.setAttribute('cx',f2(pair[1][0])); c.setAttribute('cy',f2(pair[1][1]));
          c.setAttribute('r',pair[0]==='a'?1.9:1.3);
          if(pair[0]==='h') c.setAttribute('class','h');
          c.setAttribute('data-pi',pi); c.setAttribute('data-ki',ki); c.setAttribute('data-pt',pair[0]);
          layer.appendChild(c);
        });
      });
    });
    // keep handles around 10px on screen at any zoom level
    var z=+(document.getElementById('canvas').getAttribute('data-scale')||1);
    [].slice.call(layer.querySelectorAll('circle')).forEach(function(c){
      c.setAttribute('r', c.getAttribute('class')==='h' ? Math.max(1.3,3.5/z) : Math.max(1.9,5/z));
    });
  }
  var stageEl=document.getElementById('stage');
  if(stageEl) stageEl.addEventListener('wheel',function(){ setTimeout(drawNodes,0); });
  layer.addEventListener('mousedown',function(e){e.stopPropagation();});
  layer.addEventListener('pointerdown',function(e){
    var c=e.target; if(c.tagName!=='circle') return;
    e.preventDefault(); e.stopPropagation(); push();
    var p=paths[+c.getAttribute('data-pi')], cmds=parse(p.getAttribute('d')), k=cmds[+c.getAttribute('data-ki')];
    var key=c.getAttribute('data-pt')==='a'?'p':c.getAttribute('data-pt');
    function at(ev){ var pt=svg.createSVGPoint(); pt.x=ev.clientX; pt.y=ev.clientY;
      return pt.matrixTransform(svg.getScreenCTM().inverse()); }
    function move(ev){ var q=at(ev); k[key][0]=Math.round(q.x*100)/100; k[key][1]=Math.round(q.y*100)/100;
      p.setAttribute('d',write(cmds)); c.setAttribute('cx',k[key][0]); c.setAttribute('cy',k[key][1]);
      var cd=document.getElementById('ed-coord');
      if(cd) cd.textContent='('+f2(k[key][0])+', '+f2(k[key][1])+')';
    }
    function up(){
      window.removeEventListener('pointermove',move); window.removeEventListener('pointerup',up);
      var pts=[]; parse(p.getAttribute('d')).forEach(function(k){
        if(k.c==='Z') return;
        pts.push(k.p); if(k.c==='C'){ pts.push(k.c1); pts.push(k.c2); }
      });
      if(!pts.length) return;
      var xs=pts.map(function(q){return q[0];}), ys=pts.map(function(q){return q[1];});
      var x0=Math.min.apply(null,xs), y0=Math.min.apply(null,ys);
      var bb='['+f2(x0)+', '+f2(y0)+', '+f2(Math.max.apply(null,xs)-x0)+', '+f2(Math.max.apply(null,ys)-y0)+']';
      var row=document.querySelector('tbody tr[data-gid="'+p.id+'"]');
      if(row && row.cells[2]) row.cells[2].textContent=bb;
    }
    window.addEventListener('pointermove',move); window.addEventListener('pointerup',up);
  });

  // colour inputs: replace the passive swatch in the existing layer panel
  [].slice.call(document.querySelectorAll('#layers .layer')).forEach(function(row,i){
    var sw=row.querySelector('i'); if(!sw||!paths[i]) return;
    rowEls[i]=row;
    var cur=normHex(paths[i].getAttribute('fill'))||'#000000';
    var col=document.createElement('input'); col.type='color'; col.className='colorbtn';
    col.title='取色器'; col.value=cur;
    var hx=document.createElement('input'); hx.type='text'; hx.className='hex'; hx.id='ed-hex';
    hx.value=cur.slice(1).toUpperCase(); hx.title='HEX：#ff0000 / ff0000 / f00 都行';
    row.addEventListener('click',function(){
      selected=i; rowEls.forEach(function(r,j){ if(r) r.classList.toggle('sel',j===i); });
    });
    col.addEventListener('input',function(){ setColor(i,col.value); });
    hx.addEventListener('input',function(){
      var v=normHex(hx.value);
      if(!v){ hx.classList.add('bad'); return; }
      hx.classList.remove('bad'); setColor(i,v);
    });
    row.insertBefore(hx,sw.nextSibling); row.insertBefore(col,hx); sw.style.display='none';
  });
  var pal=document.getElementById('ed-palette');
  if(pal){
    ['#000000','#ffffff','#f26a1b','#e5484d','#30a46c','#3b82f6','#a855f7','#f5d90a'].forEach(function(hex){
      var b=document.createElement('i'); b.style.background=hex; b.title=hex;
      b.addEventListener('click',function(){ setColor(selected,hex); });
      pal.appendChild(b);
    });
  }
  if(rowEls.length) rowEls[0].classList.add('sel');

  var sp=document.getElementById('ed-spacing'), wt=document.getElementById('ed-weight');
  var mode=document.getElementById('ed-mode');
  if(!groups.length && sp){ sp.disabled=true; sp.parentNode.style.opacity=.45; }
  if(mode) mode.addEventListener('click',function(){
    nodeMode=!nodeMode; layer.style.display=nodeMode?'block':'none';
    mode.classList.toggle('on',nodeMode); mode.textContent=nodeMode?'编辑节点：开':'编辑节点：关'; drawNodes();
  });
  if(sp) sp.addEventListener('input',function(){ begin('sp'); var v=+sp.value;
    groups.forEach(function(g,i){ g.setAttribute('transform','translate('+(i*v)+',0)'); }); });
  if(sp) sp.addEventListener('change',function(){ end('sp'); });
  if(wt) wt.addEventListener('input',function(){ begin('wt'); var v=+wt.value;
    paths.forEach(function(p){ if(v>0){ p.setAttribute('stroke',p.getAttribute('fill')||'#000');
      p.setAttribute('stroke-width',String(v*2)); p.style.paintOrder='stroke fill'; }
      else { p.removeAttribute('stroke'); p.removeAttribute('stroke-width'); p.style.paintOrder=''; } }); });
  if(wt) wt.addEventListener('change',function(){ end('wt'); });

  var initial=snap();
  function syncControls(){ if(sp){ var t=groups[0]?groups[0].getAttribute('transform'):'';
      var m=t&&t.match(/translate\((-?[\d.]+)/); sp.value=m?m[1]:0; }
    if(wt){ var s=paths[0]?paths[0].getAttribute('stroke-width'):''; wt.value=s?(+s/2):0; } }
  document.getElementById('ed-undo').addEventListener('click',undo);
  document.getElementById('ed-redo').addEventListener('click',redo);
  document.getElementById('ed-reset').addEventListener('click',function(){ push(); apply(initial); });
  document.addEventListener('keydown',function(e){ if(!(e.ctrlKey||e.metaKey))return;
    if(e.key==='z'){ e.preventDefault(); e.shiftKey?redo():undo(); } });
  document.getElementById('ed-export').addEventListener('click',function(){
    var clone=svg.cloneNode(true);
    var a=clone.querySelector('#r2s-edit-nodes'); if(a)a.parentNode.removeChild(a);
    var b=clone.querySelector('#r2s-nodes'); if(b&&b.style.display!=='block')b.parentNode.removeChild(b);
    var text=new XMLSerializer().serializeToString(clone);
    var blob=new Blob([text],{type:'image/svg+xml;charset=utf-8'});
    var link=document.createElement('a'); link.href=URL.createObjectURL(blob);
    link.download=(document.title||'edited').replace(/[^\w\u4e00-\u9fa5-]+/g,'_')+'.svg';
    link.click(); setTimeout(function(){URL.revokeObjectURL(link.href);},2000);
  });
  syncControls();
})();
"""


REPORT_TEMPLATE = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title><style>__CSS__</style></head>
<body>
<header>
  <h1>__TITLE__</h1>
  <p class="sub">__SUB__</p>
  <div class="cards">__CARDS__</div>
</header>
<main>
  <section>
    <div class="views">
      <button data-view="split" class="on">对比</button>
      <button data-view="src">源图</button>
      <button data-view="vec">矢量</button>
      <button data-view="diff">差异</button>
    </div>
    <div class="stage" id="stage">
      <div class="canvas" id="canvas" style="width:__W__px;height:__H__px">
        <img id="src" src="__SRC__" alt="源图">
        <div id="vec" class="vec">__SVG__</div>
        <img id="diff" src="__DIFF__" alt="差异" style="display:none">
      </div>
    </div>
    <div class="tools">
      <label><input type="checkbox" id="nodes-toggle"> 显示节点</label>
      <label>矢量不透明度 <input type="range" id="op" min="0" max="100" value="55"></label>
      <span class="hint">差异视图：红=源图有墨而 SVG 丢了 · 绿=SVG 多出的墨</span>
      <span class="hint">滚轮缩放 · 拖动平移 · 双击复位</span>
    </div>
    <div class="toolbar">
      <button id="ed-mode">编辑节点：关</button>
      <label>字距 <input type="range" id="ed-spacing" min="-30" max="40" step="1" value="0"></label>
      <label>视觉加粗 <input type="range" id="ed-weight" min="0" max="4" step="0.5" value="0"></label>
      <span id="ed-coord" class="hint">(—, —)</span>
      <button id="ed-undo">撤销</button><button id="ed-redo">重做</button><button id="ed-reset">复位</button>
      <button id="ed-export" class="primary">导出 SVG</button>
    </div>
    <div class="palette" id="ed-palette"><b>常用色</b></div>
    <p class="ednote">先点右侧某个部件选中它，再点头顶色块套色；也可在每行直接用取色器或输入 HEX（<code>#</code>、<code>0x</code> 会自动去掉，支持 3 位缩写）。打开「编辑节点」后拖白色锚点或橙色控制点。字距按每个字整体平移，视觉加粗用描边模拟（不是换字体）。导出的是改后的 SVG，源图不会被改动。</p>
  </section>
  <aside>
    <div class="panel"><h2>层 / 部件</h2><div id="layers"></div>
      <a class="dl" href="__STEM__.svg" download>下载 SVG</a></div>
    <div class="panel"><h2>部件坐标</h2>__TABLE__</div>
  </aside>
</main>
<script type="application/json" id="meta">__META__</script>
<script>__JS__</script>
<script>__EDITOR_JS__</script>
</body></html>
"""


def build_parser():
    p = argparse.ArgumentParser(
        description="Raster image -> editable SVG contour tracer (polygon/curve engines). "
                    "Version %s" % VERSION,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("-i", "--input", required=False, help="source PNG/JPG/WebP path")
    p.add_argument("-o", "--outdir", default=None, help="output directory (default: input dir)")
    p.add_argument("--text", default=None,
                   help="skip the image: render this line of text with --font, then trace it")
    p.add_argument("--font", default=None,
                   help="TTF/OTF path for --text (default: a system CJK font if one is present)")
    p.add_argument("--size", type=int, default=128, help="--text: em size in px")
    p.add_argument("--name", default=None, help="output stem (default: from the input file or --text)")
    p.add_argument("--html", dest="html", action="store_true", default=True,
                   help="write an interactive <stem>.html report")
    p.add_argument("--no-html", dest="html", action="store_false", help="skip the HTML report")
    p.add_argument("--mode", choices=["auto", "polygon", "curve"], default="auto",
                   help="auto decides per contour; forced modes apply to every contour")
    p.add_argument("--colors", type=int, default=1,
                   help="k-means colour layers; >1 = colour mode")
    p.add_argument("--ss", type=int, default=4,
                   help="supersample factor for contour extraction (1 disables; 4 removes the half-pixel inset)")
    p.add_argument("--error", type=float, default=1.2,
                   help="curve engine max fit error in source px")
    p.add_argument("--dp-eps", type=float, default=1.4,
                   help="polygon engine Douglas-Peucker tolerance in source px")
    p.add_argument("--max-snap", type=float, default=6.0,
                   help="polygon corner shift cap in source px (auto-clamped to 25%% of the component)")
    p.add_argument("--min-area", type=int, default=20,
                   help="drop connected components smaller than this (source px^2); "
                        "300 deletes the dot of 之 at 128px em")
    p.add_argument("--close", type=int, default=0, help="morphological close iterations")
    p.add_argument("--grow", type=int, default=1,
                   help="colour mode: dilate each layer by this many supersampled px to close inter-layer seams")
    p.add_argument("--merge", type=float, default=40.0,
                   help="colour mode: fold a small cluster into a bigger one when their RGB distance is below this")
    p.add_argument("--merge-share", type=float, default=0.02,
                   help="colour mode: only clusters under this share of pixels may be folded (fringe guard)")
    p.add_argument("--gap", type=int, default=40, help="x-gap (px) that starts a new <g> group")
    p.add_argument("--invert", choices=["auto", "dark", "light"], default="auto", help="ink polarity")
    p.add_argument("--bg", default="#ffffff", help="background used to composite alpha")
    p.add_argument("--fill", default="#000000", help="SVG fill colour (mono)")
    p.add_argument("--title", default=None, help="<title> text for the SVG")
    p.add_argument("--no-groups", action="store_true", help="emit one flat <path> per component")
    p.add_argument("--check", action="store_true",
                   help="exit 1 when the rendered IoU/PSNR misses the threshold or no renderer exists")
    p.add_argument("--min-iou", type=float, default=0.88,
                   help="--check: mono IoU threshold (0.88 ships; 0.90 is the high-precision target)")
    p.add_argument("--ink-min", type=float, default=0.95, help="--check: lower bound of ink_ratio")
    p.add_argument("--ink-max", type=float, default=1.05, help="--check: upper bound of ink_ratio")
    p.add_argument("--min-psnr", type=float, default=30.0, help="threshold for --check (colour)")
    p.add_argument("--version", action="version", version="%(prog)s " + VERSION)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not args.text and not args.input:
        print("error: pass -i/--input <image> or --text <words>", file=sys.stderr)
        return 2
    try:
        if args.text:
            if args.colors > 1:
                print("error: --text is a mono input; drop --colors", file=sys.stderr)
                return 2
            font = args.font or find_default_font()
            if not font or not os.path.exists(font):
                print("error: --text needs a font; pass --font <path.ttf|otf> "
                      "(no system CJK font found)", file=sys.stderr)
                return 2
            stem = args.name or safe_stem(args.text)
            odir = args.outdir or os.getcwd()
            os.makedirs(odir, exist_ok=True)
            args.input = render_text_png(args.text, font, args.size,
                                         os.path.join(odir, stem + "_source.png"))
            args._stem = stem
        if getattr(args, "colors", 1) and args.colors > 1:
            return run_color(args)
        return run_mono(args)
    except SystemExit:          # argparse keeps its own exit codes (0/2)
        raise
    except Exception as e:      # anything else is a tool error, not a trace verdict
        print("error: %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
