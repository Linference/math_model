#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q3: 相关性分析 — 量化设备相关行为与学业成绩的关系
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

# ===== 关键变量定义 =====
# 核心自变量: studytime(学习时间), freetime(自由时间), goout(社交外出)
# 因变量: G3(期末成绩)
# 控制变量: failures(过去不及格), absences(缺勤), Dalc+Walc(酒精消费)

key_vars = ['studytime', 'freetime', 'goout', 'Dalc', 'Walc', 'absences', 'failures', 'G1', 'G2', 'G3']
var_labels = {
    'studytime': '学习时间', 'freetime': '自由时间', 'goout': '社交外出',
    'Dalc': '工作日饮酒', 'Walc': '周末饮酒', 'absences': '缺勤次数',
    'failures': '不及格次数', 'G1': '阶段一成绩', 'G2': '阶段二成绩', 'G3': '期末成绩'
}

# ===== 1. Spearman 相关矩阵 (数据非正态, 用Spearman) =====
print("="*60)
print("Spearman 秩相关矩阵")
print("="*60)
corr_matrix = df[key_vars].corr(method='spearman')
print(corr_matrix['G3'].sort_values(ascending=False).to_string())

# ===== 2. 逐对相关分析 (Spearman + p值 + 95%CI) =====
print("\n" + "="*60)
print("核心变量与G3的Spearman相关逐对检验")
print("="*60)
predictors = ['studytime', 'freetime', 'goout', 'Dalc', 'Walc', 'absences', 'failures']
results = []
for var in predictors:
    r, p = spearmanr(df[var], df['G3'])
    n = len(df)
    # Fisher z 变换求 CI
    z = np.arctanh(r)
    se = 1 / np.sqrt(n - 3)
    z_lo, z_hi = z - 1.96*se, z + 1.96*se
    ci_lo, ci_hi = np.tanh(z_lo), np.tanh(z_hi)
    results.append({
        '变量': var_labels.get(var, var),
        'Spearman ρ': round(r, 4),
        'p值': f'{p:.4f}' if p >= 0.0001 else '<0.0001',
        '95% CI': f'[{ci_lo:.3f}, {ci_hi:.3f}]',
        '显著性': '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else 'n.s.'))
    })
    print(f"{var_labels.get(var, var):10s}: ρ={r:+.4f}, p={p:.4f}, 95%CI=[{ci_lo:.3f}, {ci_hi:.3f}]")

# ===== 3. 偏相关分析 (控制混杂变量) =====
print("\n" + "="*60)
print("偏相关分析 (控制: failures, absences, Dalc, Walc)")
print("="*60)
from scipy.stats import pearsonr

def partial_corr(df, x, y, controls):
    """计算偏相关系数"""
    all_vars = [x, y] + controls
    data = df[all_vars].dropna()
    # 方法: 回归残差法
    import statsmodels.api as sm
    # X 对 controls 回归
    X_ctrl = sm.add_constant(data[controls])
    model_x = sm.OLS(data[x], X_ctrl).fit()
    resid_x = model_x.resid
    # Y 对 controls 回归
    model_y = sm.OLS(data[y], X_ctrl).fit()
    resid_y = model_y.resid
    # 残差的 Pearson 相关即偏相关
    r, p = pearsonr(resid_x, resid_y)
    return r, p

controls = ['failures', 'absences', 'Dalc', 'Walc']
for var in ['studytime', 'freetime', 'goout']:
    r, p = partial_corr(df, var, 'G3', controls)
    print(f"{var_labels.get(var, var):10s}: 偏相关 r={r:+.4f}, p={p:.4f}")

# ===== 4. 分组分析: 有/无网络的家庭 =====
print("\n" + "="*60)
print("分组比较: 有网络 vs 无网络")
print("="*60)
for var in ['G3', 'studytime', 'freetime', 'goout']:
    g_yes = df[df['internet'] == 'yes'][var]
    g_no = df[df['internet'] == 'no'][var]
    stat, p = stats.mannwhitneyu(g_yes, g_no, alternative='two-sided')
    d = (g_yes.mean() - g_no.mean()) / df[var].std()  # Cohen's d
    print(f"{var_labels.get(var, var):10s}: 有网络={g_yes.mean():.2f}, 无网络={g_no.mean():.2f}, d={d:+.3f}, p={p:.4f}")

# ===== 5. 相关性热力图 =====
fig, ax = plt.subplots(figsize=(10, 8))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdBu_r',
            center=0, vmin=-0.5, vmax=0.5, mask=mask,
            xticklabels=[var_labels.get(v, v) for v in key_vars],
            yticklabels=[var_labels.get(v, v) for v in key_vars],
            ax=ax, cbar_kws={'label': "Spearman's ρ"})
ax.set_title('图1: 变量间Spearman相关热力图', fontsize=14, fontweight='bold')
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, 'fig_q3_correlation_heatmap.png'), dpi=300)
plt.close()
print("\n✅ 图1已保存: fig_q3_correlation_heatmap.png")

# ===== 6. 散点图矩阵 =====
fig, axes = plt.subplots(2, 3, figsize=(14, 9))
axes = axes.flatten()
plot_pairs = [
    ('studytime', 'G3', '学习时间 vs 期末成绩'),
    ('freetime', 'G3', '自由时间 vs 期末成绩'),
    ('goout', 'G3', '社交外出 vs 期末成绩'),
    ('absences', 'G3', '缺勤次数 vs 期末成绩'),
    ('failures', 'G3', '不及格次数 vs 期末成绩'),
]
for i, (x, y, title) in enumerate(plot_pairs):
    ax = axes[i]
    ax.scatter(df[x] + np.random.normal(0, 0.05, len(df)),
               df[y] + np.random.normal(0, 0.05, len(df)),
               alpha=0.3, s=8, color='#2C7BB6')
    # 添加 LOWESS 平滑线
    try:
        from statsmodels.nonparametric.smoothers_lowess import lowess
        xy = df[[x, y]].dropna()
        smooth = lowess(xy[y], xy[x], frac=0.5)
        ax.plot(smooth[:, 0], smooth[:, 1], 'r-', linewidth=2, label='LOWESS')
    except:
        pass
    r, p = spearmanr(df[x], df[y])
    ax.set_xlabel(var_labels.get(x, x))
    ax.set_ylabel(var_labels.get(y, y))
    ax.set_title(f'{title}\nρ={r:+.3f}, p={p:.4f}')
    ax.legend(fontsize=7)
axes[-1].axis('off')
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, 'fig_q3_scatter_matrix.png'), dpi=300)
plt.close()
print("✅ 图2已保存: fig_q3_scatter_matrix.png")

print("\n✅ Q3 相关性分析完成")
