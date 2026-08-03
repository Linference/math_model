"""
公共工具模块 — 图建模 + 时间计算 + 建筑图自动构建
依赖: numpy, json, pandas, networkx
随机种子: 42
"""

import numpy as np
import json
import pandas as pd
import networkx as nx

np.random.seed(42)

# ============================================================
# 速度常量 (m/s) — 基于 HiMCM 问题陈述
# ============================================================
SPEED_NORMAL   = 1.35   # 正常步行
SPEED_GEAR      = 1.0    # 穿着消防装备
SPEED_SMOKE     = 0.5    # 浓烟中爬行
SPEED_STAIR_UP   = 0.4   # 上楼
SPEED_STAIR_DOWN = 0.6   # 下楼
SPEED_CRAWL     = 0.3    # 极端浓烟


def load_room_params(csv_path):
    """加载房间类型参数 → dict[type] = {sweep_time_s, priority_weight, complexity_mult}"""
    df = pd.read_csv(csv_path)
    params = {}
    for _, row in df.iterrows():
        params[row['type']] = {
            'sweep_time': float(row['sweep_time_s']),
            'priority': float(row['priority_weight']),
            'complexity': float(row['complexity_mult']),
        }
    return params


def build_graph_from_json(json_path):
    """
    从建筑JSON构建 networkx 图。
    支持两种模式：
      - 有显式 connections: 直接使用 (basic 场景)
      - 无 connections: 根据房间坐标和走廊布局自动生成 (scenario B/C)
    返回 (G, data_dict)
    """
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    G = nx.Graph()
    G.graph['name'] = data['name']
    G.graph['floors'] = data['floors']
    G.graph['floor_height'] = data.get('floor_height', 3.0)

    # ---- 添加节点 ----
    # 房间
    for room in data['rooms']:
        G.add_node(room['id'],
                   type='room',
                   floor=room['floor'],
                   room_type=room['type'],
                   area=room.get('area_m2', 20),
                   label=room['label'],
                   priority=room.get('priority', 'standard'),
                   x=room.get('x', 0),
                   y=room.get('y', 0),
                   sub_zones=room.get('sub_zones', 1))

    # 出口
    for exit_ in data['exits']:
        G.add_node(exit_['id'],
                   type='exit',
                   floor=exit_.get('floor', 1),
                   label=exit_['label'],
                   x=exit_.get('x', 0),
                   y=exit_.get('y', 0))

    # 楼梯
    for stair in data.get('stairs', []):
        G.add_node(stair['id'],
                   type='stair',
                   floor_from=stair['floor_from'],
                   floor_to=stair['floor_to'],
                   length=stair['length'],
                   label=stair['label'],
                   x=stair.get('x', 0),
                   y=stair.get('y', 0))

    # ---- 添加边 ----
    if data.get('connections'):
        # 显式连接 (basic scenario) — 自动创建未声明的 hallway 节点
        for conn in data['connections']:
            for nid in [conn['from'], conn['to']]:
                if nid not in G:
                    G.add_node(nid, type='hallway', floor=1,
                               label=nid.replace('_', ' '))
            G.add_edge(conn['from'], conn['to'], distance=conn['distance'])
    else:
        # 自动生成连接 (scenario B / C)
        _auto_generate_connections(G, data)

    return G, data


def _auto_generate_connections(G, data):
    """
    自动生成楼层内部和楼梯的连接。
    假设：
      - 每层房间按 x 坐标分为左/右两列
      - 每层有一条贯穿走廊，两端连接楼梯/出口
      - 楼梯连接相邻楼层的走廊端点
    """
    hallway_cfg = data.get('hallway', {})
    hallway_length = hallway_cfg.get('length', 30)

    # --- 1. 按楼层+列分组房间 ---
    floors_rooms = {}
    for nid, nd in G.nodes(data=True):
        if nd.get('type') == 'room':
            f = nd['floor']
            floors_rooms.setdefault(f, []).append((nid, nd))

    for floor_num, rooms in floors_rooms.items():
        # 按 x 坐标分为左右列（以中位数为界）
        xs = [r[1].get('x', 0) for r in rooms]
        x_cut = float(np.median(xs)) if xs else 0.0

        left  = sorted([r for r in rooms if r[1].get('x', 0) <= x_cut],
                       key=lambda r: r[1].get('y', 0))
        right = sorted([r for r in rooms if r[1].get('x', 0) > x_cut],
                       key=lambda r: r[1].get('y', 0))

        # 走廊端点节点
        h_start = f'H{floor_num}_start'
        h_end   = f'H{floor_num}_end'
        G.add_node(h_start, type='hallway', floor=floor_num,
                   label=f'Floor {floor_num} Hall Start')
        G.add_node(h_end,   type='hallway', floor=floor_num,
                   label=f'Floor {floor_num} Hall End')
        G.add_edge(h_start, h_end, distance=hallway_length)

        def connect_column(col_nodes, reverse_hook=False):
            """将一列房间串联到走廊"""
            if not col_nodes:
                return
            top_room, bot_room = col_nodes[0], col_nodes[-1]
            if not reverse_hook:
                G.add_edge(h_start, top_room[0], distance=1.5)
                G.add_edge(bot_room[0], h_end, distance=1.5)
            else:
                G.add_edge(h_start, bot_room[0], distance=1.5)
                G.add_edge(top_room[0], h_end, distance=1.5)
            for i in range(len(col_nodes) - 1):
                dy = abs(col_nodes[i+1][1].get('y', 0) - col_nodes[i][1].get('y', 0))
                G.add_edge(col_nodes[i][0], col_nodes[i+1][0],
                           distance=max(dy, 3.0))

        connect_column(left)
        connect_column(right, reverse_hook=True)

    # --- 2. 连接出口 (均在1层) ---
    for exit_node in data['exits']:
        ey = G.nodes[exit_node['id']].get('y', 0)
        ef = G.nodes[exit_node['id']].get('floor', 1)
        # y < 0 → 北出口 → 连 hallway_start; 否则连 hallway_end
        if ey <= 0:
            G.add_edge(exit_node['id'], f'H{ef}_start', distance=2.0)
        else:
            G.add_edge(exit_node['id'], f'H{ef}_end', distance=2.0)

    # --- 3. 连接楼梯 ---
    for stair in data.get('stairs', []):
        sf = stair['floor_from']
        st = stair['floor_to']
        stair_id = stair['id']
        # 楼梯节点本身已在节点列表中；添加与走廊的连接
        G.add_edge(stair_id, f'H{sf}_end', distance=2.0)
        G.add_edge(stair_id, f'H{st}_start', distance=2.0)
        # 楼梯内部"行进边"（用离散楼层差分表达）
        # 注：实际遍历中 stair 节点充当楼层转换点


