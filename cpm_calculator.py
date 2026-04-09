# ============================================================
# MSE 131 Final — App Launch CPM Model
# ============================================================

import random
import numpy as np

# Each task: 'ID': (Optimistic, Most Likely, Pessimistic, [predecessors])
tasks = {
    'A': (2,  4,  7,  []),
    'B': (4,  6,  10, ['A']),
    'C': (7,  10, 16, ['A']),
    'D': (5,  8,  12, ['B']),
    'E': (2,  3,  5,  ['A']),
    'F': (3,  5,  9,  ['C', 'E']),
    'G': (4,  6,  10, ['D', 'F']),
    'H': (2,  4,  7,  ['G']),
    'I': (3,  5,  8,  ['H']),
    'J': (5,  7,  11, ['B']),
}

task_names = {
    'A': 'Project Planning',
    'B': 'UI/UX Design',
    'C': 'Backend Development',
    'D': 'Frontend Development',
    'E': 'Database Setup',
    'F': 'API Integration',
    'G': 'Testing & QA',
    'H': 'Bug Fixing',
    'I': 'App Store Submission',
    'J': 'Marketing & Launch Prep',
}

# ============================================================
# Extension 1 — Task Duration Uncertainty (PERT)
# ============================================================

def pert_expected(o, m, p):
    """Calculate PERT expected duration"""
    return (o + 4*m + p) / 6

def pert_sample(o, m, p):
    """Sample a random duration using PERT (approximated via triangular distribution)"""
    return random.triangular(o, p, m)

# ============================================================
# Extension 2 — Crashing
# ============================================================

# Crash info for each task: 'ID': (max_days_crashable, cost_per_day)
# Only critical path tasks are worth crashing
crash_info = {
    'A': (1, 500),    # Planning: limited crash potential
    'C': (3, 1200),   # Backend: expensive, can crash up to 3 days
    'F': (2, 800),    # API Integration: moderate cost
    'G': (2, 700),    # Testing: can add more testers
    'H': (1, 600),    # Bug Fixing: limited
    'I': (1, 1000),   # App Store: mostly fixed, limited crash
}

def least_cost_crashing(tasks, target_reduction, crash_info):
    """
    Crash the project by target_reduction days using least-cost crashing.
    Always crashes the cheapest critical path task first.
    Returns crash schedule and total crash cost.
    """
    # Work on a copy of tasks so we don't modify the original
    import copy
    crashed_tasks = copy.deepcopy(tasks)
    
    # Track how many days each task has been crashed
    days_crashed = {t: 0 for t in tasks}
    total_cost = 0
    crash_log = []

    days_reduced = 0

    while days_reduced < target_reduction:
        # Recompute CPM to find current critical path
        _, _, _, _, _, critical_path, current_duration, _ = compute_cpm(crashed_tasks)

        # Find crashable tasks on critical path (still have crash days remaining)
        options = []
        for t in critical_path:
            if t in crash_info:
                max_crash, cost_per_day = crash_info[t]
                remaining = max_crash - days_crashed[t]
                if remaining > 0:
                    options.append((cost_per_day, t, remaining))

        # If no options left, we can't crash further
        if not options:
            print("  No more crashable tasks available.")
            break

        # Pick cheapest option
        options.sort()
        cost_per_day, chosen_task, remaining = options[0]

        # Crash chosen task by 1 day
        o, m, p, preds = crashed_tasks[chosen_task]
        crashed_tasks[chosen_task] = (o, max(o, m-1), max(o, p-1), preds)
        days_crashed[chosen_task] += 1
        total_cost += cost_per_day
        days_reduced += 1

        crash_log.append((chosen_task, task_names[chosen_task], cost_per_day, total_cost))

    return crashed_tasks, total_cost, crash_log, days_crashed

# ============================================================
# Extension 3 — Random Task Delays
# ============================================================

