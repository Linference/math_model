#!/usr/bin/env python3
"""
solve_q2.py — 2024 CUMCM Problem A, Question 2
=============================================
Determine the termination time when benches first collide during spiral-in.

Algorithm:
  1. Reuse Q1 kinematics framework (arc length → head theta → handle chain)
  2. SAT (Separating Axis Theorem) rectangle collision for non-adjacent bench pairs
  3. Time bisection: search for earliest collision time t_end
     - Inner loop: coarse scan to bracket collision
     - Outer loop: bisection to refine to tol = 0.01 s

Parameters:
  - Same as Q1: p = 0.55 m, v_head = 1 m/s, theta0 = 32*pi
  - Bench width = 0.3 m for collision rectangles

Output:
  - data/result2.xlsx (single snapshot at collision time)
  - figures/fig_q2_collision_snapshot.png
  - figures/fig_q2_min_distance_curve.png
  - Console: t_end and key handle data
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
    compute_handle_chain,
    compute_all_positions,
    spiral_position,
    get_L_array,
    write_result2_xlsx,
    print_key_results,
    bench_rectangle,
    sat_collision_polygons,
    has_collision,
    N_HANDLES,
    N_BENCHES,
    KEY_HANDLE_INDICES,
    KEY_HANDLE_NAMES,
)

style_path = os.path.join(os.path.dirname(__file__), 'figures.mplstyle')
if os.path.exists(style_path):
    plt.style.use(style_path)


def check_collision_and_get_info(positions):
    """
    Check all non-adjacent bench pairs for collision.
    Returns: (has_collision_bool, collision_pairs_list, min_distance)
    """
    collisions = []
    min_d = np.inf
    for i in range(N_BENCHES):
        rect_i = bench_rectangle(positions[i], positions[i + 1])
        for j in range(i + 2, N_BENCHES):
            rect_j = bench_rectangle(positions[j], positions[j + 1])
            # Compute min distance between rectangle centers (rough approximation)
            center_i = (positions[i] + positions[i + 1]) / 2
            center_j = (positions[j] + positions[j + 1]) / 2
            d_centers = np.linalg.norm(center_i - center_j)
            if d_centers < min_d:
                min_d = d_centers
            if sat_collision_polygons(rect_i, rect_j):
                collisions.append((i, j))
    return len(collisions) > 0, collisions, min_d


def main():
    # Parameters
    p = 0.55
    v_head = 1.0
    theta0 = 32.0 * np.pi
    b = b_from_p(p)
    L_arr = get_L_array()

    print("=" * 60)
    print("Question 2: Collision Termination Time")
    print("=" * 60)

    # Step 1: Coarse scan to find collision bracket
    # Max possible time: when head reaches center (s_max = arc from 0 to theta0)
    s_max = (b / 2.0) * (theta0 * np.sqrt(theta0**2 + 1) + np.arcsinh(theta0))
    t_max = s_max / v_head  # theoretical limit
    print(f"\n  Theoretical max time (head to center): {t_max:.2f} s")
    print(f"  Arc length to center: {s_max:.2f} m")

    # Coarse scan: every 10 seconds
    print("\n[1/3] Coarse scan for collision bracket (every 10s)...")
    t_safe = 0.0
    t_collision = None

    repositions_data = []  # (t, has_coll, min_dist, positions)
    for t in range(0, int(min(t_max, 500.0)), 10):
        s = v_head * t
        theta_head = find_head_theta(theta0, s, b)
        pos, _ = compute_all_positions(theta_head, b, L_arr)
        has_c, coll_pairs, min_d = check_collision_and_get_info(pos)
        repositions_data.append((t, has_c, min_d, pos.copy()))

        if has_c:
            print(f"  t={t:5d}s: COLLISION detected ({len(coll_pairs)} pair(s)), min_center_dist={min_d:.4f} m")
            if t_collision is None:
                t_collision = t
        else:
            print(f"  t={t:5d}s: no collision, min_center_dist={min_d:.4f} m")
            t_safe = t

    if t_collision is None:
        print("  WARNING: No collision detected in scanned range!")
        t_collision = int(min(t_max, 500.0))

    # Fine bisection between last safe and first collision time
    print(f"\n[2/3] Bisection refinement: safe={t_safe}s, collision={t_collision}s...")
    t_low = t_safe
    t_high = t_collision

    for iteration in range(60):
        t_mid = (t_low + t_high) / 2.0
        s_mid = v_head * t_mid
        theta_head = find_head_theta(theta0, s_mid, b)
        pos_mid, _ = compute_all_positions(theta_head, b, L_arr)
        has_c, coll_pairs, min_d = check_collision_and_get_info(pos_mid)

        if has_c:
            t_high = t_mid
        else:
            t_low = t_mid

        if t_high - t_low < 0.001:
            break

        if iteration % 10 == 0:
            print(f"    iter {iteration}: [{t_low:.4f}, {t_high:.4f}], width={t_high-t_low:.4f}s")

    t_end = (t_low + t_high) / 2.0
    print(f"\n  *** Termination time t_end = {t_end:.6f} s ***")

    # Compute final state at t_end
    s_end = v_head * t_end
    theta_end = find_head_theta(theta0, s_end, b)
    pos_end, thetas_end = compute_all_positions(theta_end, b, L_arr)
    r_head_end = b * theta_end
    print(f"  Head radius at termination: {r_head_end:.4f} m")
    print(f"  Head theta at termination: {theta_end:.4f} rad = {theta_end/(2*np.pi):.2f} turns")

    # Check which pairs collide at t_end
    has_c, coll_pairs, min_d = check_collision_and_get_info(pos_end)
    print(f"  Collision pairs at t_end: {len(coll_pairs)}")
    for i, j in coll_pairs[:5]:
        print(f"    Bench {i} (handles {i}-{i+1}) vs Bench {j} (handles {j}-{j+1})")
        print(f"      Handle {i}: ({pos_end[i,0]:.4f}, {pos_end[i,1]:.4f})")
        print(f"      Handle {i+1}: ({pos_end[i+1,0]:.4f}, {pos_end[i+1,1]:.4f})")
        print(f"      Handle {j}: ({pos_end[j,0]:.4f}, {pos_end[j,1]:.4f})")
        print(f"      Handle {j+1}: ({pos_end[j+1,0]:.4f}, {pos_end[j+1,1]:.4f})")

    # Verify: t_end - delta should be safe
    t_check = max(0, t_end - 0.01)
    s_check = v_head * t_check
    th_check = find_head_theta(theta0, s_check, b)
    pos_check, _ = compute_all_positions(th_check, b, L_arr)
    has_c_check, _, _ = check_collision_and_get_info(pos_check)
    print(f"  At t = {t_check:.4f}s (t_end - 0.01): collision = {has_c_check}")

    # Compute speeds at t_end using adjacent time snapshots
    print("\n[3/3] Computing speeds and writing output...")
    dt = 0.01
    s_before = v_head * max(0, t_end - dt)
    theta_before = find_head_theta(theta0, s_before, b)
    pos_before, _ = compute_all_positions(theta_before, b, L_arr)

    s_after = v_head * (t_end + dt)
    theta_after = find_head_theta(theta0, s_after, b)
    pos_after, _ = compute_all_positions(theta_after, b, L_arr)

    speeds = np.sqrt(np.sum((pos_after - pos_before)**2, axis=1)) / (2 * dt)

    # Write result2.xlsx
    output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'result2.xlsx')
    write_result2_xlsx(output_path, pos_end, speeds)

    # Print key results
    print("\n" + "=" * 60)
    print(f"KEY RESULTS at t = {t_end:.6f} s")
    print("=" * 60)
    KEY_TIME = [t_end]
    # Create a small wrapper for print_key_results
    handles_for_print = [
        "龙头前把手",
        "第1节龙身前把手",
        "第51节龙身前把手",
        "第101节龙身前把手",
        "第151节龙身前把手",
        "第201节龙身前把手",
        "龙尾后把手",
    ]
    KEYS = [0, 1, 51, 101, 151, 201, 223]
    print(f"  {'Handle':<24s} {'x (m)':<16s} {'y (m)':<16s} {'v (m/s)':<12s}")
    print(f"  {'-'*24} {'-'*16} {'-'*16} {'-'*12}")
    for idx, name in zip(KEYS, handles_for_print):
        print(f"  {name:<24s} {pos_end[idx,0]:>15.6f}  {pos_end[idx,1]:>15.6f}  {speeds[idx]:>11.6f}")

    # --- Figures ---
    figures_dir = os.path.join(os.path.dirname(__file__), '..', 'figures')

    # Figure 1: Collision snapshot
    fig, ax = plt.subplots(figsize=(8, 8))
    # Plot spiral background
    theta_range = np.linspace(theta_end - 20, pos_end[-1, :].max() * 1.1, 3000)
    # Actually use theta range based on data
    th_min_plot = thetas_end.min() - 2
    th_max_plot = thetas_end.max() + 5
    theta_plot = np.linspace(th_min_plot, th_max_plot, 3000)
    x_sp = b * theta_plot * np.cos(theta_plot)
    y_sp = b * theta_plot * np.sin(theta_plot)
    ax.plot(x_sp, y_sp, 'gray', alpha=0.2, linewidth=0.5)

    # Plot all handle points
    ax.plot(pos_end[:, 0], pos_end[:, 1], 'b.-', markersize=2, linewidth=0.6)

    # Highlight key handles
    for ki in KEYS:
        ax.plot(pos_end[ki, 0], pos_end[ki, 1], 'go', markersize=6, zorder=5)
    ax.plot(pos_end[0, 0], pos_end[0, 1], 'r*', markersize=14, zorder=6, label='Head')

    # Highlight collision benches
    for i, j in coll_pairs[:3]:
        ax.plot([pos_end[i, 0], pos_end[i+1, 0]], [pos_end[i, 1], pos_end[i+1, 1]],
                'r-', linewidth=2.5, alpha=0.7)
        ax.plot([pos_end[j, 0], pos_end[j+1, 0]], [pos_end[j, 1], pos_end[j+1, 1]],
                'r-', linewidth=2.5, alpha=0.7)
        # Draw bench rectangles
        rect_i = bench_rectangle(pos_end[i], pos_end[i+1])
        rect_j = bench_rectangle(pos_end[j], pos_end[j+1])
        rect_i_closed = np.vstack([rect_i, rect_i[0]])
        rect_j_closed = np.vstack([rect_j, rect_j[0]])
        ax.plot(rect_i_closed[:, 0], rect_i_closed[:, 1], 'r-', linewidth=1.5)
        ax.plot(rect_j_closed[:, 0], rect_j_closed[:, 1], 'r-', linewidth=1.5)

    ax.plot(0, 0, 'k+', markersize=12, label='Center')
    # Draw 4.5m radius circle for context
    theta_circle = np.linspace(0, 2*np.pi, 200)
    ax.plot(4.5 * np.cos(theta_circle), 4.5 * np.sin(theta_circle),
            'k--', linewidth=0.8, alpha=0.5, label='r=4.5m')
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.set_title(f'Collision Configuration at t = {t_end:.2f} s (Q2)')
    ax.set_aspect('equal')
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'fig_q2_collision_snapshot.png'), dpi=300)
    plt.close(fig)
    print(f"  Saved fig_q2_collision_snapshot.png")

    # Figure 2: Min distance vs time
    ts = [d[0] for d in repositions_data]
    min_ds = [d[2] for d in repositions_data]
    has_cs = [d[1] for d in repositions_data]

    fig, ax = plt.subplots(figsize=(8, 4))
    safe_ts = [ts[i] for i in range(len(ts)) if not has_cs[i]]
    safe_ds = [min_ds[i] for i in range(len(ts)) if not has_cs[i]]
    coll_ts = [ts[i] for i in range(len(ts)) if has_cs[i]]
    coll_ds = [min_ds[i] for i in range(len(ts)) if has_cs[i]]

    ax.plot(safe_ts, safe_ds, 'go-', label='No collision', markersize=5)
    if coll_ts:
        ax.plot(coll_ts, coll_ds, 'ro-', label='Collision', markersize=5)
    ax.axvline(x=t_end, color='red', linestyle='--', alpha=0.7, label=f't_end = {t_end:.2f} s')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Min Center Distance (m)')
    ax.set_title('Minimum Bench Center Distance vs Time (Q2)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'fig_q2_min_distance_curve.png'), dpi=300)
    plt.close(fig)
    print(f"  Saved fig_q2_min_distance_curve.png")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Collision time: t_end = {t_end:.4f} s")
    print(f"  Head radius at collision: {r_head_end:.4f} m")
    print(f"  Number of collision pairs: {len(coll_pairs)}")
    print(f"  Collision detection method: SAT (Separating Axis Theorem)")
    print(f"  Bench rectangle width: 0.30 m")


if __name__ == '__main__':
    main()
