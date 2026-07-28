#!/usr/bin/env python3
"""
solve_q1.py — 2024 CUMCM Problem A, Question 1
=============================================
Kinematic forward solution for 0–300s clockwise spiral-in.

Algorithm:
  1. Arc length: s_head = v_head * t
  2. Head theta: bisection on arc_length(theta_head, theta0) = v_head * t
  3. Handle chain: recursive bisection for each subsequent handle position
  4. Speed: central differencing of positions across time steps

Parameters:
  - Spiral pitch p = 0.55 m,  b = p/(2*pi)
  - Initial head angle theta0 = 32*pi (16th circle, Point A)
  - Head speed v_head = 1 m/s (constant)
  - Time range: t = 0, 1, ..., 300 s

Output:
  - data/result1.xlsx (position sheet + speed sheet, matching template)
  - figures/fig_q1_spiral_overview.png
  - figures/fig_q1_velocity_distribution.png
  - Console: key handle data at t = 0, 60, 120, 180, 240, 300 s
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Add code directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
from utils import (
    b_from_p,
    find_head_theta,
    compute_handle_chain,
    spiral_position,
    get_L_array,
    write_result1_xlsx,
    print_key_results,
    N_HANDLES,
    N_BENCHES,
    KEY_HANDLE_INDICES,
    KEY_HANDLE_NAMES,
    KEY_TIME_STEPS_Q1,
)

# Use mplstyle if available
style_path = os.path.join(os.path.dirname(__file__), 'figures.mplstyle')
if os.path.exists(style_path):
    plt.style.use(style_path)


def main():
    # Parameters
    p = 0.55  # m, spiral pitch
    v_head = 1.0  # m/s
    theta0 = 32.0 * np.pi  # initial head angle (16th circle)
    b = b_from_p(p)
    L_arr = get_L_array()

    print("=" * 60)
    print("Question 1: Kinematic Forward Solution (0–300 s)")
    print("=" * 60)
    print(f"  Pitch p = {p} m")
    print(f"  Spiral parameter b = p/(2*pi) = {b:.6f}")
    print(f"  Head speed v_head = {v_head} m/s")
    print(f"  Initial theta0 = {theta0:.6f} rad = {theta0/(2*np.pi):.1f} circles")
    print(f"  Initial radius r0 = {b * theta0:.4f} m")

    # Time points
    times = np.arange(0, 301, 1)  # 0, 1, ..., 300 s
    n_times = len(times)  # 301
    print(f"  Time steps: {n_times} ({times[0]} to {times[-1]} s)")

    # Pre-compute all theta chains
    print("\n[1/3] Computing handle chains for all time steps...")
    all_positions = np.zeros((n_times, N_HANDLES, 2))
    all_thetas = np.zeros((n_times, N_HANDLES))

    for ti, t in enumerate(times):
        s_traveled = v_head * t
        theta_head = find_head_theta(theta0, s_traveled, b)
        thetas = compute_handle_chain(theta_head, b, L_arr)
        all_thetas[ti] = thetas
        all_positions[ti] = spiral_position(thetas, b)
        if ti % 60 == 0:
            r_head = b * theta_head
            print(f"  t={t:4d}s: theta_head={theta_head:.4f} rad, r_head={r_head:.4f} m")

    # Verify: check first/last chain distances
    print("\n[Verification] Checking handle-to-handle distances...")
    max_err = 0.0
    for ti in [0, n_times - 1]:
        for i in range(N_BENCHES):
            d = np.linalg.norm(all_positions[ti, i + 1] - all_positions[ti, i])
            err = abs(d - L_arr[i])
            max_err = max(max_err, err)
    print(f"  Max distance error: {max_err:.2e} m (should be < 1e-10)")

    # Compute speeds using central differences
    print("\n[2/3] Computing speeds (central differences)...")
    all_speeds = np.zeros((n_times, N_HANDLES))
    for ti in range(n_times):
        if ti == 0:
            dt = times[1] - times[0]
            diff = all_positions[ti + 1] - all_positions[ti]
            all_speeds[ti] = np.sqrt(np.sum(diff**2, axis=1)) / dt
        elif ti == n_times - 1:
            dt = times[-1] - times[-2]
            diff = all_positions[ti] - all_positions[ti - 1]
            all_speeds[ti] = np.sqrt(np.sum(diff**2, axis=1)) / dt
        else:
            dt = times[ti + 1] - times[ti - 1]  # 2 s
            diff = all_positions[ti + 1] - all_positions[ti - 1]
            all_speeds[ti] = np.sqrt(np.sum(diff**2, axis=1)) / dt

    # Verify head speed
    print(f"  Head speed at t=150s: {all_speeds[150, 0]:.6f} m/s (should ~ 1.0 m/s)")

    # Write result1.xlsx
    print("\n[3/3] Writing data/result1.xlsx...")
    output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'result1.xlsx')
    write_result1_xlsx(output_path, times.tolist(), all_positions, all_speeds)

    # Print key results for paper
    print("\n" + "=" * 60)
    print("KEY RESULTS (for paper table)")
    print("=" * 60)
    print_key_results(KEY_TIME_STEPS_Q1, all_positions, all_speeds, times)

    # --- Figures ---
    print("\nGenerating figures...")
    figures_dir = os.path.join(os.path.dirname(__file__), '..', 'figures')

    # Figure 1: Spiral overview at t=0 and t=300
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax_idx, ti in enumerate([0, n_times - 1]):
        ax = axes[ax_idx]
        t = times[ti]
        # Plot full spiral for context
        theta_plot = np.linspace(all_thetas[ti, 0], all_thetas[ti, -1] + 2, 2000)
        x_spiral = b * theta_plot * np.cos(theta_plot)
        y_spiral = b * theta_plot * np.sin(theta_plot)
        ax.plot(x_spiral, y_spiral, 'gray', alpha=0.3, linewidth=0.5)

        # Plot all handles
        ax.plot(all_positions[ti, :, 0], all_positions[ti, :, 1],
                'b.-', markersize=2, linewidth=0.8, label='Handles')
        # Highlight key handles
        for ki in KEY_HANDLE_INDICES:
            ax.plot(all_positions[ti, ki, 0], all_positions[ti, ki, 1],
                    'ro', markersize=5, zorder=5)
        ax.plot(all_positions[ti, 0, 0], all_positions[ti, 0, 1],
                'r*', markersize=12, zorder=6, label='Head')
        # Mark origin
        ax.plot(0, 0, 'k+', markersize=10)
        ax.set_xlabel('x (m)')
        ax.set_ylabel('y (m)')
        ax.set_title(f't = {t} s')
        ax.set_aspect('equal')
        ax.legend(fontsize=8)
    fig.suptitle('Bench Dragon Spiral Configuration (Q1)', fontsize=13)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'fig_q1_spiral_overview.png'), dpi=300)
    plt.close(fig)
    print(f"  Saved fig_q1_spiral_overview.png")

    # Figure 2: Velocity distribution along dragon body
    fig, ax = plt.subplots(figsize=(8, 5))
    handle_idx = np.arange(N_HANDLES)
    colors = plt.cm.viridis(np.linspace(0, 1, len(KEY_TIME_STEPS_Q1)))
    for ci, t_target in enumerate(KEY_TIME_STEPS_Q1):
        ti = np.argmin(np.abs(times - t_target))
        ax.plot(handle_idx, all_speeds[ti], '-', color=colors[ci],
                label=f't = {t_target} s', linewidth=1.5, alpha=0.85)
    ax.set_xlabel('Handle Index')
    ax.set_ylabel('Speed (m/s)')
    ax.set_title('Handle Speed Distribution Along Dragon Body (Q1)')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'fig_q1_velocity_distribution.png'), dpi=300)
    plt.close(fig)
    print(f"  Saved fig_q1_velocity_distribution.png")

    # Figure 3: Head and tail speed vs time
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(times, all_speeds[:, 0], 'b-', label='Head (handle 0)', linewidth=1.5)
    ax.plot(times, all_speeds[:, 50], 'g-', label='Handle 50', linewidth=1.2)
    ax.plot(times, all_speeds[:, 100], 'orange', linestyle='-', label='Handle 100', linewidth=1.2)
    ax.plot(times, all_speeds[:, 150], 'r-', label='Handle 150', linewidth=1.2)
    ax.plot(times, all_speeds[:, 200], 'purple', linestyle='-', label='Handle 200', linewidth=1.2)
    ax.plot(times, all_speeds[:, -1], 'brown', linestyle='-', label='Tail (handle 223)', linewidth=1.5)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Speed (m/s)')
    ax.set_title('Handle Speed vs Time (Q1)')
    ax.legend(fontsize=8, ncol=3)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'fig_q1_head_tail_trajectory.png'), dpi=300)
    plt.close(fig)
    print(f"  Saved fig_q1_head_tail_trajectory.png")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total time steps computed: {n_times}")
    print(f"  Handles per step: {N_HANDLES}")
    print(f"  Head radius at t=0: {b * theta0:.4f} m")
    print(f"  Head radius at t=300: {b * all_thetas[-1, 0]:.4f} m")
    print(f"  Tail radius at t=0: {b * theta0:.4f} m")
    print(f"  Tail radius at t=300: {b * all_thetas[-1, -1]:.4f} m")
    print(f"  Head speed range: [{all_speeds[:, 0].min():.4f}, {all_speeds[:, 0].max():.4f}] m/s")
    print(f"  Max any-handle speed: {all_speeds.max():.4f} m/s")


if __name__ == '__main__':
    main()
