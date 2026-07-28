#!/usr/bin/env python3
"""
solve_q3.py — 2024 CUMCM Problem A, Question 3
=============================================
Determine the minimum spiral pitch p_min such that the dragon head can
spiral in from the 16th circle to reach the boundary of the turning space
(r = 4.5 m) without bench collisions.

Algorithm:
  1. Geometric constraint: r0 = 16*p > 4.5, so p > 0.28125 m
  2. Bisection search over p in [0.282, 2.0] m
  3. For each candidate p, simulate from initial to r=4.5m with collision checks
  4. Coarse time steps (every 15s) with refinement near boundary

Optimizations:
  - Spatial pre-filtering in collision detection (only check bench pairs
    within index window 5-40, with center-distance quick rejection)
  - Coarse time stepping for simulation

Output:
  - figures/fig_q3_pitch_vs_margin.png
  - figures/fig_q3_critical_config.png
  - Console: p_min with verification
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
from utils import (
    b_from_p,
    find_head_theta,
    compute_all_positions,
    spiral_arc_length,
    get_L_array,
    has_collision,
    N_HANDLES,
    N_BENCHES,
    BOARD_WIDTH,
)

style_path = os.path.join(os.path.dirname(__file__), 'figures.mplstyle')
if os.path.exists(style_path):
    plt.style.use(style_path)

R_TURN = 4.5  # m, turning space radius


def simulate_until_boundary_or_collision(p, theta0=32.0*np.pi, v_head=1.0):
    """
    Simulate spiral-in from theta0 until head reaches r=R_TURN or collision.

    Returns: (reached_boundary: bool, collision_time: float, boundary_time: float)
    """
    b = b_from_p(p)
    r0 = b * theta0
    L_arr = get_L_array()

    if r0 <= R_TURN:
        return False, 0.0, 0.0

    # Theta at boundary
    theta_boundary = R_TURN / b

    # Arc length and time to boundary
    s_to_bnd = spiral_arc_length(theta_boundary, theta0, b)
    t_boundary = s_to_bnd / v_head

    # Simulate with coarse steps, refine near boundary
    dt = 15.0  # coarse step
    t = 0.0
    while t <= t_boundary:
        s = v_head * t
        theta_head = find_head_theta(theta0, s, b)
        pos, _ = compute_all_positions(theta_head, b, L_arr)

        if has_collision(pos):
            return False, t, t_boundary

        # Near boundary: finer steps
        remaining = t_boundary - t
        if remaining < 30.0:
            dt = 3.0
        elif remaining < 60.0:
            dt = 7.0

        if t + dt > t_boundary and remaining > 1.0:
            # Ensure we check close to the boundary
            t = t_boundary - 1.0
            dt = 1.0
        elif t >= t_boundary:
            break

        t += dt

    # Final check at boundary
    s = v_head * t_boundary
    theta_head = find_head_theta(theta0, s, b)
    pos, _ = compute_all_positions(theta_head, b, L_arr)
    if has_collision(pos):
        return False, t_boundary, t_boundary

    return True, np.inf, t_boundary


def main():
    v_head = 1.0
    theta0 = 32.0 * np.pi

    print("=" * 60)
    print("Question 3: Minimum Spiral Pitch for r = 4.5 m Reachability")
    print("=" * 60)
    print(f"  Turning space radius: R = {R_TURN} m")
    print(f"  Theoretical p_min = R/16 = {R_TURN/16:.4f} m")
    print(f"  Search range: [0.282, 2.0] m")

    # Verify p=2.0 is feasible
    print(f"\n[Check] p = 2.00 m...")
    ok2, ct2, bt2 = simulate_until_boundary_or_collision(2.0, theta0, v_head)
    print(f"  Feasible: {ok2}, boundary_time: {bt2:.1f}s")

    # Verify p=0.282 is infeasible (head starts at r=4.512m, barely outside)
    print(f"[Check] p = 0.282 m...")
    ok1, ct1, bt1 = simulate_until_boundary_or_collision(0.282, theta0, v_head)
    print(f"  Feasible: {ok1}")

    # Bisection
    p_low = 0.282
    p_high = 2.0

    # First determine feasible range
    if not ok2:
        print("ERROR: p=2.0 not feasible!")
        return

    # Binary search for minimum feasible pitch
    print(f"\n[Bisection] Searching for p_min...")
    for iteration in range(40):
        p_mid = (p_low + p_high) / 2.0
        ok_mid, ct_mid, bt_mid = simulate_until_boundary_or_collision(p_mid, theta0, v_head)
        status = "OK" if ok_mid else f"COLLISION at {ct_mid:.1f}s"
        print(f"  iter {iteration:2d}: p={p_mid:.6f}, {status}, boundary={bt_mid:.1f}s, width={p_high-p_low:.6f}")

        if ok_mid:
            p_high = p_mid
        else:
            p_low = p_mid

        if p_high - p_low < 0.0001:
            break

    p_min = p_high
    print(f"\n  *** Minimum pitch p_min = {p_min:.6f} m ***")
    print(f"  r0 = {16 * p_min:.4f} m")
    print(f"  Safety margin: {16 * p_min - R_TURN:.4f} m above boundary")

    # Detailed verification at p_min
    print(f"\n[Verification] Detailed simulation at p_min...")
    b_min = b_from_p(p_min)
    theta_boundary = R_TURN / b_min
    s_to_bnd = spiral_arc_length(theta_boundary, theta0, b_min)
    t_bnd = s_to_bnd / v_head
    print(f"  Travel time to boundary: {t_bnd:.2f} s")
    print(f"  Arc length to boundary: {s_to_bnd:.2f} m")
    print(f"  Head theta at boundary: {theta_boundary:.4f} rad = {theta_boundary/(2*np.pi):.2f} turns")

    # Verify with finer checks
    L_arr = get_L_array()
    dt_fine = 2.0
    t = 0.0
    while t <= t_bnd:
        s = v_head * t
        theta_head = find_head_theta(theta0, s, b_min)
        pos, _ = compute_all_positions(theta_head, b_min, L_arr)
        if has_collision(pos):
            print(f"  COLLISION at t={t:.2f}s (during fine check)!")
            break
        t += dt_fine
    else:
        print(f"  Fine check passed: no collision at dt={dt_fine}s")

    # Compute boundary snapshot
    theta_head_bnd = find_head_theta(theta0, t_bnd * v_head, b_min)
    pos_bnd, thetas_bnd = compute_all_positions(theta_head_bnd, b_min, L_arr)

    # Speeds
    dt_spd = 0.2
    s_before = v_head * max(0, t_bnd - dt_spd)
    th_before = find_head_theta(theta0, s_before, b_min)
    pos_before, _ = compute_all_positions(th_before, b_min, L_arr)
    s_after = v_head * (t_bnd + dt_spd)
    th_after = find_head_theta(theta0, s_after, b_min)
    pos_after, _ = compute_all_positions(th_after, b_min, L_arr)
    speeds_bnd = np.sqrt(np.sum((pos_after - pos_before)**2, axis=1)) / (2 * dt_spd)

    # Print key data
    print(f"\n  KEY HANDLES at r = {R_TURN} m (p_min = {p_min:.4f} m):")
    print(f"  {'Handle':<24s} {'x (m)':<16s} {'y (m)':<16s} {'v (m/s)':<12s}")
    print(f"  {'-'*24} {'-'*16} {'-'*16} {'-'*12}")
    KEYS = [0, 1, 51, 101, 151, 201, 223]
    NAMES = [
        "龙头前把手", "第1节龙身前把手", "第51节龙身前把手",
        "第101节龙身前把手", "第151节龙身前把手", "第201节龙身前把手",
        "龙尾后把手",
    ]
    for idx, name in zip(KEYS, NAMES):
        print(f"  {name:<24s} {pos_bnd[idx,0]:>15.6f}  {pos_bnd[idx,1]:>15.6f}  {speeds_bnd[idx]:>11.6f}")

    # --- Figures ---
    figures_dir = os.path.join(os.path.dirname(__file__), '..', 'figures')

    # Figure 1: Pitch scan
    p_scan = np.linspace(max(0.282, p_min - 0.1), p_min + 0.5, 20)
    results = []
    print(f"\n[Figure] Scanning {len(p_scan)} pitch values for margin plot...")
    for p_test in p_scan:
        b_test = b_from_p(p_test)
        r0_test = b_test * theta0
        if r0_test <= R_TURN:
            results.append((p_test, False, r0_test - R_TURN))
            continue
        ok, ct, bt = simulate_until_boundary_or_collision(p_test, theta0, v_head)
        results.append((p_test, ok, ct if not ok else 0))

    fig, ax = plt.subplots(figsize=(8, 4))
    p_vals = [r[0] for r in results]
    colors = ['g' if r[1] else 'r' for r in results]
    sizes = [80 if r[1] else 120 for r in results]
    ax.scatter(p_vals, [0]*len(p_vals), c=colors, s=sizes, zorder=5)
    ax.axvline(x=p_min, color='blue', linestyle='--', linewidth=2,
               label=f'p_min = {p_min:.4f} m')
    ax.axvline(x=R_TURN/16, color='gray', linestyle=':', alpha=0.5,
               label=f'Geometric limit = {R_TURN/16:.4f} m')
    ax.set_xlabel('Pitch p (m)')
    ax.set_yticks([])
    ax.set_title('Pitch Feasibility: Green=feasible, Red=infeasible (Q3)')
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'fig_q3_pitch_vs_margin.png'), dpi=300)
    plt.close(fig)
    print(f"  Saved fig_q3_pitch_vs_margin.png")

    # Figure 2: Critical configuration
    fig, ax = plt.subplots(figsize=(8, 8))
    th_plot = np.linspace(thetas_bnd[0] - 5, thetas_bnd[-1] + 5, 3000)
    x_sp = b_min * th_plot * np.cos(th_plot)
    y_sp = b_min * th_plot * np.sin(th_plot)
    ax.plot(x_sp, y_sp, 'gray', alpha=0.2, linewidth=0.5)
    ax.plot(pos_bnd[:, 0], pos_bnd[:, 1], 'b.-', markersize=2, linewidth=0.6)
    for ki in KEYS:
        ax.plot(pos_bnd[ki, 0], pos_bnd[ki, 1], 'go', markersize=6, zorder=5)
    ax.plot(pos_bnd[0, 0], pos_bnd[0, 1], 'r*', markersize=14, zorder=6, label='Head')
    theta_c = np.linspace(0, 2*np.pi, 200)
    ax.plot(R_TURN * np.cos(theta_c), R_TURN * np.sin(theta_c), 'k--',
            linewidth=1.2, label=f'r = {R_TURN} m')
    ax.plot(0, 0, 'k+', markersize=12, label='Center')
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.set_title(f'Critical Config at p_min = {p_min:.4f} m, Head at r = {R_TURN} m (Q3)')
    ax.set_aspect('equal')
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'fig_q3_critical_config.png'), dpi=300)
    plt.close(fig)
    print(f"  Saved fig_q3_critical_config.png")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Minimum pitch p_min = {p_min:.6f} m")
    print(f"  Initial radius r0 = {16 * p_min:.4f} m")
    print(f"  Distance head must travel inward: {16*p_min - R_TURN:.4f} m")
    print(f"  Time to reach boundary: {t_bnd:.2f} s")


if __name__ == '__main__':
    main()
