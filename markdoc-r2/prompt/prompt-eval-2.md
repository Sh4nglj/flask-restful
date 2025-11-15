## 执行步骤

### 1. 代码验证
- **运行项目**：不对代码做任何修改，直接运行并验证功能
- **记录问题**：如有报错，分析根本原因并详细记录
- **测试验证**：根据需要运行单元测试或构建集成测试

### 2. 完成度分析

参考 [scoring-criteria.md](../docs/scoring-criteria.md)，评估代码对` /task_data/content.json` 中 `prompt` 字段任务的完成情况。

### 3. model breaking分析

如触发model breaking，分析导致breaking的原因。

### 4. new prompt

生成一组新的prompt以修复现有的问题，不超过10条。填入`/task_data/description.md`的new prompt条目。