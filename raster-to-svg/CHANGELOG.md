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
- `tests/`：unittest 覆盖 CLI 门面、分组与孔洞、渲染 IoU 闸门、小点存活回归、低对比墨、确定性、彩色层数与高 K 不丢层、文本输入、Unicode 路径、报告自包含、唯一 id（当前 16 条）。
- `tests/tools/gen_colour_corpus.py`：8 图彩色语料（平色图标 ×2、孔洞图、徽章、UI 面板、密集 UI、线性渐变、径向渐变），纯 OpenCV 图元、确定性生成。
- 彩色模式抗锯齿小簇折叠：`--merge`（默认 40 RGB）/ `--merge-share`（默认 0.02），**K 是上界而非层数承诺**。
- `--grow`（默认 1 个超采样像素）：彩色层外扩以闭合层间缝隙。
- `--text "开源" --font <ttf> --size 160`：不必先有图——按 4× 超采样渲染一行文字（Pillow），再走同一条描摹链；不传 `--font` 时找系统 CJK 字体。单行，竖向/多行不支持。
- `<name>.html` 自包含交互报告（默认生成，`--no-html` 关）：对比/源图/矢量/差异四视图、滚轮缩放与拖动平移、按部件开关、节点叠印、指标卡、坐标表悬停高亮、下载 SVG。无 CDN，图与 SVG 全部内联，双击即可看。
- 每个部件获得稳定 id（`cNN`），报告按 id 列层，不再出现「7 个同名 glyph-01」。
- `<name>_diff.png` 单独出图，供报告内嵌。
- `references/parameters.md`、`references/evidence.md`。

### 变更

- 引擎路由：`auto` 从「角点角度占比」改为「逐轮廓比较两种拟合的最大偏差，偏差接近取节点少者」。实测 口 96px 强转曲线 IoU 0.93 → 0.52，故不再按字体一刀切。
- 默认值：`--min-area` 300 → 20（旧值会把 128px 下「之」的 189px² 点整块删除）；`--close` 2 → 0（闭运算会系统性加粗笔画）；`--max-snap` 按连通域短边 25% 自动收紧。
- 验证口径：不再用脚本内 `fillPoly` 重绘自证（旧口径报 0.93-1.00，同批 SVG 交给 resvg 实为 0.62-0.87）。
- `--ss` 现在对彩色模式同样生效（原先固定 1）：它不带来亚像素精度，但把层间半像素缝隙压掉，5 色图标 K=6 PSNR 36.66 dB。
- 解耦运行时：删除 `/mnt/cos`、`/mnt/work`、`e2b_read_image`、`image_generate` 等宿主专属路径与工具，改为纯文件路径 + 可选渲染器。
- frontmatter：`name` 改为 `raster-to-svg`；删去非标 `title` / `when_to_use`，合并进双引号 `description`；补 `metadata.version`。

### 修复

- 非 ASCII 输入路径读不了：`cv2.imread`/`cv2.imwrite` 在 Windows 打不开「桌面/截图.png」，导致中文路径一律报 `cannot read image`（`--text` 生成的中文 stem 首当其冲）。改为 `np.fromfile + imdecode` / `imencode + tofile`，中文与空格路径均可。
- `--text` 的源图画布 4× 过大：字体 bbox 已经是超采样像素，又乘了一次 `ss`，文字缩在巨大的白底左上角。已改为紧凑画布（400×225 而非 1360×661）。
- 低对比墨一条轮廓都取不到：墨平面写死 127.5，`#999`（153）与 `#ccc`（204）全被判成纸色。改为 `ink_level()`——取纸色众数与墨芯（Otsu 分出的暗侧 5 分位）的中点；黑底白字仍是 127.5，低对比自动上移。`#999` 0.9399、`#ccc` 0.9354（potrace 同输入空输出），回归用例 `grey60_yong.png`。

- 半像素内缩导致的系统性掉墨（细笔画 ink 损失 10-25%）。
- 孔洞被逐 path 叠加填实：孔洞现与父轮廓同 path、靠 `fill-rule="evenodd"` 打穿。
- 退出码：输入不可读 / 无轮廓现返回 `2`（工具错误），与 `--check` 失败的 `1` 区分。
- 彩色模式把渲染结果转成灰度再算 PSNR：自报 16-24 dB，实际 30+（`icon_flat.png` K=6：16.9 → 34.5）。
- `K=12` 时抗锯齿边缘吃掉 10 个簇，真实形状丢层（3 色圆环只剩 1 层）—— 折叠规则修复。

### 验证

- **potrace 基线（官方 1.16）**：12 个真值字形 IoU 0.9570 / 最差 0.9184（本版 0.9329 / 0.8937），SSIM 0.9951（本版 0.9943），1-3 path / 708-1597 B，耗时 0.01-0.05 s。结论照实写：纯单色轮廓 potrace 更强，本技能的差异是分组、坐标表、低对比与彩色。
- **鲁棒性矩阵**：拉丁 0.9544（potrace 0.9705）、竖排 0.9638（vtracer 0.9822）、旋转 15° 0.8742（potrace 0.9549）、1600px 0.9935（potrace 0.9938，5.5 s vs 0.05 s）。
- **真实照片 K=16**：31.84 / 27.40 dB（vtracer 22.32 / 15.79），15 条 path vs 321-530 条。
- **被否掉的两次尝试**：外扩补半像素（0.9329→0.9136→0.8662）、收紧 dp-eps 到 0.8（均值 +0.5 点但最差退步、节点变多）。均未采用。

- 12 个真值字形语料（SimHei / SimSun / KaiTi / Noto Sans SC / 思源宋体 CN），resvg 渲染 IoU：均值 0.933、最差 0.894；同语料 vtracer polygon 均值 0.913、最差 0.856；本版 9/12 样本占优（另一负 -0.0004 实为平手）。
- `python -m unittest discover -s tests -v` → 16 tests OK（无渲染器时 3 条 skip）。
- 确定性：mono 与 color 两次运行 SVG 字节一致。
- 彩色语料 8 图（resvg 渲染，源图 vs 输出）：K=6 口径本版均值 28.91 dB，vtracer 26.48 dB，4 胜 4 负；文件小 5-10 倍。落后项集中在文字密集 UI（1-4 dB）与孔洞/徽章（0.2-1.1 dB），已写入能力边界。
- 彩色层固定走折线引擎并把角点位移收紧到 1.5 源像素：交给 `auto` 时会选曲线并撑开共享边界，5 色图标 36.66 → 19.88 dB（实测）。
