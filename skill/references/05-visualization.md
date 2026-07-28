# 05 — 可视化参考手册

统一用 `<skill>/scripts/plot_helpers.py`，风格 `templates/figures.mplstyle`，输出 300dpi PNG 到 `figures/`。中文字体已设 SimHei。

> **可视化是强制阶段（阶段 5），不允许跳过。** 一篇国赛级论文通常 **6-12 张**图；图太少是常见失分点。每个模型/每小问至少 1 张，且每张图必须在正文被 `\ref` 引用并解读。图未生成则阶段 5 未完成，不得进入写作。

---

## 一、选图决策树

### 1.1 快速决策表

| 你想展示什么 | 首选图表 | 备选 | 禁用 |
|---|---|---|---|
| **比较**（类别间数值对比） | 柱状图 `bar` | 水平条形图、点图 | 饼图（>5类别）、3D柱状图 |
| **趋势**（随时间/序列变化） | 折线图 `line` | 面积图、斜率图 | 柱状图（时间点多时） |
| **分布**（数据集中/离散/形状） | 箱线图 `box` / 小提琴图 `violin` | 直方图、山脊图 | 柱状图（连续数据） |
| **关系/相关**（两变量关联） | 散点图 `scatter` | 相关性矩阵、气泡图 | 折线图（除非有序） |
| **构成**（部分占整体比例） | 堆叠柱状图 | 瀑布图、树图 | 饼图（>5类） |
| **空间/地理**（位置相关） | 热力图 `heatmap` | 等高线图、气泡地图 | — |
| **网络/拓扑**（节点关系） | 网络图 `network` | 弦图、弧长图 | 散点图 |
| **层次/聚类**（分组结构） | 树状图 `dendrogram` | 旭日图、冰柱图 | — |
| **多变量对比**（高维数据概况） | 平行坐标图 `parallel_coords` | 雷达图、成对矩阵 | — |
| **流程/转移**（来源→去向） | 桑基图 `sankey` | 冲积图、弦图 | — |

### 1.2 决策流程图

```
要展示什么？
├── 比较数值大小
│   ├── 类别 ≤ 5 且独立 → 柱状图 (bar)
│   ├── 类别 > 5 且独立 → 水平条形图 (barh)
│   ├── 类别是时间序列 → 折线图 (line)
│   └── 多方案多维度 → 雷达图 (radar) / 平行坐标图 (parallel_coords)
├── 展示数据分布
│   ├── 组数 ≤ 3 → 直方图 (hist) + KDE
│   ├── 组数 3-10 → 箱线图 (box) + 小提琴图 (violin)
│   ├── 组数 > 10 → 山脊图 (ridge)
│   └── 强调离群值 → 箱线图 (box)
├── 展示变量关系
│   ├── 2 个连续变量 → 散点图 (scatter) + 回归线
│   ├── 3+ 个连续变量 → 成对相关矩阵 (pair_correlation)
│   ├── 矩阵/表格数据 → 热力图 (heatmap)
│   └── 空间连续场 → 等高线图 (contour) / 3D 曲面 (surface_3d)
├── 展示构成/占比
│   ├── ≤ 3 类 + 时间变化 → 堆叠面积图 (stackplot)
│   ├── 因素分解 → 瀑布图 (waterfall)
│   ├── ≤ 5 类静态 → 饼图 (pie，谨慎使用)
│   └── 多类别层级 → 树图 (treemap)
├── 展示网络/关系
│   ├── 节点 + 边 → 网络图 (network_graph)
│   ├── 流量/转移 → 桑基图 (sankey)
│   └── 层次聚类 → 树状图 (dendrogram)
└── 展示多维数据全貌
    ├── 6-20 维连续 → 平行坐标图 (parallel_coords)
    └── 3-8 维离散+连续 → 雷达图 (radar)
```

### 1.3 常见建模场景 → 图类型速查

| 论文场景 | 必备图 | 加分图 |
|---|---|---|
| 优化/启发式 | 收敛曲线 `convergence_curve` | 3D 曲面 + 等高线 |
| 多目标优化 | Pareto 前沿 `pareto_front` | 平行坐标图 |
| 评价决策(AHP/TOPSIS) | 权重柱状图 + 得分排序 | 雷达图 `radar_chart` |
| 微分方程(SIR等) | 拟合预测对比 `timeseries_fit` | 相图(phase portrait) |
| 回归/预测 | 拟合 vs 实际散点图 | 残差图 + QQ 图 |
| 分类/判别 | ROC 曲线 `roc_curve_plot` | 混淆矩阵热力图 |
| 聚类 | 散点图（标颜色） | 树状图 + 轮廓系数图 |
| 图论/网络 | 网络图 `network_graph` | 度分布直方图 |
| 灵敏度分析 | 龙卷风图 `sensitivity_tornado` | 瀑布图 + 热力图 |
| 数据探索(EDA) | 成对相关矩阵 `pair_correlation` | 小提琴图多组对比 |

---

## 二、16 种图表类型详解

### 2.1 折线图 (Line Plot)

- **适用场景**：展示趋势、时间序列、迭代收敛、函数曲线
- **最佳实践**：线宽 1.5–2.5，标记点每 5-10 个数据点显示一个，多线时颜色区分度足够

```python
import matplotlib.pyplot as plt
import numpy as np

# ===== 折线图代码骨架 =====
fig, ax = plt.subplots(figsize=(8, 5))
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

ax.plot(x, y1, 'o-', color='#2C7BB6', linewidth=2, markersize=4,
        markevery=5, label='Method A')
ax.plot(x, y2, 's-', color='#D7191C', linewidth=2, markersize=4,
        markevery=5, label='Method B')

ax.set_xlabel('Time $t$ (s)', fontsize=12)
ax.set_ylabel('Value', fontsize=12)
ax.set_title('Comparison of Method A and Method B', fontsize=14)
ax.legend(loc='best', framealpha=0.8)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('figures/fig_line_demo.png', dpi=300)
plt.close()
```

- **常见错误**：
  - 用折线图表示无序类别数据（应用柱状图）
  - 线条过多（>6条）导致无法区分（应用分面子图或只标关键曲线）
  - 标记点过密导致视觉噪音

### 2.2 柱状图 (Bar Chart)

- **适用场景**：类别间数值对比、排名、权重展示
- **最佳实践**：**基线必须从 0 开始**，柱子宽度 0.6–0.8，间距一致

