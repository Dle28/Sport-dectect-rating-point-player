from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np


@dataclass
class PlayerMetrics:
    track_id: int
    team_id: Optional[int] = None
    positions_m: List[Tuple[float, float]] = field(default_factory=list)
    timestamps_s: List[float] = field(default_factory=list)
    distances_m: List[float] = field(default_factory=list)
    speeds_mps: List[float] = field(default_factory=list)

    @property
    def total_distance_m(self) -> float:
        return float(sum(self.distances_m))

    @property
    def latest_speed_mps(self) -> float:
        return float(self.speeds_mps[-1]) if self.speeds_mps else 0.0

    @property
    def top_speed_mps(self) -> float:
        return float(max(self.speeds_mps)) if self.speeds_mps else 0.0

    @property
    def avg_speed_mps(self) -> float:
        if not self.speeds_mps:
            return 0.0
        speeds = self.speeds_mps[1:] if len(self.speeds_mps) > 1 else self.speeds_mps
        return float(np.mean(speeds))


class MetricsAccumulator:
    """Accumulates per-player distance and speed over time."""

    def __init__(self):
        self.players: Dict[int, PlayerMetrics] = {}

    def update(self, track_id: int, position_m: Tuple[float, float], timestamp_s: float, team_id: Optional[int] = None) -> PlayerMetrics:
        player = self.players.get(track_id)
        if player is None:
            player = PlayerMetrics(track_id=track_id, team_id=team_id)
            self.players[track_id] = player

        player.team_id = team_id if team_id is not None else player.team_id
        if player.positions_m:
            prev_pos = np.array(player.positions_m[-1])
            prev_t = player.timestamps_s[-1]
            dt = max(timestamp_s - prev_t, 1e-6)
            dist = float(np.linalg.norm(np.array(position_m) - prev_pos))
            speed = dist / dt
            player.distances_m.append(dist)
            player.speeds_mps.append(speed)
        else:
            player.distances_m.append(0.0)
            player.speeds_mps.append(0.0)

        player.positions_m.append((float(position_m[0]), float(position_m[1])))
        player.timestamps_s.append(float(timestamp_s))
        return player

    def to_json_serializable(self):
        return {
            str(track_id): {
                "team_id": player.team_id,
                "total_distance_m": player.total_distance_m,
                "latest_speed_mps": player.latest_speed_mps,
                "top_speed_mps": player.top_speed_mps,
                "avg_speed_mps": player.avg_speed_mps,
                "positions_m": player.positions_m,
                "timestamps_s": player.timestamps_s,
            }
            for track_id, player in self.players.items()
        }

    def summarize(self) -> Dict[str, Dict[str, float]]:
        """Return lightweight summary metrics keyed by track id (as string)."""
        return {
            str(track_id): {
                "team_id": player.team_id,
                "total_distance_m": player.total_distance_m,
                "top_speed_mps": player.top_speed_mps,
                "avg_speed_mps": player.avg_speed_mps,
            }
            for track_id, player in self.players.items()
        }

    def to_rating_inputs(self, defaults: Optional[Dict[str, float]] = None) -> Dict[str, Dict[str, float]]:
        """
        Map internal metrics to the features expected by the rating engine.
        Unknown event metrics fall back to configurable defaults.
        """
        base_defaults = {
            "pass_accuracy": 0.75,
            "shots_on_target": 0.0,
            "tackles_won": 0.0,
        }
        base_defaults.update(defaults or {})

        rating_ready: Dict[str, Dict[str, float]] = {}
        for track_id, summary in self.summarize().items():
            rating_ready[track_id] = {
                "top_speed_mps": summary["top_speed_mps"],
                "avg_speed_mps": summary["avg_speed_mps"],
                "distance_m": summary["total_distance_m"],
                "pass_accuracy": base_defaults["pass_accuracy"],
                "shots_on_target": base_defaults["shots_on_target"],
                "tackles_won": base_defaults["tackles_won"],
            }
        return rating_ready
