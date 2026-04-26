import numpy as np
import matplotlib.pyplot as plt

from classical_walk import classical_target_search, classical_cumulative_hit_probability
from quantum_walk import quantum_target_search


def summarize_hit_times(hit_times):
    successful = hit_times[np.isfinite(hit_times)]
    success_rate = float(np.mean(np.isfinite(hit_times)))

    if successful.size == 0:
        return {
            "success_rate": success_rate,
            "mean": np.nan,
            "median": np.nan,
            "std": np.nan,
        }

    return {
        "success_rate": success_rate,
        "mean": float(np.mean(successful)),
        "median": float(np.median(successful)),
        "std": float(np.std(successful)),
    }


def main():
    steps = 80
    target_position = 30
    classical_trials = 8000
    quantum_shots = 8000
    seed = 42

    classical_hit_times = classical_target_search(
        steps=steps,
        trials=classical_trials,
        target_position=target_position,
        seed=seed,
    )
    classical_cumulative = classical_cumulative_hit_probability(classical_hit_times, steps)

    quantum_results = quantum_target_search(
        steps=steps,
        target_position=target_position,
        shots=quantum_shots,
        seed=seed,
    )
    quantum_hit_times = quantum_results["hit_times"]
    quantum_cumulative = quantum_results["cumulative_hit_probabilities"]

    classical_stats = summarize_hit_times(classical_hit_times)
    quantum_stats = summarize_hit_times(quantum_hit_times)

    speedup = classical_stats["mean"] / quantum_stats["mean"]
    steps_axis = np.arange(1, steps + 1)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    axes[0].plot(steps_axis, classical_cumulative, label="Classical", linewidth=2)
    axes[0].plot(steps_axis, quantum_cumulative, label="Quantum", linewidth=2)
    axes[0].set_title("Cumulative Hit Probability")
    axes[0].set_xlabel("Step")
    axes[0].set_ylabel("P(hit by step)")
    axes[0].set_ylim(0.0, 1.0)
    axes[0].grid(alpha=0.25)
    axes[0].legend()

    classical_success = classical_hit_times[np.isfinite(classical_hit_times)]
    quantum_success = quantum_hit_times[np.isfinite(quantum_hit_times)]
    axes[1].hist(classical_success, bins=25, alpha=0.65, label="Classical")
    axes[1].hist(quantum_success, bins=25, alpha=0.65, label="Quantum")
    axes[1].set_title("First Hitting Time Distribution")
    axes[1].set_xlabel("Hitting Time (steps)")
    axes[1].set_ylabel("Frequency")
    axes[1].grid(alpha=0.25)
    axes[1].legend()

    axes[2].axis("off")
    summary_text = (
        f"Map: 1D corridor\n"
        f"Target position: {target_position}\n"
        f"Step budget: {steps}\n\n"
        f"Classical success: {classical_stats['success_rate']:.3f}\n"
        f"Quantum success:   {quantum_stats['success_rate']:.3f}\n\n"
        f"Classical mean hit time: {classical_stats['mean']:.2f}\n"
        f"Quantum mean hit time:   {quantum_stats['mean']:.2f}\n"
        f"Estimated speedup: {speedup:.2f}x"
    )
    axes[2].text(
        0.02,
        0.98,
        summary_text,
        va="top",
        fontsize=11,
        bbox={"boxstyle": "round", "facecolor": "whitesmoke", "edgecolor": "lightgray"},
    )

    plt.tight_layout()
    output_path = "target_search_benchmark.png"
    plt.savefig(output_path, dpi=160)
    print("Saved benchmark plot to", output_path)
    print("Classical success rate:", round(classical_stats["success_rate"], 4))
    print("Quantum success rate:", round(quantum_stats["success_rate"], 4))
    print("Classical mean hitting time:", round(classical_stats["mean"], 4))
    print("Quantum mean hitting time:", round(quantum_stats["mean"], 4))
    print("Estimated speedup:", round(speedup, 4), "x")


if __name__ == "__main__":
    main()