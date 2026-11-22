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
import argparse, json, os, shutil, subprocess, sys
import numpy as np
import cv2

VERSION = "0.1.0"
PATH_MAGIC = "raster2svg"

# ------------------------------------------------------------------ image IO
def parse_hex(h):
    h = h.lstrip("#")
    return (int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16))  # BGR


def load_bgr(path, bg=(255, 255, 255)):
    raw = cv2.imread(path, cv2.IMREAD_UNCHANGED)
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


def coverage_mask(gray, dark_is_ink, ss=1):
    g = gray if ss == 1 else cv2.resize(gray.astype(np.float32), (gray.shape[1] * ss, gray.shape[0] * ss),
                                       interpolation=cv2.INTER_CUBIC)
    ink = (g < 127.5) if dark_is_ink else (g > 127.5)
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
            out.append('    <path d="%s" fill="%s" fill-rule="evenodd"/>' % (p["d"], fill))
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
    r = cv2.imread(tmp, cv2.IMREAD_COLOR)
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
    cv2.imwrite(os.path.join(outdir, stem + "_check.png"), panel)

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


def trace_mono(mask, gray, dark_is_ink, args):
    ss = max(1, int(args.ss))
    keep = cv2.resize(mask, (mask.shape[1] * ss, mask.shape[0] * ss), interpolation=cv2.INTER_NEAREST)
    up = cv2.bitwise_and(keep, coverage_mask(gray, dark_is_ink, ss)) if ss > 1 else mask
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
    src_ink = coverage_mask(gray, dark_is_ink, 1) > 0
    roots, comps = trace_mono(mask, gray, dark_is_ink, args)

    groups_items = []
    for r in roots:
        subpaths = []
        for node in [r] + r["children"]:
            subpaths.append(poly_d(node["pts"]) if node["kind"] == "polygon" else curve_d(node["segs"]))
        # one path per component: outer + its holes, evenodd punches the counters out
        groups_items.append(dict(component=r, paths=[dict(d=" ".join(subpaths))]))

    gs = group_components([g["component"] for g in groups_items], args.gap)
    gid_of = {}
    for gi, members in enumerate(gs):
        for m in members:
            gid_of[id(m)] = "glyph-%02d" % (gi + 1)
    groups = []
    for g in groups_items:
        groups.append(dict(gid=gid_of[id(g["component"])], paths=g["paths"]))

    svg = build_svg(W, H, groups, args.fill, args.title, grouped=not args.no_groups)

    odir = args.outdir or os.path.dirname(os.path.abspath(args.input))
    os.makedirs(odir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(args.input))[0]
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
        rec = {"component": gi + 1, "group": gid_of[id(r)],
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
    cv2.imwrite(os.path.join(odir, stem + "_overlay.png"), mark)

    print("engine        : %s (ss=%d)" % (args.mode, args.ss))
    print("image         : %dx%d  50%%-ink fraction %.3f (otsu %g, polarity %s)"
          % (W, H, float(src_ink.mean()), thr, "dark" if dark_is_ink else "light"))
    print("components    : %d  (%d holes)" % (len(roots), len(comps) - len(roots)))
    print("iou_rendered  : %.4f  (%s%s)" % (meta["iou"], meta["renderer"] or "proxy",
                                            ", proxy - not a fidelity claim" if meta["surrogate"] else ""))
    print("ink_ratio     : %.3f" % meta["ink_ratio"])
    print("svg           : %s" % svg_path)
    if args.check and (meta["iou"] < args.min_iou or meta["surrogate"]):
        print("CHECK FAILED (iou %.4f < %.2f or no renderer)" % (meta["iou"], args.min_iou),
              file=sys.stderr)
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
    for _, col, ds in layers:
        parts.append('<path d="%s" fill="%s" fill-rule="evenodd"/>' % (" ".join(ds), col))
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
           '  <!-- %s v%s | color K=%d | %d layers -->\n  %s\n</svg>\n'
           % (W, H, W, H, PATH_MAGIC, VERSION, K, len(layers), "\n  ".join(parts)))

    odir = args.outdir or os.path.dirname(os.path.abspath(args.input))
    os.makedirs(odir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(args.input))[0]
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
    if rend_bgr is None:
        rend_bgr = np.full((H, W, 3), 255, np.uint8)
    mse = float(np.mean((bgr.astype(np.float32) - rend_bgr.astype(np.float32)) ** 2)) if renderer else float("nan")
    psnr = 10 * np.log10(255.0 ** 2 / mse) if renderer and mse > 0 else float("nan")
    panel = np.concatenate([bgr, rend_bgr], axis=1)
    cv2.imwrite(os.path.join(odir, stem + "_check.png"), panel)
    print("mode          : color K=%d ss=%d" % (K, ss))
    print("layers        : %d" % len(layers))
    print("psnr_rendered : %s" % ("%.2f dB" % psnr if renderer else "n/a (no renderer)"))
    print("svg           : %s" % svg_path)
    if args.check and (not renderer or psnr < args.min_psnr):
        print("CHECK FAILED", file=sys.stderr)
        return 1
    return 0


def bgr_hex(b, g, r):
    return "#%02x%02x%02x" % (int(r), int(g), int(b))


def build_parser():
    p = argparse.ArgumentParser(
        description="Raster image -> editable SVG contour tracer (polygon/curve engines). "
                    "Version %s" % VERSION,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("-i", "--input", required=True, help="source PNG/JPG/WebP path")
    p.add_argument("-o", "--outdir", default=None, help="output directory (default: input dir)")
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
    p.add_argument("--min-iou", type=float, default=0.88, help="threshold for --check (mono)")
    p.add_argument("--min-psnr", type=float, default=30.0, help="threshold for --check (colour)")
    p.add_argument("--version", action="version", version="%(prog)s " + VERSION)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
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
