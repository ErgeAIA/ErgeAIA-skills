# Git 技能触发说明

trigger-when:
  - 用户提及 commit/branch/merge/rebase/PR 等 Git 关键词
  - 用户询问分支命名或提交信息写法
  - 用户遇到 Git 错误需要帮助解决
  - 用户准备执行危险操作（force push、删除分支、reset --hard）
  - 用户完成代码变更准备提交
intent-patterns:
  - "提交"
  - "commit"
  - "分支"
  - "branch"
  - "合并"
  - "merge"
  - "推送"
  - "push"
  - "拉取"
  - "pull"
  - "Rebase"
tech-patterns:
  - git status
  - git log
  - git diff
  - Conventional Commits
  - 分支命名规范
env-patterns:
  - Git 仓库
  - 版本控制
  - 代码协作
exclude-patterns:
  - 纯代码编写（不涉及 Git）
  - 文件内容编辑（不涉及提交）
  - 项目架构讨论（不涉及版本控制）
