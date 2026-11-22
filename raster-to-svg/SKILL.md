---
name: raster-to-svg
description: "Turns a raster image (PNG、JPG、WebP) or a typed short phrase into a grouped, editable SVG outline set, with vertex or cubic control-point coordinates (mono) and a fidelity number from rasterising the shipped SVG in a real renderer. Use when the user wants PNG 转 SVG、矢量化、描摹、轮廓提取、顶点或控制点坐标、图标或平色插画转矢量、把几个字或一句短语做成 SVG 轮廓，or asks whether a photo can be vectorised."
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

- **a word or short line** the user typed ("把这几个字做成 SVG"): render it with a font
  (`--text`) and trace that - never hand-draw outlines for typed text;
- a glyph / logotype / icon PNG that must become an editable SVG;
- extracting outline **vertex or cubic control-point coordinates**;
- flat-colour or limited-palette illustrations and icons (`--colors`);
- deciding whether a given photo *can* be vectorised (usually: no, see below).

Not for: OCR, font identification, recreating text as text, photographic fidelity.

## Modes at a glance

| | mono (default) | colour (`--colors K`) |
| --- | --- | --- |
| stdout gate | `components` / `iou_rendered` / `ink_ratio` | `layers` / `psnr_rendered` (no iou, no ink ratio) |
| `--check` | iou >= 0.88 and ink 0.95-1.05 | psnr >= 30 dB |
| SVG | `<g id="glyph-NN">` + `<path id="cNN">` | `<rect>` + one path per layer, **no groups, no ids** |
| coordinates | `_coords.json` / `_coords.txt` | **none** |

If the user asks for colour **and** vertex coordinates, say up front that this tool cannot
give both: colour layers have no coordinate table.

## Checkpoints (do not skip)

| # | Marker | Fires when | What you do |
| --- | --- | --- | --- |
| 1 | 🛑 STOP | a vector original exists (font file, source SVG, design export) | ask the user for it and stop; tracing a raster of a known vector is strictly worse |
| 2 | 🔴 CHECKPOINT | the user typed the words and cares about the shape | confirm which font (and that the output is outlines, not editable text) before running |
| 3 | 🔴 CHECKPOINT | the first run misses the gate (`--check` non-zero: iou < 0.88, ink outside 0.95-1.05, or no renderer) | show the three numbers + the `_check.png` reading, change **one** parameter, report again; do not silently sweep flags |
| 4 | 🛑 STOP | no renderer is installed (`surrogate_metric: true`) | deliver the SVG, say the number is a proxy, do not quote it as fidelity |
| 5 | 🛑 STOP | the source is a photograph the user calls "lossless" | never call a photo trace lossless; offer raster / posterisation / `<image>` (an embedded bitmap is not vector data) |

These are gates, not advice - crossing one produces a wrong answer, not a worse one.

## Runtime

`python` + `numpy` + `opencv-python-headless` + `pillow` (the renderer path decodes with
PIL, so `--check` needs it too - without it you get a proxy warning, not a score).
A renderer is optional but required for any fidelity claim: `resvg-py` (pip) or
`rsvg-convert` (binary). Without one the tool reports `surrogate_metric: true` and you
must not quote the number. Non-ASCII input paths (桌面/截图.png) are fine.

```bash
uv run --with numpy --with opencv-python-headless --with resvg-py \
  python scripts/raster2svg.py -i in.png -o out --check
```

## Workflow

1. **Locate the source.** The image must exist as a file; if it only lives on a page,
   save it first. **🛑 STOP** if a vector original exists - ask for it (checkpoint 1).
2. **Look at it once.** Ink polarity, flat vs continuous tone, rectilinear vs curved,
   smallest stroke width in pixels. Stroke width < 2 px will not survive tracing.
3. **Trace** with the default route:

   ```bash
   # typed words - no image needed
   python scripts/raster2svg.py --text "开源" --font /path/NotoSansSC.ttf --size 160 -o out
   # an image
   python scripts/raster2svg.py -i in.png -o out --check --title "源文件名"
   # flat-colour icon instead of ink:
   python scripts/raster2svg.py -i icon.png -o out --colors 6 --check
   ```

   `--text` renders one line at 4x and box-filters down, so the ink boundary is a real
   rasterisation. **🔴 CHECKPOINT** when the user typed the words and the shape matters:
   confirm the font, and say the deliverable is outlines, not selectable text (checkpoint 2).
   Default font when none is given: a system CJK font (override with `--font`).
   One line only - vertical or multi-line layout is not supported.

4. **Read three numbers** from stdout: `components`, `iou_rendered`, `ink_ratio`.
   - `--check` exit 0 (that means `iou_rendered >= 0.88` **and** `0.95 <= ink_ratio <= 1.05`)
     → ship it. 0.90 is the high-precision target, not the ship line: the corpus minimum is
     0.8937, so a 0.90 gate would fail this tool's own evidence.
   - `ink_ratio < 0.95` (ink lost) → try, **one at a time in this order**: `--min-area 10` →
     `--close 0` → `--ss 6`.
   - `ink_ratio > 1.05` (ink invented) → try, one at a time: `--error 0.8` → `--mode polygon`.
   Apply a single change, re-run, report the numbers again (checkpoint 3).
