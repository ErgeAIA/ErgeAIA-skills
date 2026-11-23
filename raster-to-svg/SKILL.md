---
name: raster-to-svg
description: "把位图（PNG、JPG、WebP）或口述的短词转成分组可编辑的 SVG 轮廓，并给出顶点/控制点坐标（单色）与真渲染器复核的保真分。Use when 用户要 PNG 转 SVG、矢量化、描摹、轮廓提取、顶点或控制点坐标、图标或平色插画转矢量、把几个字或一句短语做成 SVG 轮廓，或问照片能不能矢量化。"
metadata:
  author: ErgeAIA
  version: "0.1.0"
---

# raster-to-svg

把位图里的墨迹描成矢量轮廓，再用**不是追踪器的渲染器**复核结果。本技能是**轮廓追踪器**：
产物是轮廓，永远不是可选择文字。只要原始矢量（字体文件、源 SVG、设计稿导出）还在，先要来，
别描摹。

## 适用范围

用它做：

- **用户口述的短词或短句**（"把这几个字做成 SVG"）：用字体渲染（`--text`）再描，
  **绝不为打出来的字手画轮廓**；
- 字形 / 标志 / 图标 PNG 转可编辑 SVG；
- 提取轮廓的**顶点或三次控制点坐标**；
- 平色或有限色板的插画、图标（`--colors`）；
- 判断一张照片**能不能**矢量化（通常不能，见下）。

不适用：OCR、字体识别、把文字还原成文字、照片级保真。

## 两种模式一览

| | 单色（默认） | 彩色（`--colors K`） |
| --- | --- | --- |
| stdout 判据 | `components` / `iou_rendered` / `ink_ratio` | `layers` / `psnr_rendered`（无 iou、无 ink） |
| `--check` | iou ≥ 0.88 且 ink 0.95-1.05 | psnr ≥ 30 dB |
| SVG | `<g id="glyph-NN">` + `<path id="cNN">` | `<rect>` + 每层一条 path，**无分组、无 id** |
| 坐标 | `_coords.json` / `_coords.txt` | **无** |

用户同时要彩色**和**顶点坐标时，开工前就说清：本工具给不了两样，彩色层没有坐标表。

## 检查点（不可跳过）

| # | 标记 | 触发条件 | 你要做的 |
| --- | --- | --- | --- |
| 1 | 🛑 STOP | 存在原始矢量（字体文件、源 SVG、设计稿导出） | 向用户要来并停下；描摹已知矢量的位图严格更差 |
| 2 | 🔴 CHECKPOINT | 用户口述了字，且在意图形 | 开工前确认用哪个字体，并说明产物是轮廓不是可编辑文字 |
| 3 | 🔴 CHECKPOINT | 首次运行未过闸（`--check` 非零：iou < 0.88、ink 越界、或无渲染器） | 报三个数 + `_check.png` 读到的现象，**只改一个**参数，再报；禁止静默扫参数 |
| 4 | 🛑 STOP | 没装渲染器（`surrogate_metric: true`） | 交付 SVG，说明这个数是代理值，不得当保真度引用 |
| 5 | 🛑 STOP | 源是照片而用户说"无损" | 永不称照片描摹为无损；给三条路：留位图 / 接受海报化 / 嵌 `<image>`（嵌位图不算矢量数据） |

这些是闸门不是建议——越过任何一条，产出的是**错答案**，不是差一点的答案。

## 运行环境

`python` + `numpy` + `opencv-python-headless` + `pillow`（渲染器解码走 PIL，所以 `--check`
也需要它；缺了就只剩代理值，没有分）。渲染器可选，但任何保真声明都需要它：
`resvg-py`（pip）或 `rsvg-convert`（二进制）。都没有时工具报 `surrogate_metric: true`，
不得引用那个数。非 ASCII 路径（桌面/截图.png）可用。

```bash
uv run --with numpy --with opencv-python-headless --with pillow --with resvg-py \
  python scripts/raster2svg.py -i in.png -o out --check
```

## 工作流

1. **定位源。** 图必须落成文件；只在网页上就先存下来。**🛑 STOP**：有原始矢量就去要（检查点 1）。
2. **看一眼。** 墨的极性、平色还是连续调、直角还是曲线、最小笔画宽度（px）。笔画 < 2 px 描不出来。
3. **描摹**，默认路线：

   ```bash
   # 口述的字——不需要图
   python scripts/raster2svg.py --text "开源" --font /path/NotoSansSC.ttf --size 160 -o out
   # 一张图
   python scripts/raster2svg.py -i in.png -o out --check --title "源文件名"
   # 平色图标（不走墨）
   python scripts/raster2svg.py -i icon.png -o out --colors 6 --check
   ```

   `--text` 按 4 倍渲染一行字再盒式降采样，所以墨边界是真实的栅格化结果。用户口述了字、
   且在意图形时 **🔴 CHECKPOINT**：确认字体，并说明交付物是轮廓不是可编辑文字（检查点 2）。
   不传 `--font` 时默认用系统 CJK 字体。只支持单行——竖排与多行不支持。

4. **读三个数**（stdout）：`components`、`iou_rendered`、`ink_ratio`。
   - `--check` 退出 0（即 `iou_rendered ≥ 0.88` **且** `0.95 ≤ ink_ratio ≤ 1.05`）→ 交付。
     0.90 是高精度目标，不是出货线：语料最差样本就是 0.8937，写 0.90 会否掉本工具自己的证据。
   - `ink_ratio < 0.95`（丢墨）→ **按顺序一次改一个**：`--min-area 10` → `--close 0` → `--ss 6`。
   - `ink_ratio > 1.05`（多墨）→ 一次改一个：`--error 0.8` → `--mode polygon`。
   每次只改一处，重跑，再报数（检查点 3）。
