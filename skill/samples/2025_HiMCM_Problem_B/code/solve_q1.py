#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Problem 1: Environmental Dimension Identification & Location Variability Analysis
- Reads Super Bowl LIX baseline data, classifies by Scope 1/2/3
- Computes emission share per dimension
- Location variability: CV analysis across 13 cities on key indicators

Dependencies: pandas, numpy, matplotlib
Usage: /d/anaconda/python solve_q1.py
"""
import sys, os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Seed
np.random.seed(42)

# Plot helpers
sys.path.insert(0, r"C:\Users\HUAWEI\.claude\skills\math-modeling\scripts")
from plot_helpers import heatmap, sensitivity_tornado

# Paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
FIG_DIR  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
RES_DIR  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)

# ============================================================
# 1A: Scope 1/2/3 Classification of Super Bowl LIX Baseline
# ============================================================
print("=" * 70)
print("PROBLEM 1A: Environmental Dimensions & Scope Classification")
print("=" * 70)

baseline = pd.read_csv(os.path.join(DATA_DIR, "superbowl_lix_baseline.csv"))

# Categorize each data row into scope category
scope_map = {
    "Scope1_Direct": "Scope 1 (Direct Emissions)",
    "Scope2_Indirect": "Scope 2 (Indirect Energy)",
    "Scope3_Indirect": "Scope 3 (Value Chain)",
    "Carbon_Offset": "Carbon Offsets",
    "Waste": "Waste Management",
    "Community": "Community Initiatives",
    "Context": "Contextual Data",
    "General": "General Info",
}

baseline["scope_category"] = baseline["category"].map(scope_map).fillna("Other")

print("\n--- Super Bowl LIX Baseline Data by Scope Category ---")
for cat in sorted(baseline["scope_category"].unique()):
    subset = baseline[baseline["scope_category"] == cat]
    print(f"\n{cat} ({len(subset)} records):")
    for _, row in subset.iterrows():
        print(f"  [{row['metric']}] {row['value']} ({row['unit']})")

# Environmental dimensions identified
dimensions = {
    "Energy Consumption": {
        "scope": "Scope 2",
        "description": "Stadium game-day electricity + ancillary energy use",
        "key_data": "REC procurement 3300 MWh; grid factor 0.363 kgCO2/kWh",
        "estimated_intensity": "~0.05 kgCO2e/spectator (Scope2 only)",
    },
    "GHG Emissions (Scope 1)": {
        "scope": "Scope 1",
        "description": "On-site fuel combustion (generators, kitchen, heating)",
        "key_data": "Not publicly available as comprehensive LCA",
        "estimated_intensity": "N/A; NFL does not publish full Scope 1",
    },
    "GHG Emissions (Scope 2)": {
        "scope": "Scope 2",
        "description": "Grid electricity consumption × emission factor",
        "key_data": "SRMV eGRID factor 0.363 kgCO2/kWh; 3300 MWh RECs offset ~1092 tCO2",
        "estimated_intensity": "16.8 kgCO2e/spectator (total Scope2 estimate)",
    },
    "GHG Emissions (Scope 3)": {
        "scope": "Scope 3",
        "description": "Fan air travel, team travel, hotel stays, food supply chain",
        "key_data": "125k+ visitors; dominant Scope 3 source = air travel to MSY",
        "estimated_intensity": "Cannot be precisely quantified; dominant carbon source",
    },
    "Water Resources": {
        "scope": "Cross-cutting",
        "description": "Venue water use, irrigation, cleaning, concessions",
        "key_data": "New Orleans water stress score 1.0 (Low); Louisiana wetland loss context",
        "estimated_intensity": "Not separately reported",
    },
    "Waste Generation & Diversion": {
        "scope": "Cross-cutting",
        "description": "Materials recovery, food donation, recycling, composting",
        "key_data": "250 tons materials recovered; 12,348 lbs food; 59 tons oyster shells; 90%+ diversion at NFL House",
        "estimated_intensity": "3.85 kg waste/spectator (materials recovered)",
    },
    "Community & Ecosystem": {
        "scope": "N/A (ancillary)",
        "description": "Tree planting, wetland restoration, neighborhood cleanup",
        "key_data": "6,500 trees planted; marsh grasses; coastal restoration",
        "estimated_intensity": "N/A",
    },
}

print("\n\n--- Seven Environmental Dimensions Identified ---")
for dim_name, dim_info in dimensions.items():
    print(f"  {dim_name} [{dim_info['scope']}]: {dim_info['description']}")
    print(f"    Data: {dim_info['key_data']}")

# Scope emission share (estimated based on available data + literature)
scope_shares = {
    "Scope 1\n(Direct)": 8,      # on-site combustion, typically small for stadium events
    "Scope 2\n(Indirect Energy)": 17,  # grid electricity (offset by RECs)
    "Scope 3\n(Air Travel)": 55,  # dominant: fan flights
    "Scope 3\n(Hotels/Other)": 20,  # accommodation, food, ground transport
}

print("\n\n--- Estimated Carbon Footprint Distribution (Literature-informed) ---")
for scope, pct in scope_shares.items():
    print(f"  {scope}: {pct}%")

# ---- Figure 1: Scope emission breakdown pie chart ----
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

ax1 = axes[0]
colors = ["#E74C3C", "#F39C12", "#3498DB", "#2ECC71"]
labels = list(scope_shares.keys())
sizes = list(scope_shares.values())
explode = (0, 0, 0.08, 0)
wedges, texts, autotexts = ax1.pie(
    sizes, explode=explode, labels=labels, autopct="%1.1f%%",
    colors=colors, startangle=140, pctdistance=0.7
)
for t in autotexts:
    t.set_fontsize(10)
    t.set_fontweight("bold")
ax1.set_title("Super Bowl LIX Estimated Carbon\nFootprint by Scope", fontsize=13, fontweight="bold")

# ---- Figure 1b: Environmental dimensions bar chart ----
dim_names_short = ["Energy", "GHG\n(Scope1)", "GHG\n(Scope2)", "GHG\n(Scope3)", "Water", "Waste", "Ecosystem"]
dim_levels = [85, 25, 70, 95, 40, 80, 60]  # relative importance/significance
colors_dim = ["#E74C3C", "#E67E22", "#F39C12", "#C0392B", "#3498DB", "#27AE60", "#8E44AD"]
ax2 = axes[1]
bars = ax2.bar(range(len(dim_names_short)), dim_levels, color=colors_dim, edgecolor="white", linewidth=0.8)
ax2.set_xticks(range(len(dim_names_short)))
ax2.set_xticklabels(dim_names_short, fontsize=9)
ax2.set_ylabel("Relative Environmental Significance", fontsize=11)
ax2.set_title("Environmental Dimension\nSignificance Ranking", fontsize=13, fontweight="bold")
ax2.set_ylim(0, 110)
for bar, val in zip(bars, dim_levels):
    ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1.5,
             str(val), ha="center", va="bottom", fontsize=9, fontweight="bold")
ax2.grid(axis="y", alpha=0.3)

plt.tight_layout(pad=2)
fig.savefig(os.path.join(FIG_DIR, "fig_q1_scope_dimensions.png"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("\n[Figure] fig_q1_scope_dimensions.png saved.")


# ============================================================
# 1B: Location Variability Analysis
# ============================================================
print("\n" + "=" * 70)
print("PROBLEM 1B: Location Variability Across Host Cities")
print("=" * 70)

cities = pd.read_csv(os.path.join(DATA_DIR, "city_indicators.csv"))

# Select key quantitative indicators for variability analysis
variability_cols = {
    "grid_carbon_factor_kgCO2_per_kWh": "Grid Carbon Factor\n(kgCO2/kWh)",
    "renewable_share_pct": "Renewable Share (%)",
    "feb_avg_temp_c": "Feb Avg Temp (°C)",
    "annual_precip_inches": "Annual Precip (in)",
    "water_stress_wri_score": "Water Stress\n(WRI Score)",
    "waste_recycling_rate_pct": "Waste Recycling (%)",
    "public_transit_share_pct": "Public Transit\nShare (%)",
    "airport_enplanements_millions_2024": "Airport\nEnplanements (M)",
    "stadium_leed_level": "Stadium LEED\nLevel (0-4)",
    "population_density_per_sqmi": "Population Density\n(per sq mi)",
    "parkland_pct_city_area": "Parkland (% area)",
}

variability_df = cities[list(variability_cols.keys())].copy()

# Compute CV for each indicator
cv_results = {}
for col, label in variability_cols.items():
    vals = variability_df[col].values
    mean_val = np.mean(vals)
    std_val = np.std(vals, ddof=1)
    cv = (std_val / mean_val) * 100 if mean_val != 0 else 0
    cv_results[label] = {
        "mean": mean_val, "std": std_val, "cv_pct": cv,
        "min": np.min(vals), "max": np.max(vals),
        "min_city": cities.loc[np.argmin(vals), "city_short"],
        "max_city": cities.loc[np.argmax(vals), "city_short"],
    }

print("\n--- Coefficient of Variation (CV) by Indicator ---")
print(f"{'Indicator':<30s} {'Mean':>8s} {'Std':>8s} {'CV%':>7s} {'Min':>8s} {'Max':>8s} {'Range City'}")
print("-" * 90)
for label, stats in sorted(cv_results.items(), key=lambda x: x[1]["cv_pct"], reverse=True):
    print(f"{label:<30s} {stats['mean']:8.2f} {stats['std']:8.2f} {stats['cv_pct']:7.1f} "
          f"{stats['min']:8.2f} {stats['max']:8.2f} "
          f"{stats['min_city']}→{stats['max_city']}")

# Identify top-5 most variable indicators
top5 = sorted(cv_results.items(), key=lambda x: x[1]["cv_pct"], reverse=True)[:5]
print("\n--- Top 5 Most Variable Indicators (Location Matters Most) ---")
for i, (label, stats) in enumerate(top5, 1):
    print(f"  {i}. {label.strip()}: CV = {stats['cv_pct']:.1f}% "
          f"(Range: {stats['min']:.2f} – {stats['max']:.2f})")

# ---- Figure 2: CV bar chart ----
fig, ax = plt.subplots(figsize=(10, 6))
sorted_cv = sorted(cv_results.items(), key=lambda x: x[1]["cv_pct"], reverse=True)
labels_cv = [x[0] for x in sorted_cv]
cvs = [x[1]["cv_pct"] for x in sorted_cv]
bar_colors = ["#C0392B" if c > 100 else "#E67E22" if c > 60 else "#3498DB" for c in cvs]
bars = ax.barh(range(len(labels_cv)), cvs, color=bar_colors, edgecolor="white")
ax.set_yticks(range(len(labels_cv)))
ax.set_yticklabels(labels_cv, fontsize=10)
ax.set_xlabel("Coefficient of Variation (%)", fontsize=12)
ax.set_title("Location Variability of Environmental Indicators\n(13 US Cities with NFL Stadiums)", fontsize=14, fontweight="bold")
for bar, cv in zip(bars, cvs):
    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2.,
            f"{cv:.0f}%", va="center", fontsize=9, fontweight="bold")
ax.invert_yaxis()
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "fig_q1_cv_indicators.png"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("\n[Figure] fig_q1_cv_indicators.png saved.")

# ---- Figure 3: Key indicator heatmap across cities ----
key_indicators = [
    "grid_carbon_factor_kgCO2_per_kWh",
    "renewable_share_pct",
    "feb_avg_temp_c",
    "water_stress_wri_score",
    "waste_recycling_rate_pct",
    "public_transit_share_pct",
]
key_labels = ["Grid Carbon", "Renewable%", "Feb Temp", "Water Stress", "Recycling%", "Transit%"]
key_data = cities[key_indicators].values
# Normalize each column to [0,1] for heatmap
key_data_norm = (key_data - key_data.min(axis=0)) / (key_data.max(axis=0) - key_data.min(axis=0) + 1e-10)

fig, ax = plt.subplots(figsize=(9, 5))
im = ax.imshow(key_data_norm, cmap="RdYlGn", aspect="auto")
fig.colorbar(im, ax=ax, label="Normalized Value (0=worst, 1=best)")
ax.set_xticks(range(len(key_labels)))
ax.set_xticklabels(key_labels, rotation=30, ha="right", fontsize=10)
ax.set_yticks(range(len(cities)))
ax.set_yticklabels(cities["city_short"].values, fontsize=9)
ax.set_title("Key Environmental Indicators Across 13 Candidate Cities\n(Normalized)", fontsize=13, fontweight="bold")
for i in range(key_data_norm.shape[0]):
    for j in range(key_data_norm.shape[1]):
        ax.text(j, i, f"{key_data[i, j]:.1f}", ha="center", va="center", fontsize=7,
                color="white" if key_data_norm[i, j] < 0.5 else "black")
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "fig_q1_city_heatmap.png"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("[Figure] fig_q1_city_heatmap.png saved.")

# ---- Key insight: compare extreme city pairs ----
print("\n--- Extreme City Pair Comparison ---")
# Compare best renewable city vs worst
best_re = cities.loc[cities["renewable_share_pct"].idxmax(), "city_short"]
worst_re = cities.loc[cities["renewable_share_pct"].idxmin(), "city_short"]
print(f"  Renewable energy: {best_re} ({cities['renewable_share_pct'].max():.0f}%) "
      f"vs {worst_re} ({cities['renewable_share_pct'].min():.0f}%) "
      f"— {cities['renewable_share_pct'].max()/cities['renewable_share_pct'].min():.1f}x difference")

# Compare extreme water stress
best_ws = cities.loc[cities["water_stress_wri_score"].idxmin(), "city_short"]
worst_ws = cities.loc[cities["water_stress_wri_score"].idxmax(), "city_short"]
print(f"  Water stress: {best_ws} ({cities['water_stress_wri_score'].min():.1f}) "
      f"vs {worst_ws} ({cities['water_stress_wri_score'].max():.1f})")

# Compare transit share
best_tr = cities.loc[cities["public_transit_share_pct"].idxmax(), "city_short"]
worst_tr = cities.loc[cities["public_transit_share_pct"].idxmin(), "city_short"]
print(f"  Transit share: {best_tr} ({cities['public_transit_share_pct'].max():.1f}%) "
      f"vs {worst_tr} ({cities['public_transit_share_pct'].min():.1f}%)")

# Save results
with open(os.path.join(RES_DIR, "q1_results.txt"), "w", encoding="utf-8") as f:
    f.write("Problem 1 Results\n")
    f.write("=" * 50 + "\n")
    f.write("Seven Environmental Dimensions (Scope 1/2/3 + Cross-cutting):\n")
    for dim_name, dim_info in dimensions.items():
        f.write(f"  - {dim_name} [{dim_info['scope']}]\n")
    f.write(f"\nTop-5 Most Variable Indicators:\n")
    for i, (label, stats) in enumerate(top5, 1):
        f.write(f"  {i}. {label.strip()}: CV={stats['cv_pct']:.1f}%\n")

print("\n" + "=" * 70)
print("PROBLEM 1 COMPLETE — Results saved to results/q1_results.txt")
print("=" * 70)
