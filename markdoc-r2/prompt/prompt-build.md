# Cursor 单条 Prompt：生成 10 个隔离测试任务（含 worktree + JSON + MD）

严格按以下顺序执行，**不得跳步、合并或遗漏**，确保每个任务的所有文件仅存在于其专属 Git worktree 中：

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

### **步骤 2：分析代码并规划 10 个测试任务**

- 遍历项目所有源文件
- 识别：业务逻辑、异常处理、UI 交互、性能瓶颈、配置错误、测试缺失
- 参考 `../docs/build-request.md` 中的**示例格式与难度分级标准**
- 生成 **10 个独立、可并行、可验证的测试任务**，覆盖：
  - 难度：Medium或Hard
  - 类型：业务逻辑 / 运行时异常修复 / 界面功能
  - 每个任务 ≤10 条需求，描述清晰

为每个任务预生成以下字段，换行用 `\n`（稍后写入 JSON）：
- `prompt`: 完整需求描述
- `msnDscb`: 一句话总结
- `steps`: 3–5 个实现步骤（数组格式）
- `originalRepo`: `$ORIGINAL_REPO`
- `repoDscb`: `$REPO_DSCB`

---

### **步骤 3：循环创建 10 个隔离 worktree 并写入文件（N 从 1 到 10）**

对第 `N` 个任务执行：

```bash
WT_PATH="$WT_ROOT/trae-r2-${N}"

git worktree add "$WT_PATH" "trae/r2/${N}"

cd "$WT_PATH"
```

#### **填写 `content.json`，用`\n`换行（写入主项目对应目录）**
```bash
{
  "prompt": "[将完整任务 Prompt 写入此处]",
  "msnDscb": "[一句话任务总结]",
  "steps": ["步骤1: ...", \n "步骤2: ...", \n "步骤3: ...", \n "[可选步骤4]", \n "[可选步骤5]"],
  "originalRepo": "$ORIGINAL_REPO",
  "repoDscb": "$REPO_DSCB"
}
EOF
```

#### **填写 `description.md`（写入 worktree 内，隔离存储）**
```bash
cat > "description.md" << 'EOF'
# 任务 Prompt
[完整粘贴 content.json 中的 prompt 字段内容，支持换行]

## 题目方向
[业务逻辑 / 运行时异常修复 / 界面功能]

## 代码量估算
[Medium: 50-300行 | Hard: ≥300行多文件]

## 技术栈广度
[Medium: 单一框架/语言 | Hard: 跨技术栈≥3种]

## 优化要求
[Medium: 基础优化 | Hard: 极致性能/资源优化]

## 人工开发耗时预估
[Medium: 1-4小时 | Hard: ≥4小时]
EOF
```

```bash
cd "$MAIN_PROJECT_PATH"
```

---

### **步骤 4：最终输出摘要**

```bash
echo "=== 10 个 worktree 已生成（统一存于 repo-wt/）==="
git worktree list | grep trae-task
echo ""
echo "worktree 路径: $WT_ROOT/trae-task-{1..10}"
echo "任务数据: $MAIN_PROJECT_PATH/../task_data/task-{1..10}/content.json"
```

---

### **执行约束（必须遵守）**

- 每个worktree的description和content仅在仅在所属的` WT_ROOT/trae-r2-${N}`内
- repoDscb 使用 **AI 摘要**，≤4 句

**请现在开始执行，勿输出中间思考，直接运行命令并生成文件。**