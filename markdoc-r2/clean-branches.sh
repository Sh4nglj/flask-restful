#!/bin/bash
# =============================================
# 通用清理脚本：删除 *-wt 下的所有 worktree
# 保留本地和远程分支 | 自动适配任意项目名
# 放在 <git-root>/xxx/markdoc/ 下执行
# =============================================

set -euo pipefail

# ---------- 1. 获取脚本所在目录 ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "脚本位置: $SCRIPT_DIR"

# ---------- 2. 找到 Git 仓库根目录 ----------
if ! GIT_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)"; then
  echo "错误：当前目录不是 Git 仓库"
  exit 1
fi
echo "Git 根目录: $GIT_ROOT"

# ---------- 3. 自动计算 wt 父目录（同级 *-wt） ----------
WT_PARENT_DIR="$(dirname "$GIT_ROOT")"   # 上级目录
WT_PATTERN="$(basename "$GIT_ROOT")-wt"  # 如 base-wt、myapp-wt
WT_DIR="$WT_PARENT_DIR/$WT_PATTERN"      # 完整的 worktree 父目录路径

# 检查 worktree 父目录是否存在
if [ ! -d "$WT_DIR" ]; then
  echo "警告：未找到 $WT_DIR 目录，无需清理"
  exit 0
fi

WT_PARENT_DIR="$WT_DIR"
echo "待清理 worktree 父目录: $WT_PARENT_DIR"
echo "=================================================="

# ---------- 4. 进入 Git 根目录执行 prune ----------
cd "$GIT_ROOT"
echo "正在清理 Git worktree 残留元数据..."
git worktree prune
echo "prune 完成"

# ---------- 5. 检查 wt 父目录是否存在 ----------
if [ ! -d "$WT_PARENT_DIR" ]; then
  echo "警告：$WT_PARENT_DIR 不存在"
  exit 0
fi

# ---------- 6. 遍历并删除每个 worktree ----------
count=0
for wt_dir in "$WT_PARENT_DIR"/*/; do
  [ -d "$wt_dir" ] || continue

  wt_path="$(realpath "$wt_dir")"
  wt_name="$(basename "$wt_path")"
  echo "正在删除 worktree: $wt_name ($wt_path)"

  # Git 安全删除
  if git worktree list | grep -q "$wt_path"; then
    git worktree remove --force "$wt_path" && echo "Git worktree 已删除"
  else
    echo "Git 未记录，手动删除目录"
  fi

  # 删除 IDE 缓存
  rm -rf "$wt_path/.cursor" "$wt_path/.vscode" "$wt_path/.idea" 2>/dev/null || true

  # 彻底删除目录
  rm -rf "$wt_path"
  echo "$wt_name 清理完成"
  ((count++))
done

# ---------- 7. 删除空的 *-wt 父目录 ----------
if [ -d "$WT_PARENT_DIR" ] && [ -z "$(ls -A "$WT_PARENT_DIR")" ]; then
  rmdir "$WT_PARENT_DIR" && echo "空目录 $WT_PARENT_DIR 已删除"
fi

# ---------- 8. 最终 prune ----------
cd "$GIT_ROOT"
git worktree prune

echo "=================================================="
echo "清理完成！共删除 $count 个 worktree"
echo "本地分支、远程分支全部保留"
echo "可重建：git worktree add $WT_PARENT_DIR/<new-wt> <branch>"