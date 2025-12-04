import React, { useEffect, useRef } from "react";

type Point = { x: number; y: number };

type Props = {
  positions: Point[];
};

export function Heatmap({ positions }: Props) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const { width, height } = canvas;
    ctx.clearRect(0, 0, width, height);

    // background pitch
    const grad = ctx.createLinearGradient(0, 0, width, height);
    grad.addColorStop(0, "#0f2a44");
    grad.addColorStop(1, "#0a1c30");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, width, height);

    // draw heat spots
    positions.forEach((p) => {
      const radius = 28;
      const g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, radius);
      g.addColorStop(0, "rgba(49, 232, 174, 0.45)");
      g.addColorStop(1, "rgba(49, 232, 174, 0)");
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(p.x, p.y, radius, 0, Math.PI * 2);
      ctx.fill();
    });

    // simple pitch lines
    ctx.strokeStyle = "rgba(255,255,255,0.12)";
    ctx.lineWidth = 1;
    ctx.strokeRect(10, 10, width - 20, height - 20);
    ctx.beginPath();
    ctx.moveTo(width / 2, 10);
    ctx.lineTo(width / 2, height - 10);
    ctx.stroke();
  }, [positions]);

  return <canvas ref={canvasRef} width={640} height={360} style={{ width: "100%", borderRadius: 12 }} />;
}
