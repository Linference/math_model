"""
问题3 — 场景B和C的多响应者清扫调度 (优化版)
模型: 多响应者VRP, makespan最小化
算法: GA (OX交叉 + 交换变异, 种群100, 300代) + ACO对照
      扫描响应者数量 [2, 3, 4, 6, 8] 找最优
优化: 使用贪心分割解码 (O(n*m)) 替代全枚举分割 (O(C(n-1,m-1)))
随机种子: 42
"""

import numpy as np
import json
import os
import sys
import time
import random
from copy import deepcopy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (build_graph_from_json, load_room_params,
                   route_total_time, get_shortest_path_info,
                   compute_sweep_time, compute_travel_time,
                   compute_stair_time, SPEED_GEAR, SPEED_STAIR_UP, SPEED_STAIR_DOWN)

np.random.seed(42)
random.seed(42)


# ============================================================
# 距离缓存
# ============================================================

class DistanceCache:
    """缓存节点间距离"""
    def __init__(self, G, room_ids, start_node='E1'):
        self.G = G
        self.nodes = [start_node] + room_ids
        self.n2i = {n: i for i, n in enumerate(self.nodes)}
        n = len(self.nodes)
        self.dist = np.zeros((n, n))
        for i, u in enumerate(self.nodes):
            for j, v in enumerate(self.nodes):
                if i == j:
                    continue
                _, d = get_shortest_path_info(G, u, v)
                self.dist[i, j] = d

    def distance(self, u, v):
        return self.dist[self.n2i[u], self.n2i[v]]


# ============================================================
# GA 求解器 (贪心分割)
# ============================================================

