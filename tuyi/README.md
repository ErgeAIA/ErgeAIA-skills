# 图意 · Tuyi

> 图意者，辨图之所指，定其位而择其形。徽章之选，先明其意，而后取象。

> **版本：1.1.0** ｜ 版本记录见 [CHANGELOG.md](./CHANGELOG.md)（顶部即最新）。

把徽章图标从审美偏好变成可复核的判定：先判槽位，再查既有映射，从真实图标库检索候选，给出首选、备选与排除理由，并输出离线 HTML 对照页；也能按设计规范审查已有徽章。流程与判据见 [SKILL.md](./SKILL.md)，本文件只留入口与用法。

## 怎么用（场景 × 示例提示词）

| 能力 / 场景 | 一句话方法 | 示例提示词 |
| --- | --- | --- |
| **徽章选型**（含歧义处理） | 判槽位 → 查 locked 映射 → 真实 tags 检索 → 四类排除 → 三档结论 + IoU 数据 | "给「本地插件」配个徽章图标，它是来源标记，不是状态"; "hard-drive/package-open/folder-input 哪个适合「本地」？我要 16px 的轮廓差异" |
| **候选对比** | 明确给出备选理由与代价评估 | "为什么 hard-drive-download 不推荐？它会不会被读成下载？" |
| **审查已有徽章系统** | 按 profile 规范扫描 HTML/CSS/TSX | "审一下我们技能库里徽章用法，哪些违反状态图标规范"; "帮我看看 iconography.md:23 的尺寸有没有被执行" |
| **生成预览页** | 基于 case.yaml 输出带混淆矩阵的单页 HTML | "把这个结论渲染成 html，我要看双主题和灰度"; "用 case.local-plugin.yaml 生成本地徽章页" |
| **从规范建 rulebook** | 抽取条款转可执行 check，登记冲突与 interim | "按 docs/design/iconography.md 生成一份 profile，冲突单独登记" |
| **判断该不该加动效** | 先走静态优先五问，任一不成立即静态；确需动画才在六形态里选一种，并给目标、触发、停止与 reduce | "这个「同步中」的徽章要不要加旋转？"; "未读状态图标加个呼吸效果合适吗" |
| **审查已有徽章动效** | 查语义是否错位、有无真实触发、循环能否终止、结束/卸载是否停、预算与令牌、reduce 是否降级 | "审一下这个徽章的旋转，任务结束会不会停不下来"; "这个心跳在 reduced-motion 下会关掉吗" |
| **边界确认** | 识别不归本技能的需求（画新图标/纯排版），如实路由说明 | "帮我画一个自定义 SVG 图标"（不归 tuyi）; "这个徽章的内边距调多少好看"（不归 tuyi） |

## 判据索引

- 六槽本体与每槽禁忌 → [references/slot-model.md](./references/slot-model.md)
- 选型五步与第 6 步动效判定、排除项、推荐话术、歧义三问 → [references/selection.md](./references/selection.md)
- 审查四步、严重度、误报控制、报告结构 → [references/review.md](./references/review.md)
- profile schema、条款可执行化、脱敏 → [references/profile.md](./references/profile.md)
- 动效判定与审查（六形态、静态优先、目标与停止、reduce、运行时验证）→ [references/motion.md](./references/motion.md)
- 度量口径（IoU/墨量/灰度）、盲测与回归集 → [references/evidence.md](./references/evidence.md)
- 渲染页模块与验收 → [references/render.md](./references/render.md)

## 目录结构

```text
tuyi/
├── SKILL.md                      # 运行时入口：铁律、模式路由、六槽、判定梯子、输出契约、失败兜底、验收
├── README.md                     # 本文件（人类可读）
├── CHANGELOG.md                  # 版本记录（顶部 = 最新）
├── references/
│   ├── slot-model.md             # 六槽本体、判定顺序、跨槽混用处置
│   ├── selection.md              # 选型五步 + 动效判定、四类排除、三问、需求对照表
│   ├── review.md                 # 审查四步（含动效 9 项）、严重度、误报控制、建议排序
│   ├── profile.md                # profile schema、八种 check、抽取六步、脱敏
│   ├── motion.md                 # 动效判定：静态优先、六形态、目标与停止、reduce、运行时验证
│   ├── evidence.md               # 三类证据、度量口径、盲测与回归集
│   └── render.md                 # 渲染页模块、约束、case、验收
├── templates/
│   ├── profile.example.yaml      # 脱敏 profile 骨架（可直接改）
│   ├── case.example.yaml         # 渲染页输入骨架
│   ├── selection-card.md         # 选型卡输出模板
│   └── review-report.md          # 审查报告输出模板
├── scripts/
│   ├── iconlab.py                # catalog / search / measure / render
│   ├── badge_lint.py             # profile 驱动的徽章检查器
│   └── _profile_yaml.py          # 受限 YAML 子集解析器（badge_lint 依赖）
├── tests/
│   ├── run_selfcheck.py          # 自测：fixtures 行为 + exit code + file:line 集合
│   └── fixtures/                 # good / bad
└── data/
    └── lucide-catalog.json       # 由 iconlab.py catalog 从真实包生成（771.5 KiB）
```

## 依赖

- Python ≥ 3.10，零第三方依赖（`uv run --no-project python`）
- 图标数据：`lucide-static` 包（ISC）。首次使用先建目录：

```bash
uv run --no-project python scripts/iconlab.py catalog --from <lucide-static 根> --out data/lucide-catalog.json
```

- 渲染页验收需要 Chrome/Edge（headless 截图）；非必需，没有就手工在浏览器里核对三条验收项。

## 边界

- 不做：画新图标、改图标库、打包 icon font、纯排版与配色
- 不替规范所有者裁决冲突：profile 里的 `pending` 冲突只按 `interim` 值继续工作，并在报告里点名
- 不改产品代码：审查模式全程只读，改法写在报告里