```python
# ===== 柱状图代码骨架 =====
fig, ax = plt.subplots(figsize=(8, 5))
categories = ['A', 'B', 'C', 'D', 'E']
values = [23, 45, 56, 78, 32]
colors = ['#2C7BB6', '#D7191C', '#FDAE61', '#ABD9E9', '#5E3C99']

bars = ax.bar(categories, values, width=0.65, color=colors, edgecolor='white', linewidth=0.8)

# 数值标注
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            str(val), ha='center', va='bottom', fontsize=10)

ax.set_xlabel('Category', fontsize=12)
ax.set_ylabel('Value', fontsize=12)
ax.set_title('Comparison Across Categories', fontsize=14)
ax.set_ylim(0, max(values) * 1.15)  # ⛔ 基线必须为0
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('figures/fig_bar_demo.png', dpi=300)
plt.close()
```

- **常见错误**：
  - **基线不从 0 开始**（最常见的致命错误——视觉比例严重失真）
  - 柱子过多（>15 个）致标签重叠（改用水平条形图 `barh`）
  - 使用 3D 柱状图（柱高被透视扭曲，无法准确读取数值）

### 2.3 散点图 (Scatter Plot)

- **适用场景**：两连续变量关系、聚类可视化、拟合 vs 实际对比
- **最佳实践**：点大小合适（s=20-80），透明度（alpha=0.5-0.7）处理重叠，可加回归线

```python
# ===== 散点图代码骨架 =====
fig, ax = plt.subplots(figsize=(7, 7))
x = np.random.randn(200) * 2 + 5
y = 0.7 * x + np.random.randn(200) * 1.5

# 散点
scatter = ax.scatter(x, y, c='#2C7BB6', s=40, alpha=0.6,
                     edgecolors='white', linewidth=0.5, label='Samples')

# 拟合线
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
x_line = np.linspace(x.min(), x.max(), 100)
ax.plot(x_line, p(x_line), '--', color='#D7191C', linewidth=2, label='Fit: y=%.2fx+%.2f' % (z[0], z[1]))

ax.set_xlabel('Variable X', fontsize=12)
ax.set_ylabel('Variable Y', fontsize=12)
ax.set_title('Scatter Plot with Linear Fit', fontsize=14)
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)
ax.set_aspect('equal')  # 相关性分析时建议等比例
plt.tight_layout()
plt.savefig('figures/fig_scatter_demo.png', dpi=300)
plt.close()
```

- **常见错误**：
  - 数据点过多不设透明度，变成一块黑色
  - 坐标轴比例不同造成相关性视觉误判
  - 类别变量用散点图（应用箱线图/小提琴图）
  - 忘记标注拟合线的方程和 R² 值

### 2.4 热力图 (Heatmap)

- **适用场景**：矩阵可视化（相关矩阵/混淆矩阵/距离矩阵）、二维参数扫描结果、时空数据
- **最佳实践**：用 diverging colormap（有正负时）或 sequential（全正时），标注关键数值

```python
# ===== 热力图代码骨架 =====
fig, ax = plt.subplots(figsize=(9, 8))
matrix = np.random.randn(10, 10)
np.fill_diagonal(matrix, 1.0)
matrix = (matrix + matrix.T) / 2  # 对称化

im = ax.imshow(matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='equal')

# 数值标注（小矩阵时使用）
for i in range(matrix.shape[0]):
    for j in range(matrix.shape[1]):
        text = ax.text(j, i, f'{matrix[i, j]:.2f}',
                       ha='center', va='center', fontsize=7,
                       color='white' if abs(matrix[i, j]) > 0.6 else 'black')

ax.set_xticks(range(10))
ax.set_yticks(range(10))
ax.set_xticklabels([f'Var{i+1}' for i in range(10)], rotation=45, ha='right')
ax.set_yticklabels([f'Var{i+1}' for i in range(10)])
cbar = plt.colorbar(im, ax=ax, shrink=0.8)
cbar.set_label('Correlation Coefficient', fontsize=11)
ax.set_title('Correlation Matrix Heatmap', fontsize=14)
plt.tight_layout()
plt.savefig('figures/fig_heatmap_demo.png', dpi=300)
plt.close()
```

- **常见错误**：
  - 不设置 `vmin/vmax` 对称范围，颜色映射不对称
  - 颜色映射选择不当（如用 jet 映射有正负的数据）
  - 单元格过小（>20×20）仍标注数值，完全不可读
  - 未标注 colorbar 的含义

### 2.5 等高线图 (Contour Plot)

- **适用场景**：二维目标函数地形、可行域边界、参数空间可视化、势能场
- **最佳实践**：填充（`contourf`）+ 线标注（`contour`）双叠加，标注关键等值线数值

```python
# ===== 等高线图代码骨架 =====
fig, ax = plt.subplots(figsize=(8, 6))
x = np.linspace(-3, 3, 200)
y = np.linspace(-3, 3, 200)
X, Y = np.meshgrid(x, y)
Z = (1 - X/2 + X**5 + Y**3) * np.exp(-X**2 - Y**2)  # 示例函数

# 填充等高线
cf = ax.contourf(X, Y, Z, levels=15, cmap='viridis', alpha=0.8)
# 线标注
ct = ax.contour(X, Y, Z, levels=8, colors='black', linewidths=0.6)
ax.clabel(ct, inline=True, fontsize=8, fmt='%.1f')

cbar = plt.colorbar(cf, ax=ax, shrink=0.85)
cbar.set_label('Objective Value $f(x_1, x_2)$', fontsize=11)
ax.set_xlabel('Parameter $x_1$', fontsize=12)
ax.set_ylabel('Parameter $x_2$', fontsize=12)
ax.set_title('Contour Map of Objective Function', fontsize=14)
plt.tight_layout()
plt.savefig('figures/fig_contour_demo.png', dpi=300)
plt.close()
```

- **常见错误**：
  - 分辨率不足，等值线呈锯齿状（`np.linspace` 点数应 ≥150）
  - colorbar 不标单位/物理意义
  - 等值线标注数字重叠（调整 levels 数量或标注位置）

### 2.6 雷达图 (Radar / Spider Chart)

- **适用场景**：多方案多准则对比（AHP/TOPSIS 结果展示）、多维度性能评估
- **最佳实践**：维度 3–8 个，同一图 2–5 条线，填充用半透明；超过 8 维换平行坐标图

