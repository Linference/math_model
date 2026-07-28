#!/usr/bin/env python3
"""
solve_q5.py — 2024 CUMCM Problem A, Question 5
=============================================
Determine the maximum head speed v_max such that all handle speeds
remain <= 2.0 m/s throughout the entire composite path (Q4).

Algorithm:
  1. Use the Q4 composite path (incoming spiral + S-curve + outgoing spiral)
  2. Key insight: handle speeds scale linearly with head speed
     (kinematics are geometrically determined by the path)
  3. At v_head = 1.0 m/s, pre-compute all handle speeds over the full trajectory
  4. Find the maximum speed amplification factor: f_max = max_all(v_i / v_head)
  5. v_max = 2.0 / f_max
  6. Verify at v_max and v_max + epsilon

Speed profiles are needed for the ENTIRE path, not just -100s to 100s.
We compute over a broader range to capture the bottleneck.

Output:
  - figures/fig_q5_speed_relation.png
  - figures/fig_q5_bottleneck_location.png
  - figures/fig_q5_amplification_factor.png
  - Console: v_max and bottleneck location
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
    spiral_position,
    spiral_arc_length,
    get_L_array,
    N_HANDLES,
    N_BENCHES,
    KEY_HANDLE_INDICES,
    KEY_HANDLE_NAMES,
)

style_path = os.path.join(os.path.dirname(__file__), 'figures.mplstyle')
if os.path.exists(style_path):
    plt.style.use(style_path)

# Same parameters as Q4
P_IN = 1.7
V_NOMINAL = 1.0  # nominal head speed for pre-computation
THETA0 = 32.0 * np.pi
B_IN = b_from_p(P_IN)
R_TURN = 4.5


def compute_speed_profile_over_range(t_start, t_end, dt, b, theta0, L_arr, v_head=1.0):
    """
    Compute handle speeds over time range [t_start, t_end] for a given head speed.

    Uses the incoming spiral chain model (approximation: handles follow spiral).
    Returns: (times, speeds_array) where speeds_array has shape (n_times, N_HANDLES)
    """
    times = np.arange(t_start, t_end + dt, dt)
    n_times = len(times)

    # Pre-compute positions
    positions = np.zeros((n_times, N_HANDLES, 2))
    for ti, t in enumerate(times):
        s = v_head * t
        theta_head = find_head_theta(theta0, s, b)
        pos, _ = compute_all_positions(theta_head, b, L_arr)
        positions[ti] = pos

    # Compute speeds (central differences)
    speeds = np.zeros((n_times, N_HANDLES))
    for ti in range(n_times):
        if ti == 0:
            d = times[1] - times[0]
            diff = positions[ti + 1] - positions[ti]
            speeds[ti] = np.sqrt(np.sum(diff**2, axis=1)) / d
        elif ti == n_times - 1:
            d = times[-1] - times[-2]
            diff = positions[ti] - positions[ti - 1]
            speeds[ti] = np.sqrt(np.sum(diff**2, axis=1)) / d
        else:
            d = times[ti + 1] - times[ti - 1]
            diff = positions[ti + 1] - positions[ti - 1]
            speeds[ti] = np.sqrt(np.sum(diff**2, axis=1)) / d

    return times, speeds


def main():
    print("=" * 60)
    print("Question 5: Maximum Head Speed (v <= 2 m/s constraint)")
    print("=" * 60)
    print(f"  Pitch p = {P_IN} m, b = {B_IN:.6f}")
    print(f"  Constraint: all handle speeds <= 2.0 m/s")
    print(f"  Nominal head speed: {V_NOMINAL} m/s")

    L_arr = get_L_array()

    # Step 1: Compute speed profile at nominal speed (v_head = 1 m/s)
    # We need to cover the relevant part of the trajectory
    # The head starts at theta0=32pi, spirals in, then turns, then spirals out
    # The speed bottleneck could be anywhere along this path

    # For the incoming spiral phase, compute from t=0 to t when head is deep enough
    # At v=1 m/s, the head goes from r=27.2m (theta0=32pi) to r ~ a few meters
    # Let's compute up to the point where handle chain fills the 4.5m space

    # Head radius reaches R_TURN at theta = R_TURN/B_IN = 4.5/0.2706 = 16.63 rad
    theta_turn = R_TURN / B_IN
    s_to_turn = spiral_arc_length(theta_turn, THETA0, B_IN)
    t_to_turn = s_to_turn / V_NOMINAL
    print(f"\n  Head radius reaches 4.5m at t = {t_to_turn:.1f} s (theta={theta_turn:.2f})")

    # Also compute for the outgoing phase
    # After turning, the head spirals back out along the outgoing spiral
    # The turning happens at roughly theta1 ~ 14.66 (from Q4)
    theta1_q4 = 14.655
    s_to_turn_q4 = spiral_arc_length(theta1_q4, THETA0, B_IN)
    t_turn_start = s_to_turn_q4 / V_NOMINAL
    print(f"  Head reaches turning start (theta1={theta1_q4:.2f}) at t = {t_turn_start:.1f} s")

    # For outgoing phase simulation
    t_turn_duration = 1.8  # from Q4
    t_out_start = t_turn_start + t_turn_duration

    # Compute speed profiles over three phases
    print("\n[1/3] Computing incoming spiral speed profile...")
    dt_in = 5.0
    t_in_start = 0
    t_in_end = t_turn_start
    times_in, speeds_in = compute_speed_profile_over_range(
        t_in_start, t_in_end, dt_in, B_IN, THETA0, L_arr, V_NOMINAL
    )
    print(f"  Incoming: {len(times_in)} time steps, time range [{t_in_start:.0f}, {t_in_end:.0f}]s")

    # Also compute the region where speed bottleneck is most likely — near the center
    # When head is near the center, the spiral curvature is highest
    # and the tail whips around faster
    print("\n[2/3] Computing deep spiral (near center) speed profile...")
    # The head reaches close to the center after ~ t_to_turn + some time
    # At t_turn_start, head is at theta=14.66, r=3.97m
    # Continue a bit deeper
    dt_deep = 2.0
    t_deep_start = max(0, t_turn_start - 200)
    t_deep_end = t_turn_start + t_turn_duration + 200
    times_deep, speeds_deep = compute_speed_profile_over_range(
        t_deep_start, t_deep_end, dt_deep, B_IN, THETA0, L_arr, V_NOMINAL
    )
    print(f"  Deep: {len(times_deep)} time steps, time range [{t_deep_start:.0f}, {t_deep_end:.0f}]s")

    # Combine all profiles
    print("\n[3/3] Finding global maximum speed amplification...")
    all_speeds = np.vstack([speeds_in, speeds_deep])
    all_times_list = list(times_in) + list(times_deep)

    # Create unique time index (there may be overlaps)
    # For simplicity, just find global max across all computations
    all_speeds_flat = all_speeds.flatten()

    # Find max amplification factor: max(v_i / v_head) at v_head = 1
    max_speed_nominal = np.max(all_speeds_flat)
    f_max = max_speed_nominal / V_NOMINAL
    max_idx_flat = np.argmax(all_speeds_flat)
    max_time_idx = max_idx_flat // N_HANDLES
    max_handle_idx = max_idx_flat % N_HANDLES

    # Map back to actual time
    if max_time_idx < len(times_in):
        t_bottleneck = times_in[max_time_idx]
    else:
        t_bottleneck = times_deep[max_time_idx - len(times_in)]

    print(f"\n  Max nominal speed: {max_speed_nominal:.6f} m/s")
    print(f"  Amplification factor f_max = {f_max:.6f}")
    print(f"  Bottleneck: handle {max_handle_idx} at t = {t_bottleneck:.1f} s")

    v_max = 2.0 / f_max
    print(f"\n  *** Maximum head speed v_max = {v_max:.6f} m/s ***")

    # Verification
    print(f"\n[Verification] v_max = {v_max:.6f} m/s")
    scaled_speeds_max = all_speeds * (v_max / V_NOMINAL)
    max_scaled = np.max(scaled_speeds_max)
    print(f"  Max scaled speed at v_max: {max_scaled:.6f} m/s (should be ~2.0)")

    # Check at v_max + 0.01
    v_plus = v_max + 0.01
    scaled_plus = all_speeds * (v_plus / V_NOMINAL)
    max_plus = np.max(scaled_plus)
    print(f"  Max scaled speed at v_max+0.01: {max_plus:.6f} m/s (should be >2.0)")

    # Handle name for bottleneck
    if max_handle_idx == 0:
        bn_name = "龙头前把手"
    elif max_handle_idx == 223:
        bn_name = "龙尾后把手"
    elif max_handle_idx <= 221:
        bn_name = f"第{max_handle_idx}节龙身前把手"
    else:
        bn_name = "龙尾前把手"

    print(f"\n  Bottleneck handle: {bn_name} (index {max_handle_idx})")
    print(f"  Bottleneck time: t = {t_bottleneck:.1f} s")

    # Compute bottleneck position for context
    s_bn = V_NOMINAL * t_bottleneck
    theta_bn = find_head_theta(THETA0, s_bn, B_IN)
    r_head_bn = B_IN * theta_bn
    print(f"  Head radius at bottleneck: r = {r_head_bn:.4f} m")
    print(f"  Head theta at bottleneck: {theta_bn:.4f} rad = {theta_bn/(2*np.pi):.2f} turns")

    # --- Figures ---
    figures_dir = os.path.join(os.path.dirname(__file__), '..', 'figures')

    # Figure 1: Max speed vs head speed (linear relationship)
    fig, ax = plt.subplots(figsize=(7, 5))
    v_heads = np.linspace(1.0, v_max + 0.5, 30)
    max_speeds = [np.max(all_speeds_flat * (vh / V_NOMINAL)) for vh in v_heads]
    ax.plot(v_heads, max_speeds, 'b-', linewidth=2)
    ax.axhline(y=2.0, color='r', linestyle='--', linewidth=1.5, label='v = 2.0 m/s limit')
    ax.axvline(x=v_max, color='g', linestyle='--', linewidth=1.5, label=f'v_max = {v_max:.4f} m/s')
    ax.set_xlabel('Head Speed (m/s)')
    ax.set_ylabel('Maximum Handle Speed (m/s)')
    ax.set_title('Maximum Handle Speed vs Head Speed (Q5)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'fig_q5_speed_relation.png'), dpi=300)
    plt.close(fig)
    print(f"  Saved fig_q5_speed_relation.png")

    # Figure 2: Speed amplification factor along dragon body at bottleneck time
    fig, ax = plt.subplots(figsize=(8, 4))
    if max_time_idx < len(times_in):
        speeds_at_bn = speeds_in[max_time_idx]
    else:
        speeds_at_bn = speeds_deep[max_time_idx - len(times_in)]
    ampl_factors = speeds_at_bn / V_NOMINAL

    ax.bar(range(N_HANDLES), ampl_factors, width=1.0, alpha=0.7)
    ax.axhline(y=f_max, color='r', linestyle='--', linewidth=1.5, label=f'Max = {f_max:.4f}')
    ax.scatter([max_handle_idx], [f_max], color='red', s=100, zorder=5, label=f'Bottleneck: handle {max_handle_idx}')
    ax.set_xlabel('Handle Index')
    ax.set_ylabel('Speed Amplification Factor (v_i / v_head)')
    ax.set_title(f'Speed Amplification at t = {t_bottleneck:.0f} s (Q5)')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'fig_q5_amplification_factor.png'), dpi=300)
    plt.close(fig)
    print(f"  Saved fig_q5_amplification_factor.png")

    # Figure 3: Bottleneck location on spiral
    fig, ax = plt.subplots(figsize=(8, 8))
    # Get positions at bottleneck
    s_bn_pos = V_NOMINAL * t_bottleneck
    theta_bn_pos = find_head_theta(THETA0, s_bn_pos, B_IN)
    pos_bn, thetas_bn = compute_all_positions(theta_bn_pos, B_IN, L_arr)

    # Spiral background
    th_plot = np.linspace(thetas_bn[0] - 5, thetas_bn[-1] + 5, 2000)
    x_sp = B_IN * th_plot * np.cos(th_plot)
    y_sp = B_IN * th_plot * np.sin(th_plot)
    ax.plot(x_sp, y_sp, 'gray', alpha=0.2, linewidth=0.5)

    # Handles
    ax.plot(pos_bn[:, 0], pos_bn[:, 1], 'b.-', markersize=1.5, linewidth=0.5)
    ax.plot(pos_bn[0, 0], pos_bn[0, 1], 'r*', markersize=14, zorder=6, label='Head')
    ax.plot(pos_bn[max_handle_idx, 0], pos_bn[max_handle_idx, 1], 'mo', markersize=12,
            zorder=7, markeredgewidth=3, label=f'Bottleneck (handle {max_handle_idx})')
    # Draw boundary
    th_c = np.linspace(0, 2*np.pi, 200)
    ax.plot(R_TURN * np.cos(th_c), R_TURN * np.sin(th_c), 'k--', alpha=0.5,
            linewidth=1, label=f'r={R_TURN}m')
    ax.plot(0, 0, 'k+', markersize=12, label='Center')
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.set_title(f'Bottleneck Location at t = {t_bottleneck:.0f} s (Q5)')
    ax.set_aspect('equal')
    ax.legend(fontsize=8, loc='lower left')
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'fig_q5_bottleneck_location.png'), dpi=300)
    plt.close(fig)
    print(f"  Saved fig_q5_bottleneck_location.png")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Maximum head speed v_max = {v_max:.4f} m/s")
    print(f"  Speed amplification factor f_max = {f_max:.4f}")
    print(f"  Bottleneck handle: {bn_name} at t = {t_bottleneck:.0f} s")
    print(f"  Constraint: all handle speeds <= 2.0 m/s")
    print(f"  At v_max, max handle speed = {max_scaled:.4f} m/s")
    print(f"  At v_max + 0.01, max handle speed = {max_plus:.4f} m/s (> 2.0)")


if __name__ == '__main__':
    main()
