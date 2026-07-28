<!--
  ╔══════════════════════════════════════════════════════════════╗
  ║    数学建模多智能体论文生成系统                                ║
  ║    Math Modeling Multi-Agent Paper Generation System         ║
  ╚══════════════════════════════════════════════════════════════╝
-->

<div align="center">

<!-- Banner 占位：可替换为你的项目 Logo / Banner 图片 -->
<h1>📐 数学建模多智能体论文生成系统</h1>
<h3>Math Modeling Multi-Agent Paper Generation System</h3>

<!-- Badges -->
<p>
  <a href="https://github.com/Linference/math_model/stargazers"><img src="https://img.shields.io/github/stars/Linference/math_model?style=for-the-badge&logo=github&color=f1c40f" alt="Stars"></a>
  <a href="https://github.com/Linference/math_model/network/members"><img src="https://img.shields.io/github/forks/Linference/math_model?style=for-the-badge&logo=github&color=3498db" alt="Forks"></a>
  <a href="https://github.com/Linference/math_model/releases"><img src="https://img.shields.io/github/v/release/Linference/math_model?include_prereleases&style=for-the-badge&logo=github&color=2ecc71" alt="Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=for-the-badge" alt="License"></a>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/LaTeX-xelatex-008080?style=flat-square&logo=latex&logoColor=white" alt="LaTeX">
  <img src="https://img.shields.io/badge/Claude_Code-v2.0+-D97757?style=flat-square&logo=claude&logoColor=white" alt="Claude Code">
  <img src="https://img.shields.io/badge/竞赛-CUMCM_|_MCM_|_HiMCM-e74c3c?style=flat-square" alt="竞赛">
  <img src="https://img.shields.io/badge/平台-Windows_|_macOS_|_Linux-9b59b6?style=flat-square" alt="平台">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square" alt="PRs Welcome">
</p>

---

<p>
  <b>⭐ 如果这个项目帮到了你，请给一颗 Star！你的支持是我持续更新的动力 ⭐</b>
</p>

</div>

---

## 📈 Star History

