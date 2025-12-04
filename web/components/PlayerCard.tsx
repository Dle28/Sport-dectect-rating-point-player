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
            {player.position} · {player.team ?? "Team A"}
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
        </div>
      )}
    </div>
  );
}
