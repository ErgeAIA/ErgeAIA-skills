---
version: 2026-05
source: https://agentskills.io/specification
translator: skill-reviewer
trigger-when: V0 合规校验阶段（配合 validate-zh.md 使用）
---

# Agent Skills 规范（中文版）

> Agent Skills 格式的完整规范定义。

## 目录结构

一个 Skill 是包含至少 `SKILL.md` 文件的目录：

```
skill-name/
└── SKILL.md          # 必需
```

可选包含 `scripts/`、`references/`、`assets/` 等目录辅助你的 Skill。

## SKILL.md 格式

`SKILL.md` 文件必须包含 YAML frontmatter 加 Markdown 正文。

### Frontmatter（必需）

```yaml
---
name: skill-name
description: 描述该 Skill 做什么以及何时使用。
---
```

含可选字段的示例：

```yaml
---
name: pdf-processing
description: 从 PDF 文件提取文本和表格、填写表单、合并文档。
license: Apache-2.0
metadata:
  author: example-org
  version: "1.0"
---
```

| 字段            | 必需 | 约束                                                           |
| --------------- | ---- | -------------------------------------------------------------- |
| `name`          | 是   | 最长 64 字符。仅小写字母、数字、连字符。不以连字符开头或结尾。 |
| `description`   | 是   | 最长 1024 字符。非空。描述做什么和何时使用。                   |
| `license`       | 否   | 协议名或捆绑协议文件的引用。                                   |
| `compatibility` | 否   | 最长 500 字符。环境要求说明（目标产品、系统包、网络访问等）。  |
| `metadata`      | 否   | 任意键值映射，存储额外元数据。                                 |
| `allowed-tools` | 否   | 空格分隔的预批准工具列表（实验性）。                           |

#### name 字段

必需的 `name` 字段：
- 长度 1-64 字符
- 仅含 unicode 小写字母数字与连字符（`a-z`、`0-9`、`-`）
- 不以 `-` 开头或结尾
- 不含连续连字符（`--`）
- **必须与父目录名一致**

合法示例：`pdf-processing`、`data-analysis`、`code-review`

非法示例：
- `PDF-Processing`（含大写）
- `-pdf`（以连字符开头）
- `pdf--processing`（连续连字符）

#### description 字段

必需的 `description` 字段：
- 长度 1-1024 字符
- 应同时描述「做什么」与「何时使用」
- 应包含帮助 Agent 识别相关任务的关键词

**优秀示例**：
```yaml
description: 从 PDF 文件提取文本和表格、填写 PDF 表单、合并多个 PDF。当处理 PDF 文档或用户提到 PDF、表单、文档提取时使用。
```

**糟糕示例**：
```yaml
description: 帮助处理 PDF。
```

#### license 字段

可选的 `license` 字段：
- 指定 Skill 的协议
- 建议保持简短（协议名或捆绑协议文件名）

示例：
```yaml
license: Proprietary. LICENSE.txt has complete terms
```

#### compatibility 字段

可选的 `compatibility` 字段：
- 提供时长度 1-500 字符
- 仅当 Skill 有特定环境要求时使用
- 可指明目标产品、需要的系统包、网络访问需求等

示例：
```yaml
compatibility: Designed for Claude Code (or similar products)
```
```yaml
compatibility: Requires git, docker, jq, and access to the internet
```

> 大多数 Skill 不需要 `compatibility` 字段。

#### metadata 字段

可选的 `metadata` 字段：
- 字符串键到字符串值的映射
- 客户端可用于存储规范未定义的额外属性
- 建议键名足够独特以避免冲突

#### allowed-tools 字段

可选的 `allowed-tools` 字段：
- 空格分隔的预批准工具列表
- 实验性。各 Agent 实现支持情况可能不同

示例：
```yaml
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

### 正文内容

frontmatter 之后的 Markdown 正文包含 Skill 指令。无格式限制，写任何能帮 Agent 有效完成任务的内容。

推荐章节：
- 分步指令
- 输入输出示例
- 常见边界情况

注意：Agent 决定激活该 Skill 后会加载整个文件。考虑把较长的 `SKILL.md` 内容拆分到引用文件。

## 可选目录

### scripts/
包含 Agent 可运行的可执行代码。脚本应：
- 自包含或清楚记录依赖
- 包含有用的错误信息
- 优雅处理边界情况

支持的语言取决于 Agent 实现，常见有 Python、Bash、JavaScript。

### references/
包含 Agent 按需阅读的额外文档：
- `REFERENCE.md` - 详细技术参考
- `FORMS.md` - 表单模板或结构化数据格式
- 领域特定文件（`finance.md`、`legal.md` 等）

保持单个引用文件聚焦。Agent 按需加载，文件越小，上下文消耗越少。

### assets/
包含静态资源：
- 模板（文档模板、配置模板）
- 图片（图表、示例）
- 数据文件（查找表、Schema）

## 渐进式披露

Skill 应为高效使用上下文而设计：

1. **元数据**（~100 tokens）：所有 Skill 启动时加载 `name` 与 `description`
2. **指令**（建议 <5000 tokens）：Skill 激活时加载完整 `SKILL.md` 正文
3. **资源**（按需）：`scripts/`、`references/`、`assets/` 中的文件仅在需要时加载

保持主 `SKILL.md` 在 500 行以内。详细参考资料移到独立文件。

## 文件引用

引用 Skill 中其他文件时，使用相对于 Skill 根目录的路径：

```markdown
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
scripts/extract.py
```

引用层级保持在距 `SKILL.md` 一级深度。避免深度嵌套的引用链。

## 校验

使用官方 `skills-ref` 参考库校验你的 Skill：

```bash
skills-ref validate ./my-skill
```

这会检查你的 `SKILL.md` frontmatter 是否合规、是否遵循命名约定。
