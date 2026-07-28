# 04 — 建模配方（Cookbook）

每种方法：建模要点 + 求解工具 + 必配图 + 验证 + **算法正确性审核清单**。配合 `plot_helpers.py`。

---

## ⛔ 通用算法正确性审核清单（所有方法共用）

在写代码之前、写完代码之后、写进论文之前，三次检查以下清单：

### 编码前（设计审核）
- [ ] 算法选择理由明确（为什么选 A 不选 B/C）
- [ ] 收敛性/最优性条件已确认（优化类：凸性？启发式：收敛判据？）
- [ ] 已知失效模式已列出（如 AHP 的 CR>0.1、TOPSIS 的逆序问题）
- [ ] 数值稳定性预案已准备（矩阵奇异、除零、梯度消失）

### 编码后（实现审核）
- [ ] 代码使用固定随机种子 `np.random.seed(42)`
- [ ] 关键中间变量打印到 stdout（方便验证）
- [ ] 所有输出带单位
- [ ] 边界条件不崩溃（0、极大值、负数）
- [ ] 公式实现与方案表完全一致（变量名、参数、正负号）

### 写论文前（数值审核）
- [ ] 论文中每个数字都能在代码输出中找到对应来源（变量名+行号）
- [ ] 计算派生值标注了计算公式和输入来源
- [ ] 所有比值/差值分子分母单位一致
- [ ] 量纲体系统一（不混用 kg 和 t、不混用 °C 和 K）

---

## 优化 / 规划

- **LP/IP**：`min cᵀx s.t. Ax≤b`。工具 `pulp` 或 `scipy.optimize.linprog`。
  验证：可行性、对偶、灵敏度。图：可行域/影子价格。
  **⛔ 审核重点**：约束完整性与方案表一致、对偶价格非负检验

- **非线性**：`scipy.optimize.minimize`（SLSQP 带约束）。
  验证 KKT、凸性。图：收敛曲线。
  **⛔ 审核重点**：目标函数是否凸、多起点检验全局最优

- **多目标**：加权/ε-约束/NSGA。图：`pareto_front`。
  **⛔ 审核重点**：Pareto 前沿是否非支配、权重灵敏度

- **启发式(GA/PSO/SA/ACO)**：自写；记录每代最优。图：`convergence_curve`。
  **⛔ 审核重点**：种群多样性是否维持、是否早熟收敛、多次独立运行结果稳定

---

## 微分方程

- **SIR/SEIR/种群/扩散**：`scipy.integrate.solve_ivp`。
  验证：守恒、稳态、参数敏感。图：`timeseries_fit` 各仓室曲线。
  **⛔ 审核重点**：总人口守恒检验、稳态分析是否正确

---

## 统计 / 回归

- 多元/logistic 回归：`statsmodels`（看 p 值、R²、残差）。
  图：残差图、`roc_curve_plot`。
  **⛔ 审核重点**：多重共线性(VIF)、异方差检验、残差正态性

- 主成分/因子：`sklearn.decomposition.PCA`。图：碎石图、`heatmap` 载荷。
  **⛔ 审核重点**：KMO 检验 > 0.6、累计方差解释率

---

## 评价 / 决策

- **AHP**：构造判断矩阵→一致性检验(CR<0.1)→权重。
  **⛔ 审核重点（AHP 是最容易出错的评价方法）**：
  1. 判断矩阵必须通过一致性检验（CR < 0.1），CR ≥ 0.1 时不可用
  2. 特征分解法 vs 几何平均法的权重可能不同——必须统一算法并在论文中声明
  3. 全局权重和恰好等于 100.00% 在实际中几乎不可能（必有舍入误差）——如果恰好等于则高度可疑
  4. 必须报告 λ_max、CI、CR 值

- **TOPSIS**：规范化→正负理想解→贴近度排序。
  **⛔ 审核重点（TOPSIS 的逆序问题是经典坑）**：
  1. 新增/删除候选方案会导致排序变化（逆序问题）——必须在论文中讨论
  2. 数据规范化方式（向量规范法 vs 极差法）会影响结果——必须声明
  3. 权重 ±20% 扰动分析至少对前三名做

- **熵权法**：由信息熵定权，常与 TOPSIS 组合。
- **灰色关联 / 模糊综合评价**。图：`heatmap` 权重、评分条形图。

---

## 时间序列

- ARIMA(`statsmodels`)、指数平滑、灰色 GM(1,1)。
  验证：残差白噪声检验、后验差比。图：`timeseries_fit`。
  **⛔ 审核重点**：平稳性检验(ADF)、残差 Ljung-Box 检验 p > 0.05

---

## 图论 / 网络

- 最短路/最大流/MST/中心性：`networkx`。图：`network_graph`、`heatmap` 邻接。
  **⛔ 审核重点**：图连通性检查、负权边处理

---

## 仿真

