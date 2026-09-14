# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/lang/zh-CN/spec/v2.0.0.html).

## [Unreleased]
_最后更新：2026-09-14_

### Added

- **moxian（默现）技能加入仓库**：默会知识缺口外化技能 v0.1.0——照出 AI 写码对话里「以为懂、其实没内化」的三层认知缺口（名词层→词卡 / 表达层→更锋利的问题 / 概念层→微课），默认过闸门只给 1-2 条，落一份可累积的认知卡到 `docs/moxian/`（默现 / moxian / 我哪没懂）
- **skill-workshop 技能加入仓库**：Skill 全生命周期工作站（创建/评审/重构/评测 Agent Skill），v1.17.0，含 16 个 CLI 子命令与 9 维 48 项评审体系
- **vibe-buddy 技能加入仓库**（2026-09-10）：项目 AI 协作记忆技能 v1.0.0——协作契约写进 AGENTS.md，进度/决策/踩坑沉淀到 docs/.ai/，跨会话自包含交接，开发经验蒸馏（vibe-init / vibe-sync / vibe-handoff / vibe-distill）

### Changed

- **skill-reviewer 版本号三段式规范化**：`4.6` → `4.6.0`
- **changelog-manager 安全性增强**
  - 新增操作反例黑名单章节，包含 10 条反模式和危险动作子章节
  - 在 W0/W1/W2 工作流关键决策处添加 CHECKPOINT/STOP 视觉标记
  - 在 W0/W1/W2 工作流中添加失败处理 fallback 表
- **changelog-manager v2.0.0 → v2.0.1**（2026-09-12）：6 个 `references/` 文件补 `trigger-when` 加载指引，对齐「内容三层分层」强约束
- **skill-workshop v1.17.0 → v1.23.1 演进**（2026-08-20 ~ 09-12）：
  - v1.18.x：三段式评审元框架注入、darwin 实测修复（评审口径统一 10 维 52 项）、全脚本审查修复 7 处缺陷、V0 语义标记按构建者/运行型分类校验
  - v1.19.0：整合 skill-review-process v6.5-v6.8（0.6 铁律 / C5 交叉核对 / 5.7 分级门禁 / 0.5 状态机）
  - v1.20.0：dogfooding 自审修复（checklist FAIL→PASS、routing-check 真源三方比对、版本口径收敛）
  - v1.21.x：第一性原理自评整改（Google 5 模式基线）、版本单源化、校验器补中文 Pushy 句式
  - v1.22.0：description 判据口径对齐（消除 6 处自相矛盾 + 校验器三态分级 + 官方源缓存）
  - v1.23.0：脚本柔性化 Phase 1（plan-gate / checkpoint / profile / dry-run 默认）；版本一致性正则修复（带注记的 VERSION.md 标题不再误报）
  - v1.23.1：routing-check 工作流清单加目录门控，不再误报扁平 `references/` 布局技能
- **zuiti v0.2.4 → v0.3.9**（2026-08-31 ~ 09-12）：名言/热梗核验屉扩容与六风格体系、P0-P2 去呆板系列（引导式提示词取代填空模板）、validate_skill.py 单遍化提速、纯中文祈使句 description、validate_skill.py 支持 `--offset`/`--output` 截断

### Deprecated

- **skill-reviewer 标记为已废弃**：已被 skill-workshop 完全替代（skill-workshop 评审链已合并其全部能力：九维 48 项评审、W0-W7+V0 工作流、合规校验），不再推荐触发使用，目录保留作历史归档；根 README 技能列表与 skill-reviewer 的 SKILL.md / README 均已同步标注
- **skill-reviewer 从发布流程中移除**：`.github/workflows/release.yml` 不再打包 / 发布 skill-reviewer（从触发路径、打包步骤、Release 说明表与附件列表中删除），仅保留 changelog-manager 走发布流程

### Removed

- **skill-reviewer 技能物理删除**（2026-09-10）：此前 Deprecated 事项落地——能力已全部并入 skill-workshop，根 README / project-overview / 决策日志同步清理
- **GitHub Actions 发布流程退役**（2026-09-12）：删除 `.github/workflows/release.yml`。仓库定位纯技能集合，分发走 `npx skills add` 直读仓库；`CHANGELOG.md` / `CHANGELOG.en.md` 降级为纯人类文档，不再关联任何自动化

## [1.1.1] - 2026-05-30

### Changed

- **GitHub Actions workflow 修复**
  - 修复打包方式：使用 `zip -r` 保留目录结构（技能目录作为 zip 根）
  - 修复版本检查逻辑：版本未递增时跳过而非报错
  - 修复步骤 id 引用问题
  - 移除 artifact 上传步骤（直接在 release 中附带）

## [1.1.0] - 2026-05-30

### changelog-manager v2.0.0

- **双语言支持升级**
  - 内置双语言支持，同时维护中文 CHANGELOG.md 和英文 CHANGELOG.en.md
  - 新增 `+lang` 快捷命令切换主语言模式（`+lang zh` / `+lang en`）
  - 新增 bilingual-guide.md 参考文档（60+ 术语对照表）
  - 新增 V4 双语文档一致性验证
  - 全部工作流（W0-W5）更新为同时操作两个文件
  - README.md 和 output-template.md 同步更新

## [1.0.0] - 2026-05-29

### Added

- **skill-reviewer v4.6** - 九维 48 项结构化评审与合规校验
  - 新增指导自由度分级声明（§5），明确三种模式的约束强度
  - 新增评测驱动迭代纪律（V4.1），规范 description 修改后的回归流程
  - 调整段落编号以保持结构一致性

- **changelog-manager v1.1.0** - 基于 Keep a Changelog 规范的更新日志维护助手
  - 支持从 git 提交记录自动生成变更
  - 支持手动追加条目和版本发布归档
  - 内置规范化检查功能

### Changed

- 将中文 README 设为默认版本，英文版更名为 README.en.md
- 同步更新项目根目录和 skill-reviewer 的 README 文件
- skill-reviewer 版本号更新至 v4.6

### Docs

- 添加 README.md（中文）和 README.en.md（英文）
- 添加对 base44/skills 项目的致谢
- 格式化评审检查清单表格并添加扩展字段指南

### Deprecated

- README.zh-CN.md 已合并至 README.md（中文版作为默认）
