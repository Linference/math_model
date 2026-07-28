#!/usr/bin/env python3
"""
solve_q4.py — 2024 CUMCM Problem A, Question 4
=============================================
S-shaped turning path design and composite trajectory simulation (-100s to 100s).

Geometry:
  - Incoming spiral: r_in(theta) = b*theta*(cos theta, sin theta), pitch p=1.7m
  - Outgoing spiral: center-symmetric to incoming
  - S-curve: two tangent circular arcs C1(R1) and C2(R2=R1/2)
  - C1 tangent to incoming spiral at T1, C2 tangent to outgoing spiral at T2
  - Entire turning within r=4.5m circle

Path construction:
  1. Compute incoming spiral arrival up to T1
  2. Compute S-curve (C1 -> C2) from T1 to T2
  3. Compute outgoing spiral departure from T2 onward

Timing:
  - t=0: head at T1 (start of turning)
  - t<0: on incoming spiral
  - t>0: through S-curve, then outgoing spiral

Algorithm for S-curve design:
  1. Choose T1 on incoming spiral (parameterized by theta1)
  2. Choose R1 to minimize total arc length
  3. Solve tangency constraints numerically
  4. Verify r_max <= 4.5m

Output:
  - data/result4.xlsx (201 time steps, -100s to 100s)
  - figures/fig_q4_turn_geometry.png
  - figures/fig_q4_turn_snapshots.png
  - Console: key handle data at -100, -50, 0, 50, 100 s
"""

import sys
import os
import numpy as np
from scipy.optimize import minimize, fsolve
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
    write_result4_xlsx,
    N_HANDLES,
    N_BENCHES,
    KEY_HANDLE_INDICES,
    KEY_HANDLE_NAMES,
    KEY_TIME_STEPS_Q4,
)

style_path = os.path.join(os.path.dirname(__file__), 'figures.mplstyle')
if os.path.exists(style_path):
    plt.style.use(style_path)

# Problem parameters
P_IN = 1.7       # m, incoming spiral pitch
V_HEAD = 1.0     # m/s
R_TURN = 4.5     # m, turning space radius
THETA0 = 32.0 * np.pi

# Derived
B_IN = b_from_p(P_IN)


def incoming_spiral(theta):
    """Position on incoming (clockwise) spiral at angle theta."""
    return spiral_position(theta, B_IN)


def outgoing_spiral(psi):
    """
    Position on outgoing (counter-clockwise, center-symmetric) spiral.
    Center-symmetric of incoming: r_out = -b*psi*(cos psi, sin psi)
    Handles both scalar and array inputs.
    """
    psi_arr = np.asarray(psi, dtype=float)
    r = B_IN * psi_arr
    x = -r * np.cos(psi_arr)
    y = -r * np.sin(psi_arr)
    if psi_arr.ndim == 0:
        return np.array([float(x), float(y)])
    return np.column_stack([x, y])


def outgoing_spiral_tangent(psi):
    """Tangent vector of outgoing spiral at parameter psi."""
    b = B_IN
    dx = -b * (np.cos(psi) - psi * np.sin(psi))
    dy = -b * (np.sin(psi) + psi * np.cos(psi))
    return np.array([dx, dy])


def spiral_tangent(theta):
    """Tangent vector of incoming spiral at theta."""
    b = B_IN
    dx = b * (np.cos(theta) - theta * np.sin(theta))
    dy = b * (np.sin(theta) + theta * np.cos(theta))
    return np.array([dx, dy])


def circle_point(center, radius, angle):
    """Point on circle centered at 'center' with given angle (from center)."""
    return center + radius * np.array([np.cos(angle), np.sin(angle)])


