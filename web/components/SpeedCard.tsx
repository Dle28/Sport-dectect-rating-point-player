import React from "react";
import styles from "./SpeedCard.module.css";

type Props = {
  speed: number;
  avgSpeed: number;
};

export function SpeedCard({ speed, avgSpeed }: Props) {
  const pct = Math.min(100, (speed / 10) * 100);
  return (
    <div className={styles.card}>
      <div className="pill">
        <span role="img" aria-label="speed">
          ⚡
        </span>
        Speed pulse
      </div>
      <div className={styles.value}>{speed.toFixed(1)} m/s</div>
      <div className={styles.sub}>Avg {avgSpeed.toFixed(1)} m/s</div>
      <div className={styles.barOuter}>
        <div className={styles.barInner} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
