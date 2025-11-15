# 任务评估指令

## 评估步骤

### 1. 代码验证
- **运行项目**：不对代码做任何修改，直接运行并验证功能
- **记录问题**：如有报错，分析根本原因并详细记录
- **测试验证**：根据需要运行单元测试或构建集成测试

### 2. 对照任务要求
参考 [scoring-criteria.md](../docs/scoring-criteria.md)，评估代码对` /task_data/content.json` 中 `prompt` 字段任务的完成情况。

### 3. 分析执行记录
- **工具调用统计**：阅读 `record.md`，统计各类工具的使用次数和成功率
  - 搜索 `toolName` 关键字统计工具调用
  - 搜索 `status: success` 统计成功次数
  - 计算成功率并列出具体数据
- **Model Breaking 分析**：如触发 breaking，定位具体位置并分析原因

## 输出格式

严格按照 [evaluation-template.md](../docs/evaluation-template.md) 的格式输出评估结果。

## 评估原则
- **客观公正**：严格依据评分标准，不主观臆断
- **有理有据**：每个评分点必须有具体证据支撑
- **评分一致**：确保分数与描述内容相符，避免前后矛盾

## Git 操作流程

评估完成后，将代码更改推送到分支（不更新 main）：

### 1. 提交代码更改
```bash
git add <修改的代码文件>
git commit -m "feat: 任务描述
```

### 2. 推送分支
```bash
git push origin <分支名>
```

**注意事项**：
- 不要提交评估文件（markdoc 目录下的文件通常不在 git 跟踪中）
- 不要合并到 main 分支
- 只推送当前任务分支

## 创建 Pull Request

评估完成并推送分支后，创建 Pull Request：

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