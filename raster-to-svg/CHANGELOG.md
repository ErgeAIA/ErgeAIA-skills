# Changelog

本文件记录 raster-to-svg 的版本演进。格式遵循 Keep a Changelog，版本号三段式；
`SKILL.md` 的 `metadata.version` 与本文件顶部版本块必须一致。

## v0.1.0 (2026-11-22)

首次发布。初稿（`text-png-to-svg`）改为 `raster-to-svg`，并按实测证据重写核心。

### 新增

- 分组 SVG 输出：每个连通域一条 `<path fill-rule="evenodd">`（外轮廓 + 孔洞），按横向间距进 `<g id="glyph-NN">`，可选 `<title>`。
- `--ss`（默认 4）：边界取灰度 127.5 等值线，替代「阈值化像素外沿」。
- `--check` / `--min-iou` / `--min-psnr`：把保真度变成退出码闸门。
- `iou_rendered` / `ink_ratio` / `renderer` / `surrogate_metric`：验证走 resvg 或 rsvg-convert 渲染**输出文件**；无渲染器时如实降级并标注。
- `tests/`：10 条 unittest（CLI 门面、分组与孔洞、渲染 IoU 闸门、小点存活回归、确定性、彩色层数与高 K 不丢层）。
- `tests/tools/gen_colour_corpus.py`：8 图彩色语料（平色图标 ×2、孔洞图、徽章、UI 面板、密集 UI、线性渐变、径向渐变），纯 OpenCV 图元、确定性生成。
- 彩色模式抗锯齿小簇折叠：`--merge`（默认 40 RGB）/ `--merge-share`（默认 0.02），**K 是上界而非层数承诺**。
- `--grow`（默认 1 个超采样像素）：彩色层外扩以闭合层间缝隙。
- `references/parameters.md`、`references/evidence.md`。

### 变更

- 引擎路由：`auto` 从「角点角度占比」改为「逐轮廓比较两种拟合的最大偏差，偏差接近取节点少者」。实测 口 96px 强转曲线 IoU 0.93 → 0.52，故不再按字体一刀切。
- 默认值：`--min-area` 300 → 20（旧值会把 128px 下「之」的 189px² 点整块删除）；`--close` 2 → 0（闭运算会系统性加粗笔画）；`--max-snap` 按连通域短边 25% 自动收紧。
- 验证口径：不再用脚本内 `fillPoly` 重绘自证（旧口径报 0.93-1.00，同批 SVG 交给 resvg 实为 0.62-0.87）。
- `--ss` 现在对彩色模式同样生效（原先固定 1）：它不带来亚像素精度，但把层间半像素缝隙压掉，5 色图标 PSNR 26.8 → 36.5。
- 解耦运行时：删除 `/mnt/cos`、`/mnt/work`、`e2b_read_image`、`image_generate` 等宿主专属路径与工具，改为纯文件路径 + 可选渲染器。
- frontmatter：`name` 改为 `raster-to-svg`；删去非标 `title` / `when_to_use`，合并进双引号 `description`；补 `metadata.version`。

### 修复

- 半像素内缩导致的系统性掉墨（细笔画 ink 损失 10-25%）。
- 孔洞被逐 path 叠加填实：孔洞现与父轮廓同 path、靠 `fill-rule="evenodd"` 打穿。
- 退出码：输入不可读 / 无轮廓现返回 `2`（工具错误），与 `--check` 失败的 `1` 区分。
- 彩色模式把渲染结果转成灰度再算 PSNR：自报 16-24 dB，实际 30+（`icon_flat.png` K=6：16.9 → 34.5）。
- `K=12` 时抗锯齿边缘吃掉 10 个簇，真实形状丢层（3 色圆环只剩 1 层）—— 折叠规则修复。

### 验证

- 12 个真值字形语料（SimHei / SimSun / KaiTi / Noto Sans SC / 思源宋体 CN），resvg 渲染 IoU：均值 0.933、最差 0.894；同语料 vtracer polygon 均值 0.913、最差 0.856；本版 8/12 样本占优。
- `python -m unittest discover -s tests -v` → 8 tests OK。
- 确定性：mono 与 color 两次运行 SVG 字节一致。
- 彩色语料 8 图（resvg 渲染，源图 vs 输出）：K=6 口径本版均值 28.94 dB，vtracer 26.48 dB，5 胜 3 负；文件小 5-10 倍。落后项集中在文字密集 UI（1-4 dB），已写入能力边界。
