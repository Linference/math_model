#!/bin/bash
# ============================================================
# 数学建模 Claude Code 环境一键安装
# 用法: bash setup.sh
# ============================================================
set -e

echo "=== 数学建模 Claude Code 环境安装 ==="

# 1. 安装 Agent 定义
echo "[1/3] 安装 Agent 定义..."
mkdir -p ~/.claude/agents
cp -f agents/*.md ~/.claude/agents/
echo "  已安装 $(ls agents/*.md | wc -l) 个 Agent"

# 2. 安装 Skill
echo "[2/3] 安装 math-modeling Skill..."
rm -rf ~/.claude/skills/math-modeling
cp -r skills/math-modeling ~/.claude/skills/math-modeling
echo "  已安装 math-modeling skill"

# 3. 验证
echo "[3/3] 验证安装..."
echo "  Agents:"
ls ~/.claude/agents/mm-*.md | while read f; do echo "    - $(basename $f)"; done
echo "  Skills:"
ls -d ~/.claude/skills/math-modeling && echo "    - math-modeling"

echo ""
echo "=== 安装完成 ==="
echo "现在用 Claude Code 打开本项目，说 '数学建模' 即可开始。"
