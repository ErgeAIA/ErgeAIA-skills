# Conventional Commits 规范参考

types:
  - feat: 新功能
  - fix: 修复 bug
  - docs: 文档变更
  - style: 代码格式（不影响功能）
  - refactor: 重构（不是新功能也不是修复）
  - perf: 性能优化
  - test: 测试
  - build: 构建系统或依赖变更
  - ci: CI 配置变更
  - chore: 杂项维护
  - revert: 回滚某次提交
format: |
  <type>(<scope>): <description>

  [optional body]

  [optional footer]
rules:
  - 使用祈使语气
  - 首字母小写
  - 结尾不加句号
  - 标题不超过 50 字符
  - scope 可选，描述变更范围
  - 破坏性变更两种标注：`<type>!` 感叹号后缀，或 footer `BREAKING CHANGE: <说明>`
  - 引用 issue：`Closes #123` / `Refs #456`
examples:
  - feat(auth): add JWT token validation
  - fix(api): handle null response from server
  - docs(readme): update installation guide
  - refactor(core): extract validation logic
  - feat!: remove deprecated v1 API
  - build(deps): bump lodash to 4.17.21
  - ci: add release workflow
  - revert: revert feat(auth) due to regression
  - BREAKING CHANGE: remove deprecated v1 API
