---
trigger-when: 创建新 Skill、用 init 生成骨架后填写内容、或需要极简创建规范时
name: creation
description: 极简创建规范：职责/输入输出契约/基础结构；纯净 Markdown 模板（无步骤级 @ 标记）。
---

# 极简创建规范（creation）

## 创建时只定义三件事

1. **职责**：一句话说明这个 skill 解决什么用户任务（连贯任务单元，不是「只能有一步」）。
2. **输入输出契约**：用户/上游提供什么；skill 必须产出什么；失败时如何表现。
3. **基础结构**：`SKILL.md` 必填 frontmatter；可选 `references/` / `scripts/` / `assets/` **仅在确有需要时**再建。

不做：默认铺开多级 workflow 编号体系、强制语义化 `@` 标记、为「完整性」预埋 scripts。

## CLI 脚手架

```bash
python scripts/skill_cli.py init <skill-name> --path <parent-dir> --write
```

- 默认 dry-run，只预览将创建的路径。
- `--write` 真正落盘；AI 调用须带 plan-gate（见 CLI `--help`）。
- 生成后立即：补全 `description` 与正文 TODO → 跑 `validate` / `spec`。

## 纯净 SKILL.md 模板（复制即用）

```markdown
---
name: your-skill-name
description: "一句话说明解决什么问题 + 何时触发（含触发词）+ Not for 边界。Use this skill when ... Not for: ..."
metadata:
  author: your-name
  version: "1.0.0"
---

# your-skill-name

## 定位

[这个 skill 是什么、不是什么。]

## 何时使用

- 触发场景 1
- 触发场景 2
- Not for: [明确排除]

## 工作步骤

1. [步骤：读取什么 → 判断什么 → 产出什么]
2. [步骤]
3. [验证：如何确认完成]

## 输出契约

[必须包含的字段/文件/格式；错误时如何报告。]

## 约束

- HARD: [不可违背项]
- CONDITIONAL: [仅有某能力时才要求]
- 禁止: [误用路径]

## 资源

需要扩展细节时，再读取 `references/` 下按需创建的具体文件（带 `trigger-when`），不要在主文档堆砌全文。

## Gotchas

[仅在有高概率反直觉失败时写；没有就整节删除。]
```

## frontmatter 硬要求

| 字段 | 规则 |
| --- | --- |
| `name` | 必填；1–64；小写字母/数字/连字符；与目录名一致；无首尾/连续连字符 |
| `description` | 必填；1–1024；说明做什么 + 何时用；禁尖括号 |
| `metadata.version` | 推荐必填语义化版本；变更写入根目录 `CHANGELOG.md` |
| 其他顶层字段 | 仅官方白名单：`license` / `compatibility` / `allowed-tools`；其余进 `metadata` |

禁止顶层自定义键（如 `triggers`、`tags`）——写入 `metadata` 或正文。

## description 写法（轻量）

- 动词开头或「解决什么 + 何时触发」。
- 含用户真实说法中的触发词（中文/英文），但**核心触发词要嵌在触发句里、3-4 个以内**。
- **反模式（禁止）**：同义触发词变体罗列 >3 个（如 `review`、`audit`、`check`、`inspect` 全列）；把评测集里的查询词逐条塞进来（overfitting）；**裸词表**（只有词、没有意图句承载）。
- 必要时一句 `Not for:` 边界，减少误触发。
- 不堆砌内部机制、路径、版本号。
- **符号硬约束**（`validate` 硬拦）：必须**双引号包裹**且单行（`description: "…"`）；**禁反斜杠**（引号内是转义符，会破坏 YAML）；**禁斜杠**（改顿号；字面路径写成「某目录」）；半角冒号改全角（规格标记 `Not for:` 除外）。

## 目录骨架（可选展开）

```text
your-skill-name/
├── SKILL.md          # 必需：主文档（路由 + 硬约束 + 输出契约）
├── CHANGELOG.md      # 推荐：版本史
├── references/       # 可选：按需加载细节，带 trigger-when
├── scripts/          # 可选：确定性脚本；无则不要空目录
└── assets/           # 可选：模板/静态资源
```

原则：主文档只做路由与硬边界；细节下沉 references；**无消费者则不建文件**。

## 创建后验证

```bash
python scripts/skill_cli.py spec <skill-dir>
python scripts/skill_cli.py validate <skill-dir>
```

两者 PASS 后再交付；FAIL 时按 stderr 条目修复，不要只改报告措辞。

## 禁止事项

- 不在新建流程中注入 `@工作流` / `@步骤N` / `@动作` 等步骤级标记。
- 不把经验建议写成无条件 P0。
- 不默认生成评测集、W 流水线文档或脚本，除非用户明确要求且技能确有该能力。
- 不覆盖用户已有的同名 skill 目录。
