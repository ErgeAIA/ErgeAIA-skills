---
name: V0-validate
description: Skill 合规校验工作流；产出 PASS/FAIL 结论；增第 7-8 步版本三处一致 + frontmatter 字段过度工程化硬校验。
version: 1.1.1
<!-- @类型: 工作流 -->
<!-- @优先级: 必须 -->
role: Workflow (Judge)
trigger-when: 用户明确要求"校验/validate"时触发，独立于评审模式
reads-from:
  - references/specs/spec.md             # frontmatter 字段允许表（官方规范）
  - references/specs/validate.md         # 基础硬校验清单
  - references/authoring/versioning-and-validation.md  # 版本三处一致性硬校验
---

# V0 合规校验（基于官方 spec）

> **版本**: v1.1.1
> **改动**: v1.1.1 - 第 7 步明确版本块可选（无版本块时跳过三处比对、不判 FAIL）；输出示例计数随 8 步更新（6/6 → 8/8）

## 目标
对给定 Skill 仓库做硬性规范校验，产出 PASS/FAIL 结论。
基础规则见 `references/specs/spec.md` 与 `references/specs/validate.md`。
**版本一致性硬校验**（frontmatter `version` / 头部版本块 / 文末首条版本历史 三处必须一致）见 `references/authoring/versioning-and-validation.md` 第 1-3 节；任何一处不一致 → 整体 FAIL。

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

### 第 7 步：版本三处一致性（来自 versioning-and-validation.md）
- frontmatter `version` 字段值 == 头部版本块 `> **版本**: vX.Y.Z` 值
- frontmatter `version` 字段值 == 文末首条 `## 版本历史` 第一条版本号
- 三者任一不一致 → 整体 FAIL，错误信息形如 `[version-mismatch] frontmatter=0.2.0, header=0.2.1, history=0.2.0`
- 版本块（头部版本块 / 文末版本历史）**本身可选**：当文档完全无版本块时，跳过三处比对，**不判 FAIL**，仅在错误信息中标注 `missing-header` / `missing-history` 供人工参考
- 仅当"存在版本块但其中任意一处与 frontmatter `version` 不一致"时才判 `version-mismatch` FAIL

### 第 8 步：Frontmatter 字段过度工程化（来自 frontmatter-style-guide.md）
- frontmatter 内是否塞入了应归 VERSION.md 的元数据（如 `created` / `updated` / `origin`）
- 命中即 P1 提示，**不阻断 PASS**，但写入报告

---

## 输出格式

**通过**：
```
**Validation**: PASS
- 全部检查通过
- 检测项：8 / 8
```

**失败**：
```
**Validation**: FAIL
- [name] 'My-Skill' 含大写字符（必须为 hyphen-case）
- [description] 超过 1024 字符（实际 1203）
- [directory] 目录名 'my_skill' 与 name 字段 'my-skill' 不一致
- 检测项：3 / 8 通过
```

---

## 规则
- 每项失败必须给出具体值与期望值
- 失败项按文件结构 → frontmatter → 字段 → 目录的顺序输出
- 任意一项失败 → 整体 FAIL
- 全部通过 → PASS

---

## 版本历史

- **v1.1.1** (2026-08-22) - 第 7 步明确版本块可选（无版本块时跳过三处比对、不判 FAIL）；输出示例计数随 8 步更新（6/6 → 8/8）
- **v1.1.0** (2026-06-18) - 增第 7 步版本三处一致性硬校验（frontmatter / 头部 / 文末首条）；增第 8 步 frontmatter 字段过度工程化扫描（来自 frontmatter-style-guide.md）
- **v1.0.0** (2026-06-14) - 初版：6 步硬校验（文件结构 / frontmatter 格式 / 字段允许表 / name / description / 目录名）
