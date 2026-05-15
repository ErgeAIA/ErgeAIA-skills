---
trigger-when: 查看 references/config/ 目录结构或修改一致性检测规则时
---

# 配置文件 (Config)

| 文件 | 用途 | 何时加载 |
|------|------|----------|
| consistency-rules.yaml | 术语一致性检测规则（--consistency 模式） | 脚本启动时自动加载，PyYAML 可用时生效 |
