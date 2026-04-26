from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class GraphTopology:
    adjacency: tuple[tuple[int, ...], ...]
    coordinates: tuple[tuple[int, ...] | None, ...] | None = None
    name: str = "graph"

    def __post_init__(self):
        normalized_adjacency = []
        node_count = len(self.adjacency)

        for node, neighbors in enumerate(self.adjacency):
            cleaned_neighbors = tuple(sorted({int(neighbor) for neighbor in neighbors}))
            for neighbor in cleaned_neighbors:
                if neighbor < 0 or neighbor >= node_count:
                    raise ValueError(f"Neighbor {neighbor} for node {node} is out of range.")
            normalized_adjacency.append(cleaned_neighbors)

        object.__setattr__(self, "adjacency", tuple(normalized_adjacency))

        if self.coordinates is not None:
            coordinates = tuple(self.coordinates)
            if len(coordinates) != node_count:
                raise ValueError("coordinates must match the number of graph nodes.")
            object.__setattr__(self, "coordinates", coordinates)

    @property
    def num_nodes(self) -> int:
        return len(self.adjacency)

    def neighbors(self, node: int) -> tuple[int, ...]:
        return self.adjacency[node]

    def degree(self, node: int) -> int:
        return len(self.adjacency[node])


def graph_from_adjacency(adjacency: Sequence[Iterable[int]], name: str = "graph") -> GraphTopology:
    return GraphTopology(tuple(tuple(neighbors) for neighbors in adjacency), name=name)


def corridor_graph(num_nodes: int, name: str = "corridor") -> GraphTopology:
    if num_nodes < 2:
        raise ValueError("corridor_graph requires at least 2 nodes.")

    adjacency = []
    coordinates = []
    for node in range(num_nodes):
        neighbors = []
        if node > 0:
            neighbors.append(node - 1)
        if node < num_nodes - 1:
            neighbors.append(node + 1)
        adjacency.append(tuple(neighbors))
        coordinates.append((node,))

    return GraphTopology(tuple(adjacency), coordinates=tuple(coordinates), name=name)


def grid_graph(rows: int, cols: int, name: str | None = None) -> GraphTopology:
    if rows < 2 or cols < 2:
        raise ValueError("grid_graph requires at least a 2x2 grid.")

    adjacency: list[tuple[int, ...]] = []
    coordinates: list[tuple[int, int]] = []

    for row in range(rows):
        for col in range(cols):
            node = row * cols + col
            neighbors = []
            if row > 0:
                neighbors.append((row - 1) * cols + col)
            if row < rows - 1:
                neighbors.append((row + 1) * cols + col)
            if col > 0:
                neighbors.append(row * cols + col - 1)
            if col < cols - 1:
                neighbors.append(row * cols + col + 1)

            if len(adjacency) != node:
                raise RuntimeError("grid_graph construction order is inconsistent.")

            adjacency.append(tuple(neighbors))
            coordinates.append((row, col))

    return GraphTopology(tuple(adjacency), coordinates=tuple(coordinates), name=name or f"grid-{rows}x{cols}")


def shortest_path_distances(graph: GraphTopology, start_node: int) -> list[int]:
    if start_node < 0 or start_node >= graph.num_nodes:
        raise ValueError("start_node is out of range.")

    distances = [-1] * graph.num_nodes
    distances[start_node] = 0
    frontier = deque([start_node])

    while frontier:
        node = frontier.popleft()
        for neighbor in graph.neighbors(node):
            if distances[neighbor] == -1:
                distances[neighbor] = distances[node] + 1
                frontier.append(neighbor)

    return distances


def nodes_at_distance(graph: GraphTopology, start_node: int, distance: int) -> list[int]:
    distances = shortest_path_distances(graph, start_node)
    return [node for node, node_distance in enumerate(distances) if node_distance == distance]


def select_node_at_distance(graph: GraphTopology, start_node: int, distance: int) -> int:
    candidates = nodes_at_distance(graph, start_node, distance)
    if not candidates:
        raise ValueError(f"No node exists at distance {distance} from start node {start_node}.")
    return max(candidates)