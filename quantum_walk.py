import numpy as np
import matplotlib.pyplot as plt

def quantum_random_walk(steps=50):
    """Simulates a 1D Quantum Random Walk."""
    # Total grid size: needs to go from -steps to +steps
    positions = 2 * steps + 1
    
    # State vector: shape (positions, 2). 
    # The '2' represents our coin basis states: 0 (Left) and 1 (Right).
    # We MUST use complex numbers to allow for quantum phase interference.
    state = np.zeros((positions, 2), dtype=complex)
    
    # INITIAL STATE: Start at the center (index = steps).
    state[steps, 0] = 1 / np.sqrt(2)      # Amplitude for |0> (Left)
    state[steps, 1] = 1j / np.sqrt(2)     # Amplitude for |1> (Right)
    
    # The Hadamard Coin Operator
    H = (1 / np.sqrt(2)) * np.array([[1,  1], 
                                     [1, -1]])
    
    for _ in range(steps):
        # 1. Apply Coin Operator: put the coin at every position into superposition
        state = state @ H
        
        # 2. Apply Shift Operator: move the amplitudes left or right based on the coin state
        next_state = np.zeros_like(state)
        
        # Coin state 0 moves Left (position index decreases)
        # Takes all left amplitudes Moves them to position -1
        next_state[:-1, 0] = state[1:, 0]
        
        # Coin state 1 moves Right (position index increases)
        # Takes all right amplitudes Moves them to position +1
        next_state[1:, 1] = state[:-1, 1]
        
        # Update the state for the next step
        state = next_state

    probabilities = np.abs(state[:, 0])**2 + np.abs(state[:, 1])**2
    
    return probabilities


def plot_quantum(probabilities, steps):
    positions = np.arange(-steps, steps + 1)
    
    # We use a bar plot here because it highlights the alternating zero-probabilities 
    # (a quirk of bipartite graphs/grids in both classical and quantum walks)
    plt.bar(positions, probabilities, width=1.0, color='purple', alpha=0.8)
    plt.title(f"Quantum Random Walk Distribution ({steps} Steps)")
    plt.xlabel("Position")
    plt.ylabel("Probability")
    plt.grid(axis='y', alpha=0.3)
    plt.show()

if __name__ == "__main__":
    steps = 50
    # Run the quantum walk
    q_results = quantum_random_walk(steps=steps)
    
    # Plot the results
    plot_quantum(q_results, steps)