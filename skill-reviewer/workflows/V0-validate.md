---
role: Workflow (Judge)
trigger-when: 用户明确要求"校验/validate"时触发，独立于评审模式
---

# V0 合规校验（基于官方 spec）

## 目标
对给定 Skill 仓库做硬性规范校验，产出 PASS/FAIL 结论。
完整规则见 `references/specs/spec-zh.md` 与 `references/specs/validate-zh.md`。

## 与评审模式的关系
- 合规校验可**独立运行**（用户说「校验」/「validate」时只走 V0）
- 也可作为评审模式的**前置步骤**——FAIL 项自动升级为评审 P0
- 用户说「分析」/「review」时进 W1，不走 V0

---

## 校验顺序

### 第 1 步：文件结构
- `SKILL.md` 是否存在于 Skill 目录内
- 文件是否可读（编码合法）

### 第 2 步：Frontmatter 格式
- 文件首行是否为 `---`
- 是否有配对的 `---` 结束行
- 中间内容是否为合法 YAML（无 tab 缩进、无重复 key）

### 第 3 步：允许的属性
仅允许以下顶层 key：
- `name`
- `description`
- `license`
- `compatibility`
- `metadata`
- `allowed-tools`

检查项：
- 拼写错误（如 `descriptions`、`Name`、`Description`）
- 未知属性（顶层 key 必须在允许列表中）
- 大小写错误

### 第 4 步：name 字段
- 存在且为字符串
- 仅含小写字母 / 数字 / 连字符
- 不以连字符开头或结尾
- 不含连续连字符（`--`）
- 长度 ≤ 64
- **目录名必须与 name 一致**

### 第 5 步：description 字段
- 存在且为字符串
- 不含 `<` 或 `>` 字符
- 长度 ≤ 1024
- 非空（去除空白后长度 > 0）

### 第 6 步：目录名匹配
- Skill 目录名 == `name` 字段值（精确匹配）

---

## 输出格式

**通过**：
```
**Validation**: PASS
- 全部检查通过
- 检测项：6 / 6
```

**失败**：
```
**Validation**: FAIL
- [name] 'My-Skill' 含大写字符（必须为 hyphen-case）
- [description] 超过 1024 字符（实际 1203）
- [directory] 目录名 'my_skill' 与 name 字段 'my-skill' 不一致
- 检测项：3 / 6 通过
```

---

## 规则
- 每项失败必须给出具体值与期望值
- 失败项按文件结构 → frontmatter → 字段 → 目录的顺序输出
- 任意一项失败 → 整体 FAIL
- 全部通过 → PASS
