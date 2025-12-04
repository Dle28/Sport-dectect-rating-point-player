"use client";

import { useMemo, useState } from "react";
import styles from "./page.module.css";
import { PlayerCard } from "../components/PlayerCard";
import { Heatmap } from "../components/Heatmap";
import { EventsList } from "../components/EventsList";
import { SpeedCard } from "../components/SpeedCard";
import { SceneBackground } from "../components/SceneBackground";
import { UploadPanel } from "../components/UploadPanel";
import { RatingsGrid } from "../components/RatingsGrid";
import { analyzeVideo } from "../lib/api";
import { mockEvents, mockPlayers } from "../lib/mockData";
import { AnalyzeResponse, RatingPlayer } from "../lib/types";

function buildPlayersFromResponse(res: AnalyzeResponse): RatingPlayer[] {
  const ratings = res.ratings || {};
  const metrics = res.metrics_summary || {};
  const ratingInputs = res.rating_inputs || {};
  const positionCycle = ["GK", "DF", "MF", "FW"];

  return Object.entries(ratings).map(([id, rating], idx) => {
    const m = metrics[id] || {};
    const fallback = ratingInputs[id] || {};
    const name = `Player ${idx + 1}`;
    const team = m.team_id === undefined || m.team_id === null ? "Team" : `Team ${m.team_id + 1}`;
    const position = positionCycle[idx % positionCycle.length];

    const topSpeed = m.top_speed_mps ?? fallback.top_speed_mps ?? 0;
    const avgSpeed = m.avg_speed_mps ?? fallback.avg_speed_mps ?? 0;
    const distance = m.total_distance_m ?? fallback.distance_m ?? 0;

    return {
      id,
      name,
      position,
      team,
      rating: Math.round(rating.overall),
      topSpeed,
      avgSpeed,
      distance,
      subratings: rating.subratings,
    };
  });
}

export default function Home() {
  const [players, setPlayers] = useState<RatingPlayer[]>(mockPlayers);
  const [events] = useState(mockEvents);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [artifacts, setArtifacts] = useState<{
    ratingsPath?: string;
    metricsPath?: string;
    annotatedVideoPath?: string | null;
  } | null>(null);

  const primaryPlayer = useMemo(() => players[0] ?? mockPlayers[0], [players]);

  const handleAnalyze = async (file: File, opts: { saveAnnotated: boolean }) => {
    setLoading(true);
    setError(null);
    try {
      const res = await analyzeVideo(file, { saveAnnotated: opts.saveAnnotated });
      const nextPlayers = buildPlayersFromResponse(res);
      if (nextPlayers.length) {
        setPlayers(nextPlayers);
      }
      setArtifacts({
        ratingsPath: res.ratings_path,
        metricsPath: res.metrics_path,
        annotatedVideoPath: res.annotated_video_path ?? undefined,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to analyze video";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className={styles.main}>
      <SceneBackground />
      <section className={styles.hero}>
        <div>
          <p className={styles.kicker}>Live Match Insight</p>
          <h1 className={styles.title}>Player pulse, plays, and pitch control.</h1>
          <p className={styles.subtitle}>
            Watch avatars, heatmaps, speed bursts, and events co-exist in a single responsive surface.
          </p>
          <div className={styles.actions}>
            <span className="pill">YOLO + ByteTrack + Homography</span>
            <span className="pill">Ratings 0–99</span>
          </div>
        </div>
        <div className={styles.cards}>
          {primaryPlayer && (
            <>
              <PlayerCard player={primaryPlayer} />
              <SpeedCard speed={primaryPlayer.topSpeed} avgSpeed={primaryPlayer.avgSpeed} />
            </>
          )}
        </div>
      </section>

      <section className={styles.uploadRow}>
        <UploadPanel onAnalyze={handleAnalyze} isLoading={loading} error={error} artifacts={artifacts} />
      </section>

      <section className="grid" style={{ gridTemplateColumns: "1.2fr 1fr", width: "100%" }}>
        <div className="panel">
          <h3>Heatmap</h3>
          {primaryPlayer?.heatmap ? (
            <Heatmap positions={primaryPlayer.heatmap} />
          ) : (
            <p style={{ color: "var(--muted)" }}>Heatmap will appear after analysis.</p>
          )}
        </div>
        <div className="panel">
          <h3>Events</h3>
          <EventsList events={events} />
        </div>
      </section>

      <RatingsGrid players={players} />

      <section className="panel" style={{ width: "100%" }}>
        <h3>Squad Snapshot</h3>
        <div className="subgrid">
          {players.map((p) => (
            <PlayerCard key={p.id} player={p} compact />
          ))}
        </div>
      </section>
    </main>
  );
}
