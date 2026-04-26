import numpy as np
import matplotlib.pyplot as plt

from classical_walk import classical_cumulative_hit_probability, classical_graph_target_search
from graph_topology import corridor_graph, graph_from_adjacency, grid_graph, shortest_path_distances, select_node_at_distance
from quantum_walk import quantum_graph_target_search


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


def safe_speedup(classical_mean, quantum_mean):
    if not np.isfinite(classical_mean) or not np.isfinite(quantum_mean) or quantum_mean == 0:
        return np.nan
    return classical_mean / quantum_mean


def pick_distance_levels(graph, start_node):
    distances = shortest_path_distances(graph, start_node)
    positive_distances = sorted({distance for distance in distances if distance > 0})

    if len(positive_distances) < 3:
        raise ValueError(f"Graph {graph.name} does not expose enough distance levels for a sweep.")

    chosen_distances = [
        positive_distances[0],
        positive_distances[len(positive_distances) // 2],
        positive_distances[-1],
    ]

    levels = []
    for label, distance in zip(("near", "mid", "far"), chosen_distances):
        levels.append(
            {
                "label": label,
                "distance": distance,
                "target_node": select_node_at_distance(graph, start_node, distance),
            }
        )

    return levels


def build_scenarios():
    return [
        {
            "name": "corridor-41",
            "graph": corridor_graph(41, name="corridor-41"),
            "start_node": 20,
        },
        {
            "name": "grid-7x7",
            "graph": grid_graph(7, 7, name="grid-7x7"),
            "start_node": 24,
        },
        {
            "name": "branch-network",
            "graph": graph_from_adjacency(
                [
                    (1, 2),
                    (0, 3, 4),
                    (0, 4),
                    (1, 5),
                    (1, 2, 5, 6),
                    (3, 4, 7),
                    (4, 7, 8),
                    (5, 6, 8),
                    (6, 7),
                ],
                name="branch-network",
            ),
            "start_node": 0,
        },
    ]


def run_sweep_for_scenario(scenario, steps, trials, shots, seed):
    graph = scenario["graph"]
    start_node = scenario["start_node"]
    levels = pick_distance_levels(graph, start_node)
    results = []

    for offset, level in enumerate(levels):
        target_seed = seed + offset
        classical_hit_times = classical_graph_target_search(
            graph,
            steps=steps,
            trials=trials,
            target_node=level["target_node"],
            start_node=start_node,
            seed=target_seed,
        )
        quantum_results = quantum_graph_target_search(
            graph,
            steps=steps,
            target_node=level["target_node"],
            start_node=start_node,
            shots=shots,
            seed=target_seed,
        )

        classical_stats = summarize_hit_times(classical_hit_times)
        quantum_stats = summarize_hit_times(quantum_results["hit_times"])

        results.append(
            {
                "scenario": scenario["name"],
                "distance_label": level["label"],
                "distance": level["distance"],
                "target_node": level["target_node"],
                "classical_hit_times": classical_hit_times,
                "quantum_hit_times": quantum_results["hit_times"],
                "classical_cumulative": classical_cumulative_hit_probability(classical_hit_times, steps),
                "quantum_cumulative": quantum_results["cumulative_hit_probabilities"],
                "classical_stats": classical_stats,
                "quantum_stats": quantum_stats,
                "speedup": safe_speedup(classical_stats["mean"], quantum_stats["mean"]),
            }
        )

    return results


def main():
    steps = 60
    classical_trials = 4000
    quantum_shots = 4000
    seed = 42

    scenarios = build_scenarios()
    experiment_rows = []

    for scenario_index, scenario in enumerate(scenarios):
        experiment_rows.extend(
            run_sweep_for_scenario(
                scenario,
                steps=steps,
                trials=classical_trials,
                shots=quantum_shots,
                seed=seed + 100 * scenario_index,
            )
        )

    speedup_table = {
        row["scenario"]: {"near": np.nan, "mid": np.nan, "far": np.nan} for row in experiment_rows
    }
    for row in experiment_rows:
        speedup_table[row["scenario"]][row["distance_label"]] = row["speedup"]

    representative_rows = [row for row in experiment_rows if row["scenario"] == "corridor-41"]

    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    axes = axes.flatten()

    scenario_names = [scenario["name"] for scenario in scenarios]
    x_positions = np.arange(len(scenario_names))
    bar_width = 0.24
    distance_labels = ["near", "mid", "far"]
    colors = {"near": "#3b82f6", "mid": "#10b981", "far": "#f97316"}

    for offset, label in enumerate(distance_labels):
        values = [speedup_table[name][label] for name in scenario_names]
        axes[0].bar(x_positions + (offset - 1) * bar_width, values, width=bar_width, label=label.title(), color=colors[label])

    axes[0].set_title("Mean-Hitting-Time Speedup by Map and Target Distance")
    axes[0].set_xlabel("Map")
    axes[0].set_ylabel("Classical mean / Quantum mean")
    axes[0].set_xticks(x_positions)
    axes[0].set_xticklabels(scenario_names, rotation=15)
    axes[0].grid(axis="y", alpha=0.25)
    axes[0].legend()

    for row in representative_rows:
        steps_axis = np.arange(1, steps + 1)
        axes[1].plot(
            steps_axis,
            row["classical_cumulative"],
            linestyle="--",
            linewidth=1.8,
            color=colors[row["distance_label"]],
            label=f"Classical {row['distance_label']} (d={row['distance']})",
        )
        axes[1].plot(
            steps_axis,
            row["quantum_cumulative"],
            linewidth=2.2,
            color=colors[row["distance_label"]],
            label=f"Quantum {row['distance_label']} (d={row['distance']})",
        )

    axes[1].set_title("Corridor Cumulative Hit Probability")
    axes[1].set_xlabel("Step")
    axes[1].set_ylabel("P(hit by step)")
    axes[1].set_ylim(0.0, 1.0)
    axes[1].grid(alpha=0.25)
    axes[1].legend(fontsize=8, ncol=2)

    axes[2].axis("off")
    lines = ["Distance sweep summary"]
    for row in experiment_rows:
        lines.append(
            f"{row['scenario']:<14} {row['distance_label']:<4} d={row['distance']:<2} "
            f"succ(C/Q)={row['classical_stats']['success_rate']:.2f}/{row['quantum_stats']['success_rate']:.2f} "
            f"mean(C/Q)={row['classical_stats']['mean']:.2f}/{row['quantum_stats']['mean']:.2f} "
            f"speedup={row['speedup']:.2f}x"
        )

    axes[2].text(
        0.02,
        0.98,
        "\n".join(lines),
        va="top",
        fontsize=9.5,
        family="monospace",
        bbox={"boxstyle": "round", "facecolor": "whitesmoke", "edgecolor": "lightgray"},
    )

    axes[3].axis("off")
    overall_speedups = [row["speedup"] for row in experiment_rows if np.isfinite(row["speedup"])]
    overall_summary = (
        f"Maps: {', '.join(scenario_names)}\n"
        f"Step budget: {steps}\n"
        f"Trials / shots: {classical_trials} / {quantum_shots}\n\n"
        f"Average speedup: {np.mean(overall_speedups):.2f}x\n"
        f"Best speedup: {np.max(overall_speedups):.2f}x\n"
        f"Worst speedup: {np.min(overall_speedups):.2f}x"
    )
    axes[3].text(
        0.02,
        0.98,
        overall_summary,
        va="top",
        fontsize=11,
        bbox={"boxstyle": "round", "facecolor": "lavender", "edgecolor": "lightgray"},
    )

    plt.tight_layout()
    output_path = "graph_target_search_benchmark.png"
    plt.savefig(output_path, dpi=160)
    print("Saved benchmark plot to", output_path)
    for row in experiment_rows:
        print(
            f"{row['scenario']} / {row['distance_label']} (d={row['distance']}): "
            f"classical_mean={row['classical_stats']['mean']:.4f}, "
            f"quantum_mean={row['quantum_stats']['mean']:.4f}, "
            f"speedup={row['speedup']:.4f}x"
        )


if __name__ == "__main__":
    main()