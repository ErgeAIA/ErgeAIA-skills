---
name: raster-to-svg
description: "Trace a raster image (PNG、JPG、WebP) into a grouped, editable SVG — a polygon engine for rectilinear and heiti glyphs, a cubic-Bezier engine for serif、kai and organic shapes, per-contour engine choice by measured fit error, subpixel contours taken from the 50%-coverage edge at 4x supersampling, and fidelity scored by rasterising the shipped SVG in a real renderer. Use when the user wants PNG 转 SVG、矢量化、描摹、轮廓提取、顶点或控制点坐标、图标或平色插画转矢量，or asks whether a photo can be vectorised."
metadata:
  author: ErgeAIA
  version: "0.1.0"
---

# raster-to-svg

Trace raster ink into vector contours, then prove the result with a renderer that is
not the tracer. It is a **contour tracer**: output is outlines, never selectable text.
If the original vector (font file, source SVG, design export) still exists, ask for it
before tracing anything.

## Scope

Use it for:

- a glyph / logotype / icon PNG that must become an editable SVG;
- extracting outline **vertex or cubic control-point coordinates**;
- flat-colour or limited-palette illustrations and icons (`--colors`);
- deciding whether a given photo *can* be vectorised (usually: no, see below).

Not for: OCR, font identification, recreating text as text, photographic fidelity.

## Runtime

`python3` + `numpy` + `opencv-python-headless`. A renderer is optional but required for
any fidelity claim: `resvg-py` (pip) or `rsvg-convert` (binary). Without one the tool
reports `surrogate_metric: true` and you must not quote the number.

```bash
uv run --with numpy --with opencv-python-headless --with resvg-py \
  python scripts/raster2svg.py -i in.png -o out --check
```

## Workflow

1. **Locate the source.** The image must exist as a file; if it only lives on a page,
   save it first. If a vector original exists, stop here and use that instead.
2. **Look at it once.** Ink polarity, flat vs continuous tone, rectilinear vs curved,
   smallest stroke width in pixels. Stroke width < 2 px will not survive tracing.
3. **Trace** with the default route:

   ```bash
   python scripts/raster2svg.py -i in.png -o out --check --title "源文件名"
   # flat-colour icon instead of ink:
   python scripts/raster2svg.py -i icon.png -o out --colors 6 --check
   ```

4. **Read three numbers** from stdout: `components`, `iou_rendered`, `ink_ratio`.
   - `iou_rendered >= 0.90` and `0.95 <= ink_ratio <= 1.05` → ship it.
   - `ink_ratio < 0.95` → ink is being lost: raise `--ss`, drop `--min-area`, set `--close 0`.
   - `ink_ratio > 1.05` → ink is being invented: lower `--error`, or force `--mode polygon`.
5. **Only tune what the numbers indict.** `<stem>_check.png` marks lost ink red and added
   ink green; read it before touching flags. Full parameter semantics: `references/parameters.md`.
6. **Deliver** `<stem>.svg` together with the numbers and `<stem>_check.png`. State the
   renderer used. If `surrogate_metric` is true, say the metric is a proxy.

## Engine routing

| Route | Meaning | Use it when |
| --- | --- | --- |
| `--mode auto` (default) | per contour: fit both engines, keep the one with the smaller max deviation (ties → fewer nodes) | always, first attempt |
| `--mode polygon` | line-only; corners snapped by adjacent-line intersection | rectilinear glyphs, machined logos, 黑体 |
| `--mode curve` | cubic Bézier (Schneider + Newton) | genuinely curved strokes only |
| `--colors K` | k-means colour layers, base rect + stacked paths | flat-colour art, never photos |

Colour mode in one paragraph: `K` is an **upper bound** — k-means spends clusters on
antialiasing fringe, so a small cluster within `--merge` (default 40 RGB) of a bigger one
is folded into it before tracing. Start at the number of visually distinct colours (6-8),
not at 32. `--ss` applies here too (it closes the half-pixel seams between adjacent
layers) and `--grow` (default 1 supersampled px) closes the rest. Verified colour PSNR:
30-37 dB on flat shape art and gradients, 24-25 dB once small text or antialiased edges
dominate; for dense UI screenshots `vtracer` scores 1-4 dB higher, so say so instead of
overclaiming.

Measured warning: forcing `curve` on rectilinear shapes (口/日/思源宋体) costs 15-40 IoU
points — a 口 at 96 px went 0.93 → 0.52 when forced to `curve`. Leave `auto` on unless
the user explicitly wants curves everywhere.

## Hard rules

- **Never quote a proxy metric as fidelity.** `surrogate_metric: true` means no renderer
  was present: report the SVG, not a score.
- **The metric must come from the shipped file.** `iou_rendered` rasterises `<stem>.svg`
  with resvg/rsvg. Do not substitute a re-render of the internal contours.
- **Do not promise photo vectorisation.** SVG regions are piecewise constant; a photo is
  continuous tone. `--colors` posterises. Offer: keep the raster, accept posterisation as
  a style, or embed the raster as `<image>` (not vector data).
- **Counters are holes, not shapes.** 口/日/回 keep their inner white area; the component
  path carries holes with `fill-rule="evenodd"`. Flat layers on top would fill them.
- **One `<g id>` per visual component.** Do not flatten the SVG to a single path; the
  point of the deliverable is that a human can still edit it.

## Output contract

Into `--outdir`:

| File | Content |
| --- | --- |
| `<stem>.svg` | `<g id="glyph-NN">` groups, one `<path fill-rule="evenodd">` per component (outer + holes), optional `<title>` |
| `<stem>_coords.json` | per component: engine, bbox, `vertices_xy` + `interior_angle_deg` or `cubic_segments`, `holes`, plus `iou_rendered` / `ink_ratio` / `renderer` / `surrogate_metric` |
| `<stem>_coords.txt` | the same table, human readable |
| `<stem>_check.png` | source \| render \| diff (red = lost ink, green = added) |
| `<stem>_overlay.png` | traced outline and node markers over the source |

## Exit codes

`0` traced (and `--check` passed) · `1` traced but `--check` failed or no renderer ·
`2` tool error (unreadable input, no contours above `--min-area`, renderer crash).

## Failure handling

| Symptom | Cause | Fix |
| --- | --- | --- |
| `cannot read image` | wrong path / unsupported container | re-locate the source; never reconstruct it |
| `no contours found` | `--min-area` above the smallest component | lower it; check the image is not blank |
| ink_ratio < 0.9 | thin strokes eaten by cleanup or by curve fitting | `--close 0`, lower `--min-area`, `--mode polygon` |
| counters filled | holes dropped before tracing | `--close 0`; holes are re-attached from `RETR_CCOMP` |
| banded colour trace | input is continuous tone | expected; describe the posterisation limit |
| corners rounded | `curve` forced | `--mode auto` |

## Evidence

Corpus, method, before/after numbers and what was *not* tested: `references/evidence.md`.