```python
# ===== 雷达图代码骨架 =====
import numpy as np
import matplotlib.pyplot as plt

def radar_chart(categories, values_dict, savepath, title='Radar Chart'):
    """
    categories: list[str]  维度标签
    values_dict: dict[str, list[float]]  方案名 → 各维度值（0-5或0-10量表）
    """
    N = len(categories)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angles += angles[:1]  # 闭合

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw={'projection': 'polar'})
    colors = ['#2C7BB6', '#D7191C', '#FDAE61', '#ABD9E9', '#5E3C99']

    for idx, (label, vals) in enumerate(values_dict.items()):
        vals_closed = list(vals) + [vals[0]]
        color = colors[idx % len(colors)]
        ax.fill(angles, vals_closed, alpha=0.1, color=color)
        ax.plot(angles, vals_closed, 'o-', linewidth=2, color=color, label=label, markersize=4)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_title(title, fontsize=14, pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.set_ylim(0, max(max(v) for v in values_dict.values()) * 1.15)
    plt.tight_layout()
    plt.savefig(savepath, dpi=300)
    plt.close()

# 使用示例
radar_chart(
    ['Accuracy', 'Speed', 'Robustness', 'Interpretability', 'Scalability'],
    {'Model A': [4.2, 3.8, 4.5, 3.0, 4.0],
     'Model B': [3.5, 4.8, 3.2, 4.5, 3.5],
     'Model C': [4.0, 3.5, 4.0, 3.8, 4.8]},
    'figures/fig_radar_demo.png', title='Multi-Dimensional Model Comparison'
)
```

- **常见错误**：
  - 维度过多（>8），图形变得难以阅读
  - 各维度量纲不同却不做标准化
  - 径向轴不从 0 开始，视觉夸大差异

### 2.7 小提琴图 (Violin Plot)

- **适用场景**：多组数据分布形态对比（优于箱线图），展示多峰/偏态，蒙特卡洛结果
- **最佳实践**：与箱线图叠加使用时效果最佳，样本量 ≥30 时使用

```python
# ===== 小提琴图代码骨架 =====
fig, ax = plt.subplots(figsize=(10, 6))
data = [np.random.normal(loc, 0.8, 200) for loc in [0, 1, 2.5, 3.5, 5]]
positions = range(1, len(data)+1)

parts = ax.violinplot(data, positions=positions, showmeans=True,
                       showmedians=True, widths=0.7)

# 配色
for pc, color in zip(parts['bodies'], ['#2C7BB6','#D7191C','#FDAE61','#ABD9E9','#5E3C99']):
    pc.set_facecolor(color)
    pc.set_alpha(0.7)
    pc.set_edgecolor('black')

# 叠加箱线图（可选）
bp = ax.boxplot(data, positions=positions, widths=0.15,
                patch_artist=True, showfliers=True,
                boxprops=dict(facecolor='white', alpha=0.8),
                medianprops=dict(color='black', linewidth=1.5))

ax.set_xticks(positions)
ax.set_xticklabels([f'Group {i}' for i in range(1, 6)], fontsize=11)
ax.set_ylabel('Value', fontsize=12)
ax.set_title('Distribution Comparison via Violin Plots', fontsize=14)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('figures/fig_violin_demo.png', dpi=300)
plt.close()
```

- **常见错误**：
  - 样本量太少（<15），小提琴形状无统计意义
  - 组间量纲差异大但用同一 y 轴（导致某些组被压扁）
  - 仅用小提琴图不叠加中位数/均值信息

### 2.8 箱线图 (Box Plot)

- **适用场景**：多组数据的中位数、四分位数、离群值对比；快速分布诊断
- **最佳实践**：显示离群值点（`showfliers=True`），样本量标注在 x 轴标签上

```python
# ===== 箱线图代码骨架 =====
fig, ax = plt.subplots(figsize=(10, 6))
data = [np.random.exponential(scale=s, size=100) for s in [1, 1.5, 2, 2.5, 3]]
positions = list(range(1, len(data)+1))

bp = ax.boxplot(data, positions=positions, widths=0.5, patch_artist=True,
                showfliers=True, showmeans=True,
                meanprops=dict(marker='D', markerfacecolor='red', markersize=6),
                flierprops=dict(marker='o', markerfacecolor='gray',
                                markersize=4, alpha=0.5),
                medianprops=dict(color='black', linewidth=2))

colors = ['#2C7BB6', '#D7191C', '#FDAE61', '#ABD9E9', '#5E3C99']
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.6)

# 标注样本量
n_labels = [f'Group {i}\n(n={len(d)})' for i, d in enumerate(data, 1)]
ax.set_xticks(positions)
ax.set_xticklabels(n_labels, fontsize=10)
ax.set_ylabel('Value', fontsize=12)
ax.set_title('Box Plot: Distribution Comparison', fontsize=14)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('figures/fig_boxplot_demo.png', dpi=300)
plt.close()
```

- **常见错误**：
  - 不显示离群值（需检查并说明剔除原因）
  - 组数过多（>10），图变窄阅读困难
  - 类别变量 vs 连续变量关系用了箱线图却未配对展示

### 2.9 网络图 (Network Graph)

- **适用场景**：图论模型（最短路径/最大流/最小生成树）、社交网络、交通网络、传染病传播
- **最佳实践**：节点大小反映中心性，边的粗细反映权重，使用力导向布局

```python
# ===== 网络图代码骨架 =====
import networkx as nx

def plot_network(adj_matrix, labels=None, title='Network Graph', savepath='figures/fig_network.png'):
    G = nx.from_numpy_array(adj_matrix)

    # 计算节点重要性（度中心性）
    centrality = nx.degree_centrality(G)
    node_size = [v * 800 + 100 for v in centrality.values()]

    fig, ax = plt.subplots(figsize=(10, 8))
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    nx.draw_networkx_edges(G, pos, alpha=0.3, edge_color='gray', width=1.0, ax=ax)
    nx.draw_networkx_nodes(G, pos, node_size=node_size,
                           node_color=list(centrality.values()),
                           cmap='YlOrRd', alpha=0.85, ax=ax)

    if labels is None:
        labels = {i: str(i) for i in range(len(adj_matrix))}
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_color='black', ax=ax)

    ax.set_title(title, fontsize=14)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(savepath, dpi=300)
    plt.close()

# 使用示例
adj = np.random.randint(0, 2, (12, 12))
adj = np.triu(adj, 1)
adj = adj + adj.T
plot_network(adj, title='Random Network Topology', savepath='figures/fig_network_demo.png')
```

