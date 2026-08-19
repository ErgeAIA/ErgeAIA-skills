---
name: C1-edit
description: C1 子阶段；编辑 SKILL.md 内容 + V0 验证 + 打包；C1.3 终态。
version: 1.2.0
trigger-when: "创建 Skill 编辑与验证阶段"
---

# C1.3 编辑与验证

<!-- @类型: 工作流 -->
<!-- @优先级: 必须 -->

## @工作流: 编辑 SKILL.md 并验证

### @步骤1: 编辑 SKILL.md

<!-- @类型: 操作步骤 -->
<!-- @验证点: SKILL.md 结构清晰且关键资源可被引用 -->

- @动作: 编辑前读取 `references/authoring/skill-markup-guide.md` 和 `references/authoring/versioning-and-validation.md`
- @动作: 主 SKILL.md 只做路由层（参考 `references/authoring/progressive-disclosure-patterns.md`）
- @动作: 长内容下沉到 `references/`
- @动作: **必须使用语义化标记**：
  - `## @工作流:` 定义工作流
  - `### @步骤N:` 定义步骤
  - `- @动作:` 定义可执行事项
  - HTML 注释元数据：`@类型`、`@优先级`、`@验证点`、`@验证方式`
- @动作: 先实现 `scripts/`、`references/`、`assets/`，再回写 SKILL.md 导航
- @动作: 编辑完成后同步更新 version（三处一致）

### @步骤2: 验证

<!-- @类型: 操作步骤 -->
<!-- @验证点: validate 返回 PASS -->

```bash
python scripts/skill_cli.py validate <skill-path>
```

- @动作: PASS → 进入步骤 3
- @动作: FAIL → 修复后重跑

### @步骤3: 可选扩展

<!-- @类型: 操作步骤 -->

- @动作: **评测**：进入 [C2-evaluate.md](C2-evaluate.md)
- @动作: **打包**：`python scripts/skill_cli.py package <skill-path>`
- @动作: **评审质量**：进入 W1-W7 评审主链

---

## 验证闭环

- V1：SKILL.md 存在且 frontmatter 完整
- V2：`validate` 返回 PASS
- V3：description 覆盖触发条件
- V4：有正面/负面触发测试集（参考 `tests/trigger-test-set.md`）
