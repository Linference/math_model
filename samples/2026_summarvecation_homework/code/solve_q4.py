#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q4: 量化影响模型 — 多元回归 + 分位数回归 + 模型诊断
电子设备使用对学习的影响分析
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
import seaborn as sns
import sys, os
import statsmodels.api as sm
from scipy import stats
from scipy.stats import pearsonr, spearmanr

np.random.seed(42)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
mat = pd.read_csv(os.path.join(DATA_DIR, '..', 'data', 'student-mat.csv'), sep=';')
por = pd.read_csv(os.path.join(DATA_DIR, '..', 'data', 'student-por.csv'), sep=';')
mat['subject'] = 'Math'
por['subject'] = 'Portuguese'
df = pd.concat([mat, por], ignore_index=True)

# 加载绘图样式
style_path = os.path.join(DATA_DIR, 'figures.mplstyle')
if os.path.exists(style_path):
    plt.style.use(style_path)

FIG_DIR = os.path.join(DATA_DIR, '..', 'figures')

var_labels = {
    'studytime': '学习时间', 'freetime': '自由时间', 'goout': '社交外出',
    'Dalc': '工作日饮酒', 'Walc': '周末饮酒', 'absences': '缺勤次数',
    'failures': '不及格次数', 'G1': '阶段一成绩', 'G2': '阶段二成绩', 'G3': '期末成绩',
    'internet_yes': '有网络接入'
}

# ===== 1. 数据预处理 =====
# 编码分类变量
df_model = df.copy()
df_model['internet_yes'] = (df_model['internet'] == 'yes').astype(int)
df_model['sex_male'] = (df_model['sex'] == 'M').astype(int)
df_model['subject_math'] = (df_model['subject'] == 'Math').astype(int)

# ===== 2. 模型1: 基础OLS回归 (G3 ~ 时间分配变量 + 控制变量) =====
print("="*60)
print("模型1: 基础OLS回归")
print("="*60)
X_vars = ['studytime', 'freetime', 'goout', 'Dalc', 'Walc', 'absences', 'failures', 'internet_yes']
X = sm.add_constant(df_model[X_vars])
y = df_model['G3']

model1 = sm.OLS(y, X).fit()
print(model1.summary().tables[1])  # 系数表
print(f"\nR² = {model1.rsquared:.4f}, 调整R² = {model1.rsquared_adj:.4f}")
print(f"F = {model1.fvalue:.2f}, p = {model1.f_pvalue:.4f}")

# ===== 3. 多重共线性诊断 (VIF) =====
print("\n" + "="*60)
print("多重共线性诊断 (VIF)")
print("="*60)
from statsmodels.stats.outliers_influence import variance_inflation_factor
vif_data = pd.DataFrame({
    '变量': ['const'] + X_vars,
    'VIF': [np.nan] + [variance_inflation_factor(X.values, i+1) for i in range(len(X_vars))]
})
print(vif_data.to_string(index=False))

# ===== 4. 模型诊断图 =====
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# 残差 vs 拟合值
residuals = model1.resid
fitted = model1.fittedvalues
axes[0, 0].scatter(fitted, residuals, alpha=0.3, s=8, color='#2C7BB6')
axes[0, 0].axhline(y=0, color='r', linestyle='--', linewidth=1)
axes[0, 0].set_xlabel('拟合值')
axes[0, 0].set_ylabel('残差')
axes[0, 0].set_title('图3: 残差 vs 拟合值 (异方差检验)')

# Q-Q图
sm.qqplot(residuals, stats.norm, fit=True, line='45', ax=axes[0, 1], markerfacecolor='#2C7BB6', markeredgecolor='none', alpha=0.5)
axes[0, 1].set_title('图4: Q-Q图 (残差正态性检验)')

# 标准化残差
std_resid = residuals / np.std(residuals)
axes[1, 0].hist(std_resid, bins=30, color='#2C7BB6', alpha=0.7, edgecolor='white')
axes[1, 0].axvline(x=0, color='r', linestyle='--')
axes[1, 0].set_xlabel('标准化残差')
axes[1, 0].set_ylabel('频数')
axes[1, 0].set_title('标准化残差分布')