- 蒙特卡洛（大样本估计+置信区间）、排队论(M/M/1)、元胞自动机。
  图：分布直方图、收敛。
  **⛔ 审核重点**：收敛诊断、置信区间合理性、重复次数 ≥ 1000

---

## 机器学习（sklearn 完整族谱）

> 中文文档：https://scikit-learn.org.cn/ | 官方：https://scikit-learn.org/

### ⛔ 算法选择决策树（先看这个）

```
拿到数据集 → 回答三个问题：

Q1: 有标签吗？
  ├─ 无标签 → 无监督学习
  │    ├─ 想分群？ → KMeans / DBSCAN / 层次聚类
  │    └─ 想降维？ → PCA / t-SNE
  │
  └─ 有标签 → Q2: 标签是连续值还是类别？
       ├─ 连续值（回归）→ Q3a
       └─ 类别（分类）→ Q3b

Q3a (回归): 特征和标签大致线性？
  ├─ 是 + 需可解释 → 线性回归 / 岭回归 / Lasso
  ├─ 是 + 特征多 → 岭回归（防多重共线性）
  ├─ 否 + 样本<1000 → 随机森林回归 / SVR
  └─ 否 + 样本>1000 + 要精度 → XGBoost / GBDT

Q3b (分类): 需要强可解释性？
  ├─ 是 → 逻辑回归 / 决策树（单棵，可视化）
  ├─ 否 + 追求精度 → 随机森林 / XGBoost
  ├─ 高维稀疏(文本) → 朴素贝叶斯
  └─ 中小规模 + 边界清晰 → SVM
```

---

### 回归算法（预测连续值）

#### 1. 线性回归 `LinearRegression`
```python
from sklearn.linear_model import LinearRegression
model = LinearRegression().fit(X_train, y_train)
```
- **何时用**：特征与目标近似线性；需要可解释系数；作为基线模型
- **何时不用**：非线性关系强；多重共线性严重（→ 改用岭回归）；异常值多
- **审核重点**：R² ≥ 0.5、残差正态性、VIF < 10（无严重共线性）
- **图**：实际 vs 预测散点图 + 残差分布直方图

#### 2. 岭回归 `Ridge`
```python
from sklearn.linear_model import Ridge
model = Ridge(alpha=1.0).fit(X_train, y_train)
```
- **何时用**：特征数多或有共线性；需要正则化防过拟合；样本量 < 特征数
- **审核重点**：alpha 参数通过交叉验证选择 `RidgeCV`
- **与线性回归的关键区别**：加 L2 正则项 → 系数收缩但不归零 → 所有特征都保留

#### 3. Lasso `Lasso`
```python
from sklearn.linear_model import Lasso
model = Lasso(alpha=0.1).fit(X_train, y_train)
```
- **何时用**：需要自动特征选择；高维稀疏场景（特征很多但只有少数重要）
- **审核重点**：alpha 通过 `LassoCV` 选择；非零系数个数合理
- **与岭回归的关键区别**：L1 正则 → 不重要特征的系数直接归零 → 内置特征选择

#### 4. 随机森林回归 `RandomForestRegressor`
```python
from sklearn.ensemble import RandomForestRegressor
model = RandomForestRegressor(n_estimators=100, random_state=42).fit(X, y)
```
- **何时用**：非线性关系；特征交互复杂；需要一个"稳"的默认回归模型
- **审核重点**：n_estimators ≥ 100、输出特征重要性（`feature_importances_`）
- **图**：特征重要性条形图 + 实际 vs 预测散点图

#### 5. GBDT 回归 `GradientBoostingRegressor`
```python
from sklearn.ensemble import GradientBoostingRegressor
model = GradientBoostingRegressor(n_estimators=200, learning_rate=0.1).fit(X, y)
```
- **何时用**：追求最高回归精度；样本量 > 500
- **审核重点**：learning_rate 和 n_estimators 联动调参（小学习率 + 大树数）、防止过拟合（早停）
- **图**：学习曲线（训练/验证误差随树数变化）

---

### 分类算法（预测类别）

#### 6. 逻辑回归 `LogisticRegression`
```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(max_iter=1000).fit(X_train, y_train)
```
- **何时用**：二分类基线模型；需要输出概率（不只是类别）；需强可解释性
- **何时不用**：多类别且类别极不平衡（→ 用随机森林）；非线性边界清晰（→ SVM）
- **审核重点**：AUC ≥ 0.7、混淆矩阵无严重偏向
- **图**：`roc_curve_plot` + 混淆矩阵 `heatmap`

#### 7. 随机森林分类 `RandomForestClassifier`
```python
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_estimators=100, random_state=42).fit(X, y)
```
- **何时用**：多分类问题；特征重要性分析；不确定用什么分类器时的默认选择
- **审核重点**：n_estimators ≥ 100、类别权重 `class_weight='balanced'`（不平衡时）
- **图**：特征重要性 + 混淆矩阵 + ROC

