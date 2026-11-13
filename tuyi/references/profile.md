---
name: profile
description: 如何把一份设计规范抽成可执行的 profile：schema 字段、条款可执行化判据、锁定映射、冲突登记、轻量抽取与脱敏规则。
version: 1.0.0
trigger-when:
  - 要把设计规范变成图标规则
  - 需要新建或更新 profile
  - 规范里存在互相矛盾的条款
  - 没有完整规范，只能从现有实现反推
---

# Profile

profile 是「规范」和「可执行检查」之间的那一层：**条款本体留在规范里，profile 只存可判定的部分并指回出处**。

技能本体不写死任何产品的规范——规范换版本只换 profile，技能不动。

## schema

照 `templates/profile.example.yaml` 抄。字段分五组（动效规则独立成 `motion`）：

```yaml
profile:
  name: string            # profile 名称
  version: semver
  updated: YYYY-MM-DD
  sources:                # 规范出处，相对路径 + 行号
    - path: docs/design/iconography.md
      scope: 尺寸层级 / 状态图标 / 动作表
  icon_library: lucide
  license_note: ISC，允许商用；禁混用付费集

tokens:                   # 只用令牌名，不写死色值
  color: {text-muted, text-primary, line, state-ok, state-warn, state-error, accent}
  size: {hit-control, icon-action, icon-status, icon-source, icon-primary-nav, ...}
  stroke_width: 2.25

slots:                    # 每槽的形态契约
  status:
    size: 18
    box: 20
    border: none
    background: none
    allow_text: false
    tooltip: required
    clickable: false

mappings:                 # 已锁定的图标语义
  - slot: source
    key: local
    icon: hard-drive
    meaning: 手动安装，未关联仓库
    tooltip: 手动安装，未关联仓库
    source_ref: docs/design/iconography.md:31
    status: locked        # locked | draft

rules:                    # 可执行条款
  - id: BADGE-STATUS-01
    check: {kind: css_forbid, property: [border, background]}
    source_ref: docs/design/ui-language.md:149
    severity: major
    fix: 去掉边框与底色，只保留图标

conflicts:                # 规范内部矛盾，不替所有者裁决
  - id: C1
    topic: 状态图标尺寸
    positions:
      - {ref: docs/design/ui-baseline.md:28, says: 只允许 14/16}
      - {ref: docs/design/iconography.md:23, says: 18}
    status: pending
    interim: 16

motion:                   # 项目动效规则；不写进 mappings
  enabled: false          # 项目当前是否批准动效落地；false 时技能只出建议
  allowed_forms: [rotation, pulse, scan-line, breath, stroke-draw, shake]
  scenes:                 # 每个已批准场景一条，必须有出处与状态
    - {scene: <场景>, slot: <槽位>, form: <形态>, source_ref: <文件:行>, status: locked}
  forbidden: []           # 明确不动的场景，同样带 source_ref
  budget:
    max_primary: 1        # 同屏主动画并发上限
    max_continuous: 0     # 持续循环上限
    entrance_max_ms: null # 按项目规范填写；无值则不可判
  duration_source:
    path: null            # 项目动效令牌文件
    tokens: []            # 只引用令牌名，不写裸毫秒
  reduced_motion:
    strategy: instant     # stop | instant | opacity-only
    path: null            # reduce 规则所在文件
  state_machine:          # 过程型编排（「点了要等结果」的按钮）；可选块，无则视为未批准编排
    enabled: false        # 是否批准编排动画落地
    spec_source: null     # 编排规范/组件出处（相对路径:行）
    phases: [idle, burst, sync, done, error]  # 相位白名单；自定义命名须同步映射表
    hold:                 # 成功/失败停留时长；只引用令牌，无令牌标 proposal
      done_ms: null
      error_ms: null
    reentry: restart      # restart | ignore
    settle_fork: false    # 回落时改写静止态（分叉）是否批准
    loop_budget: per-instance                 # 每实例至多一个循环；全局并发用 budget.max_primary
  human_checks: []        # 生命周期/语义/预算等无法静态检查的条款
```

动效配置只承载**项目已批准**的规则：`locked` 场景可以执行；未批准的建议写进报告，不进 profile；`motion` 不进 `mappings`——图标语义与动画语义分开维护，规范改版时才不会互相拖累。过程编排的相位、停留、重入、回落分叉由 `state_machine` 块承载，判定见 `references/motion-statemachine.md`；循环预算按实例计，全局并发上限仍用 `budget.max_primary`。

## 十二种 check