# Delay info: 'ID': (probability_of_delay, min_delay_days, max_delay_days)
delay_info = {
    'A': (0.2, 1, 3),   # Planning delays: stakeholder feedback late
    'B': (0.3, 1, 4),   # Design delays: revision cycles
    'C': (0.4, 2, 6),   # Backend: highest risk, most complex
    'D': (0.3, 1, 4),   # Frontend: dependent on design changes
    'E': (0.2, 1, 2),   # Database: usually straightforward
    'F': (0.35, 1, 5),  # API Integration: third-party dependencies
    'G': (0.3, 1, 3),   # Testing: bug discovery takes time
    'H': (0.4, 1, 4),   # Bug fixing: hard to estimate
    'I': (0.2, 1, 5),   # App Store: review time unpredictable
    'J': (0.2, 1, 3),   # Marketing: content approval delays
}

def apply_delays(tasks, delay_info):
    """
    Randomly apply delays to tasks based on delay probabilities.
    Returns a modified tasks dict with delays baked into durations,
    and a log of what got delayed.
    """
    import copy
    delayed_tasks = copy.deepcopy(tasks)
    delay_log = []

    for t, (prob, min_d, max_d) in delay_info.items():
        if random.random() < prob:
            # Delay occurred — add random days to pessimistic duration
            extra_days = random.randint(min_d, max_d)
            o, m, p, preds = delayed_tasks[t]
            delayed_tasks[t] = (o, m, p + extra_days, preds)
            delay_log.append((t, task_names[t], extra_days))

    return delayed_tasks, delay_log

# ============================================================
# Extension 4 — Budget Tracking
# ============================================================

# Task costs: base cost + cost per day of duration
# 'ID': (fixed_cost, daily_rate)
# fixed_cost = overhead regardless of duration (tools, licenses)
# daily_rate = cost per day (team salaries, resources)
task_costs = {
    'A': (500,  300),   # Planning: PM time
    'B': (1000, 400),   # UI/UX: designer fees
    'C': (2000, 800),   # Backend: senior dev, most expensive
    'D': (1500, 600),   # Frontend: dev fees
    'E': (800,  400),   # Database: setup + admin
    'F': (1200, 500),   # API Integration: dev + licensing
    'G': (1000, 350),   # Testing: QA team
    'H': (500,  400),   # Bug fixing: dev time
    'I': (300,  200),   # App Store: submission fees + admin
    'J': (2000, 300),   # Marketing: ads + content creation
}

def compute_budget(tasks, task_costs, durations):
    """
    Compute total project budget based on task durations and costs.
    Returns total cost and breakdown per task.
    """
    budget_breakdown = {}
    total_cost = 0

    for t, (fixed, daily_rate) in task_costs.items():
        duration = durations[t]
        task_total = fixed + (daily_rate * duration)
        budget_breakdown[t] = {
            'fixed': fixed,
            'daily_rate': daily_rate,
            'duration': duration,
            'total': task_total
        }
        total_cost += task_total

    return total_cost, budget_breakdown

# ============================================================
# Extension 5 — Monte Carlo Simulation
# ============================================================

def monte_carlo(tasks, n_simulations=1000):
    """
    Run the project n_simulations times with random PERT durations.
    Returns list of project durations and critical path frequencies.
    """
    durations_list = []
    critical_path_counts = {t: 0 for t in tasks}

    for _ in range(n_simulations):
        # Run CPM with random durations (use_expected=False)
        _, _, _, _, _, cp, proj_dur, _ = compute_cpm(tasks, use_expected=False)
        durations_list.append(proj_dur)
        for t in cp:
            critical_path_counts[t] += 1

    return durations_list, critical_path_counts

