# Git 危险操作红线清单

operations:
  - command: git push --force
    impact: 强制覆盖远程历史，可能丢失他人提交
    risk: high
    alternative: git push --force-with-lease

  - command: git branch -D <branch>
    impact: 永久删除本地分支，无法恢复
    risk: high
    alternative: 先查看分支状态，确认后再删除

  - command: git reset --hard <commit>
    impact: 丢弃指定提交后的所有变更，无法恢复
    risk: high
    alternative: git reset --soft 保留变更在暂存区

  - command: git rebase -i <commit>
    impact: 修改提交历史，可能产生冲突
    risk: medium
    alternative: squash merge

  - command: git commit --amend
    impact: 改写最近一次提交（信息或内容）；若已推送，等同改写远端历史
    risk: medium
    alternative: 新建提交；已推送的提交禁止 amend

  - command: git commit --no-verify
    impact: 跳过 hooks（lint/测试门禁），可能放行问题代码
    risk: medium
    alternative: 仅在用户明确要求时使用；先修 hooks 报错

  - command: git config <key> <value>
    impact: 修改 Git 配置——全局影响所有仓库，仓库级仅当前仓库
    risk: low-medium
    alternative: 默认改仓库级；改全局前说明影响范围

  - command: git push --force 至 main/master
    impact: 强制覆盖远端 main/master 历史，不可恢复
    risk: high
    alternative: 禁止向 main/master 强推；其它分支优先 --force-with-lease 且经确认

  - command: git stash drop
    impact: 永久删除暂存的变更
    risk: high
    alternative: git stash pop 后手动处理

  - command: git clean -f
    impact: 删除所有未跟踪文件/目录，无法恢复
    risk: high
    alternative: 先 `git clean -n` 预览，确认后再执行；或用 `git stash -u` 暂存未跟踪改动

  - command: git checkout -- <file>
    impact: 丢弃指定文件的未暂存工作区改动，无法恢复
    risk: high
    alternative: 先 `git stash` 暂存，确认不再需要后再丢弃
confirmation-requirements:
  - 必须明确说明操作影响
  - 必须要求用户输入「确认执行」
  - 必须验证操作结果
