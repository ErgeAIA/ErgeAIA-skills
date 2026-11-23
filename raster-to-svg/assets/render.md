# banner 渲染说明

`banner.svg` 是唯一真源，`banner.png` 由它渲染后裁切得到，`banner.json` 是编辑器可载入的结构化版本。
改字先改 SVG，再同步 JSON，最后重渲 PNG——三处不同步就会出现"图里是旧数字、JSON 里是新数字"。

## 重新生成 PNG

一条命令，`shot.ps1` 负责零边距包装、多留高度、按内容裁切、越界报警：

```powershell
cd assets
pwsh -File shot.ps1 -In banner.svg -Width 1200 -Height 400 -Out banner.png -Bg "#1a0f0c"
```

- `-Height 0` = 自动高度（按最后一行内容 + 24px 裁），用于长短不一的页面截图；
- 固定 `-Height` = 画布尺寸（banner 就是 400），内容超出会**报警退出 1**，而不是静默裁掉；
- Chromium 走 `-Chrome` / `CHROME` 环境变量 / Playwright 缓存目录，三者都找不到才报错。

**这脚本为什么存在**：`--headless=new` 的内视口比 `--window-size` **矮约 80px**，按目标高度直接截图
会裁掉底部——2026-11-23 banner 的页脚、L 形取景标记、右区图注就是这么丢的。探针可复现：在 y=380
画一条红 rect，400 高的截图里它根本不出现。

## 图里的数字从哪来

| banner 上的字 | 值 | 出处 |
| --- | --- | --- |
| IoU | 0.933 | `references/evidence.md` §3「本版 `--mode auto`」0.9329 |
| 节点/字形 | 25 | 同表「节点均值」25 |
| SVG 体积 | 765 B | 同表「文件均值」765 B |
| 语料 | 12 字形真值语料 | §1 语料表（SimHei / SimSun / KaiTi / Noto Sans SC / 思源宋体 CN） |

改语料或改默认参数后，这四个数都要重算，并同时改 SVG 里 4 处、JSON 里 1 处。

## 交付前自检

- [ ] XML 合法：`python -c "import xml.etree.ElementTree as ET;ET.parse('banner.svg')"`
- [ ] PNG 是 1200×400，且四角都有内容：左上类目标签、左下 L 形标记 + 页脚、右下右区图注
- [ ] 右区元素 x ≤ 1160，内容底 y ≤ 340，图注在 y=358 不撞内容
- [ ] 缩小到 128px 宽，标题与四步仍能认出
- [ ] `banner.json` 的 `meta.render` 与 `meta.source` 仍准确
