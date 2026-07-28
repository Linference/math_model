# 01 — 优化问题算法手册

**目的**：从问题识别到代码实现，一站式解决优化建模。每个子类包含：问题模板、Python 工具、代码骨架、收敛判据、常见坑。

---

## 问题→算法速查表

| 问题特征 | 推荐算法 | 工具包 |
|---|---|---|
| 线性目标 + 线性约束，变量连续 | LP（线性规划） | `scipy.optimize.linprog` / `pulp` |
| 变量含整数/0-1 | IP/MILP（整数规划） | `pulp` / `pyomo` / `ortools` |
| 目标或约束含非线性项 | NLP（非线性规划） | `scipy.optimize.minimize` |
| 大规模组合优化，精确解不可行 | 启发式 (GA/PSO/SA) | `deap` / `pymoo` / 自实现 |
| 多阶段决策，阶段间有递推关系 | 动态规划 (DP) | 自实现（`functools.lru_cache`） |
| 多个相互冲突的目标 | 多目标优化 | `pymoo` (NSGA-II) / 加权法 |
| 目标与约束线性，但目标为向量 | 多目标 LP | 加权求和 / ε-约束法 |

---

## 一、线性规划 (LP)

### 标准形式

$$\min \; \mathbf{c}^T\mathbf{x} \quad \text{s.t.} \quad A\mathbf{x} \leq \mathbf{b},\quad \mathbf{x} \geq 0$$

### 代码骨架 (scipy)

```python
from scipy.optimize import linprog
import numpy as np

# 目标系数: min c^T x
c = np.array([3, 2])  # min 3x1 + 2x2

# 不等式约束: A_ub @ x <= b_ub
A_ub = np.array([[2, 1], [1, 2]])
b_ub = np.array([10, 8])

# 等式约束: A_eq @ x == b_eq (无则省略)
# A_eq = np.array([[1, 1]])
# b_eq = np.array([6])

# 变量边界
bounds = [(0, None), (0, None)]  # x1, x2 >= 0

result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
print(f"最优解: x = {result.x}, 最优值: {result.fun}")
print(f"成功: {result.success}, 状态: {result.message}")
```

### 代码骨架 (pulp — 推荐用于建模竞赛，因为输出可读)

```python
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, value

prob = LpProblem("production_plan", LpMinimize)
x1 = LpVariable("x1", lowBound=0)
x2 = LpVariable("x2", lowBound=0)

prob += 3*x1 + 2*x2              # 目标
prob += 2*x1 + x2 <= 10           # 约束1
prob += x2 + 2*x2 <= 8            # 约束2

prob.solve()
print(f"状态: {LpStatus[prob.status]}, x1={value(x1):.4f}, x2={value(x2):.4f}")
print(f"最优值: {value(prob.objective):.4f}")
```

### 审核清单
- [ ] 所有约束均已写入（对照方案表逐条核对）
- [ ] 不等式方向正确（特别注意 ≥ 与 ≤）
- [ ] 对偶价格（影子价格）非负检验
- [ ] 变量上下界与实际意义一致（如产量不可能为负）

### 常见坑
1. **量纲不统一**：目标用万元，约束里用元 → 解完全错误
2. **约束遗漏**：非负约束忘记写 `bounds`
3. **可行域为空**：约束冲突，用 `result.success` 检查
4. **无限最优解**：缺少某个方向约束，目标可无限改善

---

## 二、整数规划 (IP / MILP)

### 代码骨架 (pulp)

```python
from pulp import LpVariable, LpBinary, LpInteger

x = LpVariable("x", lowBound=0, cat='Integer')     # 整数变量
y = LpVariable("y", cat='Binary')                   # 0-1变量
z = LpVariable("z", lowBound=0, upBound=50)         # 连续变量
```

### 常见坑
1. **计算时间爆炸**：整数变量 > 100 时精确求解可能极慢 → 考虑启发式或松弛
2. **松弛不可行**：LP 松弛有解不代表 IP 有解
3. **Big-M 法**：用极大常数 M 建模逻辑约束时，M 过大导致数值问题

---

## 三、非线性规划 (NLP)

### 代码骨架 (scipy.optimize.minimize)

```python
from scipy.optimize import minimize
import numpy as np

def objective(x):
    return x[0]**2 + x[1]**2 + 3*x[0]*x[1]

def constraint1(x):
    return x[0] + x[1] - 1  # >= 0 约束，ineq 类型用 >=0 形式

cons = [{'type': 'ineq', 'fun': constraint1}]
bounds = [(-5, 5), (-5, 5)]

# 多起点检查全局最优
best_x, best_f = None, np.inf
for _ in range(20):
    x0 = np.random.uniform(-5, 5, 2)
    res = minimize(objective, x0, bounds=bounds, constraints=cons, method='SLSQP')
    if res.success and res.fun < best_f:
        best_x, best_f = res.x, res.fun

print(f"全局最优候选: x = {best_x}, f = {best_f:.6f}")
```

