"use client";

import React, { useRef, useState } from "react";
import styles from "./UploadPanel.module.css";

type Props = {
  onAnalyze: (file: File, opts: { saveAnnotated: boolean }) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
  artifacts?: {
    ratingsPath?: string;
    metricsPath?: string;
    annotatedVideoPath?: string | null;
  } | null;
};

export function UploadPanel({ onAnalyze, isLoading, error, artifacts }: Props) {
  const fileRef = useRef<HTMLInputElement | null>(null);
  const [saveAnnotated, setSaveAnnotated] = useState(true);
  const [fileName, setFileName] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFileName(file.name);
    } else {
      setFileName(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const file = fileRef.current?.files?.[0];
    if (!file) return;
    await onAnalyze(file, { saveAnnotated });
  };

  return (
    <form className="panel" onSubmit={handleSubmit}>
      <div className={styles.header}>
        <div>
          <p className={styles.kicker}>Bring your own match</p>
          <h3>Upload a video, get player ratings.</h3>
        </div>
        <label className={styles.checkbox}>
          <input
            type="checkbox"
            checked={saveAnnotated}
            onChange={(e) => setSaveAnnotated(e.target.checked)}
          />
          Save annotated video
        </label>
      </div>
      <div className={styles.body}>
        <div 
          className={styles.dropzone} 
          onClick={() => fileRef.current?.click()}
          style={{ cursor: 'pointer' }}
        >
          <input 
            ref={fileRef} 
            type="file" 
            accept="video/*" 
            required 
            onChange={handleFileChange}
            style={{ display: 'none' }} 
          />
          <p>
            {fileName ? (
              <span style={{ color: 'var(--accent)', fontWeight: 'bold' }}>{fileName}</span>
            ) : (
              "Drop a full-match clip or tactical cam video. Supported: mp4, mov, mkv."
            )}
          </p>
        </div>
        <button className={styles.button} type="submit" disabled={isLoading || !fileName}>
          {isLoading ? "Processing…" : "Analyze video"}
        </button>
      </div>
      {error && <p className={styles.error}>{error}</p>}
      {artifacts && (artifacts.ratingsPath || artifacts.annotatedVideoPath) && (
        <div className={styles.footer}>
          {artifacts.ratingsPath && (
            <span className="pill">Ratings: {artifacts.ratingsPath}</span>
          )}
          {artifacts.metricsPath && (
            <span className="pill">Metrics: {artifacts.metricsPath}</span>
          )}
          {artifacts.annotatedVideoPath && (
            <span className="pill">Annotated: {artifacts.annotatedVideoPath}</span>
          )}
        </div>
      )}
      <p className={styles.note}>
        Runs the YOLO + ByteTrack + homography pipeline server-side, then maps metrics
        to FIFA-style 0–99 ratings.
      </p>
    </form>
  );
}
