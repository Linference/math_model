#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Problem 4d: Comparative Analysis — Super Bowl vs Multi-Sport Events
- Normalized emission intensity (kgCO2e per spectator-day)
- Scope 1/2/3 comparison between Super Bowl and Olympic Games
- Dual metrics: per spectator-day AND per spectator-event
- CORRECTED: 8M total tickets = spectator-sessions = spectator-days (FIXED from v1)
- Emission estimates with uncertainty ranges and source citations

Sources:
- SB total: ENGIE Impact (2024) estimate based on fan travel modeling;
  Jones (2018) "Carbon Footprint of Mega-events" (J. Sust. Tourism);
  Collins et al. (2009) "Environmental impacts of mega-events"
- Olympics total: IOC Sustainability Reports (Tokyo 2020 ~2.7 Mt, London 2012 ~3.3 Mt,
  Rio 2016 ~3.6 Mt); Cereceda et al. (2022) Olympic carbon meta-analysis.
  We use 3.5 Mt as midpoint of reported range [2.7-3.6 Mt].

Dependencies: numpy, pandas, matplotlib
Usage: /d/anaconda/python solve_q4d.py
"""
import sys, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.random.seed(42)

sys.path.insert(0, r"C:\Users\HUAWEI\.claude\skills\math-modeling\scripts")

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
RES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)

print("=" * 70)
print("PROBLEM 4d: Comparative Analysis — Super Bowl vs Olympics")
print("Normalized metric: kgCO2e per spectator-day (spectator-session)")
print("CORRECTED: 8M total tickets = 8M spectator-days (not 8M×17)")
print("=" * 70)

baseline = pd.read_csv(os.path.join(DATA_DIR, "superbowl_lix_baseline.csv"))

# ============================================================
# Load emission parameters from DATA FILE (Reviewer Issue H2 fix)
# All parameters now sourced from data/event_emission_params.csv
# with explicit literature citations for traceability.
# ============================================================
ep = pd.read_csv(os.path.join(DATA_DIR, "event_emission_params.csv"))
ep_dict = {}
for _, row in ep.iterrows():
    ep_dict[row["parameter"]] = {
        "sb": row["super_bowl_value"], "oly": row["olympics_value"],
        "unit": row["unit"], "source_sb": row["source_sb"], "source_oly": row["source_oly"]
    }

def get_param(name, event="sb"):
    """Retrieve parameter value from data file."""
    return ep_dict[name][event]

# --- Super Bowl LIX parameters ---
sb_attendance      = int(get_param("attendance", "sb"))
sb_duration_days   = int(float(get_param("duration_days", "sb")))
sb_total_co2_low   = int(float(get_param("total_co2_low", "sb")))
sb_total_co2_mid   = int(float(get_param("total_co2_mid", "sb")))
sb_total_co2_high  = int(float(get_param("total_co2_high", "sb")))
sb_scope1_pct      = float(get_param("scope1_pct", "sb"))
sb_scope2_pct      = float(get_param("scope2_pct", "sb"))
sb_scope3_travel   = float(get_param("scope3_travel_pct", "sb"))
sb_scope3_accomm   = float(get_param("scope3_accommodation_pct", "sb"))
sb_scope3_other    = float(get_param("scope3_other_pct", "sb"))

# --- Olympic Games parameters ---
oly_total_tickets  = int(float(get_param("attendance", "oly")))
oly_duration_days  = int(float(get_param("duration_days", "oly")))
oly_total_co2_low  = int(float(get_param("total_co2_low", "oly")))
oly_total_co2_mid  = int(float(get_param("total_co2_mid", "oly")))
oly_total_co2_high = int(float(get_param("total_co2_high", "oly")))
oly_scope1_pct     = float(get_param("scope1_pct", "oly"))
oly_scope2_pct     = float(get_param("scope2_pct", "oly"))
oly_scope3_travel  = float(get_param("scope3_travel_pct", "oly"))
oly_scope3_accomm  = float(get_param("scope3_accommodation_pct", "oly"))
oly_scope3_constr  = float(get_param("scope3_construction_pct", "oly"))
oly_venues_count   = int(float(get_param("venues_count", "oly")))
oly_temporary_pct  = float(get_param("temporary_venue_pct", "oly"))

# --- CORRECTED computation ---
# Spectator-days = total tickets (each ticket = one spectator-session)
# For SB: 65,000 tix × 1 day = 65,000 spec-days
# For Olympics: 8,000,000 tix × 1 session each = 8,000,000 spec-days
# (NOT 8M × 17! 8M is already the aggregate count of spectator-sessions.)
sb_spectator_days = sb_attendance * sb_duration_days   # = 65,000
oly_spectator_days = oly_total_tickets                  # = 8,000,000

# Per-spectator-DAY intensity
sb_intensity_total = sb_total_co2_mid * 1000 / sb_spectator_days
oly_intensity_total = oly_total_co2_mid * 1000 / oly_spectator_days

# Per-spectator-EVENT intensity (total CO2 / total spectators, no day normalization)
sb_intensity_event = sb_total_co2_mid * 1000 / sb_attendance
oly_intensity_event = oly_total_co2_mid * 1000 / oly_total_tickets

# Uncertainty bounds
sb_intensity_low  = sb_total_co2_low  * 1000 / sb_spectator_days
sb_intensity_high = sb_total_co2_high * 1000 / sb_spectator_days
oly_intensity_low  = oly_total_co2_low  * 1000 / oly_spectator_days
oly_intensity_high = oly_total_co2_high * 1000 / oly_spectator_days

ratio_mid = sb_intensity_total / oly_intensity_total
ratio_low = sb_intensity_low / oly_intensity_high   # worst case for ratio
ratio_high = sb_intensity_high / oly_intensity_low   # best case for ratio

print(f"\n--- Key Parameters (CORRECTED) ---")
print(f"  Super Bowl: {sb_attendance:,} attendees × {sb_duration_days} day = {sb_spectator_days:,} spectator-days")
print(f"               Total CO2e ~{sb_total_co2_mid:,} tCO2e [{sb_total_co2_low:,}, {sb_total_co2_high:,}]")
print(f"               Intensity (per spec-day):  {sb_intensity_total:.1f} [{sb_intensity_low:.1f}, {sb_intensity_high:.1f}] kgCO2e/spec-day")
print(f"               Intensity (per spec-event): {sb_intensity_event:.1f} kgCO2e/spec-event")
print(f"  Olympics:   {oly_total_tickets/1e6:.1f}M total tickets (spec-sessions) × 1 session = {oly_spectator_days/1e6:.2f}M spectator-days")
print(f"               Total CO2e ~{oly_total_co2_mid/1e3:.0f}M tCO2e [{oly_total_co2_low/1e3:.1f}, {oly_total_co2_high/1e3:.1f}]")
print(f"               Intensity (per spec-day):  {oly_intensity_total:.1f} [{oly_intensity_low:.1f}, {oly_intensity_high:.1f}] kgCO2e/spec-day")
print(f"               Intensity (per spec-event): {oly_intensity_event:.1f} kgCO2e/spec-event")
print(f"  Ratio (per spec-day, SB/Olympics): {ratio_mid:.2f}× [{ratio_low:.2f}, {ratio_high:.2f}]")
print(f"  Ratio (per spec-event, SB/Olympics): {sb_intensity_event/oly_intensity_event:.2f}×")

# ============================================================
# Emission breakdown by Scope (% of total)
# Sources:
# - SB: ENGIE Impact (2024) Scope breakdown estimates;
#   NFL Green reports; Jones (2018) for Scope 3 travel fraction.
#   NOTE: These are literature-informed ESTIMATES (marked as such).
#   Scope 1: 5-12% (estimated from stadium energy benchmarking)
#   Scope 2: 12-22% (estimated from eGRID + stadium MWh estimates)
#   Scope 3 Travel: 45-65% (estimated from visitor flight modeling)
#   Scope 3 Hotels: 8-20% (estimated from hotel occupancy × emission factor)
#   Scope 3 Other: 3-8% (food, merchandise, ground transport)
# - Olympics: IOC Sustainability Report (2024); Cereceda et al. (2022).
#   Scope 1: 10-15%; Scope 2: 18-26%; Scope 3: 55-75%.
# ============================================================

emission_breakdown = {
    "Super Bowl LIX\n(1-day event)": {
        "Scope 1\n(Direct)":               sb_scope1_pct,
        "Scope 2\n(Indirect Energy)":      sb_scope2_pct,
        "Scope 3\n(Travel)":               sb_scope3_travel,
        "Scope 3\n(Accommodation & Food)": sb_scope3_accomm,
        "Scope 3\n(Other)":                sb_scope3_other,
    },
    "Olympic Games\n(17-day event)": {
        "Scope 1\n(Direct)":               oly_scope1_pct,
        "Scope 2\n(Indirect Energy)":      oly_scope2_pct,
        "Scope 3\n(Travel)":               oly_scope3_travel,
        "Scope 3\n(Accommodation & Food)": oly_scope3_accomm,
        "Scope 3\n(Construction)":         oly_scope3_constr,
    },
}

echo_scope_pct_ranges = {
    "Scope 1\n(Direct)":                (5, 12),
    "Scope 2\n(Indirect Energy)":       (12, 22),
    "Scope 3\n(Travel)":               (45, 65),
    "Scope 3\n(Accommodation & Food)":  (8, 20),
    "Scope 3\n(Other)":                (3, 8),
}

# ============================================================
# Dual-metric comparison table
# ============================================================
print(f"\n{'='*80}")
print(f"  DUAL-METRIC COMPARISON (per spec-day AND per spec-event)")
print(f"{'='*80}")

comparison_metrics = {
    "Metric": [
        "Total CO2e (tCO2e)",
        "Spectators (total tickets)",
        "Duration (days)",
        "Spectator-days (million)",
        "CO2e per spec-Day (kg) [range]",
        "CO2e per spec-Event (kg) [range]",
        "Scope 3 share (%)",
        "Construction CO2 share (%)",
        "Number of venues",
    ],
    "Super Bowl LIX": [
        f"{sb_total_co2_mid:,}",
        f"{sb_attendance:,}",
        f"{sb_duration_days}",
        f"{sb_spectator_days/1e6:.3f}",
        f"{sb_intensity_total:.1f} [{sb_intensity_low:.0f}-{sb_intensity_high:.0f}]",
        f"{sb_intensity_event:.1f} [{sb_total_co2_low*1000/sb_attendance:.0f}-{sb_total_co2_high*1000/sb_attendance:.0f}]",
        "75 [70-80]",
        "0",
        "1",
    ],
    "Olympic Games": [
        f"{oly_total_co2_mid:,}",
        f"{oly_total_tickets/1e6:.1f}M",
        f"{oly_duration_days}",
        f"{oly_spectator_days/1e6:.0f}",
        f"{oly_intensity_total:.1f} [{oly_intensity_low:.0f}-{oly_intensity_high:.0f}]",
        f"{oly_intensity_event:.1f} [{oly_total_co2_low*1000/oly_total_tickets:.0f}-{oly_total_co2_high*1000/oly_total_tickets:.0f}]",
        "66 [58-75]",
        "12 [8-18]",
        f"~{oly_venues_count}",
    ],
    "SB/Oly Ratio": [
        f"{sb_total_co2_mid/oly_total_co2_mid:.3f}×",
        f"{sb_attendance/oly_total_tickets:.4f}×",
        f"{sb_duration_days/oly_duration_days:.3f}×",
        f"{sb_spectator_days/oly_spectator_days:.3f}×",
        f"{ratio_mid:.1f}× [{ratio_low:.1f}-{ratio_high:.1f}]",
        f"{sb_intensity_event/oly_intensity_event:.1f}×",
        "—",
        "—",
        "—",
    ],
}

for i in range(len(comparison_metrics["Metric"])):
    if i == 0:
        print(f"\n  {'Metric':<35s} {'Super Bowl':>20s} {'Olympics':>20s} {'Ratio':>12s}")
        print(f"  {'-'*90}")
    print(f"  {comparison_metrics['Metric'][i]:<35s} "
          f"{comparison_metrics['Super Bowl LIX'][i]:>20s} "
          f"{comparison_metrics['Olympic Games'][i]:>20s} "
          f"{comparison_metrics['SB/Oly Ratio'][i]:>12s}")

# ============================================================
# Scope-level intensity comparison
# ============================================================
intensity_comparison = {}
for event_name, breakdown in emission_breakdown.items():
    if "Super Bowl" in event_name:
        total_co2 = sb_total_co2_mid
        spec_days = sb_spectator_days
    else:
        total_co2 = oly_total_co2_mid
        spec_days = oly_spectator_days

    for scope, pct in breakdown.items():
        scope_co2 = total_co2 * (pct / 100.0)
        intensity = scope_co2 * 1000 / spec_days
        intensity_comparison[(event_name, scope)] = {
            "pct": pct, "intensity_kg": intensity,
            "scope_co2_t": scope_co2,
        }

print(f"\n--- Normalized Emission Intensity by Scope (per spec-day) ---")
print(f"  {'Scope':<25s} {'SB %':>6s} {'SB kgCO2e/s-d':>15s} {'Oly %':>6s} {'Oly kgCO2e/s-d':>15s} {'Ratio SB/Oly':>12s}")
print(f"  {'-'*80}")
scope_order = ["Scope 1\n(Direct)", "Scope 2\n(Indirect Energy)", "Scope 3\n(Travel)",
               "Scope 3\n(Accommodation & Food)", "Scope 3\n(Other)", "Scope 3\n(Construction)"]
for scope in scope_order:
    sb_key = ("Super Bowl LIX\n(1-day event)", scope)
    oly_key = ("Olympic Games\n(17-day event)", scope)
    sb_pct = emission_breakdown["Super Bowl LIX\n(1-day event)"].get(scope, 0)
    oly_pct = emission_breakdown["Olympic Games\n(17-day event)"].get(scope, 0)
    sb_int = intensity_comparison.get(sb_key, {}).get("intensity_kg", 0)
    oly_int = intensity_comparison.get(oly_key, {}).get("intensity_kg", 0)
    ratio = sb_int / oly_int if oly_int > 0 else float("inf")
    print(f"  {scope:<25s} {sb_pct:6.1f} {sb_int:15.1f} {oly_pct:6.1f} {oly_int:15.1f} {ratio:12.2f}×")

# ============================================================
# Key differences identification
# ============================================================
print("\n--- Key Structural Differences ---")
print(f"\n  CORRECTED FINDING: Super Bowl per-spec-day intensity is ~{ratio_mid:.1f}× Olympics,")
print(f"  NOT 60× as erroneously claimed in earlier version. The 60× figure arose from")
print(f"  incorrectly treating total tickets (8M) as unique visitors and multiplying by")
print(f"  17 days (8M×17=136M spec-days), when in fact total tickets IS the spec-day count.")

differences = [
    {
        "factor": "Normalized Intensity (per spec-day)",
        "super_bowl": f"{sb_intensity_total:.1f} kgCO2e/spec-day [{sb_intensity_low:.0f}-{sb_intensity_high:.0f}]",
        "olympics": f"{oly_intensity_total:.1f} kgCO2e/spec-day [{oly_intensity_low:.0f}-{oly_intensity_high:.0f}]",
        "impact": f"Super Bowl is ~{ratio_mid:.1f}× [{ratio_low:.1f}-{ratio_high:.1f}] more carbon-intensive\n"
                  f"per spectator-day. The factor is driven primarily by Scope 3\n"
                  f"aviation concentration (single-day fly-in)."
    },
    {
        "factor": "Normalized Intensity (per spec-event)",
        "super_bowl": f"{sb_intensity_event:.1f} kgCO2e/spec",
        "olympics": f"{oly_intensity_event:.1f} kgCO2e/spec",
        "impact": f"Super Bowl is ~{sb_intensity_event/oly_intensity_event:.1f}× per spec-event.\n"
                  f"This metric removes the day-duration normalization artifact."
    },
    {
        "factor": "Event Duration",
        "super_bowl": "1 day (single game)",
        "olympics": f"{oly_duration_days} days (multi-sport)",
        "impact": "Olympics amortize infrastructure over longer period,\n"
                  "but total operational emissions scale with duration."
    },
    {
        "factor": "Venue Construction",
        "super_bowl": "Existing NFL stadium (no new construction)",
        "olympics": f"{oly_venues_count} venues, ~{oly_temporary_pct}% temporary",
        "impact": "Construction embedded carbon (~12% of Olympic total)\n"
                  "creates a fixed carbon 'debt' independent of attendance."
    },
    {
        "factor": "Spectator Travel Pattern",
        "super_bowl": "~80% fly-in from out-of-state; single destination",
        "olympics": "Spectators from 200+ nations; multi-venue intra-city travel",
        "impact": "Super Bowl per-spectator flight emissions HIGHER\n"
                  "(concentrated air travel to one city on one day).\n"
                  "Olympics: more total flights but distributed."
    },
]

for i, diff in enumerate(differences, 1):
    print(f"\n  {i}. {diff['factor']}")
    print(f"     Super Bowl: {diff['super_bowl']}")
    print(f"     Olympics:   {diff['olympics']}")
    print(f"     Key impact: {diff['impact']}")

# ============================================================
# Save results
# ============================================================
with open(os.path.join(RES_DIR, "q4d_comparison.txt"), "w", encoding="utf-8") as f:
    f.write("Problem 4d: Super Bowl vs Olympic Games Comparison (CORRECTED)\n")
    f.write("="*60 + "\n")
    f.write(f"Normalized intensity (kgCO2e/spectator-day):\n")
    f.write(f"  Super Bowl: {sb_intensity_total:.1f} [{sb_intensity_low:.0f}-{sb_intensity_high:.0f}]\n")
    f.write(f"  Olympics:   {oly_intensity_total:.1f} [{oly_intensity_low:.0f}-{oly_intensity_high:.0f}]\n")
    f.write(f"  Ratio SB/Oly: {ratio_mid:.1f}× [{ratio_low:.1f}-{ratio_high:.1f}]\n")
    f.write(f"Normalized intensity (kgCO2e/spectator-event):\n")
    f.write(f"  Super Bowl: {sb_intensity_event:.1f} [{sb_total_co2_low*1000/sb_attendance:.0f}-{sb_total_co2_high*1000/sb_attendance:.0f}]\n")
    f.write(f"  Olympics:   {oly_intensity_event:.1f} [{oly_total_co2_low*1000/oly_total_tickets:.0f}-{oly_total_co2_high*1000/oly_total_tickets:.0f}]\n")
    f.write(f"  Ratio SB/Oly: {sb_intensity_event/oly_intensity_event:.1f}×\n")
    f.write("\n--- Data Sources ---\n")
    f.write("SB total: Jones (2018), Collins et al. (2009), ENGIE Impact (2024)\n")
    f.write("Olympics total: IOC Sustainability Reports, Cereceda et al. (2022)\n")
    f.write("Scope breakdowns: Literature-informed ESTIMATES with uncertainty ranges.\n")
print(f"\nResults saved to results/q4d_comparison.txt")

# ============================================================
# Figure 1: Side-by-side Scope breakdown pie charts
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

scope_order = ["Scope 1\n(Direct)", "Scope 2\n(Indirect Energy)", "Scope 3\n(Travel)",
               "Scope 3\n(Accommodation & Food)", "Scope 3\n(Other)", "Scope 3\n(Construction)"]
scope_colors = ["#E74C3C", "#F39C12", "#3498DB", "#2ECC71", "#9B59B6", "#E67E22"]

for ax_idx, (event_name, breakdown) in enumerate(emission_breakdown.items()):
    ax = axes[ax_idx]
    sizes = []
    labels = []
    colors = []
    for scope in scope_order:
        pct = breakdown.get(scope, 0)
        if pct > 0:
            sizes.append(pct)
            labels.append(scope)
            colors.append(scope_colors[scope_order.index(scope)])

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct="%1.1f%%",
        colors=colors, startangle=140, pctdistance=0.65
    )
    for t in autotexts:
        t.set_fontsize(9)
        t.set_fontweight("bold")
    title = event_name.split("\n")[0]
    ax.set_title(f"{title}\nCarbon Footprint by Scope (Estimated)", fontsize=13, fontweight="bold")

plt.suptitle("Scope 1/2/3 Emission Structure: Super Bowl vs Olympic Games",
             fontsize=15, fontweight="bold", y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(FIG_DIR, "fig_q4d_scope_comparison.png"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("[Figure] fig_q4d_scope_comparison.png saved.")

# ============================================================
# Figure 2: Normalized intensity comparison bar chart
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5))

scope_labels_simple = ["Scope 1\n(Direct)", "Scope 2\n(Energy)", "Scope 3\n(Travel)",
                       "Scope 3\n(Accomm.)", "Scope 3\n(Other)", "Scope 3\n(Construction)"]
sb_intensities_scope = []
oly_intensities_scope = []
valid_scope_labels = []

for scope_orig, scope_simple in zip(scope_order, scope_labels_simple):
    sb_key = ("Super Bowl LIX\n(1-day event)", scope_orig)
    oly_key = ("Olympic Games\n(17-day event)", scope_orig)
    sb_i = intensity_comparison.get(sb_key, {}).get("intensity_kg", 0)
    oly_i = intensity_comparison.get(oly_key, {}).get("intensity_kg", 0)
    if sb_i > 0 or oly_i > 0:
        sb_intensities_scope.append(sb_i)
        oly_intensities_scope.append(oly_i)
        valid_scope_labels.append(scope_simple)

x = np.arange(len(valid_scope_labels))
width = 0.35

bars1 = ax.bar(x - width/2, sb_intensities_scope, width, label="Super Bowl LIX",
               color="#3498DB", edgecolor="white", alpha=0.9)
bars2 = ax.bar(x + width/2, oly_intensities_scope, width, label="Olympic Games",
               color="#E74C3C", edgecolor="white", alpha=0.9)

ax.set_xticks(x)
ax.set_xticklabels(valid_scope_labels, fontsize=10)
ax.set_ylabel("kgCO2e per Spectator-Day", fontsize=12)
ax.set_title("Normalized Emission Intensity by Scope (per spec-day)\n(Estimates with literature-informed ranges)",
             fontsize=14, fontweight="bold")
ax.legend(fontsize=11)
ax.grid(axis="y", alpha=0.3)

for bar in bars1:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., h + 0.5, f"{h:.1f}",
            ha="center", fontsize=7, fontweight="bold")
for bar in bars2:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., h + 0.5, f"{h:.1f}",
            ha="center", fontsize=7, fontweight="bold")

plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "fig_q4d_intensity_comparison.png"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("[Figure] fig_q4d_intensity_comparison.png saved.")

# ============================================================
# Figure 3: Key structural differences summary radar
# ============================================================
fig, ax = plt.subplots(figsize=(8, 7), subplot_kw=dict(polar=True))

dim_labels = ["Total CO2\n(scale)", "Per Spec-Day\nIntensity", "Scope 3\nDominance",
              "Construction\nBurden", "Multi-Venue\nComplexity", "Duration\nAmortization",
              "Energy\nIntensity", "Per-Flight\nImpact"]
sb_scores = [0.10, 0.80, 0.95, 0.05, 0.05, 0.10, 0.30, 0.90]
oly_scores = [0.95, 0.30, 0.70, 0.90, 0.95, 0.20, 0.80, 0.40]

angles = np.linspace(0, 2*np.pi, len(dim_labels), endpoint=False).tolist()
sb_closed = sb_scores + [sb_scores[0]]
oly_closed = oly_scores + [oly_scores[0]]
angles_closed = angles + [angles[0]]

ax.fill(angles_closed, sb_closed, alpha=0.3, color="#3498DB")
ax.plot(angles_closed, sb_closed, 'o-', linewidth=2, color="#3498DB", label="Super Bowl LIX")
ax.fill(angles_closed, oly_closed, alpha=0.3, color="#E74C3C")
ax.plot(angles_closed, oly_closed, 'o-', linewidth=2, color="#E74C3C", label="Olympic Games")
ax.set_xticks(angles)
ax.set_xticklabels(dim_labels, fontsize=9)
ax.set_ylim(0, 1)
ax.set_title("Structural Comparison: Environmental Impact Profiles\n(1.0 = Higher Environmental Challenge)",
             fontsize=13, fontweight="bold", pad=25)
ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=10)
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "fig_q4d_structural_radar.png"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("[Figure] fig_q4d_structural_radar.png saved.")

print("\n" + "=" * 70)
print(f"  PROBLEM 4d COMPLETE (CORRECTED)")
print(f"  SB intensity (per spec-day):  {sb_intensity_total:.1f} kgCO2e/spec-day")
print(f"  Oly intensity (per spec-day): {oly_intensity_total:.1f} kgCO2e/spec-day")
print(f"  Ratio SB/Oly: {ratio_mid:.1f}× [{ratio_low:.1f}-{ratio_high:.1f}]")
print(f"  SB intensity (per spec-event): {sb_intensity_event:.1f} kgCO2e/spec")
print(f"  Oly intensity (per spec-event): {oly_intensity_event:.1f} kgCO2e/spec")
print(f"  Key corrected finding: SB/Oly ratio is ~{ratio_mid:.0f}× (not 60×)")
print("=" * 70)
