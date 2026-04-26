# Quantum Walk Search Benchmark

This project compares classical and quantum random walks for an application-oriented task:

"Given a map (corridor/grid/network), how quickly can an agent find a target node?"

Phase 2 extends the benchmark from a 1D corridor to graph-based maps, including grids and simple user-defined networks, while keeping the same search API for classical and quantum walkers.

## Requirements

- Python 3.10+
- `numpy`
- `matplotlib`

Install the dependencies with:

```bash
pip install -r requirements.txt
```

## How to Run

Run the benchmark:

```bash
python main.py
```

The script generates:

- speedup comparison across corridor, grid, and network maps
- cumulative hit probability curves for representative distance sweeps
- summary statistics panel with success rate, mean hitting time, and speedup ratio

## Files

- `classical_walk.py`: classical walk simulation, target search, cumulative hit probability
- `graph_topology.py`: shared graph representation plus corridor/grid builders and distance utilities
- `quantum_walk.py`: quantum walk simulation and graph-based absorbing-target search
- `main.py`: benchmark runner, metrics summary, and application-focused plots

## Output

The benchmark reports observable performance differences via:

- success probability under fixed step budget
- first hitting time distribution
- estimated speedup ratio using mean hitting time

## Current Scenario Parameters

Default values are configured in `main.py`:

- step budget: 60
- classical trials: 4000
- quantum shots: 4000
- scenarios: 41-node corridor, 7x7 grid, and a small branching network

Each scenario sweeps near, mid, and far target distances derived from graph distance from the chosen start node.