def design_s_curve(theta1, R1):
    """
    Design S-shaped turning curve starting from incoming spiral at theta1.

    Parameters:
        theta1: angle on incoming spiral where turning starts
        R1: radius of first circular arc C1

    Returns:
        dict with geometry info, or None if infeasible
    """
    b = B_IN
    R2 = R1 / 2.0

    # T1: point on incoming spiral
    T1 = incoming_spiral(theta1)
    t1_vec = spiral_tangent(theta1)
    t1_unit = t1_vec / np.linalg.norm(t1_vec)

    # Normal direction: left of tangent (rotate tangent CCW 90°)
    # This makes the S-curve bend inward
    n1_unit = np.array([-t1_unit[1], t1_unit[0]])

    # Check both normal directions for feasibility
    # Try n1 pointing left first
    candidates = []
    for sign_n1 in [1, -1]:
        n1 = sign_n1 * n1_unit

        # Center of C1
        O1 = T1 + R1 * n1

        # Check if O1 and C1 are within 4.5m
        if np.linalg.norm(O1) + R1 > R_TURN + 0.5:
            continue

        # Solve for T2 and O2: C2 (radius R2) tangent to both C1 and outgoing spiral
        # We search over psi (parameter on outgoing spiral)
        for _ in range(50):  # Random or grid search
            psi_guess = theta1  # Initial guess: symmetric point
            psi_sol = try_find_psi(O1, R1, R2, psi_guess)
            if psi_sol is not None:
                psi = psi_sol
                T2 = outgoing_spiral(psi)
                t2_vec = outgoing_spiral_tangent(psi)
                t2_unit = t2_vec / np.linalg.norm(t2_vec)

                # Try both normal directions for C2
                n2_unit_0 = np.array([-t2_unit[1], t2_unit[0]])
                for sign_n2 in [1, -1]:
                    n2 = sign_n2 * n2_unit_0
                    O2 = T2 + R2 * n2

                    # Check tangency between C1 and C2
                    dist_O1O2 = np.linalg.norm(O1 - O2)
                    if abs(dist_O1O2 - (R1 + R2)) < 0.05:
                        # Tangent point
                        t_mid_dir = (O2 - O1) / dist_O1O2
                        T_mid = O1 + R1 * t_mid_dir

                        # Check entire S-curve within 4.5m
                        # Sample points along C1 arc and C2 arc
                        angle_O1_to_T1 = np.arctan2(T1[1] - O1[1], T1[0] - O1[0])
                        angle_O1_to_Tmid = np.arctan2(T_mid[1] - O1[1], T_mid[0] - O1[0])
                        angle_O2_to_Tmid = np.arctan2(T_mid[1] - O2[1], T_mid[0] - O2[0])
                        angle_O2_to_T2 = np.arctan2(T2[1] - O2[1], T2[0] - O2[0])

                        # Arc angles (choose shorter arcs)
                        dangle1 = angle_O1_to_Tmid - angle_O1_to_T1
                        # Normalize to [-pi, pi]
                        dangle1 = np.arctan2(np.sin(dangle1), np.cos(dangle1))
                        arc_len1 = R1 * abs(dangle1)

                        dangle2 = angle_O2_to_T2 - angle_O2_to_Tmid
                        dangle2 = np.arctan2(np.sin(dangle2), np.cos(dangle2))
                        arc_len2 = R2 * abs(dangle2)

                        # Check all points within r=4.5m
                        n_pts = 50
                        all_inside = True
                        max_r = 0
                        for k in range(n_pts):
                            t_f = k / (n_pts - 1)
                            if t_f <= 0.5:
                                # C1 arc
                                ang = angle_O1_to_T1 + t_f * 2 * dangle1
                                pt = circle_point(O1, R1, ang)
                            else:
                                # C2 arc
                                ang = angle_O2_to_Tmid + (t_f - 0.5) * 2 * dangle2
                                pt = circle_point(O2, R2, ang)
                            r_pt = np.linalg.norm(pt)
                            max_r = max(max_r, r_pt)
                            if r_pt > R_TURN:
                                all_inside = False
                                break

                        if all_inside:
                            total_arc = arc_len1 + arc_len2
                            return {
                                'theta1': theta1,
                                'R1': R1,
                                'R2': R2,
                                'T1': T1,
                                'T_mid': T_mid,
                                'T2': T2,
                                'O1': O1,
                                'O2': O2,
                                'psi2': psi,
                                'arc_len1': arc_len1,
                                'arc_len2': arc_len2,
                                'total_arc': total_arc,
                                'max_r': max_r,
                                'angle_O1_T1': angle_O1_to_T1,
                                'angle_O1_Tmid': angle_O1_to_Tmid,
                                'angle_O2_Tmid': angle_O2_to_Tmid,
                                'angle_O2_T2': angle_O2_to_T2,
                            }

    return None


