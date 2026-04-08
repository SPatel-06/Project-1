# ============================================================
# MSE 131 Final — Experiments and Sensitivity Analysis
# ============================================================

import sys
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Import everything from your main model file
import cpm_calculator as cpm

tasks      = cpm.tasks
task_names = cpm.task_names
crash_info = cpm.crash_info
delay_info = cpm.delay_info
task_costs = cpm.task_costs

# ============================================================
# Experiment A — Scenario Comparison
# 3 scenarios: No crashing, partial crashing, full crashing
# ============================================================

print("=" * 65)
print("EXPERIMENT A — SCENARIO COMPARISON")
print("=" * 65)

scenarios = [
    ("No Crashing",      0),
    ("Partial Crashing", 3),
    ("Full Crashing",    5),
]

scenario_results = []

for name, target in scenarios:
    if target == 0:
        # No crashing — use baseline tasks
        _, _, _, _, _, cp, dur, durs = cpm.compute_cpm(tasks, use_expected=True)
        cost, _ = cpm.compute_budget(tasks, task_costs, durs)
        crash_c = 0
    else:
        crashed_t, crash_c, _, _ = cpm.least_cost_crashing(tasks, target, crash_info)
        _, _, _, _, _, cp, dur, durs = cpm.compute_cpm(crashed_t, use_expected=True)
        cost, _ = cpm.compute_budget(crashed_t, task_costs, durs)

    total = cost + crash_c
    scenario_results.append((name, dur, total, crash_c))
    print(f"\n{name}:")
    print(f"  Duration   : {dur:.1f} days")
    print(f"  Base cost  : ${cost:,.0f}")
    print(f"  Crash cost : ${crash_c:,}")
    print(f"  Total cost : ${total:,.0f}")

# --- Chart A: Duration and Cost by Scenario ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Experiment A — Scenario Comparison", fontsize=14, fontweight='bold')

names   = [r[0] for r in scenario_results]
durs    = [r[1] for r in scenario_results]
costs   = [r[2] for r in scenario_results]
colors  = ['#4C72B0', '#DD8452', '#55A868']

ax1.bar(names, durs, color=colors, edgecolor='black', linewidth=0.5)
ax1.set_title("Project Duration by Scenario")
ax1.set_ylabel("Duration (days)")
ax1.set_ylim(0, max(durs) * 1.2)
for i, v in enumerate(durs):
    ax1.text(i, v + 0.3, f"{v:.1f}d", ha='center', fontweight='bold')

