# math-modeling — 数学建模多智能体论文生成系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![LaTeX](https://img.shields.io/badge/LaTeX-xelatex-green.svg)](https://www.latex-project.org/)

端到端把一道数学建模赛题做成**国赛 / 美赛级别**论文 PDF。

**多智能体对抗协作**：深度审题 → 建模框架与方法选型（含 ML/DL 决策）→ 联网找数据（维基/GitHub/Kaggle/官方统计/sklearn）→ 编程求解与可视化 → LaTeX 写作 → 编译 PDF → 写作者/审稿人/验证者/推理者多轮对抗审稿（评分 5.0 → 7.5+）。

中英双模板（国赛 CUMCM 中文 · 美赛 MCM 英文），编译即得盲审就绪的 PDF。

---

## 核心特性

### 7 阶段强制流水线

```
阶段 0 建立工作目录 → 阶段 1 深度审题 → 阶段 2 建模方法选型
→ 阶段 3 数据获取 → 阶段 4 编程求解 → 阶段 5 可视化
→ 阶段 6 LaTeX 写作与编译 → 阶段 7 多轮对抗审稿
```

**硬性门禁**：每阶段必须落盘产出，确认后才可进入下一阶段。禁止跳步、合并、颠倒。

### 8 个专项子智能体

| 子智能体 | 角色 | 阶段 |
|---|---|---|
| `mm-problem-analyst` | 深度审题：逐问拆解、显隐约束、评分点、陷阱 | 1 |
| `mm-modeler` | 方法选型：判定 ML/DL 需求、列图表清单、验证方案 | 2 |
| `mm-data-hunter` | 联网找数据：维基/GitHub/Kaggle/官方统计/sklearn | 3 |
| `mm-coder` | 编程求解与可视化：Python 实现、跑通、出图 | 4-5 |
| `mm-writer` | LaTeX 写作与修改：填充模板、回应审稿意见 | 6-7 |
| `mm-reviewer` | 批判审稿：五维度 0-10 打分、定位弱点 | 7 |
| `mm-verifier` | 交叉验证：数值/量纲/边界/自洽性检查 | 7 |
| `mm-reasoner` | 数学推理：公式推导审计、补全未证断言 | 7 |

### 对抗审稿（核心创新）

```
写作者产出草稿
  → [审稿人 ∥ 验证者 ∥ 推理者] 并行对抗打分（0-10，五维度）
  → 聚合平均分
  → 若 < 7.5 且 ≤ 4 轮：
       写作者按 high→low 弱点逐条修改（含自动补充实验）
       → 三评审复评
  → 达标或用尽 4 轮停止
```

五评分维度：建模合理性 · 数学严谨性 · 结果与验证充分性 · 表达与图表规范 · 创新性

### 论文质量保障

- **摘要 / 目录各一页以内**：硬性约束，溢出则自动压缩
- **无大空白、无文字溢出**：`\raggedbottom` + 浮动间距紧凑 + 容忍度优化
- **高端可视化**：除 6 种基础图外，提供 10 种高端图（3D 曲面、雷达图、小提琴图、网络图、瀑布图、山脊图、流图等）
- **四项深度要求**：假设局限性量化讨论 + 对比模型验证 + 创新点显式声明 + 多指标评估
- **中英双模板**：国赛 ctex/xelatex · 美赛 pdflatex，盲审就绪

---

## 快速开始

### 前提条件

- **LaTeX**：xelatex（MiKTeX 或 TeXLive），中文需 ctex/xeCJK
- **Python**：anaconda `python`（numpy, pandas, scipy, scikit-learn, matplotlib 就绪）
- **Claude Code**：已安装子智能体于 `~/.claude/agents/`

### 使用方式

在 Claude Code 中直接说，或输入：

```
/math-modeling  把赛题原文贴在这里
```

Claude 会自动按 7 阶段流水线执行：建目录 → 审题 → 选方法 → 找数据 → 求解出图 → 写论文编 PDF → 对抗审稿。

### 手动运行单步

```bash
# 建工作目录（zh=国赛 / en=美赛）
python scripts/new_project.py "2024国赛A题" --lang zh

# 找数据
python scripts/fetch_data.py --sklearn iris

# 自测所有绘图（生成 16 张示例图）
python scripts/plot_helpers.py

# 编译论文（中文自动 xelatex）
python scripts/compile.py <slug>/paper/main.tex
```

### 对抗审稿（多智能体）

```javascript
Workflow({
  scriptPath: "<skill>/workflows/adversarial-review.js",
  args: {
    draftPath: "<slug>/paper/main.tex",
    lang: "zh",
    targetScore: 7.5,
    maxRounds: 4,
    dataContext: "<关键结果数值摘要>"
  }
})
```

---

## 目录结构