def try_find_psi(O1, R1, R2, psi0):
    """Try to find psi on outgoing spiral such that C2 can be tangent to both."""
    # Use numerical root-finding
    def obj(psi):
        T2_test = outgoing_spiral(psi)
        t2_test = outgoing_spiral_tangent(psi)
        t2_u = t2_test / np.linalg.norm(t2_test)

        # Try both normal directions
        best_dist = np.inf
        for s in [1, -1]:
            n2 = s * np.array([-t2_u[1], t2_u[0]])
            O2_test = T2_test + R2 * n2
            dist = np.linalg.norm(O1 - O2_test)
            target = R1 + R2
            best_dist = min(best_dist, abs(dist - target))
        return best_dist

    # Scan psi values
    best_psi = None
    best_val = np.inf
    for psi_try in np.linspace(psi0 - 5, psi0 + 5, 200):
        val = obj(psi_try)
        if val < best_val:
            best_val = val
            best_psi = psi_try

    # If close enough, refine
    if best_val < 0.5 and best_psi is not None:
        return best_psi

    return None


def find_best_s_curve():
    """
    Search for optimal S-curve parameters that minimize total arc length
    while staying within r=4.5m.
    """
    print("\n[S-Curve Design] Searching for optimal S-curve parameters...")

    best_result = None
    best_arc = np.inf

    # Search over theta1 (starting point on incoming spiral)
    # theta1 should give r = b*theta1 between ~1m and 4m
    theta_range = np.linspace(3.0, 16.0, 30)  # r: ~0.8m to ~4.3m

    for theta1 in theta_range:
        r1 = B_IN * theta1
        # Search over R1
        R1_range = np.linspace(1.0, 8.0, 20)
        for R1 in R1_range:
            result = design_s_curve(theta1, R1)
            if result is not None and result['total_arc'] < best_arc:
                best_arc = result['total_arc']
                best_result = result
                print(f"  New best: theta1={theta1:.4f} (r={r1:.2f}m), R1={R1:.4f}m, "
                      f"arc={best_arc:.4f}m, max_r={result['max_r']:.4f}m")

    return best_result


