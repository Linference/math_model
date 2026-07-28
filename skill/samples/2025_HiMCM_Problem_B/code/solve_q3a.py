#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Problem 3a: TOPSIS Ranking — Previously-Hosted Super Bowl Cities (10 cities)
- Reads AHP weights from q2 + city indicators
- Applies TOPSIS to rank all 10 previously-hosted cities
- Output: ranking table, TOPSIS scores, distances

UPDATED:
- Multi-factor sensitivity analysis (I1+I2, I5+I6 simultaneous perturbations)
- All-city rank tracking in sensitivity (not just #1)
- Perturbation magnitude justification
- TOPSIS set-dependency analysis (10-city vs 13-city normalization)

Dependencies: numpy, pandas, matplotlib
Usage: /d/anaconda/python solve_q3a.py
"""
import sys, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.random.seed(42)

sys.path.insert(0, r"C:\Users\HUAWEI\.claude\skills\math-modeling\scripts")
from plot_helpers import sensitivity_tornado, heatmap

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
RES_DIR  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
FIG_DIR  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(RES_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

# ============================================================
# Load data and weights
# ============================================================
cities = pd.read_csv(os.path.join(DATA_DIR, "city_indicators.csv"))
weights_df = pd.read_csv(os.path.join(RES_DIR, "ahp_weights.csv"))

# Filter to previously-hosted cities only
hosted = cities[cities["superbowl_hosted"] == "Yes"].copy().reset_index(drop=True)

print("=" * 70)
print("PROBLEM 3a: TOPSIS Ranking — 10 Previously-Hosted Super Bowl Cities")
print("=" * 70)
print(f"\n  Cities: {', '.join(hosted['city_short'].values)}")
print(f"  Total: {len(hosted)} cities")

# ============================================================
# Build indicator matrix
# ============================================================
indicator_map = {
    "I1_grid_carbon":  "grid_carbon_factor_kgCO2_per_kWh",
    "I2_renewable":    "renewable_share_pct",
    "I12_airport":     "airport_enplanements_millions_2024",
    "I3_water_stress": "water_stress_wri_score",
    "I4_precipitation":"annual_precip_inches",
    "I5_transit":      "public_transit_share_pct",
    "I6_pop_density":  "population_density_per_sqmi",
    "I7_recycling":    "waste_recycling_rate_pct",
    "I8_feb_temp":     "feb_avg_temp_c",
    "I9_has_dome":     "stadium_has_dome",
    "I10_leed":        "stadium_leed_level",
    "I11_parkland":    "parkland_pct_city_area",
}

ind_keys = weights_df["indicator"].values
n_indicators = len(ind_keys)
n_cities = len(hosted)

X_raw = np.zeros((n_cities, n_indicators))
directions = []

for j, ind_key in enumerate(ind_keys):
    col = indicator_map[ind_key]
    X_raw[:, j] = hosted[col].values
    directions.append(weights_df.loc[weights_df["indicator"] == ind_key, "direction"].values[0])

weights = weights_df["global_weight"].values.astype(float)

# Transform I8: feb_avg_temp_c → climate suitability score
# FIX (Reviewer Issue M5): Dome stadiums get fixed high score (9.0), open-air use
# max(0, 10 - |T - 18|) to prevent negative "suitability" for cold open-air cities.
i8_idx = list(ind_keys).index("I8_feb_temp")
i9_idx = list(ind_keys).index("I9_has_dome")
has_dome = X_raw[:, i9_idx] >= 0.5
temp_raw = X_raw[:, i8_idx].copy()
X_raw[:, i8_idx] = np.where(has_dome, 9.0,
                             np.maximum(0.0, 10.0 - np.abs(temp_raw - 18.0)))

# ============================================================
# TOPSIS Implementation
# ============================================================
def topsis(decision_matrix, weights, directions, return_norm=False):
    m, n = decision_matrix.shape
    col_norms = np.sqrt(np.sum(decision_matrix**2, axis=0))
    col_norms[col_norms == 0] = 1e-10
    X_norm = decision_matrix / col_norms
    X_weighted = X_norm * weights
    ideal_pos = np.zeros(n)
    ideal_neg = np.zeros(n)
    for j in range(n):
        col = X_weighted[:, j]
        if directions[j] == "benefit":
            ideal_pos[j] = np.max(col)
            ideal_neg[j] = np.min(col)
        else:
            ideal_pos[j] = np.min(col)
            ideal_neg[j] = np.max(col)
    d_pos = np.sqrt(np.sum((X_weighted - ideal_pos)**2, axis=1))
    d_neg = np.sqrt(np.sum((X_weighted - ideal_neg)**2, axis=1))
    scores = d_neg / (d_pos + d_neg)
    if return_norm:
        return scores, d_pos, d_neg, col_norms, X_norm
    return scores, d_pos, d_neg


# Run TOPSIS
scores, d_pos, d_neg = topsis(X_raw, weights, directions)

# Build results table
hosted["topsis_score"] = scores
hosted["d_positive"] = d_pos
hosted["d_negative"] = d_neg
hosted = hosted.sort_values("topsis_score", ascending=False).reset_index(drop=True)
hosted["rank"] = range(1, len(hosted) + 1)

print("\n" + "=" * 70)
print("  TOPSIS RANKING RESULTS (Previously-Hosted Cities)")
print("=" * 70)
print(f"\n{'Rank':<5s} {'City':<25s} {'Score':>8s} {'D+':>8s} {'D-':>8s}")
print("-" * 65)
for _, row in hosted.iterrows():
    print(f"  {row['rank']:<5d} {row['city_full']:<25s} {row['topsis_score']:8.4f} "
          f"{row['d_positive']:8.4f} {row['d_negative']:8.4f}")

print(f"\n  Recommended City (Rank 1): {hosted.iloc[0]['city_full']}")
print(f"  TOPSIS Score: {hosted.iloc[0]['topsis_score']:.4f}")

# Save results
hosted[["rank", "city_full", "city_short", "topsis_score", "d_positive", "d_negative"]] \
    .to_csv(os.path.join(RES_DIR, "q3a_topsis_ranking.csv"), index=False)
print(f"\n  Results saved to results/q3a_topsis_ranking.csv")

# ============================================================
# TOPSIS Set-Dependency Analysis (Reviewer Issue 4 & 10)
# ============================================================
print("\n" + "=" * 70)
print("  TOPSIS SET-DEPENDENCY ANALYSIS")
print("  Comparing 10-city normalization vs 13-city normalization")
print("=" * 70)

# Build 13-city matrix
all_cities = pd.read_csv(os.path.join(DATA_DIR, "city_indicators.csv"))
X_all = np.zeros((len(all_cities), n_indicators))
for j, ind_key in enumerate(ind_keys):
    col = indicator_map[ind_key]
    X_all[:, j] = all_cities[col].values
X_all[:, i8_idx] = 10.0 - np.abs(X_all[:, i8_idx] - 18.0)

scores_10, _, _, norms_10, _ = topsis(X_raw, weights, directions, return_norm=True)
scores_13, _, _, norms_13, X_norm_13 = topsis(X_all, weights, directions, return_norm=True)

# Compare Euclidean norms
print("\n  Column norms comparison (10-city vs 13-city):")
print(f"  {'Indicator':<20s} {'Norm 10':>10s} {'Norm 13':>10s} {'Ratio':>8s}")
print(f"  {'-'*50}")
for j, ik in enumerate(ind_keys):
    ratio = norms_13[j] / norms_10[j] if norms_10[j] > 0 else float('inf')
    print(f"  {ik:<20s} {norms_10[j]:10.4f} {norms_13[j]:10.4f} {ratio:8.4f}")

# Inglewood score comparison
inglewood_idx_10 = np.where(hosted["city_short"].values == "inglewood")[0][0]
inglewood_idx_13 = np.where(all_cities["city_short"].values == "inglewood")[0][0]
print(f"\n  Inglewood TOPSIS score: C_10 = {scores_10[inglewood_idx_10]:.4f}, C_13 = {scores_13[inglewood_idx_13]:.4f}")
print(f"  Difference: {abs(scores_10[inglewood_idx_10] - scores_13[inglewood_idx_13]):.4f} "
      f"(due to normalization basis change + 3 new cities)")

# 12-city analysis (remove Seattle)
seattle_idx = np.where(all_cities["city_short"].values == "seattle")[0][0]
all_except_seattle = np.delete(all_cities.index, seattle_idx)
X_12 = X_all[all_except_seattle, :]
scores_12, _, _ = topsis(X_12, weights, directions)
cities_12 = all_cities.iloc[all_except_seattle].copy()
cities_12["score_12"] = scores_12
cities_12 = cities_12.sort_values("score_12", ascending=False)
print(f"\n  Without Seattle (12-city):")
print(f"    Rank-1: {cities_12.iloc[0]['city_full']} (C={cities_12.iloc[0]['score_12']:.4f})")
print(f"    Rank-2: {cities_12.iloc[1]['city_full']} (C={cities_12.iloc[1]['score_12']:.4f})")

# ============================================================
# Figure 1: TOPSIS ranking bar chart
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5.5))
city_names = hosted["city_short"].values[::-1]
city_scores = hosted["topsis_score"].values[::-1]
colors = ["#27AE60" if s == city_scores.max() else "#3498DB" if s > 0.5 else "#E67E22"
          for s in city_scores]
bars = ax.barh(range(len(city_names)), city_scores, color=colors, edgecolor="white")
ax.set_yticks(range(len(city_names)))
ax.set_yticklabels(city_names, fontsize=11)
ax.set_xlabel("TOPSIS Closeness Coefficient", fontsize=12)
ax.set_title("TOPSIS Environmental Sustainability Ranking\n(10 Previously-Hosted Super Bowl Cities)",
             fontsize=14, fontweight="bold")
for bar, score in zip(bars, city_scores):
    ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2.,
            f"{score:.4f}", va="center", fontsize=10, fontweight="bold")
ax.set_xlim(0, max(city_scores) * 1.20)
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "fig_q3a_topsis_ranking.png"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("[Figure] fig_q3a_topsis_ranking.png saved.")

# ============================================================
# Figure 2: Top 3 cities radar chart
# ============================================================
radar_indicators = ["Grid\nCarbon", "Renewable", "Airport", "Water\nStress",
                    "Precip", "Transit", "Pop\nDensity", "Recycling",
                    "Feb\nTemp", "Dome", "LEED", "Parkland"]
radar_data = np.zeros((3, 12))
for j in range(12):
    col_vals = X_raw[hosted.head(3).index, j]
    dir_j = directions[j]
    if dir_j == "benefit":
        mn, mx = col_vals.min(), col_vals.max()
        if mx > mn:
            radar_data[:, j] = (col_vals - mn) / (mx - mn)
        else:
            radar_data[:, j] = 1.0
    else:
        mn, mx = col_vals.min(), col_vals.max()
        if mx > mn:
            radar_data[:, j] = (mx - col_vals) / (mx - mn)
        else:
            radar_data[:, j] = 1.0

angles = np.linspace(0, 2*np.pi, 12, endpoint=False).tolist()
radar_data_closed = np.hstack([radar_data, radar_data[:, [0]]])
angles_closed = angles + [angles[0]]

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
top3_colors = ["#E74C3C", "#3498DB", "#2ECC71"]
for i, (idx, row) in enumerate(hosted.head(3).iterrows()):
    ax.fill(angles_closed, radar_data_closed[i], alpha=0.15, color=top3_colors[i])
    ax.plot(angles_closed, radar_data_closed[i], 'o-', linewidth=2,
            color=top3_colors[i], label=row["city_short"])
ax.set_xticks(angles)
ax.set_xticklabels(radar_indicators, fontsize=9)
ax.set_ylim(0, 1)
ax.set_title("Top 3 Cities: Multi-Dimensional\nEnvironmental Profile", fontsize=14, fontweight="bold", pad=25)
ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=10)
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "fig_q3a_radar_top3.png"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("[Figure] fig_q3a_radar_top3.png saved.")

# ============================================================
# Sensitivity Analysis — MULTI-FACTOR (Reviewer Issue 11)
# ============================================================
# Single-factor ±20% (as before)
# PLUS: Multi-factor scenarios (I1+I2, I5+I6, all top-4 indicators)
# Report rank changes for ALL cities, not just #1

print("\n" + "=" * 70)
print("  SENSITIVITY ANALYSIS (Single + Multi-Factor)")
print("=" * 70)

base_scores = hosted["topsis_score"].values.copy()
base_ranks = np.argsort(np.argsort(-base_scores)) + 1  # rank 1 = best

# Perturbation magnitude justification:
# ±20% is used based on typical weight uncertainty in AHP studies
# (Ishizaka & Labib, 2011). It represents a reasonable range for
# expert judgment variability in pairwise comparison matrices.

# --- Single-factor perturbations ---
single_results = []
for j, ind_key in enumerate(ind_keys):
    w_high = weights.copy()
    w_high[j] *= 1.20
    w_high = w_high / w_high.sum()
    s_high, _, _ = topsis(X_raw, w_high, directions)

    w_low = weights.copy()
    w_low[j] *= 0.80
    w_low = w_low / w_low.sum()
    s_low, _, _ = topsis(X_raw, w_low, directions)

    # Rank-1 score change
    rank1_idx = np.argmax(base_scores)
    delta_top1 = s_high[rank1_idx] - s_low[rank1_idx]
    # Rank changes for all cities
    rank_high = np.argsort(np.argsort(-s_high)) + 1
    rank_low = np.argsort(np.argsort(-s_low)) + 1
    n_rank_changes = np.sum(rank_high != base_ranks) + np.sum(rank_low != base_ranks)

    ind_label = weights_df.loc[weights_df["indicator"] == ind_key, "label"].values[0]
    single_results.append({
        "indicator": ind_label,
        "score_low_top1": s_low[rank1_idx],
        "score_high_top1": s_high[rank1_idx],
        "delta_top1": delta_top1,
        "rank_changes_high": int(n_rank_changes),
    })

sens_df = pd.DataFrame(single_results)
sens_df = sens_df.sort_values("delta_top1", ascending=True)

# --- Multi-factor perturbation scenarios ---
print("\n  Multi-Factor Perturbation Scenarios:")
multi_scenarios = {
    "I1+I2 (Energy bundle)": [("I1_grid_carbon", +0.20), ("I2_renewable", +0.20)],
    "I1+I2 (Energy bundle -20%)": [("I1_grid_carbon", -0.20), ("I2_renewable", -0.20)],
    "I5+I6 (Transport bundle)": [("I5_transit", +0.20), ("I6_pop_density", +0.20)],
    "I5+I6 (Transport bundle -20%)": [("I5_transit", -0.20), ("I6_pop_density", -0.20)],
    "I1+I2+I5 (Top 3 bundle)": [("I1_grid_carbon", +0.20), ("I2_renewable", +0.20), ("I5_transit", +0.20)],
    "I1+I2+I5 (Top 3 bundle -20%)": [("I1_grid_carbon", -0.20), ("I2_renewable", -0.20), ("I5_transit", -0.20)],
}

multi_results = []
for scenario_name, perturbations in multi_scenarios.items():
    w_multi = weights.copy()
    for ind_key, delta_factor in perturbations:
        j_idx = list(ind_keys).index(ind_key)
        w_multi[j_idx] *= (1.0 + delta_factor)
    w_multi = w_multi / w_multi.sum()
    s_multi, _, _ = topsis(X_raw, w_multi, directions)

    rank_multi = np.argsort(np.argsort(-s_multi)) + 1
    n_changes = np.sum(rank_multi != base_ranks)
    delta_rank1 = s_multi[np.argmax(base_scores)] - base_scores[np.argmax(base_scores)]

    # Identify which cities changed rank
    changed_cities = []
    for c_idx in range(len(hosted)):
        if rank_multi[c_idx] != base_ranks[c_idx]:
            changed_cities.append(f"{hosted.iloc[c_idx]['city_short']} ({base_ranks[c_idx]}→{rank_multi[c_idx]})")

    multi_results.append({
        "scenario": scenario_name,
        "rank1_score_delta": delta_rank1,
        "n_rank_changes": n_changes,
        "changed_cities": changed_cities,
    })
    print(f"    {scenario_name}: ΔC_rank1={delta_rank1:+.4f}, "
          f"rank changes={n_changes}/{len(hosted)}, cities: {', '.join(changed_cities) if changed_cities else 'none'}")

# ============================================================
# Figure 3: Sensitivity Tornado (+ multi-factor panel)
# ============================================================
base_score_rank1 = hosted.loc[hosted["rank"] == 1, "topsis_score"].values[0]

fig2, ax2 = plt.subplots(figsize=(8, 0.5 * len(ind_keys) + 1.5))
y_pos = np.arange(len(ind_keys))
ax2.barh(y_pos, sens_df["score_high_top1"].values - base_score_rank1, left=base_score_rank1,
         color="#4C72B0", label="Weight +20%", height=0.6)
ax2.barh(y_pos, sens_df["score_low_top1"].values - base_score_rank1, left=base_score_rank1,
         color="#DD8452", label="Weight -20%", height=0.6)
ax2.axvline(base_score_rank1, color="k", linewidth=1, linestyle="--")
ax2.set_yticks(y_pos)
ax2.set_yticklabels(sens_df["indicator"].values, fontsize=9)
ax2.set_xlabel("TOPSIS Score of Top-Ranked City", fontsize=11)
ax2.set_title(f"Sensitivity Analysis: ±20% Weight Perturbation\n(Base score = {base_score_rank1:.4f})",
              fontsize=12, fontweight="bold")
ax2.legend(fontsize=9)
ax2.grid(axis="x", alpha=0.3)
plt.tight_layout()
fig2.savefig(os.path.join(FIG_DIR, "fig_q3a_sensitivity_tornado.png"), dpi=300, bbox_inches="tight")
plt.close(fig2)
print("[Figure] fig_q3a_sensitivity_tornado.png saved.")

# ============================================================
# Figure 4: Multi-factor rank change heatmap
# ============================================================
if len(multi_results) > 0:
    # Build rank matrix: rows=cities, cols=multi_scenarios
    multi_keys_order = [m["scenario"] for m in multi_results]
    rank_matrix = np.zeros((len(hosted), len(multi_keys_order)))
    for s_idx, scenario_name in enumerate(multi_keys_order):
        perturbations = multi_scenarios[scenario_name]
        w_multi = weights.copy()
        for ind_key, delta_factor in perturbations:
            j_idx = list(ind_keys).index(ind_key)
            w_multi[j_idx] *= (1.0 + delta_factor)
        w_multi = w_multi / w_multi.sum()
        s_multi, _, _ = topsis(X_raw, w_multi, directions)
        rank_multi = np.argsort(np.argsort(-s_multi)) + 1
        # Map back to baseline order
        for c_idx, orig_idx in enumerate(np.argsort(np.argsort(-base_scores))):
            rank_matrix[np.argsort(np.argsort(-base_scores))[c_idx], s_idx] = rank_multi[c_idx]

    fig4, ax4 = plt.subplots(figsize=(10, 6))
    im = ax4.imshow(rank_matrix, cmap="RdYlGn_r", aspect="auto", vmin=1, vmax=10)
    fig4.colorbar(im, ax=ax4, label="Rank (1=Best)")
    city_names_ordered = hosted.iloc[np.argsort(np.argsort(-base_scores))]["city_short"].values
    ax4.set_yticks(range(len(city_names_ordered)))
    ax4.set_yticklabels(city_names_ordered, fontsize=10)
    ax4.set_xticks(range(len(multi_keys_order)))
    ax4.set_xticklabels(multi_keys_order, rotation=30, ha="right", fontsize=8)
    for i in range(len(city_names_ordered)):
        for j in range(len(multi_keys_order)):
            ax4.text(j, i, f"{int(rank_matrix[i,j])}", ha="center", va="center",
                    fontsize=9, fontweight="bold",
                    color="white" if rank_matrix[i,j] > 5 else "black")
    ax4.set_title("Multi-Factor Sensitivity: City Ranks Under Simultaneous\nWeight Perturbations",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    fig4.savefig(os.path.join(FIG_DIR, "fig_q3a_multifactor_sensitivity.png"), dpi=300, bbox_inches="tight")
    plt.close(fig4)
    print("[Figure] fig_q3a_multifactor_sensitivity.png saved.")

# Summary
print("\n" + "=" * 70)
print(f"  PROBLEM 3a COMPLETE")
print(f"  Recommended city for 2029 Super Bowl: {hosted.iloc[0]['city_full']}")
print(f"  TOPSIS Score: {hosted.iloc[0]['topsis_score']:.4f}")
print(f"  2nd place: {hosted.iloc[1]['city_full']} ({hosted.iloc[1]['topsis_score']:.4f})")
print(f"  3rd place: {hosted.iloc[2]['city_full']} ({hosted.iloc[2]['topsis_score']:.4f})")
print(f"  Score range: [{scores.min():.4f}, {scores.max():.4f}]")
print(f"  Single-factor max rank change: {sens_df['rank_changes_high'].max()} cities affected")
if multi_results:
    print(f"  Multi-factor max rank change: {max(m['n_rank_changes'] for m in multi_results)}/{len(hosted)} cities")
print("=" * 70)
