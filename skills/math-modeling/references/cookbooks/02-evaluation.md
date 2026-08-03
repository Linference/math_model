# 02 — 评价决策算法手册

**目的**：从数据到排序，一站式解决多指标评价问题。每个方法包含：步骤、公式、代码、归一化选择、常见坑。

---

## 问题→算法速查表

| 问题特征 | 推荐算法 | 权重来源 |
|---|---|---|
| 指标间可两两比较，有专家判断 | AHP（层次分析法） | 主观（判断矩阵） |
| 有原始数据，权重未知 | 熵权法 → TOPSIS | 客观（数据驱动） |
| 有原始数据 + 权重已知 | TOPSIS | 外部给定 |
| 小样本、贫信息 | 灰色关联分析 (GRA) | 外部给定或等权 |
| 指标含模糊概念（"较好""较差"） | 模糊综合评价 | 主观或熵权 |
| 需要妥协解（最大化群体效用 + 最小化个体遗憾） | VIKOR | 外部给定 |
| 需要超越关系（优于/劣于/不可比） | ELECTRE | 外部给定 |

---

## 一、归一化方法速查

| 方法 | 公式 | 适用场景 | 方向 |
|---|---|---|---|
| 极差归一化 (Min-Max) | $x' = \frac{x - x_{\min}}{x_{\max} - x_{\min}}$ | 最常用 | 正向/负向分别处理 |
| 向量归一化 | $x' = x / \sqrt{\sum x_i^2}$ | TOPSIS 标准做法 | 无方向性 |
| Z-score | $x' = \frac{x - \mu}{\sigma}$ | 统计背景 | 允许负值 |
| 比重法 | $x' = x / \sum x_i$ | 和为 1 约束 | 全正数 |

```python
import numpy as np

def normalize_minmax(X, benefit_cols=None, cost_cols=None):
    """X: (n_samples, n_features). benefit_cols: 正向指标列索引, cost_cols: 负向指标列索引"""
    X_norm = np.zeros_like(X, dtype=float)
    if benefit_cols is None:
        benefit_cols = list(range(X.shape[1]))
    if cost_cols is None:
        cost_cols = []
    for j in benefit_cols:
        X_norm[:, j] = (X[:, j] - X[:, j].min()) / (X[:, j].max() - X[:, j].min() + 1e-10)
    for j in cost_cols:
        X_norm[:, j] = (X[:, j].max() - X[:, j]) / (X[:, j].max() - X[:, j].min() + 1e-10)
    return X_norm

def normalize_vector(X):
    """向量归一化，TOPSIS 标准"""
    return X / np.sqrt((X**2).sum(axis=0))
```

---

## 二、AHP（层次分析法）

### 步骤

1. **建立层次结构**：目标层 → 准则层 → 方案层
2. **构造判断矩阵** $A = (a_{ij})$，$a_{ij}$ 表示指标 i 相对 j 的重要性（1-9 标度）
3. **计算权重**：特征向量法（或几何平均法）
4. **一致性检验**：CR < 0.1 通过

### Saaty 1-9 标度

| 标度 | 含义 |
|---|---|
| 1 | 同等重要 |
| 3 | 稍微重要 |
| 5 | 明显重要 |
| 7 | 强烈重要 |
| 9 | 极端重要 |
| 2,4,6,8 | 中间值 |

### 代码骨架

```python
import numpy as np

def ahp(A):
    """
    A: 判断矩阵 (n,n)，需满足正互反性 a_ij = 1/a_ji
    返回: 权重向量, λ_max, CI, CR
    """
    n = A.shape[0]
    # 方法1: 特征向量法
    eigvals, eigvecs = np.linalg.eig(A)
    max_idx = np.argmax(eigvals.real)
    w = eigvecs[:, max_idx].real
    w = w / w.sum()  # 归一化

    # 方法2 (备选): 几何平均法
    # w_geo = np.exp(np.log(A).mean(axis=1))
    # w_geo = w_geo / w_geo.sum()

    lambda_max = eigvals[max_idx].real
    CI = (lambda_max - n) / (n - 1)

    # RI 随机一致性指数 (n=1..15)
    RI_table = {1:0, 2:0, 3:0.58, 4:0.90, 5:1.12, 6:1.24, 7:1.32,
                8:1.41, 9:1.45, 10:1.49, 11:1.51, 12:1.54, 13:1.56, 14:1.58, 15:1.59}
    CR = CI / RI_table.get(n, 1.59) if n > 2 else 0

    return w, lambda_max, CI, CR

# 示例
A_matrix = np.array([
    [1,   3,   5],
    [1/3, 1,   2],
    [1/5, 1/2, 1]
])
w, lam, CI, CR = ahp(A_matrix)
print(f"权重: {w}")
print(f"λ_max={lam:.4f}, CI={CI:.4f}, CR={CR:.4f}, {'通过' if CR < 0.1 else '未通过!!!'}")
```