class GA_VRP_Solver:
    """
    遗传算法 + 贪心分割解码。
    染色体: 所有房间的一个排列。
    解码: 顺序扫描排列，将每个房间贪婪分配给当前累计时间最小的agent。
    """

    def __init__(self, G, room_ids, room_params, room_types_map,
                 n_agents, start_node='E1',
                 pop_size=100, n_generations=300,
                 crossover_rate=0.85, mutation_rate=0.15,
                 elite_size=5, smoke_factor=1.0):
        self.G = G
        self.room_ids = list(room_ids)
        self.n_rooms = len(self.room_ids)
        self.room_params = room_params
        self.room_types_map = room_types_map
        self.n_agents = n_agents
        self.start_node = start_node
        self.pop_size = pop_size
        self.n_generations = n_generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.smoke_factor = smoke_factor

        self.dist_cache = DistanceCache(G, self.room_ids, start_node)

        # 预计算清扫时间
        self.sweep_times = {}
        for rid in self.room_ids:
            rtype = room_types_map.get(rid, 'office')
            self.sweep_times[rid] = compute_sweep_time(rtype, room_params, smoke_factor)

        # 收敛记录
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.elapsed = 0.0
        self.best_makespan = float('inf')
        self.best_assignment = {}

    def _greedy_decode(self, chromosome):
        """
        贪心分割: 顺序扫描排列，将房间分配给当前累计时间最小的agent。
        时间复杂度: O(n_rooms * n_agents)
        """
        agent_routes = {a: [] for a in range(self.n_agents)}
        agent_last = {a: self.start_node for a in range(self.n_agents)}
        agent_time = {a: 0.0 for a in range(self.n_agents)}

        for rid in chromosome:
            best_agent = None
            best_new_time = float('inf')

            for a in range(self.n_agents):
                # 从agent当前位置到rid的距离
                travel_dist = self.dist_cache.distance(agent_last[a], rid)
                travel_t = compute_travel_time(travel_dist, SPEED_GEAR, self.smoke_factor)
                sweep_t = self.sweep_times.get(rid, 20.0)
                new_time = agent_time[a] + travel_t + sweep_t

                if new_time < best_new_time:
                    best_new_time = new_time
                    best_agent = a

            agent_routes[best_agent].append(rid)
            agent_last[best_agent] = rid
            agent_time[best_agent] = best_new_time

        makespan = max(agent_time.values()) if agent_time else 0.0
        return agent_routes, makespan

    def _fitness(self, chromosome):
        """适应度 = -makespan (越小越好)"""
        _, mk = self._greedy_decode(chromosome)
        return -mk

    def _create_individual(self):
        """随机排列"""
        perm = list(self.room_ids)
        random.shuffle(perm)
        return perm

    def _order_crossover(self, p1, p2):
        """Order Crossover (OX)"""
        n = len(p1)
        i, j = sorted(random.sample(range(n), 2))
        c1, c2 = [-1] * n, [-1] * n
        c1[i:j+1] = p1[i:j+1]
        c2[i:j+1] = p2[i:j+1]

        def fill_child(child, parent, donor):
            donor_set = set(donor[i:j+1])
            pos = (j + 1) % n
            p_pos = (j + 1) % n
            while -1 in child:
                if parent[p_pos] not in donor_set:
                    child[pos] = parent[p_pos]
                    pos = (pos + 1) % n
                p_pos = (p_pos + 1) % n
            return child

        c1 = fill_child(c1, p2, p1)
        c2 = fill_child(c2, p1, p2)
        return c1, c2

    def _swap_mutation(self, chrom):
        """交换变异"""
        i, j = random.sample(range(len(chrom)), 2)
        chrom[i], chrom[j] = chrom[j], chrom[i]
        return chrom

    def _inversion_mutation(self, chrom):
        """反转变异"""
        i, j = sorted(random.sample(range(len(chrom)), 2))
        chrom[i:j+1] = reversed(chrom[i:j+1])
        return chrom

    def solve(self, verbose=True):
        """运行GA优化"""
        t0 = time.time()

        # 初始化种群
        pop = [self._create_individual() for _ in range(self.pop_size)]
        fitness = [self._fitness(ind) for ind in pop]

        best_idx = np.argmax(fitness)
        best_chrom = deepcopy(pop[best_idx])
        best_fitness = fitness[best_idx]

        for gen in range(self.n_generations):
            # 精英保留
            elite_indices = np.argsort(fitness)[-self.elite_size:]
            new_pop = [deepcopy(pop[ei]) for ei in elite_indices]

            # 生成新个体
            while len(new_pop) < self.pop_size:
                # 锦标赛选择
                t_idx = [random.randint(0, self.pop_size - 1) for _ in range(4)]
                p1 = pop[t_idx[0]] if fitness[t_idx[0]] >= fitness[t_idx[1]] else pop[t_idx[1]]
                p2 = pop[t_idx[2]] if fitness[t_idx[2]] >= fitness[t_idx[3]] else pop[t_idx[3]]

                if random.random() < self.crossover_rate:
                    c1, c2 = self._order_crossover(p1, p2)
                else:
                    c1, c2 = deepcopy(p1), deepcopy(p2)

                if random.random() < self.mutation_rate:
                    c1 = self._swap_mutation(c1)
                if random.random() < self.mutation_rate:
                    c2 = self._inversion_mutation(c2)

                new_pop.append(c1)
                if len(new_pop) < self.pop_size:
                    new_pop.append(c2)

            pop = new_pop[:self.pop_size]
            fitness = [self._fitness(ind) for ind in pop]

            gen_best_idx = np.argmax(fitness)
            if fitness[gen_best_idx] > best_fitness:
                best_fitness = fitness[gen_best_idx]
                best_chrom = deepcopy(pop[gen_best_idx])

            self.best_fitness_history.append(-best_fitness)
            self.avg_fitness_history.append(-np.mean(fitness))

            if verbose and (gen % 50 == 0 or gen == self.n_generations - 1):
                print(f"  Gen {gen:4d}: best={-best_fitness:.1f}s, avg={-np.mean(fitness):.1f}s")

        self.elapsed = time.time() - t0
        self.best_assignment, self.best_makespan = self._greedy_decode(best_chrom)
        return self.best_makespan, self.best_assignment


# ============================================================
# ACO 对照组 (同样使用贪心分割)
# ============================================================

