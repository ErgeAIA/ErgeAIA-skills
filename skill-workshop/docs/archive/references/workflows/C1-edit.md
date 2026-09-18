---
name: C1-edit
description: C1 子阶段；编辑 SKILL.md 内容 + V0 验证 + 打包；C1.3 终态。
version: 1.2.0
trigger-when: "创建 Skill 编辑与验证阶段"
---

# C1.3 编辑与验证


## 编辑 SKILL.md 并验证

### 编辑 SKILL.md


- 编辑前读取 `references/authoring/skill-markup-guide.md` 和 `references/authoring/versioning-and-validation.md`
- 主 SKILL.md 只做路由层（参考 `references/authoring/progressive-disclosure-patterns.md`）
- 长内容下沉到 `references/`
- **必须使用语义化标记**：
  - `## ` 定义工作流
  - `### step N:` 定义步骤
  - `- ` 定义可执行事项
  - HTML 注释元数据：``、``、``、``
- 先实现 `scripts/`、`references/`、`assets/`，再回写 SKILL.md 导航
- 编辑完成后同步更新 version（三处一致）

### 验证


```bash
python scripts/skill_cli.py validate <skill-path>
```

- PASS → 进入步骤 3
- FAIL → 修复后重跑

### 可选扩展


- **评测**：进入 [C2-evaluate.md](C2-evaluate.md)
- **打包**：`python scripts/skill_cli.py package <skill-path>`
- **评审质量**：进入 W1-W7 评审主链

---

## 验证闭环

- V1：SKILL.md 存在且 frontmatter 完整
- V2：`validate` 返回 PASS
- V3：description 覆盖触发条件
- V4：有正面/负面触发测试集（参考 `references/config/trigger-test-set.md`）