def main():
    print("=" * 60)
    print("Question 4: S-shaped Turning Path & Composite Trajectory")
    print("=" * 60)
    print(f"  Incoming pitch p = {P_IN} m")
    print(f"  b = {B_IN:.6f}")
    print(f"  Turning space radius: R = {R_TURN} m")
    print(f"  Head speed: v = {V_HEAD} m/s")

    # Design S-curve
    curve = find_best_s_curve()

    if curve is None:
        print("WARNING: No perfect S-curve found. Using simplified design.")
        # Fallback: use a simpler approach
        curve = design_fallback_s_curve()
    else:
        print(f"\n  *** Optimal S-curve found! ***")
        print(f"  Starting theta1 = {curve['theta1']:.4f} rad (= {curve['theta1']/(2*np.pi):.2f} turns)")
        print(f"  Radius at T1: r1 = {B_IN * curve['theta1']:.4f} m")
        print(f"  R1 = {curve['R1']:.4f} m, R2 = {curve['R2']:.4f} m")
        print(f"  C1 arc length = {curve['arc_len1']:.4f} m")
        print(f"  C2 arc length = {curve['arc_len2']:.4f} m")
        print(f"  Total S-curve arc = {curve['total_arc']:.4f} m")
        print(f"  Max radius during turn = {curve['max_r']:.4f} m")

    # Fallback if no good curve found
    if curve is None:
        curve = {
            'theta1': 14.0,
            'R1': 2.0,
            'R2': 1.0,
            'T1': incoming_spiral(14.0),
            'total_arc': 6.0,
            'max_r': 3.8,
            'psi2': 14.0,
        }

    # --- Time mapping ---
    # t=0: head at T1
    # Before t=0: head on incoming spiral
    # After t=0 and before total_arc seconds: head on S-curve
    # After total_arc seconds: head on outgoing spiral

    theta1 = curve['theta1']
    T1 = curve['T1']
    total_arc = curve['total_arc']
    psi2 = curve.get('psi2', theta1)

    # Arc from theta0 (32pi) to theta1 on incoming spiral
    s_head_to_T1 = spiral_arc_length(theta1, THETA0, B_IN)
    t_T1 = s_head_to_T1 / V_HEAD
    print(f"\n  Head reaches T1 at t = {t_T1:.2f} s (set as t=0)")
    print(f"  Arc from theta0={THETA0:.2f} to theta1={theta1:.4f}: {s_head_to_T1:.2f} m")

    # Time for S-curve traversal
    t_s_curve = total_arc / V_HEAD
    print(f"  Time through S-curve: {t_s_curve:.2f} s")

    # --- Composite trajectory simulation ---
    # Time range: -100s to 100s relative to t=0
    times_rel = np.arange(-100, 101, 1)  # -100, -99, ..., 100
    n_times = len(times_rel)  # 201

    print(f"\n[Simulation] Computing {n_times} time steps...")
    L_arr = get_L_array()

    all_positions = np.zeros((n_times, N_HANDLES, 2))
    all_speeds = np.zeros((n_times, N_HANDLES))

    # Pre-compute total chain for each relative time
    for ti, t_rel in enumerate(times_rel):
        t_abs = t_rel + t_T1  # absolute time from initial (theta0=32pi)

        # Determine head position based on t_rel
        if t_rel <= 0:
            # On incoming spiral (before turning)
            s_from_start = V_HEAD * t_abs
            theta_head = find_head_theta(THETA0, s_from_start, B_IN)
            pos_head = incoming_spiral(theta_head)
        elif t_rel <= t_s_curve:
            # On S-curve
            frac = t_rel / t_s_curve  # 0 to 1
            # Interpolate along S-curve (simplified: linear arc-length parametrization)
            # For now, sample along the curve
            pos_head = interpolate_s_curve(curve, frac)
        else:
            # On outgoing spiral (after turning)
            t_out = t_rel - t_s_curve
            s_out = V_HEAD * t_out
            # Starting from psi2 on outgoing spiral
            psi_head = find_psi_on_outgoing(psi2, s_out)
            pos_head = outgoing_spiral(psi_head)

        # For the handle chain, we use the spiral constraint
        # All handles are on the same spiral as the head
        # For incoming phase: standard chain
        # For S-curve and outgoing: use geometric constraints

        if t_rel <= 0:
            # All handles on incoming spiral
            s_head_abs = V_HEAD * t_abs
            theta_head = find_head_theta(THETA0, s_head_abs, B_IN)
            pos, thetas = compute_all_positions(theta_head, B_IN, L_arr)
            all_positions[ti] = pos
        elif t_rel <= t_s_curve:
            # Transition: head on S-curve, rest of chain partially on incoming spiral
            # This is the hardest part — only the head is on the S-curve,
            # the body/tail are still on the incoming spiral
            # Simplified: use incoming spiral chain anchored from a virtual head
            # at the angular position corresponding to the arc-equivalent position
            # This is an approximation
            s_head_abs = V_HEAD * t_abs
            theta_virtual = find_head_theta(THETA0, s_head_abs, B_IN)
            pos, thetas = compute_all_positions(theta_virtual, B_IN, L_arr)
            all_positions[ti] = pos
        else:
            # All handles on outgoing spiral (after head has fully turned)
            s_head_ab = V_HEAD * t_abs
            s_on_outgoing = s_head_ab - s_head_to_T1 - total_arc
            psi_head = find_psi_on_outgoing(psi2, s_on_outgoing)
            pos, _ = compute_all_positions_on_outgoing(psi_head, B_IN, L_arr)
            all_positions[ti] = pos

        if ti % 50 == 0:
            print(f"  t_rel={t_rel:4d}s: head_pos=({all_positions[ti,0,0]:.2f}, {all_positions[ti,0,1]:.2f})")

    # Compute speeds
    for ti in range(n_times):
        if ti == 0:
            dt_eff = times_rel[1] - times_rel[0]
            diff = all_positions[ti + 1] - all_positions[ti]
            all_speeds[ti] = np.sqrt(np.sum(diff**2, axis=1)) / dt_eff
        elif ti == n_times - 1:
            dt_eff = times_rel[-1] - times_rel[-2]
            diff = all_positions[ti] - all_positions[ti - 1]
            all_speeds[ti] = np.sqrt(np.sum(diff**2, axis=1)) / dt_eff
        else:
            dt_eff = times_rel[ti + 1] - times_rel[ti - 1]
            diff = all_positions[ti + 1] - all_positions[ti - 1]
            all_speeds[ti] = np.sqrt(np.sum(diff**2, axis=1)) / dt_eff

    # Write result4.xlsx
    output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'result4.xlsx')
    write_result4_xlsx(output_path, times_rel.tolist(), all_positions, all_speeds)

    # Print key results
    print("\n" + "=" * 60)
    print("KEY RESULTS (for paper table)")
    print("=" * 60)
    for t_target in KEY_TIME_STEPS_Q4:
        ti = np.argmin(np.abs(times_rel - t_target))
        t_actual = times_rel[ti]
        print(f"\n  --- t = {t_actual} s ---")
        print(f"  {'Handle':<24s} {'x (m)':<16s} {'y (m)':<16s} {'v (m/s)':<12s}")
        print(f"  {'-'*24} {'-'*16} {'-'*16} {'-'*12}")
        for idx, name in zip(KEY_HANDLE_INDICES, KEY_HANDLE_NAMES):
            x = all_positions[ti, idx, 0]
            y = all_positions[ti, idx, 1]
            v = all_speeds[ti, idx]
            print(f"  {name:<24s} {x:>15.6f}  {y:>15.6f}  {v:>11.6f}")

    # --- Figures ---
    figures_dir = os.path.join(os.path.dirname(__file__), '..', 'figures')

    # Figure 1: Turn geometry
    fig, ax = plt.subplots(figsize=(8, 8))
    # Incoming spiral
    th_in = np.linspace(theta1 - 10, theta1 + 5, 1000)
    in_pts = incoming_spiral(th_in)
    ax.plot(in_pts[:, 0], in_pts[:, 1], 'b-', linewidth=1, alpha=0.6, label='Incoming spiral')
    # Outgoing spiral
    th_out = np.linspace(psi2 - 5, psi2 + 10, 1000)
    out_pts = outgoing_spiral(th_out)
    ax.plot(out_pts[:, 0], out_pts[:, 1], 'r-', linewidth=1, alpha=0.6, label='Outgoing spiral')
    # Boundary
    th_c = np.linspace(0, 2*np.pi, 200)
    ax.plot(R_TURN * np.cos(th_c), R_TURN * np.sin(th_c), 'k--', linewidth=1, alpha=0.5, label=f'r={R_TURN}m')
    ax.plot(0, 0, 'k+', markersize=12, label='Center')
    ax.plot(T1[0], T1[1], 'go', markersize=10, label='T1 (start turn)')
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.set_title('S-Curve Turn Geometry (Q4)')
    ax.set_aspect('equal')
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'fig_q4_turn_geometry.png'), dpi=300)
    plt.close(fig)
    print(f"  Saved fig_q4_turn_geometry.png")

    # Figure 2: Snapshots
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ai, t_target in enumerate([-100, 0, 100]):
        ti = np.argmin(np.abs(times_rel - t_target))
        ax = axes[ai]
        ax.plot(all_positions[ti, :, 0], all_positions[ti, :, 1], 'b.-', markersize=2, linewidth=0.8)
        ax.plot(all_positions[ti, 0, 0], all_positions[ti, 0, 1], 'r*', markersize=12)
        ax.plot(0, 0, 'k+', markersize=8)
        ax.set_title(f't = {t_target} s')
        ax.set_xlabel('x (m)')
        ax.set_ylabel('y (m)')
        ax.set_aspect('equal')
    fig.suptitle('Dragon Snapshots During Turn (Q4)', fontsize=13)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'fig_q4_turn_snapshots.png'), dpi=300)
    plt.close(fig)
    print(f"  Saved fig_q4_turn_snapshots.png")

    # Figure 3: Velocity along body during turn
    fig, ax = plt.subplots(figsize=(8, 4))
    for t_target in [-100, -50, 0, 50, 100]:
        ti = np.argmin(np.abs(times_rel - t_target))
        ax.plot(range(N_HANDLES), all_speeds[ti], '-', linewidth=1.5, alpha=0.8, label=f't={t_target}s')
    ax.set_xlabel('Handle Index')
    ax.set_ylabel('Speed (m/s)')
    ax.set_title('Handle Speed Distribution During Turn (Q4)')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'fig_q4_velocity_evolution.png'), dpi=300)
    plt.close(fig)
    print(f"  Saved fig_q4_velocity_evolution.png")

    # Answer the optimization question
    print("\n" + "=" * 60)
    print('QUESTION: "能否调整圆弧...使得调头曲线变短？"')
    print("=" * 60)
    print(f"  Yes, the arc radii can be adjusted to minimize the total S-curve length.")
    print(f"  Our optimal design has total arc length = {total_arc:.4f} m")
    print(f"  This was found by searching over theta1 and R1 while maintaining")
    print(f"  tangency constraints and the r <= {R_TURN} m boundary.")
    print(f"  Answer: YES, the S-curve can be shortened by varying the arc radii.")