<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=Linference/math_model&type=Date&legend=top-left)](https://star-history.com/#Linference/math_model&Date)

> 点击上方图表可跳转到 [Star History](https://star-history.com/) 查看实时趋势。⭐ **Star 越多，更新越快！**

</div>

---

## 📖 项目简介

这是一套**端到端的数学建模竞赛论文自动生成系统**，基于 Claude Code 的多智能体对抗协作架构。你只需把赛题原文丢进去，系统会**自动完成**从审题到最终 PDF 论文的全部流程：

```
📄 赛题原文 → 🔍 深度审题 → 📊 建模选型 → 🌐 联网找数据
           → 💻 编程求解 → 📈 可视化 → 📝 LaTeX 写作
           → 📕 编译 PDF → ⚔️ 多智能体对抗审稿 → 🏆 国赛级论文
```

**核心思路**：让 8 个专业 AI 智能体组成一支"虚拟建模队伍"——审题专家拆解赛题、方法专家选择模型、数据专家去网上找数据、编程专家跑代码出图、写作专家填 LaTeX 模板，最后由审稿人/验证者/推理者三个"杠精"围殴论文，逼着写作者反复修改，直到论文质量达标。

> 🎯 **适用竞赛**：国赛 CUMCM（中文论文）· 美赛 MCM/ICM（英文论文）· HiMCM 高中生数学建模

---

## ✨ 核心特性

### 🔄 7 阶段强制流水线

| 阶段 | 内容 | 子智能体 | 落盘产出 |
|:--:|------|----------|----------|
| 0 | 建立工作目录 | — | 项目骨架 |
| 1 | **深度审题** | `mm-problem-analyst` | 审题报告 (problem.md) |
| 2 | **建模方法选型** | `mm-modeler` | 建模方案 + 图表清单 |
| 3 | **数据获取** | `mm-data-hunter` | 数据 CSV + 来源记录 |
| 4 | **编程求解** | `mm-coder` | Python 脚本 + 结果 |
| 5 | **可视化** | `mm-coder` | 高质量图表 PNG |
| 6 | **LaTeX 写作** | `mm-writer` | 论文 .tex → 编译 PDF |
| 7 | **对抗审稿** | 三个评审并行 | 审稿意见 + 修改 + 复评 |

> ⚠️ **硬性门禁**：每阶段必须落盘产出，验证通过后才进入下一阶段。禁止跳步、合并、颠倒。

### 🤖 8 个专项子智能体

| 智能体 | 角色定位 | 一句话描述 |
|--------|----------|------------|
| `mm-problem-analyst` | 🔍 审题专家 | 逐问拆解赛题，挖出显性/隐性约束、评分点和常见陷阱 |
| `mm-modeler` | 🧠 方法顾问 | 为每一问选建模方法，判断是否需要 ML/DL，给出理由 |
| `mm-data-hunter` | 🏹 数据猎人 | 联网搜索（维基/GitHub/Kaggle/官方统计/sklearn）找数据 |
| `mm-coder` | 💻 编程求解 | Python 实现模型、跑通求解、生成结果与可视化图表 |
| `mm-writer` | ✍️ 论文写手 | 填充 LaTeX 模板、逐条回应审稿意见、补充实验 |
| `mm-reviewer` | 🔴 审稿人 | 五维度 0-10 打分，无情挑刺，定位论文弱点 |
| `mm-verifier` | ✅ 验证者 | 交叉验证数值结果、检查量纲/边界/单位自洽性 |
| `mm-reasoner` | 📐 推理者 | 深度审计公式推导每一步严谨性，补全未证断言 |

### ⚔️ 对抗审稿机制（核心创新）

这是整个系统最独特的环节——不是让一个 AI 自己写自己改，而是让**不同的 AI 角色互相对抗**：

```
写作者产出初稿
  ┌─────────────────────────────────────────┐
  │  📝 审稿人（批判打分）                     │
  │  🔢 验证者（数值交叉验证）  ← 三评审并行    │
  │  📐 推理者（公式推导审计）                  │
  └─────────────────────────────────────────┘
                    ↓
          聚合评分（五维度 0-10）
                    ↓
        ┌─ 均分 ≥ 7.5？──→ ✅ 达标，输出终稿
        │
        └─ < 7.5 且未满 4 轮？
                    ↓
      写作者按 high→low 弱点逐条修改
      （含自动补充实验/修正公式/重绘图表）
                    ↓
            三评审再次打分 → 循环
```

**五评分维度**：建模合理性 · 数学严谨性 · 结果与验证充分性 · 表达与图表规范 · 创新性

### 📊 论文质量保障

- **每阶段验证门禁**：执行 → 验证 → 确认，不通过不前进
- **摘要 ≤ 1 页、目录 ≤ 1 页**：硬性约束，溢出自动压缩
- **无大空白、无文字溢出**：`\raggedbottom` + 浮动间距紧凑 + 容忍度优化
- **16 种图表类型**：折线/柱状/散点/热力图 + 3D 曲面/雷达图/小提琴图/网络图/瀑布图/山脊图/流图/桑基图等
- **四项深度要求**：假设局限性量化讨论 + 对比模型验证 + 创新点声明 + 多指标评估
- **中英双模板**：国赛 ctex/xelatex（中文）· 美赛 pdflatex（英文），盲审就绪
- **自动交叉验证**：`verify_results.py` 比对代码输出与论文数字一致性

---

## 📁 项目结构

```
math_model/
│
├── README.md                           # 👈 你正在读的文件
├── .gitignore
│
├── 📂 2024_CUMCM_A/                    # 示例项目 1：2024 国赛 A 题 "板凳龙"
│   ├── A题.pdf                         #   赛题原题 PDF
│   ├── problem.md                      #   审题报告
│   ├── REPORT.md                       #   建模全流程记录
│   ├── format2024.doc                  #   国赛论文格式模板
│   ├── _read_excel.py                  #   数据读取工具
│   ├── code/                           #   Python 求解代码
│   │   ├── utils.py                    #     公共函数（运动学/几何）
│   │   ├── solve_q1.py                 #     问题 1：运动学正解
│   │   ├── solve_q2.py                 #     问题 2：碰撞检测
│   │   ├── solve_q3.py                 #     问题 3：最小螺距
│   │   ├── solve_q4.py                 #     问题 4：调头路径
│   │   ├── solve_q5.py                 #     问题 5：最大速度
│   │   └── figures.mplstyle            #     matplotlib 样式
│   ├── data/                           #   数据与结果
│   │   ├── result{1,2,4}.xlsx          #     计算结果
│   │   └── SOURCES.md                  #     数据来源记录
│   ├── figures/                        #   高清输出图表
│   │   ├── fig_q1_spiral_overview.png
│   │   ├── fig_q1_head_tail_trajectory.png
│   │   ├── fig_q1_velocity_distribution.png
│   │   ├── fig_q2_collision_snapshot.png
│   │   ├── fig_q2_min_distance_curve.png
│   │   ├── fig_q3_critical_config.png
│   │   ├── fig_q3_pitch_vs_margin.png
│   │   ├── fig_q4_turn_geometry.png
│   │   ├── fig_q4_turn_snapshots.png
│   │   ├── fig_q4_velocity_evolution.png
│   │   ├── fig_q5_amplification_factor.png
│   │   ├── fig_q5_bottleneck_location.png
│   │   └── fig_q5_speed_relation.png
│   ├── paper/                          #   LaTeX 论文
│   │   ├── main.tex                    #     论文主文件
│   │   └── refs.bib                    #     参考文献
│   └── 附件/                           #   竞赛提交附件
│       ├── result1.xlsx
│       ├── result2.xlsx
│       └── result4.xlsx
│
├── 📂 2025_HiMCM_Problem_B/            # 示例项目 2：2025 HiMCM B 题 "超级碗选址"
│   ├── 2025_HiMCM_Problem_B.pdf        #   赛题原题 PDF
│   ├── problem.md                      #   审题报告
│   ├── REPORT.md                       #   建模全流程记录
│   ├── code/                           #   Python 求解代码
│   │   ├── solve_q1.py                 #     问题 1：指标体系
│   │   ├── solve_q2.py                 #     问题 2：AHP 层次分析
│   │   ├── solve_q3a.py                #     问题 3a：TOPSIS 排名
│   │   ├── solve_q3b.py                #     问题 3b：候选城市评估
│   │   ├── solve_q4ab.py               #     问题 4a-4b：模型扩展
│   │   ├── solve_q4c.py                #     问题 4c：策略分析
│   │   ├── solve_q4d.py                #     问题 4d：多赛事比较
│   │   └── figures.mplstyle            #     matplotlib 样式
│   ├── data/                           #   数据与来源
│   │   ├── city_indicators.csv         #     城市环境指标
│   │   ├── superbowl_lix_baseline.csv  #     Super Bowl LIX 基线
│   │   ├── event_emission_params.csv   #     赛事排放参数
│   │   └── SOURCES.md                  #     数据来源记录
│   ├── figures/                        #   高清输出图表（19张）
│   │   ├── fig_q1_*.png                #     问题 1：热力图/雷达图/维度图
│   │   ├── fig_q2_*.png                #     问题 2：AHP权重/相关性矩阵
│   │   ├── fig_q3a_*.png               #     问题 3a：TOPSIS/敏感性/雷达
│   │   ├── fig_q3b_*.png               #     问题 3b：综合排名/对比
│   │   └── fig_q4*.png                 #     问题 4：扩展/热力图/边际效益
│   ├── results/                        #   数值结果
│   │   ├── q1_results.txt
│   │   ├── ahp_weights.csv
│   │   ├── q3a_topsis_ranking.csv
│   │   ├── q3b_combined_ranking.csv
│   │   ├── q4b_olympic_ranking.csv
│   │   ├── q4c_scenario_rank_changes.csv
│   │   └── q4d_comparison.txt
│   └── paper/                          #   LaTeX 论文
│       ├── main.tex
│       ├── main.pdf                    #   ✅ 已编译完成的 PDF
│       └── refs.bib
│
└── 📂 .claude/                         # Claude Code 项目配置
    └── settings.local.json
```

---

## 🚀 快速开始

### 前提条件

| 工具 | 用途 | 安装方式 |
|------|------|----------|
| **Python 3.10+** | 科学计算 + 绘图 | [Anaconda](https://www.anaconda.com/) 或 [python.org](https://python.org) |
| **LaTeX** | 论文编译（xelatex） | [MiKTeX](https://miktex.org/) (Win) / [TeXLive](https://tug.org/texlive/) (跨平台) |
| **Claude Code** | AI 编排引擎 | 见下方详细安装指南 |
| **Git** | 版本控制 | [git-scm.com](https://git-scm.com/) |

### Python 依赖

```bash
pip install numpy pandas scipy scikit-learn matplotlib seaborn openpyxl
```

### 一键使用

在 Claude Code 中直接输入以下命令，然后把赛题原文贴进去：

```
/math-modeling

[在此粘贴赛题原文——PDF 截图或文字均可]
```

Claude Code 会自动按 7 阶段流水线执行：
1. 创建项目工作目录
2. 调用审题专家拆解赛题
3. 调用方法专家选定建模方案
4. 调用数据猎人联网搜索数据
5. 调用编程专家求解并画图
6. 调用写作专家填充 LaTeX 模板
7. 启动审稿人/验证者/推理者三评审对抗审稿

**最终产出**：一份可直接提交的 PDF 论文 + 全部代码和数据。

---

## 🛠️ 完整开发环境搭建指南

> 本项目的完整运行依赖 **Claude Code** 作为 AI 编排引擎。以下是最详细的安装与配置指南。

---

### 1️⃣ Claude Code CLI（终端版）安装

Claude Code 是 Anthropic 推出的命令行 AI 编程助手，支持直接在终端中使用。

#### 步骤 1：安装 Node.js

Claude Code 依赖 Node.js 环境，请先安装：

```bash
# 方法 A：官网下载安装（推荐 Windows 用户）
# 👉 https://nodejs.org/zh-cn（选择 LTS 版本，≥18.x）

# 方法 B：命令行安装（macOS / Linux）
# macOS (Homebrew)
brew install node

# Ubuntu / Debian
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

验证安装：
```bash
node --version   # 应显示 ≥ v18.x
npm --version    # 应显示 ≥ 9.x
```

#### 步骤 2：安装 Claude Code

```bash
# 全局安装 Claude Code CLI
npm install -g @anthropic-ai/claude-code

# 验证安装
claude --version
```

#### 步骤 3：启动与认证

```bash
# 在项目目录中启动
cd "你的项目路径"
claude

# 首次启动会自动打开浏览器进行 Anthropic 账号登录
# 或使用 API Key 认证（推荐国内用户）：
export ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxx"
claude
```

> 📌 **获取 API Key**：访问 [console.anthropic.com](https://console.anthropic.com/) 注册并生成 API Key。

#### 步骤 4：验证安装

启动后输入：
```
你好，请简单介绍一下你自己
```

如果正常回复，安装完成 ✅

---

### 2️⃣ VSCode 中安装 Claude Code 扩展

在 VSCode 中直接使用 Claude Code，体验更佳：

#### 安装步骤

1. **打开 VSCode**，点击左侧活动栏的「扩展」图标（或按 `Ctrl+Shift+X`）
2. **搜索** `Claude Code`
3. 找到由 **Anthropic** 发布的官方扩展，点击 **「安装」**
4. 安装完成后，重启 VSCode

#### 配置 Claude Code 扩展

1. 打开 VSCode 设置（`Ctrl+,`）
2. 搜索 `claude`
3. 找到 **Claude: API Key** 设置项，填入你的 API Key

或者在 VSCode 的 `settings.json` 中添加：
```json
{
  "claude.apiKey": "sk-ant-xxxxxxxxxxxxx"
}
```

#### 使用方式

- **命令面板**：按 `Ctrl+Shift+P`，输入 `Claude` 查看所有可用命令
- **侧边栏**：点击左侧活动栏的 Claude 图标，打开对话面板
- **内联编辑**：选中代码 → 右键 → 「Claude: Edit Selection」
- **终端集成**：在 VSCode 终端中直接输入 `claude`

> 📌 **参考文档**：[Claude Code VSCode 扩展官方文档](https://docs.anthropic.com/en/docs/claude-code/ide-integrations#vs-code)

---

### 3️⃣ CCSwitch 安装与使用指南

[**CCSwitch**](https://github.com/ccswitch/ccswitch) 是一个 Claude Code 配置切换工具，可以让你在同一台机器上**快速切换不同的 Claude Code 配置**——比如在公司用 API Key、回家用另一个 Key，或者在多个 Anthropic 账号间切换。

#### 为什么需要 CCSwitch？

- 🏠 **多环境切换**：家里一套配置，公司一套配置，一键切换
- 🔑 **多 API Key 管理**：不同项目用不同 Key，互不干扰
- 🌐 **代理切换**：国内/国外网络环境一键适配
- 💾 **配置备份**：快速备份/恢复 Claude Code 配置

#### 安装 CCSwitch

```bash
# 方法 A：从 GitHub 克隆安装
git clone https://github.com/ccswitch/ccswitch.git
cd ccswitch
npm install
npm link

# 方法 B：直接 npm 安装（如果已发布到 npm）
npm install -g ccswitch
```

#### CCSwitch 基本使用

```bash
# 1. 查看当前配置
ccswitch status

# 2. 列出所有保存的配置环境
ccswitch list

# 3. 创建一个新配置环境（例如：工作用）
ccswitch create work
# 按提示填入 API Key、代理设置等

# 4. 创建另一个配置环境（例如：个人项目）
ccswitch create personal

# 5. 切换配置环境
ccswitch use work       # 切换到工作环境
ccswitch use personal   # 切换到个人环境

# 6. 备份当前配置
ccswitch backup

# 7. 恢复配置
ccswitch restore
```

#### CCSwitch 典型工作流

```bash
# 场景：白天在公司用公司 API Key，晚上回家用个人 Key

# 上午到公司：
ccswitch use work          # 一键切到公司配置

# 晚上回家：
ccswitch use personal      # 一键切到个人配置

# 去国外出差：
ccswitch use us-proxy      # 切到带代理的配置
```

> 📌 更多用法详见 [CCSwitch 官方文档](https://github.com/ccswitch/ccswitch)

---

### 4️⃣ 备选方案：DeepSeek V4 Pro

如果因为网络或地区限制**无法使用 Claude Code**，可以选择 **DeepSeek V4 Pro** 作为备选方案：

#### DeepSeek V4 Pro 简介

DeepSeek V4 Pro 是 DeepSeek 推出的高性能大模型，具备以下优势：

| 对比维度 | Claude Code | DeepSeek V4 Pro |
|----------|-------------|-----------------|
| **访问方式** | 需 Anthropic API / 海外网络 | 国内直接访问 |
| **中文能力** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐（原生中文） |
| **数学推理** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **代码能力** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐½ |
| **价格** | $3/$15 per MTok | 显著更低 |
| **上下文窗口** | 200K tokens | 128K tokens |

#### 使用 DeepSeek V4 Pro 运行本项目

1. **注册 DeepSeek 账号**：访问 [platform.deepseek.com](https://platform.deepseek.com/)
2. **获取 API Key**：在控制台 → API Keys → 创建新 Key
3. **使用方式**：

```bash
# 方式 A：通过 Web 界面（最简单）
# 直接访问 chat.deepseek.com，上传赛题 PDF，粘贴本项目的 SKILL.md 指令

# 方式 B：通过 API 调用
# 安装 openai 兼容客户端
pip install openai

# Python 脚本调用示例
from openai import OpenAI

client = OpenAI(
    api_key="sk-xxxxxxxx",  # 替换为你的 DeepSeek API Key
    base_url="https://api.deepseek.com"
)

# 发送赛题 + 系统指令
response = client.chat.completions.create(
    model="deepseek-chat",  # 或 deepseek-reasoner（推理增强）
    messages=[
        {"role": "system", "content": open("SKILL.md").read()},  # 系统指令
        {"role": "user", "content": "请分析这道数学建模赛题：[贴入题目]"}
    ]
)
print(response.choices[0].message.content)

# 方式 C：通过 Continue / Cody 等 VSCode 插件
# 在插件设置中将 Provider 改为 DeepSeek，填入 API Key
```

> 💡 **提示**：本项目虽然为 Claude Code 深度优化（利用了多智能体 Agent 体系），但核心的流水线逻辑和子智能体角色定义（`SKILL.md` / `references/`）可以适配到任何支持系统指令的大模型中。DeepSeek V4 Pro 在数学推理和中文写作方面的能力也很强，可以手动分步执行流水线。

---

### 5️⃣ 推荐 VSCode 扩展（增强体验）

以下扩展能显著提升本项目的使用体验：

#### 📝 文档与 Markdown 类

| 扩展名 | 图标 | 用途 | 安装 ID |
|--------|------|------|---------|
| **Markdown Preview Enhanced** | 📘 | 增强 Markdown 预览，支持数学公式渲染 | `shd101wyy.markdown-preview-enhanced` |
| **Markdown All in One** | 📝 | Markdown 编辑增强：快捷键/目录/自动补全 | `yzhang.markdown-all-in-one` |
| **Markdown PDF** | 📄 | 一键将 .md 导出为 PDF/HTML/PNG | `yzane.markdown-pdf` |
| **Markdownlint** | ✅ | Markdown 语法检查，确保规范 | `davidanson.vscode-markdownlint` |
| **LaTeX Workshop** | 📚 | LaTeX 编辑与编译一体化 | `james-yu.latex-workshop` |

#### 📊 Office / 表格类

| 扩展名 | 图标 | 用途 | 安装 ID |
|--------|------|------|---------|
| **Excel Viewer** | 📊 | 在 VSCode 中直接查看 .xlsx / .csv 文件 | `grapecity.gc-excelviewer` |
| **Rainbow CSV** | 🌈 | CSV 列高亮着色，一眼看清数据列 | `mechatroner.rainbow-csv` |
| **vscode-pdf** | 📕 | 在 VSCode 中直接查看 PDF 文件 | `tomoki1207.pdf` |
| **Office Viewer (Markdown Editor)** | 🏢 | 在 VSCode 中查看 .doc/.docx/.xlsx/.pptx | `cweijan.vscode-office` |

#### 🤖 AI 辅助类

| 扩展名 | 图标 | 用途 | 安装 ID |
|--------|------|------|---------|
| **Claude Code** | 🧠 | 官方 Claude Code 扩展 | 见上方安装指南 |

#### 🎨 通用增强类

| 扩展名 | 图标 | 用途 | 安装 ID |
|--------|------|------|---------|
| **Project Manager** | 📂 | 多项目管理，快速切换 | `alefragnani.project-manager` |
| **Better Comments** | 💬 | 注释高亮着色（TODO/FIXME/!） | `aaron-bond.better-comments` |
| **Error Lens** | 🔍 | 行内显示错误/警告信息 | `usernamehw.errorlens` |
| **GitLens** | 🔀 | Git 超级增强：blame/历史/对比 | `eamodio.gitlens` |

#### 一键安装所有推荐扩展

在终端中执行以下命令，一次性安装全部推荐扩展：

```bash
# Markdown
code --install-extension shd101wyy.markdown-preview-enhanced
code --install-extension yzhang.markdown-all-in-one
code --install-extension yzane.markdown-pdf
code --install-extension davidanson.vscode-markdownlint

# LaTeX
code --install-extension james-yu.latex-workshop

# Office / 表格
code --install-extension grapecity.gc-excelviewer
code --install-extension mechatroner.rainbow-csv
code --install-extension tomoki1207.pdf
code --install-extension cweijan.vscode-office

# 通用增强
code --install-extension alefragnani.project-manager
code --install-extension aaron-bond.better-comments
code --install-extension usernamehw.errorlens
code --install-extension eamodio.gitlens
```

> 💡 如果 `code` 命令未识别，在 VSCode 中按 `Ctrl+Shift+P`，输入 `Shell Command: Install 'code' command in PATH`，回车即可。

---

## 📦 Skills 安装包（Releases）

本项目的核心是一套完整的 **Claude Code Skills**（技能包），包含 8 个子智能体的完整定义、流水线控制脚本、LaTeX 模板和工具脚本。

### 下载安装

前往 **[Releases 页面](https://github.com/Linference/math_model/releases)** 下载最新版本。

| 文件 | 说明 |
|------|------|
| `math-modeling-v3.1.zip` | 完整 Skills 安装包 |
| `Source code (zip)` | 项目源代码 |
| `Source code (tar.gz)` | 项目源代码（tar.gz） |

### 安装方式

**方法 A：Git 克隆（推荐，可自动更新）**
```bash
# 克隆到 Claude Code skills 目录
git clone https://github.com/Linference/math_model.git ~/.claude/skills/math-modeling

# 后续更新
cd ~/.claude/skills/math-modeling && git pull
```

**方法 B：下载 ZIP 手动安装**
```bash
# 下载 Releases 中的 math-modeling-vX.X.zip
# 解压到 ~/.claude/skills/math-modeling/
```

### Skills 包含内容

```
math-modeling/
├── SKILL.md                    # 主技能定义（7阶段流水线）
├── README.md                   # 技能说明文档
│
├── 📂 references/              # 10 本参考手册（给 AI 用的知识库）
│   ├── 01-problem-analysis.md  #   深度审题方法论
│   ├── 02-framework.md         #   建模框架选型指南
│   ├── 03-data-acquisition.md  #   数据获取策略
│   ├── 04-modeling-cookbook.md #   建模算法手册
│   ├── 05-visualization.md     #   可视化规范
│   ├── 06-writing.md           #   LaTeX 写作标准
│   ├── 07-adversarial-review.md#   对抗审稿机制
│   ├── 08-stage-verification.md#   阶段验证门禁
│   ├── 09-innovation-playbook.md#  创新方法手册（12种策略）
│   ├── 10-modeling-tricks.md   #   数学建模 33 讲优化技巧
│   ├── data-sources.md         #   数据源大全
│   └── scoring-rubric.md       #   评分细则
│
├── 📂 scripts/                 # 辅助脚本
│   ├── new_project.py          #   新建项目骨架
│   ├── fetch_data.py           #   联网获取数据
│   ├── compile.py              #   编译 LaTeX→PDF
│   ├── plot_helpers.py         #   16种图表绘制工具
│   └── verify_results.py       #   交叉验证（代码 vs 论文）
│
├── 📂 templates/               # LaTeX 模板
│   ├── cumcm-zh/main.tex       #   国赛中文模板
│   ├── mcm-en/main.tex         #   美赛英文模板
│   └── figures.mplstyle        #   matplotlib 全局样式
│
├── 📂 samples/                 # 示例项目
│   └── 2025_HiMCM_Problem_B/   #   HiMCM 示例
│
└── 📂 workflows/               # 工作流脚本
    └── adversarial-review.js   #   对抗审稿工作流
```

> 📌 **Release 版本历史**：v3.1 (当前) → v3.0 → v2.2 → v2.1。详见 [Releases](https://github.com/Linference/math_model/releases)。

---

## 🔗 相关仓库与参考链接

### 本项目相关

| 仓库 | 说明 |
|------|------|
| ⭐ [Linference/math_model](https://github.com/Linference/math_model) | 本仓库——数学建模多智能体系统 |
| 📦 [Skills Releases](https://github.com/Linference/math_model/releases) | 完整 Skills 安装包下载 |

### 工具链参考

| 仓库 / 链接 | 说明 |
|-------------|------|
| 🧠 [Anthropic Claude Code](https://docs.anthropic.com/en/docs/claude-code) | Claude Code 官方文档 |
| 🔌 [Claude Code VSCode 扩展](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code) | VSCode 扩展市场页面 |
| 🔄 [CCSwitch](https://github.com/ccswitch/ccswitch) | Claude Code 配置切换工具 |
| 🤖 [DeepSeek Platform](https://platform.deepseek.com/) | DeepSeek V4 Pro 备选方案 |
| 📐 [CUMCM 官网](http://www.mcm.edu.cn/) | 全国大学生数学建模竞赛官网 |
| 🌍 [MCM/ICM 官网](https://www.comap.com/contests/mcm-icm) | 美国大学生数学建模竞赛官网 |

### 推荐参考的开源项目

| 仓库 | Stars | 说明 |
|------|-------|------|
| [Visualize-ML/Book7](https://github.com/Visualize-ML/Book7_Visualizations-for-Mathematical-Modeling) | 🔥 | 数学建模可视化方法大全 |
| [zhanwen/MathModel](https://github.com/zhanwen/MathModel) | ⭐ | 数学建模算法汇总 |
| [BetterBench/Math_modeling](https://github.com/BetterBench/Math_modeling) | ⭐ | 数学建模学习资源合集 |
| [qiqiqiqishu/Mathematical-Modeling-Competition](https://github.com/qiqiqiqishu/Mathematical-Modeling-Competition) | ⭐ | 竞赛经验与代码分享 |
| [luoguofeng0406/Mathematical-Modeling](https://github.com/luoguofeng0406/Mathematical-Modeling) | ⭐ | 常用建模算法 Python 实现 |

---

## 📝 示例项目展示

### 示例 1：2024 国赛 CUMCM A 题 "板凳龙闹元宵"

> **赛题**：[2024_CUMCM_A/A题.pdf](2024_CUMCM_A/A题.pdf)  
> **关键词**：运动学建模、几何约束、碰撞检测、螺线方程、数值求解

**核心挑战**：
- 223 节板凳首尾相连沿阿基米德螺线盘入/盘出
- 精确计算每节板凳在任意时刻的位置和速度
- 检测非相邻板凳间的碰撞（30cm 矩形板面刚体）
- 优化调头路径使其面积最小

**技术亮点**：
- 弦长约束二分搜索求解把手位置（亚毫米精度）
- SAT（分离轴定理）碰撞检测
- 带约束的非线性优化求解最小螺距

---

### 示例 2：2025 HiMCM Problem B "超级碗可持续选址"

> **赛题**：[2025_HiMCM_Problem_B/2025_HiMCM_Problem_B.pdf](2025_HiMCM_Problem_B/2025_HiMCM_Problem_B.pdf)  
> **关键词**：MCDM、AHP、TOPSIS、碳足迹、可持续发展、决策分析

**核心挑战**：
- 建立纯环境因素驱动的选址决策模型（不考虑经济）
- 将模型应用于 19 个历史主办城市和 3 个候选城市的评估
- 扩展模型至奥运会/世界杯等其他大型赛事

**技术亮点**：
- AHP + TOPSIS 双层决策框架
- Scope 1/2/3 碳排放全生命周期分析
- 多因素敏感性分析（龙卷风图）
- 边际减排效益曲线

---

## 🌟 致谢与支持

### 如果这个项目帮到了你

<div align="center">

| 动作 | 链接 | 效果 |
|:--:|------|------|
| ⭐ **Star** | 页面右上角 ⭐ 按钮 | 让更多人发现这个项目 |
| 🍴 **Fork** | 页面右上角 🍴 按钮 | 二次开发，分享你的改进 |
| 📢 **分享** | 分享到知乎/CSDN/竞赛群 | 帮助更多建模人 |
| 🐛 **Issue** | [提交 Issue](https://github.com/Linference/math_model/issues) | 报告 Bug 或提建议 |
| 💡 **PR** | [提交 Pull Request](https://github.com/Linference/math_model/pulls) | 贡献代码/文档改进 |

</div>

### 你的 Star 意味着什么

- ✨ **1 Star** = "这个项目有点意思"
- 📌 **10 Stars** = "真的有人用起来了"
- 🔥 **50 Stars** = "是建模圈值得关注的项目"
- 🚀 **100+ Stars** = "数学建模标杆开源项目"

> **每一个 Star 都是我更新的动力！** 看到 Star 数涨了，我就会加更多示例项目、更新 Skills 新功能、完善文档。如果这个项目为你节省了数十小时的建模时间，**请点一颗 Star 支持一下** 🙏

---

## 📄 License

本项目采用 [MIT License](LICENSE) 开源协议。你可以自由地使用、修改、分发本项目代码，但需保留原始版权声明。

---

<div align="center">

**[⬆ 回到顶部](#-数学建模多智能体论文生成系统)** · **[📦 下载 Skills](https://github.com/Linference/math_model/releases)** · **[🐛 报告问题](https://github.com/Linference/math_model/issues)** · **[💡 贡献代码](https://github.com/Linference/math_model/pulls)**

---

<p>
  <sub>Made with ❤️ by <a href="https://github.com/Linference">Linference</a> · Powered by <a href="https://claude.ai">Claude Code</a> · 愿每一篇论文都值得被看见</sub>
</p>

</div>