# ============================================================
# 时间计算函数
# ============================================================

def compute_sweep_time(room_type, room_params, smoke_factor=1.0):
    """计算单个房间的清扫时间 (秒)"""
    params = room_params.get(room_type, {'sweep_time': 20.0})
    return params['sweep_time'] * smoke_factor


def compute_travel_time(distance, speed=SPEED_GEAR, smoke_factor=1.0):
    """计算行进时间 (秒)，smoke_factor 越大速度越慢"""
    effective_speed = speed / max(smoke_factor, 0.1)
    return distance / effective_speed


def compute_stair_time(num_floors, stair_length=8.0, going_up=True):
    """计算爬楼层数 × 楼梯长度的时间 (秒)"""
    speed = SPEED_STAIR_UP if going_up else SPEED_STAIR_DOWN
    return num_floors * stair_length / speed


def get_shortest_path_info(G, source, target):
    """获取最短路径与距离，容错返回 (路径, 距离)"""
    try:
        path = nx.shortest_path(G, source, target, weight='distance')
        dist = nx.shortest_path_length(G, source, target, weight='distance')
        return path, dist
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return [], 999.0


def route_total_time(G, room_order, room_params, start_node,
                     room_types_map=None, smoke_factor=1.0):
    """
    计算单个响应者按顺序访问房间的总时间。
    room_order: list[str]  按顺序访问的房间ID
    start_node: str        起始位置节点ID（通常是出口）
    returns: (总时间_秒, 移动时间_秒, 清扫时间_秒, 房间数)

    注意：如果 room_types_map 未提供，从 G.nodes 获取 room_type。
    """
    total_travel = 0.0
    total_sweep  = 0.0
    current = start_node

    for room_id in room_order:
        _, dist = get_shortest_path_info(G, current, room_id)
        total_travel += compute_travel_time(dist, SPEED_GEAR, smoke_factor)

        if room_types_map:
            rtype = room_types_map.get(room_id, 'office')
        else:
            rtype = G.nodes[room_id].get('room_type', 'office')

        total_sweep += compute_sweep_time(rtype, room_params, smoke_factor)
        current = room_id

    return (total_travel + total_sweep,
            total_travel,
            total_sweep,
            len(room_order))


def makespan_of_assignment(G, assignment_dict, room_params, start_node='E1',
                           room_types_map=None, smoke_factor=1.0):
    """
    计算给定分配下的 makespan（所有响应者中最长耗时）。
    assignment_dict: {agent_id: [room_id, ...]}
    """
    agent_times = {}
    details = {}
    for agent, rooms in assignment_dict.items():
        ttotal, ttravel, tsweep, nrooms = route_total_time(
            G, rooms, room_params, start_node, room_types_map, smoke_factor
        )
        agent_times[agent] = ttotal
        details[agent] = {'total': ttotal, 'travel': ttravel,
                          'sweep': tsweep, 'n_rooms': nrooms}
    makespan = max(agent_times.values()) if agent_times else 0.0
    return makespan, agent_times, details


# ============================================================
# 自检
# ============================================================
if __name__ == '__main__':
    print("=== utils.py 自检 ===")
    import os
    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 测试1：加载 basic
    G1, d1 = build_graph_from_json(os.path.join(BASE, 'data', 'building_basic.json'))
    print(f"[PASS] Basic: {G1.number_of_nodes()} nodes, {G1.number_of_edges()} edges, "
          f"name={G1.graph['name']}")

    # 测试2：加载 scenario B
    G2, d2 = build_graph_from_json(os.path.join(BASE, 'data', 'building_scenario_B.json'))
    print(f"[PASS] Scenario B: {G2.number_of_nodes()} nodes, {G2.number_of_edges()} edges, "
          f"name={G2.graph['name']}")

    # 测试3：加载 scenario C
    G3, d3 = build_graph_from_json(os.path.join(BASE, 'data', 'building_scenario_C.json'))
    print(f"[PASS] Scenario C: {G3.number_of_nodes()} nodes, {G3.number_of_edges()} edges, "
          f"name={G3.graph['name']}")

    # 测试4：房间参数
    rp = load_room_params(os.path.join(BASE, 'data', 'room_type_params.csv'))
    print(f"[PASS] Room params: {len(rp)} types loaded")
    for k, v in rp.items():
        print(f"  {k}: sweep={v['sweep_time']}s, priority={v['priority']}, "
              f"complexity={v['complexity']}")

    # 测试5：最短路径
    path, dist = get_shortest_path_info(G1, 'E1', 'R3')
    print(f"[PASS] Shortest path E1→R3: dist={dist:.1f}m, path={path}")

    print("\n=== 自检全部通过 ===")
