# 05 — 统计与机器学习手册

**目的**：从假设检验到聚类降维，一站式解决数据驱动的推断和探索问题。每个方法包含：假设条件、检验选择、scipy/sklearn 代码、结果解读模板、常见误用。

---

## 问题→算法速查表

| 问题特征 | 推荐方法 | 工具包 |
|---|---|---|
| 比较两组均值差异 | 独立样本 t 检验 | `scipy.stats.ttest_ind` |
| 比较两组配对数据差异 | 配对 t 检验 | `scipy.stats.ttest_rel` |
| 比较 ≥3 组均值差异 | 单因素 ANOVA | `scipy.stats.f_oneway` |
| 检验分类变量独立性 | 卡方检验 | `scipy.stats.chi2_contingency` |
| 检验分布形态 | Kolmogorov-Smirnov / Shapiro-Wilk | `scipy.stats.kstest` / `shapiro` |
| 发现数据自然分组 | KMeans / DBSCAN / 层次聚类 | `sklearn.cluster` |
| 降维到 2D/3D 可视化 | PCA / t-SNE | `sklearn.decomposition.PCA` / `sklearn.manifold.TSNE` |
| 更新先验信念 → 后验 | 贝叶斯推断 | `pymc` / `scipy.stats.beta` (共轭) |
| 事件发生时间分析 | 生存分析 (Kaplan-Meier / Cox) | `lifelines` |

---

## 一、假设检验

### 检验选择决策树

```
数据类型？
├─ 连续 → 问题是什么？
│    ├─ 一个样本 vs 已知值 → 单样本 t 检验
│    ├─ 两个独立样本 → 问题？
│    │    ├─ 均值差 → ttest_ind（需方差齐性，否则 Welch t）
│    │    └─ 分布同 → Mann-Whitney U（非参数）
│    ├─ 两个配对样本 → ttest_rel
│    └─ 三个及以上样本 → ANOVA（需正态+方差齐性，否则 Kruskal-Wallis）
│
├─ 分类 → 问题是什么？
│    ├─ 拟合优度（观测 vs 期望）→ 卡方拟合优度
│    ├─ 独立性（列联表）→ 卡方独立性检验
│    └─ 比例 → z 检验 / 精确二项检验
│
└─ 相关 → Spearman（非参数）/ Pearson（需正态）
```

### 前置检验（用哪个 t 检验？）

```python
from scipy.stats import shapiro, levene, ttest_ind

# 1. 正态性检验
stat, p = shapiro(data)
print(f"Shapiro-Wilk: p={p:.4f} {'→ 正态' if p > 0.05 else '→ 拒绝正态'}")

# 2. 方差齐性检验
stat, p = levene(group1, group2)
print(f"Levene: p={p:.4f} {'→ 方差齐' if p > 0.05 else '→ 方差不齐，用 Welch t'}")

# 3. 选择并执行 t 检验
if p_levene > 0.05:
    stat, p = ttest_ind(group1, group2, equal_var=True)
else:
    stat, p = ttest_ind(group1, group2, equal_var=False)  # Welch's t-test
```

### 代码骨架

```python
from scipy import stats
import numpy as np

# ---- t 检验 ----
t_stat, p_value = stats.ttest_ind(group_a, group_b)
print(f"t = {t_stat:.4f}, p = {p_value:.4f}")

# ---- 配对 t 检验 ----
t_stat, p_value = stats.ttest_rel(before, after)

# ---- 单因素 ANOVA ----
f_stat, p_value = stats.f_oneway(group1, group2, group3)

# ---- 卡方独立性检验 ----
# 列联表: [[a, b], [c, d]]
chi2, p_value, dof, expected = stats.chi2_contingency(observed_table)

# ---- 非参数替代 ----
# Mann-Whitney U (替代独立 t)
u_stat, p_value = stats.mannwhitneyu(group_a, group_b, alternative='two-sided')
# Kruskal-Wallis (替代 ANOVA)
h_stat, p_value = stats.kruskal(group1, group2, group3)
# Wilcoxon (替代配对 t)
w_stat, p_value = stats.wilcoxon(before, after)
```

### 结果解读模板

```
"独立样本 t 检验显示，实验组 (M=72.3, SD=8.5) 与对照组 (M=65.1, SD=9.2)
之间存在显著差异，t(58)=3.21，p=0.002<0.05，Cohen's d=0.82（大效应）。
因此拒绝 H₀，接受 H₁：实验处理对因变量有显著正向影响。"
```

### 效应量 (Effect Size)

