---
trigger-when: "设计 Skill 渐进式披露结构时"
name: progressive-disclosure-patterns
description: 渐进式披露设计模式参考。当你需要把目标 Skill 的长示例、变体细节或模板化内容下沉到 references 时使用此参考。
version: 1.9.0
---

# 渐进式披露模式参考

<!-- @类型: 参考指南 -->
<!-- @目的: 指导如何把目标 Skill 的细节从 SKILL.md 下沉到 references -->
<!-- @场景: SKILL.md 过长、内容变体过多、示例或模板占用上下文 -->
<!-- @触发条件: 当需要压缩正文、保留导航并把细节移入 references 时 -->

> **一句话**: 主文档只保留核心流程，细节、变体和模板放进 references
> **版本**: v1.8.0
> **用途**: 渐进式披露设计参考
> **适用范围**: 所有需要控制正文长度的目标 Skill

## 1. 何时下沉

内容分三层落点：

- **AI 专属（留在 `SKILL.md`）**：触发条件、主工作流、关键决策点、去哪个参考文件读什么内容、强制规则。
- **人类可读（新建 `README.md`）**：技能是什么、何时用/不用、人类如何调用、设计哲学、进阶指引。**这些内容禁止留在 SKILL.md**——SKILL.md 是给执行 Agent 读的指令，不是给人类读的文档。
- **按需细节（下沉 `references/`）**：优先把以下移出 SKILL.md 正文：
  - 大段示例或代码块
  - 多框架、多领域、多提供商变体
  - 固定模板、报告格式、版本校验清单
  - 评测闭环、回放、复盘等次级流程

## 2. 常用模式

### 2.1 高层指南 + 按需参考

适合“主流程简单，扩展场景很多”的 Skill。

```text
SKILL.md
references/
├── forms.md
├── api.md
└── examples.md
```

正文只写：

- 基础做法
- 什么时候读 `forms.md`
- 什么时候读 `api.md`
- 什么时候读 `examples.md`

### 2.2 按领域或变体拆分

适合不同业务域、框架、云厂商、语言栈共存的 Skill。

```text
references/
├── aws.md
├── gcp.md
├── finance.md
└── sales.md
```

正文只负责“如何选择哪一份参考”，不要把所有变体混在一起。

### 2.3 主流程 + 条件细节

适合默认流程很稳定，但少量高级场景需要额外说明的 Skill。

正文写默认路径；把“修订模式”“高级排错”“底层格式细节”拆成独立参考。

### 2.4 主路由 + 场景输入模板

适合工作流路由本身稳定，但用户的高频使用场景会逐渐沉淀出更高效输入方式的 Skill。

```text
SKILL.md
references/
├── templates/
│   └── scenario-input-template.md
└── examples/
    ├── input-template-<english-slug>.md
    └── index.md
```

分工建议：

- `SKILL.md`：保留工作流路由、决策树、进入条件和执行步骤
- `references/templates/scenario-input-template.md`：提供高频使用场景下的一次性输入模板；优先复制 [scenario-input-template.md](../templates/scenario-input-template.md) 的固定结构，再按当前场景做最小改写
- `references/examples/*.md`：存放基于工作流自动生成或继续人工收敛的场景示例文档，推荐命名为 `input-template-<english-slug>.md`
- `references/examples/index.md`：轻量列出当前已有示例、场景内容与对应工作流，方便快速检索

约束：

- 模板文档只辅助输入补全，不参与路由判断
- 模板文档应显式写出“本文档不负责工作流路由”
- 正文中必须写清“何时读取它”，例如“当用户进入某个高频场景但输入还不够完整时”
- 如果用户信息已经足够，不应强制回到模板
- 每个高频场景默认保留 1 个主输入模板；只有存在稳定输入分支时，才扩展到 2-3 个模板
- 如果某个场景需要 3 个以上模板，优先回到 `SKILL.md` 检查是否只是同一场景下不同目的的差异
- 模板固定结构建议至少包含 `适用场景`、`建议提供的信息`、`可直接复制输入模板`
- 若目标 Skill 的工作流信息较完整，可运行 `python scripts/skill_cli.py generate-templates <skill-path>` 自动生成草稿，默认输出到 `references/examples/`，并自动更新 `references/examples/index.md`

## 3. 写法建议

- 一份参考文件只解决一类问题
- 文件名尽量表达使用场景，而不是内部来源
- 在正文中写清“何时读它”，不要只放裸链接
- 避免 references 之间再深层跳转，尽量让 `SKILL.md` 成为一级导航入口

## 4. 验收标准

- `SKILL.md` 保持在可快速浏览的体量内（≤500 行）
- 人类可读内容已从 SKILL.md 剥离到 `README.md`，SKILL.md 仅含 AI 专属与指针
- 正文中每个非核心主题都有明确去向
- 所有引用路径（含代码块内、正文裸路径）真实存在，新增 references 带 `trigger-when`
- 变体细节不再堆积在主流程里

---

## 版本历史

- **v1.9.0** (2026-08-19) - 内容落点改为三层模型（AI 专属 SKILL.md / 人类可读 README / 按需 references），明确人类可读内容禁止留在 SKILL.md；§4 验收标准强化为「所有引用路径（含代码块/裸路径）真实存在 + 新增 references 带 trigger-when」
- **v1.8.0** (2026-05-02) - 修正目录职责：固定模板来源保留在 `references/templates/`，自动生成的场景示例文档改回 `references/examples/`
- **v1.7.0** (2026-05-02) - 取消模板目录分层，统一放回 `references/templates/`，并引入表格版 `index.md` 做轻量索引
- **v1.6.0** (2026-05-02) - 补充模板生成路径分层：人工模板在 `references/templates/`，自动生成草稿在 `references/templates/generated/`
- **v1.5.0** (2026-05-02) - 将输入模板视角从“工作流”切换到“使用场景”，并改用 `scenario-input-template.md` 作为基线模板
- **v1.4.0** (2026-05-02) - 将通用输入模板目录从 `examples` 调整为 `templates`，并精简固定结构

---
