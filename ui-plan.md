Goal
Create an interactive, demo-ready dashboard where users can explore Classical vs Quantum walk behavior across corridor, grid, and branch-network maps.

Phase 1: Define MVP Scope (Day 1)

Pick stack: Streamlit + Plotly + NetworkX.
Freeze MVP features:
Map selector (corridor/grid/branch-network)
Start node + target distance selector (near/mid/far)
Run simulation button
Side-by-side Classical vs Quantum cumulative hit plots
KPI cards: success rate, mean hitting time, speedup
Keep simulation logic unchanged; only add a UI layer.
Phase 2: Refactor for Reuse (Day 1-2)

Extract benchmark orchestration into reusable functions.
Add a UI-friendly result schema that returns:
scenario metadata
per-step cumulative arrays
summary stats
speedup
Ensure deterministic runs through visible seed input.
Phase 3: Build Core UI (Day 2-3)

Left control panel:
map type
rows/cols or corridor size
start node
target mode (near/mid/far or manual)
steps, trials, shots, seed
Main panel tabs:
Graph View
Probability Curves
Summary
Run interaction:
spinner while compute runs
cached results for same parameter set
validation messages for invalid settings
Phase 4: Visual Design for Demo Impact (Day 3)

Use a clear visual language:
clean light theme
strong contrast colors
consistent mapping (Classical dashed cool tone, Quantum solid warm tone)
Add polished elements:
animated curve reveal over steps
highlighted Speedup Card with one-line takeaway
Graph view:
node-edge map with start and target emphasis
optional node label toggle
Phase 5: Fun Interaction Layer (Day 4)

Add preset buttons:
Quick Win
Balanced Case
Hard Target
Add Race Mode:
progress bars for cumulative hit probability at selected step
Add step scrubber:
slider to inspect state by step
Phase 6: Validation + Demo Packaging (Day 4-5)

Accuracy checks:
compare UI stats against CLI outputs
verify reproducibility with fixed seed
Performance checks:
target under 2-4 seconds for common presets
reduced trials/shots for live demo mode if needed
Demo prep:
one-command run
static image fallback
short 3-scenario script
Suggested File Structure

app.py (Streamlit entrypoint)
ui_data.py (simulation adapters)
ui_components.py (charts/cards/graph drawing)
ui_presets.py (demo presets)
Success Criteria

User can run at least 3 scenarios without editing code.
UI shows Quantum vs Classical differences quickly.
Final summary communicates speedup clearly.
Demo Script (2-3 minutes)

Run corridor far-target preset.
Show cumulative curves and speedup card.
Switch to grid preset and compare outcomes.
End with branch-network case and conclude practical takeaway.