def compute_cpm(tasks, use_expected=True):
    """
    Compute CPM on the task network.
    use_expected=True  → uses PERT expected durations (baseline)
    use_expected=False → samples random durations (for simulation)
    """
    from collections import deque

    # Build duration dict based on mode
    durations = {}
    for t, (o, m, p, preds) in tasks.items():
        if use_expected:
            durations[t] = pert_expected(o, m, p)
        else:
            durations[t] = pert_sample(o, m, p)

    # --- Step 1: Topological sort ---
    # We need to process tasks in order (predecessors before successors)
    # This is called a "topological sort"
    in_degree = {t: 0 for t in tasks}
    for t, (o, m, p, predecessors) in tasks.items():
        in_degree[t] += len(predecessors)

    queue = deque([t for t in tasks if in_degree[t] == 0])
    topological_order = []

    while queue:
        node = queue.popleft()
        topological_order.append(node)
        for t, (o, m, p, predecessors) in tasks.items():
            if node in predecessors:
                in_degree[t] -= 1
                if in_degree[t] == 0:
                    queue.append(t)
                    
    # --- Step 2: Compute earliest start and finish times ---
    ES = {}  # Early Start
    EF = {}  # Early Finish

    for t in topological_order:
        o, m, p, predecessors = tasks[t]
        duration = durations[t]
        if not predecessors:
            ES[t] = 0
        else:
            ES[t] = max(EF[p] for p in predecessors)
        EF[t] = ES[t] + duration
    project_duration = max(EF.values())
    
    # --- Step 3: Compute latest start and finish times ---
    LF = {}  # Late Finish
    LS = {}  # Late Start

    for t in reversed(topological_order):
        o, m, p, predecessors = tasks[t]
        successors = [s for s in tasks if t in tasks[s][3]]
        if not successors:
            LF[t] = project_duration
        else:
            LF[t] = min(LS[s] for s in successors)
        LS[t] = LF[t] - durations[t]

    # --- Step 4: Identify critical path & Calculate Slack ---
    slack = {}
    critical_path = []

    for t in topological_order:
        slack[t] = round(LS[t] - ES[t], 2)
        if slack[t] <= 0.01:  # small tolerance for floating point
            critical_path.append(t)

    return ES, EF, LS, LF, slack, critical_path, project_duration, durations

# ============================================================
# Run the baseline model
# ============================================================

