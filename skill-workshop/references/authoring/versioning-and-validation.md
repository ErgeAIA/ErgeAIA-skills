---
trigger-when: "验证与打包 Skill 时"
name: versioning-and-validation
description: Skill 版本与验证参考。当你需要更新 version、维护版本历史、运行 validate 或 package 子命令时使用此参考。
version: 1.18.0
---

# Skill 版本与验证参考

<!-- @类型: 参考指南 -->
<!-- @目的: 统一版本号维护、版本历史位置和打包前验证流程 -->
<!-- @场景: 修改 Skill 文档、脚本、参考资料或发布产物前 -->
<!-- @触发条件: 当目标 Skill 或本技能发生修改，需要验证并打包时 -->

> **一句话**: 每次修改都同步更新版本，并在打包前完成最小验证
> **版本**: v1.18.0
> **用途**: 版本维护与验证参考
> **适用范围**: 本技能与所有目标 Skill

## 1. 版本更新规则

每次修改 `SKILL.md`、`scripts/`、`references/` 或 `assets/` 时，同步更新：

- YAML frontmatter 中的 `version`
- 标题下的版本信息块（`> **版本**: vX.Y.Z`）
- 文末 `## 版本历史`

对于 `references/examples/*.md` 里的场景示例文档，沿用同一套规则：

- 模板 frontmatter 中的 `version`
- 模板标题下的版本信息块（`> **版本**: vX.Y.Z`）
- 模板文末 `## 版本历史`
- 若自动生成覆盖已有模板，默认递增补丁版本
- 版本历史同样最多保留 5 条

默认遵循语义化版本（**版本号强制三段式 X.Y.Z**，如 `v1.1.1`；**禁止两段式**，如 `v1.1`）：

- **补丁版本**：措辞修正、小型校验增强、非结构性调整
- **次版本**：新增参考文件、新增流程指引、中等结构调整
- **主版本**：工作流、目录约定或兼容约束发生重大变化

## 2. frontmatter 字段口径

- 必填：`name`、`description`、`metadata.version`（顶层 `version` 非官方字段，一律放 metadata 内）
- 允许但非必需：`license`、`metadata`、`compatibility`
- 不要增加未约定的自定义字段

## 3. 版本历史位置要求

`## 版本历史` 应位于文末附近。其后只允许保留：

- 空行
- 结尾分隔线（如 `---`）

不要把新的正文段落写在版本历史之后，否则校验器应视为结构错误。

**条目数量约束**：版本历史保留最近 5 条，超出时裁剪最早的条目。每次新增版本记录后，若条目超过 5 条，应删除最早的条目以保持 5 条以内。

## 4. 最小验证流程

先跑快速验证：

```bash
python scripts/skill_cli.py validate <path_to_skill_folder>
```

如果目标 Skill 提供 `scripts/validate_skill.py`，继续跑工程硬校验（这是目标 Skill 自己的入口，不走本技能 CLI）：

```bash
cd <path_to_skill_folder>
python scripts/validate_skill.py --skill .
```

再做打包验证：

```bash
python scripts/skill_cli.py package <path_to_skill_folder> [./dist]
```

实现层约定：

- `scripts/skill_cli.py` 是唯一公开 CLI 入口
- `scripts/_impl/*` 放共享实现；维护逻辑时优先修改 `_impl/`，不要再新增并行入口脚本

验证器重点检查：