- **常见错误**：
  - 节点过多（>50），图文完全糊在一起
  - 边权重差异很大但没有映射到线条宽度
  - 布局种子不固定，每次运行图不同（务必设 `seed=42`）

### 2.10 桑基图 (Sankey Diagram)

- **适用场景**：流量转移、能量流动、资金分配、人口迁移、决策树流向
- **最佳实践**：节点 ≤ 20 个，流量用宽度编码，颜色映射来源→目标

```python
# ===== 桑基图代码骨架 (matplotlib.sankey) =====
from matplotlib.sankey import Sankey

fig, ax = plt.subplots(figsize=(10, 6))
sankey = Sankey(ax=ax, scale=0.01, offset=0.3, head_angle=120,
                format='%.1f', unit=' units')

# 第一个节点
sankey.add(flows=[100, -40, -60],
           labels=['Total', 'Path A', 'Path B'],
           orientations=[0, 0, 1],
           pathlengths=[0.5, 0.5, 0.5],
           facecolor='#2C7BB6', alpha=0.6)

# 连接到第二个节点
sankey.add(flows=[40, -15, -25],
           labels=['', 'A1', 'A2'],
           orientations=[0, 0, 1],
           pathlengths=[0.3, 0.3, 0.3],
           facecolor='#D7191C', alpha=0.6,
           connect=(1, 0))  # 连接到上一个输出的第1个流

diagrams = sankey.finish()
ax.set_title('Sankey Flow Diagram', fontsize=14)
ax.axis('off')
plt.tight_layout()
plt.savefig('figures/fig_sankey_demo.png', dpi=300)
plt.close()
```

- **常见错误**：
  - 流量数值不守恒（流入总和必须等于流出总和）
  - 节点过多/流量过细导致不可读
  - `connect` 参数索引不对应

### 2.11 瀑布图 (Waterfall Chart)

- **适用场景**：因素拆解/贡献分解、盈亏分析、灵敏度因素逐项分解、累积效应展示
- **最佳实践**：增量用颜色编码（正向绿色/负向红色），总计列突出

```python
# ===== 瀑布图代码骨架 =====
def waterfall_chart(labels, values, title='Waterfall Chart', savepath='figures/fig_waterfall.png'):
    """
    labels: list[str]  各因素名称（最后一个视为"总计"）
    values: list[float]  各因素贡献值（增量），最后一个为最终值
    """
    n = len(labels)
    bottoms = [0] * n
    running_total = 0
    for i in range(n - 1):
        bottoms[i] = running_total
        running_total += values[i]
    bottoms[-1] = 0

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = []
    for i in range(n - 1):
        colors.append('#2CA02C' if values[i] >= 0 else '#D7191C')  # 绿增红减
    colors.append('#2C7BB6')  # 总计蓝色

    bars = ax.bar(range(n), [abs(v) for v in values[:-1]] + [running_total],
                  bottom=bottoms, color=colors, width=0.6, edgecolor='white')

    # 标注
    for i, (bar, val, label) in enumerate(zip(bars, values, labels)):
        y_pos = bar.get_height() + bar.get_y()
        ax.text(bar.get_x() + bar.get_width()/2, y_pos + max(values)*0.02,
                f'{val:+.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        ax.text(bar.get_x() + bar.get_width()/2, -max(values)*0.04,
                label, ha='center', va='top', fontsize=9, rotation=30)

    ax.axhline(y=0, color='black', linewidth=0.8)
    ax.set_title(title, fontsize=14)
    ax.set_ylabel('Cumulative Value', fontsize=12)
    ax.set_xticks([])
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(savepath, dpi=300)
    plt.close()

# 使用示例
waterfall_chart(
    ['Revenue', 'Cost A', 'Cost B', 'Tax', 'Net\nProfit'],
    [100, -30, -25, -10, 35],
    title='Profit Decomposition',
    savepath='figures/fig_waterfall_demo.png'
)
```

- **常见错误**：
  - 不设基准线（y=0 的水平线）
  - 区分增/减的颜色不当（红-绿对色盲不友好，应该同时用形状区分）
  - 最后一个总计条的 bottom 不归零

### 2.12 山脊图 (Ridge Plot)

- **适用场景**：多组分布沿某维度（时间/参数）的重叠对比
- **最佳实践**：组数 5–30，半透明填充，x 轴对齐以便比较

```python
# ===== 山脊图代码骨架 (需要 joypy) =====
# pip install joypy 或使用手动实现

import numpy as np
import matplotlib.pyplot as plt

def ridge_plot_manual(data_dict, title='Ridge Plot', savepath='figures/fig_ridge.png'):
    """
    data_dict: OrderedDict  label → array (sorted by the dimension you want to show)
    """
    n_groups = len(data_dict)
    labels = list(data_dict.keys())
    colors = plt.cm.viridis(np.linspace(0.15, 0.85, n_groups))

    fig, axes = plt.subplots(n_groups, 1, figsize=(10, 1.5 * n_groups),
                              sharex=True)

    for i, (label, data) in enumerate(data_dict.items()):
        ax = axes[i] if n_groups > 1 else axes
        ax.fill_between(np.sort(data),
                        np.zeros_like(data),
                        alpha=0.6, color=colors[i])
        # KDE 叠加
        from scipy.stats import gaussian_kde
        kde = gaussian_kde(data)
        x_kde = np.linspace(data.min(), data.max(), 200)
        ax.plot(x_kde, kde(x_kde), color='black', linewidth=0.8)
        ax.set_ylabel(label, fontsize=9, rotation=0, labelpad=30, ha='right', va='center')
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)

    axes[-1].set_xlabel('Value', fontsize=12)
    axes[0].set_title(title, fontsize=14)
    plt.tight_layout()
    plt.savefig(savepath, dpi=300)
    plt.close()

# 使用示例
from collections import OrderedDict
np.random.seed(42)
ridge_data = OrderedDict()
for t in range(2010, 2020):
    ridge_data[str(t)] = np.random.normal(loc=5 + (t-2010)*0.3, scale=1.0, size=500)
ridge_plot_manual(ridge_data, title='Distribution Evolution 2010-2019',
                  savepath='figures/fig_ridge_demo.png')
```

