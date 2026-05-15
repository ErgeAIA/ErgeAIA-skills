---
version: 2026-05
source: agentskills validate.md
translator: skill-reviewer
trigger-when: V0 合规校验阶段（spec-zh.md 的配套规则）
---

# Skill 校验检查清单（中文版）

Agent Skills 的快速校验清单。在完整评审前，用此验证 Skill 是否满足基本要求。

## 如何校验

给定 Skill 路径（如 `skills/my-skill/`），按顺序执行以下检查：

### 1. 文件结构
- [ ] Skill 目录中存在 `SKILL.md` 文件

### 2. Frontmatter 格式
- [ ] 文件以 `---`（YAML frontmatter 分隔符）开头
- [ ] frontmatter 以独占一行的 `---` 结束
- [ ] 分隔符之间的内容是合法 YAML

### 3. 允许的属性

frontmatter 仅允许以下顶层属性：

| 属性            | 必需 |
| --------------- | ---- |
| `name`          | 是   |
| `description`   | 是   |
| `license`       | 否   |
| `compatibility` | 否   |
| `metadata`      | 否   |
| `allowed-tools` | 否   |

- [ ] 无意外属性（检查拼写错误，如 `descriptions`、`Name` 等）

### 4. name 校验
- [ ] `name` 字段存在
- [ ] 值为字符串（不是数字或列表）
- [ ] 仅使用 hyphen-case：小写字母（`a-z`）、数字（`0-9`）、连字符（`-`）
- [ ] **不**以连字符开头
- [ ] **不**以连字符结尾
- [ ] **不**含连续连字符（`--`）
- [ ] 最长 64 字符

**合法示例**：`pdf-processing`、`code-review`、`my-skill-v2`

**非法示例**：
- `PDF-Processing`（含大写）
- `-pdf`（以连字符开头）
- `pdf--tool`（连续连字符）

### 5. description 校验
- [ ] `description` 字段存在
- [ ] 值为字符串（不是数字或列表）
- [ ] **不**含尖括号（`<` 或 `>`）
- [ ] 最长 1024 字符
- [ ] 非空（有实际内容）

### 6. 目录名匹配
- [ ] Skill 目录名与 `name` 字段值一致

## 校验结果格式

按以下格式报告校验结果：

```
**Validation**: [PASS/FAIL]
- [列出每个失败项的具体细节]
```

### 通过示例

```
**Validation**: PASS
- 全部检查通过
```

### 失败示例

```
**Validation**: FAIL
- name 'My-Skill' 含大写字符（必须为 hyphen-case）
- description 超过 1024 字符（实际 1203）
```

## 常见失败速查

| 问题                      | 修复方法                              |
| ------------------------- | ------------------------------------- |
| `name` 含大写             | 转小写：`My-Skill` → `my-skill`       |
| `name` 含空格             | 替换为连字符：`my skill` → `my-skill` |
| `name` 含下划线           | 替换为连字符：`my_skill` → `my-skill` |
| `description` 含 `<tags>` | 移除尖括号或转义                      |
| 未知属性                  | 检查拼写，不在允许列表则移除          |
| 缺少 frontmatter          | 添加 `---` 分隔符与必需字段           |
