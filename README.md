# 数学建模多智能体论文生成系统

[![Stars](https://img.shields.io/github/stars/Linference/math_model?style=social)](https://github.com/Linference/math_model/stargazers)
[![Forks](https://img.shields.io/github/forks/Linference/math_model?style=social)](https://github.com/Linference/math_model/network/members)
[![Version](https://img.shields.io/badge/version-v2.0-6f42c1)](https://github.com/Linference/math_model/blob/main/skill/CHANGELOG.md)
[![Release](https://img.shields.io/github/v/release/Linference/math_model)](https://github.com/Linference/math_model/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)
![LaTeX](https://img.shields.io/badge/LaTeX-xelatex-008080?logo=latex)
![Claude Code](https://img.shields.io/badge/Claude_Code-v2.0-D97757?logo=claude)
![竞赛](https://img.shields.io/badge/CUMCM_|_MCM_|_HiMCM-e74c3c)
![Subagent](https://img.shields.io/badge/质检-5_Gates-2ecc71)

---

**v2.0** — 多智能体对抗协作 + Subagent 独立质检 + 跨阶段状态管理。21 本参考手册、6 本算法 Cookbook、中英句式库、反模式知识库、环境自检脚本。

把赛题 PDF 丢进去，自动走完审题 → 选方法 → 联网找数据 → Python 求解 → 可视化 → LaTeX 论文编译 → 三角色并行对抗审稿 → 终版 PDF。国赛 CUMCM / 美赛 MCM / HiMCM 全支持。

---

## Star History

[查看 Star 趋势图](https://star-history.com/#Linference/math_model&Date)

---

## 环境搭建（国内用户）

Claude Code 的 API 在国内无法直连，需要用 CCSwitch 转发到 DeepSeek。下面是每一步的详细操作。

### 第一步：安装 Node.js

Claude Code 和 CCSwitch 都依赖 Node.js。如果你不确定装没装，打开终端（Win+R → 输入 `cmd` → 回车），输入 `node --version`，如果显示版本号且 ≥ v18 就跳过这一步。

**Windows：**

1. 打开 [nodejs.org/zh-cn](https://nodejs.org/zh-cn/)
2. 点左边绿色的 **LTS** 按钮下载（标题类似 "v20.x.x 长期支持"）
3. 双击 `.msi` 文件安装，一路点 Next 即可（所有选项保持默认）
4. 装完后关闭终端重新打开，输入 `node --version` 验证

**macOS：**

```bash
# 先装 Homebrew（如果没有）：去 https://brew.sh 复制安装命令
brew install node
```

**Linux（Ubuntu/Debian）：**

```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

验证安装成功：

```bash
node --version   # 应显示 ≥ v18.0.0
npm --version    # 应显示 ≥ 9.0.0
```

---

### 第二步：装 Claude Code

打开终端，输入：

```bash
npm install -g @anthropic-ai/claude-code
```

装完后验证：

```bash
claude --version
```

> 如果装了 VSCode，也可以在扩展商店搜 `Claude Code` 安装图形界面版。安装后在 VSCode 设置里搜 `claude` 填 API Key。

---

### 第三步：装 CCSwitch，接入 DeepSeek

CCSwitch 让 Claude Code 的请求走到 DeepSeek 而非 Anthropic，国内就能用。

1. 打开 [ccswitch.io](https://ccswitch.io) → 点 Download
   - Windows：下载 `.msi` 安装包
   - macOS：下载 `.dmg`，或用 `brew install --cask cc-switch`
   - Linux：下载 `.deb` / `.rpm` / `.AppImage`
2. 安装后打开 CCSwitch，点左侧「提供商」→「添加」，按以下填写：

   | 配置项 | 填什么 |
   |--------|--------|
   | 提供商类型 | 选择 **DeepSeek** |
   | API Key | 去 [platform.deepseek.com](https://platform.deepseek.com/) 注册 → API Keys → 创建 Key → 复制过来 |
   | 模型 | 选 `deepseek-chat`（日常）或 `deepseek-reasoner`（推理更强） |
   | Base URL | 保持默认 `https://api.deepseek.com` |

   填完点「测试连接」，提示成功即可。

3. 回到主界面，把刚添加的 DeepSeek 设为**默认后端**，点「启动代理」。状态栏显示绿色连接即表示生效。

> CCSwitch 完全免费，只从 [ccswitch.io](https://ccswitch.io) 或 [GitHub](https://github.com/farion1231/cc-switch) 下载。任何收钱的都是假的。

---

### 第四步：安装本项目 Skills

```bash
git clone https://github.com/Linference/math_model.git ~/.claude/skills/math-modeling
```

没有 Git 的话，去 [Releases](https://github.com/Linference/math_model/releases) 下载 `skill-v3.1.zip`，手动解压到 `C:\Users\你的用户名\.claude\skills\math-modeling\`（Windows）或 `~/.claude/skills/math-modeling/`（macOS/Linux）。

---

### 第五步：跑起来

打开终端，输入 `claude` 启动，然后输入：

```
/math-modeling
[粘贴赛题原文，或拖入 PDF 文件]
```

系统会自动按阶段执行：审题 → 选方法 → 找数据 → 写代码 → 画图 → 写论文 → 编译 PDF → 对抗审稿。

---

### 如果实在不想折腾

直接把 `skill/SKILL.md` 的内容复制粘贴到 [DeepSeek 网页版](https://chat.deepseek.com) 的对话框里当系统提示词，然后把赛题贴进去，手动一步步让 AI 帮你做。麻烦一点，但也能用。

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

---

## 项目更新历程

### v2.0.0 (2026-07-28) — 架构升级

**新增 Subagent 独立质检协议**：M1/P1/P2/W1/W2 五道门禁，写作者和质检者角色分离，FAIL 强制回溯。解决"自己写的代码自己审"的信任问题。

**新增跨阶段状态管理**：`state/decision_log.json` 记录每阶段决策/参数/评分，流水线中断后可恢复，不再依赖聊天上下文。

**参考手册全面升级**（6 本，3-13 倍行数增长）：
- `02-framework.md` 61→541 行：三级问题判定体系、44 种方法速查表、ML/DL 决策框架、8 个选型反例
- `03-data-acquisition.md` 97→695 行：8 类数据源速查表（含 API URL）、6 段完整获取代码、缺失值处理决策树
- `05-visualization.md` 85→1144 行：16 种图表含代码骨架、5 套色觉友好配色、10 个 wrong→right 对照
- `07-adversarial-review.md` 69→449 行：三角色评分锚点（0-10 五档）、评审模板、修改-复评循环协议
- `data-sources.md` 33→367 行：分类数据源大全（经济/环境/气候/人口/交通/能源），每源含 API 端点
- `scoring-rubric.md` 128→303 行：国赛+美赛双评分标准、五维度锚定描述、评分校准

**新增文件**（8 个）：
- `11-anti-patterns.md`（654 行）：24 个建模常见错误，症状→诊断→修复三段式
- `13-phrase-bank.md`（401 行）：中英双语句式库，按章节组织，含美赛 Memo 专用
- `cookbooks/`（6 本，~2200 行）：独立算法手册（优化/评价/预测/机理/统计ML/网络博弈）
- `doctor.py`：37 项环境自检，一键 `python doctor.py`
- `decision_log.json`：跨阶段状态模板
- `assumption_table.md`：标准化假设表格（假设→论证→影响→违反后果）
- `playbook-guide.md`：样本项目走通指南
- `CHANGELOG.md`：本更新记录

**SKILL.md 重写**：新增 Subagent 质检协议、路径解析协议、参考手册速查表、每阶段反模式检查项。从 404 行精简为 370 行。

### v1.2 (2026-07-27) — 初始版本

- 7 阶段强制流水线（0-7）+ 硬性门禁
- 8 个子智能体（审题/建模/数据/编程/写作/审稿/验证/推理）
- 三角色并行对抗审稿（Workflow 驱动，≤4 轮，targetScore 7.5）
- 12 本参考手册（01-10 + data-sources + scoring-rubric）
- 5 个辅助脚本（new_project/fetch_data/compile/plot_helpers/verify_results）
- 中英双版 LaTeX 模板（cumcm-zh/mcm-en）
- 四个深度要求（假设量化/对比模型/创新声明/多指标）
- 数据引擎（World Bank API + 质量报告 + 多源合并 + 小样本增强）
- 两个完整样本项目（2024 国赛 A + 2025 HiMCM B）