### 方法选择

| 问题类型 | 推荐 method | 说明 |
|---|---|---|
| 无约束或仅边界 | `L-BFGS-B` | 最快，大变量数友好 |
| 有等式/不等式约束 | `SLSQP` | 通用，收敛好 |
| 目标含噪声 | `Nelder-Mead` | 无梯度，简单 |
| 全局优化 | `differential_evolution` | 不需梯度，代价高 |

### 审核清单
- [ ] 目标函数可微性已确认（用梯度方法时）
- [ ] 多起点检验（非凸必做，≥10 次随机起点）
- [ ] KKT 条件近似检验（乘子是否合理）
- [ ] 收敛曲线绘图（判断是否早停）

### 常见坑
1. **局部最优当全局最优**：非凸函数只跑一次 `minimize`
2. **数值梯度失效**：目标有台阶/不连续，改用 `Nelder-Mead`
3. **约束缩放**：约束值数量级差太大导致 SLSQP 失败 → 归一化

---

## 四、启发式算法

### 4.1 遗传算法 (GA)

```python
# 使用 deap 库
import random
from deap import base, creator, tools, algorithms

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))  # 最小化
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("attr_float", random.uniform, -10, 10)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=5)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evaluate(ind):
    x, y = ind[0], ind[1]
    return (x**2 + y**2 + 0.1*(x-3)**2,)  # 目标函数

toolbox.register("mate", tools.cxSimulatedBinaryBounded, low=-10, up=10, eta=20.0)
toolbox.register("mutate", tools.mutPolynomialBounded, low=-10, up=10, eta=20.0, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evaluate)

pop = toolbox.population(n=100)
hof = tools.HallOfFame(1)
stats = tools.Statistics(lambda ind: ind.fitness.values[0])
stats.register("min", np.min)

pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=0.7, mutpb=0.2, ngen=200,
                                    stats=stats, halloffame=hof, verbose=False)
print(f"GA 最优: {hof[0]}, 适应度: {hof[0].fitness.values[0]:.6f}")
```

### 4.2 粒子群 (PSO)

```python
# 自实现骨架（不依赖第三方库）
import numpy as np

def pso(objective, bounds, n_particles=50, n_iter=200, w=0.7, c1=1.5, c2=1.5):
    dim = len(bounds)
    lb = np.array([b[0] for b in bounds])
    ub = np.array([b[1] for b in bounds])

    # 初始化
    pos = np.random.uniform(lb, ub, (n_particles, dim))
    vel = np.random.uniform(-1, 1, (n_particles, dim))
    pbest_pos = pos.copy()
    pbest_val = np.array([objective(p) for p in pos])
    gbest_idx = np.argmin(pbest_val)
    gbest_pos = pbest_pos[gbest_idx].copy()
    gbest_val = pbest_val[gbest_idx]

    history = [gbest_val]
    for t in range(n_iter):
        r1, r2 = np.random.rand(2)
        vel = w*vel + c1*r1*(pbest_pos - pos) + c2*r2*(gbest_pos - pos)
        pos = pos + vel
        pos = np.clip(pos, lb, ub)

        vals = np.array([objective(p) for p in pos])
        improved = vals < pbest_val
        pbest_pos[improved] = pos[improved]
        pbest_val[improved] = vals[improved]

        new_gbest_idx = np.argmin(pbest_val)
        if pbest_val[new_gbest_idx] < gbest_val:
            gbest_pos = pbest_pos[new_gbest_idx].copy()
            gbest_val = pbest_val[new_gbest_idx]
        history.append(gbest_val)

    return gbest_pos, gbest_val, history
```

### 4.3 模拟退火 (SA)

```python
import numpy as np

def simulated_annealing(objective, bounds, n_iter=2000, T0=1000, alpha=0.95):
    lb = np.array([b[0] for b in bounds])
    ub = np.array([b[1] for b in bounds])
    x = np.random.uniform(lb, ub)
    fx = objective(x)
    best_x, best_f = x.copy(), fx
    T = T0

    for i in range(n_iter):
        x_new = x + np.random.normal(0, 0.1*(ub - lb))  # 邻域扰动
        x_new = np.clip(x_new, lb, ub)
        f_new = objective(x_new)

        if f_new < fx or np.random.rand() < np.exp((fx - f_new) / T):
            x, fx = x_new, f_new
            if fx < best_f:
                best_x, best_f = x.copy(), fx
        T *= alpha

    return best_x, best_f
```