if __name__ == "__main__":

    ES, EF, LS, LF, slack, critical_path, duration, durations = compute_cpm(tasks, use_expected=True)

    print("=" * 65)
    print("APP LAUNCH PROJECT — BASELINE CPM RESULTS (PERT Expected)")
    print("=" * 65)
    print(f"\nProject Duration: {duration:.1f} days\n")
    print(f"{'Task':<6} {'Name':<25} {'Exp.Dur':<9} {'ES':<6} {'EF':<6} {'Slack':<7} {'Critical?'}")
    print("-" * 65)

    for t in ['A','B','C','D','E','F','G','H','I','J']:
        crit = "YES ***" if t in critical_path else ""
        print(f"{t:<6} {task_names[t]:<25} {durations[t]:<9.1f} {ES[t]:<6.1f} {EF[t]:<6.1f} {slack[t]:<7.1f} {crit}")

    print(f"\nCritical Path: {' → '.join(critical_path)}")
    print(f"Project Duration: {duration:.1f} days")

    # ============================================================
    # Extension 2 — Crashing Analysis
    # ============================================================

    print("\n" + "=" * 65)
    print("EXTENSION 2 — CRASHING ANALYSIS")
    print("=" * 65)

    target = 5
    crashed_tasks, crash_cost, crash_log, days_crashed = least_cost_crashing(
        tasks, target, crash_info
    )

    ES2, EF2, LS2, LF2, slack2, cp2, duration2, durations2 = compute_cpm(
        crashed_tasks, use_expected=True
    )

    print(f"\nTarget reduction : {target} days")
    print(f"Original duration: {duration:.1f} days")
    print(f"Crashed duration : {duration2:.1f} days")
    print(f"Days saved       : {duration - duration2:.1f} days")
    print(f"Total crash cost : ${crash_cost:,}")

    print(f"\n{'Step':<6} {'Task':<6} {'Name':<25} {'Cost/Day':<10} {'Total Cost'}")
    print("-" * 60)
    for i, (t, name, cpd, tc) in enumerate(crash_log, 1):
        print(f"{i:<6} {t:<6} {name:<25} ${cpd:<9,} ${tc:,}")

    print(f"\nNew Critical Path: {' → '.join(cp2)}")

    # ============================================================
    # Extension 3 — Random Task Delays
    # ============================================================

    print("\n" + "=" * 65)
    print("EXTENSION 3 — RANDOM TASK DELAYS")
    print("=" * 65)

    random.seed(42)

    for scenario in range(1, 4):
        delayed_tasks, delay_log = apply_delays(tasks, delay_info)
        _, _, _, _, _, cp3, duration3, _ = compute_cpm(delayed_tasks, use_expected=True)

        print(f"\n--- Scenario {scenario} ---")
        if delay_log:
            print("  Delays occurred:")
            for t, name, extra in delay_log:
                print(f"    {t} ({name}): +{extra} days")
        else:
            print("  No delays occurred this scenario")

        print(f"  Project duration : {duration3:.1f} days")
        print(f"  Critical path    : {' → '.join(cp3)}")
        print(f"  vs baseline      : {duration3 - duration:.1f} days longer")

    # ============================================================
    # Extension 4 — Budget Tracking
    # ============================================================

    print("\n" + "=" * 65)
    print("EXTENSION 4 — BUDGET TRACKING")
    print("=" * 65)

    total_cost, budget_breakdown = compute_budget(tasks, task_costs, durations)

    print(f"\n{'Task':<6} {'Name':<25} {'Duration':<10} {'Fixed':<10} {'Daily':<10} {'Total'}")
    print("-" * 70)

    for t in ['A','B','C','D','E','F','G','H','I','J']:
        b = budget_breakdown[t]
        print(f"{t:<6} {task_names[t]:<25} {b['duration']:<10.1f} ${b['fixed']:<9,} ${b['daily_rate']:<9,} ${b['total']:,.0f}")

    print(f"\nTotal Project Budget : ${total_cost:,.0f}")
    print(f"Project Duration     : {duration:.1f} days")
    print(f"Average Cost/Day     : ${total_cost/duration:,.0f}")
    print(f"\nBudget without crashing : ${total_cost:,.0f}")
    print(f"Crash cost added        : ${crash_cost:,}")
    print(f"Total with crashing     : ${total_cost + crash_cost:,.0f}")
    print(f"Time saved by crashing  : {duration - duration2:.1f} days")

    # ============================================================
    # Extension 5 — Monte Carlo Simulation
    # ============================================================

    print("\n" + "=" * 65)
    print("EXTENSION 5 — MONTE CARLO SIMULATION (1,000 runs)")
    print("=" * 65)

    random.seed(99)
    sim_durations, cp_counts = monte_carlo(tasks, n_simulations=1000)

    sim_array = np.array(sim_durations)

    print(f"\nProject Duration Statistics (over 1,000 simulations):")
    print(f"  Mean duration      : {np.mean(sim_array):.1f} days")
    print(f"  Median duration    : {np.median(sim_array):.1f} days")
    print(f"  Std deviation      : {np.std(sim_array):.1f} days")
    print(f"  Minimum            : {np.min(sim_array):.1f} days")
    print(f"  Maximum            : {np.max(sim_array):.1f} days")
    print(f"  10th percentile    : {np.percentile(sim_array, 10):.1f} days")
    print(f"  90th percentile    : {np.percentile(sim_array, 90):.1f} days")

    # Probability of finishing by certain deadlines
    for deadline in [30, 33, 35, 38, 40]:
        prob = np.mean(sim_array <= deadline) * 100
        print(f"  P(finish <= {deadline} days): {prob:.1f}%")

    print(f"\nCritical Path Task Frequencies (how often each task was critical):")
    print(f"{'Task':<6} {'Name':<25} {'Frequency':<10} {'% of runs'}")
    print("-" * 55)
    for t in ['A','B','C','D','E','F','G','H','I','J']:
        freq = cp_counts[t]
        pct = freq / 1000 * 100
        print(f"{t:<6} {task_names[t]:<25} {freq:<10} {pct:.1f}%")