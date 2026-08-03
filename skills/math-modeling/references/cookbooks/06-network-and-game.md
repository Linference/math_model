# 06 — 网络与博弈论手册

**目的**：从图论算法到博弈均衡，一站式解决网络结构分析和策略交互问题。每个方法包含：问题识别、networkx/cvxpy 代码骨架、结果解读。

---

## 问题→算法速查表

| 问题特征 | 推荐方法 | 核心工具 |
|---|---|---|
| 找两点间最短路径 | Dijkstra / A* | `networkx.dijkstra_path` |
| 所有点对间最短路径 | Floyd-Warshall / Johnson | `networkx.floyd_warshall` |
| 连通网络的最小成本 | 最小生成树 (MST) | `networkx.minimum_spanning_tree` |
| 从源到汇的最大流量 | 最大流 (Ford-Fulkerson / Edmonds-Karp) | `networkx.maximum_flow` |
| 最小成本满足流量需求 | 最小费用最大流 | `networkx.min_cost_flow` |
| 节点重要性排名 | PageRank / 中心性 | `networkx.pagerank` / `betweenness_centrality` |
| 旅行商问题（小规模） | 精确/启发式 TSP | `networkx.approximation.traveling_salesman_problem` |
| 两人/多人策略交互 | 博弈论 | `nashpy` / `cvxpy` / 自实现 |
| 传播/扩散动态 | SIR / SEIR 网络传播 | `networkx` + `solve_ivp` |

---

## 一、图论基础操作

### 建图

```python
import networkx as nx
import numpy as np

# 方式1: 逐边添加
G = nx.Graph()           # 无向图
# G = nx.DiGraph()       # 有向图
G.add_edges_from([(1,2,{'weight':5}), (2,3,{'weight':3}),
                  (3,4,{'weight':2}), (4,1,{'weight':7})])

# 方式2: 从邻接矩阵
adj = np.array([[0,5,0,7], [5,0,3,0], [0,3,0,2], [7,0,2,0]])
G = nx.from_numpy_array(adj)

# 方式3: 从边列表 CSV
import pandas as pd
edges = pd.read_csv('edges.csv')
G = nx.from_pandas_edgelist(edges, source='from', target='to', edge_attr='weight')
```

### 基本属性

```python
print(f"节点数: {G.number_of_nodes()}, 边数: {G.number_of_edges()}")
print(f"连通分量数: {nx.number_connected_components(G)}")
print(f"平均度: {2*G.number_of_edges()/G.number_of_nodes():.2f}")
print(f"平均聚类系数: {nx.average_clustering(G):.4f}")
print(f"平均最短路径: {nx.average_shortest_path_length(G):.4f}")  # 需连通
```

---

## 二、最短路径

### Dijkstra（非负权）

```python
# 单源最短路径
path = nx.dijkstra_path(G, source=1, target=5, weight='weight')
length = nx.dijkstra_path_length(G, source=1, target=5, weight='weight')
print(f"最短路径: {path}, 长度: {length}")

# 所有节点对最短路径
paths = dict(nx.all_pairs_dijkstra_path(G, weight='weight'))
lengths = dict(nx.all_pairs_dijkstra_path_length(G, weight='weight'))
```

### 负权边用 Bellman-Ford

```python
# networkx 会自动检测并切换算法
try:
    path = nx.shortest_path(G, source=1, target=5, weight='weight', method='bellman-ford')
except nx.NetworkXUnbounded:
    print("存在负环！")
```

### ⛔ 审核重点
- [ ] 图是否有负权边（Dijkstra 不适用）
- [ ] 图是否连通（不连通则某些节点对间无路径）

---

## 三、最小生成树 (MST)

### Prim / Kruskal

```python
mst = nx.minimum_spanning_tree(G, weight='weight')
mst_edges = mst.edges(data=True)
total_weight = sum(d['weight'] for _, _, d in mst_edges)
print(f"MST 总权重: {total_weight}")

# 验证: MST 边数 = 节点数 - 1
assert mst.number_of_edges() == G.number_of_nodes() - (len(list(nx.connected_components(G))))
```

### 常见场景
- 铺设网络（电网、通信、管道）使总成本最小
- 聚类：从 MST 中删除最长的 k-1 条边 → k 个簇

---

## 四、最大流 / 最小割

### Ford-Fulkerson / Edmonds-Karp