5. **只调被数字指认的参数**（检查点 3）：先读 `<stem>_check.png`（红 = 丢墨，绿 = 多墨），
   再动参数；一次一个，改完再报。参数语义见 `references/parameters.md`。
6. **交付** `<stem>.svg` + 三个数 + `<stem>_check.png`，写明用的渲染器。
   `surrogate_metric` 为真时 **🛑 STOP**：给文件，说清这个数是代理值，别包装成保真度（检查点 4）。

## 引擎路由

| 路线 | 含义 | 什么时候用 |
| --- | --- | --- |
| `--mode auto`（默认） | 逐条轮廓两个引擎各拟合一次，取最大偏差更小者（接近时取节点少者） | 永远先试这个 |
| `--mode polygon` | 只走直线；角点由相邻直线求交吸附 | 矩形字形、机械感标志、黑体 |
| `--mode curve` | 三次贝塞尔（Schneider + Newton） | 只用于确实弯曲的笔画 |
| `--colors K` | k-means 分色层，底 rect + 叠层 path | 平色插画；**不要用于照片** |

彩色路线：`K` 是**上界**，从视觉上能数出的颜色数起（6-8），别从 32 起；抬高 K 不会在真实 UI 上
买到保真。K=6 时真实 UI 页的文字会**碎成块**（3 页语料上目视观察；§8 记的是 PSNR 差距，不是
可读性）——文字密集的源是**选错路线**，不是调参问题。源是真实 UI 时，要明说本版比 vtracer 低
1-4 dB。数字与取舍见 `references/evidence.md` §7-§8。

不要在矩形字形上强推 `--mode curve`：已测的唯一一个样本（96 px 口）从 0.93 掉到 0.52，
即 41 个 IoU 点。

## 工具选型（要明说，不要猜）

- **纯单色轮廓、高对比、机器上有 potrace** → potrace 在保真度与速度上更强（数字见
  `references/evidence.md` §9.1）。用本技能，是因为用户需要 potrace 给不了的东西：
  分组可编辑的 SVG、坐标表、彩色分层，或低对比墨（potrace 固定按 0.5 阈值切，
  对 `#999` 灰字**输出空文件**；本工具能描）。
- **必须保持可读的抗锯齿小字** → 本工具的彩色模式与任何海报化追踪器都不行；
  留位图，或直说文字会碎。

## 不要做（红灯）

- **绝不覆盖或删除用户的源图。** 只往 `--outdir` 写。
- **绝不手改 `_coords.json` 里的坐标**，也绝不为了凑过指标凭空补点。
- **绝不在没有真渲染器 `--check` 数字时声称保真**；代理值不是分数。
- **绝不把照片描摹称为"无损矢量化"。** 海报化是风格，不是保真。
- **绝不把 vtracer 或 potrace 的分数当成本工具的成绩。** 只引本工具自己的语料。
- **绝不输出 `<text>`。** 产物是轮廓；可编辑文字要用字体，不是描摹。
- **绝不先放大源图**再声称"高精度"——要改就改 SVG 的 `width`/`height` 属性，
  `viewBox` 本来就带着真实几何。
- **绝不交付分组错乱的竖排、旋转或多行结果。** `--gap` 是横向间隙启发式；
  交付前量一下分组，并说明哪部分不支持。
- **绝不把内部轮廓重绘当成指标。** `iou_rendered` 渲染的是交付的 `<stem>.svg`；
  换一个重绘不是同一个声明。
- **绝不把 SVG 拍平成一条 path。** 每个视觉部件一个 `<g id>` 才是交付物的意义；
  孔洞靠 `fill-rule="evenodd"` 保持为孔。

## 产物契约

写入 `--outdir`：

| 文件 | 内容 |
| --- | --- |
| `<stem>.svg` | `<g id="glyph-NN">` 分组，每个部件一条 `<path id="cNN" fill-rule="evenodd">`（外轮廓 + 孔洞），可选 `<title>` |
| `<stem>.html`（`--no-html` 可关） | **自包含交互报告**（无 CDN，图内联）：缩放平移、对比/源图/矢量/差异四视图、按部件显隐、节点叠印、指标卡、悬停高亮的坐标表 |
| `<stem>_coords.json` / `.txt` | **仅单色**：逐部件的引擎、bbox、`vertices_xy` + `interior_angle_deg` 或 `cubic_segments`、`holes`，外加 `iou_rendered` / `ink_ratio` / `renderer` / `surrogate_metric`；`.txt` 是同一张表的人读版 |
| `<stem>_check.png` | 单色：源图 \| 渲染 \| 差异（红 = 丢墨，绿 = 多墨）；彩色：只有源图 \| 渲染 |
| `<stem>_diff.png` | **仅单色**：差异图，嵌在报告里 |
| `<stem>_source.png` | 仅 `--text`：被描的那张字图 |
| `<stem>_overlay.png` | **仅单色**：轮廓与节点叠在源图上 |

## 退出码

`0` 已描摹（带 `--check` 时表示通过）· `1` `--check` 未通过（iou、ink_ratio，或无渲染器）·
`2` 工具错误（读不了输入、`--min-area` 之上没有轮廓、渲染器崩溃）。

## 失败处理

症状 → 原因 → 修法表：`references/parameters.md` §故障；调参顺序规则：同文件 §判据。
两条不得临场发挥：`cannot read image` → 重新定位源文件（绝不凭记忆重建）；
`no contours found` → 先确认图不是空白，再降 `--min-area`。

## 证据

语料、方法、前后对比数字与**明确没测的**：`references/evidence.md`。
