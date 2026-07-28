# 04 — 机理建模手册

**目的**：基于物理/生物/经济内在规律建立数学模型。从常微分方程到元胞自动机，一站式覆盖。每个方法包含：建模步骤、稳定性条件、参数估计、代码骨架、验证方法。

---

## 问题→算法速查表

| 问题特征 | 推荐方法 | 核心工具 |
|---|---|---|
| 状态随时间连续变化，可用方程描述 | ODE（常微分方程） | `scipy.integrate.solve_ivp` |
| 空间分布 + 时间演化（热传导、扩散） | PDE（偏微分方程） | 有限差分法自实现 / `FEniCS` |
| 多变量反馈回路，政策仿真 | 系统动力学 | 自实现（ODE 方程组）/ `PySD` |
| 局部规则 → 全局涌现现象 | 元胞自动机 (CA) | 自实现（numpy 网格） |
| 随机因素主导，需估计不确定性 | 蒙特卡洛模拟 | `numpy.random` |
| 服务系统等待时间、队列长度 | 排队论 (M/M/1 等) | 解析公式 + `simpy` (复杂系统) |

---

## 一、常微分方程 (ODE)

### 建模范式

1. **识别状态变量**：描述系统在任意时刻 t 的状态（如 S(t), I(t), R(t)）
2. **写出变化率方程**：d(状态)/dt = 流入 - 流出
3. **确定初始条件**和**参数**
4. **数值求解** → 验证守恒律 → 灵敏度

### 代码骨架

```python
from scipy.integrate import solve_ivp
import numpy as np

def sir_model(t, y, beta, gamma):
    """SIR 传染病模型"""
    S, I, R = y
    N = S + I + R
    dS = -beta * S * I / N
    dI =  beta * S * I / N - gamma * I
    dR =  gamma * I
    return [dS, dI, dR]

# 参数
beta, gamma = 0.3, 0.1
N = 1000
I0, R0 = 1, 0
S0 = N - I0 - R0

# 求解
sol = solve_ivp(
    sir_model,
    t_span=(0, 160),          # 时间范围
    y0=[S0, I0, R0],          # 初始条件
    args=(beta, gamma),       # 额外参数
    method='RK45',            # 默认自适应步长
    rtol=1e-6,                # 相对容差
    max_step=1.0              # 最大步长（防止跳过大快事件）
)

# 验证守恒
total = sol.y[0] + sol.y[1] + sol.y[2]
print(f"总人口守恒检验 max|N(t)-N(0)| = {np.max(np.abs(total - N)):.2e}")
```

### 方法选择

| method | 适用 | 特点 |
|---|---|---|
| `RK45` | 默认首选 | 显式，自适应步长，非刚性 |
| `Radau` | 刚性方程 | 隐式，稳定 |
| `BDF` | 刚性方程 | 隐式多步，极刚性时用 |
| `LSODA` | 自动检测刚性 | 自动切换 Adams/BDF |

### 刚性判断

如果系统各组分变化速率相差极大（快变量 ms 级，慢变量 天 级）→ 刚性 → 用 `Radau` 或 `BDF`。

### 参数估计（ODE 拟合数据）

```python
from scipy.optimize import minimize

def ode_loss(params, t_data, y_data):
    beta, gamma = params
    sol = solve_ivp(sir_model, (t_data[0], t_data[-1]),
                    y0=[S0, I0, R0], args=(beta, gamma),
                    t_eval=t_data, method='RK45')
    y_pred = sol.y[1]  # 拟合 I(t) 曲线
    return np.mean((y_pred - y_data)**2)

res = minimize(ode_loss, x0=[0.2, 0.05], args=(t_obs, I_obs),
               bounds=[(0.001, 1), (0.001, 1)])
print(f"估计参数: beta={res.x[0]:.4f}, gamma={res.x[1]:.4f}")
```

### 稳定性分析

```python
import sympy as sp

# 符号计算雅可比矩阵 → 求特征值 → 判断平衡点稳定性
S, I, R, beta, gamma = sp.symbols('S I R beta gamma')
# 平衡点 (S*, I*, R*)
eq1 = -beta * S * I
eq2 = beta * S * I - gamma * I
J = sp.Matrix([[sp.diff(eq1, S), sp.diff(eq1, I)],
               [sp.diff(eq2, S), sp.diff(eq2, I)]])
# 代入平衡点求特征值判断稳定性
```

### ODE 审核清单
- [ ] 守恒律验证（S+I+R 恒定？质量守恒？）
- [ ] 稳态分析：平衡点存在性 + 稳定性
- [ ] 数值稳定性：不同 method 和步长的结果是否一致
- [ ] 参数灵敏度：±20% 扰动对关键输出的影响
- [ ] 初始条件不敏感（最优情况）