```python
# 有向图，每条边有 capacity 属性
DG = nx.DiGraph()
DG.add_edge('s', 'a', capacity=10)
DG.add_edge('s', 'b', capacity=5)
DG.add_edge('a', 'b', capacity=15)
DG.add_edge('a', 't', capacity=10)
DG.add_edge('b', 't', capacity=10)

flow_value, flow_dict = nx.maximum_flow(DG, 's', 't')
print(f"最大流量: {flow_value}")
# flow_dict[u][v] 给出 u→v 的实际流量

# 最小割
cut_value, (reachable, non_reachable) = nx.minimum_cut(DG, 's', 't')
print(f"最小割容量: {cut_value}, S 侧: {reachable}, T 侧: {non_reachable}")
assert flow_value == cut_value  # Max-Flow Min-Cut 定理
```

### 最小费用最大流

```python
# 每条边有 capacity 和 weight(单位费用)
DG = nx.DiGraph()
DG.add_edge('s', 'a', capacity=10, weight=2)
DG.add_edge('s', 'b', capacity=5, weight=3)
DG.add_edge('a', 't', capacity=8, weight=1)
DG.add_edge('b', 't', capacity=7, weight=4)

flow_dict = nx.min_cost_flow(DG)
total_cost = sum(d['weight'] * flow for d in DG.edges.values())
```

### ⛔ 审核重点
- [ ] 容量非负（capacity ≥ 0）
- [ ] 无容量为 0 的冗余边（会使 flow_dict 混乱）
- [ ] Max-Flow Min-Cut 定理验证（flow_value == cut_value）

---

## 五、中心性与节点重要性

```python
# 度中心性（最简单的度量）
dc = nx.degree_centrality(G)  # 归一化到 [0,1]

# 介数中心性（经过该节点的最短路径占比，计算量大）
bc = nx.betweenness_centrality(G, weight='weight')

# 接近中心性（到其他节点距离之和的倒数）
cc = nx.closeness_centrality(G)

# PageRank（递归重要性：被重要节点连接 = 自己重要）
pr = nx.pagerank(G, alpha=0.85)

# 特征向量中心性
ec = nx.eigenvector_centrality(G, max_iter=1000)

# 找出最重要的节点
top_node = sorted(bc.items(), key=lambda x: x[1], reverse=True)[:5]
print(f"介数中心性 Top 5: {top_node}")
```

### 中心性选择指南

| 中心性 | 含义 | 何时用 |
|---|---|---|
| 度中心性 | 朋友多 | 局部影响力 |
| 介数 | 桥梁/守门人 | 控制信息流动 |
| 接近 | 能快速到达所有人 | 广播效率 |
| PageRank | 被重要朋友推荐 | 有向图 / 推荐系统 |
| 特征向量 | 朋友重要则自己重要 | 无向图全局影响 |

---

## 六、博弈论

### 纳什均衡 (Nash Equilibrium)

```python
import numpy as np
import nashpy as nash

# 支付矩阵: 行玩家 (P1) 的收益矩阵
# 囚徒困境
P1_payoffs = np.array([[3, 0],   # P1 背叛时的收益
                       [5, 1]])  # P1 合作时的收益
P2_payoffs = np.array([[3, 5],   # P2 背叛时的收益
                       [0, 1]])  # P2 合作时的收益

game = nash.Game(P1_payoffs, P2_payoffs)

# 计算纳什均衡
equilibria = list(game.support_enumeration())
for eq in equilibria:
    sigma1, sigma2 = eq
    print(f"P1 混合策略: {sigma1}, P2 混合策略: {sigma2}")

# 期望收益
for eq in equilibria:
    sigma1, sigma2 = eq
    print(f"收益: P1={game[sigma1, sigma2][0]:.3f}, P2={game[sigma1, sigma2][1]:.3f}")
```

### Stackelberg 博弈（主从博弈）

```python
# 领导者 (Leader) 先行动，追随者 (Follower) 观察到后最优反应
# 求解: 逆向归纳法

def follower_best_response(q1, a, b, c):
    """追随者利润: π2 = (a - b*(q1+q2))*q2 - c*q2"""
    # 最优反应: q2 = (a - c - b*q1) / (2*b)
    return max(0, (a - c - b*q1) / (2*b))

def leader_profit(q1, a, b, c):
    q2 = follower_best_response(q1, a, b, c)
    return (a - b*(q1+q2))*q1 - c*q1

# 一维优化求领导者的最优 q1
from scipy.optimize import minimize_scalar
a, b, c = 100, 1, 10
res = minimize_scalar(lambda q: -leader_profit(q, a, b, c), bounds=(0, a/b), method='bounded')
q1_opt = res.x
q2_opt = follower_best_response(q1_opt, a, b, c)
print(f"Stackelberg: q1*={q1_opt:.2f}, q2*={q2_opt:.2f}")
```

### 讨价还价 (Bargaining) — Nash Bargaining Solution

