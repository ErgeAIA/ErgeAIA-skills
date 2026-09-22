---
trigger-when: 运行 validate/spec/package、编写校验相关步骤、或需要基础格式与核心安全规范时
name: validation
description: 基础格式、版本 SSOT、链接与脚本安全闸门；CLI validate/spec/package 用法与退出码。
---

# 验证规范（validation）

## 机器闸门（运行时 CLI）

| 命令 | 检查什么 | 退出码 |
| --- | --- | --- |
| `python scripts/skill_cli.py spec <path>` | **官方** frontmatter 契约：字段白名单、必填、name 与目录一致及格式、description 存在/非空/长度/尖括号（字段**顺序**为 advisory，不阻塞） | 0 PASS / 1 FAIL / 2 ERROR |
| `python scripts/skill_cli.py validate <path>` | 结构静态校验全量：上述 + **项目级 YAML 稳健性**（双引号单行、无反斜杠、无 `{{…}}`/`TODO` 占位符）+ 版本 SSOT、引用与链接、references `trigger-when` | 同上 |
| `python scripts/skill_cli.py init <name> --path <dir>` | 纯 Markdown 骨架；默认 dry-run；`--write` 落盘（plan-gate） | 0/1/2 |
| `python scripts/skill_cli.py package <path> [out]` | 校验后打包 `.skill`；默认 dry-run；`--write` 才落盘（plan-gate） | 0/1/2 |

两命令分工固定：`spec` 只对官方契约负责，`validate` 对本仓额外结构约束负责——同一条 description 在两者结论可以不同且属预期（例如未双引号：`spec` PASS、`validate` FAIL），交付报告以 `validate` 为准。

约定：错误与诊断写 **stderr**，状态/数据写 **stdout**；禁止 `input()` 交互。

**改动 validator 必须带用例**：`python scripts/tests/test_validator.py`（`unittest`，零第三方依赖）锁住本文件的结构判据与「CLI 不判语义」契约；改判据而不改测试 = 未完成。

## HARD 格式与安全

1. **目录**：技能目录存在 `SKILL.md`。
2. **Frontmatter**：YAML 块完整；必含 `name`、`description`。
3. **name**：与父目录名一致；`[a-z0-9-]`；长度 ≤64；无首尾连字符；无 `--`。
4. **description 结构**：存在、非空、单行 string（禁 `|` `>` 块标量）、≤1024、双引号包裹、无反斜杠、不含尖括号 `<` `>`（本仓约定）、无未完成占位符（`{{…}}` / `TODO`）。
   **validator 只判结构**：自 v2.3.0 起不再统计触发词、核心意图关键词或引号词数量，也不用正则判「主动触发句式」——实测那些词法判据会把裸词表判成高分、把自然中文描述判成硬错误，反向激励堆词。语义与触发质量由评审/优化模式按 `optimization.md` §10、§11 判断。
5. **顶层字段白名单**：仅 `name` / `description` / `license` / `compatibility` / `metadata` / `allowed-tools`；`triggers`/`tags` 等禁止顶层。**字段顺序只是本仓建议，官方无顺序要求 → 顺序不一致记 advisory，不阻塞交付**。
   **`metadata` 是 string→string 映射**（官方 spec：*"A map from string keys to string values"*）：值写成裸 `true` / `1` / `null` 会被严格消费者解析成布尔/数字而加载失败，本仓 `disable-model-invocation` 一类字段须写作 `"true"`。此条为 HARD——它是官方契约，不是本仓品味。
