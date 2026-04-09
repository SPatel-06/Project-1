# App Launch CPM Simulator

A computational project scheduling model built in Python that applies **Critical Path Method (CPM)**, **PERT estimation**, and **Monte Carlo simulation** to analyze schedule risk and cost-time tradeoffs for a mobile app launch project.

Built as part of MSE 131 (Introduction to Management Science) at the University of Waterloo.

---

## What it does

- Computes the **critical path** of a 10-task project network using CPM
- Models **task duration uncertainty** using PERT (optimistic / most likely / pessimistic estimates)
- Implements a **least-cost crashing algorithm** to shorten the project by spending optimally
- Simulates **random task delays** with configurable probabilities
- Tracks **project budget** using fixed + daily-rate cost model
- Runs **1,000 Monte Carlo simulations** to produce a probability distribution of completion times

---

## Key Results

| Metric | Value |
|---|---|
| Baseline project duration | 35.7 days |
| Critical path | A → C → F → G → H → I |
| Duration with full crashing | 31.5 days |
| Extra cost to crash | $1,717 |
| Monte Carlo mean duration | 37.9 days |
| P(finish ≤ 35 days) | 16.2% |
| 80% confidence interval | 34.3 – 41.7 days |

---

## Project Structure

```
app-launch-cpm-simulator/
├── cpm_calculator.py       # Core model: CPM, PERT, crashing, delays, budget, Monte Carlo
├── experiments.py          # Scenario comparison, sensitivity analysis, charts
├── experiment_a_scenarios.png
├── experiment_b_sensitivity.png
├── experiment_c_montecarlo.png
└── README.md
```

---

## How to Run

**Requirements:**
```
pip install numpy matplotlib
```

**Run the core model:**
```
python cpm_calculator.py
```
Outputs the CPM table, crashing analysis, delay scenarios, budget breakdown, and Monte Carlo statistics.

**Run experiments and generate charts:**
```
python experiments.py
```
Generates and saves three figures:
- `experiment_a_scenarios.png` — scenario comparison (no / partial / full crashing)
- `experiment_b_sensitivity.png` — sensitivity analysis on backend duration and delay probability
- `experiment_c_montecarlo.png` — Monte Carlo distribution with percentile lines

---

## Model Overview

### Tasks and Dependencies

| Task | Name | Duration (days) | Predecessors |
|---|---|---|---|
| A | Project Planning | 4 | — |
| B | UI/UX Design | 6 | A |
| C | Backend Development | 10 | A |
| D | Frontend Development | 8 | B |
| E | Database Setup | 3 | A |
| F | API Integration | 5 | C, E |
| G | Testing & QA | 6 | D, F |
| H | Bug Fixing | 4 | G |
| I | App Store Submission | 5 | H |
| J | Marketing & Launch Prep | 7 | B |

### Extensions

1. **PERT Uncertainty** — each task has optimistic, most likely, and pessimistic durations sampled via triangular distribution
2. **Least-Cost Crashing** — iteratively crashes the cheapest critical path task first, recomputing CPM after each step
3. **Random Task Delays** — each task has a configurable probability of delay with random magnitude
4. **Budget Tracking** — fixed overhead + daily resource cost per task, with crash cost comparison
5. **Monte Carlo Simulation** — 1,000 runs with random PERT samples to produce completion time distribution and critical path frequencies

---

## Sample Output

```
APP LAUNCH PROJECT — BASELINE CPM RESULTS (PERT Expected)
=================================================================
Project Duration: 35.7 days

Task   Name                      Exp.Dur   ES     EF     Slack   Critical?
-----------------------------------------------------------------
A      Project Planning          4.2       0.0    4.2    0.0     YES ***
C      Backend Development       10.5      4.2    14.7   0.0     YES ***
F      API Integration           5.3       14.7   20.0   0.0     YES ***
G      Testing & QA              6.3       20.0   26.3   0.0     YES ***
H      Bug Fixing                4.2       26.3   30.5   0.0     YES ***
I      App Store Submission      5.2       30.5   35.7   0.0     YES ***

Critical Path: A → C → F → G → H → I
```

---

## Skills Demonstrated

- Python (data structures, algorithms, simulation)
- Critical Path Method (CPM) and PERT scheduling
- Monte Carlo simulation and probabilistic analysis
- Sensitivity analysis and scenario comparison
- Data visualization with matplotlib
- Operations research concepts (crashing, cost-time tradeoffs, utilization)

---

## License

MIT