```python
def cohens_d(group1, group2):
    """Cohen's d: 0.2 小, 0.5 中, 0.8 大"""
    diff = np.mean(group1) - np.mean(group2)
    pooled_std = np.sqrt((np.var(group1, ddof=1) + np.var(group2, ddof=1)) / 2)
    return diff / pooled_std
```

### ⛔ p 值常见误用

1. **p-hacking**：跑 20 个检验，只报告 p < 0.05 的那个 → 必须做多重比较校正（Bonferroni / FDR）
2. **p > 0.05 当"无差异"**：p > 0.05 只能说不拒绝 H₀，不能证明 H₀ 成立
3. **大样本下 p 值必然显著**：n > 10000 时几乎任何微小差异都 p < 0.05 → 必须报告效应量
4. **p 值大小不代表效应大小**：p < 0.0001 但效应可忽略不计
5. **单尾 vs 双尾**：事后换单尾检验 → 严重违规

---

## 二、回归诊断

### 完整诊断流程

```python
import statsmodels.api as sm
import numpy as np

# 拟合
X_with_const = sm.add_constant(X)
model = sm.OLS(y, X_with_const).fit()
print(model.summary())

# 诊断 1: 残差正态性
from scipy.stats import shapiro
stat, p = shapiro(model.resid)

# 诊断 2: 多重共线性 (VIF)
from statsmodels.stats.outliers_influence import variance_inflation_factor
vif_data = {f"X{i}": variance_inflation_factor(X, i) for i in range(X.shape[1])}
# VIF > 10 → 严重共线性, VIF > 5 → 需关注

# 诊断 3: 异方差性 (Breusch-Pagan)
from statsmodels.stats.diagnostic import het_breuschpagan
bp_test = het_breuschpagan(model.resid, X_with_const)
# p < 0.05 → 存在异方差 → 用稳健标准误

# 诊断 4: Durbin-Watson（自相关）
dw = sm.stats.durbin_watson(model.resid)
# 接近 2 → 无自相关; < 1 或 > 3 → 严重自相关
```

### 常见坑

1. **R² 高就认为模型好**：过度关注 R² 而忽略残差诊断
2. **多重共线性不管**：VIF > 10 的变量直接删或合并
3. **异方差无视**：标准误偏小 → 假阳性 → 用 `HC3` 稳健标准误
4. **高杠杆点/异常值不清除**：Cook's distance 标记极端影响点

---

## 三、聚类

### K-Means

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# 1. 必须标准化！
X_scaled = StandardScaler().fit_transform(X)

# 2. 肘部法则选 K
inertias = []
K_range = range(1, 11)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_scaled)
    inertias.append(km.inertia_)
# 画 inertia vs K 曲线，找"肘部"

# 3. 轮廓系数辅助验证
from sklearn.metrics import silhouette_score
silhouettes = []
for k in range(2, 11):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    silhouettes.append(silhouette_score(X_scaled, labels))
best_k = np.argmax(silhouettes) + 2

# 4. 最终模型
model = KMeans(n_clusters=best_k, random_state=42, n_init=10)
labels = model.fit_predict(X_scaled)
```

### DBSCAN

```python
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors

# k-distance 图定 eps
nn = NearestNeighbors(n_neighbors=5)
nn.fit(X_scaled)
distances = np.sort(nn.kneighbors()[0][:, -1])
# 找距离曲线的"拐点"作为 eps

db = DBSCAN(eps=0.5, min_samples=5)
labels = db.fit_predict(X_scaled)
n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
n_noise = (labels == -1).sum()
print(f"聚类数: {n_clusters}, 噪声点数: {n_noise}")
```

### 层次聚类

```python
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage

# 树状图
Z = linkage(X_scaled, method='ward')
dendrogram(Z)

# 模型
model = AgglomerativeClustering(n_clusters=3, linkage='ward')
labels = model.fit_predict(X_scaled)
```

### 聚类选择决策

| 特征 | K-Means | DBSCAN | 层次聚类 |
|---|---|---|---|
| 簇形状 | 球形 | 任意 | 任意 |
| 噪声处理 | 无 | 有 | 无 |
| 需预知 K | 是 | 否 | 是 |
| 大数据友好 | 是 | 中等 | 否 (>10000) |
| 高维友好 | 中等 | 差（距离失效） | 中等 |

### 常见坑
1. **不标准化直接 KMeans**：量纲大的特征主导聚类
2. **不看轮廓系数就定 K**：随便设 K=3
3. **DBSCAN 的 eps 乱设**：不用 k-distance 图
4. **聚类结果过度解读**：聚类只是探索工具，不是"发现真理"

---

## 四、降维

### PCA

```python
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

X_scaled = StandardScaler().fit_transform(X)

