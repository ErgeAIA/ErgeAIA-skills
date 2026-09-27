# shuxu 版本记录

> 保持简洁；只记"改了什么" + "为什么"。

---

## v1.1.1 (2026-09-27) · Deep Review 三项落地

- **P1 规则冲突修复**：Step 5.1 禁止命令清单原含"发请求"，与 5.2"WebFetch 抽查 URL"自相矛盾；改为**豁免**——发请求（WebFetch 只读抽查 URL 除外，见 5.2，只读 GET 不构成副作用）。
- **P2-1 措辞修正**：Step 5.1"只运行无副作用命令"原列 build/test（会写本地产物）自相矛盾；改为明确"本地环境内可回滚操作，不对外部世界造成影响"。
- **P2-2 风格**：frontmatter version 加引号 `"1.1.1"`（对齐仓库惯例）。

## v1.1.0 (2026-09-13)

### 管线编号对齐 + 旁路机制家族化 + 分支关系显式化

- **管线六段**：快速管线改为「① 模式确认 → ② 只读分析 → ③ 写作 或 ④ 优化 → ⑤ 验证 → ⑥ 收尾」，与正文 Step 编号一致；原「⑤收尾」无编号问题消除。
- **③④ 互斥分支**：Step 3/4 标题与文内注明「生成 / 增量互斥、非串行」，产物后写明跳转（3→5，4→5）。
- **旁路机制对齐家族**：动笔前 CHECKPOINT 跳过条件改为「编排自动模式」同构表述（编排非交互或用户一步到位），并在收尾清单要求标注跳过原因；与 huiyi / zhen / pailei 口径一致。
- `metadata.version` → 1.1.0。
- **description 优化（2026-09-26，不升版）**：按 Trigger+Job+Boundary 重写；Not for 只留路由冲突项。

### 未改（保持最优实践）
- description 英文触发句保留（家族对照中的正向样板）。

---

## v1.0.4 (2026-08-25)

### 边界补齐（darwin dim9 负面集 dry_run 发现，用户裁决后落地）

- description Not for 补「README 翻译」——关闭「翻译请求」边界缺口（v1.0.2 dry_run 发现：翻译请求既不在做什么也不在不做什么，Agent 需临场判断）；翻译不涉及仓库分析，与防幻觉纪律冲突，明确排除。
- 字节复核：Not for 增补后约 816 UTF-8 字节 / <500 字符，双口径仍合规。

---

## v1.0.3 (2026-08-25)

### description 最佳实践优化

- **动词前置**：「撰写、生成、重写或优化项目 README」替代「分析代码仓库并生成或优化」——触发匹配更直接，前 100 字符承载核心意图。
- **Pushy 强化**：加 "even if they do not say README"（intent-calibration Pushy 正例风格，防止用户只说"写个项目介绍"不触发）。
- **压缩冗余**：Not for「技术博客文章」→「技术博客」；保留三维触发锚点（README.md / Markdown / package.json / Cargo.toml / pyproject.toml / JSON）。
- **字节验证**：官方 spec 限制为 1024 characters；优化版 493 字符 / 801 UTF-8 字节，双口径合规（用户提示按 1024 字节口径保守校验）。

---

## v1.0.2 (2026-08-25)

### darwin-skill 2.1 审查整改（9 维评分 84.6/100，仅评估→用户确认后落地）

- **P1 dim4 显性标记**：Step 1 模式确认加 `🔴 CHECKPOINT`（可见性/语言无法判断时强制询问）；Step 2 动笔前加 `🔴 CHECKPOINT`（分析摘要 + 模式取舍先确认，用户要求「一步到位」可跳过）。
- **P1 dim3 分析阶段失败分支**：清单文件缺失 → 基于现存文件继续并标注「来源局限」；无 LICENSE / 可见性不明 → 回 Step 1 CHECKPOINT 询问；语言混杂 → 按主导处理并记录差异。
- **P2 dim2 中间产物显式化**：Step 2 产物 = 来源记录表；Step 3 产物 = README 草稿全文/改动清单；Step 4 产物 = 改动摘要。
- **P2 dim8 负面集 dry_run**（未真跑 LLM，标注 dry_run）：①「写篇公众号文章介绍我的项目」→ 路由转 zhubi / long-article ✓；②「生成完整 API 文档」→ Non-Goals 拒绝 ✓；③「把 README 翻译成日语」→ **边界缺口**：Not for 未覆盖「翻译」场景，预期响应为拒绝但缺显式边界声明——记录待用户裁决是否补 Not for。
- **Runtime gate**：红灯扫描零命中，runtime-neutral ✓。

---

## v1.0.1 (2026-08-25)

### skill-workshop 完整链审查整改（W1-W7 + 三段式元框架 + 机器校验门禁）

- **方向判定**：第一性锚定「防幻觉文档生产纪律」→ 对齐；复杂度轻量（六维仅执行链命中）；10 维未命中仅 D1/D3/O1a，档位稳定可复用；8 维加权 88/100。
- **P1 D1 双轨标注**：Step 5 命令验证改为每条示例命令二选一 `[已运行验证]` / `[未经运行验证]`（无标注即禁止）+ 补「禁止命令清单」（publish/写库/发请求/改源码）；CHECKLIST 第 4 条同步口径。
- **P2 D3 输入契约**：Step 1 补仓库路径校验分支（路径缺失 → [待澄清] 询问；不存在/拉取失败/不可读 → 中止说明，不静默降级）。
- **O1a 信息性**：metadata.origin 缺失，来源已在 VERSION/CHANGELOG 记录，申报不补。

---

## v1.0.0 (2026-08-25)

### 初始创建

- **定位**：分析代码仓库 → 生成 / 优化项目 README（读者 = 外部开发者），最高准则防幻觉（只写代码确认事实、命令字面一致、未验证必标注）。
- **模式**：开源（默认中文主文件 README.md + 英文版 README.en.md 双语平行）/ 私有（单文件中文）；用户显式指定优先。
- **结构依据**：Standard Readme 社区共识；模板 2 套（oss-bilingual / private-zh）+ CHECKLIST 10 项。
- **命名**：shuxu（书序）——README 即项目之序；拼音双字，与 zhubi / fuzi 同命名体系（用户 2026-08-25 定稿偏好；候选 shuxu / tiji / shuoming，用户选 shuxu）。
- **来源**：用户与 tabbit 讨论文档（对话纪律 + README 方法论 + readme-craft 草案）经本仓库规范重写；语言策略按用户裁决改为**中文主文件**。
- **实测**：skill_cli validate / checklist / consistency 全 PASS（checklist 首次全绿，M6/V4 措辞修正后）；ErgeMD 实战——只读分析报告已出（P1×3：Node 18+ 不实、生产构建命令缺发布链、pnpm 8+ 不实）；命令真实性：`vitest run` 19/19 通过；`pnpm test` 本体因 pnpm 依赖状态检查需重建 node_modules（无 TTY 中止 `ERR_PNPM_ABORTED_REMOVE_MODULES_DIR_NO_TTY`）未直接跑通；`cargo test` 因 target 缓存引用迁移前旧路径（`D:\Workspace\Code\RustProject\ErgeMD` 不存在）失败——均为环境问题非脚本错误，按防幻觉纪律如实标注（对应 ErgeMD README「测试」节待优化项）。
