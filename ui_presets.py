"""Demo presets - quick configuration sets for showcasing."""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Preset:
    """Configuration preset for quick demo scenarios."""
    name: str
    description: str
    scenario_name: str
    steps: int
    trials: int
    shots: int
    distance_mode: str  # 'all', 'near', 'mid', 'far'


PRESETS = {
    "quick_win": Preset(
        name="Quick Win",
        description="Fast demo — small graph, few steps, significant speedup",
        scenario_name="corridor-41",
        steps=40,
        trials=2000,
        shots=2000,
        distance_mode="far",
    ),
    "balanced": Preset(
        name="Balanced Case",
        description="Moderate setup — good detail without long runtime",
        scenario_name="grid-7x7",
        steps=50,
        trials=3000,
        shots=3000,
        distance_mode="all",
    ),
    "comprehensive": Preset(
        name="Hard Target",
        description="Comprehensive analysis — longer distances, more trials",
        scenario_name="branch-network",
        steps=60,
        trials=4000,
        shots=4000,
        distance_mode="all",
    ),
}


def get_preset(preset_key: str) -> Preset:
    """Get a preset by key."""
    return PRESETS.get(preset_key)


def get_all_presets() -> Dict[str, Preset]:
    """Get all available presets."""
    return PRESETS


def preset_to_config(preset: Preset) -> Dict[str, Any]:
    """Convert preset to configuration dict."""
    return {
        "steps": preset.steps,
        "trials": preset.trials,
        "shots": preset.shots,
        "distance_mode": preset.distance_mode,
    }