6. **版本 SSOT**：`metadata.version`（三段式 `X.Y.Z`）为机器事实；变更史在技能根 `CHANGELOG.md`。**不要求** SKILL 正文头部版本块与文末版本历史（有 CHANGELOG 时可省略）。
7. **引用**：主文档与保留 references 中的相对路径必须真实存在。
8. **非破坏**：重构/归档不得覆盖用户未授权的技能产物；写文件走 plan-gate。
9. **脚本（CONDITIONAL）**：存在 `scripts/` 时——无 `input()` 交互；支持 `--help`；退出码 0=PASS/1=FAIL/2=ERROR；错误走 stderr。**无 `scripts/` → 本组检查 = N/A，不记缺陷。**
10. **密钥**：任何配置/文档不得写入 token、密码、连接串。
11. **Runtime/Governance 分离**：不得把 skill-workshop 治理条文写入被审计技能的运行时文档。
12. **无平行流程**：整合方法论后不得出现「旧流程 + 新流程」双跑；单一审计主路径。

## 判据来源与严重度（v2.4.0 反向审计）

每条判据必须能说出来源等级；说不出来源的 blocker 一律降级或删除。审计中实测存在「归档作者体系的写法偏好」被实现成硬闸门并标 `incident-backed`、却无任何事故登记的情形。

| 来源等级 | 例 | 严重度 |
| --- | --- | --- |
| 官方 spec | name 格式、字段白名单、`metadata` 值必须是 string | HARD |
| 本仓约定（有解析/加载后果） | description 双引号与禁反斜杠、版本 SSOT、相对链接真实存在 | HARD |
| 本仓约定（纯风格） | description 含斜杠、半角冒号 | advisory |
| 已归档作者体系（`docs/archive/`，v2 运行时不再强制） | 决策矩阵↔强规则摘要互锁、`references/examples/input-template-*.md` 固定三章节与命名、示例速查表 `index.md` | advisory |

降级不等于删除：归档写法在 `ErgeAIA-skills/AGENTS.md`「架构偏好」里仍是推荐项，判据保留为提示，且不再要求 `@步骤N:` 标记（`creation.md` 禁止在新建流程注入步骤级标记）。

## 条件检查 N/A（不把不适用判成缺陷）

| 无此能力时 | 对应检查 |
| --- | --- |
| 无 `scripts/` | 脚本纪律 / P 系列 |
| 无 eval 且不要求评测 | V4/V5、Eval Review |
| 无家族 baseline 指定 | family-diff 类 |
| 无编排共享字段 | 字段争用 |
| 无已知 recurring gotcha | 不强制 Gotchas 章 |

## 版本与发布对齐（本仓库）

推送前核对：

```text
SKILL.md metadata.version = CHANGELOG.md 顶部版本 = 根 README 索引版本
```

技能增删或升版后，在 `Skills-Depot` 执行：

```bash
uv run --no-project python scripts/sync_skills_browser.py
```

## validate 使用注意

- 建议传显式路径：`validate path/to/skill-dir`。
- `validate` findings 可能含 advisory；**FAIL 才阻塞**「通过」结论。
- `spec` 与 `validate` 职责不同；交付前两者都跑。
- **解释器决定类型判据是否生效**：无 PyYAML 时（例如 `uv run --no-project python`）frontmatter 走降级解析，所有标量都是字符串，`metadata` 值类型一类的检查无法触发。此时 `validate` 会输出「PyYAML 不可用…降级解析」警告——看到该警告就不把 PASS 当作类型合规证据，需用带 PyYAML 的解释器复跑。
- 重构/方法论整合后：对**本技能自身**也跑 `spec` + `validate`，并记录 Before/After 体量。

## package 注意

- 默认 **dry-run**；`--write` 生成 `.skill` 且须 plan-gate。
- 打包跳过 `dist/`、`__pycache__/`、评测运行目录及 `docs/archive/` 等。

## 报告中的验证表述

- 机器 FAIL → 不得写「校验通过」。
- 未跑命令 → 不得写「已验证」；写「未验证」。
- 归档工具链结果不得伪装成运行时 CLI 结果。

## 失败处理顺序

1. 读 stderr 具体条目（含修复建议）。
2. 改源文件，不改断言来「让测试变绿」。
3. 重跑 `spec` + `validate` 至 PASS。
4. 涉及版本变更 → 同步 CHANGELOG 与根 README → 跑 sync 脚本。