5. **Tune only what the numbers indict** (checkpoint 3): read `<stem>_check.png` (red = lost
   ink, green = added) before touching a flag, change one parameter, report again.
   Semantics: `references/parameters.md`.
6. **Deliver** `<stem>.svg` together with the numbers and `<stem>_check.png`. State the
   renderer used. **🛑 STOP** if `surrogate_metric` is true: hand over the file and say the
   number is a proxy - do not dress it as fidelity (checkpoint 4).

## Engine routing

| Route | Meaning | Use it when |
| --- | --- | --- |
| `--mode auto` (default) | per contour: fit both engines, keep the one with the smaller max deviation (ties → fewer nodes) | always, first attempt |
| `--mode polygon` | line-only; corners snapped by adjacent-line intersection | rectilinear glyphs, machined logos, 黑体 |
| `--mode curve` | cubic Bézier (Schneider + Newton) | genuinely curved strokes only |
| `--colors K` | k-means colour layers, base rect + stacked paths | flat-colour art, never photos |

Colour routing: `K` is an upper bound, start at the number of visually distinct colours
(6-8), never 32; raising K does not buy fidelity on real UI. At K=6 a real UI page's text visually
breaks into blocks (observed on the 3-page corpus; §8 records the PSNR deficit, not the
readability) - text-dense sources are the wrong route, not a tuning problem.
When the source is real UI, say out loud that this trace is 1-4 dB behind vtracer. Numbers and
trade-offs: `references/evidence.md` §7-§8.

Do not force `--mode curve` on rectilinear shapes: on the one sample measured (96 px 口) it
went 0.93 → 0.52, i.e. 41 IoU points.

## Tool choice (state it, do not guess)

- **Pure mono outline, high contrast, potrace available** → potrace wins on fidelity and
  speed (numbers: `references/evidence.md` §9.1). Use this skill when the user needs what
  potrace cannot emit: grouped editable SVG, coordinate tables, colour layers, or low-contrast
  ink (potrace's fixed 0.5 threshold returns an empty file on #999 text; this tool traces it).
- **Anti-aliased small text that must stay readable** → neither colour mode here nor a
  posterising tracer; keep the raster or say the text will break.

## Do not (red lines)

- **Never overwrite or delete the user's source image.** Write only into `--outdir`.
- **Never hand-edit coordinates** in `_coords.json`, and never invent points to make a metric pass.
- **Never claim fidelity without a `--check` number from a real renderer**; a proxy is not a score.
- **Never call a photo trace "vectorised without loss".** Posterisation is a style, not fidelity.
- **Never quote vtracer's or potrace's scores as this tool's result.** Use this tool's own corpus.
- **Never emit `<text>`.** Output is outlines; editable text needs the font, not a trace.
- **Never upscale the source** and then report "high precision" - set the SVG `width`/`height`
  attributes instead; `viewBox` already carries the real geometry.
- **Never ship a vertical, rotated or multi-line result whose grouping is wrong.** `--gap`
  is an x-gap heuristic; measure the groups before delivering, and say what is unsupported.
- **Never re-render the internal contours and call it the metric.** `iou_rendered` rasterises
  the shipped `<stem>.svg`; a substitute is not the same claim.
- **Never flatten the SVG to one path.** One `<g id>` per visual component is the point of
  the deliverable; counters stay holes via `fill-rule="evenodd"`.

## Output contract

Into `--outdir`:

| File | Content |
| --- | --- |
| `<stem>.svg` | `<g id="glyph-NN">` groups, one `<path id="cNN" fill-rule="evenodd">` per component (outer + holes), optional `<title>` |
| `<stem>.html` (`--no-html` to skip) | **self-contained interactive report** (no CDN, images inlined): zoom/pan, 对比/源图/矢量/差异 views, per-component visibility toggles, node overlay, metrics cards, coordinate table that highlights the path on hover |
| `<stem>_coords.json` / `.txt` | **mono only**: per component engine, bbox, `vertices_xy` + `interior_angle_deg` or `cubic_segments`, `holes`, plus `iou_rendered` / `ink_ratio` / `renderer` / `surrogate_metric`; the `.txt` is the same table human-readable |
| `<stem>_check.png` | mono: source \| render \| diff (red = lost ink, green = added); colour: source \| render only |
| `<stem>_diff.png` | **mono only**: the diff plate, embedded in the report |
| `<stem>_source.png` | `--text` only: the rasterised text that was traced |
| `<stem>_overlay.png` | **mono only**: traced outline and node markers over the source |

## Exit codes

`0` traced (with `--check`: passed) · `1` `--check` failed (iou, ink_ratio, or no renderer) ·
`2` tool error (unreadable input, no contours above `--min-area`, renderer crash).

## Failure handling

Symptom → cause → fix table: `references/parameters.md` §故障; ordering rules: §判据.
Two that must not be improvised: `cannot read image` → re-locate the source (never
reconstruct it); `no contours found` → check the image is not blank before lowering `--min-area`.

## Evidence

Corpus, method, before/after numbers and what was *not* tested: `references/evidence.md`.
