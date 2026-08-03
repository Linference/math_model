"""
问题4b — 12项火灾安全技术 AHP 评估
模型: Analytic Hierarchy Process (AHP), 5维度评分
算法: 幂法求权重 + CR一致性检验 + 加权排序
随机种子: 42
"""

import numpy as np
import json
import os
import sys

np.random.seed(42)

# ============================================================
# 12 项技术定义
# ============================================================

TECHNOLOGIES = [
    {'id': 'T1',  'name': 'Thermal Imaging Camera (TIC)',
     'desc': 'Handheld IR camera for locating victims through smoke'},
    {'id': 'T2',  'name': 'SCBA with Extended Duration',
     'desc': 'Self-contained breathing apparatus with 60+ min air supply'},
    {'id': 'T3',  'name': 'AI-Powered Search Path Optimizer',
     'desc': 'ML algorithm suggesting optimal room search order in real-time'},
    {'id': 'T4',  'name': 'Personal Alert Safety System (PASS)',
     'desc': 'Motion-sensing distress alarm worn by firefighters'},
    {'id': 'T5',  'name': 'Drone-Assisted Overwatch',
     'desc': 'Quadcopter providing aerial thermal feed of building exterior'},
    {'id': 'T6',  'name': 'Augmented Reality (AR) Helmet Display',
     'desc': 'HUD showing building map, teammate locations, and air status'},
    {'id': 'T7',  'name': 'Robotic Search Unit (Ground)',
     'desc': 'Tracked robot for searching hazardous/confined areas'},
    {'id': 'T8',  'name': 'Smart Floor Sensors (IoT)',
     'desc': 'Pressure/temp sensors embedded in floors detecting occupant locations'},
    {'id': 'T9',  'name': 'LiDAR Building Scanner',
     'desc': 'Pre-incident 3D mapping for precise navigation in zero visibility'},
    {'id': 'T10', 'name': 'Acoustic Victim Locator',
     'desc': 'Directional microphone array detecting faint sounds (tapping, breathing)'},
    {'id': 'T11', 'name': 'Wearable Biometric Monitor',
     'desc': 'Wristband tracking heart rate, core temp, and exertion of firefighters'},
    {'id': 'T12', 'name': 'Automatic Door/Wedge System',
     'desc': 'Remote-controlled door chocks maintaining egress path for retreat'},
]

# ============================================================
# 5 个评估准则
# ============================================================

CRITERIA = [
    {'id': 'C1', 'name': 'Search Speed Improvement',
     'desc': 'Reduction in time to complete primary search', 'type': 'benefit'},
    {'id': 'C2', 'name': 'Victim Detection Rate',
     'desc': 'Increase in probability of finding all occupants', 'type': 'benefit'},
    {'id': 'C3', 'name': 'Firefighter Safety',
     'desc': 'Reduction in risk of injury, disorientation, or fatality', 'type': 'benefit'},
    {'id': 'C4', 'name': 'Cost & Logistics',
     'desc': 'Acquisition cost, training burden, maintenance overhead', 'type': 'cost'},
    {'id': 'C5', 'name': 'Operational Reliability',
     'desc': 'Performance under extreme heat, smoke, water exposure', 'type': 'benefit'},
]

# ============================================================
# 成对比较矩阵 (Saaty 1-9 scale)
# ============================================================
# 准则层比较矩阵 (5×5)
# 基于题目设定: Safety > Detection > Speed > Reliability > Cost
CRITERIA_PAIRWISE = np.array([
    #   C1-Speed  C2-Detect  C3-Safety  C4-Cost  C5-Reliability
    [1,    1/3,   1/5,   3,    1/2],   # C1: Speed
    [3,    1,     1/3,   5,    2  ],   # C2: Detection
    [5,    3,     1,     7,    4  ],   # C3: Safety (most important)
    [1/3,  1/5,   1/7,   1,    1/3],   # C4: Cost (least important)
    [2,    1/2,   1/4,   3,    1  ],   # C5: Reliability
])

# 12项技术 × 5准则的评分矩阵 (1-9 scale, 专家/文献评估)
# 行=技术, 列=准则 C1..C5
TECH_SCORES = np.array([
    # C1-Speed  C2-Detect  C3-Safety  C4-Cost_inv  C5-Reliability
    [7,    8,    5,    7,    8],    # T1: TIC - good for detection + reliability
    [3,    2,    9,    4,    8],    # T2: SCBA - primarily safety
    [9,    7,    4,    3,    6],    # T3: AI Path Optimizer - best for speed
    [2,    3,    8,    7,    7],    # T4: PASS - primarily safety
    [6,    8,    5,    4,    5],    # T5: Drone - good detection
    [8,    6,    7,    3,    5],    # T6: AR Helmet - speed + safety
    [3,    7,    6,    2,    6],    # T7: Robot - detection + safety
    [5,    9,    5,    3,    4],    # T8: IoT Sensors - best detection
    [7,    5,    6,    2,    7],    # T9: LiDAR - speed + reliability
    [4,    8,    3,    5,    5],    # T10: Acoustic - detection focused
    [3,    3,    8,    6,    6],    # T11: Biometric - safety focused
    [3,    2,    7,    6,    8],    # T12: Door Wedge - safety + reliability
])