- frontmatter 是否可解析，且只包含约定字段
- 必填字段 `name`、`description`、`metadata.version` 是否存在
- 语义化标记是否存在
- frontmatter、头部版本信息、文末首条版本历史是否版本一致
- 版本历史是否存在、是否位于文末附近、是否保留不超过 5 条（超出时裁剪最早的条目，保留最近 5 条）
- `SKILL.md` 是否仍残留脚手架模板占位：如 `TODO`、`YYYY-MM-DD`、占位标题等
- 若存在 `references/examples/*.md`，其是否包含固定章节，并显式声明“`不负责工作流路由`”
- 若存在 `references/examples/input-template-*.md`，其 frontmatter/header/latest history 三处版本是否一致，且版本历史条目不超过 5 条
- 若存在自动生成示例，是否写入 `references/examples/`，且 `index.md` 已同步更新为示例索引表
- 若主 `SKILL.md` 采用"决策矩阵 + 强规则摘要"，二者是否同时存在；不要只保留矩阵或只保留规则摘要的一半结构
- 若主文档采用决策矩阵，矩阵是否使用稳定表头 `| 场景 | 命中信号 | 跳转到 |`
- 若主文档采用决策矩阵，且存在 `references/examples/input-template-*.md`，`references/examples/index.md` 是否补了"决策矩阵命中速查"与表头 `| 用户常见说法 | 命中矩阵行 | 建议先打开 |`
- 评测用 `eval-set` 是否结构合法：`query` 唯一且非空，`should_trigger` 为布尔值
- 若存在 `scripts/validate_skill.py`，目标 Skill 的工程硬校验是否通过
- 正文是否超过建议行数阈值（软告警）
- 本地 Markdown 链接是否有效：
  - 相对路径文件是否存在
  - 同文件锚点 `#section` 是否存在
  - 跨文件锚点 `file.md#section` 是否存在
- 错误信息是否可排查：
  - 缺文件时显示 `missing file`
  - 缺锚点时显示 `missing anchor`
  - 缺锚点时附带目标文件前几个可用锚点
  - 若存在接近的锚点拼写，附带 `maybe:` 推荐项
- **路由一致性（仅 skill-workshop 自身校验时）**：SKILL.md §4 路由表 + 5 个 workflow 的 `reads-from` 块 + 9 个 authoring 文件的 `trigger-when` 块三处必须与 `references/routing-table.md` 保持一致；三处任一失配 → 整体 FAIL，错误信息形如 `[routing-mismatch] file=authoring/X.md, missing-from=SKILL.md-table|workflow-reads|trigger-when`

## 5. 发布包过时提醒

如果 `dist/<skill-name>.skill` 已存在，而源码中有文件的修改时间晚于当前归档，打包脚本应提示“发布包可能过时，请重新打包”。

这类提醒不应阻断打包，但应促使重新发布，避免仓库里长期保留陈旧产物。

## 6. 推荐排查顺序

当 `python scripts/skill_cli.py validate ...` 失败时，建议按以下顺序处理：

1. 先修 frontmatter、头部版本、首条版本历史这类结构性错误
2. 再清理 `TODO`、占位日期和占位标题
3. 再修版本历史位置和条目数量问题
4. 若存在 `references/examples/*.md`，先补齐固定章节，并明确写出“`不负责工作流路由`”
5. 再检查示例文档 frontmatter/header/latest history 是否三处一致，以及版本历史是否不超过 5 条
6. 若主文档采用“决策矩阵 + 强规则摘要”，确认矩阵、规则摘要和示例索引速查是否成套出现
7. 若存在自动生成示例，再检查是否落在 `references/examples/`，且 `index.md` 已同步更新
8. 再修 Markdown 链接：先解决 `missing file`，再解决 `missing anchor`
9. 若评测失败，先修 `eval-set` 结构，再重跑 `skill_cli.py eval` / `skill_cli.py loop`
10. 若打包失败，优先看目标 Skill 的 `scripts/validate_skill.py` 输出
11. 最后处理正文行数软告警，把长示例和变体细节继续下沉到 `references/`

---

## 版本历史

- **v1.18.0** (2026-08-19) - 版本号强制三段式 X.Y.Z（禁止两段式 v1.1）；修复本文件 frontmatter 版本漂移（1.16.0 → 1.18.0，对齐头部与版本历史）
- **v1.17.0** (2026-06-18) - 增"路由一致性"硬校验项：SKILL.md §4 路由表 + 5 个 workflow 的 `reads-from` 块 + 9 个 authoring 文件的 `trigger-when` 块三处必须与 `references/routing-table.md` 保持一致；失配 → 整体 FAIL
- **v1.16.0** (2026-05-16) - 将"决策矩阵 + 强规则摘要"纳入验证口径：补充矩阵表头、强规则摘要与示例索引速查的联动检查要求
- **v1.15.0** (2026-05-02) - 修正版本与校验口径：固定模板来源留在 `references/templates/`，自动生成的场景示例文档回到 `references/examples/`
- **v1.14.0** (2026-05-02) - 将 Skill 版本规则扩展到场景模板文档：模板也要求 frontmatter/header/history 三处一致，并校验版本历史不超过 5 条

---
