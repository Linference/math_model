#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电子设备使用对学习的影响分析 — 完整分析流水线
Q2: 描述性统计 → Q3: 相关性分析 → Q4: 量化回归模型
数据: 模拟问卷数据 (n=250), ⚠ 标注为模拟数据
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
matplotlib.rcParams['axes.unicode_minus'] = False
import seaborn as sns
from scipy import stats
from scipy.stats import pearsonr, spearmanr, shapiro
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import os, sys

np.random.seed(42)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(DATA_DIR, '..', 'figures')
df = pd.read_csv(os.path.join(DATA_DIR, '..', 'data', 'survey_data.csv'))

device_vars = ['手机_学习使用_小时', '手机_娱乐使用_小时', '电脑_学习使用_小时',
               '电脑_娱乐使用_小时', '平板_学习使用_小时', '平板_娱乐使用_小时']
control_vars = ['睡眠时长_小时', '自主学习时长_小时', '自控力_1到5']
all_pred = device_vars + control_vars
target = '考试总分'

print("=" * 60)
print("Q2: 描述性统计")
print("=" * 60)
print(f"样本量: n = {len(df)}")
print(f"\n考试总分: M={df[target].mean():.1f}, SD={df[target].std():.1f}, "
      f"范围=[{df[target].min():.1f}, {df[target].max():.1f}]")

# 按设备类型汇总
print("\n--- 设备使用时长汇总 (小时/天) ---")
for v in device_vars:
    print(f"  {v}: M={df[v].mean():.2f}, SD={df[v].std():.2f}, "
          f"中位数={df[v].median():.2f}, 范围=[{df[v].min():.1f}, {df[v].max():.1f}]")

# 总娱乐时长 vs 总学习时长
df['总娱乐时长'] = df['手机_娱乐使用_小时'] + df['电脑_娱乐使用_小时'] + df['平板_娱乐使用_小时']
df['总学习使用时长'] = df['手机_学习使用_小时'] + df['电脑_学习使用_小时'] + df['平板_学习使用_小时']
print(f"\n总娱乐时长(手机+电脑+平板): M={df['总娱乐时长'].mean():.2f}h, SD={df['总娱乐时长'].std():.2f}h")
print(f"总学习使用时长: M={df['总学习使用时长'].mean():.2f}h, SD={df['总学习使用时长'].std():.2f}h")

# 正态性检验
print("\n--- Shapiro-Wilk 正态性检验 ---")
for v in [target] + all_pred:
    s, p = shapiro(df[v])
    print(f"  {v}: W={s:.4f}, p={p:.4f} {'⚠ 非正态' if p < 0.05 else '✓'}")

# 按性别的分组统计
print("\n--- 按性别分组 ---")
for v in [target, '总娱乐时长', '总学习使用时长']:
    m = df[df['性别']=='男'][v].mean()
    f = df[df['性别']=='女'][v].mean()
    stat, p = stats.mannwhitneyu(df[df['性别']=='男'][v], df[df['性别']=='女'][v])
    d = (m - f) / df[v].std()
    print(f"  {v}: 男={m:.1f}, 女={f:.1f}, d={d:+.3f}, p={p:.4f}")

print("\n" + "=" * 60)
print("Q3: 相关性分析")
print("=" * 60)

# Pearson 相关矩阵（样本量足够，CLT适用）
corr_vars = [target] + all_pred
corr_matrix = df[corr_vars].corr()

print("\n--- 各变量与考试总分的 Pearson 相关系数 ---")
results = []
for v in all_pred:
    r, p = pearsonr(df[v], df[target])
    n = len(df)
    z = np.arctanh(r); se = 1/np.sqrt(n-3)
    ci_lo, ci_hi = np.tanh(z-1.96*se), np.tanh(z+1.96*se)
    effect = '|r|>0.3' if abs(r)>0.3 else ('|r|>0.1' if abs(r)>0.1 else '可忽略')
    stars = '***' if p<0.001 else ('**' if p<0.01 else ('*' if p<0.05 else 'n.s.'))
    results.append({'变量': v, 'r': r, 'p': p, 'CI': f'[{ci_lo:.3f},{ci_hi:.3f}]', '显著性': stars})
    print(f"  {v:15s}: r={r:+.4f}, p={p:.4f}, 95%CI=[{ci_lo:.3f},{ci_hi:.3f}] {stars}")