# 保留 95% 方差
pca = PCA(n_components=0.95)
X_pca = pca.fit_transform(X_scaled)
print(f"{pca.n_components_} 个主成分保留了 {pca.explained_variance_ratio_.sum()*100:.1f}% 方差")

# 载荷矩阵（各原始特征对各主成分的贡献）
loadings = pca.components_.T * np.sqrt(pca.explained_variance_)

# KMO 和 Bartlett 检验（判断是否适合 PCA）
from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity
kmo_all, kmo_model = calculate_kmo(X_scaled)
chi2, p = calculate_bartlett_sphericity(X_scaled)
print(f"KMO = {kmo_model:.4f} {'(≥0.6 适合)' if kmo_model >= 0.6 else '(不适合)'}")
print(f"Bartlett p={p:.4f} {'(适合)' if p < 0.05 else '(不适合)'}")
```

### t-SNE（仅用于可视化，不用于特征提取）

```python
from sklearn.manifold import TSNE
tsne = TSNE(n_components=2, perplexity=30, random_state=42)
X_tsne = tsne.fit_transform(X_scaled)
# 注意: t-SNE 仅反映相对距离，轴无物理意义
```

### 常见坑
1. **PCA 不做 KMO**：数据不相关 → PCA 无意义
2. **t-SNE 用于特征工程**：t-SNE 不可逆，不能 transform 新数据
3. **不标准化**：PCA 对方差敏感，必须标准化

---

## 五、贝叶斯推断

### Beta-Binomial 共轭（最简）

```python
from scipy.stats import beta
import numpy as np

# 先验: Beta(α=2, β=2)，即认为概率约 0.5，但不确定
# 数据: 10 次试验 7 次成功
# 后验: Beta(α+successes, β+failures) = Beta(9, 5)

a_prior, b_prior = 2, 2
successes, failures = 7, 3
a_post = a_prior + successes
b_post = b_prior + failures

x = np.linspace(0, 1, 200)
prior_pdf = beta.pdf(x, a_prior, b_prior)
post_pdf = beta.pdf(x, a_post, b_post)

# MAP 估计
map_estimate = (a_post - 1) / (a_post + b_post - 2)
# 95% 可信区间
ci_lower = beta.ppf(0.025, a_post, b_post)
ci_upper = beta.ppf(0.975, a_post, b_post)

print(f"后验均值 = {a_post/(a_post+b_post):.3f}, 95% CI = [{ci_lower:.3f}, {ci_upper:.3f}]")
```

### 复杂模型用 PyMC

```python
# import pymc as pm
# with pm.Model() as model:
#     mu = pm.Normal('mu', mu=0, sigma=10)
#     sigma = pm.HalfNormal('sigma', sigma=1)
#     y = pm.Normal('y', mu=mu, sigma=sigma, observed=data)
#     trace = pm.sample(2000, return_inferencedata=True)
```

---

## 六、生存分析

```python
from lifelines import KaplanMeierFitter, CoxPHFitter
import pandas as pd

# Kaplan-Meier 估计
kmf = KaplanMeierFitter()
kmf.fit(durations=df['time'], event_observed=df['event'])
kmf.plot()  # 生存曲线 + 置信区间
median = kmf.median_survival_time_

# Log-rank 检验（两组生存曲线比较）
from lifelines.statistics import logrank_test
result = logrank_test(group_a_times, group_b_times,
                      event_observed_A=group_a_events, event_observed_B=group_b_events)
print(f"Log-rank: p = {result.p_value:.4f}")

# Cox 比例风险模型
cph = CoxPHFitter()
cph.fit(df, duration_col='time', event_col='event')
cph.print_summary()  # 各协变量的 HR (风险比) 和 p 值
# HR > 1 → 风险增大，HR < 1 → 保护因素
```

---

## ML/统计通用审核清单

1. 训练/测试严格分离（时序 = TimeSeriesSplit）
2. 数据标准化（SVM/KMeans/PCA/神经网络 必须做）
3. 类别不平衡已处理（class_weight / SMOTE）
4. 随机种子固定 `random_state=42`
5. 交叉验证分数已报告（非训练集分数）
6. p 值多重比较已校正
7. 效应量已报告（非仅 p 值）
8. 特征无数据泄露（归一化前分离训练/测试）

### 常见全局坑
1. **数据泄露**：先标准化再分训练/测试 → 测试集信息泄露到训练集
2. **p-hacking**：不做多重比较校正
3. **相关性当因果**：回归系数显著 ≠ 因果关系
4. **不做诊断直接建模**：残差不正态、异方差、共线全不管
5. **过拟合不自知**：训练集 R²=0.99，测试集 R²=0.3
