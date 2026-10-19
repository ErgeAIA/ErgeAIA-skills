---
name: "W-ROLLBACK 回滚"
description: "取证 → 卸载 → 还原三步，把「改坏用户已有配置」这个唯一不可逆风险点关掉。"
version: 1.0.0
trigger-when: 用户要卸载 REA、或安装后配置被改坏需要还原时
reads-from: SKILL.md, references/workflows/install-and-verify.md
writes-to: 用户宿主的 MCP 配置文件（仅还原为原内容）
---
# @工作流: W-ROLLBACK 回滚

## @步骤1: 先取证（知道会动哪些文件）

```bash
rea doctor --format json   # 抄下 registrations[].config_path 与 state
```

- 列出 REA 拥有哪些注册与技能文件；确认哪些是**用户原有**配置（uninstall 会移除 REA 写入的部分，但你要先知道它写在哪个文件里）。
- 找出 `backupPath`：出现在 `rea setup --dry-run --format json` 的 `plannedActions[]` 里，形如 `<配置>.rea.backup[.<hash>].recovery`。

## @步骤2: 卸载

```bash
rea uninstall                      # 只删 REA 自己拥有的注册与技能文件
rea uninstall --purge-data         # 额外清 REA 缓存与状态（不可逆，需单独确认）
```

🔴 CHECKPOINT：`--purge-data` 前必须明确告知「会清缓存与状态且不可逆」，等用户同意。

**必须讲清**：`rea uninstall` **不删分析引擎**。Hopper / Ghidra / IDA / JADX / Kuna 是用户自己装的（REA 只有 `--install-hopper` 会装 Hopper）；要删引擎得用户自己动手。

## @步骤3: 还原（uninstall 没清干净时）

1. 打开 `backupPath` 指向的备份文件，确认它是安装**前**的内容。
2. 用它覆盖目标配置，或手工把 REA 那一段删掉（保留用户其它 MCP 配置）。
3. 重启宿主，确认 REA 工具消失、其它 MCP 服务器照常。

@验证点：卸载后 `rea doctor` 里该注册消失；还原后文件内容与备份一致（给出关键片段对比）；其它 MCP 配置未被改动。

## 为什么这样做（写进技能的理由）

安装会**修改用户已有的 MCP 配置文件**（本机实测计划会 update `~/.claude.json` 等文件并留 backupPath），而「改坏用户已有配置」是这条链上唯一的不可逆风险点。官方 6.7.0 专门修了「重复成员」语义（编辑最后一条重复成员、拒绝会复活被遮蔽成员的删除），说明官方也把这条当红线。

所以卸载与安装**同权重**写进技能，且顺序固定为**先取证、再动手**。