# 偏相关（控制：睡眠、自主学习和自控力）
print("\n--- 偏相关分析 (控制: 睡眠+自主学习+自控力) ---")
for v in device_vars:
    ctrls = ['睡眠时长_小时', '自主学习时长_小时', '自控力_1到5']
    data = df[[v, target] + ctrls].dropna()
    X_ctrl = sm.add_constant(data[ctrls])
    resid_v = sm.OLS(data[v], X_ctrl).fit().resid
    resid_t = sm.OLS(data[target], X_ctrl).fit().resid
    r_partial, p_partial = pearsonr(resid_v, resid_t)
    print(f"  {v:15s}: r_partial={r_partial:+.4f}, p={p_partial:.4f}")

# 热力图
fig, ax = plt.subplots(figsize=(10, 8))
short_names = ['考试总分','手机学','手机娱','电脑学','电脑娱','平板学','平板娱','睡眠','自学','自控']
plot_vars = [target] + all_pred
plot_corr = df[plot_vars].corr()
mask = np.triu(np.ones_like(plot_corr, dtype=bool), k=1)
sns.heatmap(plot_corr, annot=True, fmt='.3f', cmap='RdBu_r', center=0,
            vmin=-0.3, vmax=0.3, mask=mask,
            xticklabels=short_names, yticklabels=short_names, ax=ax)
ax.set_title('各变量间 Pearson 相关系数矩阵', fontsize=14)
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, 'fig_correlation_heatmap.png'), dpi=300)
plt.close()
print("\n✅ 热力图已保存")

# 散点图：关键变量 vs 考试总分
fig, axes = plt.subplots(2, 3, figsize=(14, 9))
key_pairs = [
    ('手机_娱乐使用_小时', '考试总分', '手机娱乐时长 vs 考试总分'),
    ('电脑_娱乐使用_小时', '考试总分', '电脑娱乐时长 vs 考试总分'),
    ('总娱乐时长', '考试总分', '总娱乐时长 vs 考试总分'),
    ('手机_学习使用_小时', '考试总分', '手机学习时长 vs 考试总分'),
    ('自主学习时长_小时', '考试总分', '自主学习时长 vs 考试总分'),
    ('睡眠时长_小时', '考试总分', '睡眠时长 vs 考试总分'),
]
for i, (x, y, title) in enumerate(key_pairs):
    ax = axes.flat[i]
    ax.scatter(df[x], df[y], alpha=0.5, s=15, color='#2C7BB6')
    r, p = pearsonr(df[x], df[y])
    # 拟合线
    m, b = np.polyfit(df[x], df[y], 1)
    xs = np.linspace(df[x].min(), df[x].max(), 100)
    ax.plot(xs, m*xs+b, 'r-', linewidth=2, alpha=0.7)
    ax.set_xlabel(x.replace('_',' '))
    ax.set_ylabel('考试总分')
    ax.set_title(f'{title}\nr={r:+.3f}, p={p:.4f}')
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, 'fig_scatter_panels.png'), dpi=300)
plt.close()
print("✅ 散点图矩阵已保存")

print("\n" + "=" * 60)
print("Q4: 量化回归模型")
print("=" * 60)

# 模型1: 仅设备使用变量
X1 = sm.add_constant(df[device_vars])
y = df[target]
m1 = sm.OLS(y, X1).fit()
print(f"\n模型1 (仅设备使用): R²={m1.rsquared:.4f}, Adj R²={m1.rsquared_adj:.4f}, F={m1.fvalue:.1f}, p={m1.f_pvalue:.4f}")

# 模型2: 设备使用 + 控制变量
X2 = sm.add_constant(df[all_pred])
m2 = sm.OLS(y, X2).fit()
print(f"模型2 (设备+控制): R²={m2.rsquared:.4f}, Adj R²={m2.rsquared_adj:.4f}, F={m2.fvalue:.1f}, p={m2.f_pvalue:.4f}")
print(f"ΔR² = {m2.rsquared - m1.rsquared:.4f}")

print("\n--- 模型2 回归系数 ---")
coef_df = pd.DataFrame({
    '变量': ['截距'] + all_pred,
    '系数β': m2.params.values.round(4),
    '标准误': m2.bse.values.round(4),
    't值': m2.tvalues.values.round(2),
    'p值': [f'{p:.4f}' if p>=0.0001 else '<0.0001' for p in m2.pvalues.values],
    '显著性': ['***' if p<0.001 else ('**' if p<0.01 else ('*' if p<0.05 else '')) for p in m2.pvalues.values]
})
print(coef_df.to_string(index=False))

