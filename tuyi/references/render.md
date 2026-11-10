---
name: render
description: 渲染页的模块、视觉约束、case 结构与验收方法：单文件离线、双主题、灰度、真实行上下文、候选对比与混淆矩阵。
version: 1.0.0
trigger-when:
  - 要生成选型结论的 HTML 预览页
  - 要验收渲染页是否达标
  - 需要写 case.yaml
---

# 渲染页

渲染页的作用：让人在 30 秒内确认「这枚图标在真实尺寸、真实邻居、灰度、两套主题下都成立」。它不是作品集，不许放大美化。

## 必需模块

按顺序排，缺一个都算未完成：

1. **结论头**：槽位 / 首选 id / 尺寸 / 色令牌 / Tooltip 原文 / 一句话理由
2. **尺寸阶梯**：12 / 16 / 18 / 20 / 24 五档并排，标明哪档是本例的适用尺寸（其余是「若换槽位会怎样」的参照）
3. **双主题**：浅色与深色各一组，同尺寸同上下文
4. **灰度**：整页可切灰度，验证形状区分度
5. **真实行上下文**：把图标放进 3–6 个真实邻居里（同尺寸、同间距、同对齐），展示"扫视时会不会混"
6. **候选对比**：每个候选一行，含图标、id、命中 tags、16px IoU（对首选）、被排除理由
7. **混淆矩阵**：候选两两 IoU 表格，> 0.75 的格子标红
8. **规格块**：可直接复制的结论（id、尺寸、stroke、色令牌、Tooltip、示例代码片段）

## 约束

| 项 | 要求 |
| --- | --- |
| 文件 | 单个 HTML，双击可开，**零外部请求**（无 CDN、无外链字体、无远程图片） |
| 图标 | 内联 `<svg>`，来自真实图标数据，不手写路径 |
| 颜色 | 全部走 CSS 变量；页面内不出现字面色值（`#xxx`/`rgb()` 只允许出现在 `:root` 的变量定义里） |
| 主题 | `html[data-theme="light"|"dark"]` 切换，切完不许有硬编码色残留 |
| 宽度 | 1440×950 视口下**无横向滚动**（`document.scrollWidth <= innerWidth`） |
| 动效 | 无必要动效；若有，遵守 `prefers-reduced-motion` |
| 无障碍 | 图标按钮有 `aria-label`；纯装饰图标 `aria-hidden="true"` |

## case.yaml

照 `templates/case.example.yaml` 写：

```yaml
title: 本地插件 · 来源徽章
slot: source
intent: 标注这个插件是本机手动安装的，不是从远端仓库拉的
size: 16
stroke: 2.25
color: text-muted
tooltip: 手动安装，未关联仓库
primary: hard-drive
alternatives:
  - id: package-open
    why: 与安装/仓库族形成对照
    cost: package 家族 16px 下易混
rejected:
  - id: unlink
    why: 借用断连语义，正常状态被读成故障
  - id: folder-input
    why: 动词性图形，状态位会读成「导入」
neighbors: [git-fork, external-link, trash-2, star]
context_line: 本地插件 · 已安装 · 3 个文件
```

## 生成

```bash
PYTHONIOENCODING=utf-8 uv run --no-project python scripts/iconlab.py render --case case.yaml --out badge.html
```

## 验收

生成不算完，跑完这三步才算：

1. **溢出**：headless 打开 1440×950，读 `document.documentElement.scrollWidth` 与 `innerWidth`，前者不得大于后者
2. **主题**：分别切 `light`/`dark` 截图，检查有无硬编码色导致的「切主题不跟着变」的区块
3. **灰度**：切灰度截图，看状态图标之间是否还分得开

```bash
"C:/Program Files/Google/Chrome/Application/chrome.exe" --headless --disable-gpu --window-size=1440,950 --screenshot=shot.png "file:///<abs>/badge.html"
```

截图要看得见结论头与混淆矩阵——只截首屏、看不到证据，等于没验收。

## 反例

- 把 24px 大图当主视觉，16px 缩在角落
- 只展示首选，不展示被排除的候选
- 用彩色圆角卡片衬托徽章（衬托会掩盖 16px 下的真实观感）
- 用 CDN 的 lucide 脚本（离线打不开，且版本不受控）
- 颜色写死在样式里，深色主题靠 filter 硬转

## 自检

- 八个模块齐
- 无外部请求、无字面色值外泄
- 1440×950 无横向滚动
- 双主题 + 灰度都验过
- 规格块能直接复制粘贴使用
