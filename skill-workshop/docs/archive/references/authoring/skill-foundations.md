---
trigger-when: "创建 Skill 前了解基础概念"
name: skill-foundations
description: Skill 基础设计参考。当你需要回顾 Skill 的基本概念、目录结构、资源职责、frontmatter 口径与渐进加载原则时使用此参考。
version: 1.0.0
---

# Skill 基础设计参考


> **一句话**: 把主 `SKILL.md` 留给路由和决策，把基础解释、资源口径和内容下沉规则放到这里
> **版本**: v1.0.0
> **用途**: Skill 基础设计与资源规划参考
> **适用范围**: 所有 Skill 的创建、重构与瘦身

## 目录

- [1. Skill 到底提供什么](#1-skill-到底提供什么)
- [2. 目录结构与 frontmatter](#2-目录结构与-frontmatter)
- [3. resources 怎么放](#3-resources-怎么放)
- [4. 什么不该出现在 Skill 里](#4-什么不该出现在-skill-里)
- [5. 渐进加载与正文瘦身](#5-渐进加载与正文瘦身)
- [版本历史](#版本历史)

---

## 回顾 Skill 基础设计口径


---

## 1. Skill 到底提供什么

### 识别 Skill 的四类能力


Skill 通常通过四类东西提供价值：

- **工作流**：把多步任务写成可执行流程
- **工具集成**：把 CLI、脚本、文件格式或 API 的正确用法沉淀下来
- **领域知识**：把模型默认不知道但又关键的规则、术语、约束写清楚
- **捆绑资源**：把模板、示例、脚本、静态文件按需组织好


## 2. 目录结构与 frontmatter

### 用最小结构起步


最小目录结构通常是：

```text
skill-name/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

`SKILL.md` 至少应包含：

- `name`
- `description`
- `metadata.version`（顶层 `version` 非官方字段，一律放 metadata 内）
- 主工作流与关键步骤
- 头部版本块（可选；存在外部变更记录 CHANGELOG.md/VERSION.md 时可省略）
- 文末 `## 版本历史`（可选；使用外部变更记录承载版本演进时可省略）

允许但非必需的字段：

- `license`
- `metadata`
- `compatibility`

@警告: 不要随意增加未约定字段。版本三处一致性与发布前校验，交给 [versioning-and-validation.md](versioning-and-validation.md)。

## 3. resources 怎么放

### 先按职责分资源，再决定是否真的要建


三个目录的基本职责：

- `scripts/`：稳定执行、工程校验、批处理、脆弱动作封装
- `references/`：大段规则、扩展场景、示例、模式、排错手册
- `assets/`：模板、样例、静态资源、评测回放页面

推荐默认：

- 新 Skill 尽量提供 `scripts/validate_skill.py`
- 落盘动作或易错流程再考虑 `scripts/run.py`
- 若参考资料超过约 `10k` 字，主 `SKILL.md` 中应写清“何时读取哪份参考”

关于输入模板与示例：

- `references/templates/*.md`：固定模板来源
- `references/examples/*.md`：示例文档与自动生成产物
- 模板文档不负责工作流路由
- 单一高频场景默认维护 1 个主模板；只有存在稳定分支时，才扩展到 2-3 个


## 4. 什么不该出现在 Skill 里

### 删除对执行无帮助的内容


主 `SKILL.md` 尽量不要堆：

- 大段背景介绍
- 多个变体混写
- 长模板、长示例、长表格
- 只有人类读者才关心、却不影响执行的说明

除非仓库另有约定，否则通常不要额外创建：

- `README.md`
- `INSTALLATION_GUIDE.md`
- `QUICK_REFERENCE.md`

> 版本变更记录（`CHANGELOG.md` 或 `VERSION.md`）按仓库约定创建其一即可：本仓库统一使用 `CHANGELOG.md`（Keep a Changelog，由 changelog-manager 维护），`SKILL.md` 不再内联 `## 版本历史`。

## 5. 渐进加载与正文瘦身

### 把主 SKILL.md 保持成路由层


渐进加载的三层结构：

1. `name + description`：始终在上下文中
2. `SKILL.md` 正文：Skill 触发后加载
3. `references/`、`scripts/`、`assets/`：按需读取或执行

主 `SKILL.md` 应优先保留：

- 触发边界
- 主 workflow
- 关键步骤
- 决策点
- 校验入口
- “何时读哪份参考”

优先下沉到 `references/` 的内容：

- 大段解释
- 多框架 / 多业务域变体
- 完整模板
- 详细排错手册
- 评测、复盘、回放等次级流程


---

## 版本历史

- **v1.0.0** (2026-05-13) - 初始版本，承接 `skill-workshop` 主文档下沉出的基础概念、资源职责与渐进加载口径