| kind | 语义 | 关键参数 |
| --- | --- | --- |
| `css_forbid` | 禁止出现某属性（含某值） | `property`, 可选 `value` |
| `css_value_in` | 属性值必须属于白名单 | `property`, `values` |
| `css_value_not_in` | 属性值不得属于黑名单 | `property`, `values` |
| `css_value_min` | 数值属性不得小于阈值 | `property`, `min` |
| `dom_attr_required` | 元素必须带某属性 | `attr` |
| `dom_text_forbidden` | 元素内不得有文本 | — |
| `dom_forbid_descendant` | 不得含某后代（如数字进图标） | `selector` |
| `source_forbid_regex` | 源码不得匹配某模式（如绕过统一入口直接 import） | `pattern` |
| `phase_css_required` | 每个相位必须有 `.<base>.<prefix><phase>` 样式覆盖 | `base_class`, `phases`, 可选 `class_prefix` |
| `phase_anim_reduce_required` | 相位关键帧动画须在 `prefers-reduced-motion: reduce` 媒体块内关闭 | `base_class`, `phases`, 可选 `class_prefix` |
| `phase_slot_overlay_required` | 编排槽位图标须绝对定位叠放、默认 `opacity: 0` | `selectors` |
| `phase_aria_busy_required` | 含编排类标记的源文件须设置 `aria-busy` 相位联动 | `marker` |

不够用的条款**不要硬塞**进这十二种：标 `human_check`，在报告里转成人判清单。把不可执行的写成可执行，只会制造假阳性。

编排四检只覆盖可静态判定的部分（类名序列、reduce 关键帧关闭、槽位叠放、aria 属性存在）；生命周期、语义必要性、任务结束是否停止、成败判定口径、回落分叉正确性仍 `human_check`——见 `references/motion-statemachine.md` §九。编排判定与 `motion.state_machine` 块是两件事：profile 存已批准规则，机检按 `rules` 执行。

## 条款可执行化的判据

一条规范能转 check，必须同时满足：

1. **指得出元素**：知道查哪个 DOM 或哪个类名
2. **指得出属性或值**：边框、底色、尺寸、aria、import 路径
3. **指得出期望**：禁/必须/白名单/下限

三条缺一，转 `human_check`，并写清人判时看什么。典型不可执行条款：「状态图标要克制」「图标不要太多」——这类要转成可数指标（同行图标 ≤ 3）才有意义。

## 抽取六步

1. **列源**：把所有相关规范文件列出来（图标、交互、基线、设计令牌），标出各管什么，避免同一件事两处定义。
2. **抽槽位**：规范里对「状态标记 / 来源标记 / 计数 / 筛选 / 动作 / 导航」的形态规定，归并成六槽。缺失的槽位标 `undefined`，不要凭空补。
3. **抽映射**：规范里点名的「某概念 = 某图标」，全部进 `mappings` 并标 `locked`；只提了概念没给图标的，留空，交给选型模式补。
4. **抽条款**：把形态规定转成八种 check 之一，带 `source_ref` 行号；转不了的转 `human_check`。
5. **登记冲突**：同一件事两处规定不一致 → 进 `conflicts`，写清两种读法各自导致什么后果，选一个 `interim` 值继续工作，状态 `pending`。
6. **抽动效**：把动效规范抽进 `motion` 块——是否允许落地、六形态白名单、已批准场景与出处、预算、时长令牌、reduce 策略；生命周期/语义类条款进 `human_checks`。参考文档与产品规范冲突时登记，不把参考建议写成 `locked`。有过程编排（相位状态机）时加抽 `state_machine` 块（相位、停留、重入、回落分叉）。

## 轻量抽取（没有完整规范时）

从现有实现反推一份 `draft` profile：

1. 抽 20 个左右的真实徽章实例（覆盖工具条、列表行、详情页）
2. 按形态聚类：纯图标/图标+数字/图标+文字/文字胶囊
3. 每类量尺寸、颜色令牌、有无边框、有无 Tooltip
4. 出现 ≥ 3 次的形态记为「事实标准」，写进 `slots`（`status: draft`）
5. 报告里明确：**这是现状快照，不是规范**——一致性可查，正确性不可判

## 脱敏

profile 可能被分享到团队外，写的时候：

- `source_ref` 用**相对路径 + 行号**，不写绝对路径
- 不写产品内部代号、内部决策编号
- `meaning`/`tooltip` 写用户能看到的话，不写内部黑话
- 需要保留产品特有语义时，用中性词替换（「插件市场」→「远端来源」）
- 动效场景、令牌名、时长、文件名只进独立 profile 或仓外产物；技能本体只留通用形态与判定

## 版本与生命周期

- profile 独立版本化；规范改了 → profile 升版 → 技能本体不动
- `locked` 映射只能由规范所有者改；选型模式只能读
- `conflicts` 从 `pending` 变 `resolved` 时，必须写 `resolution` 与裁决出处，并把对应条款改成实际生效值
- 每次升版在报告里给出「与上一版的差异」，否则审查结论无法回归

## 自检

- 每条 rule 都有 `source_ref` 与 `fix`
- 不可执行的条款已转 `human_check`，没有硬塞十二种 check
- conflicts 有 `interim`，确实能让人继续工作
- 没有绝对路径与产品代号
- 从 draft 转正时，标注了依据
- `motion` 只含已批准规则；参考建议没有混进 `locked`
- 动效场景都有 `source_ref` 与 `status`；无法静态检查的条款在 `human_checks`