# ============================================================
# AHP 核心函数
# ============================================================

def ahp_power_method(matrix, max_iter=1000, tol=1e-9):
    """
    幂法求最大特征值和对应特征向量（权重）。
    矩阵需为正互反矩阵 (positive reciprocal)。
    返回: (weights, lambda_max)
    """
    n = matrix.shape[0]
    # 初始向量
    w = np.ones(n) / n
    for _ in range(max_iter):
        w_new = matrix @ w
        w_new = w_new / np.sum(w_new)
        if np.linalg.norm(w_new - w) < tol:
            w = w_new
            break
        w = w_new

    # Rayleigh quotient 求最大特征值
    Aw = matrix @ w
    lambda_max = np.sum(Aw / w) / n

    return w, lambda_max


def consistency_ratio(matrix, weights=None, lambda_max=None):
    """
    CR = CI / RI
    CI = (lambda_max - n) / (n - 1)
    RI: 随机一致性指标 (Saaty)
    """
    n = matrix.shape[0]

    if weights is None or lambda_max is None:
        weights, lambda_max = ahp_power_method(matrix)

    CI = (lambda_max - n) / (n - 1)

    # Saaty 随机一致性指标 RI
    RI_table = {1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
                6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
                11: 1.51, 12: 1.48, 13: 1.56, 14: 1.57, 15: 1.59}
    RI = RI_table.get(n, 1.5)

    CR = CI / RI if RI > 0 else 0.0
    return CI, CR, RI


def ahp_evaluate(criteria_matrix, tech_scores):
    """
    完整 AHP 评估流程:
    1. 计算准则权重 (幂法)
    2. CR 一致性检验
    3. 加权求和 → 技术排序
    返回: (criteria_weights, tech_scores_norm, final_scores, diagnostics)
    """
    n_criteria = criteria_matrix.shape[0]
    n_techs = tech_scores.shape[0]

    # Step 1: 准则权重
    crit_weights, lambda_max = ahp_power_method(criteria_matrix)
    CI, CR, RI = consistency_ratio(criteria_matrix, crit_weights, lambda_max)

    # Step 2: 技术评分归一化 (每列归一化: score / col_max)
    # 注意: C4 (Cost) 已经按倒数处理（越高越好），如果是原始成本需取倒数
    tech_scores_norm = tech_scores.astype(float) / tech_scores.max(axis=0)

    # Step 3: 加权求和
    final_scores = tech_scores_norm @ crit_weights

    # 排序
    ranking = np.argsort(-final_scores)

    diagnostics = {
        'lambda_max': lambda_max,
        'CI': CI,
        'CR': CR,
        'RI': RI,
        'consistent': CR < 0.10,  # Saaty: CR < 0.10 可接受
    }

    return crit_weights, tech_scores_norm, final_scores, ranking, diagnostics


# ============================================================
# 灵敏度分析: 准则权重扰动
# ============================================================

def sensitivity_weights(criteria_matrix, tech_scores, n_perturb=11):
    """
    对每个准则权重做 ±20% 扰动，观察技术排名变化。
    """
    base_weights, _, base_scores, base_ranking, _ = ahp_evaluate(criteria_matrix, tech_scores)
    n_criteria = len(base_weights)
    n_techs = tech_scores.shape[0]

    sensitivity = {}
    tech_names = [t['name'] for t in TECHNOLOGIES]

    for c in range(n_criteria):
        cname = CRITERIA[c]['name']
        sens_data = {'perturbations': [], 'rank_changes': []}

        for alpha in np.linspace(0.70, 1.30, n_perturb):
            perturbed_weights = base_weights.copy()
            perturbed_weights[c] *= alpha
            perturbed_weights /= perturbed_weights.sum()

            tech_norm = tech_scores.astype(float) / tech_scores.max(axis=0)
            new_scores = tech_norm @ perturbed_weights
            new_ranking = np.argsort(-new_scores)

            # 排名变化 (Kendall tau)
            rank_corr = np.corrcoef(base_scores, new_scores)[0, 1]
            n_swaps = np.sum(base_ranking != new_ranking)

            sens_data['perturbations'].append({
                'alpha': round(alpha, 2),
                'weights': perturbed_weights.tolist(),
                'top_3': [tech_names[i] for i in new_ranking[:3]],
                'rank_correlation': round(float(rank_corr), 4),
                'rank_swaps': int(n_swaps),
            })

        sensitivity[cname] = sens_data

    return sensitivity