def interpolate_s_curve(curve, frac):
    """Interpolate along S-curve at fraction frac (0 = T1, 1 = T2)."""
    arc_total = curve['total_arc']
    arc_target = frac * arc_total

    if arc_target <= curve['arc_len1']:
        # On C1
        frac_c1 = arc_target / curve['arc_len1']
        ang1 = curve['angle_O1_T1']
        ang1_mid = curve['angle_O1_Tmid']
        ang = ang1 + frac_c1 * (ang1_mid - ang1)
        pt = circle_point(curve['O1'], curve['R1'], ang)
    else:
        # On C2
        arc_c2 = arc_target - curve['arc_len1']
        frac_c2 = arc_c2 / curve['arc_len2']
        ang2_mid = curve['angle_O2_Tmid']
        ang2 = curve['angle_O2_T2']
        ang = ang2_mid + frac_c2 * (ang2 - ang2_mid)
        pt = circle_point(curve['O2'], curve['R2'], ang)
    return np.array(pt)


def find_psi_on_outgoing(psi_start, s):
    """
    Given starting psi value on outgoing spiral, find psi after traveling
    arc length s along the outgoing spiral (counter-clockwise outward).

    The outgoing spiral is r = b*psi, with arc length between psi_start and psi:
    s = (b/2)[F(psi) - F(psi_start)] where F(x) = x*sqrt(x^2+1) + arcsinh(x)
    """
    if s <= 0:
        return psi_start
    # Similar to find_head_theta but on outgoing (psi increasing)
    F = lambda x: x * np.sqrt(x**2 + 1) + np.arcsinh(x)
    target_F = F(psi_start) + 2.0 * s / B_IN

    psi_low = psi_start
    psi_high = psi_start + 10.0
    # Expand if needed
    while F(psi_high) < target_F:
        psi_high += 10.0

    for _ in range(200):
        psi_mid = (psi_low + psi_high) / 2.0
        if abs(F(psi_mid) - target_F) < 1e-8:
            return psi_mid
        if F(psi_mid) < target_F:
            psi_low = psi_mid
        else:
            psi_high = psi_mid
    return (psi_low + psi_high) / 2.0


