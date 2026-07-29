#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成模拟调查数据 — 电子设备使用对学习的影响分析
基于问卷设计（3设备类型 × 2使用目的 × 15题），生成 n=250 份模拟问卷数据
⚠ 模拟数据：所有数据均基于合理假设生成，论文中显著标注为"模拟数据"
"""
import numpy as np
import pandas as pd
import os

np.random.seed(42)

n = 250  # 样本量（基于 G*Power 计算，考虑 20% 无效问卷率后的发放量）

# ===== 1. 人口学变量 =====
grades = np.random.choice(['初一','初二','初三','高一','高二','高三'], n, p=[0.15,0.15,0.15,0.20,0.20,0.15])
sex = np.random.choice(['男','女'], n, p=[0.52, 0.48])

# ===== 2. 电子设备使用时長 (小时/天) — 基于合理分布 =====
# 手机娱乐：右偏分布，均值≈3h，多数人1-5h，少数人>6h
phone_ent = np.random.lognormal(mean=1.0, sigma=0.5, size=n)  # 中位数≈2.7h
phone_ent = np.clip(phone_ent, 0.2, 10)  # 截断到合理范围

# 手机学习：右偏但均值低，多数人0-1h
phone_study = np.random.lognormal(mean=-0.5, sigma=0.8, size=n)
phone_study = np.clip(phone_study, 0, 4)

# 电脑娱乐（游戏/视频）：右偏，均值≈1.5h
pc_ent = np.random.lognormal(mean=0.2, sigma=0.7, size=n)
pc_ent = np.clip(pc_ent, 0, 8)

# 电脑学习：正态-ish，均值≈1h
pc_study = np.random.lognormal(mean=-0.3, sigma=0.6, size=n)
pc_study = np.clip(pc_study, 0, 5)

# 平板娱乐：多数人没有或用得少
tablet_ent = np.random.exponential(scale=0.5, size=n)
tablet_ent = np.clip(tablet_ent, 0, 5)

# 平板学习：少数人使用
tablet_study = np.random.exponential(scale=0.3, size=n)
tablet_study = np.clip(tablet_study, 0, 3)

# ===== 3. 控制变量 =====
sleep_hrs = np.random.normal(7.5, 1.2, n)  # 睡眠均值7.5h
sleep_hrs = np.clip(sleep_hrs, 4, 11)

self_study = np.random.lognormal(mean=0.8, sigma=0.5, size=n)  # 自主学习均值≈2.5h
self_study = np.clip(self_study, 0.2, 8)

self_control = np.random.choice([1,2,3,4,5], n, p=[0.05,0.15,0.35,0.30,0.15])  # Likert 5点

# ===== 4. 生成考试成绩（含真实的与设备使用的相关性） =====
# 基础分数：75 ± 12，受多个因素影响
base_score = 75

# 各因素对成绩的影响权重（基于文献中的典型效应量）
# 负向影响：娱乐使用（手机>-0.5分/h, 电脑>-0.4分/h, 平板>-0.2分/h）
# 正向影响：学习使用（手机+0.3分/h, 电脑+0.4分/h, 平板+0.2分/h）
# 控制变量：睡眠+1.0分/h, 自主学习+2.0分/h, 自控力+2.5分/级
score = (base_score
         + (phone_study - phone_study.mean()) * 0.3
         + (phone_ent - phone_ent.mean()) * (-0.6)
         + (pc_study - pc_study.mean()) * 0.4
         + (pc_ent - pc_ent.mean()) * (-0.5)
         + (tablet_study - tablet_study.mean()) * 0.2
         + (tablet_ent - tablet_ent.mean()) * (-0.3)
         + (sleep_hrs - sleep_hrs.mean()) * 1.0
         + (self_study - self_study.mean()) * 2.0
         + (self_control - self_control.mean()) * 2.5
         + np.random.normal(0, 8, n))  # 随机噪声（不可解释变异）

score = np.clip(score, 10, 100).round(1)  # 截断到合理范围

# 排名区间
def score_to_rank(s):
    if s >= 85: return '前20%'
    elif s >= 70: return '20-40%'
    elif s >= 55: return '40-60%'
    elif s >= 40: return '60-80%'
    else: return '后20%'
rank_level = np.array([score_to_rank(s) for s in score])

# ===== 5. 家长管控（与成绩正相关） =====
parent_control_prob = 0.3 + 0.3 * (score - score.min()) / (score.max() - score.min())
parent_control = np.array(['是' if np.random.random() < p else '否' for p in parent_control_prob])

# ===== 6. 父母教育水平 =====
parent_edu_levels = ['初中及以下', '高中', '本科', '研究生']
parent_edu_probs = np.zeros((n, 4))
for i in range(n):
    # 成绩越好的学生，父母教育水平倾向于更高
    s_norm = (score[i] - score.mean()) / score.std()
    logits = np.array([-0.5, 0.2, 0.5, -0.2]) + s_norm * 0.4
    probs = np.exp(logits) / np.exp(logits).sum()
    parent_edu_probs[i] = probs
parent_edu = np.array([np.random.choice(parent_edu_levels, p=p) for p in parent_edu_probs])

# ===== 组装 DataFrame =====
df = pd.DataFrame({
    '年级': grades,
    '性别': sex,
    '睡眠时长_小时': sleep_hrs.round(1),
    '自主学习时长_小时': self_study.round(1),
    '手机_学习使用_小时': phone_study.round(1),
    '手机_娱乐使用_小时': phone_ent.round(1),
    '电脑_学习使用_小时': pc_study.round(1),
    '电脑_娱乐使用_小时': pc_ent.round(1),
    '平板_学习使用_小时': tablet_study.round(1),
    '平板_娱乐使用_小时': tablet_ent.round(1),
    '考试总分': score,
    '排名区间': rank_level,
    '自控力_1到5': self_control,
    '父母教育水平': parent_edu,
    '家长管控设备': parent_control,
})

# 保存
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(DATA_DIR, '..', 'data', 'survey_data.csv')
df.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"✅ 模拟调查数据已生成: {output_path}")
print(f"   样本量: n={len(df)}")
print(f"   变量数: {len(df.columns)}")
print(f"\n描述性统计:")
print(df.describe().round(2).to_string())
print(f"\n相关性矩阵 (Pearson):")
num_cols = df.select_dtypes(include=[np.number]).columns
print(df[num_cols].corr().round(3).to_string())
