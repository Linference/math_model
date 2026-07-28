# 03 — 预测算法手册

**目的**：从时序分析到机器学习预测，一站式解决预测问题。每个方法包含：适用场景、数据要求、代码骨架、评估指标、回测协议。

---

## 问题→算法速查表

| 问题特征 | 推荐算法 | 最小样本量 |
|---|---|---|
| 单变量时序，有趋势无季节 | ARIMA | > 30 点 |
| 单变量时序，有趋势 + 季节 | SARIMA / Holt-Winters | > 2 个完整季节周期 |
| 多变量，线性关系 | 线性回归 / 岭回归 / Lasso | > 10×特征数 |
| 多变量，非线性，样本充足 | 随机森林 / XGBoost | > 200 |
| 长序列时序，复杂模式 | LSTM | > 500 |
| 日/周/年周期，节假日效应 | Prophet | > 2 个周期 |
| 数据极少，趋势明确 | 灰色 GM(1,1) | > 4 |

---

## 一、评估指标速查

```python
import numpy as np

def forecast_metrics(y_true, y_pred):
    """返回 RMSE, MAE, MAPE (%), R²"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    rmse  = np.sqrt(np.mean((y_true - y_pred)**2))
    mae   = np.mean(np.abs(y_true - y_pred))
    # MAPE: 避免除零
    mask  = y_true != 0
    mape  = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    ss_res = np.sum((y_true - y_pred)**2)
    ss_tot = np.sum((y_true - y_true.mean())**2)
    r2    = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return {"RMSE": rmse, "MAE": mae, "MAPE(%)": mape, "R²": r2}
```

| 指标 | 含义 | 适用场景 | 注意 |
|---|---|---|---|
| RMSE | 均方根误差 | 大误差惩罚重 | 对异常值敏感 |
| MAE | 平均绝对误差 | 稳健评估 | 不突出大误差 |
| MAPE | 平均绝对百分比误差 | 跨量纲比较 | y=0 时无定义 |
| R² | 决定系数 | 解释拟合程度 | 不是越大越好 |

### 回测协议（铁律）

```
训练数据                   测试数据
[-------训练----------][---测试---]
                       不可偷看！

时间序列必须时序分割（不可随机打乱）。
可做多期滚动回测：
  窗口1: train[0:50] → test[50:60]
  窗口2: train[0:60] → test[60:70]
  ...
  报告所有窗口的平均指标 ± 标准差
```

---

## 二、ARIMA / SARIMA

### 适用：单变量平稳时序

**使用前必须**：ADF 检验（p < 0.05 表示平稳）

```python
from statsmodels.tsa.stattools import adfuller
p_value = adfuller(series)[1]
print(f"ADF p-value = {p_value:.4f} {'→ 平稳' if p_value < 0.05 else '→ 不平稳，需差分'}")
```

### 定阶

```python
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
# ACF 图 → 定 q (MA 阶数)
# PACF 图 → 定 p (AR 阶数)
# 或用 auto_arima
import pmdarima as pm
model_auto = pm.auto_arima(series, seasonal=False, stepwise=True,
                           trace=False, error_action='ignore', suppress_warnings=True)
print(f"最优 ARIMA 阶数: {model_auto.order}")
```

### ARIMA 代码骨架

```python
from statsmodels.tsa.arima.model import ARIMA
import numpy as np

# 拟合
model = ARIMA(train_series, order=(p, d, q))
result = model.fit()
print(result.summary())  # 查看 AIC/BIC、系数显著性

# 预测
forecast = result.forecast(steps=len(test))
# 或带置信区间
forecast_obj = result.get_forecast(steps=len(test))
forecast_mean = forecast_obj.predicted_mean
ci = forecast_obj.conf_int(alpha=0.05)  # 95% CI
```

### SARIMA（带季节性）

```python
# order=(p,d,q), seasonal_order=(P,D,Q,s)，s 为季节周期
model = ARIMA(train_series, order=(p,d,q), seasonal_order=(P,D,Q,s))
```

### 审核清单
- [ ] ADF 平稳性检验已做，差分阶数 d 已报告
- [ ] 残差 Ljung-Box 检验 p > 0.05（残差为白噪声）
- [ ] AIC/BIC 用于模型选择（越小越好）
- [ ] 预测区间已报告（不只是点预测）