class ACO_VRP_Solver:
    """蚁群算法 + 贪心分割"""

    def __init__(self, G, room_ids, room_params, room_types_map,
                 n_agents, start_node='E1',
                 n_ants=50, n_iterations=200,
                 alpha=1.0, beta=2.0, rho=0.1, Q=100, smoke_factor=1.0):
        self.G = G
        self.room_ids = list(room_ids)
        self.n_rooms = len(self.room_ids)
        self.room_params = room_params
        self.room_types_map = room_types_map
        self.n_agents = n_agents
        self.start_node = start_node
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.Q = Q
        self.smoke_factor = smoke_factor

        self.dist_cache = DistanceCache(G, self.room_ids, start_node)

        # 预计算清扫时间
        self.sweep_times = {}
        for rid in self.room_ids:
            rtype = room_types_map.get(rid, 'office')
            self.sweep_times[rid] = compute_sweep_time(rtype, room_params, smoke_factor)

        # 信息素
        tau0 = 1.0 / (self.n_rooms * 100)
        self.pheromone = np.full((self.n_rooms, self.n_rooms), tau0)

        self.best_fitness_history = []
        self.elapsed = 0.0
        self.best_makespan = float('inf')
        self.best_assignment = {}

    def _greedy_decode(self, perm):
        """贪心分割 (同GA)"""
        agent_routes = {a: [] for a in range(self.n_agents)}
        agent_last = {a: self.start_node for a in range(self.n_agents)}
        agent_time = {a: 0.0 for a in range(self.n_agents)}

        for rid in perm:
            best_agent = None
            best_new_time = float('inf')
            for a in range(self.n_agents):
                travel_dist = self.dist_cache.distance(agent_last[a], rid)
                travel_t = compute_travel_time(travel_dist, SPEED_GEAR, self.smoke_factor)
                new_time = agent_time[a] + travel_t + self.sweep_times.get(rid, 20.0)
                if new_time < best_new_time:
                    best_new_time = new_time
                    best_agent = a
            agent_routes[best_agent].append(rid)
            agent_last[best_agent] = rid
            agent_time[best_agent] = best_new_time

        makespan = max(agent_time.values()) if agent_time else 0.0
        return agent_routes, makespan

    def _construct_solution(self):
        """基于信息素的概率构造排列"""
        unvisited = list(range(self.n_rooms))
        random.shuffle(unvisited)
        solution = []
        current = random.choice(unvisited)
        solution.append(current)
        unvisited.remove(current)

        while unvisited:
            probs = []
            for j in unvisited:
                tau = self.pheromone[current, j] ** self.alpha
                eta = (1.0 / max(self.dist_cache.dist[current + 1, j + 1], 0.1)) ** self.beta
                probs.append(tau * eta)
            probs = np.array(probs, dtype=float)
            p_sum = probs.sum()
            if p_sum < 1e-15:
                probs = np.ones(len(unvisited)) / len(unvisited)
            else:
                probs = probs / p_sum

            next_idx = np.random.choice(unvisited, p=probs)
            solution.append(next_idx)
            current = next_idx
            unvisited.remove(current)

        return [self.room_ids[i] for i in solution]

    def solve(self, verbose=True):
        t0 = time.time()
        best_mk = float('inf')
        best_sol = None

        for it in range(self.n_iterations):
            for _ in range(self.n_ants):
                perm = self._construct_solution()
                routes, mk = self._greedy_decode(perm)

                if mk < best_mk:
                    best_mk = mk
                    best_sol = (perm, routes)

                # 信息素更新
                idxs = [self.room_ids.index(r) for r in perm]
                delta = self.Q / max(mk, 0.1)
                for k in range(len(idxs) - 1):
                    self.pheromone[idxs[k], idxs[k+1]] += delta

            # 蒸发
            self.pheromone *= (1 - self.rho)

            self.best_fitness_history.append(best_mk)
            if verbose and (it % 50 == 0 or it == self.n_iterations - 1):
                print(f"  ACO Iter {it:4d}: best={best_mk:.1f}s")

        self.elapsed = time.time() - t0
        self.best_makespan = best_mk
        self.best_assignment = best_sol[1] if best_sol else {}
        return self.best_makespan, self.best_assignment


# ============================================================
# 扫描响应者数量
# ============================================================

def scan_agents(G, room_params, room_types_map, scenario_name,
                agent_counts=[2, 3, 4, 6, 8],
                ga_pop=100, ga_gen=300, output_dir=None):
    """扫描不同响应者数量"""
    room_ids = [n for n, d in G.nodes(data=True) if d.get('type') == 'room']
    n_rooms = len(room_ids)
    print(f"\n{'='*60}")
    print(f"  {scenario_name}: {n_rooms} 房间, {G.graph['floors']} 层")
    print(f"{'='*60}")

    results = {}
    for n_agents in agent_counts:
        if n_agents > n_rooms:
            n_agents = n_rooms  # 不超过房间数

        t_start = time.time()
        print(f"\n--- 响应者数量 = {n_agents} ---")

        # GA
        ga = GA_VRP_Solver(G, room_ids, room_params, room_types_map,
                           n_agents=n_agents, pop_size=ga_pop,
                           n_generations=ga_gen, smoke_factor=1.0)
        ga_mk, ga_asgn = ga.solve(verbose=True)

        # ACO
        aco = ACO_VRP_Solver(G, room_ids, room_params, room_types_map,
                             n_agents=n_agents, n_ants=50, n_iterations=200)
        aco_mk, aco_asgn = aco.solve(verbose=True)

        results[n_agents] = {
            'n_rooms': n_rooms,
            'GA_makespan_s': round(ga_mk, 2),
            'GA_makespan_min': round(ga_mk / 60, 2),
            'GA_time_s': round(ga.elapsed, 2),
            'ACO_makespan_s': round(aco_mk, 2),
            'ACO_makespan_min': round(aco_mk / 60, 2),
            'ACO_time_s': round(aco.elapsed, 2),
            'GA_convergence': [round(v, 2) for v in ga.best_fitness_history],
            'ACO_convergence': [round(v, 2) for v in aco.best_fitness_history],
            'GA_best_routes': {str(k): v for k, v in ga.best_assignment.items()},
        }

        elapsed_i = time.time() - t_start
        print(f"  >> GA={ga_mk:.1f}s, ACO={aco_mk:.1f}s, 耗时={elapsed_i:.1f}s")

    # 保存
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        fname = f'q3_{scenario_name.lower().replace(" ", "_").replace(":", "")}_scan.json'
        fpath = os.path.join(output_dir, fname)
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n  扫描结果已保存: {fpath}")

    return results


