#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q1: 数据加载与描述性统计分析
电子设备使用对学习的影响分析
数据集: UCI Student Performance (Cortez & Silva, 2008)
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import sys, os
from scipy import stats

np.random.seed(42)

# ===== 加载数据 =====
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
mat = pd.read_csv(os.path.join(DATA_DIR, '..', 'data', 'student-mat.csv'), sep=';')
por = pd.read_csv(os.path.join(DATA_DIR, '..', 'data', 'student-por.csv'), sep=';')
mat['subject'] = 'Math'
por['subject'] = 'Portuguese'
df = pd.concat([mat, por], ignore_index=True)
print(f"合并数据集: {df.shape[0]} 条记录, {df.shape[1]} 个变量")
print(f"数学: {mat.shape[0]} 条, 葡萄牙语: {por.shape[0]} 条")

# ===== Q2: 描述性统计分析 =====
print("\n" + "="*60)
print("描述性统计 — 核心连续变量")
print("="*60)

core_vars = ['studytime', 'freetime', 'goout', 'Dalc', 'Walc', 'absences', 'failures', 'G1', 'G2', 'G3']
desc = df[core_vars].describe().round(2)
desc.loc['skew'] = df[core_vars].skew().round(3)
desc.loc['kurtosis'] = df[core_vars].kurtosis().round(3)
desc.loc['missing'] = df[core_vars].isnull().sum()
print(desc.to_string())

# 缺失值报告
print(f"\n缺失值总计: {df[core_vars].isnull().sum().sum()}")

# 分组描述: 按网络接入
print("\n--- 按网络接入分组 ---")
for var in ['studytime', 'freetime', 'goout', 'G3']:
    g = df.groupby('internet')[var].agg(['mean', 'std', 'count'])
    print(f"\n{var}:")
    print(g.to_string())

# 异常值检测 (IQR方法)
print("\n" + "="*60)
print("异常值检测 (IQR方法)")
print("="*60)
for var in ['absences', 'G3', 'failures']:
    Q1, Q3 = df[var].quantile(0.25), df[var].quantile(0.75)
    IQR = Q3 - Q1
    lower, upper = Q1 - 1.5*IQR, Q3 + 1.5*IQR
    outliers = df[(df[var] < lower) | (df[var] > upper)]
    print(f"{var}: Q1={Q1:.1f}, Q3={Q3:.1f}, IQR={IQR:.1f}, 下限={lower:.1f}, 上限={upper:.1f}, 异常值={len(outliers)} ({len(outliers)/len(df)*100:.1f}%)")

# 正态性检验 (Shapiro-Wilk on G3)
print("\n" + "="*60)
print("正态性检验 (Shapiro-Wilk) — 指导 Pearson vs Spearman 选择")
print("="*60)
for var in ['G3', 'studytime', 'freetime', 'goout', 'absences']:
    stat, p = stats.shapiro(df[var].dropna().sample(min(500, len(df)), random_state=42))
    print(f"{var}: W={stat:.4f}, p={p:.4f}  {'⚠ 非正态' if p < 0.05 else '✅ 近似正态'}")

print("\n✅ Q1+Q2 分析完成")
