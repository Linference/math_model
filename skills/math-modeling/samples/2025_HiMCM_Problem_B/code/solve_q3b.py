#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Problem 3b: TOPSIS Ranking — Never-Hosted Super Bowl Cities (3 cities)
- Same AHP+TOPSIS model as 3a
- Evaluates Nashville, Charlotte, Seattle
- Merges with 3a ranking for combined comparison

Dependencies: numpy, pandas, matplotlib
Usage: /d/anaconda/python solve_q3b.py
"""
import sys, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.random.seed(42)

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts"))
from plot_helpers import sensitivity_tornado

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

# Split: hosted and never-hosted
hosted = cities[cities["superbowl_hosted"] == "Yes"].copy().reset_index(drop=True)
never_hosted = cities[cities["superbowl_hosted"] == "No"].copy().reset_index(drop=True)

print("=" * 70)
print("PROBLEM 3b: TOPSIS Ranking — 3 Never-Hosted NFL Cities")
print("=" * 70)
print(f"\n  Cities: {', '.join(never_hosted['city_full'].values)}")
print(f"  Total: {len(never_hosted)} cities")

# ============================================================
# Indicator setup (same as q3a)
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
weights = weights_df["global_weight"].values.astype(float)
directions = weights_df["direction"].values


def topsis(decision_matrix, weights, directions):
    """TOPSIS implementation — identical to q3a."""
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
    return scores, d_pos, d_neg


def build_matrix(df, ind_keys, indicator_map):
    """Build decision matrix with feb_temp suitability transform."""
    X = np.zeros((len(df), len(ind_keys)))
    for j, ind_key in enumerate(ind_keys):
        col = indicator_map[ind_key]
        X[:, j] = df[col].values
    # Transform I8: feb_avg_temp_c → suitability (FIX Issue M5)
    i8_idx = list(ind_keys).index("I8_feb_temp")
    i9_idx = list(ind_keys).index("I9_has_dome")
    has_dome = X[:, i9_idx] >= 0.5
    temp_raw = X[:, i8_idx].copy()
    X[:, i8_idx] = np.where(has_dome, 9.0,
                             np.maximum(0.0, 10.0 - np.abs(temp_raw - 18.0)))
    return X


# ============================================================
# Run TOPSIS on never-hosted cities
# ============================================================
X_nh = build_matrix(never_hosted, ind_keys, indicator_map)
scores_nh, d_pos_nh, d_neg_nh = topsis(X_nh, weights, directions)

never_hosted["topsis_score"] = scores_nh
never_hosted["d_positive"] = d_pos_nh
never_hosted["d_negative"] = d_neg_nh
never_hosted = never_hosted.sort_values("topsis_score", ascending=False).reset_index(drop=True)
never_hosted["rank"] = range(1, len(never_hosted) + 1)

print("\n" + "=" * 70)
print("  TOPSIS RANKING — Never-Hosted Cities")
print("=" * 70)
print(f"\n{'Rank':<5s} {'City':<25s} {'Score':>8s} {'D+':>8s} {'D-':>8s}")
print("-" * 60)
for _, row in never_hosted.iterrows():
    print(f"  {row['rank']:<5d} {row['city_full']:<25s} {row['topsis_score']:8.4f} "
          f"{row['d_positive']:8.4f} {row['d_negative']:8.4f}")

print(f"\n  Best never-hosted city: {never_hosted.iloc[0]['city_full']}")
print(f"  Score: {never_hosted.iloc[0]['topsis_score']:.4f}")

# ============================================================
# Combined ranking (all 13 cities)
# ============================================================
all_cities = pd.concat([hosted, never_hosted], ignore_index=True)
X_all = build_matrix(all_cities, ind_keys, indicator_map)
scores_all, d_pos_all, d_neg_all = topsis(X_all, weights, directions)

all_cities["topsis_score"] = scores_all
all_cities["d_positive"] = d_pos_all
all_cities["d_negative"] = d_neg_all
all_cities = all_cities.sort_values("topsis_score", ascending=False).reset_index(drop=True)
all_cities["rank"] = range(1, len(all_cities) + 1)

print("\n" + "=" * 70)
print("  COMBINED RANKING — All 13 Cities (Hosted + Never-Hosted)")
print("=" * 70)
print(f"\n{'Rank':<5s} {'City':<25s} {'Hosted?':<10s} {'Score':>8s} {'D+':>8s} {'D-':>8s}")
print("-" * 75)
for _, row in all_cities.iterrows():
    marker = " ***" if row["superbowl_hosted"] == "No" else ""
    print(f"  {row['rank']:<5d} {row['city_full']:<25s} {row['superbowl_hosted']:<10s} "
          f"{row['topsis_score']:8.4f} {row['d_positive']:8.4f} {row['d_negative']:8.4f}{marker}")

# Save combined ranking
all_cities[["rank", "city_full", "city_short", "superbowl_hosted", "topsis_score",
            "d_positive", "d_negative"]] \
    .to_csv(os.path.join(RES_DIR, "q3b_combined_ranking.csv"), index=False)
print(f"\n  Combined ranking saved to results/q3b_combined_ranking.csv")

# ============================================================
# Figure 1: Combined ranking bar chart
# ============================================================
fig, ax = plt.subplots(figsize=(11, 6))
city_names_all = all_cities["city_short"].values[::-1]
scores_all_rev = all_cities["topsis_score"].values[::-1]
hosted_all_rev = all_cities["superbowl_hosted"].values[::-1]

colors_all = ["#3498DB" if h == "Yes" else "#E74C3C" for h in hosted_all_rev]
bars = ax.barh(range(len(city_names_all)), scores_all_rev, color=colors_all, edgecolor="white", alpha=0.85)
ax.set_yticks(range(len(city_names_all)))
ax.set_yticklabels(city_names_all, fontsize=10)
ax.set_xlabel("TOPSIS Closeness Coefficient", fontsize=12)
ax.set_title("Combined TOPSIS Ranking: All 13 Candidate Cities\n(Blue=Previously Hosted, Red=Never Hosted)",
             fontsize=13, fontweight="bold")
for bar, score in zip(bars, scores_all_rev):
    ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2.,
            f"{score:.4f}", va="center", fontsize=9, fontweight="bold")
ax.set_xlim(0, max(scores_all_rev) * 1.15)

# Legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor="#3498DB", alpha=0.85, label="Previously Hosted"),
                   Patch(facecolor="#E74C3C", alpha=0.85, label="Never Hosted")]
ax.legend(handles=legend_elements, loc="lower right", fontsize=10)
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "fig_q3b_combined_ranking.png"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("[Figure] fig_q3b_combined_ranking.png saved.")

# ============================================================
# Figure 2: 3 never-hosted cities radar comparison
# ============================================================
radar_indicators = ["Grid\nCarbon", "Renewable", "Airport", "Water\nStress",
                    "Precip", "Transit", "Pop\nDensity", "Recycling",
                    "Feb\nTemp", "Dome", "LEED", "Parkland"]

# Normalize across all 13 cities for radar
X_nh_local = build_matrix(never_hosted.reset_index(drop=True), ind_keys, indicator_map)
radar_data = np.zeros((3, 12))
for j in range(12):
    col_vals = X_nh_local[:, j]
    dir_j = directions[j]
    # Use min/max across all 13 cities for scaling
    all_col_vals = X_all[:, j]
    mn, mx = all_col_vals.min(), all_col_vals.max()
    if dir_j == "benefit":
        if mx > mn:
            radar_data[:, j] = (col_vals - mn) / (mx - mn)
        else:
            radar_data[:, j] = 1.0
    else:
        if mx > mn:
            radar_data[:, j] = (mx - col_vals) / (mx - mn)
        else:
            radar_data[:, j] = 1.0

angles = np.linspace(0, 2*np.pi, 12, endpoint=False).tolist()
radar_data_closed = np.hstack([radar_data, radar_data[:, [0]]])
angles_closed = angles + [angles[0]]

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
colors_nh = ["#E74C3C", "#3498DB", "#2ECC71"]
for i in range(3):
    ax.fill(angles_closed, radar_data_closed[i], alpha=0.12, color=colors_nh[i])
    ax.plot(angles_closed, radar_data_closed[i], 'o-', linewidth=2, markersize=5,
            color=colors_nh[i], label=never_hosted.iloc[i]["city_short"])
ax.set_xticks(angles)
ax.set_xticklabels(radar_indicators, fontsize=9)
ax.set_ylim(0, 1)
ax.set_title("Never-Hosted Cities: Multi-Dimensional\nEnvironmental Profile (Normalized Across All 13)",
             fontsize=12, fontweight="bold", pad=25)
ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=10)
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "fig_q3b_radar_nh.png"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("[Figure] fig_q3b_radar_nh.png saved.")

# ============================================================
# Figure 3: Never-hosted city detailed comparison
# ============================================================
fig, axes = plt.subplots(2, 3, figsize=(15, 9))
key_pairs = [
    ("grid_carbon_factor_kgCO2_per_kWh", "Grid CO2 (kg/kWh)", True),
    ("renewable_share_pct", "Renewable (%)", False),
    ("public_transit_share_pct", "Transit (%)", False),
    ("waste_recycling_rate_pct", "Recycling (%)", False),
    ("water_stress_wri_score", "Water Stress", True),
    ("feb_avg_temp_c", "Feb Temp (°C)", False),
]

for idx, (col, title, lower_better) in enumerate(key_pairs):
    ax = axes[idx // 3, idx % 3]
    vals = never_hosted[col].values
    names = never_hosted["city_short"].values
    bar_colors = ["#E74C3C", "#3498DB", "#2ECC71"]
    bars = ax.bar(range(3), vals, color=bar_colors, edgecolor="white")
    ax.set_xticks(range(3))
    ax.set_xticklabels(names, fontsize=10)
    ax.set_title(title, fontsize=11, fontweight="bold")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02*max(vals),
                f"{v:.1f}", ha="center", fontsize=9, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)

plt.suptitle("Never-Hosted Cities: Key Indicator Comparison", fontsize=14, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(os.path.join(FIG_DIR, "fig_q3b_detail_comparison.png"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("[Figure] fig_q3b_detail_comparison.png saved.")

# Identify where never-hosted cities rank in combined list
print("\n--- Never-Hosted Cities in Combined Ranking ---")
for _, row in never_hosted.iterrows():
    combined_row = all_cities[all_cities["city_short"] == row["city_short"]]
    print(f"  {row['city_full']}: Individual score = {row['topsis_score']:.4f}, "
          f"Combined rank = {int(combined_row['rank'].values[0])}/{len(all_cities)}")

print("\n" + "=" * 70)
print(f"  PROBLEM 3b COMPLETE")
print(f"  Best never-hosted city: {never_hosted.iloc[0]['city_full']}")
print(f"  Combined ranking position: {int(all_cities[all_cities['city_short']==never_hosted.iloc[0]['city_short']]['rank'].values[0])}/{len(all_cities)}")
print("=" * 70)
