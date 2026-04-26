import numpy as np
import matplotlib.pyplot as plt


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


def classical_cumulative_hit_probability(hit_times, steps):
    """Return cumulative probability of hitting target by each step."""
    cumulative = np.zeros(steps)
    finite_hits = hit_times[np.isfinite(hit_times)]

    for step in range(1, steps + 1):
        cumulative[step - 1] = np.mean(finite_hits <= step) if finite_hits.size else 0.0

    # The mean above is over successful trials only; convert to total-trial probability.
    success_rate = np.mean(np.isfinite(hit_times))
    return cumulative * success_rate



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