### 常见坑
1. **符号错误**：dS 的负号遗漏 → 结果完全错误
2. **刚性未识别**：方法用 RK45 但系统刚性 → 计算极慢或发散
3. **t_eval 与 t_span 不一致**：t_eval 在 t_span 之外 → 无声错误
4. **状态值变负**：如 S < 0 无意义，但 solver 可能产生负值 → 加 clip 或事件检测

---

## 二、偏微分方程 (PDE)

### 有限差分数值解

以 1D 热传导方程 $\partial u/\partial t = \alpha \partial^2 u/\partial x^2$ 为例。

```python
import numpy as np

def heat_1d_fdm(alpha, L, T, nx=100, nt=500):
    """1D 热传导 有限差分 Crank-Nicolson"""
    dx = L / (nx - 1)
    dt = T / nt
    r = alpha * dt / dx**2

    if r > 0.5:  # 显式格式稳定性条件
        print(f"警告: r={r:.3f} > 0.5，显式格式可能不稳定")

    # 初始条件
    x = np.linspace(0, L, nx)
    u = np.sin(np.pi * x / L)  # 示例: 正弦初始分布

    # 边界条件: u(0,t)=u(L,t)=0（已在初始化中满足）

    for n in range(nt):
        u_new = u.copy()
        for i in range(1, nx-1):
            u_new[i] = u[i] + r * (u[i+1] - 2*u[i] + u[i-1])
        u = u_new

    return x, u
```

### 稳定性条件

| 格式 | 条件 | 说明 |
|---|---|---|
| 显式 (FTCS) | $r = \alpha \Delta t / \Delta x^2 \leq 0.5$ | 步长限制严格 |
| 隐式 (BTCS) | 无条件稳定 | 每步需解三对角方程组 |
| Crank-Nicolson | 无条件稳定 | 二阶精度，推荐 |

### 审核重点
- [ ] 稳定性条件已检查并满足
- [ ] 网格收敛性检验：减半步长，解的变化 < 1%
- [ ] 边界条件正确实现（Dirichlet / Neumann / 周期）

---

## 三、系统动力学

### 本质：多变量反馈 ODE 系统

典型模式：库存-流量图 → 微分方程组 → 数值仿真。

```python
# 例: 捕食者-猎物模型 (Lotka-Volterra)
def lotka_volterra(t, y, alpha, beta, delta, gamma):
    prey, predator = y
    d_prey = alpha*prey - beta*prey*predator
    d_predator = delta*prey*predator - gamma*predator
    return [d_prey, d_predator]

sol = solve_ivp(lotka_volterra, (0, 50), [40, 9],
                args=(1.0, 0.1, 0.01, 0.5), max_step=0.1)
# 预期: 相位图形成闭合环（周期震荡）
```

### 系统动力学建模步骤
1. 识别库存变量（存量）和流量变量（速率）
2. 画出因果回路图（正反馈 R / 负反馈 B）
3. 写出微分方程
4. 数值仿真 → 情景分析

### 审核重点
- [ ] 反馈回路正确识别（增强型 vs 平衡型）
- [ ] 量纲一致性：所有方程左右量纲一致
- [ ] 极端条件测试：参数为 0 或极大时的行为合理

---

## 四、元胞自动机 (CA)

### 本质：离散网格 + 局部规则 → 全局涌现

```python
import numpy as np

def ca_step(grid, rule_func):
    """grid: 2D numpy array, rule_func: 每个细胞的新状态 = f(当前状态, 邻居状态)"""
    new_grid = grid.copy()
    rows, cols = grid.shape
    for i in range(1, rows-1):
        for j in range(1, cols-1):
            neighbors = grid[i-1:i+2, j-1:j+2]
            new_grid[i, j] = rule_func(grid[i, j], neighbors)
    return new_grid

# 例: 生命游戏 (Conway's Game of Life)
def conway_rule(cell, neighbors):
    alive = np.sum(neighbors) - cell  # 邻居活细胞数（不含自身）
    if cell == 1:
        return 1 if alive in [2, 3] else 0
    else:
        return 1 if alive == 3 else 0

# 模拟
grid = np.random.choice([0, 1], size=(100, 100))
for step in range(200):
    grid = ca_step(grid, conway_rule)
```

### 常见 CA 应用
- 森林火灾蔓延：燃烧 → 燃尽，概率传播
- 交通流 Nagel-Schreckenberg
- 人群疏散
- 城市扩张

### 审核重点
- [ ] 邻居定义明确（von Neumann 4邻域? Moore 8邻域?）
- [ ] 边界处理声明的处理方式（周期性 / 固定值 / 反射）
- [ ] 随机性来源固定种子 `np.random.seed(42)`
- [ ] 多次运行结果的统计分布（单次结果不可靠）