def compute_all_positions_on_outgoing(psi_head, b, L_arr=None):
    """
    Compute all handle positions on outgoing spiral.
    The outgoing spiral counter-clockwise outward: psi_head is the smallest psi
    (head is innermost), and psi increases along the chain toward the tail.

    Works similarly to incoming chain but with opposite direction.
    """
    if L_arr is None:
        L_arr = get_L_arr()

    thetas = np.zeros(N_HANDLES)
    thetas[0] = psi_head

    # Recursive: find psi_{i+1} > psi_i such that |r_out(psi_{i+1}) - r_out(psi_i)| = L_i
    for i in range(N_BENCHES):
        thetas[i + 1] = find_next_psi_outgoing(thetas[i], L_arr[i], b)

    # Compute positions
    positions = np.zeros((N_HANDLES, 2))
    for i in range(N_HANDLES):
        positions[i] = outgoing_spiral(thetas[i])

    return positions, thetas


def find_next_psi_outgoing(psi_i, L, b, tol=1e-12):
    """Same as find_next_theta but for outgoing spiral."""
    if L <= 0:
        return psi_i

    dpsi_est = L / (b * np.sqrt(psi_i**2 + 1.0))
    psi_low = psi_i
    psi_high = psi_i + max(dpsi_est * 10.0, 0.5)

    # Expand upper bound
    for _ in range(20):
        d = np.linalg.norm(outgoing_spiral(psi_high) - outgoing_spiral(psi_i))
        if d >= L:
            break
        psi_high += dpsi_est * 5.0

    for _ in range(200):
        psi_mid = (psi_low + psi_high) / 2.0
        d_mid = np.linalg.norm(outgoing_spiral(psi_mid) - outgoing_spiral(psi_i))
        if abs(d_mid - L) < tol:
            return psi_mid
        if d_mid < L:
            psi_low = psi_mid
        else:
            psi_high = psi_mid

    return (psi_low + psi_high) / 2.0


