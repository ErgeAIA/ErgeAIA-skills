---
version: 2026-05
source: anthropics-skills/skill-creator
role: Rubric (examples & thresholds only)
trigger-when: W7 description 审计阶段（T1-T5 判定）
consumed-by: W7
---

# 意图校准示例库

> 本文件是 W7 的标尺与示例库，**不做判定**。
> W7 引用本文件的定义与示例完成 T1–T5 的判定。

---

## 1. 三维触发矩阵定义

| 维度                 | 含义                                | 正例                                                           | 反例              |
| -------------------- | ----------------------------------- | -------------------------------------------------------------- | ----------------- |
| 意图 (Intent)        | 用户想「做什么」？(动词)            | 提取、合并、重构、审计、部署                                   | "关于 PDF 的工具" |
| 技术特征 (Technical) | 涉及哪些代码模式 / 文件类型 / API？ | `.jsonc` 文件、`base44.entities.*`、`@文件引用`、`Python 脚本` | "处理文件"        |
| 项目环境 (Context)   | 处于什么框架 / 堆栈 / 目录结构？    | `Vite` 项目、`Next.js`、`src/api/`、`./scripts`                | "任意项目"        |

---

## 2. Pushy 风格对照

| 类型         | 示例                                                                                                                                                   |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 被动（反例） | `Provides tools for analyzing skills.`                                                                                                                 |
| 主动（正例） | `Make sure to use this skill whenever the user mentions skill analysis, refactoring, or compliance, even if they don't explicitly ask for a 'review'.` |
| 被动（反例） | `How to build a dashboard.`                                                                                                                            |
| 主动（正例） | `How to build a dashboard. Use this skill whenever the user mentions dashboards, data visualization, or wants to display company data.`                |

---

## 3. 边界声明对照

| 类型           | 示例                                                                                          |
| -------------- | --------------------------------------------------------------------------------------------- |
| 无边界（反例） | `适用于所有 Skill 相关任务。`                                                                 |
| 有边界（正例） | `适用于：Skill 创建、优化、评审、合规校验。不适用于：通用代码调试、与 Skill 无关的文档创作。` |

---

## 4. 做法优于答案对照

| 类型                | 示例                                                                                                                                                             |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Overfitting（反例） | `Join the orders table to customers on customer_id, filter where region = 'EMEA'.`                                                                               |
| 方法论（正例）      | `1. Read the schema to find relevant tables\n2. Join tables using the _id foreign key convention\n3. Apply any filters from the user's request as WHERE clauses` |

---

## 5. 解释 Why 对照

| 类型             | 示例                                                                                                                      |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------- |
| 单纯 MUST（弱）  | `MUST use parameterized queries.`                                                                                         |
| MUST + Why（强） | `Use parameterized queries to prevent SQL injection. This is critical because user input may contain malicious payloads.` |

---

## 6. 意图范围参考

| 场景                                                 | 判断                  |
| ---------------------------------------------------- | --------------------- |
| 一个 Skill 同时处理「数据库查询」+「服务器运维」     | 拆分（T4 命中）       |
| 步骤 A（提取数据）+ 步骤 B（格式化输出）总是连续发生 | 保持内聚（T4 不命中） |
| 加载 Skill 后 80% 内容在当前任务用不到               | 拆分（T4 命中）       |
| 两个候选 Skill 拆开后需加载相同 reference            | 合并（T4 不命中）     |

---

## 7. 控制校准参考

| 任务类型                         | 建议控制强度 | 建议模式                         |
| -------------------------------- | ------------ | -------------------------------- |
| 破坏性操作（删除 / 写入 / 交易） | 强           | Plan-Validate-Handoff + 显式确认 |
| 不可逆操作（API 调用 / 部署）    | 强           | Dry-run 优先                     |
| 弹性任务（文案 / 创意 / 翻译）   | 弱           | 给方向，留自由度                 |
| 探索性任务（分析 / 总结）        | 中           | 给框架，不给死答案               |
