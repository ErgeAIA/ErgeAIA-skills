# moxian 版本历史

## v0.2.1 (2026-09-26)
- README 头图替换为 tupu 真实产物横版图谱（`Inbox/tupu/moxian/moxian.svg` → `assets/banner.svg`），README 引用路径不变。

## v0.2.0 (2026-09-25)
- 清理 frontmatter：移除非规范字段 `compatibility`，仅保留 `metadata{author, version}`（与仓库其它技能一致）。
- Non-Goals 补充 `@会话` 依赖宿主能力的说明：假定宿主能注入 `@指定的会话` 上下文，否则只照当前会话、不报错也不扩展范围。
- 删除冗余产物 `assets/banner.json`（纯展示只需 `banner.svg`）。
- 首次真实运行验收通过：按三判据（证据锚点齐 / 已落档 / 概念层假设语气）跑通一次对话，认知卡存 `docs/moxian/20260925-git仓库判定与gitlink.md`。

## v0.1.0 (2026-09-14)
- 初始版本：默现技能。读当前或 @指定会话，照出「以为懂、其实没内化」的三层认知缺口（名词层→词卡 / 表达层→更锋利的问题 / 概念层→微课），默认过闸门只给 1-2 条，落 markdown 到 `docs/moxian/` 可累积。
- 理论底座一个方向一个名人：根 Polanyi（默会知识 + 隐含前提）、引擎 Nonaka（外化）、诊断 Argyris（宣称 vs 在用）、框架镜 Schön（行动反思 / 取景框），姿态取 Schein 过程咨询（不评判）。
- 主 SKILL.md 做路由，三层特征 + 证据 + 四面孔分工 + 闸门下沉 `references/mental-models.md`；认知卡模板 + docs/moxian 存档结构下沉 `references/card-templates.md`。
- 触发词「默现 / moxian / 我哪没懂 / 照一下我没懂的」，刻意避开「盲区」与 qiao 的「说不清 / 帮我看看」等已被占用的触发词。
- 明确与 vibe-buddy 边界：moxian 收割没意识到的缺口（默会 / 负空间），vibe-buddy 收割已做完的做法（显性经验），卡片与入库目录分开。
- 发版 / 推送前版本号保持 v0.1.0，不升级。