### 常见坑
1. **未做平稳性检验**：不平稳序列直接 ARIMA → 完全无效
2. **差分过度**：d 越大数据越"白噪声化"，预测越差
3. **季节周期选错**：月度数据 s≠12 却硬设 12 → 检查数据实际频率
4. **残差不白噪声**：模型未充分提取信息 → 需调整阶数

---

## 三、指数平滑 (Holt-Winters)

### 适用：带趋势和季节性的时序，样本 < 50

```python
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Holt-Winters 加法季节模型
model = ExponentialSmoothing(
    train_series,
    trend='add',           # 'add' 或 'mul'（乘法趋势）
    seasonal='add',        # 'add' 或 'mul'（乘法季节）
    seasonal_periods=12    # 季节周期
)
result = model.fit()
forecast = result.forecast(steps=len(test))
```

### 模型选择

| 数据特征 | trend | seasonal |
|---|---|---|
| 趋势稳定上升/下降（固定增量） | 'add' | — |
| 趋势按比例增长（指数型） | 'mul' | — |
| 季节波动幅度恒定 | — | 'add' |
| 季节波动幅度随水平增大 | — | 'mul' |

### 常见坑
1. 乘法模型要求数据 > 0
2. seasonal_periods 设错（日数据=7, 月数据=12, 季数据=4）

---

## 四、岭回归 / Lasso（正则化线性模型）

### 适用：多变量预测，特征数多或有共线性

```python
from sklearn.linear_model import RidgeCV, LassoCV
from sklearn.preprocessing import StandardScaler

# 必须标准化！
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 岭回归（自动选 alpha）
ridge = RidgeCV(alphas=np.logspace(-3, 3, 50), cv=5)
ridge.fit(X_train_scaled, y_train)
print(f"最佳 alpha: {ridge.alpha_:.4f}")

# Lasso（自动选 alpha + 内置特征选择）
lasso = LassoCV(alphas=np.logspace(-3, 3, 50), cv=5, max_iter=10000)
lasso.fit(X_train_scaled, y_train)
print(f"非零系数个数: {(lasso.coef_ != 0).sum()} / {len(lasso.coef_)}")

# 预测与评估
y_pred = ridge.predict(X_test_scaled)
```

### 何时用哪个
- **岭回归**：特征都重要，但需要防过拟合 → L2 正则化，系数收缩但不归零
- **Lasso**：需要自动特征选择 → L1 正则化，不重要系数归零
- **线性回归**：特征 > 样本时根本跑不了 → 必须换成 Ridge

---

## 五、随机森林 / XGBoost（集成树）

### 随机森林回归

```python
from sklearn.ensemble import RandomForestRegressor

rf = RandomForestRegressor(n_estimators=100, max_depth=None,
                           random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)

# 特征重要性
importances = rf.feature_importances_
```

### XGBoost（通常比随机森林精度更高）

```python
import xgboost as xgb

# 转换为 DMatrix（可选，但更高效）
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest  = xgb.DMatrix(X_test)

params = {
    'objective': 'reg:squarederror',
    'learning_rate': 0.1,
    'max_depth': 6,
    'n_estimators': 200,
    'random_state': 42
}
model = xgb.train(params, dtrain, num_boost_round=200,
                  evals=[(dtrain, 'train')], verbose_eval=False)
y_pred = model.predict(dtest)

# 特征重要性（三种类型）
# model.get_score(importance_type='weight')      # 被用作分裂的次数
# model.get_score(importance_type='gain')        # 平均增益（推荐）
# model.get_score(importance_type='cover')       # 平均覆盖
```

### 快速 XGBoost（sklearn 接口）

```python
from xgboost import XGBRegressor

xgb_model = XGBRegressor(n_estimators=200, learning_rate=0.1,
                         max_depth=6, random_state=42)
xgb_model.fit(X_train, y_train)
y_pred = xgb_model.predict(X_test)
```

### 时序特殊处理

```python
# 滑动窗口构造监督学习样本
def create_sequences(data, lookback):
    """data: 1D array, lookback: 用过去多少步预测下一步"""
    X, y = [], []
    for i in range(lookback, len(data)):
        X.append(data[i-lookback:i])
        y.append(data[i])
    return np.array(X), np.array(y)
```

---

## 六、LSTM（深度学习时序预测）

### 适用：长序列（>500 点）、复杂非线性模式

