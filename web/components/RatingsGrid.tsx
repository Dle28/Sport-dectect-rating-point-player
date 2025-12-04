"use client";

import React from "react";
import styles from "./RatingsGrid.module.css";
import { formatMeters } from "../lib/api";
import { RatingPlayer } from "../lib/types";

const ORDERED_SUBS = ["PAC", "SHO", "PAS", "DEF", "PHY"];

export function RatingsGrid({ players }: { players: RatingPlayer[] }) {
  if (!players.length) return null;

  return (
    <div className="panel">
      <div className={styles.header}>
        <h3>Ratings from your upload</h3>
        <span className="pill">FIFA 0–99 scale</span>
      </div>
      <div className={styles.table}>
        <div className={styles.head}>
          <span>Player</span>
          <span>OVR</span>
          <span>Top</span>
          <span>Avg</span>
          <span>Distance</span>
          <span>Attributes</span>
        </div>
        {players.map((p) => (
          <div key={p.id} className={styles.row}>
            <div>
              <div className={styles.name}>{p.name}</div>
              <div className={styles.meta}>{p.position} - {p.team ?? "Team"}</div>
            </div>
            <div className={styles.overall}>{p.rating}</div>
            <div>{p.topSpeed.toFixed(1)} m/s</div>
            <div>{p.avgSpeed.toFixed(1)} m/s</div>
            <div>{formatMeters(p.distance)}</div>
            <div className={styles.subratings}>
              {ORDERED_SUBS.map((k) => (
                <span key={k} className={styles.sub}>
                  <span className={styles.subLabel}>{k}</span>
                  <span className={styles.bar}>
                    <span
                      className={styles.fill}
                      style={{ width: `${Math.min(100, p.subratings?.[k] ?? 0)}%` }}
                    />
                  </span>
                  <span className={styles.subValue}>{Math.round(p.subratings?.[k] ?? 0)}</span>
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