ax2.bar(names, costs, color=colors, edgecolor='black', linewidth=0.5)
ax2.set_title("Total Cost by Scenario")
ax2.set_ylabel("Cost ($)")
ax2.set_ylim(0, max(costs) * 1.2)
for i, v in enumerate(costs):
    ax2.text(i, v + 300, f"${v:,.0f}", ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig("experiment_a_scenarios.png", dpi=150, bbox_inches='tight')
plt.show()
print("\nChart saved: experiment_a_scenarios.png")

# ============================================================
# Experiment B — Sensitivity Analysis
# B1: Vary Backend (C) duration
# B2: Vary number of simulation runs to check stability
# ============================================================

print("\n" + "=" * 65)
print("EXPERIMENT B — SENSITIVITY ANALYSIS")
print("=" * 65)

# --- B1: Sensitivity to Backend Development duration ---
print("\nB1: Effect of Backend Development (C) duration on project")

import copy
backend_durations = [6, 8, 10, 12, 14, 16]
b1_results = []

for new_m in backend_durations:
    modified_tasks = copy.deepcopy(tasks)
    o, m, p, preds = modified_tasks['C']
    modified_tasks['C'] = (o, new_m, p, preds)
    _, _, _, _, _, cp, dur, durs = cpm.compute_cpm(modified_tasks, use_expected=True)
    cost, _ = cpm.compute_budget(modified_tasks, task_costs, durs)
    b1_results.append((new_m, dur, cost))
    crit = "CRITICAL" if 'C' in cp else "not critical"
    print(f"  Backend most-likely = {new_m}d → Project: {dur:.1f}d | Cost: ${cost:,.0f} | C is {crit}")

# --- B2: Sensitivity to delay probability ---
print("\nB2: Effect of overall delay probability on project duration")

delay_multipliers = [0.0, 0.5, 1.0, 1.5, 2.0]
b2_results = []

for multiplier in delay_multipliers:
    modified_delays = {
        t: (prob * multiplier, mn, mx)
        for t, (prob, mn, mx) in delay_info.items()
    }
    # Run 500 simulations for each multiplier
    random.seed(42)
    sim_durs = []
    for _ in range(500):
        delayed_t, _ = cpm.apply_delays(tasks, modified_delays)
        _, _, _, _, _, _, dur, _ = cpm.compute_cpm(delayed_t, use_expected=True)
        sim_durs.append(dur)
    mean_dur = np.mean(sim_durs)
    b2_results.append((multiplier, mean_dur))
    print(f"  Delay multiplier = {multiplier:.1f}x → Mean duration: {mean_dur:.1f} days")

# --- Chart B: Two sensitivity plots ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Experiment B — Sensitivity Analysis", fontsize=14, fontweight='bold')

# B1 chart
b1_x = [r[0] for r in b1_results]
b1_y = [r[1] for r in b1_results]
ax1.plot(b1_x, b1_y, marker='o', color='#4C72B0', linewidth=2, markersize=8)
ax1.axhline(y=cpm.compute_cpm(tasks)[6], color='gray', linestyle='--', label='Baseline')
ax1.set_title("Project Duration vs Backend Duration")
ax1.set_xlabel("Backend Dev most-likely duration (days)")
ax1.set_ylabel("Project duration (days)")
ax1.legend()
ax1.grid(True, alpha=0.3)

# B2 chart
b2_x = [r[0] for r in b2_results]
b2_y = [r[1] for r in b2_results]
ax2.plot(b2_x, b2_y, marker='s', color='#DD8452', linewidth=2, markersize=8)
ax2.set_title("Project Duration vs Delay Probability")
ax2.set_xlabel("Delay probability multiplier (1.0 = baseline)")
ax2.set_ylabel("Mean project duration (days)")
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("experiment_b_sensitivity.png", dpi=150, bbox_inches='tight')
plt.show()
print("\nChart saved: experiment_b_sensitivity.png")

# ============================================================
# Experiment C — Monte Carlo Histogram
# ============================================================

print("\n" + "=" * 65)
print("EXPERIMENT C — MONTE CARLO DISTRIBUTION")
print("=" * 65)

random.seed(99)
sim_durations, cp_counts = cpm.monte_carlo(tasks, n_simulations=1000)
sim_array = np.array(sim_durations)

fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(sim_array, bins=40, color='#4C72B0', edgecolor='white',
        linewidth=0.5, alpha=0.85)

# Add vertical lines for key percentiles
ax.axvline(np.percentile(sim_array, 10), color='green',
           linestyle='--', linewidth=1.5, label='10th percentile')
ax.axvline(np.mean(sim_array), color='orange',
           linestyle='-', linewidth=2, label=f'Mean: {np.mean(sim_array):.1f}d')
ax.axvline(np.percentile(sim_array, 90), color='red',
           linestyle='--', linewidth=1.5, label='90th percentile')

ax.set_title("Monte Carlo Simulation — Project Duration Distribution (1,000 runs)",
             fontsize=13, fontweight='bold')
ax.set_xlabel("Project Duration (days)")
ax.set_ylabel("Frequency")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("experiment_c_montecarlo.png", dpi=150, bbox_inches='tight')
plt.show()
print(f"\nChart saved: experiment_c_montecarlo.png")
print(f"Mean: {np.mean(sim_array):.1f} days")
print(f"80% confidence interval: {np.percentile(sim_array,10):.1f} – {np.percentile(sim_array,90):.1f} days")