---

## 五、蒙特卡洛模拟

### 本质：大量随机采样 → 统计估计

### 标准流程

```python
import numpy as np

def monte_carlo(sim_func, n_sim=10000, seed=42):
    """
    sim_func: 无参函数，返回一次模拟的结果（标量）
    返回: 均值, 标准差, 95% 置信区间
    """
    np.random.seed(seed)
    results = np.array([sim_func() for _ in range(n_sim)])
    mean = results.mean()
    std = results.std()
    ci_lower = mean - 1.96 * std / np.sqrt(n_sim)
    ci_upper = mean + 1.96 * std / np.sqrt(n_sim)
    return mean, std, (ci_lower, ci_upper)

# 例: 估计 π
def estimate_pi():
    x, y = np.random.uniform(-1, 1, 2)
    return 1 if x**2 + y**2 <= 1 else 0

mean, std, ci = monte_carlo(estimate_pi, n_sim=100000)
print(f"π ≈ {4*mean:.6f}, 95% CI: [{4*ci[0]:.6f}, {4*ci[1]:.6f}]")
```

### 收敛诊断

```python
def convergence_check(results):
    """检查 MC 是否收敛: 均值的滚动标准差应趋稳"""
    cum_mean = np.cumsum(results) / np.arange(1, len(results)+1)
    # 最后 10% 数据的均值波动应 < 1%
    tail_std = cum_mean[-len(cum_mean)//10:].std()
    tail_mean = cum_mean[-1]
    return tail_std / abs(tail_mean) < 0.01
```

### 审核重点
- [ ] 模拟次数 ≥ 1000（基本要求）
- [ ] 收敛诊断通过
- [ ] 95% 置信区间已报告
- [ ] 随机种子固定

### 常见坑
1. **收敛未检查**：100 次模拟就报结果 → 结果根本不稳定
2. **伪随机数生成器循环**：不用 numpy 的随机数而用低质随机源
3. **方差过大**：样本量不足 → 报告 CI 过宽 → 结论无意义

---

## 六、排队论

### 标准模型速查

| 模型 | 含义 | 关键公式 |
|---|---|---|
| M/M/1 | 泊松到达，指数服务，1 服务器 | $L = \frac{\lambda}{\mu - \lambda}$, $W = \frac{1}{\mu - \lambda}$ |
| M/M/c | 多服务器 | Erlang-C 公式，$P(\text{等待}) = \frac{(cp)^c}{c!(1-p)} / \sum$ |
| M/G/1 | 一般服务时间 | Pollaczek-Khinchine 公式 |
| M/M/1/K | 有限队列 | 有拒绝概率 |

```python
import numpy as np

def mm1_stats(arrival_rate, service_rate):
    """M/M/1 队列分析"""
    rho = arrival_rate / service_rate  # 利用率
    if rho >= 1:
        raise ValueError("系统不稳定: ρ ≥ 1")
    L = rho / (1 - rho)               # 平均队长
    Lq = rho**2 / (1 - rho)           # 平均排队长度
    W = 1 / (service_rate - arrival_rate)  # 平均逗留时间
    Wq = rho / (service_rate - arrival_rate)  # 平均等待时间
    P0 = 1 - rho                      # 系统空闲概率
    return {"ρ": rho, "L": L, "Lq": Lq, "W": W, "Wq": Wq, "P0": P0}

# 复杂排队系统用 simpy 离散事件仿真
# import simpy
# 详见 simpy 官方文档
```

### 排队论审核重点
- [ ] 到达时间间隔的分布验证（是否真的服从泊松？做 χ² 拟合优度检验）
- [ ] 服务时间分布验证
- [ ] ρ < 1 稳态条件满足
- [ ] 解析公式 vs 仿真结果一致性校验

---

## 机理建模通用审核清单

1. 模型假设物理合理性（守恒律、量纲一致）
2. 数值稳定性条件已检查（ODE 步长、PDE CFL、排队 ρ<1）
3. 参数可辨识性（数据是否足以唯一确定所有参数？）
4. 模型验证：至少与真实数据 / 简化解析解 / 极端条件三种之一对比
5. 参数灵敏度分析：关键参数的 ±20% 变化对输出的影响
6. 不确定性量化：蒙特卡洛时报告置信区间
7. 稳态分析：如适用，讨论长期行为（平衡点、极限环、混沌）

### 常见全局坑
1. **数值精度不够**：默认 rtol=1e-3 太松 → 至少 1e-6
2. **量纲混乱**：一个方程中混用天和小时 → 无单位检查
3. **没有与数据对比**：纯机理模型无验证 → 在论文中极容易受质疑
4. **参数"拍脑袋"**：不估计、不查文献、不说来源
