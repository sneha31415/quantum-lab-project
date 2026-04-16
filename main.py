import numpy as np
import matplotlib.pyplot as plt
from classical_walk import classical_random_walk
from quantum_walk import quantum_random_walk

# PARAMETERS
steps = 50
trials = 1000

# --- Classical ---
classical_results = classical_random_walk(steps=steps, trials=trials)

# Convert classical results into probability distribution
positions_classical = np.arange(-steps, steps + 1)
counts_classical = np.zeros(len(positions_classical))

for pos in classical_results:
    counts_classical[pos + steps] += 1

prob_classical = counts_classical / np.sum(counts_classical)

# --- Quantum ---
prob_quantum = quantum_random_walk(steps=steps)
positions_quantum = np.arange(-steps, steps + 1)

# --- Plotting ---
plt.figure(figsize=(14, 6))

# Classical Plot
plt.subplot(1, 2, 1)
plt.bar(positions_classical, prob_classical, width=1.0)
plt.title("Classical Random Walk (50 Steps)")
plt.xlabel("Position")
plt.ylabel("Probability")

# Quantum Plot
plt.subplot(1, 2, 2)
plt.bar(positions_quantum, prob_quantum, width=1.0, color='purple')
plt.title("Quantum Random Walk (50 Steps)")
plt.xlabel("Position")
plt.ylabel("Probability")

plt.tight_layout()
plt.show()