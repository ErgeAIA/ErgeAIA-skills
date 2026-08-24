---
trigger-when: "创建 Skill 时确认目录归属"
name: naming-and-ownership
description: Skill 目录/文件命名与归属规范。用于区分“本技能（skill-workshop）”与“目标技能”，并统一 references/scripts/assets 等目录语义。
version: 1.6.0
---

# Skill 目录与命名规范（归属说明）

<!-- @类型: 参考指南 -->
<!-- @目的: 统一 Skill 目录/文件命名，并明确内容归属（本技能 vs 目标技能） -->
<!-- @场景: 创建/迭代/评测 Skill，或需要在仓库内放置多份 Skill 时 -->
<!-- @前置条件: 已理解“本技能/目标技能”术语 -->

> **一句话**: 用路径就能判断“属于哪个技能、用于什么阶段”
> **版本**: v1.6.0
> **用途**: 目录与文件命名规范
> **适用范围**: 本技能与所有目标技能

## 1. 术语（强制）

- **本技能**：skill-workshop（本目录），用于指导你创建/迭代/评测目标技能
- **目标技能**：你正在创建/修改/评测的那个 Skill
- **目标技能工作流**：目标技能的 SKILL.md 里的 `## @工作流:`
- **本技能工作流**：本技能 SKILL.md 里的流程（如创建流程、评测闭环）

## 2. 目录语义（强制）

### 2.1 目标技能（你正在做的那个 Skill）

目标技能目录结构只表达“这个技能如何被使用”，不放本技能的工程化工具链：

```
<target-skill>/
├── SKILL.md
├── scripts/        # 目标技能的可执行代码（run/validate_skill 等）
├── references/     # 目标技能的参考资料（领域知识/接口/流程细节）
└── assets/         # 目标技能输出会用到的资源（模板/示例/静态文件）
```

命名规则：
- 目标技能名使用 `kebab-case`（如 `pdf-tools`、`dash-developer`）
- references 内的文件名优先“面向使用场景”（如 `api.md`、`examples.md`、`troubleshooting.md`）

### 2.2 本技能（skill-workshop）

本技能目录结构表达“如何创建/评测目标技能”，分区必须清晰：

```
skill-workshop/
├── SKILL.md
├── scripts/
│   ├── skill_cli.py                 # 唯一公开 CLI 入口（init/package/validate/eval/loop/...）
│   └── _impl/                       # 子命令背后的实现模块（不直接作为公开入口）
├── references/
│   ├── authoring/                   # 编写目标技能用（规范/工作流模式/命名规则）
│   │   ├── skill-foundations.md
│   │   ├── business-to-workflow-mapping.md
│   │   ├── skill-markup-guide.md
│   │   ├── workflow-patterns.md
│   │   ├── versioning-and-validation.md
│   │   └── naming-and-ownership.md
│   ├── workflows/                   # 面向人阅读的工作流与业务流程说明
│   └── evaluation/                  # 评测闭环用（如何评测/产物结构/回放与汇总）
│       └── eval-loop.md
├── agents/                          # 评测闭环提示词（比较/分析/打分）
└── assets/                          # 本技能输出资源（如回放模板）
```

命名规则：
- `references/authoring/*`：只写“如何把目标技能写对/写稳”
- `references/workflows/*`：只写“本技能有哪些工作流、这些工作流之间是什么关系”
- `references/evaluation/*`：只写“如何评测/复盘/迭代目标技能”
- `agents/*`：只放评测闭环提示词，不放通用写作规范
- `assets/eval_review.html`：评测回放页模板资源
- `assets/eval_set_editor.html`：eval JSON 编辑工具页
- `scripts/skill_cli.py`：唯一公开入口；共享逻辑与具体实现统一下沉到 `scripts/_impl/`
- `scripts/_impl/*.py`：默认不再作为公开入口，避免重复入口扩散
- 不强制文件名前缀：通过目录语义区分归属与用途

## 3. 文件归属判断（快速表）

| 你看到的路径/文件 | 属于哪个技能 | 用途 |
|---|---|---|
| `<target-skill>/SKILL.md` | 目标技能 | 目标技能说明/工作流/步骤 |
| `<target-skill>/scripts/*` | 目标技能 | 目标技能执行与验证 |
| `skill-workshop/scripts/skill_cli.py` | 本技能 | 创建/打包/校验/评测统一入口 |
| `skill-workshop/scripts/_impl/*` | 本技能 | 各入口脚本背后的共享实现模块 |
| `skill-workshop/references/authoring/*` | 本技能 | 目标技能写作规范与模式 |
| `skill-workshop/references/workflows/*` | 本技能 | 本技能自身的工作流与业务流程说明 |
| `skill-workshop/references/evaluation/*` | 本技能 | 评测闭环规范与产物说明 |
| `skill-workshop/agents/*` | 本技能 | 评测比较/分析/打分提示词 |
| `skill-workshop/assets/eval_review.html` | 本技能 | 评测回放页模板 |
| `skill-workshop/assets/eval_set_editor.html` | 本技能 | eval JSON 编辑工具页 |

---

## 版本历史

- **v1.6.0** (2026-05-13) - 新增 `references/workflows/` 目录语义，纳入本技能工作流与业务流程说明文档
- **v1.5.0** (2026-05-13) - 更新本技能目录示意树，补入新增的 authoring 参考文档
- **v1.4.0** (2026-03-09) - 明确区分 assets 中的回放模板与 eval JSON 编辑工具页
- **v1.3.0** (2026-03-08) - 删除 eval-viewer 目录，将回放生成逻辑并入 scripts/_impl，模板收敛到 assets
- **v1.2.0** (2026-03-08) - 删除 scripts 根目录薄包装入口，明确 skill_cli.py 为唯一公开入口
