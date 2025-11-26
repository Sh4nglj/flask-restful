## Git 操作流程

评估完成后，将代码更改推送到分支（不更新 main）：

### 1. 提交代码更改

提交除markdoc-2/以外的内容

```bash
git add <修改的代码文件>
git commit -m "feat: 任务描述
```

### 2. 推送分支
```bash
git push origin <分支名>
```

**注意事项**：
- 不要提交评估文件（markdoc* 目录下的文件通常不在 git 跟踪中）
- 不要合并到 main 分支
- 只推送当前任务分支

## 创建 Pull Request

评估完成并推送分支后，创建 Pull Request，**base分支为自己仓库的master，非fork的原始仓库**：

### 1. 确保 GitHub CLI 已登录
```bash
gh auth status
# 如未登录，运行：
gh auth login
```

### 2. 创建 PR
使用 `content.json` 中的信息创建 PR：
- **title**：使用 `sessionID` 字段的值
- **body**：使用 `prompt` 字段的值（使用正常换行）
- **base**：main 分支（自己的仓库）
- **head**：当前任务分支

```bash
gh pr create --base main --head <分支名> --title "<sessionID>" --body "<prompt内容>"
```

### 3. 更新 content.json
创建 PR 后，将 PR 链接填写到 `content.json` 的 `githubPR` 字段中。