- **常见错误**：
  - 组间 y 偏移不够，曲线重叠无法辨认
  - x 轴范围不统一导致无法跨组比较
  - 样本量差异大但未标注

### 2.13 流图 (Streamgraph)

- **适用场景**：构成成分随时间演变（市场份额、种群比例、能源结构）
- **最佳实践**：配色柔和以显示趋势而非精确值，类别 3-10 个

```python
# ===== 流图代码骨架 =====
def streamgraph(labels, t, y_matrix, title='Streamgraph', savepath='figures/fig_stream.png'):
    """
    labels: list[str]  各成分名称
    t: np.array  时间轴 (N,)
    y_matrix: np.array  各成分值 (M, N)，M 个成分 × N 个时间点
    """
    fig, ax = plt.subplots(figsize=(12, 5))
    colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))

    # 中心化：使流图围绕 0 对称
    y_centered = y_matrix - y_matrix.sum(axis=0) / 2

    ax.stackplot(t, y_centered, labels=labels, colors=colors, alpha=0.8,
                 edgecolor='white', linewidth=0.3)

    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Proportion Shifted', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0), framealpha=0.9,
              fontsize=9)
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(savepath, dpi=300)
    plt.close()

# 使用示例
t = np.arange(2000, 2021)
np.random.seed(42)
y = np.abs(np.random.randn(5, 21).cumsum(axis=1))
streamgraph(['A', 'B', 'C', 'D', 'E'], t, y,
            title='Composition Evolution 2000-2020',
            savepath='figures/fig_stream_demo.png')
```

- **常见错误**：
  - 类别过多（>10），颜色难以区分
  - y 轴不标注"已中心化"，读者困惑为何有负值
  - 堆叠面积图与比例面积图混淆

### 2.14 3D 曲面图 (3D Surface Plot)

- **适用场景**：优化目标函数地形、损失函数曲面、双参数扫描、参数空间景观
- **最佳实践**：视角选择使得曲面特征可见，颜色映射用 sequential，打光适度

```python
# ===== 3D 曲面图代码骨架 =====
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

x = np.linspace(-5, 5, 100)
y = np.linspace(-5, 5, 100)
X, Y = np.meshgrid(x, y)
Z = X**2 + Y**2 + 3 * np.sin(X) * np.cos(Y)  # 示例函数

surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.85,
                        linewidth=0, antialiased=True,
                        rstride=1, cstride=1)

# 优化：查找并标注最小值点
min_idx = np.unravel_index(np.argmin(Z), Z.shape)
ax.scatter(X[min_idx], Y[min_idx], Z[min_idx],
           color='red', s=80, marker='*', label='Minimum')

ax.set_xlabel('$x_1$', fontsize=12, labelpad=10)
ax.set_ylabel('$x_2$', fontsize=12, labelpad=10)
ax.set_zlabel('$f(x_1, x_2)$', fontsize=12, labelpad=10)
ax.set_title('3D Surface of Objective Function', fontsize=14)
ax.view_init(elev=25, azim=-60)  # 视角：仰角25°，方位角-60°
fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label='Objective Value')
plt.tight_layout()
plt.savefig('figures/fig_surface3d_demo.png', dpi=300)
plt.close()
```

- **常见错误**：
  - 网格分辨率不足（`np.linspace` 点数 < 50），曲面呈块状
  - 视角遮挡关键特征（多尝试几个 `elev`/`azim`）
  - 不用 `antialiased=True`，线条锯齿严重
  - colorbar 不标物理意义

### 2.15 相关性矩阵 (Correlation Matrix / Pair Plot)

- **适用场景**：特征工程前的 EDA、多重共线性诊断、变量关系一览
- **最佳实践**：按变量分组排序，用 diverging colormap，标注显著性

```python
# ===== 成对相关矩阵代码骨架 =====
import pandas as pd
import seaborn as sns

def pair_correlation_plot(df, title='Correlation Matrix', savepath='figures/fig_corr_matrix.png'):
    """
    df: pandas DataFrame  数值型列
    """
    corr = df.corr()

    fig, ax = plt.subplots(figsize=(max(8, len(df.columns)*0.8),
                                     max(7, len(df.columns)*0.7)))

    # 只显示下三角
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)

    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f',
                cmap='RdBu_r', vmin=-1, vmax=1, center=0,
                square=True, linewidths=0.5, cbar_kws={'shrink': 0.8},
                ax=ax, annot_kws={'fontsize': 7})

    ax.set_title(title, fontsize=14, pad=15)
    plt.tight_layout()
    plt.savefig(savepath, dpi=300)
    plt.close()

# 使用示例
df = pd.DataFrame(np.random.randn(200, 8), columns=[f'Feature_{i}' for i in range(8)])
pair_correlation_plot(df, title='Feature Correlation Matrix',
                      savepath='figures/fig_corr_matrix_demo.png')
```

- **常见错误**：
  - 变量过多（>20），图无法阅读（应分块或选前 n 个）
  - 不用 mask 显示上下三角，信息冗余
  - 相关系数不标注
  - 不对变量做聚类排序，模式不明显

### 2.16 平行坐标图 (Parallel Coordinates)

- **适用场景**：高维数据（6-20 维）的多方案/多样本全貌对比，Pareto 解集展示
- **最佳实践**：每条线代表一个样本/方案，不同类别用不同颜色，做归一化

```python
# ===== 平行坐标图代码骨架 =====
from pandas.plotting import parallel_coordinates
import pandas as pd

def parallel_coords_plot(df, class_col, title='Parallel Coordinates',
                         savepath='figures/fig_parallel.png'):
    """
    df: DataFrame  包含数值列 + 一个分类列
    class_col: str  分类列名（用于着色）
    """
    # 归一化到 [0,1]
    numeric_cols = [c for c in df.columns if c != class_col]
    df_norm = df.copy()
    for col in numeric_cols:
        col_min, col_max = df[col].min(), df[col].max()
        df_norm[col] = (df[col] - col_min) / (col_max - col_min + 1e-10)

    fig, ax = plt.subplots(figsize=(12, 5))
    parallel_coordinates(df_norm, class_col, ax=ax,
                         colormap='Set2', alpha=0.5, linewidth=1.2)

    ax.set_title(title + '\n(Normalized)', fontsize=14)
    ax.set_xlabel('Dimension', fontsize=12)
    ax.set_ylabel('Normalized Value', fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1.0), fontsize=9)
    plt.tight_layout()
    plt.savefig(savepath, dpi=300)
    plt.close()

# 使用示例
df_pc = pd.DataFrame(np.random.randn(50, 6), columns=[f'Dim_{i}' for i in range(6)])
df_pc['Class'] = np.random.choice(['A', 'B', 'C'], 50)
parallel_coords_plot(df_pc, 'Class', title='Multi-Dimensional Solution Comparison',
                     savepath='figures/fig_parallel_demo.png')
```