# ============================================================
# 主程序
# ============================================================
if __name__ == '__main__':
    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT = os.path.join(BASE, 'code', 'outputs')

    print("=" * 60)
    print("  Q4b: 12项火灾安全技术 AHP 评估")
    print("=" * 60)

    # ---- 1. 准则权重 ----
    print("\n[1] 准则成对比较矩阵 (5×5):")
    crit_names = [c['name'] for c in CRITERIA]
    for i, row in enumerate(CRITERIA_PAIRWISE):
        print(f"  {crit_names[i]}: {row}")

    # ---- 2. AHP 计算 ----
    print("\n[2] AHP 权重计算 (幂法)...")
    crit_weights, tech_scores_norm, final_scores, ranking, diag = ahp_evaluate(
        CRITERIA_PAIRWISE, TECH_SCORES
    )

    print(f"\n  最大特征值 λ_max = {diag['lambda_max']:.4f}")
    print(f"  CI = {diag['CI']:.4f}")
    print(f"  RI = {diag['RI']:.4f}")
    status_str = 'OK (<0.10)' if diag['consistent'] else 'FAIL (>=0.10)'
    print(f"  CR = {diag['CR']:.4f} {status_str}")

    # 准则权重
    print("\n  准则权重:")
    for i, cn in enumerate(crit_names):
        bar = '█' * int(crit_weights[i] * 40)
        print(f"    {cn}: {crit_weights[i]:.4f}  {bar}")

    # ---- 3. 技术排序 ----
    print("\n[3] 技术加权排名:")
    print(f"  {'排名':<5} {'技术':<42} {'得分':>8}  {'评级'}")
    print(f"  {'-'*5} {'-'*42} {'-'*8}  {'-'*4}")

    for rank, idx in enumerate(ranking):
        tech = TECHNOLOGIES[idx]
        score = final_scores[idx]
        if score > 0.80:
            rating = 'A (强烈推荐)'
        elif score > 0.65:
            rating = 'B (推荐)'
        elif score > 0.50:
            rating = 'C (可考虑)'
        else:
            rating = 'D (低优先级)'

        bar = '█' * int(score * 30)
        print(f"  {rank+1:<5} {tech['id']} {tech['name']:<38} {score:>8.4f}  {rating}")

    # ---- 4. CR 检验 ----
    cr_stat = '< 0.10 OK' if diag['consistent'] else '>= 0.10 FAIL'
    print(f"\n[4] 一致性检验: CR = {diag['CR']:.4f} {cr_stat}")
    if not diag['consistent']:
        print("  WARNING: 成对比较矩阵一致性不足，建议复查判断矩阵")

    # ---- 5. 灵敏度分析 ----
    print("\n[5] 准则权重灵敏度分析 (±30%)...")
    sensitivity = sensitivity_weights(CRITERIA_PAIRWISE, TECH_SCORES, n_perturb=7)

    for cname, sdata in sensitivity.items():
        swaps_total = sum(p['rank_swaps'] for p in sdata['perturbations'])
        print(f"  {cname}: 平均排名交换={swaps_total/len(sdata['perturbations']):.1f}")

    # ---- 保存结果 ----
    results = {
        'criteria_weights': {crit_names[i]: round(float(crit_weights[i]), 4) for i in range(len(crit_names))},
        'diagnostics': {
            'lambda_max': round(float(diag['lambda_max']), 4),
            'CI': round(float(diag['CI']), 4),
            'CR': round(float(diag['CR']), 4),
            'RI': round(float(diag['RI']), 4),
            'consistent': bool(diag['consistent']),
        },
        'technology_ranking': [
            {
                'rank': int(rank + 1),
                'id': TECHNOLOGIES[idx]['id'],
                'name': TECHNOLOGIES[idx]['name'],
                'score': round(float(final_scores[idx]), 4),
                'criteria_breakdown': {
                    crit_names[c]: round(float(tech_scores_norm[idx, c]), 4)
                    for c in range(len(crit_names))
                }
            }
            for rank, idx in enumerate(ranking)
        ],
        'sensitivity': {
            cname: {
                'rank_swaps': [int(p['rank_swaps']) for p in sdata['perturbations']],
                'alphas': [float(p['alpha']) for p in sdata['perturbations']],
            }
            for cname, sdata in sensitivity.items()
        }
    }

    fpath = os.path.join(OUTPUT, 'q4b_ahp_results.json')
    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n  AHP结果已保存: {fpath}")

    # ---- 汇总 ----
    print("\n" + "=" * 60)
    print("  Q4b 汇总")
    print("=" * 60)
    top3 = [(TECHNOLOGIES[idx]['name'], final_scores[idx]) for idx in ranking[:3]]
    print(f"  前3推荐: {[t[0].split('(')[0].strip() for t in top3]}")
    cr_ok = 'OK' if diag['consistent'] else 'FAIL'
    print(f"  准则一致性: CR={diag['CR']:.4f} {cr_ok}")
    print("\n[Q4b] 完成.")
