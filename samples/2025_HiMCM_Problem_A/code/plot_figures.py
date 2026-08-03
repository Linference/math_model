"""阶段5: 生成所有论文图表 PNG → figures/"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams.update({'font.size': 11, 'figure.dpi': 150, 'savefig.dpi': 300, 'savefig.bbox': 'tight'})

BASE = "c:/Users/HUAWEI/Desktop/数学建模/samples/2025_HiMCM_Problem_A"
OUT = f"{BASE}/code/outputs"
FIGS = f"{BASE}/figures"
os.makedirs(FIGS, exist_ok=True)

def load_json(name):
    with open(f"{OUT}/{name}") as f:
        return json.load(f)

# ============ Q2 Figures ============
def fig_q2_building_graph():
    """图1: 建筑图G可视化 + 最优路径"""
    fig, ax = plt.subplots(figsize=(10, 6))
    # 房间位置
    rooms_left = {'R1': (2,1), 'R2': (2,4), 'R3': (2,7)}
    rooms_right = {'R4': (8,1), 'R5': (8,4), 'R6': (8,7)}
    exits = {'E1': (5, -1), 'E2': (5, 10)}
    hallway = {'H_N': (5, 0.5), 'H_S': (5, 8.5)}
    all_nodes = {**rooms_left, **rooms_right, **exits, **hallway}
    for name, (x,y) in all_nodes.items():
        color = 'green' if name.startswith('E') else ('lightblue' if name.startswith('R') else 'gray')
        ax.plot(x, y, 's' if name.startswith('R') else 'o', markersize=18 if name.startswith('R') else 14,
                color=color, markeredgecolor='black', markeredgewidth=1.5, zorder=3)
        ax.text(x, y, name, ha='center', va='center', fontsize=8, fontweight='bold')
    # 走廊
    ax.plot([5,5], [0.5, 8.5], 'k--', linewidth=2, alpha=0.4, zorder=1)
    # 最优路径 (红线Agent2左列, 蓝线Agent1右列)
    ax.plot([5,2,2,2], [0.5,1,4,7], 'red', linewidth=3, alpha=0.7, zorder=2, label='Agent 2: R1→R2→R3')
    ax.plot([5,8,8,8], [0.5,1,4,7], 'blue', linewidth=3, alpha=0.7, zorder=2, label='Agent 1: R4→R5→R6')
    ax.set_xlim(0, 10); ax.set_ylim(-2, 11)
    ax.set_title('Figure 1: Building Graph & Optimal Sweep Path (73.5s)', fontweight='bold')
    ax.legend(loc='lower right'); ax.axis('equal')
    fig.savefig(f"{FIGS}/fig_q2_building_graph.png"); plt.close()

def fig_q2_time_breakdown():
    """图2: 时间分解饼图"""
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie([13.5, 60.0], labels=['Travel (18%)', 'Sweep (82%)'],
           colors=['#3498db', '#e74c3c'], autopct='%1.1f%%', startangle=90,
           explode=(0.03, 0), textprops={'fontsize': 13})
    ax.set_title('Time Breakdown per Agent (73.5s total)', fontweight='bold', fontsize=14)
    fig.savefig(f"{FIGS}/fig_q2_time_pie.png"); plt.close()

def fig_q2_sensitivity():
    """图3: 灵敏度分析"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    # Speed
    speeds = [-30, -15, 0, 15, 30]
    times_speed = [79.3, 75.9, 73.5, 71.7, 70.4]
    axes[0].plot(speeds, times_speed, 'o-', linewidth=2, markersize=8, color='#2c3e50')
    axes[0].axhline(73.5, color='red', linestyle='--', alpha=0.5, label='Baseline')
    axes[0].set_xlabel('Speed Change (%)'); axes[0].set_ylabel('Makespan (s)')
    axes[0].set_title('Speed Sensitivity'); axes[0].legend()
    # Smoke
    smokes = [1.0, 1.5, 2.0, 3.0]
    times_smoke = [73.5, 110.2, 147.0, 220.5]
    axes[1].bar([str(s)+'x' for s in smokes], times_smoke, color=['green','yellow','orange','red'])
    axes[1].set_xlabel('Smoke Factor'); axes[1].set_ylabel('Makespan (s)')
    axes[1].set_title('Smoke Impact')
    for i, v in enumerate(times_smoke):
        axes[1].text(i, v+2, f'{v:.0f}s', ha='center', fontweight='bold')
    fig.suptitle('Parameter Sensitivity Analysis', fontweight='bold', fontsize=14)
    fig.tight_layout()
    fig.savefig(f"{FIGS}/fig_q2_sensitivity.png"); plt.close()