### 多级 AHP（准则层→子准则层→方案层）

```python
def hierarchical_ahp(level_matrices):
    """level_matrices: 各级判断矩阵列表，[准则层矩阵, 子准则层矩阵1, ...]
    返回: 全局权重"""
    w_level0, *_ = ahp(level_matrices[0])  # 目标→准则
    global_weights = []
    offset = 1
    for i, w_i in enumerate(w_level0):
        sub_w, *_ = ahp(level_matrices[offset + i])
        global_weights.append(w_i * sub_w)
    return np.concatenate(global_weights)
```

### ⛔ AHP 最易出错的点

1. **CR ≥ 0.1 仍使用**：必须调整判断矩阵，不可"差不多就行"。调整策略：检查偏离最大的 a_ij，请专家重判
2. **特征向量法与几何平均法混用**：必须统一声明使用哪种
3. **全局权重恰好等于 100.00%**：舍入误差必然存在，刚好等于 100 可能是人为凑整
4. **必须报告**：λ_max、CI、CR 三个值
5. **判断矩阵不满足正互反性**：必须检查 `a_ij ≈ 1/a_ji`

---

## 三、熵权法

### 原理

信息熵越小 → 指标变异程度越大 → 包含信息越多 → 权重越大。

### 步骤

1. 数据归一化（极差法）
2. 计算第 j 项指标的熵值：$e_j = -k \sum_{i=1}^n p_{ij} \ln p_{ij}$，其中 $p_{ij} = x'_{ij} / \sum_i x'_{ij}$，$k = 1/\ln n$
3. 计算权重：$w_j = (1 - e_j) / \sum (1 - e_j)$

```python
def entropy_weight(X_norm):
    """X_norm: 已归一化到 [0,1] 的数据矩阵 (n_samples, n_features)"""
    n = X_norm.shape[0]
    # 避免 log(0)
    X_norm = np.clip(X_norm, 1e-10, 1)
    P = X_norm / X_norm.sum(axis=0)
    k = 1.0 / np.log(n)
    e = -k * np.sum(P * np.log(P), axis=0)
    w = (1 - e) / (1 - e).sum()
    return w
```

### 常见坑
1. 熵权法只反映数据差异程度，不反映指标实际重要性
2. 样本量太少时熵权不稳定（n < 10 慎用）
3. 常与 TOPSIS 组合使用：熵权定权 → TOPSIS 排序

---

## 四、TOPSIS

### 步骤

1. 向量归一化原始数据
2. 用权重矩阵加权：$z_{ij} = w_j \cdot r_{ij}$
3. 确定正理想解 $Z^+$（各指标最优值）和负理想解 $Z^-$（各指标最劣值）
4. 计算各方案与正负理想解的距离：$D_i^+ = \sqrt{\sum (z_{ij} - z_j^+)^2}$
5. 计算相对贴近度：$C_i = D_i^- / (D_i^+ + D_i^-)$
6. 按 $C_i$ 降序排列

```python
def topsis(X, w, benefit_cols):
    """
    X: 原始数据矩阵 (n_samples, n_features)
    w: 权重向量
    benefit_cols: 正向指标列索引
    """
    n, m = X.shape
    # Step 1: 向量归一化
    X_norm = X / np.sqrt((X**2).sum(axis=0))
    # Step 2: 加权
    Z = X_norm * w
    # Step 3: 正负理想解
    Z_pos = np.zeros(m)
    Z_neg = np.zeros(m)
    for j in range(m):
        if j in benefit_cols:
            Z_pos[j] = Z[:, j].max()
            Z_neg[j] = Z[:, j].min()
        else:
            Z_pos[j] = Z[:, j].min()
            Z_neg[j] = Z[:, j].max()
    # Step 4: 距离
    D_pos = np.sqrt(((Z - Z_pos)**2).sum(axis=1))
    D_neg = np.sqrt(((Z - Z_neg)**2).sum(axis=1))
    # Step 5: 贴近度
    C = D_neg / (D_pos + D_neg + 1e-10)
    return C

# 熵权+TOPSIS 组合
# w = entropy_weight(normalize_minmax(X, benefit_cols))
# scores = topsis(X, w, benefit_cols)
```

### ⛔ TOPSIS 逆序问题

**新增或删除候选方案会导致原有方案的排序变化**，这是 TOPSIS 的固有缺陷。必须在论文中：
1. 声明存在逆序风险
2. 做敏感性测试（随机删除一个方案，检查前 3 名是否变化）
3. 如变化 > 1 个名次，讨论其影响

### 常见坑
1. 归一化方式不一致：TOPSIS 标准用向量归一化，与熵权法的极差归一化不同。如组合使用：熵权用极差归一化算权重 → TOPSIS 用向量归一化算评分
2. 权重 ±20% 扰动分析未做
3. 距离公式未加平方根

