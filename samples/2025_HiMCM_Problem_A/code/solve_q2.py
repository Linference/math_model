"""
问题2 — 基本场景 (6房间, 2消防员) 最优清扫调度
模型: 多响应者VRP (并行清扫, makespan最小化)
算法: 枚举法 (穷举所有分配+排列) + pulp MILP对照
随机种子: 42
"""

import numpy as np
import json
import os
import sys
import time
import itertools
from itertools import permutations, product
from collections import defaultdict

# 确保 code 目录在 path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (build_graph_from_json, load_room_params,
                   route_total_time, makespan_of_assignment,
                   get_shortest_path_info, compute_travel_time,
                   compute_sweep_time, SPEED_GEAR)

np.random.seed(42)

# ============================================================
# 枚举求解
# ============================================================

def enumerate_optimal_vrp(G, room_ids, room_params, n_agents=2,
                          start_node='E1', room_types_map=None):
    """
    枚举所有可能的房间分配 → 各代理内部全排列 → 找最小 makespan。
    返回: (best_makespan, best_assignment, all_results)
    """
    n_rooms = len(room_ids)
    best_makespan = float('inf')
    best_assignment = None
    all_results = []

    total_assignments = 2 ** n_rooms  # 每个房间可分配给 agent 0 或 agent 1
    print(f"  枚举空间: {total_assignments} 种分配 × 内部全排列")

    for mask in range(total_assignments):
        # 按位分配
        agent_rooms = {i: [] for i in range(n_agents)}
        for j, rid in enumerate(room_ids):
            agent_idx = (mask >> j) & 1
            agent_rooms[agent_idx].append(rid)

        # 跳过空分配
        if any(len(v) == 0 for v in agent_rooms.values()):
            continue

        # 对每个 agent 找最优序列（全排列）
        best_agent_time = {}
        best_agent_order = {}
        feasible = True
        for agent in range(n_agents):
            rooms = agent_rooms[agent]
            if len(rooms) == 0:
                best_agent_time[agent] = 0.0
                best_agent_order[agent] = []
                continue
            best_t = float('inf')
            best_perm = None
            for perm in permutations(rooms):
                tt, _, _, _ = route_total_time(
                    G, list(perm), room_params, start_node, room_types_map
                )
                if tt < best_t:
                    best_t = tt
                    best_perm = list(perm)
            best_agent_time[agent] = best_t
            best_agent_order[agent] = best_perm

        makespan = max(best_agent_time.values())
        all_results.append({
            'mask': mask,
            'assignment': {k: list(v) for k, v in agent_rooms.items()},
            'optimal_order': best_agent_order,
            'agent_times': dict(best_agent_time),
            'makespan': makespan,
        })

        if makespan < best_makespan:
            best_makespan = makespan
            best_assignment = all_results[-1]

    return best_makespan, best_assignment, all_results


def solve_q2_enum(G, room_params, room_types_map=None):
    """枚举法主求解"""
    room_ids = [n for n, d in G.nodes(data=True) if d.get('type') == 'room']
    print(f"\n[枚举法] 房间: {room_ids}")

    t0 = time.time()
    best_mk, best_asgn, all_res = enumerate_optimal_vrp(
        G, room_ids, room_params, n_agents=2,
        start_node='E1', room_types_map=room_types_map
    )
    elapsed = time.time() - t0

    print(f"[枚举法] 最优 makespan = {best_mk:.2f} s  ({best_mk/60:.2f} min)")
    print(f"[枚举法] 耗时 {elapsed:.3f} s")
    print(f"[枚举法] 分配:")
    for agent, order in best_asgn['optimal_order'].items():
        t = best_asgn['agent_times'][agent]
        print(f"  响应者 {agent+1}: {order} → {t:.2f} s ({t/60:.2f} min)")

    return best_mk, best_asgn, all_res, elapsed


# ============================================================
# pulp MILP 对照求解
# ============================================================

