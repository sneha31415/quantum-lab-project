"""UI components - charts, cards, and graph visualization."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import networkx as nx
from typing import Dict, Any, List, Optional

from ui_data import SimulationResult
from graph_topology import GraphTopology


def render_kpi_card(label: str, value: Any, subtitle: str = "", is_metric: bool = False):
    """Render a KPI card with label, value, and optional subtitle."""
    with st.container(border=True):
        st.metric(label, f"{value:.2f}" if isinstance(value, float) and not np.isnan(value) else str(value))
        if subtitle:
            st.caption(subtitle)


def render_speedup_card(speedup: float, classical_mean: float, quantum_mean: float):
    """Render highlighted speedup card."""
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Speedup", f"{speedup:.2f}×" if np.isfinite(speedup) else "N/A")
        with col2:
            if np.isfinite(speedup):
                improvement = (speedup - 1) * 100
                st.metric("Improvement", f"{improvement:.0f}%")
        
        st.caption(f"Classical: {classical_mean:.1f} steps | Quantum: {quantum_mean:.1f} steps")


def plot_cumulative_hit_probability(result: SimulationResult) -> go.Figure:
    """Create interactive cumulative hit probability plot."""
    steps = np.arange(1, result.steps + 1)
    
    fig = go.Figure()
    
    # Classical curve (dashed, cool tone)
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=result.classical_cumulative,
            mode="lines",
            name="Classical",
            line=dict(color="#3498db", width=3, dash="dash"),
            fill="tozeroy",
            fillcolor="rgba(52, 152, 219, 0.1)",
        )
    )
    
    # Quantum curve (solid, warm tone)
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=result.quantum_cumulative,
            mode="lines",
            name="Quantum",
            line=dict(color="#e74c3c", width=3),
            fill="tozeroy",
            fillcolor="rgba(231, 76, 60, 0.1)",
        )
    )
    
    fig.update_layout(
        title=f"Cumulative Hit Probability — {result.scenario_name} ({result.distance_label} target)",
        xaxis_title="Steps",
        yaxis_title="Hit Probability",
        hovermode="x unified",
        template="plotly_white",
        height=400,
        showlegend=True,
        legend=dict(x=0.02, y=0.98),
    )
    
    return fig


def plot_success_rate_comparison(results: List[SimulationResult]) -> go.Figure:
    """Create bar chart comparing success rates."""
    distances = [r.distance_label.title() for r in results]
    classical_success = [r.classical_stats["success_rate"] * 100 for r in results]
    quantum_success = [r.quantum_stats["success_rate"] * 100 for r in results]
    
    fig = go.Figure(
        data=[
            go.Bar(name="Classical", x=distances, y=classical_success, marker_color="#3498db"),
            go.Bar(name="Quantum", x=distances, y=quantum_success, marker_color="#e74c3c"),
        ]
    )
    
    fig.update_layout(
        title="Success Rate Comparison (%)",
        xaxis_title="Target Distance",
        yaxis_title="Success Rate (%)",
        template="plotly_white",
        height=350,
        barmode="group",
        hovermode="x unified",
    )
    
    return fig


def plot_mean_hitting_time_comparison(results: List[SimulationResult]) -> go.Figure:
    """Create bar chart comparing mean hitting times."""
    distances = [r.distance_label.title() for r in results]
    classical_means = [r.classical_stats["mean"] for r in results]
    quantum_means = [r.quantum_stats["mean"] for r in results]
    
    fig = go.Figure(
        data=[
            go.Bar(name="Classical", x=distances, y=classical_means, marker_color="#3498db"),
            go.Bar(name="Quantum", x=distances, y=quantum_means, marker_color="#e74c3c"),
        ]
    )
    
    fig.update_layout(
        title="Mean Hitting Time Comparison",
        xaxis_title="Target Distance",
        yaxis_title="Mean Steps to Target",
        template="plotly_white",
        height=350,
        barmode="group",
        hovermode="x unified",
    )
    
    return fig


def plot_speedup_comparison(results: List[SimulationResult]) -> go.Figure:
    """Create bar chart showing speedup across distances."""
    distances = [r.distance_label.title() for r in results]
    speedups = [r.speedup if np.isfinite(r.speedup) else 0 for r in results]
    colors = ["#27ae60" if s > 1 else "#e74c3c" for s in speedups]
    
    fig = go.Figure(
        data=[go.Bar(x=distances, y=speedups, marker_color=colors)]
    )
    
    fig.update_layout(
        title="Quantum Speedup (Classical / Quantum)",
        xaxis_title="Target Distance",
        yaxis_title="Speedup Factor",
        template="plotly_white",
        height=350,
        hovermode="x unified",
    )
    
    fig.add_hline(y=1, line_dash="dash", line_color="gray", annotation_text="No speedup")
    
    return fig


def plot_graph_topology(
    graph: GraphTopology,
    start_node: int,
    target_node: Optional[int] = None,
) -> go.Figure:
    """Visualize graph topology with NetworkX and Plotly."""
    # Convert to NetworkX graph
    G = nx.Graph()
    G.add_nodes_from(range(graph.num_nodes))
    
    for node, neighbors in enumerate(graph.adjacency):
        for neighbor in neighbors:
            if neighbor > node:  # Avoid duplicate edges
                G.add_edge(node, neighbor)
    
    # Use spring layout for visualization
    pos = nx.spring_layout(G, k=1, iterations=50, seed=42)
    
    # Extract edges
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
    
    # Create edge trace
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(width=1, color="#888"),
        hoverinfo="none",
        showlegend=False,
    )
    
    # Color nodes based on role
    node_colors = []
    node_sizes = []
    for node in G.nodes():
        if node == start_node:
            node_colors.append("#3498db")  # Blue for start
            node_sizes.append(15)
        elif node == target_node:
            node_colors.append("#e74c3c")  # Red for target
            node_sizes.append(15)
        else:
            node_colors.append("#95a5a6")  # Gray for others
            node_sizes.append(10)
    
    # Create node trace
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=[str(node) for node in G.nodes()],
        textposition="top center",
        hoverinfo="text",
        hovertext=[f"Node {node}" for node in G.nodes()],
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color="white"),
        ),
        showlegend=False,
    )
    
    fig = go.Figure(data=[edge_trace, node_trace])
    
    fig.update_layout(
        title=f"Graph Topology — {graph.name}",
        showlegend=False,
        hovermode="closest",
        template="plotly_white",
        height=400,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )
    
    # Add legend annotations
    fig.add_annotation(
        text="🔵 Start  🔴 Target",
        xref="paper",
        yref="paper",
        x=0.02,
        y=0.98,
        showarrow=False,
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="black",
        borderwidth=1,
    )
    
    return fig


def render_summary_table(results: List[SimulationResult]):
    """Render summary statistics table."""
    data = []
    for result in results:
        data.append({
            "Distance": result.distance_label.title(),
            "Target Node": result.target_node,
            "Classical Success %": f"{result.classical_stats['success_rate']*100:.1f}%",
            "Quantum Success %": f"{result.quantum_stats['success_rate']*100:.1f}%",
            "Classical Mean": f"{result.classical_stats['mean']:.1f}",
            "Quantum Mean": f"{result.quantum_stats['mean']:.1f}",
            "Speedup": f"{result.speedup:.2f}×" if np.isfinite(result.speedup) else "N/A",
        })
    
    st.dataframe(data, use_container_width=True, hide_index=True)
