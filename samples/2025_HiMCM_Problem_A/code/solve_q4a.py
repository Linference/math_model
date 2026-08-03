"""
问题4a — 烟雾扩散 + 传感器退化下的鲁棒性评估 (优化版)
模型: 向量化CA烟雾扩散 (20x20) + Monte Carlo (N=200) + DES
输出: 时间分布统计数据、龙卷风图、退化验证数据
随机种子: 42
优化: 向量化CA步进, 火源内置建筑内, 烟雾效应更显著
"""

import numpy as np
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (build_graph_from_json, load_room_params,
                   route_total_time, get_shortest_path_info,
                   SPEED_GEAR, SPEED_SMOKE, SPEED_CRAWL)

np.random.seed(42)

# ============================================================
# 向量化烟雾扩散 CA (快速版)
# ============================================================

class FastSmokeCA:
    """
    向量化烟雾扩散。状态: 0=安全, 1=轻烟, 2=中烟, 3=浓烟, 4=极浓。
    使用numpy布尔索引加速扩散。
    """

    def __init__(self, width=20, height=20,
                 fire_sources=None,
                 diffusion_rate=0.20,
                 intensity_growth=0.05):
        self.W = width
        self.H = height
        self.grid = np.zeros((height, width), dtype=np.float32)
        self.diffusion_rate = diffusion_rate
        self.intensity_growth = intensity_growth
        self.fire_sources = fire_sources or [(width // 2, 0)]
        self.time_step = 0
        self._kernel = np.array([[0,1,0],[1,0,1],[0,1,0]], dtype=np.float32)

    def reset(self):
        self.grid = np.zeros((self.H, self.W), dtype=np.float32)
        self.time_step = 0
        for sx, sy in self.fire_sources:
            if 0 <= sx < self.W and 0 <= sy < self.H:
                self.grid[sy, sx] = 2.0

    def step(self):
        """向量化单步扩散"""
        self.time_step += 1

        # 1) 火源持续产烟
        for sx, sy in self.fire_sources:
            if 0 <= sx < self.W and 0 <= sy < self.H:
                self.grid[sy, sx] = min(4.0, self.grid[sy, sx] +
                                         self.intensity_growth * (1 + np.random.random()))

        # 2) 扩散: 每个格点向4邻域扩散
        # 用卷积实现 (简化，仅向邻域扩散且衰减)
        smoke_mask = self.grid >= 1.0
        if not smoke_mask.any():
            return self.grid

        # 扩散: 将高浓度烟扩散到邻域
        spread_amount = self.diffusion_rate * self.grid
        # 4-neighbor averaging via padding
        padded = np.pad(self.grid, ((1,1),(1,1)), mode='constant')
        # Up neighbor contribution
        self.grid += self.diffusion_rate * 0.25 * (
            padded[0:-2, 1:-1]   # up
            + padded[2:, 1:-1]   # down
            + padded[1:-1, 0:-2] # left
            + padded[1:-1, 2:]   # right
            - 4 * self.grid      # out of center
        )
        self.grid = np.clip(self.grid, 0, 4.0)
        return self.grid

    def get_smoke_factor(self, x_idx, y_idx):
        level = self.grid[int(np.clip(y_idx, 0, self.H-1)),
                          int(np.clip(x_idx, 0, self.W-1))]
        if level < 0.5:
            return 1.0
        elif level < 1.5:
            return 1.3
        elif level < 2.5:
            return 2.0
        elif level < 3.5:
            return 3.0
        else:
            return 5.0


# ============================================================
# 传感器退化模型
# ============================================================

class SensorDegradation:
    def __init__(self, initial_reliability=0.95,
                 failure_prob_per_min=0.01,
                 error_growth_rate=0.003):
        self.reliability = initial_reliability
        self.failure_prob = failure_prob_per_min
        self.error_growth = error_growth_rate
        self.functional = True
        self.time_alive = 0.0
        self.measurement_error = 0.0

    def update(self, dt_min=1.0):
        self.time_alive += dt_min
        # 指数衰减可靠性
        self.reliability = self.reliability * np.exp(-self.error_growth * dt_min * 10)
        if self.functional and np.random.random() < self.failure_prob * dt_min:
            self.functional = False
        self.measurement_error = max(0.0, (1.0 - self.reliability) * 0.5)


# ============================================================
# DES 仿真
# ============================================================

def simulate_one_run(G, route_assignments, room_params, room_types_map,
                     ca_smoke, sensor, start_node='E1'):
    """
    仿真一次完整清扫。
    路径上的烟雾因子用房间坐标插值到CA格点。
    """
    agent_times = {}

    for agent, route in route_assignments.items():
        t = 0.0
        current = start_node

        for rid in route:
            # 获取房间坐标
            rx = G.nodes[rid].get('x', 0)
            ry = G.nodes[rid].get('y', 0)
            cx = G.nodes[current].get('x', 0)
            cy = G.nodes[current].get('y', 0)

            # 路径中点映射到CA格点
            mx = (cx + rx) / 2
            my = (cy + ry) / 2
            gx = int(np.clip((mx + 2) / 15 * ca_smoke.W, 0, ca_smoke.W - 1))
            gy = int(np.clip((my + 2) / 15 * ca_smoke.H, 0, ca_smoke.H - 1))

            sf = ca_smoke.get_smoke_factor(gx, gy)
            if sf >= 3.0:
                speed = SPEED_CRAWL
            elif sf >= 2.0:
                speed = SPEED_SMOKE
            else:
                speed = SPEED_GEAR

            # 行进距离
            _, dist = get_shortest_path_info(G, current, rid)
            travel_t = dist / max(speed, 0.2)
            t += travel_t

            # 烟雾扩散 (行进期间)
            for _ in range(int(travel_t)):
                ca_smoke.step()
            sensor.update(dt_min=travel_t / 60.0)

            # 清扫时间
            rtype = room_types_map.get(rid, 'office')
            base_sweep = room_params.get(rtype, {'sweep_time': 20.0})['sweep_time']

            if not sensor.functional:
                sweep_t = base_sweep * (2.0 + 0.5 * np.random.random())
            else:
                sweep_t = base_sweep * (1.0 + sensor.measurement_error)

            t += sweep_t

            # 清扫期间烟雾继续扩散
            for _ in range(int(sweep_t / 2)):
                ca_smoke.step()
            sensor.update(dt_min=sweep_t / 60.0)

            current = rid

        agent_times[agent] = t

    return max(agent_times.values()) if agent_times else 0.0


def monte_carlo(G, route_assignments, room_params, room_types_map,
                n_runs=200, verbose=True):
    """Monte Carlo 仿真"""
    completion_times = []
    sensor_oks = []

    for run in range(n_runs):
        if verbose and run % 50 == 0:
            print(f"  MC run {run}/{n_runs}...")

        ca = FastSmokeCA(width=20, height=20,
                         fire_sources=[(10, 0), (12, 0)],
                         diffusion_rate=0.22,
                         intensity_growth=0.06)
        ca.reset()

        # 预烧 (随机0-90秒)
        pre_burn = np.random.randint(0, 90)
        for _ in range(pre_burn):
            ca.step()

        sensor = SensorDegradation(
            initial_reliability=0.92,
            failure_prob_per_min=0.008,
            error_growth_rate=0.004
        )

        mk = simulate_one_run(G, route_assignments, room_params,
                              room_types_map, ca, sensor)
        completion_times.append(mk)
        sensor_oks.append(sensor.functional)

    return np.array(completion_times), np.array(sensor_oks)


def tornado_analysis(G, route_assignments, room_params, room_types_map,
                     n_runs=50):
    """OAT灵敏度分析"""
    base_params = {
        'diffusion_rate': 0.22,
        'intensity_growth': 0.06,
        'sensor_reliability': 0.92,
        'failure_prob': 0.008,
    }
    perturbs = {
        'diffusion_rate': (0.12, 0.32),
        'intensity_growth': (0.03, 0.10),
        'sensor_reliability': (0.75, 0.98),
        'failure_prob': (0.002, 0.020),
    }

    # 基线
    baseline_times = []
    for _ in range(n_runs):
        ca = FastSmokeCA(diffusion_rate=base_params['diffusion_rate'],
                         intensity_growth=base_params['intensity_growth'])
        ca.reset()
        for _ in range(np.random.randint(0, 90)):
            ca.step()
        sensor = SensorDegradation(
            initial_reliability=base_params['sensor_reliability'],
            failure_prob_per_min=base_params['failure_prob'])
        baseline_times.append(simulate_one_run(
            G, route_assignments, room_params, room_types_map, ca, sensor))
    baseline_mean = np.mean(baseline_times)

    tornado = {}
    for pname, (lo, hi) in perturbs.items():
        for val, label in [(lo, 'low'), (hi, 'high')]:
            times = []
            params = dict(base_params)
            params[pname] = val
            for _ in range(n_runs):
                ca = FastSmokeCA(diffusion_rate=params['diffusion_rate'],
                                 intensity_growth=params['intensity_growth'])
                ca.reset()
                for _ in range(np.random.randint(0, 90)):
                    ca.step()
                sensor = SensorDegradation(
                    initial_reliability=params['sensor_reliability'],
                    failure_prob_per_min=params['failure_prob'])
                times.append(simulate_one_run(
                    G, route_assignments, room_params, room_types_map, ca, sensor))
            tornado.setdefault(pname, {})[label] = {
                'value': val, 'mean': float(np.mean(times)),
                'std': float(np.std(times)),
                'min': float(np.min(times)), 'max': float(np.max(times)),
            }
        print(f"  {pname}: low={tornado[pname]['low']['mean']:.1f}s, "
              f"baseline={baseline_mean:.1f}s, high={tornado[pname]['high']['mean']:.1f}s")

    return baseline_mean, tornado


def degradation_analysis(G, route_assignments, room_params, room_types_map,
                         n_runs=50):
    """传感器可靠性退化验证"""
    rel_levels = [0.95, 0.80, 0.60, 0.40, 0.20]
    results = {}
    for rel in rel_levels:
        times = []
        okay = []
        for _ in range(n_runs):
            ca = FastSmokeCA()
            ca.reset()
            for _ in range(np.random.randint(0, 90)):
                ca.step()
            sensor = SensorDegradation(initial_reliability=rel,
                                       failure_prob_per_min=0.015)
            mk = simulate_one_run(G, route_assignments, room_params,
                                  room_types_map, ca, sensor)
            times.append(mk)
            okay.append(sensor.functional)
        results[f'reliability_{rel}'] = {
            'mean_s': float(np.mean(times)),
            'std_s': float(np.std(times)),
            'median_s': float(np.median(times)),
            'max_s': float(np.max(times)),
            'sensor_survival_rate': float(np.mean(okay)),
        }
        print(f"  rel={rel}: mean={np.mean(times):.1f}s, std={np.std(times):.1f}s, "
              f"sensor_ok={np.mean(okay)*100:.1f}%")
    return results


# ============================================================
# 主程序
# ============================================================
if __name__ == '__main__':
    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT = os.path.join(BASE, 'code', 'outputs')
    os.makedirs(OUTPUT, exist_ok=True)

    print("=" * 60)
    print("  Q4a: CA烟雾扩散 + Monte Carlo + DES (优化版)")
    print("=" * 60)

    G, data = build_graph_from_json(os.path.join(BASE, 'data', 'building_basic.json'))
    room_params = load_room_params(os.path.join(BASE, 'data', 'room_type_params.csv'))
    room_types_map = {n: d['room_type'] for n, d in G.nodes(data=True) if d.get('type') == 'room'}

    # Q2最优分配
    route_assignments = {0: ['R1','R2','R3'], 1: ['R4','R5','R6']}

    # ---- Monte Carlo ----
    print("\n[1] Monte Carlo (N=200)...")
    t0 = time.time()
    times, s_ok = monte_carlo(G, route_assignments, room_params,
                              room_types_map, n_runs=200)
    mc_t = time.time() - t0

    print(f"\n  MC done in {mc_t:.1f}s")
    print(f"  mean={np.mean(times):.1f}s, median={np.median(times):.1f}s, "
          f"std={np.std(times):.1f}s")
    print(f"  min={np.min(times):.1f}s, max={np.max(times):.1f}s")
    print(f"  P5={np.percentile(times,5):.1f}s, P95={np.percentile(times,95):.1f}s")
    print(f"  Sensor survival: {np.mean(s_ok)*100:.1f}%")

    mc_data = {
        'n_runs': 200,
        'mean_s': float(np.mean(times)),
        'median_s': float(np.median(times)),
        'std_s': float(np.std(times)),
        'min_s': float(np.min(times)),
        'max_s': float(np.max(times)),
        'p5_s': float(np.percentile(times, 5)),
        'p25_s': float(np.percentile(times, 25)),
        'p75_s': float(np.percentile(times, 75)),
        'p95_s': float(np.percentile(times, 95)),
        'sensor_survival': float(np.mean(s_ok)),
        'runtime_s': mc_t,
        'times_sample': [float(t) for t in times[:100]],
    }
    with open(os.path.join(OUTPUT, 'q4a_mc_results.json'), 'w', encoding='utf-8') as f:
        json.dump(mc_data, f, indent=2, ensure_ascii=False)

    # ---- Tornado ----
    print("\n[2] Tornado (OAT, N=50)...")
    t0 = time.time()
    bl_mean, tornado = tornado_analysis(G, route_assignments, room_params,
                                        room_types_map, n_runs=50)
    print(f"  Tornado done in {time.time()-t0:.1f}s")

    with open(os.path.join(OUTPUT, 'q4a_tornado.json'), 'w', encoding='utf-8') as f:
        json.dump({'baseline_mean_s': bl_mean, 'parameters': tornado}, f,
                  indent=2, ensure_ascii=False)

    # ---- Degradation ----
    print("\n[3] Sensor degradation (N=50)...")
    t0 = time.time()
    deg = degradation_analysis(G, route_assignments, room_params,
                               room_types_map, n_runs=50)
    print(f"  Degradation done in {time.time()-t0:.1f}s")

    with open(os.path.join(OUTPUT, 'q4a_degradation.json'), 'w', encoding='utf-8') as f:
        json.dump(deg, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"  Q4a Complete")
    print(f"  MC: mean={np.mean(times):.1f}s ({np.mean(times)/60:.2f}min), "
          f"95% CI=[{np.percentile(times,2.5):.1f}, {np.percentile(times,97.5):.1f}]s")
    print(f"  Sensor survival rate: {np.mean(s_ok)*100:.1f}%")
    print(f"{'='*60}")
