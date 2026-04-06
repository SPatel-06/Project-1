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

def pert_expected(o, m, p):
    """Calculate PERT expected duration"""
    return (o + 4*m + p) / 6

def pert_sample(o, m, p):
    """Sample a random duration using PERT (approximated via triangular distribution)"""
    return random.triangular(o, p, m)

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

ES, EF, LS, LF, slack, critical_path, duration, durations = compute_cpm(tasks)

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