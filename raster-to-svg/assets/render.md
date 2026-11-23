# banner 渲染说明

`banner.svg` 是唯一真源，`banner.png` 由它渲染后裁切得到，`banner.json` 是编辑器可载入的结构化版本。
改字先改 SVG，再同步 JSON，最后重渲 PNG——三处不同步就会出现"图里是旧数字、JSON 里是新数字"。

## 渲染配方（照抄即可）

```bash
# 1) 用零边距页面包住 SVG，避免浏览器给图片加白边
#    page.html = <style>html,body{margin:0;padding:0;background:#1a0f0c;overflow:hidden}svg{display:block}</style> + banner.svg 内容
# 2) 按 560 高渲染，再裁到 400
chrome --headless=new --disable-gpu --hide-scrollbars \
  --window-size=1200,560 --virtual-time-budget=4000 \
  --screenshot=tall.png "file:///…/page.html"
# 3) 裁掉底部多余 160px（用 System.Drawing / PIL / magick 都行）
```

**为什么是 560 不是 400**：`--headless=new` 的内视口比 `--window-size` **矮约 80px**（模拟了浏览器
chrome）。按 400 渲只截到 y≈320，页脚、左下 L 形取景标记、右区图注会被裁掉——2026-11-23 就这么
裁过一次。探针可复现：在 y=380 画一条红色 rect，400 高截图里它根本不出现。

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