#### 8. 支持向量机 SVM `SVC`
```python
from sklearn.svm import SVC
model = SVC(kernel='rbf', C=1.0, probability=True).fit(X_train, y_train)
```
- **何时用**：中小规模数据（<10000 样本）；类别边界需要复杂分割；特征维度高
- **何时不用**：样本量大（训练慢）；需要概率输出（需要额外 `probability=True`）
- **审核重点**：C 和 gamma 通过网格搜索调优；数据先做标准化
- **图**：决策边界图（仅 2 特征时）+ ROC

#### 9. 朴素贝叶斯 `GaussianNB` / `MultinomialNB`
```python
from sklearn.naive_bayes import GaussianNB, MultinomialNB
model = GaussianNB().fit(X_train, y_train)        # 连续特征
model = MultinomialNB().fit(X_train, y_train)     # 离散/文本特征
```
- **何时用**：文本分类（MultinomialNB）；特征独立性假设近似成立；需要快速基线
- **审核重点**：特征独立性检验（至少做相关性分析）

---

### 聚类算法（无监督分群）

#### 10. K-Means `KMeans`
```python
from sklearn.cluster import KMeans
model = KMeans(n_clusters=3, random_state=42, n_init=10).fit(X)
labels = model.labels_
```
- **何时用**：数据探索第一步；簇形状近似球形；需要快速得到分群结果
- **何时不用**：簇形状不规则（→ DBSCAN）；簇数量未知（→ 肘部法则 + 轮廓系数辅助选 K）
- **审核重点**：K 值通过肘部法则 + 轮廓系数确定；多次运行结果稳定
- **图**：肘部曲线 + 轮廓系数图 + 散点着色图

#### 11. DBSCAN `DBSCAN`
```python
from sklearn.cluster import DBSCAN
model = DBSCAN(eps=0.5, min_samples=5).fit(X)
```
- **何时用**：簇形状任意；需要识别噪声点（标签=-1）；城市地理聚类、异常检测
- **何时不用**：数据密度差异大（eps 难选）；高维数据（距离失效）
- **审核重点**：eps 通过 k-distance 图选择

#### 12. 层次聚类 `AgglomerativeClustering`
```python
from sklearn.cluster import AgglomerativeClustering
model = AgglomerativeClustering(n_clusters=3).fit(X)
```
- **何时用**：需要层次结构（大类包含小类）；样本量 < 10000
- **审核重点**：linkage 方法选择（ward/average/complete）
- **图**：`dendrogram_plot` 树状图

---

### 降维算法

#### 13. PCA `PCA`
```python
from sklearn.decomposition import PCA
pca = PCA(n_components=0.95)     # 保留 95% 方差
X_reduced = pca.fit_transform(X)
```
- **何时用**：特征数多（>20）、特征间强相关、需要可视化（降到 2D/3D）
- **审核重点**：KMO 检验 > 0.6、累计方差解释率 > 80%
- **图**：碎石图 + 累计方差解释率图 + `scatter_3d`（前3主成分）

---

### 模型验证与调参

#### 14. 交叉验证 `cross_val_score`
```python
from sklearn.model_selection import cross_val_score, KFold
scores = cross_val_score(model, X, y, cv=KFold(n_splits=5, shuffle=True, random_state=42))
print(f"CV Accuracy: {scores.mean():.3f} ± {scores.std():.3f}")
```
- **铁律**：任何 ML 模型必须报告交叉验证分数（非训练集分数）
- **时间序列特殊要求**：`TimeSeriesSplit`（不可随机打乱时间顺序）

#### 15. 网格搜索 `GridSearchCV`
```python
from sklearn.model_selection import GridSearchCV
param_grid = {'n_estimators': [50, 100, 200], 'max_depth': [None, 10, 20]}
search = GridSearchCV(RandomForestRegressor(random_state=42), param_grid, cv=5).fit(X, y)
```
- **何时用**：关键模型需要最优超参（在论文中声明调优过程）
- **审核重点**：报告最佳参数组合和对应的 CV 分数

---

### ⛔ ML 通用审核清单

1. 训练/测试分离（时间序列必须时序分割，不可随机打乱）
2. 样本量 ≥ 特征数 × 10（基本统计要求）
3. 是否报告了验证集指标而非训练集指标（训练集指标无意义）
4. 超参调优方式是否声明（GridSearchCV / RandomizedSearchCV）
5. 数据是否标准化（SVM、KMeans、神经网络必须标准化）
6. 类别不平衡是否处理（`class_weight='balanced'` 或 SMOTE 过采样）
7. 特征是否做了筛选（移除方差为 0 的特征、强相关特征去重）
8. 随机种子是否固定（`random_state=42`）

---

## 每个模型都要有的三件套

1. **灵敏度分析**（`sensitivity_tornado`）——参数扰动看结果稳不稳
2. **误差/精度**——与真值或交叉验证比
3. **结果解读**——数字背后的现实含义
4. **⛔ 算法正确性自证**——关键数字的代码出处要能追溯（变量名+行号）
