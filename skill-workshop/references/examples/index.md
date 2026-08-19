# 场景示例索引

- 目标 Skill: `kz-skill-creator`
- 示例目录: `references/examples/`
- 使用方式: 先按主 `SKILL.md` 判断当前请求是创建、重构还是评测；如果一时拿不准用户原话更像哪条路径，再先看下面的“决策矩阵命中速查”

## 示例列表

| 示例文件 | 场景内容 | 对应工作流 |
|---|---|---|
| `input-template-generate-skill-input-template.md` | `为某个 Skill 生成输入模板` | `理解并创建Skill` |
| `input-template-skill-creator-main.md` | `用户需要创建或更新 Skill` | `理解并创建Skill` |
| `input-template-refactor-existing-skill.md` | `用户需要重构已有 Skill` | `重构现有 Skill` |
| `input-template-evaluate-existing-skill.md` | `用户需要评测已有 Skill` | `评测已有 Skill` |

## 决策矩阵命中速查

| 用户常见说法 | 命中矩阵行 | 建议先打开 |
|---|---|---|
| `帮我创建一个处理 PDF 的 Skill` | `创建 / 更新目标 Skill` | `input-template-skill-creator-main.md` |
| `把这个 Python 脚本封装成技能` | `创建 / 更新目标 Skill` | `input-template-skill-creator-main.md` |
| `帮我重构这个 Skill 的 workflow 边界` | `重构已有 Skill` | `input-template-refactor-existing-skill.md` |
| `整理这个 Skill 的 references 和验证机制` | `重构已有 Skill` | `input-template-refactor-existing-skill.md` |
| `帮我审一下这个 Skill，并保存成文档` | `评测已有 Skill` | `input-template-evaluate-existing-skill.md` |
| `看看这个 Skill 的结构有没有明显问题` | `评测已有 Skill` | `input-template-evaluate-existing-skill.md` |
| `为这个 Skill 生成场景输入模板` | `生成输入模板` | `input-template-generate-skill-input-template.md` |
