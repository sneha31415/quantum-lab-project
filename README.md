# Quantum Random Walk

This project compares a classical random walk with a 1D quantum random walk and visualizes both results using Matplotlib.

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

Run the main comparison plot:

```bash
python main.py
```

Run only the quantum walk plot:

```bash
python quantum_walk.py
```

## Files

- `classical_walk.py`: classical random walk simulation and plotting helper
- `quantum_walk.py`: quantum random walk simulation and plotting helper
- `main.py`: side-by-side comparison of classical and quantum walks
- `plot_results.py`: optional plotting script

## Output

The scripts generate bar charts showing the final position probability distribution for the classical and quantum walks.
