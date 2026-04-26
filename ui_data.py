"""UI data adapters - wraps existing simulation logic for reuse."""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Any

from classical_walk import (
    classical_graph_target_search,
    classical_cumulative_hit_probability,
)
from quantum_walk import quantum_graph_target_search
from graph_topology import (
    corridor_graph,
    grid_graph,
    graph_from_adjacency,
    shortest_path_distances,
    select_node_at_distance,
)


@dataclass
class SimulationResult:
    """Result container for a single scenario run."""
    scenario_name: str
    distance_label: str
    distance: int
    target_node: int
    classical_cumulative: np.ndarray
    quantum_cumulative: np.ndarray
    classical_stats: Dict[str, float]
    quantum_stats: Dict[str, float]
    speedup: float
    steps: int


def summarize_hit_times(hit_times: np.ndarray) -> Dict[str, float]:
    """Summarize hitting time statistics."""
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


def safe_speedup(classical_mean: float, quantum_mean: float) -> float:
    """Calculate speedup, handling edge cases."""
    if not np.isfinite(classical_mean) or not np.isfinite(quantum_mean) or quantum_mean == 0:
        return np.nan
    return classical_mean / quantum_mean


def get_scenarios() -> List[Dict[str, Any]]:
    """Return available graph scenarios."""
    return [
        {
            "name": "corridor-41",
            "graph": corridor_graph(41, name="corridor-41"),
            "start_node": 20,
            "label": "Corridor (41 nodes)",
        },
        {
            "name": "grid-7x7",
            "graph": grid_graph(7, 7, name="grid-7x7"),
            "start_node": 24,
            "label": "Grid (7×7)",
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
            "label": "Branch Network",
        },
    ]


def pick_distance_levels(graph, start_node: int) -> List[Dict[str, Any]]:
    """Pick near/mid/far distance targets."""
    distances = shortest_path_distances(graph, start_node)
    positive_distances = sorted({distance for distance in distances if distance > 0})

    if len(positive_distances) < 3:
        raise ValueError(f"Graph {graph.name} does not expose enough distance levels.")

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


def run_single_scenario(
    scenario: Dict[str, Any],
    steps: int = 60,
    trials: int = 4000,
    shots: int = 4000,
    seed: int = 42,
    distance_mode: str = "all",  # 'all', 'near', 'mid', 'far'
) -> List[SimulationResult]:
    """Run simulation for a single scenario, optionally filtering distance."""
    graph = scenario["graph"]
    start_node = scenario["start_node"]
    levels = pick_distance_levels(graph, start_node)

    # Filter levels if specific distance requested
    if distance_mode != "all":
        levels = [l for l in levels if l["label"] == distance_mode]

    results = []

    for offset, level in enumerate(levels):
        target_seed = seed + offset

        # Run classical walk
        classical_hit_times = classical_graph_target_search(
            graph,
            steps=steps,
            trials=trials,
            target_node=level["target_node"],
            start_node=start_node,
            seed=target_seed,
        )

        # Run quantum walk
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
            SimulationResult(
                scenario_name=scenario["name"],
                distance_label=level["label"],
                distance=level["distance"],
                target_node=level["target_node"],
                classical_cumulative=classical_cumulative_hit_probability(classical_hit_times, steps),
                quantum_cumulative=quantum_results["cumulative_hit_probabilities"],
                classical_stats=classical_stats,
                quantum_stats=quantum_stats,
                speedup=safe_speedup(classical_stats["mean"], quantum_stats["mean"]),
                steps=steps,
            )
        )

    return results


def get_graph_for_visualization(scenario_name: str):
    """Get graph object for visualization."""
    scenarios = {s["name"]: s for s in get_scenarios()}
    if scenario_name in scenarios:
        return scenarios[scenario_name]["graph"], scenarios[scenario_name]["start_node"]
    return None, None
