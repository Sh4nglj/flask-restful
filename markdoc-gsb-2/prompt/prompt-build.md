## prompt-build

### **执行约束（必须遵守）**

- **主项目路径**：`MAIN_PROJECT_PATH=$(pwd)`，在**被测代码仓库根目录**下执行本指令。
- **worktree 根目录**：所有任务相关 worktree 统一放在：`$MAIN_PROJECT_PATH/../repo-wt/trae-task-N-{seed,kimi}`。
- **每个任务对应 2 个独立 worktree**：
  - `trae-task-N-seed`：只给 **Seed_Beta** 使用；
  - `trae-task-N-kimi`：只给 **Kimi_K2** 使用；
  - 两个 worktree 之间不得互相拷贝代码或文件。
- **每个 worktree 的描述文件仅保存在本 WT 内**：例如 `WT_ROOT/trae-task-N-seed/description.md`，不得跨 WT 共享。
- **repoDscb 使用 AI 摘要**，≤4 句；以后会写入 GSB `contents/content-common.json` 的 `repo 介绍` 字段。
- **GSB 的 `contents/content-common.json` 字段格式要求**：
  - 字段值为**纯文本字符串**，不使用任何 markdown 语法（如 `**`、`#`、反引号等）。
  - 所有多行内容统一使用 `\n` 表示换行，不使用真实换行。
  - 字段内容不使用 JSON 数组，如需列表，用 `\n` 拼接为单个字符串。
  - 不新增、删除或重命名字段，只填写/更新既有字段的 value。

严格按以下顺序执行，**不得跳步、合并或遗漏**，确保每个任务的所有文件仅存在于其专属 Git worktree 中。

---

### **步骤 1：初始化与信息采集**

```bash
MAIN_PROJECT_PATH=$(pwd)
echo "主项目路径: $MAIN_PROJECT_PATH"

WT_ROOT="$MAIN_PROJECT_PATH/../repo-wt"
mkdir -p "$WT_ROOT"

ORIGINAL_REPO=$(git remote get-url upstream 2>/dev/null || git remote get-url origin)
echo "上游仓库: $ORIGINAL_REPO"

REPO_DSCB=$(cat README.md | head -n 300 | \
  cursor-summarize "请用中文、4 句以内总结以下项目 README 的主要功能与技术栈，语言简洁专业，直接输出总结文本，无需编号或引号：")
```

- `ORIGINAL_REPO`：将作为 **Github 原始 Repo 链接** 写入 `contents/content-common.json`。
- `REPO_DSCB`：将作为 **repo 介绍** 写入 `contents/content-common.json`。

---

### **步骤 2：分析代码并规划 10 个测试任务**

- 遍历项目所有源文件，识别：
  - 业务逻辑、异常处理、UI 交互、性能瓶颈、配置错误、测试缺失等高价值区域；
- 参考 `../docs/build-request.md` 中的**示例格式与难度分级标准**；
- 生成 **10 个独立、可并行、可验证的测试任务**，覆盖：
  - 难度：Medium 或 Hard；
  - 类型：业务逻辑 / 运行时异常修复 / 界面功能；
  - 每个任务 ≤10 条需求，描述清晰、可验证。

为每个任务预生成以下字段（后续将用于 GSB 的 `contents/content-common.json`）——所有文本字段均遵守 **纯文本 + `\n` 换行 + 不使用 JSON 数组** 的规则：

- `Prompt`：完整任务需求描述（中文），用于直接喂给 Seed_Beta / Kimi_K2；
- `describtion`：一句话任务总结（相当于之前的 `msnDscb`）；
- `题目方向`：例如：业务逻辑 / 运行时异常修复 / 界面功能；
- `任务难度评估——代码量`：Medium / Hard，对应 `docs/build-request.md` 中的代码量行数说明；
- `任务难度评估——技术栈广度`：Medium / Hard，对应单一框架 vs 跨技术栈；
- `任务难度评估——优化要求`：Medium / Hard，对应基础优化 vs 极致性能/资源优化；
- `任务难度评估——人工开发耗时预估`：Medium / Hard，对应 1–4 小时 vs ≥4 小时；
- `Github 原始 Repo 链接`：使用 `ORIGINAL_REPO`；
- `repo 介绍`：使用 `REPO_DSCB`；
- `技术栈`：从 README / 代码结构中提取的主要技术栈（可基于 `REPO_DSCB` 再精炼 1–2 句）。

