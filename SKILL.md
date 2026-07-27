---
name: math-modeling
description: 端到端数学建模竞赛论文生成系统（国赛 CUMCM 中文 / 美赛 MCM 英文）。多智能体对抗协作：深度审题→建模框架与方法选型(含是否用ML/DL)→联网找数据(维基/GitHub/Kaggle/官方统计/sklearn)→编程求解与可视化→LaTeX写作→编译PDF→写作者/审稿人/验证者/推理者多轮对抗审稿(评分5.0→7.5)，产出国赛级别论文。当用户给出一道数学建模赛题、或说"数学建模""建模论文""国赛/美赛论文""/math-modeling"时使用。
---

# 数学建模多智能体系统

把一道赛题，经 7 个阶段、多智能体对抗协作，产出可编译为 PDF 的国赛级别论文。

## 环境（本机 Windows，已验证）
- 编译：`xelatex`(MiKTeX) + `ctex`/`xeCJK`，中文字体 SimHei/SimSun → 中文 PDF 可编。
- Python：anaconda `python`（numpy/pandas/scipy/sklearn/matplotlib 全就绪）。命令行显式用 `python`。
- 联网：内置 WebSearch / WebFetch。
- Skill 根目录：`C:/Users/HUAWEI/.claude/skills/math-modeling/`（下称 `<skill>`）。

## 何时用哪种执行方式
- **子智能体**（`Agent` 工具，agentType 见下）：单阶段专项工作。
- **对抗审稿**：用 `Workflow` 跑 `<skill>/workflows/adversarial-review.js`（真实多智能体并行对抗，≤4 轮）。
- 只有当用户明确要"多智能体/工作流/对抗"或说了触发词时才启动 Workflow（它会开多个子智能体，耗 token）。

---

## ⛔ 强制流程门禁（不允许跳步）

**这是硬性约束，优先级高于一切效率考量。必须严格按阶段 0→1→2→3→4→5→6→7 顺序执行，禁止跳过、合并、颠倒任何阶段。**

规则：
1. **每个阶段完成后，必须落盘产出**（写入 `REPORT.md` 对应小节或生成对应文件），产出不存在 = 该阶段未完成。
2. **进入下一阶段前，必须先确认上一阶段的产出已存在**（用 Read 检查 `REPORT.md` 相应小节 / `data/` / `code/` / `figures/` 有无对应内容）。缺失就回到该阶段补做，不得前进。
3. **禁止"心算跳过"**：不允许因为"这题简单""数据不用找""图随便画"而略过阶段 3（数据）、阶段 5（可视化）或阶段 7（审稿）。每个阶段都必须真实执行并留痕。
4. **阶段门禁清单**：开工时用 `TaskCreate` 建 8 个任务（阶段 0–7），每进入一个阶段 `TaskUpdate` 设为 in_progress，产出落盘并检查通过后才设 completed 并进入下一个。任何时刻只允许一个阶段是 in_progress。
5. **可视化是必经阶段**：阶段 5 必须为每个模型至少产出 1 张图到 `figures/`，且阶段 6 的论文里每张图都要被正文引用并解读。图未生成 = 阶段 5 未完成，不得进入写作。
6. **对抗审稿不可省**：阶段 7 是核心创新，除非用户明确说"不要审稿"，否则必须跑；跑完要把每轮评分写进 `REPORT.md` 第 6 节。

阶段依赖（后一阶段的输入 = 前一阶段的产出，缺则不可开始）：
```
0 目录  →  1 审题报告  →  2 建模方案表  →  3 data/*.csv+SOURCES  →
4 code/solve_qN.py+结果  →  5 figures/*.png  →  6 main.pdf  →  7 评分记录+终版PDF
```

## 可用子智能体（已装于 ~/.claude/agents）
| agentType | 角色 | 阶段 |
|---|---|---|
| mm-problem-analyst | 审题 | 1 |
| mm-modeler | 方法选型(含ML/DL决策) | 2 |
| mm-data-hunter | 联网找数据 | 3 |
| mm-coder | 编程求解+可视化 | 4-5 |
| mm-writer | 论文写作/修改 | 6,7 |
| mm-reviewer | 批判审稿 | 7 |
| mm-verifier | 交叉验证 | 7 |
| mm-reasoner | 数学推理/证明 | 7 |

---

## 执行流程（7 阶段）