# Cook's距离
influence = model1.get_influence()
cooks = influence.cooks_distance[0]
axes[1, 1].stem(range(len(cooks)), cooks, markerfmt=',', linefmt='grey', basefmt=' ')
axes[1, 1].axhline(y=4/len(df), color='r', linestyle='--', label='4/n 阈值')
axes[1, 1].set_xlabel('观测序号')
axes[1, 1].set_ylabel("Cook's距离")
axes[1, 1].set_title("Cook's距离 (影响点检测)")
axes[1, 1].legend()
n_influential = (cooks > 4/len(df)).sum()

plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, 'fig_q4_model_diagnostics.png'), dpi=300)
plt.close()
print(f"\n✅ 图3+4已保存: fig_q4_model_diagnostics.png")
print(f"高影响力点: {n_influential} 个 (Cook's d > 4/n)")

# ===== 5. 效应量计算 =====
print("\n" + "="*60)
print("效应量分析 (标准化系数 + Cohen's f²)")
print("="*60)
# 标准化系数
X_std = (X.iloc[:, 1:] - X.iloc[:, 1:].mean()) / X.iloc[:, 1:].std()
y_std = (y - y.mean()) / y.std()
model_std = sm.OLS(y_std, sm.add_constant(X_std)).fit()
print("标准化回归系数 (β*):")
for var, coef in zip(X_vars, model_std.params[1:]):
    stars = '***' if model_std.pvalues[1:][var] < 0.001 else ('**' if model_std.pvalues[1:][var] < 0.01 else ('*' if model_std.pvalues[1:][var] < 0.05 else ''))
    print(f"  {var_labels.get(var, var):12s}: β*={coef:+.4f}{stars}")

# Cohen's f²
f2 = model1.rsquared / (1 - model1.rsquared)
print(f"\nCohen's f² = {f2:.4f} ({'大效应' if f2 > 0.35 else ('中效应' if f2 > 0.15 else '小效应')})")

# ===== 6. 模型2: 扩展模型 (加入人口学变量) =====
print("\n" + "="*60)
print("模型2: 扩展OLS (加入性别+学科+年龄)")
print("="*60)
X2_vars = X_vars + ['sex_male', 'subject_math', 'age']
X2 = sm.add_constant(df_model[X2_vars])
model2 = sm.OLS(y, X2).fit()
print(f"R² = {model2.rsquared:.4f}, 调整R² = {model2.rsquared_adj:.4f}")
print(f"ΔR² (vs M1) = {model2.rsquared - model1.rsquared:.4f}")

# ===== 7. 系数可视化 =====
fig, ax = plt.subplots(figsize=(10, 6))
coefs = model2.params[1:]
errors = model2.bse[1:]
y_pos = range(len(coefs))
colors = ['#D7191C' if c < 0 else '#2C7BB6' for c in coefs]
ax.barh(y_pos, coefs, xerr=errors*1.96, color=colors, alpha=0.8, height=0.6)
ax.set_yticks(y_pos)
ax.set_yticklabels([var_labels.get(v, v) for v in X2_vars])
ax.axvline(x=0, color='black', linewidth=0.8)
ax.set_xlabel('回归系数 (95% CI)')
ax.set_title('图5: 各因素对期末成绩(G3)的影响效应', fontsize=14, fontweight='bold')
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, 'fig_q4_coefficient_forest.png'), dpi=300)
plt.close()
print("✅ 图5已保存: fig_q4_coefficient_forest.png")

# ===== 8. 关键数值输出汇总 =====
print("\n" + "="*60)
print("关键数值结果汇总 (供论文引用)")
print("="*60)
print(f"样本量: n = {len(df)}")
print(f"Spearman ρ (学习时间→G3): {spearmanr(df['studytime'], df['G3'])[0]:+.4f}")
print(f"Spearman ρ (自由时间→G3): {spearmanr(df['freetime'], df['G3'])[0]:+.4f}")
print(f"Spearman ρ (社交外出→G3): {spearmanr(df['goout'], df['G3'])[0]:+.4f}")
print(f"Spearman ρ (不及格→G3): {spearmanr(df['failures'], df['G3'])[0]:+.4f}")
print(f"OLS R² (模型1) = {model1.rsquared:.4f}")
print(f"OLS 调整R² (模型1) = {model1.rsquared_adj:.4f}")
print(f"OLS R² (模型2) = {model2.rsquared:.4f}")
print(f"Cohen's f² = {f2:.4f}")
print(f"VIF 最大值 = {vif_data['VIF'][1:].max():.2f}")
print(f"高影响力点 = {n_influential}")

print("\n✅ Q4 量化模型分析完成")