# 标准化系数
X_std = (X2.iloc[:,1:] - X2.iloc[:,1:].mean()) / X2.iloc[:,1:].std()
y_std = (y - y.mean()) / y.std()
m_std = sm.OLS(y_std, sm.add_constant(X_std)).fit()
print("\n--- 标准化回归系数 (β*) ---")
for v, b in zip(all_pred, m_std.params[1:]):
    print(f"  {v:15s}: β*={b:+.4f}")

# VIF
print("\n--- 多重共线性诊断 (VIF) ---")
for i, v in enumerate(['截距'] + all_pred):
    vif = variance_inflation_factor(X2.values, i) if i > 0 else np.nan
    flag = ' ⚠' if (vif and vif > 5) else ''
    print(f"  {v:15s}: VIF={vif:.2f}{flag}" if vif else f"  {v:15s}: VIF=—")

# 效应量
f2 = m2.rsquared / (1 - m2.rsquared)
print(f"\nCohen's f² = {f2:.4f} ({'大' if f2>0.35 else '中' if f2>0.15 else '小'}效应)")

# 模型诊断图
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
resid = m2.resid; fitted = m2.fittedvalues
axes[0,0].scatter(fitted, resid, alpha=0.4, s=8, color='#2C7BB6')
axes[0,0].axhline(y=0, color='r', linestyle='--'); axes[0,0].set_xlabel('拟合值'); axes[0,0].set_ylabel('残差')
axes[0,0].set_title('残差 vs 拟合值')
sm.qqplot(resid, stats.norm, fit=True, line='45', ax=axes[0,1], markerfacecolor='#2C7BB6', markeredgecolor='none', alpha=0.5)
axes[0,1].set_title('Q-Q图 (残差正态性)')
axes[1,0].hist(resid/np.std(resid), bins=25, color='#2C7BB6', alpha=0.7, edgecolor='white')
axes[1,0].axvline(x=0, color='r', linestyle='--'); axes[1,0].set_xlabel('标准化残差'); axes[1,0].set_title('残差分布')
cooks = m2.get_influence().cooks_distance[0]
axes[1,1].stem(range(len(cooks)), cooks, markerfmt=',', linefmt='grey'); axes[1,1].axhline(y=4/len(df), color='r', linestyle='--')
axes[1,1].set_xlabel('观测序号'); axes[1,1].set_title("Cook's距离")
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, 'fig_regression_diagnostics.png'), dpi=300)
plt.close()
print("✅ 回归诊断图已保存")

# 系数森林图
fig, ax = plt.subplots(figsize=(9, 5))
coefs_m2 = m2.params[1:]; errors_m2 = m2.bse[1:]
short_lbl = ['手机学习','手机娱乐','电脑学习','电脑娱乐','平板学习','平板娱乐','睡眠时长','自主学习','自控力']
colors = ['#D7191C' if c<0 else '#2C7BB6' for c in coefs_m2]
ax.barh(range(len(coefs_m2)), coefs_m2, xerr=[e*1.96 for e in errors_m2], color=colors, alpha=0.8, height=0.6)
ax.set_yticks(range(len(coefs_m2))); ax.set_yticklabels(short_lbl)
ax.axvline(x=0, color='black', linewidth=0.8)
ax.set_xlabel('回归系数 β (95% CI)'); ax.set_title('各因素对考试总分的影响效应 (模型2)', fontsize=13)
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, 'fig_coefficient_forest.png'), dpi=300)
plt.close()
print("✅ 系数森林图已保存")

# 关键数值汇总
print("\n" + "=" * 60)
print("关键数值结果汇总 (供论文引用)")
print("=" * 60)
print(f"样本量: n={len(df)}")
print(f"手机娱乐时长均值: {df['手机_娱乐使用_小时'].mean():.1f}h/天")
print(f"总娱乐时长均值: {df['总娱乐时长'].mean():.1f}h/天")
print(f"考试总分均值: {df[target].mean():.1f}分")
print(f"手机娱乐 vs 总分: r={pearsonr(df['手机_娱乐使用_小时'], df[target])[0]:+.4f}")
print(f"总娱乐 vs 总分: r={pearsonr(df['总娱乐时长'], df[target])[0]:+.4f}")
print(f"自主学习 vs 总分: r={pearsonr(df['自主学习时长_小时'], df[target])[0]:+.4f}")
print(f"模型2 R²={m2.rsquared:.4f}, Adj R²={m2.rsquared_adj:.4f}")
print(f"Cohen's f²={f2:.4f}")
for v, b, p in zip(all_pred, m2.params[1:], m2.pvalues[1:]):
    if p < 0.1:
        print(f"  {v}: β={b:+.3f}, p={p:.4f}")
print("\n✅ 全部分析完成")
