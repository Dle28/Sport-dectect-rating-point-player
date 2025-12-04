import React from "react";
import styles from "./PlayerCard.module.css";

type Player = {
  id: string;
  name: string;
  position: string;
  rating: number;
  avatar?: string;
  team?: string;
  topSpeed: number;
  avgSpeed: number;
  distance?: number;
  subratings?: Record<string, number>;
};

type Props = {
  player: Player;
  compact?: boolean;
};

export function PlayerCard({ player, compact = false }: Props) {
  const initials = player.name
    .split(" ")
    .map((p) => p[0])
    .join("");
  return (
    <div className={styles.card} data-compact={compact}>
      <div className={styles.header}>
        <div className={styles.avatar}>{initials}</div>
        <div>
          <div className={styles.name}>{player.name}</div>
          <div className={styles.meta}>
            {player.position} - {player.team ?? "Team"}
          </div>
        </div>
        <div className={styles.badge}>
          <span className={styles.score}>{player.rating}</span>
          <span className={styles.label}>OVR</span>
        </div>
      </div>
      {!compact && (
        <div className={styles.body}>
          <div className={styles.stat}>
            <span>Top speed</span>
            <strong>{player.topSpeed.toFixed(1)} m/s</strong>
          </div>
          <div className={styles.stat}>
            <span>Avg speed</span>
            <strong>{player.avgSpeed.toFixed(1)} m/s</strong>
          </div>
          {typeof player.distance === "number" && (
            <div className={styles.stat}>
              <span>Distance</span>
              <strong>{(player.distance / 1000).toFixed(2)} km</strong>
            </div>
          )}
          {player.subratings && (
            <div className={styles.subratings}>
              {Object.entries(player.subratings).map(([k, v]) => (
                <span key={k} className={styles.sub}>
                  {k}: {Math.round(v)}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