def solve_q2_pulp(G, room_params, room_types_map=None, time_limit=60):
    """
    用 pulp 建立 VRP MILP 模型。
    变量: x[i,j,k] = 1 如果 agent k 从 i 直接到 j
          u[i,k] = 访问顺序辅助变量 (MTZ subtour elimination)
    目标: min makespan = max_k sum_{i,j} x[i,j,k] * (travel_ij + sweep_j)
    """
    try:
        import pulp
    except ImportError:
        print("[pulp] pulp 未安装，跳过 MILP 对照")
        return None

    room_ids = [n for n, d in G.nodes(data=True) if d.get('type') == 'room']
    n_rooms = len(room_ids)
    n_agents = 2
    start_node = 'E1'

    # 预计算所有节点对距离矩阵
    all_nodes = [start_node] + room_ids
    node_idx = {n: i for i, n in enumerate(all_nodes)}
    n_nodes = len(all_nodes)
    dist_matrix = np.zeros((n_nodes, n_nodes))
    for i, u in enumerate(all_nodes):
        for j, v in enumerate(all_nodes):
            if i == j:
                continue
            _, d = get_shortest_path_info(G, u, v)
            dist_matrix[i, j] = d

    # 清扫时间
    sweep_times = {}
    for rid in room_ids:
        rtype = room_types_map.get(rid, 'office') if room_types_map else G.nodes[rid].get('room_type', 'office')
        sweep_times[rid] = compute_sweep_time(rtype, room_params)

    # 时间矩阵: travel + sweep (j 的清扫时间加到进入 j 的边上)
    time_matrix = np.zeros((n_nodes, n_nodes))
    for i in range(n_nodes):
        for j in range(n_nodes):
            if i == j:
                continue
            travel = compute_travel_time(dist_matrix[i, j], SPEED_GEAR)
            # sweep time of destination (except start node)
            sweep = sweep_times.get(all_nodes[j], 0.0) if j > 0 else 0.0
            time_matrix[i, j] = travel + sweep

    # 建立模型
    prob = pulp.LpProblem("Firefighter_VRP", pulp.LpMinimize)

    # 决策变量
    x = {}  # x[i,j,k]: agent k goes from i to j
    for k in range(n_agents):
        for i in range(n_nodes):
            for j in range(n_nodes):
                if i != j:
                    x[(i, j, k)] = pulp.LpVariable(f"x_{i}_{j}_{k}", cat='Binary')

    u = {}  # MTZ subtour elimination: visit order at room i for agent k
    for k in range(n_agents):
        for i in range(1, n_nodes):  # room nodes only
            u[(i, k)] = pulp.LpVariable(f"u_{i}_{k}", lowBound=1, upBound=n_rooms, cat='Integer')

    # Makespan variable
    T = pulp.LpVariable("T", lowBound=0)

    # Objective
    prob += T

    # Constraints
    # (1) Each room visited exactly once
    for j in range(1, n_nodes):  # rooms only
        prob += pulp.lpSum(x[(i, j, k)] for k in range(n_agents) for i in range(n_nodes) if i != j) == 1

    # (2) Flow conservation for each agent
    for k in range(n_agents):
        for j in range(1, n_nodes):
            prob += (pulp.lpSum(x[(i, j, k)] for i in range(n_nodes) if i != j) ==
                     pulp.lpSum(x[(j, i, k)] for i in range(n_nodes) if i != j))

    # (3) Each agent starts at the depot at most once
    for k in range(n_agents):
        prob += pulp.lpSum(x[(0, j, k)] for j in range(1, n_nodes)) <= 1

    # (4) MTZ subtour elimination
    bigM = n_rooms + 1
    for k in range(n_agents):
        for i in range(1, n_nodes):
            for j in range(1, n_nodes):
                if i != j:
                    prob += u[(i, k)] - u[(j, k)] + bigM * x[(i, j, k)] <= bigM - 1

    # (5) Makespan ≥ each agent's total time
    for k in range(n_agents):
        prob += T >= pulp.lpSum(time_matrix[i, j] * x[(i, j, k)]
                                for i in range(n_nodes) for j in range(n_nodes) if i != j)

    # Solve
    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit)
    prob.solve(solver)

    status = pulp.LpStatus[prob.status]
    print(f"\n[pulp] 状态: {status}")
    if prob.status != pulp.LpOptimal:
        print("[pulp] 未找到最优解")
        return None

    opt_makespan = pulp.value(T)
    print(f"[pulp] 最优 makespan = {opt_makespan:.2f} s ({opt_makespan/60:.2f} min)")

    # 提取路径
    for k in range(n_agents):
        route = []
        current = 0  # start from depot
        while True:
            next_node = None
            for j in range(1, n_nodes):
                if (current, j, k) in x and pulp.value(x[(current, j, k)]) > 0.5:
                    next_node = j
                    break
            if next_node is None:
                break
            route.append(all_nodes[next_node])
            current = next_node
        agent_time = sum(time_matrix[all_nodes.index(route[i-1]) if i > 0 else 0, all_nodes.index(route[i])]
                         for i in range(len(route)))
        print(f"  响应者 {k+1}: {route}")

    return {'makespan': opt_makespan, 'status': status}


