"""
Rating engine that maps metrics to FIFA-style 0-99 ratings.

Inputs:
- player_metrics.json: {player_id: {metric_name: value, ...}}
- weights: dict for PAC, SHO, PAS, DEF, PHY

Outputs:
- dict of player_id -> {"overall": score, "subratings": {...}}
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Mapping


DEFAULT_WEIGHTS = {
    "PAC": 0.2,
    "SHO": 0.2,
    "PAS": 0.2,
    "DEF": 0.2,
    "PHY": 0.2,
}


@dataclass
class RatingWeights:
    pac: float = DEFAULT_WEIGHTS["PAC"]
    sho: float = DEFAULT_WEIGHTS["SHO"]
    pas: float = DEFAULT_WEIGHTS["PAS"]
    deff: float = DEFAULT_WEIGHTS["DEF"]
    phy: float = DEFAULT_WEIGHTS["PHY"]

    @classmethod
    def from_dict(cls, data: Mapping[str, float]) -> "RatingWeights":
        return cls(
            pac=data.get("PAC", DEFAULT_WEIGHTS["PAC"]),
            sho=data.get("SHO", DEFAULT_WEIGHTS["SHO"]),
            pas=data.get("PAS", DEFAULT_WEIGHTS["PAS"]),
            deff=data.get("DEF", DEFAULT_WEIGHTS["DEF"]),
            phy=data.get("PHY", DEFAULT_WEIGHTS["PHY"]),
        )

    def as_dict(self) -> Dict[str, float]:
        return {"PAC": self.pac, "SHO": self.sho, "PAS": self.pas, "DEF": self.deff, "PHY": self.phy}


def min_max_scale(value: float, min_val: float, max_val: float) -> float:
    if max_val - min_val <= 1e-6:
        return 50.0
    scaled = 99.0 * (value - min_val) / (max_val - min_val)
    return max(0.0, min(99.0, scaled))


def compute_subratings(player_metrics: Mapping[str, float]) -> Dict[str, float]:
    """
    Map raw metrics to FIFA attribute buckets.
    Expected keys (extend as needed):
        - "top_speed_mps"
        - "avg_speed_mps"
        - "pass_accuracy"
        - "shots_on_target"
        - "tackles_won"
        - "distance_m"
    """
    top_speed = player_metrics.get("top_speed_mps", 0.0)
    avg_speed = player_metrics.get("avg_speed_mps", 0.0)
    pass_acc = player_metrics.get("pass_accuracy", 0.0)
    shots_on_target = player_metrics.get("shots_on_target", 0.0)
    tackles_won = player_metrics.get("tackles_won", 0.0)
    distance_m = player_metrics.get("distance_m", 0.0)

    # Simple min-max anchors (can be calibrated)
    pac = min_max_scale(0.7 * top_speed + 0.3 * avg_speed, min_val=3.0, max_val=10.0)
    sho = min_max_scale(shots_on_target, min_val=0, max_val=5)
    pas = min_max_scale(pass_acc, min_val=0.5, max_val=0.95)
    deff = min_max_scale(tackles_won, min_val=0, max_val=8)
    phy = min_max_scale(distance_m, min_val=5000, max_val=13000)  # meters per match

    return {"PAC": pac, "SHO": sho, "PAS": pas, "DEF": deff, "PHY": phy}


def compute_overall(subratings: Dict[str, float], weights: RatingWeights) -> float:
    w = weights.as_dict()
    total = sum(w.values())
    if total <= 1e-6:
        return 0.0
    overall = sum(subratings[k] * w[k] for k in subratings) / total
    return round(overall, 2)


def rate_players_from_metrics(metrics: Mapping[str, Mapping[str, float]], weights_dict: Dict[str, float] = None) -> Dict[str, Dict]:
    """
    Rate players using an in-memory metrics mapping.
    metrics: {player_id: {"top_speed_mps": float, "avg_speed_mps": float, ...}}
    """
    weights = RatingWeights.from_dict(weights_dict or {})
    results: Dict[str, Dict] = {}
    for player_id, player_metrics in metrics.items():
        sub = compute_subratings(player_metrics)
        overall = compute_overall(sub, weights)
        results[str(player_id)] = {"overall": overall, "subratings": sub}
    return results


def rate_players(metrics_json_path: Path, weights_dict: Dict[str, float] = None) -> Dict[str, Dict]:
    """
    Backwards-compatible wrapper that reads metrics from disk then rates players.
    """
    data = json.loads(Path(metrics_json_path).read_text())
    return rate_players_from_metrics(data, weights_dict=weights_dict)


def save_ratings(ratings: Dict[str, Dict], out_path: Path) -> Path:
    out_path.write_text(json.dumps(ratings, indent=2))
    return out_path
