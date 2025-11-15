## 执行步骤

### 1. 完成度分析

参考 [scoring-criteria.md](../docs/scoring-criteria.md)，评估代码对` /task_data/content.json` 中 `prompt` 字段任务的完成情况。

### 2. model breaking分析

如触发model breaking，分析导致breaking的原因。

总结为3-5条原因，填写 ` /task_data/content.json` 的 `failure`字段。使用 `\n`换行。

### 3. new prompt

生成一组新的prompt，填入`/task_data/description.md`的new prompt条目。 