> 后续当你选定某一个任务作为 **GSB 双模型对比任务** 时，将把该任务的这些字段写入 `contents/content-common.json` 对应 key 的 value 中，其他字段（Session ID、交互轮次、评分理由等）留待评估阶段填写。

---

### **步骤 3：为每个任务创建 Seed / Kimi 两个隔离 worktree（N 从 1 到 10）**

对第 `N` 个任务执行：

```bash
WT_BASE="$WT_ROOT/trae-task-${N}"
SEED_WT_PATH="${WT_BASE}-seed"
KIMI_WT_PATH="${WT_BASE}-kimi"

# 建议：为每个任务创建两个独立的评估分支
# 你可以在创建 worktree 前先基于当前 commit 新建分支，例如：
#   git branch "trae/task/${N}-seed"
#   git branch "trae/task/${N}-kimi"

# 创建 Seed_Beta 专用 worktree
git worktree add "$SEED_WT_PATH" "trae/task/${N}-seed"

# 创建 Kimi_K2 专用 worktree
git worktree add "$KIMI_WT_PATH" "trae/task/${N}-kimi"
```

> 要求：两个 worktree 的初始代码来自同一任务起点，只是分支名称不同，方便后续分别让 Seed_Beta / Kimi_K2 修改代码、提交 PR。

---

### **步骤 4：在每个 worktree 内写入任务描述文件**

在 **Seed_Beta worktree** 和 **Kimi_K2 worktree** 中都需要各自维护一份 `description.md`，内容结构完全一致，只是后续由不同模型来实现任务。

以 Seed_Beta worktree 为例（Kimi_K2 类似）：

```bash
cd "$SEED_WT_PATH"

cat > "description.md" << 'EOF'
# 任务 Prompt
[完整粘贴本任务的 Prompt 字段内容，支持多行]
EOF

cd "$MAIN_PROJECT_PATH"
```

> 说明：`description.md` 主要服务于人类/模型快速理解任务背景，与 GSB 的 `contents/content-common.json` 字段含义保持一致，但存储位置隔离在各自的 worktree 内。

---

### **步骤 5：为 GSB 评测准备 `contents/content-common.json`**

当你从上述 10 个任务中**选定一个任务**用于 Seed_Beta vs Kimi_K2 的对比评测时：

1. 在 GSB 项目（本仓库）中，复制模板：
   - 从 `contents- template/content-common.json` 拷贝为 `contents/content-common.json`（如尚未存在）。
2. 将该任务在步骤 2 中整理出的信息，按字段名称写入 `contents/content-common.json` 对应的 value：
   - `Prompt`
   - `describtion`
   - `题目方向`
   - `任务难度评估——代码量`
   - `任务难度评估——技术栈广度`
   - `任务难度评估——优化要求`
   - `任务难度评估——人工开发耗时预估`
   - `Github 原始 Repo 链接`
   - `repo 介绍`
   - `技术栈`
3. 保持其他字段（Session ID、交互轮次、评分理由、GSB - 整体评估等）为空，由后续的 eval / eval-final 步骤填写。
4. 填写时必须遵守：
   - 仅使用**纯文本字符串**，不使用 markdown 语法；
   - 多行内容统一用 `\\n` 表示换行，不使用真实换行；
   - 不使用 JSON 数组；
   - 不新增、删除或重命名字段。

---

### **步骤 6：最终输出摘要**

```bash
echo "=== 10 个任务的 Seed/Kimi worktree 已生成（统一存于 repo-wt/）==="
git worktree list | grep "trae-task-"

echo ""
echo "Seed_Beta worktree 示例路径: $WT_ROOT/trae-task-1-seed"
echo "Kimi_K2 worktree 示例路径: $WT_ROOT/trae-task-1-kimi"

echo "GSB 公用信息文件: $MAIN_PROJECT_PATH/contents/content-common.json（需在选定任务后按步骤 5 填写）"
```

**请现在开始按上述步骤执行，勿输出中间思考，直接运行命令并生成任务与 worktree。**


