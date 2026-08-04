# 数学建模项目 — Claude Code 配置

## 项目说明
数学建模竞赛论文生成系统。使用多智能体对抗协作流程：审题→文献综述→方法选型→数据获取→编程求解→可视化→LaTeX写作→对抗审稿。

## 启动方式
在本目录打开 Claude Code，说"数学建模"或给赛题即可自动启动流水线。

## 环境要求
- Python 3.11+ (Anaconda) with numpy, pandas, scipy, scikit-learn, matplotlib, seaborn, networkx
- MiKTeX (xelatex) 用于编译中文 LaTeX 论文

## 首次使用
运行 `bash setup.sh` 安装 agents 和 skill 到 `~/.claude/`。
