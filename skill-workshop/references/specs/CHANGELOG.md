---
version: 2026-06
purpose: skill-workshop 规范源（spec.md / best-practices.md / validate.md）拉取与对齐历史记录
source: local-convention
audience: AI agents / humans
role: project-convention
consumed-by: V0 / W3 / W7 / user (manual review)
not-consumed-by: runtime
trigger-when: V0 版本一致性校验 / spec 漂移审查
last-updated: 2026-06-18
---

# Spec Sources Changelog

> **目的**: 记录 `references/specs/` 目录下三个规范源（spec.md / best-practices.md / validate.md）的拉取、版本、对齐历史，作为 **spec 演进跟踪机制**。
> **不维护**: 业务功能变更历史（归 VERSION.md）

## 跟踪字段

| 字段 | 含义 |
|------|------|
| `last-fetched` | 最后一次 WebFetch 该官方源的日期（v1.6 引入） |
| `last-verified` | 最后一次人工或自动校验与官方源对齐的日期 |
| `align-status` | `VERIFIED`（已验证对齐）/ `UNVERIFIED`（未验证）/ `UNREACHABLE`（源不可达） |
| `version` | 本地版本号（不一定等于官方源版本号） |

## 拉取流程

1. 用户说"同步 spec" / "检查 spec 对齐" / "拉取最新 best-practices"
2. WebFetch 官方源 URL
3. 若失败：
   - **第二次尝试**：换 URL 形式（如 `https://agentskills.io/llms.txt` 全文索引）
   - **第三次尝试**：尝试 WebSearch 找替代源（GitHub mirror / 文档快照）
   - **第四次尝试**：告知用户"无法拉取"，请用户**提供本地源文件**
4. 若成功：
   - 对比本地与官方差异
   - 更新本地文件 + bump `last-fetched` / `last-verified`
   - 更新本 CHANGELOG

## 源对齐历史

### spec.md

| 日期 | 拉取者 | 来源 | 版本 | 状态 |
|------|--------|------|------|------|
| 2026-06-18 | v1.6 整改（我） | https://agentskills.io/specification | 2026-06 | ✅ VERIFIED |

**关键修正**: `allowed-tools` 字段从"array of strings"（旧 spec-zh.md 翻译错误）改为"space-separated string"（真实官方规范）。

### best-practices.md

| 日期 | 拉取者 | 来源 | 版本 | 状态 |
|------|--------|------|------|------|
| 2026-05 | v1.5 前 | 未知（中文版，含 Karpathy 4 条） | 2026-05 | ⚠️ UNREACHABLE |
| 2026-06-18 | v1.6 整改（我） | https://agentskills.io/skill-creation/best-practices | 2026-06 | ✅ **VERIFIED** |

**当前状态**: 与官方源**对齐**。frontmatter 已更新为 `version: 2026-06` + `last-verified: 2026-06-18 (VERIFIED — 全文来自真实官方源)`。
**Karpathy 4 条**: 不再属于此技能——Karpathy 4 条是 claude code 等 agent 的工程原则，不是 skill 创建最佳实践。已删除 `references/authoring/karpathy-engineering.md`（v1.6 final）。

### validate.md

| 日期 | 拉取者 | 来源 | 版本 | 状态 |
|------|--------|------|------|------|
| 2026-06-18 | v1.5 整改（我） | https://github.com/agentskills/agentskills/tree/main/skills-ref | 2026-06 | ✅ VERIFIED |

**关键内容**: 6 步校验流程 + 失败速查表 + skills-ref validate 命令用法。

## 待用户决策

- [ ] best-practices.md 官方源 URL 已废止，是否提供本地源 / 或确认使用当前版？
- [ ] spec.md / validate.md 已对齐官方源，是否需要定期（如每月）自动 re-verify？

## 不在本变更日志

- skill-workshop 自身功能变更 → `VERSION.md`
- review-checklist.md 维度过修订 → `references/rubrics/review-checklist.md` 历史段
- workflow 路由调整 → `references/routing-table.md` 演练段