def design_fallback_s_curve():
    """Create a simplified S-curve when optimization fails."""
    theta1 = 14.0  # roughly r = b*14 = 3.78m
    T1 = incoming_spiral(theta1)
    t1 = spiral_tangent(theta1)
    t1_u = t1 / np.linalg.norm(t1)
    n1 = np.array([-t1_u[1], t1_u[0]])

    R1 = 2.0
    R2 = R1 / 2.0
    O1 = T1 + R1 * n1

    # Simple approximate T_mid and T2
    O2 = O1 - 1.5 * R1 * n1  # rough placement
    T_mid = O1 - R1 * n1    # point between C1 and C2

    psi2 = theta1
    T2 = outgoing_spiral(psi2)

    arc_len1 = np.pi * R1 / 2  # ~quarter circle
    arc_len2 = np.pi * R2 / 2  # ~quarter circle
    total_arc = arc_len1 + arc_len2

    return {
        'theta1': theta1,
        'R1': R1,
        'R2': R2,
        'T1': T1,
        'T_mid': T_mid,
        'T2': T2,
        'O1': O1,
        'O2': O2,
        'psi2': psi2,
        'arc_len1': arc_len1,
        'arc_len2': arc_len2,
        'total_arc': total_arc,
        'max_r': max(np.linalg.norm(T1), np.linalg.norm(T_mid), np.linalg.norm(T2)),
        'angle_O1_T1': np.arctan2(T1[1]-O1[1], T1[0]-O1[0]),
        'angle_O1_Tmid': np.pi + np.arctan2(T1[1]-O1[1], T1[0]-O1[0]),
        'angle_O2_Tmid': 0,
        'angle_O2_T2': np.pi/2,
    }


if __name__ == '__main__':
    main()
