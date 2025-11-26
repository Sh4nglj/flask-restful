## 任务评估指令（单模型 / 单 worktree）

本指令用于在「单个模型的专属 worktree」中，对该模型的最终表现进行评估。  
每个任务会分别在 **Seed_Beta worktree** 和 **Kimi_K2 worktree** 中各自运行一次本评估指令，互不影响。

---

## 使用场景与输入

- **当前工作目录**：某个任务的单一模型 worktree，例如：
  - Seed_Beta 的 worktree：只包含 Seed_Beta 的代码、执行记录和 `contents/` 文件
  - Kimi_K2 的 worktree：只包含 Kimi_K2 的代码、执行记录和 `contents/` 文件
- **你将被告知以下信息**（由上游调用时提供）：
  - **当前模型名称**：`MODEL_NAME`，取值只能是 `Seed_Beta` 或 `Kimi_K2`
  - **任务信息**：`/task_data/content-common.json` 中的 `prompt` 及相关字段，仅用于理解任务，不必修改
  - **执行记录**：`record-*.md`，包含本模型在本任务上的工具调用、运行结果、报错等
  - **目标 JSON 模板**：当前 worktree 下的  
    - `contents/content-seed-beta.json`（若当前模型为 Seed_Beta），或  
    - `contents/content-kimi-k2.json`（若当前模型为 Kimi_K2）

你的目标：**只根据本 worktree 内的信息，对当前模型进行评估，并完整填写对应的 `contents/content-*.json` 中的字段。**

---

## 评估步骤

### 1. 代码与功能验证
- **运行项目**：不对代码做任何修改，直接运行并验证功能是否满足 `/task_data/content.json` 中 `prompt` 的要求。
- **记录问题**：如有编译错误、运行时异常、功能缺失或行为不符合预期，分析根本原因并记录。
- **必要的测试**：根据项目情况，适当运行单元测试或集成测试，验证关键路径。

### 2. 对照任务要求与评分标准
- 参考 `../docs/scoring-criteria.md` 中的评分维度与定义。
- 从以下角度评估当前模型对本任务的完成情况：
  - 交付完整性
  - 工具调用
  - 错误修复
  - 上下文理解
  - 用户体验
- 为每个字段打分1-5

---

## 需填写的字段（写入 `contents/content-*.json`）

当前 worktree 只对应一个模型，因此：

- 如果 `MODEL_NAME = Seed_Beta`，你需要填写 `contents/content-seed-beta.json` 中的字段：
  - `交付完整性 - Seed_Beta`
  - `工具调用 - Seed_Beta`
  - `错误修复 - Seed_Beta`
  - `上下文理解 - Seed_Beta`
  - `用户体验 - Seed_Beta`
  - `评分理由（工具调用） - Seed_Beta`
  - `评分理由（上下文理解） - Seed_Beta`
  - `评分理由（用户体验） - Seed_Beta`

- 如果 `MODEL_NAME = Kimi_K2`，你需要填写 `contents/content-kimi-k2.json` 中的字段：
  - `交付完整性 - Kimi_K2`
  - `工具调用 - Kimi_K2`
  - `错误修复 - Kimi_K2`
  - `上下文理解 - Kimi_K2`
  - `用户体验 - Kimi_K2`
  - `评分理由（工具调用） - Kimi_K2`
  - `评分理由（上下文理解） - Kimi_K2`
  - `评分理由（用户体验） - Kimi_K2`

### 评分理由字段（每项≤150字）

- **交付完整性 - <MODEL_NAME>**
  - 说明本模型对任务需求的覆盖程度：
    - 已完全实现的功能点
    - 部分实现或实现质量不足的功能点
    - 完全缺失的关键需求
  - 建议结构示例：  
    `已实现需求：\n1. ...\n2. ...\n\n未完整实现或存在严重问题：\n1. ...\n2. ...\n评分：X/5，根据 scoring-criteria.md 中「交付完整性」的定义给出评分。`
  - 末尾给出 `评分：X/5`，并引用scoring-criteria的原文说明依据。


- **上下文理解 - <MODEL_NAME>**
  - 评估模型对项目整体结构、业务逻辑和历史信息的理解程度：
    - 是否正确理解任务描述与项目架构
    - 是否利用 README、配置、已有代码进行推理
  - 末尾给出 `评分：X/5`，并引用scoring-criteria的原文说明依据。

- **用户体验 - <MODEL_NAME>**
  - 针对最终交付物的可用性和易维护性：
    - 代码风格、可读性、命名与注释
    - 界面交互（如适用）、错误提示友好度
  - 末尾给出 `评分：X/5`，并引用scoring-criteria的原文说明依据。


---

## 输出格式与约束

- **只修改当前模型对应的 `contents/content-*.json`**：
  - 在 Seed_Beta worktree 中，只写 `contents/content-seed-beta.json`；
  - 在 Kimi_K2 worktree 中，只写 `contents/content-kimi-k2.json`。
- **字段值为纯文本字符串**：
  - 不使用任何 markdown 语法（如 `**`、`#`、反引号等）。
  - 不使用 JSON 数组；如需列出多条内容，用 `\n` 分行在一个字符串中完成。
- **换行统一使用 `\n` 表示**，不要使用真实换行。
- **不新增字段，不更改字段顺序，不删除字段**。
- **只基于当前模型的信息打分**：
  - 不与另一个模型进行对比，不引用对方的表现。
  - 所有表述都以「当前模型在本任务中的表现」为视角。

---

## 评估原则

- **客观公正**：严格依据 `../docs/scoring-criteria.md` 中的标准，在评分语句中引用相关等级描述。  
- **有理有据**：每个评分点必须有具体证据支撑，指出文件或函数名称。  
- **评分一致**：描述给出的理由必须与打分高低匹配，避免前后矛盾。
