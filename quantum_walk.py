import numpy as np
import matplotlib.pyplot as plt

from graph_topology import GraphTopology, corridor_graph

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


def _build_graph_walk_basis(graph: GraphTopology):
    directed_edges = []
    edge_to_index = {}
    outgoing_edges = [[] for _ in range(graph.num_nodes)]

    for source, neighbors in enumerate(graph.adjacency):
        for destination in neighbors:
            edge = (source, destination)
            edge_to_index[edge] = len(directed_edges)
            directed_edges.append(edge)
            outgoing_edges[source].append(edge_to_index[edge])

    return directed_edges, edge_to_index, [tuple(indices) for indices in outgoing_edges]


def _apply_grover_coin(state, outgoing_edges):
    coin_state = state.copy()

    for edge_indices in outgoing_edges:
        edge_indices = np.asarray(edge_indices, dtype=int)
        degree = len(edge_indices)
        if degree == 0:
            continue

        amplitudes = coin_state[edge_indices]
        coin_state[edge_indices] = 2.0 * np.mean(amplitudes) - amplitudes

    return coin_state


def quantum_graph_target_search(
    graph: GraphTopology,
    steps=60,
    target_node=0,
    start_node=0,
    shots=5000,
    seed=None,
):
    """Estimate first hitting times for a coined quantum walk on a graph."""
    if start_node < 0 or start_node >= graph.num_nodes:
        raise ValueError("start_node is out of range.")
    if target_node < 0 or target_node >= graph.num_nodes:
        raise ValueError("target_node is out of range.")

    rng = np.random.default_rng(seed)
    directed_edges, edge_to_index, outgoing_edges = _build_graph_walk_basis(graph)
    state = np.zeros(len(directed_edges), dtype=complex)
    target_edge_indices = np.asarray(outgoing_edges[target_node], dtype=int)

    if start_node == target_node:
        first_hit_probabilities = np.zeros(steps)
        if steps > 0:
            first_hit_probabilities[0] = 1.0
        cumulative_hit_probabilities = np.cumsum(first_hit_probabilities)
        hit_times = np.zeros(shots, dtype=float)
        return {
            "first_hit_probabilities": first_hit_probabilities,
            "cumulative_hit_probabilities": cumulative_hit_probabilities,
            "success_probability": float(cumulative_hit_probabilities[-1]) if steps > 0 else 1.0,
            "hit_times": hit_times,
        }

    start_degree = graph.degree(start_node)
    if start_degree == 0:
        raise ValueError("start_node must have at least one neighbor for a quantum walk.")

    initial_amplitude = 1.0 / np.sqrt(start_degree)
    for edge_index in outgoing_edges[start_node]:
        state[edge_index] = initial_amplitude

    first_hit_probabilities = np.zeros(steps)

    for step in range(steps):
        state = _apply_grover_coin(state, outgoing_edges)

        shifted_state = np.zeros_like(state)
        for edge_index, (source, destination) in enumerate(directed_edges):
            reverse_index = edge_to_index.get((destination, source))
            if reverse_index is None:
                raise ValueError("Graph must be undirected and contain reverse edges for each link.")
            shifted_state[reverse_index] = state[edge_index]

        state = shifted_state

        if target_edge_indices.size > 0:
            hit_probability = float(np.sum(np.abs(state[target_edge_indices]) ** 2))
            first_hit_probabilities[step] = hit_probability
            state[target_edge_indices] = 0.0

    cumulative_hit_probabilities = np.cumsum(first_hit_probabilities)
    success_probability = float(cumulative_hit_probabilities[-1]) if steps > 0 else 0.0

    miss_probability = max(0.0, 1.0 - success_probability)
    sampling_probs = np.concatenate([first_hit_probabilities, np.array([miss_probability])])
    sampling_probs = np.clip(sampling_probs, 0.0, None)
    sampling_total = float(np.sum(sampling_probs))
    if sampling_total == 0.0:
        sampling_probs = np.zeros_like(sampling_probs)
        sampling_probs[-1] = 1.0
    else:
        sampling_probs = sampling_probs / sampling_total

    sampled = rng.choice(np.arange(1, steps + 2), size=shots, p=sampling_probs)
    hit_times = sampled.astype(float)
    hit_times[hit_times == (steps + 1)] = np.nan

    return {
        "first_hit_probabilities": first_hit_probabilities,
        "cumulative_hit_probabilities": cumulative_hit_probabilities,
        "success_probability": success_probability,
        "hit_times": hit_times,
    }


def quantum_target_search(
    steps=60,
    target_position=20,
    start_position=0,
    shots=5000,
    seed=None,
):
    """Estimate first hitting times for a 1D quantum walk with absorbing target.

    The state is measured at each step only at the target position. Any amplitude
    found at the target is removed from the surviving state (absorbing boundary),
    which yields a first-hit probability distribution across steps.
    """
    if target_position < -steps or target_position > steps:
        raise ValueError("target_position must lie within [-steps, steps].")
    if start_position < -steps or start_position > steps:
        raise ValueError("start_position must lie within [-steps, steps].")

    rng = np.random.default_rng(seed)
    positions = 2 * steps + 1
    center = steps
    target_index = center + target_position
    start_index = center + start_position

    state = np.zeros((positions, 2), dtype=complex)
    state[start_index, 0] = 1 / np.sqrt(2)
    state[start_index, 1] = 1j / np.sqrt(2)

    hadamard = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]])
    first_hit_probabilities = np.zeros(steps)

    for step in range(steps):
        state = state @ hadamard

        next_state = np.zeros_like(state)
        next_state[:-1, 0] = state[1:, 0]
        next_state[1:, 1] = state[:-1, 1]
        state = next_state

        hit_probability = np.abs(state[target_index, 0]) ** 2 + np.abs(state[target_index, 1]) ** 2
        first_hit_probabilities[step] = hit_probability

        state[target_index, :] = 0.0
        remaining_norm = np.sum(np.abs(state) ** 2)
        if remaining_norm > 0:
            state /= np.sqrt(remaining_norm)

    cumulative_hit_probabilities = np.cumsum(first_hit_probabilities)
    success_probability = float(cumulative_hit_probabilities[-1]) if steps > 0 else 0.0

    miss_probability = max(0.0, 1.0 - success_probability)
    sampling_probs = np.concatenate([first_hit_probabilities, np.array([miss_probability])])
    sampling_probs = sampling_probs / np.sum(sampling_probs)

    sampled = rng.choice(np.arange(1, steps + 2), size=shots, p=sampling_probs)
    hit_times = sampled.astype(float)
    hit_times[hit_times == (steps + 1)] = np.nan

    return {
        "first_hit_probabilities": first_hit_probabilities,
        "cumulative_hit_probabilities": cumulative_hit_probabilities,
        "success_probability": success_probability,
        "hit_times": hit_times,
    }


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