- **常见错误**：
  - 不做归一化，各维度量纲不同导致图形被主导
  - 样本过多（>200），线条完全重叠
  - x 轴顺序任意，不打乱为有意义顺序

---

## 三、色觉友好配色方案

### 3.1 五大配色方案（Hex 值，可直接复制）

#### 方案 1：Default Blue-Orange（默认通用方案）
```
#2C7BB6  #D7191C  #FDAE61  #ABD9E9  #5E3C99  #2CA02C
```
适用：柱状图、折线图多线对比、散点多类

#### 方案 2：Colorblind-Safe / Viridis（色盲安全方案）
```
#440154  #414487  #2A788E  #22A884  #7AD151  #FDE725
```
适用：热力图、等高线图、3D 曲面、连续变量映射
**Viridis 是 matplotlib 默认 colormap，对色盲友好且在灰度打印下可辨。**

#### 方案 3：CUMCM Formal Grayscale-Compatible（国赛正式 / 灰度兼容）
```
#000000  #666666  #AAAAAA  #444444  #888888  #222222
```
或用高对比度线型组合：
```
#1A1A1A  #4D4D4D  #808080  #B3B3B3  #333333  #999999
```
适用：柱状图（黑白打印论文）、需保证灰度下可区分的图

#### 方案 4：Dark Theme（深色背景，用于 PPT/海报）
```
#E69F00  #56B4E9  #009E73  #F0E442  #0072B2  #D55E00  #CC79A7
```
适用：演示文稿、海报展示；论文正文禁止使用深色背景

#### 方案 5：Sequential + Diverging（序列型 + 发散型）
**Sequential（单向渐变，用于正值数据）**:
```
#F7FBFF  #DEEBF7  #C6DBEF  #9ECAE1  #6BAED6  #4292C6  #2171B5  #08519C
```
**Diverging（双向发散，用于有正负的数据，如相关系数、变化率）**:
```
#053061  #2166AC  #4393C3  #92C5DE  #D1E5F0  #F7F7F7  #FDDBC7  #F4A582  #D6604D  #B2182B  #67001F
```
适用：热力图、等高线、相关性矩阵

### 3.2 配色 → 图表类型对应表

| 图表类型 | 推荐配色方案 | 原因 |
|---|---|---|
| 柱状图（≤5 类） | 方案 1 (Blue-Orange) | 高饱和度，区分度高 |
| 柱状图（灰度打印） | 方案 3 (Grayscale) | 黑白打印可辨 |
| 折线图多线 | 方案 1 或方案 4 | 需要 4-6 种区分色 |
| 散点图多类 | 方案 2 (Viridis) | 连续渐变体现密度 |
| 热力图 / 相关矩阵 | 方案 5 发散 (RdBu_r) | 正负值以红蓝区分 |
| 3D 曲面 | 方案 2 (Viridis) 或方案 5 序列 | 地形高低用明暗 |
| 等高线图 | 方案 2 (Viridis) | 等值层次清晰 |
| 雷达图 | 方案 1 (半透明) | 填充区需透明 |
| 小提琴图 / 箱线图 | 方案 1 或方案 4 | 组间颜色区分 |
| 网络图 | 节点按中心性用方案 5 序列 | 中心性映射颜色 |
| 桑基图 | 方案 1 或方案 4 | 流量路径区分 |
| 注：论文正文**禁止使用深色背景图**（方案 4 仅用于演示） | | |

### 3.3 matplotlib 全局配色设置代码

```python
import matplotlib.pyplot as plt
import matplotlib as mpl

# ===== 设置全局默认配色 =====
# 方案 1: Blue-Orange
BLUE_ORANGE = ['#2C7BB6', '#D7191C', '#FDAE61', '#ABD9E9', '#5E3C99', '#2CA02C']
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=BLUE_ORANGE)

# 方案 2: 设置 viridis 为默认 colormap
mpl.rcParams['image.cmap'] = 'viridis'

# 中文字体设置（Windows: SimHei / macOS: Heiti SC / Linux: WenQuanYi Micro Hei）
mpl.rcParams['font.sans-serif'] = ['SimHei', 'Heiti SC', 'WenQuanYi Micro Hei', 'DejaVu Sans']
mpl.rcParams['axes.unicode_minus'] = False  # 解决负号显示为方块的问题
```

---

## 四、图表规范（数学建模竞赛标准）

### 4.1 分辨率与尺寸