```python
def nash_bargaining(u1_vals, u2_vals, d1, d2):
    """NBS = arg max (u1-d1)*(u2-d2)，无协议点为 (d1,d2)"""
    products = (u1_vals - d1) * (u2_vals - d2)
    idx = np.argmax(products)
    return u1_vals[idx], u2_vals[idx]
```

### ⛔ 博弈论审核重点
- [ ] 均衡存在性讨论（Nash 证明了有限博弈中混合策略均衡一定存在）
- [ ] 均衡唯一性（如不唯一，讨论焦点均衡 / 风险占优）
- [ ] 支付函数依据（数据？文献？假设？）
- [ ] 均衡的实际可解释性

---

## 七、网络上的传染病模型 (SIR / SEIR on Networks)

```python
import networkx as nx
import numpy as np

def sir_network(G, beta, gamma, initial_infected, max_steps=200):
    """
    网络上 SIR 传播模拟 (基于 Gillespie 或离散时间)
    beta: 传播率, gamma: 恢复率
    """
    N = G.number_of_nodes()
    status = np.full(N, 'S')      # 所有人初始为易感
    for node in initial_infected:
        status[node] = 'I'

    S_hist, I_hist, R_hist = [], [], []

    for step in range(max_steps):
        S_hist.append((status == 'S').sum())
        I_hist.append((status == 'I').sum())
        R_hist.append((status == 'R').sum())

        if (status == 'I').sum() == 0:
            break  # 传播结束

        new_status = status.copy()
        # 遍历所有感染节点
        infected_nodes = np.where(status == 'I')[0]
        for node in infected_nodes:
            # 易感邻居以 beta 概率感染
            neighbors = list(G.neighbors(node))
            for nb in neighbors:
                if status[nb] == 'S' and np.random.rand() < beta:
                    new_status[nb] = 'I'
            # 以 gamma 概率恢复
            if np.random.rand() < gamma:
                new_status[node] = 'R'

        status = new_status

    return S_hist, I_hist, R_hist
```

### ⛔ 网络 SIR 审核重点
- [ ] 总人口守恒: S(t)+I(t)+R(t) ≡ N
- [ ] 网络结构对传播的影响（随机网络 vs 小世界 vs 无标度）
- [ ] 基本再生数 R₀ 的估计（在网络中 R₀ ≈ (β/γ) * ⟨k⟩）
- [ ] 多次模拟取平均（单次模拟不可靠）

---

## 八、常见图论问题速解

### TSP（旅行商问题）

```python
# 精确解: Held-Karp (DP, O(2^n n²)), n ≤ 20
# 近似解:
import networkx.approximation as nx_app
cycle = nx_app.traveling_salesman_problem(G, weight='weight')
# 返回: 访问所有节点的最短回路（节点序列）

# Christofides 算法 (3/2 近似比)
cycle = nx_app.christofides(G, weight='weight')
```

### 二分图匹配（指派问题）

```python
from scipy.optimize import linear_sum_assignment

cost_matrix = np.array([[4, 1, 3], [2, 0, 5], [3, 2, 2]])
row_ind, col_ind = linear_sum_assignment(cost_matrix)
total_cost = cost_matrix[row_ind, col_ind].sum()
print(f"最优指派: {list(zip(row_ind, col_ind))}, 总成本: {total_cost}")
```

### 社区检测

```python
from networkx.algorithms.community import greedy_modularity_communities
communities = list(greedy_modularity_communities(G))
print(f"检测到 {len(communities)} 个社区")
for i, comm in enumerate(communities):
    print(f"社区 {i}: {len(comm)} 个节点")
```

---

## 网络与博弈通用审核清单

1. 图连通性检查（不连通 → 某些算法不适用）
2. 负权边处理（Dijkstra 不支持 → 用 Bellman-Ford）
3. 容量的量纲一致（最大流中各边容量单位统一）
4. 博弈均衡的存在性和唯一性讨论
5. 多次随机模拟（网络传播类）→ 报告均值 ± 标准差
6. 网络结构假设有依据（全连接 / 小世界 / 无标度）
7. 结果放在现实语境中解读（"关键节点是 XX 市，切断后网络效率降低 37%"）

### 常见全局坑
1. **有向图/无向图混淆**：道路可能单行，建图时应用 DiGraph
2. **权重含义相反**：权重=距离（最短路径） vs 权重=容量（最大流）
3. **大图直接算所有节点对最短路径**：Floyd-Warshall O(n³)，n>1000 时用近似
4. **均衡分析只算不解**：算出混策略概率 0.6/0.4 但不解释含义
5. **忽略图结构对结果的敏感性**：删除关键节点后系统行为可能剧变
