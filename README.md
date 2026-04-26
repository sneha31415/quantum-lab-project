# Quantum Walk Search Benchmark

This project compares classical and quantum random walks for an application-oriented task:

"Given a map (corridor/grid/network), how quickly can an agent find a target node?"

Phase 1 in this repository implements the corridor (1D line) benchmark and evaluates search quality using first hitting time metrics.

## Requirements

- Python 3.10+
- `numpy`
- `matplotlib`
- `qiskit`
- `qiskit-aer`

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

- cumulative hit probability vs step
- first hitting time histograms
- summary statistics panel with success rate and mean hitting time

## Files

- `classical_walk.py`: classical walk simulation, target search, cumulative hit probability
- `quantum_walk.py`: quantum walk simulation and absorbing-target quantum search
- `main.py`: benchmark runner, metrics summary, and application-focused plots

## Output

The benchmark reports observable performance differences via:

- success probability under fixed step budget
- first hitting time distribution
- estimated speedup ratio using mean hitting time

## Current Scenario Parameters

Default values are configured in `main.py`:

- step budget: 80
- target position: +30
- classical trials: 8000
- quantum shots: 8000

These can be changed directly in code for additional experiments.
