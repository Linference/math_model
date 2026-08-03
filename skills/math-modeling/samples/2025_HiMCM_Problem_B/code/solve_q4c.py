#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Problem 4c: Scenario Analysis — Infrastructure/Energy/Transport Strategies
- 4 strategy scenarios applied to 10 previously-hosted cities
- Baseline / Green Energy (-30% grid carbon) / Transit Upgrade (+20%) / Combined
- Re-ranks cities under each scenario

Dependencies: numpy, pandas, matplotlib
Usage: /d/anaconda/python solve_q4c.py
"""
import sys, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.random.seed(42)

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts"))
from plot_helpers import heatmap

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
RES_DIR  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
FIG_DIR  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(RES_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

print("=" * 70)
print("PROBLEM 4c: Scenario Analysis — Strategy Impact on Rankings")
print("=" * 70)

# Load data and weights (same as q3a)
cities = pd.read_csv(os.path.join(DATA_DIR, "city_indicators.csv"))
weights_df = pd.read_csv(os.path.join(RES_DIR, "ahp_weights.csv"))
hosted = cities[cities["superbowl_hosted"] == "Yes"].copy().reset_index(drop=True)

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
weights = weights_df["global_weight"].values.astype(float)
directions = weights_df["direction"].values

def topsis(decision_matrix, weights, directions):
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
    X = np.zeros((len(df), len(ind_keys)))
    for j, ind_key in enumerate(ind_keys):
        col = indicator_map[ind_key]
        X[:, j] = df[col].values
    i8_idx = list(ind_keys).index("I8_feb_temp")
    i9_idx = list(ind_keys).index("I9_has_dome")
    has_dome = X[:, i9_idx] >= 0.5
    temp_raw = X[:, i8_idx].copy()
    X[:, i8_idx] = np.where(has_dome, 9.0,
                             np.maximum(0.0, 10.0 - np.abs(temp_raw - 18.0)))
    return X

# ============================================================
# Define 4 Strategy Scenarios
# ============================================================
scenarios = {
    "S0_Baseline": {
        "label": "Baseline (Current)",
        "description": "No intervention -- current values",
        "modifications": {},  # no changes
    },
    "S1_GreenEnergy": {
        "label": "Green Energy\nProcurement",
        "description": "Reduce grid carbon by 0.08 kgCO2/kWh\n(absolute) via RECs and renewable PPAs,\nincrease renewable share by 15 pp",
        "modifications": {
            "I1_grid_carbon": ("additive", -0.08, 0.05, None),   # reduce by 0.08, floor at 0.05
            "I2_renewable":   ("additive", 15.0, 0, 100),        # add 15 pp, cap at 100
        },
    },
    "S2_TransitUpgrade": {
        "label": "Public Transit\nUpgrade",
        "description": "Add 5 percentage points to transit\nmode share via infrastructure investment",
        "modifications": {
            "I5_transit": ("additive", 5.0, 0, 100),  # add 5 pp, cap at 100
        },
    },
    "S3_Combined": {
        "label": "Combined\nStrategy",
        "description": "Both green energy procurement\nAND transit infrastructure upgrade",
        "modifications": {
            "I1_grid_carbon": ("additive", -0.08, 0.05, None),
            "I2_renewable":   ("additive", 15.0, 0, 100),
            "I5_transit":     ("additive", 5.0, 0, 100),
        },
    },
}

print("\n--- Strategy Scenarios ---")
for s_key, s_info in scenarios.items():
    print(f"  {s_info['label']}: {s_info['description'].split(chr(10))[0]}")

# ============================================================
# Run TOPSIS under each scenario
# ============================================================
all_results = {}
for s_key, s_info in scenarios.items():
    # Build baseline matrix (raw values, before feb_temp transform)
    X = build_matrix(hosted, ind_keys, indicator_map).copy()

    # Apply scenario modifications using additive approach
    for ind_mod, mod_spec in s_info["modifications"].items():
        j_idx = list(ind_keys).index(ind_mod)
        op = mod_spec[0]
        if op == "additive":
            delta, floor, ceiling = mod_spec[1], mod_spec[2], mod_spec[3]
            X[:, j_idx] = X[:, j_idx] + delta
            if floor is not None:
                X[:, j_idx] = np.maximum(X[:, j_idx], floor)
            if ceiling is not None:
                X[:, j_idx] = np.minimum(X[:, j_idx], ceiling)
        elif op == "multiply":
            X[:, j_idx] *= mod_spec[1]
            if len(mod_spec) > 2 and mod_spec[2] is not None:
                X[:, j_idx] = np.maximum(X[:, j_idx], mod_spec[2])
            if len(mod_spec) > 3 and mod_spec[3] is not None:
                X[:, j_idx] = np.minimum(X[:, j_idx], mod_spec[3])

    scores, d_pos, d_neg = topsis(X, weights, directions)

    # Build ranking
    sc_df = hosted[["city_full", "city_short"]].copy()
    sc_df["score"] = scores
    sc_df = sc_df.sort_values("score", ascending=False).reset_index(drop=True)
    sc_df["rank"] = range(1, len(sc_df) + 1)
    sc_df.index = sc_df["city_short"]  # for cross-referencing
    all_results[s_key] = sc_df

# ============================================================
# Report results
# ============================================================
print("\n" + "=" * 70)
print("  SCENARIO RANKINGS")
print("=" * 70)

# Print ranking table for each scenario
all_city_names = sorted(hosted["city_short"].unique())

for s_key, s_info in scenarios.items():
    sc_df = all_results[s_key]
    print(f"\n--- {s_info['label']} ---")
    print(f"    {s_info['description'].replace(chr(10), ' | ')}")
    print(f"    {'Rank':<5s} {'City':<20s} {'Score':>8s}")
    print(f"    {'-'*35}")
    for _, row in sc_df.iterrows():
        print(f"    {row['rank']:<5d} {row['city_full']:<20s} {row['score']:8.4f}")

# ============================================================
# Rank changes vs baseline
# ============================================================
print("\n" + "=" * 70)
print("  RANK CHANGES (vs Baseline)")
print("=" * 70)

baseline_df = all_results["S0_Baseline"]
rank_changes = {}
for city_name in all_city_names:
    base_rank = int(baseline_df.loc[city_name, "rank"])
    row_data = {"city": city_name, "baseline_rank": base_rank, "baseline_score": baseline_df.loc[city_name, "score"]}
    for s_key in ["S1_GreenEnergy", "S2_TransitUpgrade", "S3_Combined"]:
        new_rank = int(all_results[s_key].loc[city_name, "rank"])
        new_score = all_results[s_key].loc[city_name, "score"]
        row_data[f"{s_key}_rank"] = new_rank
        row_data[f"{s_key}_delta"] = new_rank - base_rank  # negative = improved
        row_data[f"{s_key}_score"] = new_score
        row_data[f"{s_key}_score_delta"] = new_score - base_rank  # will fix below
    rank_changes[city_name] = row_data

# Fix score delta calculation
for city_name in all_city_names:
    base_score = baseline_df.loc[city_name, "score"]
    for s_key in ["S1_GreenEnergy", "S2_TransitUpgrade", "S3_Combined"]:
        rank_changes[city_name][f"{s_key}_score_delta"] = \
            all_results[s_key].loc[city_name, "score"] - base_score

rc_df = pd.DataFrame(rank_changes).T

print(f"\n{'City':<15s} {'Base':>4s} | {'Green Rk':>8s} {'Delta':>6s} | "
      f"{'Transit Rk':>10s} {'Delta':>6s} | {'Combo Rk':>8s} {'Delta':>6s}")
print("-" * 75)
for city_name in all_city_names:
    row = rank_changes[city_name]
    print(f"  {city_name:<15s} {row['baseline_rank']:4d} | "
          f"{row['S1_GreenEnergy_rank']:8d} {row['S1_GreenEnergy_delta']:+6d} | "
          f"{row['S2_TransitUpgrade_rank']:10d} {row['S2_TransitUpgrade_delta']:+6d} | "
          f"{row['S3_Combined_rank']:8d} {row['S3_Combined_delta']:+6d}")

# Identify cities that benefit most from each strategy
print("\n--- Marginal Benefit Analysis ---")
for s_key, s_label in [("S1_GreenEnergy", "Green Energy"), ("S2_TransitUpgrade", "Transit Upgrade"), ("S3_Combined", "Combined")]:
    deltas = [(city_name, rank_changes[city_name][f"{s_key}_score_delta"])
              for city_name in all_city_names]
    deltas.sort(key=lambda x: x[1], reverse=True)
    print(f"  {s_label}:")
    for name, d in deltas[:3]:
        print(f"    {name}: score change = {d:+.4f}")

# Save results
rc_save = rc_df.reset_index()
rc_save.columns = ["city"] + list(rc_df.columns)
rc_save.to_csv(os.path.join(RES_DIR, "q4c_scenario_rank_changes.csv"), index=False)
print(f"\n  Results saved to results/q4c_scenario_rank_changes.csv")

# ============================================================
# Figure 1: Rank change arrow plot
# ============================================================
fig, ax = plt.subplots(figsize=(12, 6))
scenario_names = ["S0_Baseline", "S1_GreenEnergy", "S2_TransitUpgrade", "S3_Combined"]
scenario_labels = ["Baseline", "Green Energy\n(-30% grid CO2)", "Transit\n(+20% share)", "Combined\n(Both)"]

for i, city_name in enumerate(all_city_names):
    ranks = [int(all_results[s].loc[city_name, "rank"]) for s in scenario_names]
    ax.plot(range(4), ranks, 'o-', linewidth=1.8, markersize=6,
            label=city_name if i < 5 else "",
            alpha=0.8)
    # Annotate start and end
    ax.annotate(city_name.replace("_", " ").title() if i < 2 else "",
                (0, ranks[0]), textcoords="offset points", xytext=(-80, 0),
                fontsize=8, ha="right")

ax.set_xticks(range(4))
ax.set_xticklabels(scenario_labels, fontsize=10)
ax.set_ylabel("Rank (1=Best)", fontsize=12)
ax.set_ylim(10.5, 0.5)
ax.set_title("Scenario Analysis: City Ranking Changes\nUnder Infrastructure & Energy Strategies",
             fontsize=14, fontweight="bold")
ax.grid(True, alpha=0.3)
ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=8, ncol=2)
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "fig_q4c_rank_changes.png"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("[Figure] fig_q4c_rank_changes.png saved.")

# ============================================================
# Figure 2: Score change heatmap
# ============================================================
score_heat = np.zeros((len(all_city_names), 3))  # 3 strategies × 10 cities
for i, city_name in enumerate(all_city_names):
    for j, s_key in enumerate(["S1_GreenEnergy", "S2_TransitUpgrade", "S3_Combined"]):
        score_heat[i, j] = rank_changes[city_name][f"{s_key}_score_delta"]

fig, ax = plt.subplots(figsize=(7, 6))
im = ax.imshow(score_heat, cmap="RdBu_r", aspect="auto", vmin=-0.05, vmax=0.05)
fig.colorbar(im, ax=ax, label="TOPSIS Score Change (vs Baseline)")
ax.set_xticks(range(3))
ax.set_xticklabels(["Green\nEnergy", "Transit\nUpgrade", "Combined\nStrategy"], fontsize=10)
ax.set_yticks(range(len(all_city_names)))
ax.set_yticklabels(all_city_names, fontsize=10)
for i in range(len(all_city_names)):
    for j in range(3):
        ax.text(j, i, f"{score_heat[i,j]:+.3f}", ha="center", va="center",
                fontsize=9, fontweight="bold",
                color="white" if abs(score_heat[i,j]) > 0.03 else "black")
ax.set_title("TOPSIS Score Change Under Strategy Scenarios\n(Red=Worsened, Blue=Improved)",
             fontsize=12, fontweight="bold")
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "fig_q4c_score_heatmap.png"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("[Figure] fig_q4c_score_heatmap.png saved.")

# ============================================================
# Figure 3: Marginal benefit bar chart
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(len(all_city_names))
width = 0.25
for j, (s_key, s_label, color) in enumerate([
    ("S1_GreenEnergy", "Green Energy", "#3498DB"),
    ("S2_TransitUpgrade", "Transit", "#E74C3C"),
    ("S3_Combined", "Combined", "#2ECC71"),
]):
    deltas = [rank_changes[cn][f"{s_key}_score_delta"] for cn in all_city_names]
    ax.bar(x + j*width, deltas, width, label=s_label, color=color, alpha=0.8, edgecolor="white")

ax.set_xticks(x + width)
ax.set_xticklabels(all_city_names, fontsize=9)
ax.set_ylabel("TOPSIS Score Change", fontsize=11)
ax.set_title("Marginal Benefit of Strategy Scenarios by City", fontsize=13, fontweight="bold")
ax.axhline(y=0, color="black", linewidth=0.8, linestyle="--")
ax.legend(fontsize=9)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "fig_q4c_marginal_benefit.png"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("[Figure] fig_q4c_marginal_benefit.png saved.")

# Sorted rank stability
print("\n--- Rank Stability Summary ---")
for city_name in all_city_names:
    ranks = [int(all_results[s].loc[city_name, "rank"]) for s in scenario_names]
    rank_range = max(ranks) - min(ranks)
    print(f"  {city_name:<15s}: ranks = {ranks}, range = {rank_range}")

print("\n" + "=" * 70)
print("PROBLEM 4c COMPLETE")
print("=" * 70)
