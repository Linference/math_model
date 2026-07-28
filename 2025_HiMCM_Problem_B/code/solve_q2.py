#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Problem 2: AHP (Analytic Hierarchy Process) — Weight Determination
- 3-level hierarchy: Goal → 6 Criteria → 12 Indicators
- Judgment matrices with CR < 0.1 consistency check
- Uses EIGENVECTOR METHOD (principal right eigenvector) for both weights and lambda_max
  (consistent with Saaty's original method; resolves previous GM/eigenvalue inconsistency)
- Outputs indicator weights for use by q3a/q3b/q4*
- Added: collinearity diagnostics (correlation matrix + VIF)

Dependencies: numpy, pandas, matplotlib
Usage: /d/anaconda/python solve_q2.py
"""
import sys, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.random.seed(42)

sys.path.insert(0, r"C:\Users\HUAWEI\.claude\skills\math-modeling\scripts")
from plot_helpers import heatmap

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
RES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)

# ============================================================
# AHP Core Functions
# ============================================================
RI_TABLE = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24,
            7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}

def ahp_weights_eigenvector(judgment_matrix, name="Matrix"):
    """
    Compute AHP weights using PRINCIPAL EIGENVECTOR METHOD (Saaty's standard).
    Both weights and lambda_max come from the eigen decomposition.
    This ensures full consistency between reported weights and CR values.

    Returns (weights, CR, lambda_max)
    """
    A = np.array(judgment_matrix, dtype=float)
    n = A.shape[0]

    # Eigenvector method — principal right eigenvector
    eigenvalues, eigenvectors = np.linalg.eig(A)
    max_idx = np.argmax(np.abs(eigenvalues))
    lambda_max = np.real(eigenvalues[max_idx])
    w = np.abs(np.real(eigenvectors[:, max_idx]))
    w = w / np.sum(w)

    CI = (lambda_max - n) / (n - 1) if n > 1 else 0
    RI = RI_TABLE.get(n, 1.49)
    CR = CI / RI if RI > 0 else 0

    # Verification: also compute GM weights and GM-based lambda for comparison
    gm = np.exp(np.mean(np.log(A), axis=1))
    w_gm = gm / np.sum(gm)
    Aw_gm = A @ w_gm
    lambda_max_gm = np.mean(Aw_gm / w_gm)
    CI_gm = (lambda_max_gm - n) / (n - 1) if n > 1 else 0
    CR_gm = CI_gm / RI if RI > 0 else 0

    print(f"  [Verification] Eigenvalue method:  lambda={lambda_max:.4f}, CI={CI:.6f}, CR={CR:.6f}")
    print(f"  [Verification] Geom-mean method:   lambda_gm={lambda_max_gm:.4f}, CI={CI_gm:.6f}, CR={CR_gm:.6f}")
    print(f"  [Verification] Using EIGENVALUE method for reporting (consistent with Saaty).")

    return w, CR, lambda_max


def print_ahp_results(matrix, names, title):
    """Pretty-print AHP judgment matrix and results."""
    n = len(names)
    w, cr, lam = ahp_weights_eigenvector(matrix, title)

    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print("Judgment Matrix:")
    header = "      " + "  ".join(f"{n:<8s}" for n in names)
    print(header)
    for i, name in enumerate(names):
        row_str = "  ".join(f"{matrix[i][j]:8.3f}" for j in range(n))
        print(f"  {name:<4s} {row_str}")

    status = "PASS" if cr < 0.1 else "FAIL (CR >= 0.1)"
    print(f"\n  Consistency: lambda_max = {lam:.4f}, CI = {abs((lam-n)/(n-1)):.6f}, "
          f"CR = {cr:.6f} [{status}]")
    print("  Weights:")
    for name, wi in zip(names, w):
        print(f"    {name:<25s}: {wi:.4f} ({wi*100:.1f}%)")
    return w, cr, lam


# ============================================================
# Hierarchy Structure Definition
# ============================================================
print("=" * 70)
print("PROBLEM 2: AHP Weight Determination (Eigenvector Method)")
print("3-Level Hierarchy: Goal → 6 Criteria → 12 Indicators")
print("=" * 70)

# --- Level 1: Criteria ---
criterion_names = [
    "C1_Energy_GHG",
    "C2_Water",
    "C3_Transport",
    "C4_Waste",
    "C5_Climate",
    "C6_Venue",
]
criterion_labels = [
    "Energy & Carbon\nEmissions",
    "Water\nResources",
    "Transportation &\nAccessibility",
    "Waste\nManagement",
    "Climate\nSuitability",
    "Venue\nSustainability",
]

# Judgment matrix (6x6) — based on Super Bowl environmental priorities
criteria_matrix = np.array([
    [1,    4,    2,    5,    3,    6   ],
    [1/4,  1,    1/3,  1,    1/2,  2   ],
    [1/2,  3,    1,    4,    2,    5   ],
    [1/5,  1,    1/4,  1,    1/2,  1   ],
    [1/3,  2,    1/2,  2,    1,    3   ],
    [1/6,  1/2,  1/5,  1,    1/3,  1   ],
])

crit_w, crit_cr, crit_lam = print_ahp_results(criteria_matrix, criterion_labels, "Criteria Level (6×6)")

# --- Level 2: Sub-criteria ---
print("\n" + "-"*50)
print("  Sub-Criteria Level (Indicators under Each Criterion)")
print("-"*50)

# All indicator definitions
# NOTE (Reviewer Issue 8): I12 (airport enplanements) re-classified:
# Moved from C1 (Energy & Carbon) to C3 (Transport & Accessibility).
# Reasoning: Airport throughput is an infrastructure/accessibility metric, not an
# energy/carbon metric. Higher throughput enables better long-haul connectivity,
# but also correlates with Scope 3 aviation emissions. Its net environmental
# sign depends on context (direct flights vs connections). We classify it as
# COST-TYPE under transport to reflect the Scope 3 risk, and discuss this
# directional ambiguity in the paper's collinearity section.

all_indicators = {
    # C1: Energy & Carbon (2 indicators — I12 MOVED to C3)
    "I1_grid_carbon":     {"label": "Grid Carbon Factor\n(kgCO2/kWh)", "direction": "cost"},
    "I2_renewable":       {"label": "Renewable Energy\nShare (%)",    "direction": "benefit"},

    # C2: Water (2 indicators)
    "I3_water_stress":    {"label": "Water Stress\n(WRI Score)",      "direction": "cost"},
    "I4_precipitation":   {"label": "Annual Precipitation\n(inches)",  "direction": "cost"},

    # C3: Transport (3 indicators — I12 added)
    "I5_transit":         {"label": "Public Transit\nShare (%)",      "direction": "benefit"},
    "I6_pop_density":     {"label": "Population Density\n(per sq mi)", "direction": "benefit"},
    "I12_airport":        {"label": "Airport Enplanements\n(Millions)", "direction": "cost"},

    # C4: Waste (1 indicator)
    "I7_recycling":       {"label": "Waste Recycling\nRate (%)",      "direction": "benefit"},

    # C5: Climate (2 indicators)
    "I8_feb_temp":        {"label": "Feb Temperature\nSuitability",   "direction": "benefit"},
    "I9_has_dome":        {"label": "Stadium Has\nDome (0/1)",        "direction": "benefit"},

    # C6: Venue (2 indicators)
    "I10_leed":           {"label": "Stadium LEED\nLevel (0-4)",      "direction": "benefit"},
    "I11_parkland":       {"label": "Parkland\n(% city area)",        "direction": "benefit"},
}

# Sub-criteria groups (with I12 moved to C3)
sub_criteria_groups = {
    "C1_Energy_GHG": {
        "indicators": ["I1_grid_carbon", "I2_renewable"],
        "matrix": np.array([
            [1,    3   ],   # grid_carbon > renewable
            [1/3,  1   ],
        ]),
    },
    "C2_Water": {
        "indicators": ["I3_water_stress", "I4_precipitation"],
        "matrix": np.array([
            [1,    3   ],
            [1/3,  1   ],
        ]),
    },
    "C3_Transport": {
        "indicators": ["I5_transit", "I6_pop_density", "I12_airport"],
        "matrix": np.array([
            [1,    3,    4   ],   # transit > density > airport
            [1/3,  1,    2   ],
            [1/4,  1/2,  1   ],
        ]),
    },
    "C4_Waste": {
        "indicators": ["I7_recycling"],
        "matrix": np.array([[1]]),
    },
    "C5_Climate": {
        "indicators": ["I8_feb_temp", "I9_has_dome"],
        "matrix": np.array([
            [1,    1/2 ],
            [2,    1   ],
        ]),
    },
    "C6_Venue": {
        "indicators": ["I10_leed", "I11_parkland"],
        "matrix": np.array([
            [1,    3   ],
            [1/3,  1   ],
        ]),
    },
}

# Compute sub-criteria weights
all_sub_weights = {}
all_cr_checks = {}
for crit_key, group in sub_criteria_groups.items():
    inds = group["indicators"]
    labels = [all_indicators[i]["label"] for i in inds]
    sub_w, sub_cr, _ = print_ahp_results(group["matrix"], labels, f"{crit_key} Sub-Criteria")
    all_sub_weights[crit_key] = dict(zip(inds, sub_w))
    all_cr_checks[crit_key] = sub_cr

# --- Level 3: Global weights ---
print("\n" + "=" * 70)
print("  GLOBAL INDICATOR WEIGHTS (criteria_weight × sub_criteria_weight)")
print("=" * 70)

global_weights = {}
crit_w_dict = dict(zip(criterion_names, crit_w))

print(f"\n{'Indicator':<20s} {'Criteria':>20s} {'C-Weight':>8s} {'S-Weight':>8s} {'Global':>8s} {'Dir':>8s}")
print("-" * 85)

for crit_key in criterion_names:
    for ind_key in sub_criteria_groups[crit_key]["indicators"]:
        cw = crit_w_dict[crit_key]
        sw = all_sub_weights[crit_key][ind_key]
        gw = cw * sw
        global_weights[ind_key] = gw
        direction = all_indicators[ind_key]["direction"]
        print(f"  {ind_key:<20s} {crit_key:>20s} {cw:8.4f} {sw:8.4f} {gw:8.4f} {direction:>8s}")

total_gw = sum(global_weights.values())
print(f"\n  Sum of global weights: {total_gw:.6f} (should be 1.0)")

# Verify all CR < 0.1
all_pass = all(cr < 0.1 for cr in all_cr_checks.values()) and crit_cr < 0.1
print(f"\n  All CR checks: {'ALL PASS (CR < 0.1)' if all_pass else 'SOME FAIL'}")

# ============================================================
# Collinearity Diagnostics (Reviewer Issue 3)
# ============================================================
print("\n" + "=" * 70)
print("  COLLINEARITY DIAGNOSTICS")
print("  Addressing potential violation of AHP independence assumption")
print("=" * 70)

# Load city indicator data
cities = pd.read_csv(os.path.join(DATA_DIR, "city_indicators.csv"))

# Indicator-to-column mapping (for VIF computation)
vif_col_map = {
    "I1_grid_carbon":  "grid_carbon_factor_kgCO2_per_kWh",
    "I2_renewable":    "renewable_share_pct",
    "I12_airport":     "airport_enplanements_millions_2024",
    "I3_water_stress": "water_stress_wri_score",
    "I4_precipitation":"annual_precip_inches",
    "I5_transit":      "public_transit_share_pct",
    "I6_pop_density":  "population_density_per_sqmi",
    "I7_recycling":    "waste_recycling_rate_pct",
    "I9_has_dome":     "stadium_has_dome",
    "I10_leed":        "stadium_leed_level",
    "I11_parkland":    "parkland_pct_city_area",
}

ind_keys_for_vif = list(vif_col_map.keys())
n_vif = len(ind_keys_for_vif)
X_vif = np.zeros((len(cities), n_vif))
for j, key in enumerate(ind_keys_for_vif):
    X_vif[:, j] = cities[vif_col_map[key]].values

# Correlation matrix
corr_matrix = np.corrcoef(X_vif.T)

print("\n  Correlation Matrix (|r| > 0.5 highlighted):")
print(f"  {'':>16s}", end="")
for k in ind_keys_for_vif:
    print(f"  {k[:8]:>8s}", end="")
print()
for i, ki in enumerate(ind_keys_for_vif):
    print(f"  {ki:>16s}", end="")
    for j in range(n_vif):
        marker = " ***" if abs(corr_matrix[i,j]) > 0.7 else "  *" if abs(corr_matrix[i,j]) > 0.5 else "   "
        print(f"  {corr_matrix[i,j]:+5.2f}{marker}", end="")
    print()

# Identify high-correlation pairs
print("\n  High-correlation pairs (|r| > 0.5):")
high_corr_pairs = []
for i in range(n_vif):
    for j in range(i+1, n_vif):
        if abs(corr_matrix[i,j]) > 0.5:
            high_corr_pairs.append((ind_keys_for_vif[i], ind_keys_for_vif[j], corr_matrix[i,j]))
            print(f"    {ind_keys_for_vif[i]} <-> {ind_keys_for_vif[j]}: r = {corr_matrix[i,j]:+.3f}")

# VIF computation (simplified: regress each indicator on all others)
print("\n  Variance Inflation Factors (VIF):")
try:
    # Add intercept
    X_design = np.hstack([np.ones((X_vif.shape[0], 1)), X_vif])
    vif_values = {}
    for j in range(n_vif):
        y = X_vif[:, j]
        # OLS: regress indicator j on all others + intercept
        X_other = np.delete(X_design, j+1, axis=1)  # delete column j+1 (j+1 because intercept at col 0)
        try:
            beta = np.linalg.lstsq(X_other, y, rcond=None)[0]
            y_pred = X_other @ beta
            ss_res = np.sum((y - y_pred)**2)
            ss_tot = np.sum((y - np.mean(y))**2)
            r_squared = 1 - ss_res / ss_tot if ss_tot > 1e-10 else 0
            vif = 1.0 / (1.0 - r_squared) if r_squared < 0.999 else float('inf')
        except:
            vif = float('inf')
        vif_values[ind_keys_for_vif[j]] = vif
        severity = "HIGH" if vif > 10 else "MODERATE" if vif > 5 else "LOW"
        print(f"    {ind_keys_for_vif[j]:<20s}: VIF = {vif:6.2f}  [{severity}]")
except Exception as e:
    print(f"    VIF computation error: {e}")

# Collinearity summary
print("\n  Collinearity Assessment:")
print(f"    I1 (grid carbon) & I2 (renewable):     r = {corr_matrix[0,1]:+.3f} — negative correlation expected.")
print(f"    I5 (transit) & I6 (pop density):       r = {corr_matrix[4,5]:+.3f} — positive correlation expected.")
print(f"    I1+I2 combined AHP weight (under C1):   {(global_weights.get('I1_grid_carbon',0)+global_weights.get('I2_renewable',0))*100:.1f}%")
print(f"    I5+I6 combined AHP weight (under C3):   {(global_weights.get('I5_transit',0)+global_weights.get('I6_pop_density',0))*100:.1f}%")
print(f"    Recommendation: Paper should discuss ANP alternative or merged indices.")

# ============================================================
# Save weights for downstream use
# ============================================================
weight_records = []
for ind_key, gw in global_weights.items():
    weight_records.append({
        "indicator": ind_key,
        "global_weight": gw,
        "direction": all_indicators[ind_key]["direction"],
        "label": all_indicators[ind_key]["label"].replace("\n", " "),
    })
weight_df = pd.DataFrame(weight_records)
weight_df.to_csv(os.path.join(RES_DIR, "ahp_weights.csv"), index=False)
print(f"\n  AHP weights saved to results/ahp_weights.csv")

# ============================================================
# Figure 1: AHP hierarchy diagram (weights bar chart)
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left: Criteria weights
ax1 = axes[0]
crit_colors = ["#E74C3C", "#3498DB", "#F39C12", "#27AE60", "#9B59B6", "#1ABC9C"]
bars = ax1.barh(range(6), crit_w * 100, color=crit_colors, edgecolor="white")
ax1.set_yticks(range(6))
ax1.set_yticklabels([l.replace("\n", " ") for l in criterion_labels], fontsize=10)
ax1.invert_yaxis()
ax1.set_xlabel("Weight (%)", fontsize=11)
ax1.set_title("AHP Criteria Weights", fontsize=13, fontweight="bold")
for bar, w in zip(bars, crit_w * 100):
    ax1.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2.,
             f"{w:.1f}%", va="center", fontsize=9, fontweight="bold")
ax1.grid(axis="x", alpha=0.3)

# Right: Global indicator weights (sorted)
ax2 = axes[1]
sorted_gw = sorted(global_weights.items(), key=lambda x: x[1], reverse=True)
ind_names = [all_indicators[k]["label"] for k, _ in sorted_gw]
ind_vals = [v * 100 for _, v in sorted_gw]
ind_colors = ["#E74C3C" if v > 10 else "#F39C12" if v > 5 else "#3498DB" for v in ind_vals]
bars = ax2.barh(range(len(ind_vals)), ind_vals, color=ind_colors, edgecolor="white")
ax2.set_yticks(range(len(ind_vals)))
ax2.set_yticklabels(ind_names, fontsize=9)
ax2.invert_yaxis()
ax2.set_xlabel("Global Weight (%)", fontsize=11)
ax2.set_title("AHP Global Indicator Weights (12 Indicators)", fontsize=13, fontweight="bold")
for bar, v in zip(bars, ind_vals):
    ax2.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2.,
             f"{v:.1f}%", va="center", fontsize=8, fontweight="bold")
ax2.grid(axis="x", alpha=0.3)

plt.tight_layout(pad=2)
fig.savefig(os.path.join(FIG_DIR, "fig_q2_ahp_weights.png"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("[Figure] fig_q2_ahp_weights.png saved.")

# ---- Figure 2: Correlation between indicator weights and criteria ----
fig, ax = plt.subplots(figsize=(10, 6))

crit_ind_matrix = np.zeros((6, 12))
all_ind_keys = list(global_weights.keys())
for i, crit_key in enumerate(criterion_names):
    for j, ind_key in enumerate(all_ind_keys):
        if ind_key in sub_criteria_groups[crit_key]["indicators"]:
            crit_ind_matrix[i, j] = global_weights[ind_key]

criterion_labels_short = ["Energy &\nCarbon", "Water", "Transport", "Waste", "Climate", "Venue"]
ind_labels_short = [all_indicators[k]["label"].split("\n")[0] for k in all_ind_keys]

im = ax.imshow(crit_ind_matrix * 100, cmap="YlOrRd", aspect="auto")
fig.colorbar(im, ax=ax, label="Global Weight (%)")
ax.set_xticks(range(len(all_ind_keys)))
ax.set_xticklabels(ind_labels_short, rotation=45, ha="right", fontsize=8)
ax.set_yticks(range(6))
ax.set_yticklabels(criterion_labels_short, fontsize=10)
for i in range(6):
    for j in range(12):
        if crit_ind_matrix[i, j] > 0:
            ax.text(j, i, f"{crit_ind_matrix[i,j]*100:.1f}", ha="center", va="center",
                    fontsize=8, color="white" if crit_ind_matrix[i,j] > 0.05 else "black")
ax.set_title("Criteria-Indicator Weight Distribution\n(C1-C6 rows × I1-I12 columns)", fontsize=12, fontweight="bold")
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "fig_q2_weight_matrix.png"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("[Figure] fig_q2_weight_matrix.png saved.")

# ============================================================
# Figure 3: Correlation matrix heatmap (collinearity diagnostic)
# ============================================================
fig, ax = plt.subplots(figsize=(9, 7))
im = ax.imshow(corr_matrix, cmap="RdBu_r", aspect="auto", vmin=-1, vmax=1)
fig.colorbar(im, ax=ax, label="Pearson r")
ax.set_xticks(range(n_vif))
ax.set_xticklabels([k[:10] for k in ind_keys_for_vif], rotation=45, ha="right", fontsize=8)
ax.set_yticks(range(n_vif))
ax.set_yticklabels([k[:10] for k in ind_keys_for_vif], fontsize=9)
for i in range(n_vif):
    for j in range(n_vif):
        ax.text(j, i, f"{corr_matrix[i,j]:+.2f}", ha="center", va="center",
                fontsize=7, color="white" if abs(corr_matrix[i,j]) > 0.5 else "black")
ax.set_title("Indicator Correlation Matrix\n(Addressing AHP Independence Assumption)",
             fontsize=12, fontweight="bold")
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "fig_q2_correlation_matrix.png"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("[Figure] fig_q2_correlation_matrix.png saved.")

# Summary
print("\n" + "=" * 70)
print("PROBLEM 2 COMPLETE (Eigenvector Method)")
print(f"  Hierarchy: Goal → 6 Criteria → 12 Indicators")
print(f"  Criteria: lambda_max = {crit_lam:.4f}, CI = {(crit_lam-6)/(5):.6f}, CR = {crit_cr:.4f}")
print(f"  All sub-CR: {'PASS' if all_pass else 'FAIL'}")
print(f"  Top-3 indicators by weight:")
for i, (k, v) in enumerate(sorted_gw[:3], 1):
    print(f"    {i}. {all_indicators[k]['label'].split(chr(10))[0]}: {v*100:.1f}%")
print(f"  Collinearity: I1-I2 r={corr_matrix[0,1]:+.3f}, I5-I6 r={corr_matrix[4,5]:+.3f}")
print("=" * 70)