| 参数 | 标准 | 说明 |
|---|---|---|
| 分辨率 (DPI) | **≥300** | 出版级最低要求，低于300在打印/放大时模糊 |
| 图片格式 | **PNG**（论文用）/**SVG**（后期编辑用） | PNG 无损且兼容 LaTeX；SVG 可导入 AI/Inkscape 微调 |
| 图片宽度 | `0.45-0.95\textwidth` | 单列图 0.45-0.5，通栏 0.7-0.95 |
| 宽高比 | 16:9 或 4:3 或黄金比例 1.618:1 | 避免正方形（除散点矩阵、热力图外） |
| 文件大小 | ≤ 2 MB | 过大影响 Word→PDF 转换 |

### 4.2 字体规范

| 元素 | 字号 (pt) | 字体 | 粗细 |
|---|---|---|---|
| 图标题 | 12-14 | SimHei / Arial | bold |
| 轴标签 | 10-12 | SimHei / Arial | regular |
| 轴刻度 | 8-10 | SimHei / Arial | regular |
| 图例 | 8-10 | SimHei / Arial | regular |
| 数值标注 | 7-9 | SimHei / Arial | regular |
| 脚注/来源 | 6-8 | SimSun / Times | regular |

**关键规则：图中最小文字 ≥ 8pt（最终排版尺寸下），这是评审阅读的最低可读标准。**

### 4.3 中文字体配置（完整方案）

```python
# ===== matplotlib 中文字体完整配置 =====
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 方法 1: 直接指定（Windows 最稳）
plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体，适用于标题/标注
plt.rcParams['font.serif'] = ['SimSun']       # 宋体，适用于脚注
plt.rcParams['axes.unicode_minus'] = False

# 方法 2: 使用系统已安装字体（跨平台安全）
# 先查找可用中文字体
# available_fonts = [f.name for f in fm.fontManager.ttflist]
# 然后设置第一个找到的中文字体
for font_name in ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC']:
    if font_name in [f.name for f in fm.fontManager.ttflist]:
        plt.rcParams['font.sans-serif'] = [font_name]
        break

# 方法 3: 使用 fontproperties 逐对象指定（最精细但最繁琐）
from matplotlib.font_manager import FontProperties
font_title = FontProperties(fname='C:/Windows/Fonts/simhei.ttf', size=14)
font_label = FontProperties(fname='C:/Windows/Fonts/simsun.ttc', size=10)
# ax.set_title('标题', fontproperties=font_title)
```

### 4.4 图例位置规范

| 场景 | 推荐位置 | `loc` 参数 |
|---|---|---|
| 图内部空白区 | 最佳自动选择 | `'best'` |
| 右上角（默认） | 图内部，不遮挡数据 | `'upper right'` |
| 图外部（数据密集时） | 右侧外部 | `bbox_to_anchor=(1.01, 1.0)` |
| 图下方横排（多系列时） | 图正下方 | `loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=4` |

**图例规则**：
- 系列数 ≥ 3 时必须有图例
- 图例框半透明（`framealpha=0.8`），不遮挡数据
- 图例顺序与数据出现顺序一致
- 不要用纯数字作为图例标签（1/2/3→方案A/B/C）

### 4.5 子图编号与文件命名规范

```
figures/fig_q1_convergence.png       # 问题1收敛曲线
figures/fig_q1_pareto_front.png      # 问题1 Pareto前沿
figures/fig_q2_heatmap_params.png    # 问题2参数热力图
figures/fig_q2_radar_comparison.png  # 问题2方案对比雷达图
figures/fig_q3_surface3d_obj.png     # 问题3目标函数3D曲面
figures/fig_q3_network_opt.png       # 问题3最优网络
figures/fig_q4_timeseries_pred.png   # 问题4时序预测
figures/fig_q4_sensitivity.png       # 问题4灵敏度分析
figures/fig_appendix_eda_corr.png    # 附录：EDA相关矩阵
```

命名规则：`fig_q{题号}_{内容描述}.{png/svg}`

### 4.6 导出设置（savefig 最佳参数）

```python
plt.savefig(
    'figures/fig_q1_xxx.png',
    dpi=300,                    # 分辨率
    bbox_inches='tight',        # 自动裁剪白边
    pad_inches=0.1,             # 少量内边距
    facecolor='white',          # 白色背景（不要透明背景用于论文）
    edgecolor='none',
    format='png',
    metadata={'Creator': 'Matplotlib', 'Title': 'Figure Title'}
)
# SVG 格式（后期可编辑）
plt.savefig('figures/fig_q1_xxx.svg', format='svg', bbox_inches='tight')
```

---

## 五、常见画图错误（10 例 Wrong → Right）

### 错误 1：饼图超过 5 个类别

| Wrong | Right |
|---|---|
| 8 个类别用饼图，切片细小且颜色相近无法区分 | 改用**水平条形图**（`barh`），从大到小排序，一目了然 |
| `ax.pie(values, labels=8_labels)` | `ax.barh(sorted_labels, sorted_values)` |

**原则**：饼图仅用于 2-5 个类别且和为 100% 的场景。超过 5 类用条形图。

### 错误 2：柱状图基线不是 0

| Wrong | Right |
|---|---|
| `ax.set_ylim(50, 80)`——柱高差视觉放大多倍 | `ax.set_ylim(0, 85)`——真实比例，A 是 B 的 1.2 倍而非 2 倍 |
| 读者被误导认为差异极大 | 诚实展示数据，差异由读者判断 |

**原则**：柱状图 y 轴**必须从 0 开始**（除非是残差图、变化率等特殊场景）。

### 错误 3：相关性用了折线图

| Wrong | Right |
|---|---|
| `ax.plot(x, y)` 展示两个变量的关系 | `ax.scatter(x, y, alpha=0.6)` + 回归线 |
| 数据点无序时折线产生伪趋势 | 散点图如实展示每个数据点 |

**原则**：折线图包含"连接线 = 趋势"的暗示，仅适用于有序数据（时间/序列）。

### 错误 4：颜色无意义（彩虹色滥用）

| Wrong | Right |
|---|---|
| 5 个互不相关的类别用 jet colormap 渐变 | 用**定性配色方案**（方案 1），每类一个独立颜色 |
| 暗示类别有顺序关系 | 颜色传达类别身份而非数值大小 |

**原则**：定性数据（类别）用不同的 hue，定量数据（数值）用亮度/饱和度变化。

### 错误 5：双 Y 轴滥用

| Wrong | Right |
|---|---|
| 两条数量级差 100 倍的曲线绑在同一双轴图上 | 用**两个上下并排的子图**，共享 x 轴 |
| 读者被迫在两个刻度间来回跳跃 | 每个子图清晰独立，趋势直观 |

**原则**：双 Y 轴应谨慎使用。若两变量数量级差 > 10 倍，用子图拆分。若必须用，两条线的颜色分别匹配对应 y 轴颜色。

### 错误 6：散点图不设透明度，数据重叠成黑块

| Wrong | Right |
|---|---|
| `ax.scatter(x, y, s=20)` 无 alpha，2000 个点 | `ax.scatter(x, y, s=15, alpha=0.3, edgecolors='none')` |
| 无法判断密度和分布形态 | 透明度叠加反映密度 |

**原则**：数据点 > 300 时必须设 `alpha ≤ 0.5`。

### 错误 7：3D 饼图

| Wrong | Right |
|---|---|
| 3D 饼图，透视扭曲各扇区面积比例 | 纯净的 2D 饼图（≤5 类）或水平条形图 |
| 前方的扇区看起来比后方大 | 二维平面面积比例准确 |

**原则**：**永远不要用 3D 饼图**。任何有倾斜角度的 3D 图都会造成视觉偏差。3D 图仅用于真正需要 3 个维度展示的数据（如曲面、散点）。

### 错误 8：图例遮挡关键数据

| Wrong | Right |
|---|---|
| `ax.legend()` 默认覆盖数据密集区 | `ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0))` 放在图外 |
| 关键离群值被图例挡住 | 图例和数据互不干扰 |

**原则**：**图例不应遮挡任何数据点**。数据密集区的图例一律移到图外。

### 错误 9：热力图用 jet colormap

| Wrong | Right |
|---|---|
| `cmap='jet'`——颜色变化不均匀，造成伪边界 | `cmap='viridis'` 或 `cmap='RdBu_r'`（有正负时） |
| 人为制造出数据中不存在的"条纹" | 感知均匀的 colormap，忠实呈现数据模式 |

**原则**：避免使用 jet 和 rainbow colormap。用 perceptually uniform 的 colormap（viridis, magma, plasma, inferno 或 RdBu_r）。

### 错误 10：图片分辨率低导致模糊

| Wrong | Right |
|---|---|
| `plt.savefig('fig.png')` 默认 100 dpi | `plt.savefig('fig.png', dpi=300)` |
| 插到论文/放大到通栏后文字和线条模糊 | 出版级清晰度 |

**原则**：所有论文用图 dpi ≥ 300。截图粘贴绝对禁止。

---

## 六、必备图（plot_helpers 调用）

| 方法 | 推荐图 | plot_helpers 函数 | 关键参数 |
|---|---|---|---|
| 优化/启发式 | 收敛曲线 | `convergence_curve(history, path)` | `history`: list[float] 每代最优值 |
| 多目标 | Pareto 前沿 | `pareto_front(f1, f2, path)` | `f1, f2`: list[float] 两目标值 |
| 相关/距离/混淆矩阵 | 热力图 | `heatmap(matrix, path)` | `matrix`: 2D array |
| 敏感性分析 | 龙卷风图 | `sensitivity_tornado(names, vals, path)` | `names/values`: 因素名和灵敏度值 |
| 时间序列/微分方程 | 拟合预测对比 | `timeseries_fit(t, y_real, y_pred, path)` | 各数组同长度 |
| 分类 | ROC 曲线 | `roc_curve_plot(y_true, y_score, path)` | — |

---

## 七、高端图（加分项）

| 图类型 | plot_helpers 函数 | 适用场景 |
|---|---|---|
| 3D 曲面 | `surface_3d(X, Y, Z, path)` | 目标函数地形 |
| 填充等高线 | `contour_filled(X, Y, Z, path)` | 可行域/等值域 |
| 雷达图 | `radar_chart(cats, vals_dict, path)` | 多方案多准则对比 |
| 小提琴图 | `violin_plot(data_list, path)` | 多组分布对比 |
| 网络图 | `network_graph(adj_matrix, path)` | 图论/网络拓扑 |
| 树状图 | `dendrogram_plot(data, path)` | 层次聚类 |
| 瀑布图 | `waterfall_chart(cats, vals, path)` | 因素分解 |
| 成对相关 | `pair_correlation(data, path)` | EDA |
| 3D 散点 | `scatter_3d(x, y, z, path)` | 三维数据分布 |
| 山脊图 | `ridge_plot(data_dict, path)` | 多组分布重叠 |
| 流图 | `streamgraph(labels, t, y, path)` | 成分时间演变 |

---

## 八、高端图选型指南

| 论文场景 | 推荐高端图 | 理由 |
|---|---|---|
| 多方案综合评价（AHP/TOPSIS/熵权） | 雷达图 | 一图展示所有维度得分 |
| 优化问题有 2 个关键参数 | 3D 曲面 + 等高线 | 地形+投影双视角 |
| 图论/网络（最短路/最大流/中心性） | 网络图 | 拓扑结构一目了然 |
| 聚类分析（KMeans/层次/DBSCAN） | 树状图 + 3D散点 | 层次+空间双角度 |
| 灵敏度分析（多因素） | 瀑布图 + 龙卷风图 | 逐个因素拆解贡献 |
| 随机模拟/多次重复实验 | 小提琴图或山脊图 | 分布全貌vs仅均方差 |
| 数据探索（特征工程前） | 成对相关矩阵 | 变量关系一览 |
| 种群/传染病/市场演化 | 流图 + 时序图 | 构成演变+总量趋势 |

---

## 九、使用方式

```python
import sys; sys.path.insert(0, r"C:/Users/HUAWEI/.claude/skills/math-modeling/scripts")

# 基础图
from plot_helpers import convergence_curve, heatmap, sensitivity_tornado
from plot_helpers import pareto_front, timeseries_fit, roc_curve_plot

# 高端图（按需导入）
from plot_helpers import surface_3d, contour_filled, radar_chart, violin_plot
from plot_helpers import network_graph, dendrogram_plot, waterfall_chart
from plot_helpers import pair_correlation, scatter_3d, ridge_plot, streamgraph

# 使用示例
convergence_curve(hist, "figures/fig_q1_convergence.png")
surface_3d(X, Y, Z, "figures/fig_q2_surface3d.png", title="Objective Function Surface")
radar_chart(["Accuracy","Speed","Robustness"], {"Model A":[4,3,5],"Model B":[3,5,4]},
            "figures/fig_q2_radar.png", title="Multi-Dimensional Comparison")
```

LaTeX 引用：`\includegraphics[width=0.7\textwidth]{fig_q1_convergence.png}`（模板已设 `graphicspath` 含 `figures/`）。

---

## 十、快速检查清单（提交前自查）

- [ ] 每张图都在正文中用 `\ref` 引用并解读（不只放图不说话）
- [ ] 分辨率 ≥ 300 dpi，字体 ≥ 8pt（最终尺寸下）
- [ ] 柱状图基线从 0 开始
- [ ] 所有轴线标有标签和单位
- [ ] 图例不遮挡数据、标签有意义
- [ ] 配色在灰度打印下可区分（至少线型/图案辅助）
- [ ] 无 3D 饼图 / jet colormap / 无意义彩虹色
- [ ] 数据来源图注明来源；仿真图注明重复次数与随机种子
- [ ] 高端图服务于论证，正文解释"揭示了什么、为什么非它不可"
- [ ] 每道题至少 1 张图，论文整体 6-12 张图
- [ ] 文件名遵循 `fig_q{题号}_{内容描述}.png` 规范
- [ ] 透明度合理（散点图点数 >300 时 alpha ≤ 0.5）