# ============================================================
# 参数灵敏度分析
# ============================================================

def sensitivity_analysis(G, room_params, room_types_map=None):
    """
    分析关键参数对 makespan 的影响：
      - 行进速度 (±30%)
      - 清扫时间 (±30%)
      - 烟雾因子 [1.0, 1.5, 2.0, 3.0]
    """
    print("\n=== 参数灵敏度分析 ===")
    room_ids = [n for n, d in G.nodes(data=True) if d.get('type') == 'room']

    results = {}

    # (a) 速度变化
    from utils import compute_travel_time as ctt, SPEED_GEAR as base_speed
    speeds = {'-30%': base_speed * 0.70, '-15%': base_speed * 0.85,
              'baseline': base_speed, '+15%': base_speed * 1.15, '+30%': base_speed * 1.30}
    speed_results = {}
    for label, spd in speeds.items():

        def custom_route_time(G, rooms, rp, start, rtm, sf):
            # 用自定义速度计算
            tt, ttv, tts, n = 0, 0, 0, len(rooms)
            cur = start
            for rid in rooms:
                _, dist = get_shortest_path_info(G, cur, rid)
                ttv += compute_travel_time(dist, spd, sf)
                rtype = room_types_map.get(rid, 'office') if room_types_map else G.nodes[rid].get('room_type', 'office')
                tts += compute_sweep_time(rtype, room_params, sf)
                cur = rid
                tt = ttv + tts
            return tt, ttv, tts, n

        # 重新枚举
        best_mk = float('inf')
        for mask in range(2 ** len(room_ids)):
            agent_rooms = {0: [], 1: []}
            for j, rid in enumerate(room_ids):
                agent_rooms[(mask >> j) & 1].append(rid)
            if any(len(v) == 0 for v in agent_rooms.values()):
                continue
            agent_times = {}
            for agent, rooms in agent_rooms.items():
                best_t = float('inf')
                for perm in permutations(rooms):
                    tt, _, _, _ = custom_route_time(G, list(perm), room_params, 'E1', room_types_map, 1.0)
                    if tt < best_t:
                        best_t = tt
                agent_times[agent] = best_t
            mk = max(agent_times.values())
            if mk < best_mk:
                best_mk = mk
        speed_results[label] = best_mk
    results['speed'] = speed_results
    for label, val in speed_results.items():
        print(f"  速度 {label}: makespan = {val:.1f} s ({val/60:.2f} min)")

    # (b) 烟雾因子
    smoke_results = {}
    for sf in [1.0, 1.5, 2.0, 3.0]:
        best_mk = float('inf')
        for mask in range(2 ** len(room_ids)):
            agent_rooms = {0: [], 1: []}
            for j, rid in enumerate(room_ids):
                agent_rooms[(mask >> j) & 1].append(rid)
            if any(len(v) == 0 for v in agent_rooms.values()):
                continue
            agent_times = {}
            for agent, rooms in agent_rooms.items():
                best_t = float('inf')
                for perm in permutations(rooms):
                    tt, _, _, _ = route_total_time(G, list(perm), room_params, 'E1', room_types_map, sf)
                    if tt < best_t:
                        best_t = tt
                agent_times[agent] = best_t
            mk = max(agent_times.values())
            if mk < best_mk:
                best_mk = mk
        smoke_results[f'smoke_{sf}x'] = best_mk
    results['smoke'] = smoke_results
    for label, val in smoke_results.items():
        print(f"  {label}: makespan = {val:.1f} s ({val/60:.2f} min)")

    return results


