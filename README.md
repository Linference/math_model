# 数学建模多智能体论文生成系统

[![Stars](https://img.shields.io/github/stars/Linference/math_model?style=social)](https://github.com/Linference/math_model/stargazers)
[![Forks](https://img.shields.io/github/forks/Linference/math_model?style=social)](https://github.com/Linference/math_model/network/members)
[![Release](https://img.shields.io/github/v/release/Linference/math_model)](https://github.com/Linference/math_model/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

把数学建模赛题 PDF 丢进去，自动出论文。国赛 CUMCM / 美赛 MCM / HiMCM 都支持。

8 个 AI 子智能体分工协作：审题 → 选方法 → 找数据 → 写代码求解 → 画图 → 写论文编译 PDF → 三个评审角色并行批改 → 写作者反复修改直到达标。

---

## Star History

[查看 Star 趋势图](https://star-history.com/#Linference/math_model&Date)

---

## 国内用户看这里：环境怎么搭

Claude Code 的 API（Anthropic）在国内无法直接访问。推荐方案：

### 用 CCSwitch 让 Claude Code 走 DeepSeek

**[CCSwitch](https://ccswitch.io)** 是一个免费的 Claude Code 桌面管理工具，可以配置 Claude Code 使用 DeepSeek V4 Pro 作为后端，国内直连。

1. 去 [ccswitch.io](https://ccswitch.io) 下载安装（Windows `.msi` / macOS `brew install --cask cc-switch`）
2. 打开 CCSwitch，添加 DeepSeek 提供商，填入 API Key（去 [platform.deepseek.com](https://platform.deepseek.com/) 注册获取）
3. 选择 DeepSeek 为默认后端，Claude Code 即可正常使用

> 官方 GitHub：[github.com/farion1231/cc-switch](https://github.com/farion1231/cc-switch)。CCSwitch 完全免费，只从官网下载。

### 装 Claude Code

```bash
# 需要 Node.js ≥18.x：https://nodejs.org/zh-cn
npm install -g @anthropic-ai/claude-code
```

VSCode 用户直接搜 `Claude Code` 扩展安装，设置里填 API Key。

### 跑起来

在 Claude Code 中输入：

```
/math-modeling
[粘贴赛题原文]
```

### 如果不想折腾 Claude Code

直接把 `skill/SKILL.md` 的内容当系统提示词，用 DeepSeek 网页版 ([chat.deepseek.com](https://chat.deepseek.com)) 或 API 手动按阶段跑，效果也够用。

---

## 项目结构

```
math_model/
├── README.md
├── samples/                      # 两个完整示例
│   ├── 2024_CUMCM_A/             # 国赛A题：板凳龙
│   └── 2025_HiMCM_Problem_B/     # HiMCM B题：超级碗选址
└── skill/                        # Skills 安装包
    ├── SKILL.md                  # 主技能定义
    ├── references/               # 12本参考手册
    ├── scripts/                  # 辅助脚本
    ├── templates/                # LaTeX模板（中英双版）
    └── workflows/                # 审稿工作流
```

---

## 7 阶段流水线

| 阶段 | 做什么 | 产出 |
|:--:|--------|------|
| 0 | 建项目目录 | 标准骨架 |
| 1 | 逐问拆解题意，挖约束和陷阱 | 审题报告 |
| 2 | 给每问选建模方法 | 建模方案 + 图表清单 |
| 3 | 联网搜数据，落盘 CSV | 数据文件 + 来源记录 |
| 4 | Python 实现求解 | 可运行脚本 + 数值结果 |
| 5 | 画图（16种类型） | 高质量图表 |
| 6 | 填充 LaTeX 模板，编译 PDF | 论文初稿 |
| 7 | 3 角色并行审稿，写作者修改 | 终稿 PDF |

## 8 个子智能体

| 角色 | 干什么 |
|------|--------|
| `mm-problem-analyst` | 审题：逐问拆解，挖约束、评分点、陷阱 |
| `mm-modeler` | 方法选型：要不要 ML/DL，列图表清单 |
| `mm-data-hunter` | 数据：搜维基/GitHub/Kaggle/sklearn，记录来源 |
| `mm-coder` | 求解：Python 实现，跑通，出图 |
| `mm-writer` | 写作：填 LaTeX，回应审稿意见，补实验 |
| `mm-reviewer` | 审稿：五维度打分，找弱点 |
| `mm-verifier` | 验证：交叉核对数值、量纲、边界 |
| `mm-reasoner` | 推理：审计公式推导，补未证断言 |

## 对抗审稿

三个评审角色并行批改同一份论文——审稿人看建模合理性，验证者核对数值，推理者审计公式。写作者逐条修改后三评审重新打分，均分不到 7.5 继续改，最多 4 轮。

---

## 推荐 VSCode 扩展

```bash
# Markdown
code --install-extension shd101wyy.markdown-preview-enhanced
code --install-extension yzhang.markdown-all-in-one

# LaTeX
code --install-extension james-yu.latex-workshop

# 表格/文档预览
code --install-extension grapecity.gc-excelviewer
code --install-extension mechatroner.rainbow-csv
code --install-extension tomoki1207.pdf
code --install-extension cweijan.vscode-office

# 效率
code --install-extension eamodio.gitlens
```

---

## 两个示例

### 2024 国赛 A 题 — 板凳龙闹元宵

223 节板凳沿阿基米德螺线盘入/调头/盘出。建模每节运动轨迹、检测碰撞、优化调头路径。

技术点：弦长约束二分搜索、SAT 碰撞检测、带约束非线性优化。

### 2025 HiMCM B 题 — 超级碗可持续选址

为 NFL 建立纯环境因素选址模型，评估 19 个历史城市 + 3 个候选城市，扩展到奥运会。

技术点：AHP + TOPSIS 双层决策、Scope 1/2/3 碳排放分析、敏感性分析。

---

## 安装

```bash
git clone https://github.com/Linference/math_model.git ~/.claude/skills/math-modeling
```

或去 [Releases](https://github.com/Linference/math_model/releases) 下载 ZIP，解压到同一目录。

---

## License

MIT
