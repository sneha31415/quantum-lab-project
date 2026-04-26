import numpy as np
import matplotlib.pyplot as plt

from graph_topology import GraphTopology, corridor_graph


def classical_random_walk(steps=50, trials=1000):
    final_positions = []

    for _ in range(trials):
        position = 0

        for _ in range(steps):
            step = np.random.choice([-1, 1])  # left or right
            position += step

        final_positions.append(position)

    return final_positions


def classical_target_search(steps=60, trials=5000, target_position=20, start_position=0, seed=None):
    """Run repeated classical random-walk searches and return first hitting times.

    Hitting time is the first step when the walker reaches target_position.
    If target is not reached within "steps", the corresponding entry is np.nan.
    """
    rng = np.random.default_rng(seed)
    hit_times = np.full(trials, np.nan)

    for trial in range(trials):
        position = start_position
        for step in range(1, steps + 1):
            position += rng.choice([-1, 1])
            if position == target_position:
                hit_times[trial] = step
                break

    return hit_times


def classical_graph_target_search(
    graph: GraphTopology,
    steps=60,
    trials=5000,
    target_node=0,
    start_node=0,
    seed=None,
):
    """Run repeated classical random-walk searches on a graph and return first hitting times."""
    rng = np.random.default_rng(seed)
    hit_times = np.full(trials, np.nan)

    if start_node == target_node:
        hit_times.fill(0.0)
        return hit_times

    for trial in range(trials):
        node = start_node

        for step in range(1, steps + 1):
            neighbors = graph.neighbors(node)
            if not neighbors:
                break

            node = int(rng.choice(neighbors))
            if node == target_node:
                hit_times[trial] = step
                break

    return hit_times


def classical_cumulative_hit_probability(hit_times, steps):
    """Return cumulative probability of hitting target by each step."""
    cumulative = np.zeros(steps)

    for step in range(1, steps + 1):
        cumulative[step - 1] = float(np.mean(np.isfinite(hit_times) & (hit_times <= step)))

    return cumulative



def plot_classical(results, steps):
    plt.hist(results, bins=range(-steps, steps + 2), density=True)
    plt.title("Classical Random Walk Distribution")
    plt.xlabel("Position")
    plt.ylabel("Probability")
    plt.show()

# if __name__ == "__main__":
#     steps = 50
#     results = classical_random_walk(steps=steps)
    
#     print(results[:10])
#     plot_classical(results, steps)