# ============ Q3 Figures ============
def fig_q3_convergence():
    """图4: GA收敛曲线"""
    b = load_json("q3_scenario_b_scan.json")
    c = load_json("q3_scenario_c_scan.json")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, data, title in [(axes[0], b, 'Scenario B (2 floors, 11 rooms)'),
                              (axes[1], c, 'Scenario C (3 floors, 16 rooms)')]:
        for n_agents in ['2', '4', '6']:
            if n_agents in data and 'GA_convergence' in data[n_agents]:
                conv = data[n_agents]['GA_convergence']
                ax.plot(conv, linewidth=1.5, alpha=0.8, label=f'{n_agents} agents')
        ax.set_xlabel('Generation'); ax.set_ylabel('Makespan (s)')
        ax.set_title(title); ax.legend(fontsize=8)
    fig.suptitle('GA Convergence Curves', fontweight='bold', fontsize=14)
    fig.tight_layout()
    fig.savefig(f"{FIGS}/fig_q3_convergence.png"); plt.close()

def fig_q3_agent_sweep():
    """图5: 响应者数量-时间关系"""
    b = load_json("q3_scenario_b_scan.json")
    c = load_json("q3_scenario_c_scan.json")
    fig, ax = plt.subplots(figsize=(9, 6))
    for label, data, color in [('Scenario B', b, '#3498db'), ('Scenario C', c, '#e74c3c')]:
        agents, times = [], []
        for k in sorted(data.keys(), key=int):
            agents.append(int(k))
            times.append(data[k]['GA_makespan_s'])
        ax.plot(agents, times, 'o-', linewidth=2.5, markersize=10, label=label, color=color)
        for a, t in zip(agents, times):
            ax.annotate(f'{t:.0f}s', (a, t), textcoords="offset points", xytext=(0,12), ha='center', fontsize=9)
    ax.set_xlabel('Number of Responders', fontsize=13)
    ax.set_ylabel('Makespan (s)', fontsize=13)
    ax.set_title('Responder Count vs. Sweep Time (Diminishing Returns)', fontweight='bold', fontsize=14)
    ax.legend(fontsize=11); ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(f"{FIGS}/fig_q3_agent_sweep.png"); plt.close()

# ============ Q4a Figures ============
def fig_q4a_mc_histogram():
    """图6: MC时间分布"""
    m = load_json("q4a_mc_results.json")
    times = m['times_sample']
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(times, bins=30, density=True, alpha=0.7, color='steelblue', edgecolor='white')
    ax.axvline(m['mean_s'], color='red', linestyle='--', linewidth=2, label=f'Mean={m["mean_s"]:.1f}s')
    ax.axvline(m['median_s'], color='orange', linestyle=':', linewidth=2, label=f'Median={m["median_s"]:.1f}s')
    ax.axvline(m['p95_s'], color='purple', linestyle='-.', linewidth=2, label=f'P95={m["p95_s"]:.1f}s')
    # KDE
    from scipy import stats
    kde_x = np.linspace(min(times), max(times), 200)
    kde = stats.gaussian_kde(times)
    ax.plot(kde_x, kde(kde_x), 'darkblue', linewidth=2, label='KDE')
    ax.set_xlabel('Total Sweep Time (s)', fontsize=13)
    ax.set_ylabel('Probability Density', fontsize=13)
    ax.set_title(f'Monte Carlo Simulation (N={m["n_runs"]}): Sweep Time Distribution', fontweight='bold')
    ax.legend(fontsize=10)
    fig.tight_layout()
    fig.savefig(f"{FIGS}/fig_q4a_mc_hist.png"); plt.close()