### 阶段 0 — 建立工作目录
先问/推断赛制语言：国赛→`zh`，美赛→`en`。然后：
```bash
python <skill>/scripts/new_project.py "<赛题名>" --lang zh   # 或 en
```
把赛题原文粘进 `<slug>/problem.md`。之后所有产出落在该工作目录。
用 `TaskCreate` 建立阶段 0–7 共 8 个门禁任务。
> ✅ 门禁：工作目录+8 个任务已建、`problem.md` 已填 → 才可进入阶段 1。

### 阶段 1 — 深度审题
用 `Agent`（agentType=`mm-problem-analyst`）读 `problem.md`，产出结构化审题报告（逐问拆解、显隐约束、数据情况、评分点、陷阱）。写入 `REPORT.md` 第 1 节。
参考：`<skill>/references/01-problem-analysis.md`。
> ✅ 门禁：`REPORT.md` 第 1 节已写入审题报告 → 才可进入阶段 2。

### 阶段 2 — 建模框架与方法选型
用 `Agent`（`mm-modeler`）基于审题报告，为每问选方法、**判定是否用 ML/DL 并给理由**、列所需图表与验证方式，产出建模方案表。写入 `REPORT.md` 第 2 节。
参考：`02-framework.md`、`04-modeling-cookbook.md`、`05-visualization.md`。
> ✅ 门禁：`REPORT.md` 第 2 节含每问方案表（方法/是否ML/所需图表/验证）→ 才可进入阶段 3。

### 阶段 3 — 数据获取
用 `Agent`（`mm-data-hunter`，带 WebSearch/WebFetch）按方案找数据，用 `<skill>/scripts/fetch_data.py` 落盘到 `data/`，来源记入 `data/SOURCES.md`。
参考：`03-data-acquisition.md`、`data-sources.md`。
> ✅ 门禁：`data/` 有 CSV 且 `data/SOURCES.md` 记录来源（或明确标注"题目附件提供/需自采/已标注模拟"）→ 才可进入阶段 4。

### 阶段 4 — 建模求解 + 编程
用 `Agent`（`mm-coder`）用 anaconda `python` 实现模型、跑通、存结果。每问 `code/solve_qN.py`。
> ✅ 门禁：每问有 `code/solve_qN.py` 且已跑通、产出关键数值结果 → 才可进入阶段 5。

### 阶段 5 — 可视化（必经，不可略过）
仍由 `mm-coder`，用 `<skill>/scripts/plot_helpers.py`（统一风格 `templates/figures.mplstyle`，中文字体已设）出图到 `figures/`。

**硬性要求：**
- **每个模型 / 每一小问至少 1 张说明性图**；一篇国赛级论文通常 **6–12 张**图（含结果图+分析图），太少会明显失分。
- **每类方法配套必备图**（见下表，也见 `05-visualization.md`）：

| 方法类型 | 必备图 | plot_helpers 函数 |
|---|---|---|
| 优化/启发式 | 收敛曲线 | `convergence_curve` |
| 多目标 | Pareto 前沿 | `pareto_front` |
| 相关/混淆/距离矩阵 | 热力图 | `heatmap` |
| **灵敏度分析（几乎每题必做）** | 龙卷风图 | `sensitivity_tornado` |
| 时序/微分方程 | 拟合预测对比 | `timeseries_fit` |
| 分类 | ROC 曲线 | `roc_curve_plot` |

- **高端图加分**（按模型类型选 1-3 张，见 `05-visualization.md` 高端图选型指南）：

| 图类型 | 适用场景 | 函数 |
|---|---|---|
| 3D 曲面 / 填充等高线 | 优化目标地形、双参数分析 | `surface_3d` / `contour_filled` |
| 雷达图 | 多方案多准则对比 (AHP/TOPSIS) | `radar_chart` |
| 小提琴图 / 山脊图 | 多组分布对比、随机模拟 | `violin_plot` / `ridge_plot` |
| 网络拓扑图 | 图论/网络模型 | `network_graph` |
| 层次聚类树状图 | 聚类分析 | `dendrogram_plot` |
| 瀑布图 | 因素拆解 / 贡献分解 | `waterfall_chart` |
| 成对相关矩阵 | 特征探索 (EDA) | `pair_correlation` |
| 三维散点图 | 高维数据分布 | `scatter_3d` |
| 流图 | 成分随时间演化 | `streamgraph` |