```python
import torch
import torch.nn as nn
import numpy as np

class LSTMPredictor(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                           batch_first=True, dropout=dropout)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        # x: (batch, seq_len, input_size)
        out, (hn, cn) = self.lstm(x)
        return self.fc(out[:, -1, :])  # 只取最后一步

# 训练骨架
def train_lstm(model, train_loader, val_loader, epochs=100, lr=0.001):
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    for epoch in range(epochs):
        model.train()
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            loss = criterion(model(X_batch).squeeze(), y_batch)
            loss.backward()
            optimizer.step()
        # 验证...
```

### LSTM 审核重点
- [ ] 数据和标签已标准化（切记！）
- [ ] 训练/验证/测试严格按时间分割
- [ ] 防止过拟合：Dropout + 早停（patience=10）
- [ ] 超参：hidden_size 64-256, num_layers 1-3, lr 1e-3~1e-4

---

## 七、Prophet（Meta 开源时序工具）

### 适用：有明确周期（日/周/年）+ 节假日 + 趋势突变点

```python
from prophet import Prophet
import pandas as pd

# 数据必须是两列：ds（日期）, y（值）
df = pd.DataFrame({'ds': dates, 'y': values})

# 模型：加法年季节 + 加法周季节 + 自动假期
model = Prophet(
    yearly_seasonality=True,   # 年周期（适合月度以上数据）
    weekly_seasonality=True,   # 周周期（适合日数据）
    daily_seasonality=False,   # 日周期（适合小时数据）
    changepoint_prior_scale=0.05,  # 趋势灵活度：越小越平滑
    seasonality_prior_scale=10.0    # 季节强度：越大越灵活
)
model.fit(df)

# 预测
future = model.make_future_dataframe(periods=30)  # 预测未来 30 天
forecast = model.predict(future)

# 输出含 yhat（预测值）, yhat_lower, yhat_upper（置信区间）
# 可视化
fig = model.plot(forecast)       # 时序图
fig2 = model.plot_components(forecast)  # 趋势 + 季节分解
```

### Prophet 审核重点
- [ ] changepoint_prior_scale 是否合理（0.001~0.5，默认 0.05）
- [ ] 节假日效果是否添加（如有）
- [ ] 趋势突变点是否合理（模型自动检测或手动指定）
- [ ] 不确定性区间是否合理（默认 80% 区间可能过窄）

---

## 八、灰色预测 GM(1,1)

### 适用：极少数据（4-10 点）、指数趋势

```python
import numpy as np

def gm11(x0, forecast_steps=1):
    """x0: 原始序列 (1D array)，返回预测值和后验差比"""
    # 1-AGO 累加生成
    x1 = np.cumsum(x0)
    n = len(x0)
    # 构造 B 矩阵和 Y 向量
    B = np.column_stack([-0.5*(x1[:-1] + x1[1:]), np.ones(n-1)])
    Y = x0[1:]
    # 最小二乘估计参数
    a, b = np.linalg.lstsq(B, Y, rcond=None)[0]
    # 预测 x1
    def pred_x1(k):
        return (x0[0] - b/a) * np.exp(-a*k) + b/a if a != 0 else x0[0] + b*k
    # 还原
    x1_pred = np.array([pred_x1(k) for k in range(n + forecast_steps)])
    x0_pred = np.diff(x1_pred, prepend=0)
    # 后验差检验
    e = x0 - x0_pred[:n]
    C = e.std() / x0.std()  # C < 0.35 好, < 0.5 合格, < 0.65 勉强
    return x0_pred, C
```

---

## 预测通用审核清单

1. 回测协议遵守：时间序列使用时序分割（！！！）
2. 至少报告 RMSE + MAE + MAPE（三个都报，不只一个）
3. 基准模型对比（至少与 naive 预测/线性回归对比）
4. 残差检验：白噪声（时序）、正态性（回归）
5. 预测区间已报告（点预测+区间，不只是点）
6. 长期预测的退化已讨论（预测步数越远越不准）
7. 过拟合检查（训练 vs 验证指标差距 > 30% = 过拟合）

### 常见全局坑
1. **用未来信息预测过去**：测试集归一化时用了测试集自己的统计量 → 数据泄露 → 结果不可信
2. **MAPE 存在除零**：真实值含 0 → MAPE 无穷大 → 不报
3. **随机打乱时序**：时间序列的交叉验证必须用 TimeSeriesSplit
4. **不报预测区间只报点预测**：预测必然有不确定性，不报区间等于隐瞒模型风险
