# 05 — 可视化清单

统一用 `<skill>/scripts/plot_helpers.py`，风格 `templates/figures.mplstyle`，输出 300dpi PNG 到 `figures/`。中文字体已设 SimHei。

> ⛔ **可视化是强制阶段（阶段 5），不允许跳过。** 一篇国赛级论文通常 **6–12 张**图；图太少是常见失分点。每个模型/每小问至少 1 张，且每张图必须在正文被 `\ref` 引用并解读。图未生成则阶段 5 未完成，不得进入写作。

---

## 必备图（基础）

| 方法 | 推荐图 | plot_helpers 函数 |
|---|---|---|
| 优化/启发式 | 收敛曲线 | `convergence_curve` |
| 多目标 | Pareto 前沿 | `pareto_front` |
| 相关/距离/混淆矩阵 | 热力图 | `heatmap` |
| 敏感性分析 | 龙卷风图 | `sensitivity_tornado` |
| 时间序列/微分方程 | 拟合预测对比 | `timeseries_fit` |
| 分类 | ROC | `roc_curve_plot` |

---

## 高端图（加分项）

这些图属于"锦上添花"，能让论文在可视化上明显优于平均水平。根据模型类型选用 1-3 张。

| 图类型 | 适用场景 | plot_helpers 函数 | 示例 |
|---|---|---|---|
| **3D 曲面图** | 优化目标函数地形、参数空间景观 | `surface_3d(X, Y, Z)` | 损失函数曲面、势能面 |
| **填充等高线图** | 二维优化等值域、约束可行域 | `contour_filled(X, Y, Z)` | 双参数优化的等高线 |
| **雷达图（蜘蛛图）** | 多方案/多准则对比（AHP、TOPSIS） | `radar_chart(cats, vals)` | 不同模型性能多维度对比 |
| **小提琴图** | 多组数据分布对比（优于箱线图） | `violin_plot(data)` | 不同算法多次运行结果分布 |
| **网络拓扑图** | 图论/网络模型可视化 | `network_graph(adj_matrix)` | 最短路径、交通网络、社交网络 |
| **层次聚类树状图** | 聚类结果可视化 | `dendrogram_plot(data)` | 样本分层聚类、指标体系聚类 |
| **瀑布图** | 因素拆解 / 贡献分解 | `waterfall_chart(cats, vals)` | 灵敏度因素分解、利润驱动 |
| **成对相关矩阵图** | 数据探索 / EDA | `pair_correlation(data)` | 特征间相关关系一览 |
| **三维散点图** | 高维数据可视化 | `scatter_3d(x, y, z)` | 三维数据分布、第四维颜色映射 |
| **山脊图** | 多组分布重叠对比 | `ridge_plot(data)` | 参数后验分布对比、时间序列分布演化 |
| **流图** | 成分随时间变化 | `streamgraph(data)` | 种群构成演变、市场份额变化 |

### 高端图选型指南

| 论文中出现的场景 | 推荐高端图 |
|---|---|
| 多方案综合评价（AHP/TOPSIS/熵权） | 雷达图 `radar_chart` |
| 优化问题有 2 个关键参数 | 3D 曲面 `surface_3d` + 等高线 `contour_filled` |
| 图论/网络（最短路/最大流/中心性） | 网络图 `network_graph` |
| 聚类分析（KMeans/层次/DBSCAN） | 树状图 `dendrogram_plot` + 3D 散点 `scatter_3d` |
| 灵敏度分析（多因素拆解） | 瀑布图 `waterfall_chart` + 龙卷风图 `sensitivity_tornado` |
| 随机模拟 / 多次重复实验 | 小提琴图 `violin_plot` 或山脊图 `ridge_plot` |
| 数据探索（特征工程前） | 成对相关矩阵 `pair_correlation` |
| 种群/传染病/市场演化 | 流图 `streamgraph` + 时序图 `timeseries_fit` |

---

## 通用规范（评分点）

- 每图有**标题、轴标签、单位、图例**；正文用 `\ref` 引用并解读，不能只放图不说话。
- 配色一致（mplstyle 已定）；避免花哨；黑白打印可辨。
- 数据来源图注明来源；仿真图注明重复次数与随机种子。
- 图不要太多也不要太少：每个模型 1-3 张关键图。
- **高端图要服务于论证**——不要为了炫技而加图。每张高端图必须在正文中解释它揭示了什么、为什么非它不可。

---

## 用法

```python
import sys; sys.path.insert(0, r"C:/Users/HUAWEI/.claude/skills/math-modeling/scripts")

# 基础图
from plot_helpers import convergence_curve, heatmap, sensitivity_tornado, pareto_front, timeseries_fit, roc_curve_plot

# 高端图（按需导入）
from plot_helpers import surface_3d, contour_filled, radar_chart, violin_plot
from plot_helpers import network_graph, dendrogram_plot, waterfall_chart
from plot_helpers import pair_correlation, scatter_3d, ridge_plot, streamgraph

# 使用示例
convergence_curve(hist, "figures/fig_convergence.png")
surface_3d(X, Y, Z, "figures/fig_surface3d.png", title="优化目标函数曲面")
radar_chart(["精度","速度","稳定性"], {"方案A":[4,3,5],"方案B":[3,5,4]},
            "figures/fig_radar.png", title="方案多维度对比")
```

LaTeX 引用：`\includegraphics[width=0.7\textwidth]{fig_convergence.png}`（模板已设 `graphicspath` 含 `figures/`）。