- **每张图规范**：标题、坐标轴标签+单位、图例、来源/随机种子（仿真图）；300dpi PNG。
- **图要说话**：出图后写一句该图说明了什么，供阶段 6 写进正文（不能只放图不解读）。
- 落盘检查：`figures/` 下 PNG 数量 ≥ 模型数，否则本阶段未完成。

参考：`05-visualization.md`、`04-modeling-cookbook.md`（每方法"三件套"含灵敏度）。
> ✅ 门禁：`figures/*.png` 已生成且覆盖每个模型 → 才可进入阶段 6。

### 阶段 6 — LaTeX 写作 + 编译
用 `Agent`（`mm-writer`）把审题/模型/结果/图表填进 `paper/main.tex`（模板已按语言复制好），然后编译并检查页面约束。

**⛔ 页面硬约束（编译后必须逐项检查，不合格退回修改）：**
1. **摘要一页内**——溢出则压缩或 `\zihao{5}`；不足半页则补量化结论。
2. **目录一页内**——溢出改 `\setcounter{tocdepth}{1}`；模板已用 `tocloft` 紧凑化。
3. **无大空白**——模板已 `\raggedbottom` + 浮动间距紧凑；图用 `[htbp]` 非 `[H]`。
4. **无文字溢出**——`\tolerance=800`、大图 `width=\textwidth`、长公式换行。
5. **每节后 `\FloatBarrier`** 阻断浮动体漂移。

**⛔ 四项深度内容要求（高分分水岭，缺一不可）：**
1. **假设局限性深度讨论**：每条假设含依据+局限性+放宽后果的量化估计+补救方案。不可只写"假设系统稳态"。
2. **对比模型验证**：至少 1-2 个基准/消融模型，≥3 个指标对比，含对比表+雷达图，证明你的模型更优。
3. **创新点显式声明**：摘要和评价中写明创新（方法组合/改进/应用/视角），至少 1 条理论创新+1 条方法创新。
4. **多指标评估**：每模型报告精度+效率+稳健性三类指标；有冲突时用 Pareto 前沿讨论权衡。

```bash
# 编译
python <skill>/scripts/compile.py paper/main.tex        # 中文自动走 xelatex
```
编译失败时脚本会回读 .log 定位报错，修到出 PDF。
参考：`06-writing.md`。
> ✅ 门禁：`paper/main.pdf` 已成功编译、每张图被正文引用并解读、摘要含量化结果、**页面约束+四项深度要求全部满足** → 才可进入阶段 7。

### 阶段 7 — 多轮对抗审稿（核心创新）
用 `Workflow` 运行对抗审稿：
```
Workflow({ scriptPath: "<skill>/workflows/adversarial-review.js",
           args: { draftPath: "<slug>/paper/main.tex", lang: "zh",
                   targetScore: 7.5, maxRounds: 4,
                   dataContext: "<关键结果数值摘要>" } })
```
机制：写作者生成 → 审稿人/验证者/推理者**并行对抗打分**（0-10 五维度）→ 若 <7.5，写作者按弱点逐条修改（含**自动补充实验**）→ 复评，≤4 轮。返回最终评分、每轮记录、残留 high 弱点。
把评审记录写入 `REPORT.md` 第 6 节，最后再 `compile.py` 出终版 PDF（终版也须通过页面约束检查）。
参考：`07-adversarial-review.md`、`scoring-rubric.md`。

---

## 交付物
- `<slug>/paper/main.pdf` —— 终版论文
- `<slug>/paper/main.tex`、`code/`、`figures/`、`data/`、`REPORT.md`（全过程可追溯）

## 原则
- **稳中求新**：先保证基础分（模型合理、结果正确、排版规范），再加创新点。创新要显式声明（方法组合/改进/应用迁移/视角创新）。
- **不造假**：数据、结果、引用真实；模拟数据必须显著标注。
- **可复现**：代码固定随机种子、路径相对化，能放进附录复跑。
- **量化摘要**：摘要页必须有具体数字，这是评分命脉。
- **排版即分数**：摘要/目录各一页、无大空白、无溢出 → 基础排版分不丢。
- **对比即说服力**：每个模型必须有对比基准，用数据证明"为什么选这个模型"而非"我用了这个模型"。
- **深度即区分度**：假设讨论必须到"若放宽→误差X%→结论是否逆转"的深度；缺点必须到"哪个参数、缺什么数据、量级多大"的粒度。
