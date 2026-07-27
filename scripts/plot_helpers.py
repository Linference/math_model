#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""plot_helpers.py — 数学建模常用可视化配方（统一风格 + 高端扩展）。

所有函数返回保存后的图片路径，供 LaTeX \\includegraphics 引用。
默认使用同目录 templates/figures.mplstyle（若存在），中文字体自动设置。

导入方式：
    import sys; sys.path.insert(0, r"<skill>/scripts")
    from plot_helpers import (
        # 基础必备
        convergence_curve, heatmap, sensitivity_tornado, pareto_front,
        timeseries_fit, roc_curve_plot,
        # 高端扩展
        surface_3d, contour_filled, radar_chart, violin_plot,
        network_graph, dendrogram_plot, waterfall_chart, pair_correlation,
        scatter_3d, ridge_plot, streamgraph,
    )
"""
import os
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm, gridspec
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch
from matplotlib.collections import LineCollection
from matplotlib.path import Path
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.ticker as mticker

# ---- 中文字体：Windows 优先 SimHei，退化到常见无衬线 ----
for _f in ["SimHei", "Microsoft YaHei", "WenQuanYi Zen Hei", "Arial Unicode MS"]:
    try:
        matplotlib.font_manager.findfont(_f, fallback_to_default=False)
        plt.rcParams["font.sans-serif"] = [_f]
        break
    except Exception:
        continue
plt.rcParams["axes.unicode_minus"] = False

# 若存在项目风格文件则叠加
_style = os.path.join(os.path.dirname(__file__), "..", "templates", "figures.mplstyle")
if os.path.exists(_style):
    try:
        plt.style.use(_style)
    except Exception:
        pass


def _save(fig, out):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out


# ====================================================================
#   基础必备图（保留原函数，小幅增强）
# ====================================================================

def convergence_curve(history, out="fig_convergence.png",
                      xlabel="迭代次数", ylabel="目标函数值", title="算法收敛曲线"):
    """优化/启发式算法收敛曲线。history: 1D 序列或 {label: seq}。"""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    if isinstance(history, dict):
        for k, v in history.items():
            ax.plot(range(1, len(v) + 1), v, label=k, linewidth=1.8)
        ax.legend(framealpha=0.7)
    else:
        ax.plot(range(1, len(history) + 1), history, linewidth=2, color="#4C72B0")
        # 标注最优值
        best = min(history) if history else 0
        ax.axhline(best, color="crimson", linestyle="--", alpha=0.5,
                   label=f"最优值 = {best:.4g}")
        ax.legend()
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_title(title, fontweight="bold")
    ax.grid(True, alpha=0.3)
    return _save(fig, out)


def heatmap(matrix, out="fig_heatmap.png", xticklabels=None, yticklabels=None,
            title="相关性 / 距离热力图", cmap="RdBu_r", annotate=True, fmt=".2f"):
    """相关系数矩阵、混淆矩阵、距离矩阵等热力图。默认 annotate=True。"""
    matrix = np.asarray(matrix, dtype=float)
    n, m = matrix.shape
    fig, ax = plt.subplots(figsize=(max(6, m * 0.8), max(5, n * 0.7)))
    im = ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=-1, vmax=1
                   if cmap == "RdBu_r" else None)
    cbar = fig.colorbar(im, ax=ax, shrink=0.85)
    if xticklabels is not None:
        ax.set_xticks(range(m))
        ax.set_xticklabels(xticklabels, rotation=45, ha="right", fontsize=9)
    if yticklabels is not None:
        ax.set_yticks(range(n))
        ax.set_yticklabels(yticklabels, fontsize=9)
    if annotate:
        for i in range(n):
            for j in range(m):
                val = matrix[i, j]
                ax.text(j, i, f"{val:{fmt}}", ha="center", va="center",
                        color="white" if abs(val) > 0.5 else "black",
                        fontsize=8, fontweight="bold")
    ax.set_title(title, fontweight="bold")
    return _save(fig, out)


def sensitivity_tornado(params, low, high, base=0.0, out="fig_sensitivity.png",
                        title="敏感性分析（龙卷风图）"):
    """参数敏感性龙卷风图。params 名称列表；low/high 对应低高扰动下的输出。"""
    params, low, high = list(params), np.asarray(low), np.asarray(high)
    order = np.argsort(np.abs(high - low))
    params = [params[i] for i in order]
    low, high = low[order], high[order]
    y = np.arange(len(params))
    fig, ax = plt.subplots(figsize=(7, 0.6 * len(params) + 1.5))
    ax.barh(y, high - base, left=base, color="#4C72B0", alpha=0.85, label="参数增大 (+Δ)")
    ax.barh(y, low - base, left=base, color="#DD8452", alpha=0.85, label="参数减小 (-Δ)")
    ax.axvline(base, color="k", linewidth=1.2)
    ax.set_yticks(y); ax.set_yticklabels(params, fontsize=10)
    ax.set_xlabel("目标输出", fontsize=11); ax.set_title(title, fontweight="bold")
    ax.legend(loc="lower right", framealpha=0.8)
    ax.grid(axis="x", alpha=0.3)
    return _save(fig, out)


def pareto_front(objectives, out="fig_pareto.png", labels=("目标 1", "目标 2"),
                 title="Pareto 前沿（多目标优化）"):
    """多目标优化 Pareto 前沿散点+前沿线。objectives: N×2 数组。"""
    obj = np.asarray(objectives, dtype=float)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(obj[:, 0], obj[:, 1], s=18, alpha=0.35, color="gray", label="可行解")
    # 计算非支配前沿（最小化两目标）
    idx = np.argsort(obj[:, 0])
    front, best = [], np.inf
    for i in idx:
        if obj[i, 1] <= best:
            front.append(i); best = obj[i, 1]
    f = obj[front]
    ax.plot(f[:, 0], f[:, 1], "-o", color="crimson", linewidth=2,
            markersize=6, label="Pareto 前沿")
    ax.set_xlabel(labels[0], fontsize=11); ax.set_ylabel(labels[1], fontsize=11)
    ax.set_title(title, fontweight="bold")
    ax.legend(framealpha=0.8); ax.grid(True, alpha=0.3)
    return _save(fig, out)


def timeseries_fit(t, y_true, y_pred=None, t_pred=None, y_pred_future=None,
                   out="fig_timeseries.png", xlabel="时间", ylabel="值",
                   title="时间序列拟合/预测", labels=("实际值", "拟合值", "预测值")):
    """时序拟合与预测对比。可选：未来预测用 t_pred / y_pred_future + 置信区间样式。"""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(t, y_true, "-", label=labels[0], linewidth=1.8, color="#4C72B0")
    if y_pred is not None:
        ax.plot(t, y_pred, "--", label=labels[1], linewidth=1.6, color="#DD8452")
    if t_pred is not None and y_pred_future is not None:
        ax.plot(t_pred, y_pred_future, ":", label=labels[2], linewidth=1.8,
                color="crimson")
        # 未来预测区域着色
        ax.axvspan(t[-1], t_pred[-1] if len(t_pred) else t[-1],
                   alpha=0.08, color="crimson")
    ax.set_xlabel(xlabel, fontsize=11); ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontweight="bold")
    ax.legend(framealpha=0.8); ax.grid(True, alpha=0.3)
    return _save(fig, out)


def roc_curve_plot(fpr, tpr, auc=None, out="fig_roc.png", title="ROC 曲线"):
    """分类模型 ROC 曲线。可传多个 {(name, fpr, tpr, auc), ...} 画多条。"""
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    if isinstance(fpr, dict):
        for name, d in fpr.items():
            lbl = f"{name} (AUC={d['auc']:.3f})" if d.get("auc") else name
            ax.plot(d["fpr"], d["tpr"], linewidth=2, label=lbl)
    else:
        lbl = f"AUC = {auc:.3f}" if auc is not None else "ROC"
        ax.plot(fpr, tpr, linewidth=2, label=lbl)
    ax.plot([0, 1], [0, 1], "k--", alpha=0.4)
    ax.set_xlabel("假正率 (FPR)", fontsize=11)
    ax.set_ylabel("真正率 (TPR)", fontsize=11)
    ax.set_title(title, fontweight="bold")
    ax.legend(loc="lower right", framealpha=0.8)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    return _save(fig, out)


# ====================================================================
#   高端扩展图（新增）
# ====================================================================

def surface_3d(X, Y, Z, out="fig_surface3d.png",
               xlabel="X", ylabel="Y", zlabel="Z",
               title="三维曲面图", azimuth=-60, elevation=30,
               cmap_name="viridis", contour_proj=True):
    """3D 曲面图：优化/参数空间的景观可视化。X, Y: 网格坐标；Z: 函数值。"""
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(X, Y, Z, cmap=cmap_name, alpha=0.9,
                           linewidth=0, antialiased=True)
    if contour_proj:
        ax.contour(X, Y, Z, zdir="z", offset=Z.min() * 1.1 if Z.min() < 0 else 0,
                   cmap=cmap_name, alpha=0.4, linewidths=0.8)
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=12)
    ax.set_xlabel(xlabel, fontsize=10); ax.set_ylabel(ylabel, fontsize=10)
    ax.set_zlabel(zlabel, fontsize=10)
    ax.set_title(title, fontweight="bold", fontsize=13)
    ax.view_init(elevation, azimuth)
    return _save(fig, out)


def contour_filled(X, Y, Z, out="fig_contour.png",
                   xlabel="X", ylabel="Y", title="等高线填充图",
                   levels=12, cmap_name="viridis"):
    """填充等高线图：二维优化目标函数地形。"""
    fig, ax = plt.subplots(figsize=(7, 6))
    cf = ax.contourf(X, Y, Z, levels=levels, cmap=cmap_name, alpha=0.9)
    cs = ax.contour(X, Y, Z, levels=levels, colors="black", linewidths=0.4, alpha=0.4)
    ax.clabel(cs, inline=True, fontsize=7, fmt="%.1f")
    fig.colorbar(cf, ax=ax, shrink=0.85)
    ax.set_xlabel(xlabel, fontsize=11); ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontweight="bold")
    return _save(fig, out)


def radar_chart(categories, values, out="fig_radar.png",
                title="雷达图（多指标评价）",
                labels=None, colors=None,
                fill_alpha=0.15, value_range=None):
    """雷达图/蜘蛛图：多准则决策(AHP/TOPSIS)方案对比。
    values: 单方案 1D 序列，或多方案 {"方案A": [...], "方案B": [...]}。
    """
    categories = list(categories)
    N = len(categories)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]  # 闭合

    fig, ax = plt.subplots(figsize=(6.5, 6.5), subplot_kw=dict(polar=True))

    if not isinstance(values, dict):
        values = {"": list(values)}
    if labels is None:
        labels = list(values.keys())
    if colors is None:
        colors = plt.cm.Set2(np.linspace(0, 1, len(values)))

    for (name, vals), color, label in zip(values.items(), colors, labels):
        vals = list(vals) + [list(vals)[0]]
        ax.fill(angles, vals, alpha=fill_alpha, color=color)
        ax.plot(angles, vals, "o-", linewidth=2, label=label or name, color=color,
                markersize=5)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10)
    if value_range:
        ax.set_ylim(*value_range)
    ax.set_title(title, fontweight="bold", pad=20, fontsize=12)
    if any(labels):
        ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), framealpha=0.8)
    ax.grid(True, alpha=0.3)
    return _save(fig, out)


def violin_plot(data, out="fig_violin.png", labels=None, title="小提琴图",
                xlabel="", ylabel="值", show_means=True, show_extrema=True):
    """小提琴图：多组数据分布对比（优于箱线图的细节呈现）。
    data: 列表的列表或 {label: array}。
    """
    fig, ax = plt.subplots(figsize=(7, 5))
    if isinstance(data, dict):
        labels = list(data.keys())
        datasets = list(data.values())
    else:
        datasets = list(data)
    parts = ax.violinplot(datasets, showmeans=show_means, showextrema=show_extrema)
    # 配色
    for pc, color in zip(parts["bodies"],
                         plt.cm.viridis(np.linspace(0.1, 0.9, len(datasets)))):
        pc.set_facecolor(color)
        pc.set_alpha(0.7)
    if labels:
        ax.set_xticks(range(1, len(labels) + 1))
        ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=11); ax.set_xlabel(xlabel, fontsize=11)
    ax.set_title(title, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    return _save(fig, out)


def network_graph(adj_matrix, out="fig_network.png", labels=None,
                  title="网络拓扑图", node_size=300, layout="spring",
                  edge_cmap="viridis", node_color=None):
    """网络/图论可视化：邻接矩阵 → 力导向布局图。
    需要 networkx（若未安装则自动提示）。
    """
    try:
        import networkx as nx
    except ImportError:
        raise ImportError("network_graph 需要 networkx 库: pip install networkx")

    adj = np.asarray(adj_matrix, dtype=float)
    n = adj.shape[0]
    G = nx.from_numpy_array(adj, create_using=nx.DiGraph() if not np.allclose(adj, adj.T) else nx.Graph())

    fig, ax = plt.subplots(figsize=(8, 7))
    if layout == "spring":
        pos = nx.spring_layout(G, seed=42, k=2.5 / np.sqrt(n))
    elif layout == "circular":
        pos = nx.circular_layout(G)
    elif layout == "kamada_kawai":
        pos = nx.kamada_kawai_layout(G)
    else:
        pos = nx.spring_layout(G, seed=42)

    edges = nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.4, edge_color="gray",
                                   width=1.0, arrowsize=12,
                                   arrowstyle="-|>")
    if node_color is None:
        node_color = "#4C72B0"
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_size,
                           node_color=node_color, alpha=0.9,
                           edgecolors="white", linewidths=1.5)
    if labels is None:
        labels = {i: str(i + 1) for i in range(n)}
    nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=9, font_weight="bold")
    ax.set_title(title, fontweight="bold", fontsize=13)
    ax.axis("off")
    return _save(fig, out)


def dendrogram_plot(data, out="fig_dendrogram.png", labels=None,
                    title="层次聚类树状图", method="ward",
                    orientation="top", color_threshold=None,
                    leaf_rotation=90):
    """层次聚类树状图。data: N×M 数组（样本×特征）或距离矩阵(condensed)。
    """
    matrix = np.asarray(data, dtype=float)
    Z = linkage(matrix, method=method)
    fig, ax = plt.subplots(figsize=(8, 5))
    dendrogram(Z, labels=labels, orientation=orientation,
               leaf_rotation=leaf_rotation, leaf_font_size=9,
               color_threshold=color_threshold, ax=ax,
               above_threshold_color="gray")
    ax.set_title(title, fontweight="bold", fontsize=13)
    ax.set_ylabel("距离", fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    return _save(fig, out)


def waterfall_chart(categories, values, out="fig_waterfall.png",
                    title="瀑布图（因素分解）", ylabel="贡献值",
                    total_label="总计"):
    """瀑布图：因素分解 / 累计贡献分析（如敏感性拆解、利润驱动分解）。
    categories: 因素名称; values: 各因素贡献值（正负均可）。
    """
    categories = list(categories)
    values = np.asarray(values, dtype=float)
    n = len(values)
    cumulative = np.zeros(n + 1)
    for i in range(n):
        cumulative[i + 1] = cumulative[i] + values[i]

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#4C72B0" if v >= 0 else "#DD8452" for v in values]
    bottoms = [cumulative[i] if values[i] >= 0 else cumulative[i + 1] for i in range(n)]
    heights = [abs(v) for v in values]

    # 画柱
    x = np.arange(n)
    bars = ax.bar(x, heights, bottom=bottoms, color=colors, alpha=0.85, edgecolor="white")
    # 连接线
    for i in range(n):
        ax.plot([i - 0.4, i + 0.4], [cumulative[i + 1]] * 2, color="gray",
                linewidth=1, alpha=0.6)
    # 总计柱
    ax.bar(n, cumulative[-1], color="crimson", alpha=0.7, edgecolor="white")

    all_xticks = categories + [total_label]
    ax.set_xticks(range(n + 1))
    ax.set_xticklabels(all_xticks, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontweight="bold")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.grid(axis="y", alpha=0.3)
    # 标注值
    for i in range(n):
        y_pos = cumulative[i + 1] + (heights[i] * 0.2 if values[i] >= 0 else -heights[i] * 0.2)
        ax.text(i, y_pos, f"{values[i]:+.2f}", ha="center", va="bottom" if values[i] >= 0 else "top",
                fontsize=8, fontweight="bold")
    ax.text(n, cumulative[-1], f"{cumulative[-1]:.2f}", ha="center", va="bottom",
            fontsize=9, fontweight="bold", color="crimson")
    return _save(fig, out)


def pair_correlation(data, out="fig_paircorr.png", columns=None,
                     title="成对相关矩阵图", diagonal="hist"):
    """成对相关图：散点矩阵 + 下三角相关 + 对角线直方图/KDE。
    模仿 seaborn pairplot 但用纯 matplotlib。
    data: N×M 数组。
    """
    data = np.asarray(data, dtype=float)
    n, m = data.shape
    if columns is None:
        columns = [f"X{i+1}" for i in range(m)]

    fig, axes = plt.subplots(m, m, figsize=(m * 2.5, m * 2.2))
    if m == 1:
        axes = np.array([[axes]])
    corr = np.corrcoef(data.T)

    for i in range(m):
        for j in range(m):
            ax = axes[i, j]
            if i == j:
                if diagonal == "hist":
                    ax.hist(data[:, i], bins=20, color="#4C72B0", alpha=0.7, edgecolor="white")
                else:
                    from scipy import stats as scipy_stats
                    kde_x = np.linspace(data[:, i].min(), data[:, i].max(), 100)
                    kde = scipy_stats.gaussian_kde(data[:, i])
                    ax.plot(kde_x, kde(kde_x), color="#4C72B0", linewidth=2)
                    ax.fill_between(kde_x, kde(kde_x), alpha=0.2, color="#4C72B0")
                ax.set_xlabel(columns[i], fontsize=9)
            elif j < i:
                ax.scatter(data[:, j], data[:, i], s=10, alpha=0.4, color="#4C72B0",
                           edgecolors="none")
                # 趋势线
                slope, intercept = np.polyfit(data[:, j], data[:, i], 1)
                xs = np.array([data[:, j].min(), data[:, j].max()])
                ax.plot(xs, slope * xs + intercept, "--", color="crimson",
                        linewidth=1, alpha=0.6)
            else:
                ax.text(0.5, 0.5, f"{corr[i, j]:.2f}", transform=ax.transAxes,
                        ha="center", va="center", fontsize=14,
                        fontweight="bold",
                        color="crimson" if abs(corr[i, j]) > 0.7 else "black")
                ax.set_xticks([]); ax.set_yticks([])
                # 背景色块
                bg = abs(corr[i, j])
                rect = plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                                     facecolor=plt.cm.RdBu_r(bg), alpha=0.25)
                ax.add_patch(rect)

            if j > 0:
                ax.set_yticklabels([])
            if i < m - 1:
                ax.set_xticklabels([])
            if j == 0 and i != 0:
                ax.set_ylabel(columns[i], fontsize=9)

    fig.suptitle(title, fontweight="bold", fontsize=14, y=1.01)
    fig.tight_layout()
    return _save(fig, out)


def scatter_3d(x, y, z, out="fig_scatter3d.png",
               xlabel="X", ylabel="Y", zlabel="Z",
               title="三维散点图", color=None, size=30,
               cmap_name="viridis", azimuth=-50, elevation=25):
    """3D 散点图：三维数据分布，支持颜色映射第四维。"""
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")
    if color is None:
        color = "#4C72B0"
    sc = ax.scatter(x, y, z, c=color, s=size, cmap=cmap_name,
                    alpha=0.8, edgecolors="white", linewidth=0.3)
    if isinstance(color, (list, np.ndarray)):
        fig.colorbar(sc, ax=ax, shrink=0.5, aspect=12)
    ax.set_xlabel(xlabel, fontsize=10); ax.set_ylabel(ylabel, fontsize=10)
    ax.set_zlabel(zlabel, fontsize=10)
    ax.set_title(title, fontweight="bold", fontsize=13)
    ax.view_init(elevation, azimuth)
    return _save(fig, out)


def ridge_plot(data, out="fig_ridge.png", labels=None,
               title="山脊图（分布对比）", cmap_name="viridis",
               overlap=1.5):
    """山脊图/ridgeline：多组分布重叠对比，适合展示参数后验或时序分布演化。
    data: 列表的列表或 {label: array}。
    """
    from scipy import stats as scipy_stats

    if isinstance(data, dict):
        labels = list(data.keys())
        datasets = list(data.values())
    else:
        datasets = list(data)
    if labels is None:
        labels = [f"G{i+1}" for i in range(len(datasets))]

    n = len(datasets)
    colors = plt.get_cmap(cmap_name)(np.linspace(0.1, 0.9, n))
    fig, ax = plt.subplots(figsize=(8, max(4, n * 0.8)))

    for i, (ds, lbl, clr) in enumerate(zip(datasets, labels, colors)):
        ds = np.asarray(ds, dtype=float)
        xs = np.linspace(ds.min(), ds.max(), 200)
        kde = scipy_stats.gaussian_kde(ds)
        ys = kde(xs)
        ys = ys / ys.max() * overlap  # 缩放
        baseline = -i * overlap
        ax.fill_between(xs, baseline, baseline + ys, color=clr, alpha=0.7)
        ax.plot(xs, baseline + ys, color="white", linewidth=0.6)
        ax.text(xs.min(), baseline + overlap * 0.15, lbl,
                fontsize=9, va="bottom", fontweight="bold")

    ax.set_yticks([])
    ax.set_xlabel("值", fontsize=11)
    ax.set_title(title, fontweight="bold", fontsize=13)
    ax.grid(axis="x", alpha=0.3)
    return _save(fig, out)


def streamgraph(data, out="fig_streamgraph.png", labels=None,
                title="流图（构成随时间变化）", x=None,
                cmap_name="Set3"):
    """流图/streamgraph：展示各成分随时间的变化（如种群构成、市场份额）。
    data: T×K 数组（时间×类别）。
    """
    data = np.asarray(data, dtype=float)
    T, K = data.shape
    if x is None:
        x = np.arange(T)
    if labels is None:
        labels = [f"C{i+1}" for i in range(K)]

    # 中心化堆叠
    proportions = data / data.sum(axis=1, keepdims=True)
    stacked = np.cumsum(proportions, axis=1)
    centers = (stacked - proportions / 2)
    centered = centers - 0.5

    colors = plt.get_cmap(cmap_name)(np.linspace(0, 1, K))
    fig, ax = plt.subplots(figsize=(9, 5))

    for k in range(K):
        y_top = centered[:, k] + proportions[:, k] / 2
        y_bot = centered[:, k] - proportions[:, k] / 2
        # 使用平滑填充
        ax.fill_between(x, y_bot, y_top, label=labels[k],
                        color=colors[k], alpha=0.85, linewidth=0.3,
                        edgecolor="white")

    ax.set_xlim(x[0], x[-1])
    ax.set_xlabel("时间", fontsize=11)
    ax.set_yticks([])
    ax.set_title(title, fontweight="bold", fontsize=13)
    ax.legend(loc="upper right", framealpha=0.8, fontsize=9,
              ncol=max(1, K // 6))
    ax.grid(axis="x", alpha=0.3)
    return _save(fig, out)


if __name__ == "__main__":
    print("=" * 60)
    print("plot_helpers 自测 —— 生成全部示例图")
    print("=" * 60)

    # 基础图
    convergence_curve(np.exp(-np.linspace(0, 3, 40)) + 0.02, "demo_conv.png")
    heatmap(np.random.RandomState(0).rand(5, 5), "demo_heat.png",
            xticklabels=list("ABCDE"), yticklabels=list("ABCDE"), annotate=True)
    sensitivity_tornado(["参数 a", "参数 b", "参数 c", "参数 d"],
                        [-1.2, -2.5, -0.3, -1.8],
                        [1.5, 2.8, 0.6, 1.4],
                        out="demo_tornado.png")
    pareto_front(np.random.RandomState(1).rand(60, 2), "demo_pareto.png")
    t = np.linspace(0, 4 * np.pi, 100)
    timeseries_fit(t, np.sin(t) + np.random.RandomState(2).normal(0, 0.1, 100),
                   np.sin(t), out="demo_timeseries.png")
    roc_curve_plot(np.linspace(0, 1, 50), np.sqrt(np.linspace(0, 1, 50)),
                   auc=0.67, out="demo_roc.png")

    # 高端图
    # 3D 曲面
    xs = np.linspace(-3, 3, 50)
    ys = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(xs, ys)
    Z = -(X**2 + Y**2) + 3 * np.sin(X) * np.cos(Y)
    surface_3d(X, Y, Z, "demo_surface3d.png")

    # 填充等高线
    contour_filled(X, Y, Z, "demo_contour.png")

    # 雷达图
    radar_chart(["精度", "速度", "稳定性", "可解释性", "泛化性"],
                {"模型 A": [4.2, 3.5, 4.8, 3.0, 4.5],
                 "模型 B": [3.8, 4.6, 3.2, 4.2, 3.9]},
                out="demo_radar.png")

    # 小提琴图
    violin_plot([np.random.RandomState(i).normal(0, 1, 200) for i in range(4)],
                labels=["A", "B", "C", "D"], out="demo_violin.png")

    # 网络图 (简单环)
    adj = np.array([[0, 1, 0, 0, 1],
                    [1, 0, 1, 0, 0],
                    [0, 1, 0, 1, 0],
                    [0, 0, 1, 0, 1],
                    [1, 0, 0, 1, 0]], dtype=float)
    try:
        network_graph(adj, "demo_network.png", labels={i: f"V{i+1}" for i in range(5)})
    except ImportError:
        print("（跳过 network_graph: 需 networkx）")

    # 树状图
    dendrogram_plot(np.random.RandomState(5).rand(10, 4), "demo_dendrogram.png",
                    labels=[f"S{i+1}" for i in range(10)])

    # 瀑布图
    waterfall_chart(["因子 A", "因子 B", "因子 C", "因子 D", "因子 E"],
                    [5.2, -2.1, 3.8, -1.5, 2.6], "demo_waterfall.png")

    # 成对相关
    pair_correlation(np.random.RandomState(7).rand(100, 4),
                     columns=["特征 1", "特征 2", "特征 3", "特征 4"],
                     out="demo_paircorr.png")

    # 3D 散点
    rng = np.random.RandomState(9)
    scatter_3d(rng.randn(200), rng.randn(200), rng.randn(200),
               color=rng.rand(200), out="demo_scatter3d.png")

    # 山脊图
    ridge_plot([rng.normal(i * 2, 1, 300) for i in range(5)],
               labels=[f"t={i}" for i in range(5)], out="demo_ridge.png")

    # 流图
    streamgraph(np.abs(rng.randn(30, 4).cumsum(axis=0) + 5),
                labels=["组分 A", "组分 B", "组分 C", "组分 D"],
                out="demo_streamgraph.png")

    print("\n✅ 全部 16 张示例图已生成到当前目录。")
