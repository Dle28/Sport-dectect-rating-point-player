import React from "react";
import styles from "./EventsList.module.css";

type EventItem = {
  id: string;
  time: string;
  type: "Pass" | "Shot" | "Tackle";
  player: string;
  speed?: number;
};

type Props = {
  events: EventItem[];
};

const colors: Record<EventItem["type"], string> = {
  Pass: "#31e8ae",
  Shot: "#ff7f50",
  Tackle: "#5f8bff",
};

export function EventsList({ events }: Props) {
  return (
    <div className={styles.list}>
      {events.map((e) => (
        <div className={styles.row} key={e.id}>
          <div className={styles.icon} style={{ background: colors[e.type] }}>
            {e.type[0]}
          </div>
          <div>
            <div className={styles.title}>{e.type}</div>
            <div className={styles.meta}>
              {e.player} · {e.time} {e.speed ? `· ${e.speed.toFixed(1)} m/s` : ""}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
