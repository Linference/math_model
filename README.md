# 数学建模多智能体论文生成系统

[![Stars](https://img.shields.io/github/stars/Linference/math_model?style=social)](https://github.com/Linference/math_model/stargazers)
[![Forks](https://img.shields.io/github/forks/Linference/math_model?style=social)](https://github.com/Linference/math_model/network/members)
[![Release](https://img.shields.io/github/v/release/Linference/math_model?include_prereleases)](https://github.com/Linference/math_model/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)
![LaTeX](https://img.shields.io/badge/LaTeX-xelatex-008080?logo=latex)
![竞赛](https://img.shields.io/badge/CUMCM_|_MCM_|_HiMCM-e74c3c)

---

一套用 Claude Code 多智能体协作自动生成数学建模论文的工具。把赛题 PDF 丢进去，自动走完审题、选方法、找数据、写代码、画图、写论文、编译 PDF、对抗审稿的全流程。国赛美赛都支持。

核心做法是让 8 个不同角色的 AI 子智能体组成流水线，每阶段产出落地到磁盘文件，后一阶段检查前一阶段的结果再继续。最后让审稿人、验证者、推理者三个角色分别批改论文，写作者按意见反复修改，直到评分达标。

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Linference/math_model&type=Date&legend=top-left)](https://star-history.com/#Linference/math_model&Date)

> 图表由 [star-history.com](https://star-history.com) 生成。新仓库的数据需要等第一次 Star 后才能开始记录趋势，如果你觉得这项目有用，点个 Star 就是最好的支持。

---

## 快速开始

### 你需要准备

- **Python 3.10+**（跑代码和画图）→ [Anaconda](https://www.anaconda.com/) 或 [python.org](https://python.org)
- **LaTeX**（编译 PDF）→ [MiKTeX](https://miktex.org/) (Windows) / [TeXLive](https://tug.org/texlive/) (跨平台)
- **Claude Code**（AI 编排引擎）→ 安装方法见下方

### 安装 Claude Code

**终端版：**

```bash
# 先装 Node.js（≥18.x）
# 下载：https://nodejs.org/zh-cn

# 全局安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 启动（首次需登录 Anthropic 账号）
claude
```

**VSCode 扩展版：**

1. VSCode 左侧栏 → 扩展（`Ctrl+Shift+X`）
2. 搜索 `Claude Code`，安装 Anthropic 官方版
3. 设置 → 搜 `claude` → 填入 API Key
4. 用 `Ctrl+Shift+P` → `Claude` 调出命令面板

> 获取 API Key：[console.anthropic.com](https://console.anthropic.com/)

### 一键启动建模流水线

在 Claude Code 中直接输入：

```
/math-modeling

[在这里粘贴赛题原文]
```

系统会自动按阶段执行：建目录 → 审题 → 选方法 → 找数据 → 写代码求解 → 画图 → 写论文编译 → 对抗审稿。

手动单步操作：

```bash
# 新建项目骨架（zh=国赛 / en=美赛）
python skill/scripts/new_project.py "2024国赛A题" --lang zh

# 联网找数据
python skill/scripts/fetch_data.py --sklearn iris

# 编译论文
python skill/scripts/compile.py 项目文件夹/paper/main.tex
```

---

## 怎么做出来的：7 阶段流水线

| 阶段 | 做什么 | 产出 |
|:--:|--------|------|
| 0 | 建项目目录 | 标准骨架 |
| 1 | 逐问拆解题意、挖约束和陷阱 | 审题报告 |
| 2 | 给每问选建模方法，判断要不要 ML/DL | 建模方案 + 图表清单 |
| 3 | 联网搜数据，落盘 CSV，记录出处 | 数据文件 + SOURCES.md |
| 4 | Python 实现模型求解 | 可运行脚本 + 数值结果 |
| 5 | 画图（折线/热力/雷达/3D/网络等 16 种类型） | 高质量图表 |
| 6 | 填充 LaTeX 模板，编译 PDF | 论文初稿 |
| 7 | 审稿人 + 验证者 + 推理者并行审稿，写作者修改 | 终稿 PDF |

每阶段都有门禁检查，产出必须落盘、验证通过才能进入下一阶段。

## 8 个子智能体

| 角色 | 干什么 |
|------|--------|
| `mm-problem-analyst` | 审题：拆解每问，挖显性/隐性约束、评分点、常见坑 |
| `mm-modeler` | 方法选型：决策要不要用 ML/DL，列图表清单 |
| `mm-data-hunter` | 数据：搜索维基/GitHub/Kaggle/官方统计/sklearn，记录来源 |
| `mm-coder` | 求解：Python 实现模型，跑通，出图，代码可复现 |
| `mm-writer` | 写作：填 LaTeX 模板，回应审稿意见，补实验 |
| `mm-reviewer` | 审稿：五维度 0-10 打分，找弱点，输出修改意见 |
| `mm-verifier` | 验证：交叉检查数值、量纲、边界、代码与论文是否一致 |
| `mm-reasoner` | 推理：审计公式推导，补全未证明的断言 |

## 对抗审稿机制

一般 AI 写论文的套路是"写 → 自己检查 → 改"，同一个模型既当运动员又当裁判，效果有限。

这里用三个不同角色的子智能体并行批改同一份论文，每个角色侧重不同维度：

- **审稿人**：看建模合理性和创新性，给总体分
- **验证者**：逐项核对数值结果，检查量纲和单位有没有错
- **推理者**：一行行审计公式推导，确保数学上站得住

三份审稿意见汇合后，**写作者**（又一个独立的子智能体）按意见逐条修改。改完一轮后三个评审重新打分，均分 ≥ 7.5 / 10 才放行，最多改 4 轮。

> 这个思路参考了 AlphaGo 的 self-play 和 GAN 的 adversarial training——通过对抗来逼近更好的结果。

---

## 推荐 VSCode 扩展

这些扩展能让整个工作流更顺手：

```bash
# Markdown（写 README / 报告 / 审稿意见）
code --install-extension shd101wyy.markdown-preview-enhanced
code --install-extension yzhang.markdown-all-in-one
code --install-extension davidanson.vscode-markdownlint

# LaTeX（论文编辑 + 实时预览）
code --install-extension james-yu.latex-workshop

# 表格和文档预览
code --install-extension grapecity.gc-excelviewer    # 在 VSCode 里看 .xlsx
code --install-extension mechatroner.rainbow-csv      # CSV 列着色
code --install-extension tomoki1207.pdf               # 在 VSCode 里看 PDF
code --install-extension cweijan.vscode-office        # 看 .doc / .docx / .pptx

# 效率工具
code --install-extension alefragnani.project-manager  # 多项目管理
code --install-extension eamodio.gitlens              # Git 增强
```

> 如果 `code` 命令不识别：VSCode → `Ctrl+Shift+P` → `Shell Command: Install 'code' command in PATH`

---

## 备选方案：用不了 Claude Code 怎么办

如果因为网络问题用不了 Claude Code，可以用 **DeepSeek V4 Pro** 替代。开通方式：

1. 访问 [platform.deepseek.com](https://platform.deepseek.com/) 注册
2. 控制台 → API Keys → 创建 Key
3. 通过 Web 对话或 API 调用

本事项目的核心流水线逻辑和子智能体角色定义在 `skill/SKILL.md` 和 `skill/references/` 里，可以直接复制给 DeepSeek 用：

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-xxx",  # 你的 DeepSeek Key
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",  # deepseek-reasoner 推理更强
    messages=[
        {"role": "system", "content": open("skill/SKILL.md").read()},
        {"role": "user", "content": "赛题内容：[粘贴题目]"}
    ]
)
```

> Claude Code 的强项是多智能体自动编排 + 工具调用，DeepSeek 在数学推理和中文写作上也很强。不自动编排的话，手动按流水线一步步跑也完全能用。

---

## 切换配置：CCSwitch

如果你有多套 API Key（公司 vs 个人、国内 vs 国外），[CCSwitch](https://github.com/ccswitch/ccswitch) 可以帮你一键切换：

```bash
git clone https://github.com/ccswitch/ccswitch.git
cd ccswitch && npm install && npm link

ccswitch create work     # 创建"工作"配置
ccswitch create personal # 创建"个人"配置
ccswitch use work        # 一键切换
ccswitch backup          # 备份当前配置
```

---

## 项目结构

```
math_model/
├── README.md
├── .gitignore
│
├── samples/                      # 示例项目（可直接参考）
│   ├── 2024_CUMCM_A/             # 国赛 A 题：板凳龙运动学
│   │   ├── code/                 # 5 个求解脚本 + 公共函数
│   │   ├── data/                 # 结果 xlsx + SOURCES.md
│   │   ├── figures/              # 14 张图表
│   │   ├── paper/                # LaTeX 论文（main.tex + PDF）
│   │   └── REPORT.md             # 全流程记录
│   └── 2025_HiMCM_Problem_B/     # HiMCM B 题：超级碗选址
│       ├── code/                 # 7 个求解脚本
│       ├── data/                 # 4 个 CSV + SOURCES.md
│       ├── figures/              # 19 张图表
│       ├── results/              # 7 个结果文件
│       ├── paper/                # LaTeX 论文（含 PDF）
│       └── REPORT.md
│
└── skill/                        # Skills 安装包
    ├── SKILL.md                  # 主技能定义
    ├── references/               # 12 本参考手册
    │   ├── 01-problem-analysis.md
    │   ├── 02-framework.md
    │   ├── 03-data-acquisition.md
    │   ├── 04-modeling-cookbook.md
    │   ├── 05-visualization.md
    │   ├── 06-writing.md
    │   ├── 07-adversarial-review.md
    │   ├── 08-stage-verification.md
    │   ├── 09-innovation-playbook.md
    │   ├── 10-modeling-tricks.md
    │   ├── data-sources.md
    │   └── scoring-rubric.md
    ├── scripts/                  # 5 个辅助脚本
    ├── templates/                # LaTeX 模板（中英双版）
    └── workflows/                # 审稿工作流脚本
```

---

## 安装 Skills 包

**方法 A：Git 克隆（推荐，能自动更新）**

```bash
git clone https://github.com/Linference/math_model.git ~/.claude/skills/math-modeling
cd ~/.claude/skills/math-modeling && git pull  # 更新
```

**方法 B：下载 ZIP**

去 [Releases 页面](https://github.com/Linference/math_model/releases) 下载最新 `skill-vX.X.zip`，解压到 `~/.claude/skills/math-modeling/`。

---

## 两个示例简介

### 2024 国赛 CUMCM A 题 — "板凳龙闹元宵"

223 节板凳首尾相连沿阿基米德螺线盘入/调头/盘出。需要精确建模每节板凳的运动轨迹、检测非相邻板凳间的碰撞、优化调头路径。

技术点：弦长约束二分搜索、SAT 碰撞检测、带约束非线性优化。

### 2025 HiMCM Problem B — Super Bowl Sustainable Site Selection

为 NFL 建立纯环境因素驱动的选址模型，评估历史主办城市和候选新城市，扩展到奥运会等其他赛事。

技术点：AHP + TOPSIS 双层决策、Scope 1/2/3 碳排放分析、多因素敏感性分析。

---

## 如果你觉得有用

这个项目还在持续更新中。Star、Fork、提 Issue、发 PR 都欢迎。

- **Star** → 知道有人在用，有动力继续做
- **Fork** → 拿去改成你自己的版本
- **Issue** → 有 bug 或想法直接说
- **PR** → 代码和文档改进都欢迎

---

## License

MIT License.

---

> 项目用 [Claude Code](https://claude.ai/code) 驱动多智能体协作，也支持 DeepSeek V4 Pro 手动流程。有问题提 Issue，看到会回。
