# Random Walk Target Search (Quantum vs Classical)

This project is a **target-search benchmark**: given a graph (corridor/grid/network), compare how quickly a **classical random walk** versus a **discrete-time coined quantum walk** finds a **target node**.

The benchmark is framed in terms of **first hitting time**:

- Each run has a fixed **step budget**.
- A trial/shot is successful if the walker reaches the target within that budget.
- We compare **success rate**, **mean hitting time**, and a simple **speedup** ratio:
	$\text{speedup} = \frac{\mathbb{E}[T_\text{classical}]}{\mathbb{E}[T_\text{quantum}]}$.

## What’s Implemented

### Classical target search

- Classical walk samples a random neighbor at every step.
- Repeats for many **trials** and records the first step that hits the target.

### Quantum target search

- Quantum walk is implemented on the **directed-edge basis** with a **Grover coin** at each node.
- The target is treated as an **absorbing measurement** each step: probability mass at the target is recorded as a “first-hit” event and removed from the surviving state.
- Results include the **first-hit probability distribution** and **cumulative hit probability** curve.

## Included Maps / Scenarios

The default scenarios used by both the CLI benchmark and the UI are:

- `corridor-41` (1D line graph)
- `grid-7x7` (2D grid)
- `branch-network` (a small custom branching graph)

Targets are chosen at **near / mid / far** shortest-path distances from the start node.

## Setup

Python 3.10+ is recommended.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The core simulation code uses `numpy`. The interactive UI additionally uses `streamlit`, `plotly`, and `networkx`.

> Note: `requirements.txt` currently includes a few packages (e.g. `qiskit`, `qiskit-aer`, `rustworkx`, `scipy`) that are **not imported by the current simulation/UI code**. They’re safe to keep if you plan to extend the project, but they’re not required by the code paths used by `main.py` / `app.py` today.

## Run (CLI benchmark)

```bash
python main.py
```

This will:

- run the 3 default scenarios (near/mid/far targets)
- print a per-scenario summary to the terminal
- save a figure to `graph_target_search_benchmark.png`

To change defaults (step budget, trial counts, scenarios), edit the top of `main()` in `main.py`.

## Run (Streamlit UI)

Option A:

```bash
streamlit run app.py
```

Option B (uses the local `venv/`):

```bash
chmod +x run_ui.sh
./run_ui.sh
```

The UI lets you choose a graph and parameters (steps, trials, shots, target distance) and then displays:

- cumulative hit-probability curves (classical vs quantum)
- success-rate and mean-hitting-time comparisons
- speedup chart
- graph topology visualization (start/target highlighted)

## Project Structure

- `main.py`: CLI benchmark runner; saves `graph_target_search_benchmark.png`
- `app.py`: Streamlit dashboard entrypoint
- `classical_walk.py`: classical walk + graph target-search + cumulative hit probability
- `quantum_walk.py`: quantum walk + graph absorbing-target search + sampling of hit times
- `graph_topology.py`: graph representation + corridor/grid builders + shortest-path utilities
- `ui_data.py`: adapters that run scenarios and return structured results for the UI
- `ui_components.py`: Streamlit/Plotly visualization components
- `ui_presets.py`: demo preset configurations (optional)
- `run_ui.sh`: convenience script to run the Streamlit app

## Screenshots

- CLI output: `assets/terminal-output.png`
- CLI benchmark plot: `assets/graph_target_search_benchmark.png`
- Comparison figure: `assets/comparision-graph.png`
