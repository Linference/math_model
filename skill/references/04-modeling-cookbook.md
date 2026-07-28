# 04 — 建模配方索引（Cookbook Index）

本文件为索引页。算法细节已拆分到 `cookbooks/` 子目录下的 6 个独立手册中，每个手册 150-300 行，**自包含**（读一个即可实现算法）。

---

## 手册目录

| # | 文件 | 覆盖内容 | 何时查阅 |
|---|---|---|---|
| 01 | [`cookbooks/01-optimization.md`](cookbooks/01-optimization.md) | LP / IP / NLP / 启发式(GA,PSO,SA) / 动态规划 / 多目标(NSGA-II, Pareto) | 资源分配、路径规划、参数标定、调度排产 |
| 02 | [`cookbooks/02-evaluation.md`](cookbooks/02-evaluation.md) | AHP(CR检验) / TOPSIS / 熵权法 / 灰色关联 / 模糊综合评价 / VIKOR / ELECTRE | 多指标排序、方案优选、绩效评估、选址决策 |
| 03 | [`cookbooks/03-prediction.md`](cookbooks/03-prediction.md) | ARIMA / Holt-Winters / 岭回归&Lasso / 随机森林 / XGBoost / LSTM / Prophet | 时序预测、回归预测、趋势外推 |
| 04 | [`cookbooks/04-mechanistic.md`](cookbooks/04-mechanistic.md) | ODE/PDE / 系统动力学 / 元胞自动机 / 蒙特卡洛 / 排队论 | 传染病、热传导、生态种群、交通流、风险分析 |
| 05 | [`cookbooks/05-statistics-and-ml.md`](cookbooks/05-statistics-and-ml.md) | 假设检验 / 回归诊断 / 聚类(KMeans,DBSCAN,层次) / 降维(PCA,t-SNE) / 贝叶斯 / 生存分析 | 差异性检验、数据探索、因果推断、问卷分析 |
| 06 | [`cookbooks/06-network-and-game.md`](cookbooks/06-network-and-game.md) | 最短路 / 最大流 / MST / 中心性 / 博弈论(Nash,Stackelberg) / 网络SIR | 交通网络、物流调度、影响力分析、策略优化 |

---

## 通用资源

| 文件 | 内容 |
|---|---|
| [`10-modeling-tricks.md`](10-modeling-tricks.md) | 建模实战技巧：从简入繁五步法、假设松绑、灵敏度进阶、论文呈现三步法、低分陷阱规避 |

---

## 快速决策流程

```
拿到赛题 → 判断核心问题类型 →

  优化/分配  → 01-optimization
  评价/排序  → 02-evaluation
  预测/外推  → 03-prediction
  机理/仿真  → 04-mechanistic
  推断/分类  → 05-statistics-and-ml
  网络/策略  → 06-network-and-game

同时读 10-modeling-tricks 避免常见低级错误。
```

---

## 每个手册的统一结构

1. **问题→算法速查表**（顶部）
2. **Python 代码骨架**（可直接复制改写）
3. **审核清单**（含数值验证要求）
4. **常见坑**（该类别特有）
5. **通用审核清单**（跨子类的共性要求）

---

## 通用铁律（适用所有模型）

1. **随机种子固定**：`np.random.seed(42)` / `random_state=42`
2. **两次以上验证**：灵敏度 + 对照实验 + 交叉验证，三选至少二
3. **结果三步呈现**：数字 → 含义 → 洞察
4. **代码可追溯**：论文中每个数字都能追溯到代码中的变量名和行号
5. **量纲统一**：建模前检查所有变量单位，建模后检查结果物理合理性
