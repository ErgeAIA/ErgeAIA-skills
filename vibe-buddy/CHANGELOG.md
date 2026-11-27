# vibe-buddy 版本记录

> 只记录版本号、核心变更与修改文件。设计取舍见 README，生成规范见 references。

---

## [Unreleased]

## v1.12.0 (2026-11-27)

### 新增

- 第 9 个触发词 `vibe-req`：EARS 需求澄清。内核是「升维四问」——高手会多做什么、最原始材料、具体方法、外部验证——要更深不是更大；EARS 五类句式只是落盘形态，空类不写。
- `vibe-audit` 的变更集与 `mode=security` 两种模式；`vibe-check` 只读档案体检；`vibe-release` 发布治理契约。

### 变更

- 全部工作流共用 `references/workflow-protocol.md`；`SKILL.md` 从 196 行压到 184 行。
- 过程档案加入增长边界（进度 300 行、决策 200 条等），超阈值先归档再写，编号跨归档唯一。
- Git 白名单扩展到逐文件取证，禁止裸 `diff` / `log -p` / `show`，设 30 文件 / 400 行 / 80KB 上限。

### 修复

- 模板不再引用技能内部路径（目标项目没有这些文件）；安全清单补「不评栈」声明。

## v1.11.0 (2026-11-27)

### 新增

- `references/workflow-protocol.md`：公共工作流协议（触发顺序、事实源、写入唯一性、原因码、归档阈值、三档分级），6 份 reference 各加指针。
- `references/audit-checklist.md`（通用危险写法 10 条 + 安全 12 条）、`references/release-checklist.md`（发布六步闸）、`references/check-artifacts.md`（只读档案体检 10 项）。
- 第 7 个触发词 `vibe-check`；第 8 个 `vibe-release`；`vibe-audit` 增加变更集模式与 `mode=security`。
- 过程档案增长边界：进度 300 行、决策 200 条等 8 项阈值，超阈值先归档再写，编号跨归档唯一。
- `vibe-sync` 执行台账（`produced` / `skipped` / `level` 机读行）。

### 变更

- `SKILL.md` 196→185 行；脱敏、五态、原因码收敛为单一真源；`project-overview.md` 升级为架构基线四段。
- Git 白名单扩展逐文件取证，禁止裸 `diff` / `log -p` / `show`。

### 修复

- 模板不再引用技能内部路径；`check-artifacts.md` 完成判据节号改正；README 触发词数量统一。

## v1.10.0 (2026-11-16)

### 变更

- description 收为两段式（Job + Use when），按触发自测集校正触发词；边界事实移到正文 Non-Goals。

---

## v1.9.0 (2026-11-15)

### 新增

- `vibe-wrap`（收尾）：一次自审后按 triage 串行执行 sync → distill → handoff，跳过项给原因码。
- 蒸馏去重改用 `experience/.distill-index.json`（按 commit SHA），`changelog.md` 降为一行人读台账。

### 变更

- 语义判据（杂音 N1–N6、行数须实测）降级为审稿提示，不再当过闸条件。
- 环境判定去重：Git 空输出 / 零提交的解释收敛到 `command-policy.md`。

---

## v1.8.0 (2026-10-10)

### 新增

- 初始化新增「仓库卫生检查与补齐」：检测 `.gitignore` / `CHANGELOG.md` / `README.md`，按归属委托 git-manager / changelog-manager / shuxu 并验收。

---

## v1.7.0 (2026-10-06)

### 变更

- 初始化状态机 A–E 细化；半程项目只补缺失文档，不重写既有文件。

---

## v1.6.1 (2026-09-27)

### 修复

- 修复同日多份交接文档「最新一份」判据：按文件名日期取最新，同日再比 frontmatter `updated`。

---

## v1.6.0 (2026-09-27)

### 新增

- 新增 `vibe-init`：建立 `AGENTS.md` 与 `docs/agents/` 全套过程文档，含 CLAUDE → AGENTS 受控迁移与安全删除闸。
- 新增 `vibe-audit`：对开发类项目做只读审查（代码质量 / 架构 / 技术栈），每条结论带 `路径:行`，Skill 项目转交 skill-workshop。
- 新增 `vibe-handoff`：生成自包含交接文档，只展开别处读不到的四类。
- 新增 `vibe-distill`：把反复成立的做法提炼成按领域组织的经验条目（五要素 + 三级）。

### 变更

- 「接管」去触发词化：读项目档案 + 复述现状是目标项目 `AGENTS.md` 的义务，不依赖本技能入口。
- 终端命令改白名单制：默认不跑命令，只放开 Git 检测 / 初始化与 codegraph 检测 / 建索引。

---

## v1.5.1 (2026-09-26)

### 修复

- 修复决策编号与调试编号取法：读最大编号加一，三位补齐。

---

## v1.5.0 (2026-09-25)

### 新增

- 新增 `vibe-sync`：沉淀进度 / 决策 / 调试记录，按需回填 `AGENTS.md` 事实区。
- 过程文档加入客观事实源：Git 只读核对 > 最新交接 > 既有过程文档 > 会话上下文，冲突以客观源为准。

---

## v1.4.1 (2026-09-24)

### 修复

- 修复「契约区与事实区」自相矛盾：`AGENTS.md` 契约区只由 init 写，事实区由 sync 回填。

---

## v1.4.0 (2026-09-24)

### 新增

- 新增 `references/command-policy.md`：终端命令白名单单一真源，按触发词声明允许子集。

---

## v1.3.0 (2026-09-24)

### 新增

- 过程文档统一 YAML frontmatter（`title` / `type` / `project` / `updated` / `description`），每次修改须同步 `updated`。
- 新增 `docs/agents/init-report.md`：初始化执行报告，只追加。

### 变更

- 模板外置到 `assets/docs/`，消除模板与规范两处漂移。

---

## v1.2.0 (2026-09-13)

### 新增

- 新增 `vibe-init` 的 Git 检查（只读检测，无仓库则初始化）与 Codegraph 集成（已装且无索引才建索引）。

---

## v1.1.0 (2026-09-13)

### 新增

- 新增 `vibe-distill` 的经验分层（🔴 红线 / 🟡 倾向 / 🟢 参数）与双台账（`changelog.md` + `.distill-index.json`）。

---

## v1.0.0 (2026-09-10)

### 新增

- 首个版本：`vibe-init` + `vibe-sync`，建立 `AGENTS.md` 唯一契约源与 `docs/agents/` 过程文档区。