def fig_q4a_tornado():
    """图7: 龙卷风图"""
    t = load_json("q4a_tornado.json")
    fig, ax = plt.subplots(figsize=(10, 5))
    params = t['parameters']
    names = list(params.keys())
    base = t['baseline_mean_s']
    lows = [params[n]['low']['mean'] for n in names]
    highs = [params[n]['high']['mean'] for n in names]
    y_pos = range(len(names))
    ax.barh(y_pos, [h - base for h in highs], left=base, height=0.5, color='#e74c3c', label='+Delta')
    ax.barh(y_pos, [l - base for l in lows], left=base, height=0.5, color='#3498db', label='-Delta')
    ax.set_yticks(y_pos); ax.set_yticklabels(names, fontsize=11)
    ax.axvline(base, color='black', linewidth=1.5, linestyle='--')
    ax.set_xlabel('Makespan (s)', fontsize=13)
    ax.set_title('Tornado Chart: Parameter Impact on Sweep Time', fontweight='bold', fontsize=14)
    ax.legend(fontsize=11)
    for i, (n, l, h) in enumerate(zip(names, lows, highs)):
        ax.text(l-1, i, f'{l:.1f}', ha='right', va='center', fontsize=8)
        ax.text(h+0.5, i, f'{h:.1f}', ha='left', va='center', fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{FIGS}/fig_q4a_tornado.png"); plt.close()

# ============ Q4b Figures ============
def fig_q4b_radar():
    """图8: AHP雷达图"""
    a = load_json("q4b_ahp_results.json")
    ranking = a['technology_ranking'][:5]
    weights = a['criteria_weights']
    criteria = list(weights.keys())
    N = len(criteria)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
    for i, tech in enumerate(ranking):
        name = tech['name'][:15]
        raw = tech.get('raw_scores', {})
        scores = [raw.get(c, 0.5) for c in criteria]
        scores += scores[:1]
        ax.fill(angles, scores, alpha=0.1, color=colors[i])
        ax.plot(angles, scores, 'o-', linewidth=2, label=name, color=colors[i])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([c[:12] for c in criteria], fontsize=9)
    ax.set_title('Technology Evaluation Radar Chart (Top 5)', fontweight='bold', fontsize=14, pad=25)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{FIGS}/fig_q4b_radar.png"); plt.close()

def fig_q4b_ranking():
    """图9: 技术排名条形图"""
    a = load_json("q4b_ahp_results.json")
    ranking = a['technology_ranking']
    fig, ax = plt.subplots(figsize=(10, 5))
    names = [r['name'][:20] for r in reversed(ranking)]
    scores = [r['score'] for r in reversed(ranking)]
    bars = ax.barh(names, scores, color=plt.cm.RdYlGn([s/1.0 for s in scores]))
    ax.set_xlabel('Weighted Score', fontsize=13)
    ax.set_title(f"Technology Ranking (AHP, CR={a['diagnostics']['CR']})", fontweight='bold', fontsize=14)
    for bar, s in zip(bars, scores):
        ax.text(bar.get_width()+0.005, bar.get_y()+bar.get_height()/2, f'{s:.3f}', va='center', fontsize=9)
    fig.tight_layout()
    fig.savefig(f"{FIGS}/fig_q4b_ranking.png"); plt.close()

# ============ RUN ALL ============
if __name__ == '__main__':
    print("Generating figures...")
    fig_q2_building_graph();       print("  [1/9] Q2 Building Graph OK")
    fig_q2_time_breakdown();       print("  [2/9] Q2 Time Breakdown OK")
    fig_q2_sensitivity();          print("  [3/9] Q2 Sensitivity OK")
    fig_q3_convergence();          print("  [4/9] Q3 GA Convergence OK")
    fig_q3_agent_sweep();          print("  [5/9] Q3 Agent Sweep OK")
    fig_q4a_mc_histogram();        print("  [6/9] Q4a MC Histogram OK")
    fig_q4a_tornado();             print("  [7/9] Q4a Tornado Chart OK")
    fig_q4b_radar();               print("  [8/9] Q4b AHP Radar OK")
    fig_q4b_ranking();             print("  [9/9] Q4b Tech Ranking OK")
    print(f"\nAll 9 figures saved to {FIGS}/")