def print_best_solution(G, room_params, room_types_map, n_agents,
                        makespan, assignment, scenario_name, start_node='E1'):
    """打印最优解详情"""
    print(f"\n{'─'*50}")
    print(f"  {scenario_name} 最优解 (n_agents={n_agents})")
    print(f"  Makespan = {makespan:.1f} s = {makespan/60:.2f} min")
    print(f"{'─'*50}")
    for agent, route in sorted(assignment.items()):
        ttotal, ttravel, tsweep, nrooms = route_total_time(
            G, route, room_params, start_node, room_types_map
        )
        floors_covered = set()
        for rid in route:
            floors_covered.add(G.nodes[rid].get('floor', 1))
        print(f"  Agent {int(agent)+1}: {route}")
        print(f"    T={ttotal:.1f}s (travel={ttravel:.1f}s, sweep={tsweep:.1f}s), "
              f"floors={sorted(floors_covered)}, rooms={nrooms}")


# ============================================================
# 主程序
# ============================================================
if __name__ == '__main__':
    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT = os.path.join(BASE, 'code', 'outputs')
    os.makedirs(OUTPUT, exist_ok=True)

    print("=" * 60)
    print("  Q3: 场景B和C — GA + ACO 多响应者调度 (优化版)")
    print("=" * 60)

    room_params = load_room_params(os.path.join(BASE, 'data', 'room_type_params.csv'))

    # ==================== 场景 B ====================
    GB, dataB = build_graph_from_json(os.path.join(BASE, 'data', 'building_scenario_B.json'))
    rtmB = {n: d['room_type'] for n, d in GB.nodes(data=True) if d.get('type') == 'room'}
    room_idsB = [n for n, d in GB.nodes(data=True) if d.get('type') == 'room']
    print(f"\n场景B: {len(room_idsB)} rooms, {GB.graph['floors']} floors, "
          f"{len(dataB.get('stairs',[]))} stairs")
    print(f"  房间: {room_idsB}")

    resultsB = scan_agents(GB, room_params, rtmB, 'Scenario_B',
                           agent_counts=[2, 3, 4, 6],
                           ga_pop=100, ga_gen=300, output_dir=OUTPUT)

    # 推荐4 agent的详细解
    ga4 = GA_VRP_Solver(GB, room_idsB, room_params, rtmB, n_agents=4,
                        pop_size=100, n_generations=300)
    mk4, asgn4 = ga4.solve(verbose=False)
    print_best_solution(GB, room_params, rtmB, 4, mk4, asgn4, 'Scenario B')

    # ==================== 场景 C ====================
    GC, dataC = build_graph_from_json(os.path.join(BASE, 'data', 'building_scenario_C.json'))
    rtmC = {n: d['room_type'] for n, d in GC.nodes(data=True) if d.get('type') == 'room'}
    room_idsC = [n for n, d in GC.nodes(data=True) if d.get('type') == 'room']
    print(f"\n场景C: {len(room_idsC)} rooms, {GC.graph['floors']} floors, "
          f"{len(dataC.get('stairs',[]))} stairs")
    print(f"  房间: {room_idsC}")

    resultsC = scan_agents(GC, room_params, rtmC, 'Scenario_C',
                           agent_counts=[2, 3, 4, 6, 8],
                           ga_pop=100, ga_gen=300, output_dir=OUTPUT)

    # 推荐6 agent的详细解
    ga6 = GA_VRP_Solver(GC, room_idsC, room_params, rtmC, n_agents=6,
                        pop_size=100, n_generations=300)
    mk6, asgn6 = ga6.solve(verbose=False)
    print_best_solution(GC, room_params, rtmC, 6, mk6, asgn6, 'Scenario C')

    # ==================== 汇总 ====================
    print("\n" + "=" * 60)
    print("  Q3 汇总")
    print("=" * 60)
    for sname, results in [('Scenario B', resultsB), ('Scenario C', resultsC)]:
        print(f"\n{sname}:")
        for n in sorted(results.keys()):
            r = results[n]
            print(f"  n={n}: GA={r['GA_makespan_s']:.1f}s ({r['GA_makespan_min']:.1f}min), "
                  f"ACO={r['ACO_makespan_s']:.1f}s ({r['ACO_makespan_min']:.1f}min), "
                  f"GA耗时={r['GA_time_s']:.1f}s")

    print("\n[Q3] 完成.")
