## [Unreleased]

未发布条目在此累积；版本号只在切发布时改（版本与提交解耦）。

## [1.2.0] - 2026-11-13

补齐「点了要等结果」按钮的过程编排：判定、机检与可交互验收三件齐全。

### 新增

- 新增过程型状态机动效的编排层判定（准入、五相位、中断与回落分叉、每实例循环预算、审查清单），使「点了要等结果」的按钮不再按单图标动效硬套。
- profile 新增 `motion.state_machine` 可选块；未配置即视为项目未批准编排。
- 新增四种编排机检（相位类名、reduce 关关键帧、槽位叠放、aria-busy）与对应测试样例。
- 新增可交互状态机演示页生成命令，供运行时验证 reduce、打断、卸载与回落分叉。

### 变更

- 参考资源、README 与渲染页验收同步接线编排层。
- 仓库归属迁入开源仓 `ErgeAIA-skills`（不升版）：技能内容、版本与行为不变；此前开发历史留在私有仓，公开仓自本条起。
- 第二轮脚本热点优化（不升版）：`badge_lint.py` 的开标签定位加「停字符集 + C 级查找」快路径，非 CSS 目标的倒排索引改为按需建立，路径归一化去掉重复 `resolve`，选择器规格只解析一次；`iconlab.py` 的胶囊栅格化改为逐行区间填充、重量级模块按需导入。目的是缩短全量扫描与预览渲染的等待，判定结论与产物字节不变。
- 实测（HEAD 对改后交替 5–15 轮取最小）：真实项目 `src/`（87 个前端文件）全量扫描约 −7%～−13%，`render` 约 −6%～−9%，`measure` 约 −3%～−6%，`catalog`/`search`/单 fixture 扫描变化落在进程启动噪声内（±2%）。

## [1.1.0] - 2026-11-05

以「可复核」补齐动效与检查盲区：动效结论必须落到真实触发与停止条件，机器检查不再把未检查的规则算作通过。

### 新增

- 增加动效判定（`references/motion.md`）：先问真实变化、停止条件与静态等价，任一不成立即静态，避免为动效而动效。
- 选型（A）增加第 6 步、审查（B）增加第 4 步动效分支：动效沿用槽位与证据底座，不另立第四模式。
- profile 与输出模板增加 `motion` 配置与字段：项目已批准的动效规则可复用，参考建议只留在报告里。

### 修复

- 开标签解析改为字符级状态机，内联 `style` 纳入同一套规则：跨行 JSX 不再被静默跳过，未检查的规则也不再计入 `passed`。
- 增加跨行、解析失败与解析边界三组回归 fixture，锁定「未检查 ≠ 通过」的语义。

### 变更

- `badge_lint.py` 预编译正则并缓存类名与选择器匹配，缩短全量扫描耗时且不改变结论。
- 降低扫描与栅格化热点开销（选择器规格缓存、字节计数替代逐像素求和、免去目录节点复制），结论与产物保持不变。
- 脚本输出统一 UTF-8，避免 Windows 控制台下中文报告解码失败。
- 审查报告模板删除内嵌重复副本，模板只留一处，避免双份漂移。
- 歧义停点加显式标记，description 补建 profile 与动效触发，失败兜底补解析与动效两类。
- 自测收敛为 `good` / `bad` 两组 fixture，删除跨行、解析失败与解析边界三组用例，降低维护面；核心判定仍由零误报与逐行命中覆盖。

## [1.0.1] - 2026-11-03

按 skill-workshop AUDIT→OPTIMIZE 流程做的首次优化：触发面更准、文档结构更瘦，能力与验收口径不变。

### 变更

- **SKILL.md description 重写**：137 字含技术细节（16px 轮廓相似度、离线 HTML）压缩为 56 字两段式（做什么 + Use when），技术细节留在正文；降低触发门槛，提高自然语言命中率。
- **README「怎么用」表重排为 6 场景**：徽章选型（含歧义处理）/ 候选对比 / 审查已有徽章系统 / 生成预览页 / 从规范建 rulebook / 边界确认，示例提示词覆盖审查模式与 profile 生成。
- **references/review.md 与 templates/review-report.md 合并**：报告模板以内嵌代码块并入 review.md 附录（155 行）；templates/review-report.md 保留为独立模板，CHANGELOG 资源行同步改写。

- `spec` + `validate` 双 PASS（advisory：description 含斜杠、runtime-class，非阻塞）。
- `tests/run_selfcheck.py` ALL OK（exit 0）：fixture-good 零误报、fixture-bad 9 条 file:line 精确命中、边界 exit 2 与 --rules 10 条不变。

## [1.0.0] - 2026-11-03