```
math-modeling/
├── SKILL.md                       # 主编排文件（完整的 7 阶段指令）
├── README.md                      # 本文件
│
├── references/                    # 阶段参考文档
│   ├── 01-problem-analysis.md     # 审题指南
│   ├── 02-framework.md            # 建模框架与方法选型（含 ML/DL 决策）
│   ├── 03-data-acquisition.md     # 数据获取策略
│   ├── 04-modeling-cookbook.md    # 建模配方（优化/微分方程/统计/ML/评价…）
│   ├── 05-visualization.md        # 可视化清单（基础图+高端图选型指南）
│   ├── 06-writing.md              # 写作规范（页面约束+四项深度要求）
│   ├── 07-adversarial-review.md   # 对抗审稿协议
│   ├── scoring-rubric.md          # 五维度评分细则
│   └── data-sources.md            # 数据源目录
│
├── templates/                     # LaTeX 模板
│   ├── cumcm-zh/main.tex          # 国赛中文（ctex + xelatex）
│   ├── mcm-en/main.tex            # 美赛英文（pdflatex）
│   └── figures.mplstyle           # matplotlib 统一风格
│
├── scripts/                       # Python 工具链
│   ├── new_project.py             # 建标准工作目录
│   ├── compile.py                 # 编译 LaTeX → PDF（自动选引擎、抓报错）
│   ├── plot_helpers.py            # 可视化函数库（16 种图表类型）
│   └── fetch_data.py              # 数据获取辅助
│
└── workflows/
    └── adversarial-review.js      # 多智能体对抗审稿工作流（≤4 轮）
```

---

## 可视化能力

### 基础必备图（6 种）

| 函数 | 用途 |
|---|---|
| `convergence_curve` | 优化/启发式算法收敛曲线 |
| `pareto_front` | 多目标 Pareto 前沿 |
| `heatmap` | 相关/距离/混淆矩阵热力图 |
| `sensitivity_tornado` | 参数灵敏度龙卷风图 |
| `timeseries_fit` | 时间序列拟合与预测对比 |
| `roc_curve_plot` | 分类模型 ROC 曲线 |

### 高端扩展图（10 种）

| 函数 | 用途 |
|---|---|
| `surface_3d` | 3D 曲面图（优化地形/参数景观） |
| `contour_filled` | 填充等高线图（双参数分析） |
| `radar_chart` | 雷达图（多方案多准则对比） |
| `violin_plot` | 小提琴图（多组分布对比） |
| `network_graph` | 网络拓扑图（图论/网络模型） |
| `dendrogram_plot` | 层次聚类树状图 |
| `waterfall_chart` | 瀑布图（因素分解/贡献拆解） |
| `pair_correlation` | 成对相关矩阵图（数据探索） |
| `scatter_3d` | 三维散点图（第四维颜色映射） |
| `ridge_plot` / `streamgraph` | 山脊图 / 流图（分布演化） |

所有图统一风格（`figures.mplstyle`），中文字体自适应，300dpi PNG 输出。

---

## 论文结构（模板内置）

1. **摘要**（单独一页，量化结论，评分命脉）
2. 问题重述
3. 问题分析
4. **模型假设与局限性讨论**（每条含依据 + 放宽后果量化 + 补救方案）
5. 符号说明
6. 模型的建立与求解（按问分小节）
7. **模型对比验证**（≥2 个基准/消融，≥3 个指标，含雷达图）
8. 灵敏度分析
9. **模型的评价与推广**（创新点显式声明 + 深度缺点分析）
10. 参考文献
11. 附录（核心代码）

---

## 设计原则

- **稳中求新**：先保基础分（模型合理、结果正确、排版规范），再加创新点
- **不造假**：数据、结果、引用真实；模拟数据必须显著标注
- **可复现**：代码固定随机种子、路径相对化，可放进附录复跑
- **量化摘要**：摘要必须有具体数字，这是评分命脉
- **排版即分数**：摘要/目录各一页、无大空白、无溢出
- **对比即说服力**：每个模型必须有对比基准，用数据证明选择
- **深度即区分度**：假设讨论到"放宽→误差X%→结论是否逆转"的粒度

---

## 本机环境（开发 & 验证）

- **OS**：Windows 11
- **LaTeX**：xelatex (MiKTeX) + ctex/xeCJK，中文字体 SimHei/SimSun
- **Python**：anaconda `python`（numpy, pandas, scipy, scikit-learn, matplotlib）
- **联网**：Claude Code 内置 WebSearch / WebFetch
- **额外依赖**（高端图选装）：`networkx`（网络图）、`scipy`（树状图/山脊图）

---

## 许可

MIT License

---

## 致谢

本系统受数学建模竞赛（CUMCM / MCM-ICM）多年参赛经验启发，将人工建模流程系统化为多智能体协作流水线。审稿协议借鉴学术同行评审机制，通过对抗协作提升论文质量。