---

## 五、灰色关联分析 (GRA)

### 适用：小样本（n < 30）、贫信息、不确定性问题

```python
def gra(X, w=None, rho=0.5):
    """
    X: (n_samples, n_features), 所有指标需正向化
    w: 权重向量，默认等权
    rho: 分辨系数，通常 0.5
    """
    n, m = X.shape
    if w is None:
        w = np.ones(m) / m
    # 归一化 (极差)
    X_norm = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0) + 1e-10)
    # 参考序列 (最优)
    ref = X_norm.max(axis=0)
    # 关联系数
    diff = np.abs(X_norm - ref)
    xi = (diff.min() + rho * diff.max()) / (diff + rho * diff.max() + 1e-10)
    # 关联度
    gamma = (xi * w).sum(axis=1)
    return gamma
```

---

## 六、模糊综合评价

### 步骤

1. 确定评价因素集 U 和评语集 V（如 {优, 良, 中, 差}）
2. 构造隶属度矩阵 R：每个因素对每个评语的隶属度
3. 确定因素权重 W（AHP 或熵权）
4. 模糊合成：B = W × R（取 max-min 或加权平均）
5. 按最大隶属度原则确定等级

```python
def fuzzy_eval(W, R):
    """
    W: 权重向量 (1, n)
    R: 隶属度矩阵 (n, m)，n 个因素，m 个评语等级
    返回: 综合评价向量 B (1, m)
    """
    # 加权平均型算子（推荐，信息利用充分）
    B = W @ R
    # 最大隶属度原则
    grade = np.argmax(B)
    return B, grade

# 示例
W = np.array([0.3, 0.4, 0.3])
R = np.array([[0.5, 0.3, 0.2, 0],    # 因素1 对各评语的隶属度
              [0.1, 0.4, 0.4, 0.1],  # 因素2
              [0.2, 0.3, 0.3, 0.2]]) # 因素3
B, grade = fuzzy_eval(W, R)
```

### 常见坑
1. **算子选择不当**：max-min 算子信息损失大，推荐加权平均型
2. **隶属度构造无依据**：必须说明隶属度函数（梯形/三角形）的选择理由

---

## 七、VIKOR（折中妥协法）

### 适用：决策者希望同时考虑群体最大效用和个体最小遗憾

```python
def vikor(X, w, benefit_cols, v=0.5):
    """v 是决策机制系数：v>0.5 偏群体效用，v<0.5 偏个体遗憾，v=0.5 折中"""
    n, m = X.shape
    # 归一化
    f_best = np.zeros(m); f_worst = np.zeros(m)
    for j in range(m):
        f_best[j] = X[:, j].max() if j in benefit_cols else X[:, j].min()
        f_worst[j] = X[:, j].min() if j in benefit_cols else X[:, j].max()

    # S: 群体效用 (加权Manhattan距离), R: 个体遗憾 (最大加权Chebyshev距离)
    S = np.zeros(n); R = np.zeros(n)
    for i in range(n):
        for j in range(m):
            d = w[j] * (f_best[j] - X[i, j]) / (f_best[j] - f_worst[j] + 1e-10)
            S[i] += d
            R[i] = max(R[i], d)

    S_best, S_worst = S.min(), S.max()
    R_best, R_worst = R.min(), R.max()
    Q = v * (S - S_best)/(S_worst - S_best) + (1-v) * (R - R_best)/(R_worst - R_best)
    return Q  # 越小越好

# 可接受优势条件: Q(第二) - Q(第一) >= 1/(n-1)
# 可接受稳定性条件: 排序第一的方案同时在 S 或 R 中排第一
```

---

## 八、ELECTRE（淘汰与选择转换法）

### 核心思想：超越关系。方案 a 超越方案 b 当且仅当"多数指标支持 a≥b"且"无指标强烈反对"

步骤摘要（详见专业文献）：
1. 构造一致度矩阵和反对度矩阵
2. 设定一致度阈值和反对度阈值
3. 构建超越关系图
4. 核分析或净优势值排序

---

## 评价算法通用审核清单

1. 指标方向统一（正向化处理已完成）
2. 归一化方式已声明并统一
3. 权重来源有依据（主观=专家+一致性，客观=数据+样本量）
4. 逆序问题已讨论（至少 TOPSIS）
5. 权重灵敏度分析（±20%，前 3 名排序稳定性）
6. 至少与另一种评价方法对比（如 AHP 结果 vs 熵权-TOPSIS 结果）
7. 结果解读：不仅报排名，要解释"为什么第一"

### 常见全局坑
1. **评分标准与指标方向矛盾**：某些指标越大越好，某些越小越好 → 未统一正向化
2. **单一方法报告**：无对比 → 说服力弱
3. **排序相差不大但解读夸大**：贴近度仅差 0.002 就"显著优于" → 应做显著性检验