首个版本。把「徽章图标怎么选」从审美偏好收敛成可复核的判定流程，并支持对已有徽章系统做规范审查。

### 新增

- **六槽模型**（`references/slot-model.md`）：状态 / 来源 / 计数 / 筛选 / 动作 / 导航，每槽写死形态契约（尺寸、色、Tooltip、可否点击）、允许与禁止用法、跨槽混用处置。核心判据是「图标义由槽位决定，不由字面决定」。
- **选型流程**（`references/selection.md`）：五步（判槽位 → 查既有映射 → 检索真实 tags → 四类排除 → 三档结论）；四类排除项（借用错误语义 / 动作状态错位 / 同族轮廓混淆 / 风格许可不合）；可计算的歧义阈值（分差 < 20% 且近邻 IoU > 0.75）与固定三问。
- **判定梯子**（`SKILL.md`）：纯图标 + Tooltip → 图标 + 短词 → 纯文字胶囊 → 换表述，带退出条件，回答「什么时候根本不该用图标」。
- **审查模式**（`references/review.md`）：按输入形态分级结论强度；机器查形态、人查语义；blocker/major/minor 以「误读后果」定级；误报控制（未覆盖不算通过、单点不外推、pending 冲突不静默、不确定降级）。
- **可执行 profile**（`references/profile.md` + `templates/profile.example.yaml`）：规范与检查之间的那一层，条款带 `source_ref` 行号；八种 check（`css_forbid` / `css_value_in` / `css_value_not_in` / `css_value_min` / `dom_attr_required` / `dom_text_forbidden` / `dom_forbid_descendant` / `source_forbid_regex`）；不可执行的条款转 `human_check` 而不是硬塞；规范内部矛盾登记为 `conflicts` 并给 `interim`，不替所有者裁决。技能本体不写死任何产品条款。
- **证据纪律**（`references/evidence.md`）：只认三类证据——规范原句（`文件:行`）、图标库事实（id + tags + 许可 + 版本）、视觉度量（16px 剪影 IoU / 墨量比 / 灰度 / 行上下文）；给不出就写「未验证」；附留出集盲测（≥ 7/8）与回归集设计。
- **渲染页**（`references/render.md`）：离线单页 HTML，八个模块（结论头 / 尺寸阶梯 / 双主题 / 灰度 / 真实行上下文 / 候选对比 / 混淆矩阵 / 可复制规格块）；零外部请求、颜色只走变量、1440×950 无横向滚动。
- **脚本**：`scripts/iconlab.py`（catalog 建库 / search 意图检索 / measure 几何度量 / render 出页），`scripts/badge_lint.py`（profile 驱动的 `file:line` 级检查，未覆盖标 N/A）。
- **模板**：selection-card / review-report / case.example.yaml（报告格式指引已内嵌至 references/review.md）。
- **自测**：`tests/run_selfcheck.py`（纯标准库）+ `tests/fixtures/{good,bad}`，锁定 exit code、`file:line` 集合与 N/A 语义。

### 变更

- **selfcheck 全绿**：fixture-good → exit 0 / verdict PASS / blocker 0 / major 0（零误报）；fixture-bad → exit 1，9 条 findings 的 `file:line` 集合与期望**完全相等**（不缺不多）；目标不存在 → exit 2；`--rules` 列 10 条；目录 2019 图标。
- **真实项目扫描**：57 文件 / 33370 处检查，10/12 条规则 PASS，6 条 major 逐条回读源码确认属实后保留（`.status-icon` 尺寸盒 20px 超白名单、`.help-badge` 18px 与 `.note-btn` 32px 低于 36px 热区下限）。N/A 2 条如实标注，未冒充合规。
- **渲染页浏览器实测**：`scrollWidth 1409 ≤ innerWidth 1424` 无横向溢出；外部请求 0；内联 SVG 30 个；尺寸阶梯为真实像素（12/16/18/20/24）；灰度块 `filter: grayscale(1)` 生效；规格块与复制按钮在场。
- **修掉两处会致误报/漏报的缺陷**：① 扫描根由 `cwd` 改为目标集合的公共根——原实现下 `--target <项目>/src` 时全部路径以 `src/` 为根，`except_files` 里的 `src/components/Icon.tsx` 永不匹配，会把统一图标入口自身报成违规；② 豁免匹配改双向路径后缀，兼容不同根视点下的同一文件。

- 脱敏：技能本体不含产品名、内部决策编号与绝对路径；具体规范以独立 profile 承载，规范改版只换 profile。
- 分层：`README.md` 人读 / `SKILL.md` 执行规则 / `references/` 按需加载（均带 `trigger-when`）。
