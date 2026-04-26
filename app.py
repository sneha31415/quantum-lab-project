"""Streamlit app — Interactive dashboard for Quantum vs Classical Random Walk comparison."""

import streamlit as st
import numpy as np
from typing import Optional

from ui_data import get_scenarios, run_single_scenario, get_graph_for_visualization
from ui_components import (
    plot_cumulative_hit_probability,
    plot_success_rate_comparison,
    plot_mean_hitting_time_comparison,
    plot_speedup_comparison,
    plot_graph_topology,
    render_kpi_card,
    render_speedup_card,
    render_summary_table,
)


# Page config
st.set_page_config(
    page_title="Random Walk Target Search",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; }
    .kpi-container { padding: 20px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def main():
    st.title("Random Walk Target Search")
    st.markdown("Explore the power of quantum walks across different graph topologies")

    scenarios = get_scenarios()
    scenario_lookup = {scenario["name"]: index for index, scenario in enumerate(scenarios)}
    preset_defaults = {
        "steps": 60,
        "trials": 3000,
        "shots": 3000,
        "distance_mode": "all",
    }

    # ===== SIDEBAR: Configuration =====
    with st.sidebar:
        st.header("⚙️ Configuration")

        preset_mode = st.radio("Choose mode:", ["Preset", "Custom"])

        if preset_mode == "Preset":
            graph_choice = st.selectbox(
                "Choose graph:",
                options=["corridor", "grid", "branch network"],
                format_func=lambda choice: {
                    "corridor": "Corridor",
                    "grid": "Grid",
                    "branch network": "Branch Network",
                }[choice],
            )

            scenario_name = {
                "corridor": "corridor-41",
                "grid": "grid-7x7",
                "branch network": "branch-network",
            }[graph_choice]
            scenario_key = scenario_lookup[scenario_name]

            config = preset_defaults.copy()
            st.caption("Preset mode uses fixed demo values: 60 steps, 3000 trials, and Target Distance = All.")
        else:
            # Custom configuration
            scenario_idx = st.selectbox(
                "Select graph:",
                range(len(scenarios)),
                format_func=lambda i: scenarios[i]["label"],
            )
            scenario_key = scenario_idx
            
            config = {
                "steps": st.slider("Steps:", 20, 100, 60, step=10),
                "trials": st.slider("Classical Trials:", 1000, 5000, 4000, step=500),
                "shots": st.slider("Quantum Shots:", 1000, 5000, 4000, step=500),
                "distance_mode": st.selectbox(
                    "Target Distance:",
                    ["all", "near", "mid", "far"],
                    format_func=lambda x: {
                        "all": "All Distances",
                        "near": "Near",
                        "mid": "Mid",
                        "far": "Far",
                    }[x],
                ),
            }
        
        st.divider()
        seed = st.number_input("Random Seed:", min_value=0, max_value=1000000, value=42)
        
        st.divider()
        run_button = st.button("▶️ Run Simulation", key="run_btn", use_container_width=True)

    # ===== MAIN CONTENT =====

    # Get selected scenario
    selected_scenario = scenarios[scenario_key]
    
    # Run simulation on button click
    if run_button:
        with st.spinner("⏳ Running simulation..."):
            try:
                results = run_single_scenario(
                    scenario=selected_scenario,
                    steps=config["steps"],
                    trials=config["trials"],
                    shots=config["shots"],
                    seed=seed,
                    distance_mode=config["distance_mode"],
                )
                st.session_state.last_results = results
                st.session_state.last_scenario = selected_scenario
            except Exception as e:
                st.error(f"Error during simulation: {e}")
                return
    
    # Display results
    if "last_results" in st.session_state:
        results = st.session_state.last_results
        scenario = st.session_state.last_scenario
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Probability Curves",
            "📈 Comparisons",
            "🗺️ Graph View",
            "📋 Summary",
        ])
        
        with tab1:
            st.subheader("Cumulative Hit Probability")
            st.markdown(
                "**Classical** (dashed blue) vs **Quantum** (solid red) — "
                "Lower is faster (reaches target sooner)"
            )
            
            for result in results:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.plotly_chart(
                            plot_cumulative_hit_probability(result),
                            use_container_width=True,
                        )
                    with col2:
                        st.markdown(f"**Target: Node {result.target_node}**")
                        st.markdown(f"Distance: {result.distance} hops")
                        render_speedup_card(
                            result.speedup,
                            result.classical_stats["mean"],
                            result.quantum_stats["mean"],
                        )
        
        with tab2:
            st.subheader("Multi-Distance Comparison")
            
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(
                    plot_success_rate_comparison(results),
                    use_container_width=True,
                )
            with col2:
                st.plotly_chart(
                    plot_mean_hitting_time_comparison(results),
                    use_container_width=True,
                )
            
            st.plotly_chart(
                plot_speedup_comparison(results),
                use_container_width=True,
            )
        
        with tab3:
            st.subheader("Graph Topology")
            
            for result in results:
                with st.container(border=True):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        fig = plot_graph_topology(
                            scenario["graph"],
                            scenario["start_node"],
                            result.target_node,
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    with col2:
                        st.markdown(f"**{scenario['label']}**")
                        st.metric("Nodes", scenario["graph"].num_nodes)
                        st.metric("Target Node", result.target_node)
                        st.metric("Distance", result.distance)
        
        with tab4:
            st.subheader("Summary Statistics")
            render_summary_table(results)
            
            # KPI cards summary
            st.markdown("### Key Metrics (Averaged)")
            avg_classical_mean = np.mean([r.classical_stats["mean"] for r in results])
            avg_quantum_mean = np.mean([r.quantum_stats["mean"] for r in results])
            avg_speedup = np.mean([r.speedup for r in results if np.isfinite(r.speedup)])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                render_kpi_card(
                    "Avg Classical Mean",
                    avg_classical_mean,
                    "steps to target",
                )
            with col2:
                render_kpi_card(
                    "Avg Quantum Mean",
                    avg_quantum_mean,
                    "steps to target",
                )
            with col3:
                render_kpi_card(
                    "Avg Speedup",
                    avg_speedup,
                    "quantum advantage",
                )
    else:
        # Empty state
        st.info(
            "👈 **Configure simulation in the sidebar and click 'Run Simulation'** to see results."
        )
        
        

if __name__ == "__main__":
    main()
