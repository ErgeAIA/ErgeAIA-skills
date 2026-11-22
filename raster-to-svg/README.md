# raster-to-svg

> 栅格描摹者，取其边以为线。直者还直，曲者还曲，成器而后可改。

**v0.1.0** · Agent Skill ｜ 位图 → 可编辑 SVG 轮廓追踪

把一张 PNG/JPG/WebP 描成可编辑的 SVG，并且用**真渲染器**证明它像——不是用描摹器自己的掩膜自证。

## 解决什么

「PNG 转 SVG」听起来是一个转换，实际是三件不同的事：保住直角、还原曲线、分出颜色。多数工具只在其中一件上像样：转出来的 SVG 要么是一个巨型单路径（没法编辑）、要么把 `口` 的内腔填成实心、要么为了贴边把细笔画削掉半个像素。

raster-to-svg 把这件事拆成可量的三步：

1. **边界从哪来**——读灰度的 50% 覆盖率等值线（4 倍超采样），而不是阈值化像素的外沿。后者天然内缩半像素，细笔画会整圈掉墨。
2. **用哪个引擎**——每条轮廓各拟合一次折线与曲线，按实测最大偏差选，直角与曲线可以同图共存。
3. **凭什么说像**——把**要交付的那个 SVG 文件**交给 resvg / rsvg-convert 栅格化，与源图比 IoU 与墨量比；渲染器不在场时明确标注 `surrogate_metric`，不许把代理分当保真度。

产出不是「一张图」，是**能改的矢量 + 可复算的数**。

## 快速开始

### 安装

```bash
npx skills add https://github.com/ErgeAIA/ErgeAIA-skills --skill raster-to-svg
```

### 前置条件

| 要做的事 | 要求 |
| --- | --- |
| 描摹（必需） | Python ≥ 3.10 + `numpy` + `opencv-python-headless` |
| 要一个可信的保真度数字 | `resvg-py`（pip）或 `rsvg-convert`（二进制），二选一 |
| 只要 SVG 不在乎数字 | 可以不装渲染器，但输出会标 `surrogate_metric: true` |

### 跑通一条

```bash
uv run --with numpy --with opencv-python-headless --with resvg-py \
  python scripts/raster2svg.py -i tests/fixtures/kou_96.png -o /tmp/out --check
```

stdout 三行是判据：`components`（几个字形）、`iou_rendered`（真渲染 IoU）、`ink_ratio`（墨量比）。

## 怎么用

| 场景 | 一句话要点 | 可复制示例提示词 |
| --- | --- | --- |
| 字/logo 转可编辑 SVG | 用默认 `auto`，看 ink_ratio 再决定调什么 | 「把这张字图描成 SVG，直角保持住，每个字一个组」 |
| 只要轮廓坐标 | 交付 `_coords.json`，别只给 SVG | 「导出这些字形的顶点坐标和内角，我要拿去重建」 |
| 平色图标转矢量 | `--colors 6` 起，逐层看 `_check.png` | 「这个图标转 SVG，颜色分 6 层，别把圆角啃掉」 |
| 判断照片能不能矢量化 | 先答「不能无损」，再给海报化或嵌图两条路 | 「这张照片能转成矢量吗？我要印刷级」 |
| 已有源文件时 | 有字体/原始 SVG 就不要描摹 | 「这是从 AI 导出的 PNG，但我有原始 SVG——还要描吗？」 |

## 能力边界（如实）

- **只出轮廓，不出文字**。不做 OCR、不认字体；想要可改的字，请回到字体与源文件。
- **照片不能无损矢量化**。SVG 区域是分段常色，照片是连续调；`--colors` 是海报化。三条路：留位图、接受海报化、嵌 `<image>`（不是矢量数据）。
- **细笔画有下限**。源图里笔画 < 2px 时，追踪结果会失真，先放大源图再说。
- **排版假设是横向单行**。`--gap` 按横向间距分组，竖排/多行/旋转未覆盖（见 `references/evidence.md` 第 6 节）。
- **彩色层不享受亚像素，但吃超采样**。`--colors` 追的是量化标签边界，没有抗锯齿可读；`--ss` 仍在生效，作用是把层间半像素缝隙压掉（实测 5 色图标 PSNR 26.8 → 36.5）。
- **文字密集的 UI 截图不是它的主场**。合成 8 图与 3 张真实页面（Chromium 渲染，900×560）都指向同一结论：本版落后 vtracer 1.3-3.5 dB。**换来的另一头**是 5-10 条路径 / 7-49 KB，而 vtracer 是 348-738 条路径 / 276-631 KB——要「像」选 vtracer，要「能改」选这里，要原样就留位图。
- **调大 K 不等于提精度**。真实截图上 K=12 常比 K=6 更差（`ui_browser` 22.37 → 20.02）：k-means 会把抗锯齿渐变切成薄层，薄层随后被面积与角点规则吃掉。

## 实测（12 个真值字形，resvg 渲染比 IoU）

| 工具 | IoU 均值 | IoU 最差 | 节点均值 |
| --- | --- | --- | --- |
| 初稿（polygon 默认） | 0.772 | 0.617 | 27 |
| 初稿（curve） | 0.533 | 0.295 | 25 |
| **本版（auto）** | **0.933** | **0.894** | **25** |
| vtracer 0.6.15 polygon | 0.913 | 0.856 | 35 |
| vtracer 0.6.15 spline | 0.912 | 0.852 | 50 |

彩色模式（8 图语料，PSNR / K=6）：平色图标 36.7、线条图标 30.1、孔洞图 33.1、渐变 28.3-28.9；徽章 24.4、UI 面板 24.4、密集 UI 25.4（后三者 vtracer 高 0.2-3.9 dB）。8 图均值本版 28.9 dB vs vtracer 26.5 dB，文件小 5-10 倍。

语料、方法、逐样本胜负与「明确没测的」都在 `references/evidence.md`。

## 文件地图

```
raster-to-svg/
├── SKILL.md                  Agent 执行规则
├── README.md                 本文件
├── CHANGELOG.md
├── references/
│   ├── parameters.md         参数语义、调参判据、别做的事
│   └── evidence.md           语料、指标、前后对照、未测项
├── scripts/raster2svg.py     追踪器（CLI）
└── tests/
    ├── test_raster2svg.py    8 条自检
    └── fixtures/             口 96 / 之 128 / 平色图标
```

## 版本

- **v0.1.0** — 首次发布。版本号在 `SKILL.md` 的 `metadata.version`、本文件、`CHANGELOG.md` 顶部三处对齐。