### 启发式通用审核清单
- [ ] 种群多样性是否维持（GA：每代适应度标准差 > 0）
- [ ] 收敛曲线是否平稳下降（无剧烈抖动后"死掉"）
- [ ] 至少 5 次独立运行，报告均值 ± 标准差
- [ ] 如可能，与精确解（小规模）或 LP 松弛界对比
- [ ] 参数不敏感测试（种群大小 ±50%，变异率 ±30%）

### 常见坑
1. **早熟收敛**：种群所有个体适应度相同但非全局最优 → 增大变异率
2. **收敛判据不明确**：只跑固定代数不判断是否已收敛 → 设容忍度阈值
3. **参数全用默认**：GA 的默认参数是为测试函数设计的，实际问题需调整

---

## 五、动态规划 (DP)

### 适用条件
1. **最优子结构**：问题的最优解包含子问题的最优解
2. **重叠子问题**：子问题被反复调用

### 代码骨架

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def dp(state):
    """状态定义需显式写出，如 dp(i, j) 表示前 i 个物品容量为 j 的最优值"""
    if base_case(state):
        return base_value
    # 递推关系
    options = [dp(next_state) + cost for next_state in valid_transitions(state)]
    return min(options)  # 或 max
```

### 常见坑
1. **状态爆炸**：维度超 3-4 时 DP 不适用 → 改用近似/启发式
2. **递推方向错误**：必须确保子问题在父问题之前计算完毕
3. **忘记记忆化**：不用 `lru_cache` 导致指数时间

---

## 六、多目标优化

### 6.1 加权法

```python
# 两目标: min f1(x), min f2(x) → min w*f1 + (1-w)*f2
ws = np.linspace(0, 1, 21)  # 21 组权重扫描
pareto_front = []
for w in ws:
    res = minimize(lambda x: w*f1(x) + (1-w)*f2(x), x0, ...)
    pareto_front.append((f1(res.x), f2(res.x)))
```

### 6.2 NSGA-II (pymoo)

```python
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import Problem
from pymoo.optimize import minimize as moo_minimize
import numpy as np

class MyProblem(Problem):
    def __init__(self):
        super().__init__(n_var=2, n_obj=2, n_constr=1, xl=np.array([0, 0]), xu=np.array([5, 5]))

    def _evaluate(self, x, out, *args, **kwargs):
        f1 = x[:, 0]**2 + x[:, 1]**2
        f2 = (x[:, 0]-3)**2 + (x[:, 1]-3)**2
        g1 = x[:, 0] + x[:, 1] - 8  # 约束: x0+x1 ≤ 8
        out["F"] = np.column_stack([f1, f2])
        out["G"] = g1.reshape(-1, 1)

problem = MyProblem()
algorithm = NSGA2(pop_size=100)
res = moo_minimize(problem, algorithm, ('n_gen', 200), seed=42)
print(f"Pareto 前沿共 {len(res.F)} 个解，目标范围: F1∈[{res.F[:,0].min():.3f}, {res.F[:,0].max():.3f}], F2∈[{res.F[:,1].min():.3f}, {res.F[:,1].max():.3f}]")
```

### 多目标审核清单
- [ ] Pareto 前沿是否非支配（每个解都不能被另一个同时改进）
- [ ] 权重灵敏度分析（加权法中 w 对前沿形状的影响）
- [ ] 前沿图入论文（展示 trade-off 关系）

### 常见坑
1. **加权和法丢失凹部**：Pareto 前沿为凹时加权和法无法捕捉 → 改用 ε-约束或 NSGA-II
2. **种群规模与目标数**：目标数 > 3 时 NSGA-II 性能下降 → 考虑 MOEA/D
3. **归一化缺失**：目标量纲差异大时不归一化，加权和完全被占主导地位的目标控制

---

## 通用优化审核清单（跨所有子类）

1. 问题类型正确识别（LP / IP / NLP / 多目标）
2. 目标函数方向正确（min vs max，`linprog` 默认 min）
3. 约束完整性与方案表逐条对应
4. 数值稳定性（系数量级差 < 1e6）
5. 解的实际可行性检验（负数产量？非整数人数？）
6. 至少做一组对比（不同方法、不同初始点、不同参数）
7. 灵敏度分析（关键参数 ±20%，最优值变化 < 10% 为稳健）
