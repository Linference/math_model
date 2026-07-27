# 04 — 建模配方（Cookbook）

每种方法：建模要点 + 求解工具 + 必配图 + 验证。配合 `plot_helpers.py`。

## 优化 / 规划
- **LP/IP**：`min cᵀx s.t. Ax≤b`。工具 `pulp` 或 `scipy.optimize.linprog`。验证：可行性、对偶、灵敏度。图：可行域/影子价格。
- **非线性**：`scipy.optimize.minimize`（SLSQP 带约束）。验证 KKT、凸性。图：收敛曲线。
- **多目标**：加权/ε-约束/NSGA。图：`pareto_front`。
- **启发式(GA/PSO/SA/ACO)**：自写；记录每代最优。图：`convergence_curve`。

## 微分方程
- **SIR/SEIR/种群/扩散**：`scipy.integrate.solve_ivp`。验证：守恒、稳态、参数敏感。图：`timeseries_fit` 各仓室曲线。
- 参数辨识：最小二乘拟合观测。

## 统计 / 回归
- 多元/logistic 回归：`statsmodels`（看 p 值、R²、残差）。方差分析、假设检验。图：残差图、`roc_curve_plot`。
- 主成分/因子：`sklearn.decomposition.PCA`。图：碎石图、`heatmap` 载荷。

## 评价 / 决策
- **AHP**：构造判断矩阵→一致性检验(CR<0.1)→权重。
- **TOPSIS**：规范化→正负理想解→贴近度排序。
- **熵权法**：由信息熵定权，常与 TOPSIS 组合。
- **灰色关联 / 模糊综合评价**。图：`heatmap` 权重、评分条形图。

## 时间序列
- ARIMA(`statsmodels`)、指数平滑、灰色 GM(1,1)。验证：残差白噪声检验、后验差比。图：`timeseries_fit`。

## 图论 / 网络
- 最短路/最大流/MST/中心性：`networkx`。图：网络图、`heatmap` 邻接。

## 仿真
- 蒙特卡洛（大样本估计+置信区间）、排队论(M/M/1)、元胞自动机。图：分布直方图、收敛。

## 机器学习
- 随机森林/XGBoost/SVM/KMeans：`sklearn`。**必做交叉验证**防过拟合。图：`roc_curve_plot`、混淆矩阵 `heatmap`、特征重要性。

## 每个模型都要有的三件套
1. **灵敏度分析**（`sensitivity_tornado`）——参数扰动看结果稳不稳。
2. **误差/精度**——与真值或交叉验证比。
3. **结果解读**——数字背后的现实含义。
