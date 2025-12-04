"use client";

import styles from "./page.module.css";
import { PlayerCard } from "../components/PlayerCard";
import { Heatmap } from "../components/Heatmap";
import { EventsList } from "../components/EventsList";
import { SpeedCard } from "../components/SpeedCard";
import { SceneBackground } from "../components/SceneBackground";
import { mockEvents, mockPlayers } from "../lib/mockData";

export default function Home() {
  const primaryPlayer = mockPlayers[0];
  return (
    <main className={styles.main}>
      <SceneBackground />
      <section className={styles.hero}>
        <div>
          <p className={styles.kicker}>Live Match Insight</p>
          <h1>Player pulse, plays, and pitch control.</h1>
          <p className={styles.subtitle}>
            Watch avatars, heatmaps, speed bursts, and events co-exist in a single responsive surface.
          </p>
        </div>
        <div className={styles.cards}>
          <PlayerCard player={primaryPlayer} />
          <SpeedCard speed={primaryPlayer.topSpeed} avgSpeed={primaryPlayer.avgSpeed} />
        </div>
      </section>

      <section className="grid" style={{ gridTemplateColumns: "1.2fr 1fr", width: "100%" }}>
        <div className="panel">
          <h3>Heatmap</h3>
          <Heatmap positions={primaryPlayer.heatmap} />
        </div>
        <div className="panel">
          <h3>Events</h3>
          <EventsList events={mockEvents} />
        </div>
      </section>

      <section className="panel" style={{ width: "100%" }}>
        <h3>Squad Snapshot</h3>
        <div className="subgrid">
          {mockPlayers.map((p) => (
            <PlayerCard key={p.id} player={p} compact />
          ))}
        </div>
      </section>
    </main>
  );
}