# ============================================================
# 输出保存
# ============================================================

def save_results(best_mk, best_asgn, elapsed, sens_results, output_dir):
    """保存结果到 JSON"""
    os.makedirs(output_dir, exist_ok=True)
    out = {
        'method': 'enumeration',
        'best_makespan_s': best_mk,
        'best_makespan_min': best_mk / 60,
        'assignment': {str(k): v for k, v in best_asgn['optimal_order'].items()},
        'agent_times_s': {str(k): v for k, v in best_asgn['agent_times'].items()},
        'runtime_s': elapsed,
        'sensitivity': {
            'speed': sens_results.get('speed', {}),
            'smoke': sens_results.get('smoke', {}),
        }
    }
    fpath = os.path.join(output_dir, 'q2_results.json')
    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\n[Q2] 结果已保存: {fpath}")


# ============================================================
# 主程序
# ============================================================
if __name__ == '__main__':
    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT = os.path.join(BASE, 'code', 'outputs')

    # 加载
    print("=" * 60)
    print("  Q2: 基本场景 — 最优清扫调度")
    print("=" * 60)
    G, data = build_graph_from_json(os.path.join(BASE, 'data', 'building_basic.json'))
    room_params = load_room_params(os.path.join(BASE, 'data', 'room_type_params.csv'))

    # 房间类型映射
    room_types_map = {}
    for n, d in G.nodes(data=True):
        if d.get('type') == 'room':
            room_types_map[n] = d.get('room_type', 'office')

    print(f"建筑: {G.graph['name']}")
    print(f"节点: {G.number_of_nodes()}, 边: {G.number_of_edges()}")
    room_ids = [n for n, d in G.nodes(data=True) if d.get('type') == 'room']
    print(f"房间: {room_ids}")

    # ---- 枚举法 ----
    best_mk, best_asgn, all_res, elapsed = solve_q2_enum(G, room_params, room_types_map)

    # ---- 时间分解 ----
    print("\n[时间分解]")
    for agent, rooms in best_asgn['optimal_order'].items():
        ttotal, ttravel, tsweep, nrooms = route_total_time(
            G, rooms, room_params, 'E1', room_types_map
        )
        print(f"  响应者 {agent+1}: {rooms}")
        print(f"    总时间={ttotal:.1f}s, 移动={ttravel:.1f}s ({ttravel/ttotal*100:.0f}%), "
              f"清扫={tsweep:.1f}s ({tsweep/ttotal*100:.0f}%), 房间数={nrooms}")

    # ---- pulp 对照 ----
    pulp_result = solve_q2_pulp(G, room_params, room_types_map)

    # ---- 灵敏度分析 ----
    sens_results = sensitivity_analysis(G, room_params, room_types_map)

    # ---- 保存 ----
    save_results(best_mk, best_asgn, elapsed, sens_results, OUTPUT)

    print("\n" + "=" * 60)
    print(f"  最终结果: makespan = {best_mk:.1f} s = {best_mk/60:.2f} min")
    print("=" * 60)
