---
trigger-when: "被问「这个数凭什么」「和 vtracer/potrace 比怎么样」「改之前是什么水平」，或要复算/扩充语料时"
name: evidence
description: "raster-to-svg 的验证记录：12 个字形的真值闭环语料、真渲染器 IoU 前后对照、与 vtracer 的逐样本比较、确定性实测，以及明确未测的部分。"
---

# 验证记录（evidence）

所有数字来自本机实际运行（Windows 11，Python 3.12.9，opencv-python-headless 5.1.0.95，resvg-py 0.5.0）。语料与脚本在 `tests/fixtures`，复算步骤见文末。

## 1. 语料：真值已知，不是随手找的图

12 个字形，从本机字体文件用 FreeType 渲染（4× 超采样后面积降采样），因此**原始轮廓可精确取得**：

| 字体 | 字形 | 字号（em px） |
| --- | --- | --- |
| SimHei | 永 / 口 / 日 / 口 | 128 / 128 / 96 / 48 |
| SimSun | 永 / 口 / 日 / 的 | 128 / 96 / 96 / 96 |
| KaiTi | 永 / 之 | 128 / 128 |
| Noto Sans SC | 口 | 128 |
| 思源宋体 CN | 日 | 96 |

选字理由：口/日 测直角与孔洞，永 测多笔画与分离点，之 测小连通域，的 测复杂多轮廓，48px 测细笔画下限。

## 2. 指标定义（两层，别混用）

- **真值层**：追踪结果到「字体轮廓」的 Chamfer / Hausdorff（px）。用于判断引擎本身的几何误差；含 0.14-0.48px 的栅格化下限（FreeType hinting + 抗锯齿阈值），因此不应期望 0。
- **交付层（对外只引用这一层）**：把**输出的 SVG 文件**交给 resvg 栅格化，与源图在 **127.5（50% 覆盖率）** 处二值化后算 IoU 与 ink_ratio。这是用户实际看到的结果。

## 3. 前后对照（同一语料，12 样本，resvg 渲染）

| 版本 / 工具 | IoU 均值 | IoU 最差 | SSIM 均值 | 节点均值 | 文件均值 |
| --- | --- | --- | --- | --- | --- |
| 初稿 `--mode polygon`（默认） | 0.7716 | 0.6166 | 0.9822 | 27 | 497 B |
| 初稿 `--mode polygon`（调参：close 0 / min-area 20） | 0.7948 | 0.6180 | 0.9837 | 42 | 636 B |
| 初稿 `--mode curve`（调参） | 0.5332 | 0.2946 | 0.9618 | 25 | 986 B |
| **本版 `--mode auto`** | **0.9329** | **0.8937** | **0.9943** | **25** | **765 B** |
| vtracer 0.6.15 `polygon` | 0.9127 | 0.8560 | 0.9909 | 35 | 517 B |
| vtracer 0.6.15 `spline` | 0.9124 | 0.8521 | 0.9905 | 50 | 4093 B |

逐样本胜负：本版胜 8 / 12（vs vtracer polygon），平 0，负 3（notosans 口 -0.055、思源宋体 日 -0.008、simhei 口 -0.0004）。
本版节点更少（25 vs 35）但文件更大（765 B vs 517 B）：坐标保留两位小数、带 `<g id>` 与注释。

## 4. 初稿的四个实测缺陷（本版已修）

1. **半像素内缩**：`findContours` 沿外层像素中心走，填充成 SVG 后整体比真边界小约 0.5px，细笔画 ink 掉 10-25%。→ 改为读灰度 127.5 等值线（`--ss` 4）。
2. **默认 `--min-area 300` 删字**：128px 下「之」的点 189px² 被整块删除（2 连通域 → 1）。→ 默认 20，并有回归用例。
3. **`curve` 强路由撑坏直角**：口 96px 强转曲线后 IoU 0.93 → 0.52，ink 涨到 1.21 倍（外凸）。→ `auto` 改为按拟合最大偏差逐轮廓选择。
4. **自评分乐观**：初稿 IoU 用 Otsu 掩膜 + fillPoly 重绘，报 0.93-1.00；同一批 SVG 交给 resvg 只有 0.62-0.87。→ 验证改为「渲染输出的 SVG + 127.5 阈值」，且渲染器缺席时标 `surrogate_metric: true`。

## 5. 确定性

- mono：同一输入两次运行，SVG 字节相同（sha256 一致）。
- color：`cv2.setRNGSeed(0)` 后两次运行字节相同；不设种子时 k-means 初值随进程 RNG 状态走，不保证跨机器可复现。

## 6. 明确未测

- 真实照片、JPEG 压缩伪影、渐变图标、重叠色层（`--colors` 仅一个 5 色图标的冒烟测试，未做 PSNR 全表）。
- 非汉字书写系统（拉丁/阿拉伯/天城文）、竖排、旋转、多行排版（`--gap` 仍是横向启发式）。
- 超大图（>4000px）与 `--ss 8` 的时间/内存。
- 与 potrace / autotrace 的对照：本机 potracer 0.0.4 无 SVG 导出，未取得基线，因此表中只有 vtracer（不得用推断补空）。
- 跨 resvg 版本的栅格化差异。

## 7. 复算

```bash
# 单样本
uv run --with numpy --with opencv-python-headless --with resvg-py \
  python scripts/raster2svg.py -i tests/fixtures/kou_96.png -o out --check --mode auto
# 回归
uv run --with numpy --with opencv-python-headless --with resvg-py \
  python -m unittest discover -s tests -v
```
