import { v4 as uuid } from "uuid";

export const mockPlayers = [
  {
    id: "p1",
    name: "Amina Duarte",
    position: "CM",
    rating: 86,
    team: "Home",
    topSpeed: 8.2,
    avgSpeed: 6.1,
    heatmap: [
      { x: 120, y: 80 },
      { x: 200, y: 120 },
      { x: 260, y: 200 },
      { x: 320, y: 140 },
      { x: 420, y: 190 },
      { x: 520, y: 120 },
    ],
  },
  {
    id: "p2",
    name: "Leo Kruger",
    position: "ST",
    rating: 90,
    team: "Home",
    topSpeed: 9.4,
    avgSpeed: 7.2,
    heatmap: [
      { x: 320, y: 90 },
      { x: 360, y: 120 },
      { x: 400, y: 160 },
      { x: 460, y: 190 },
      { x: 520, y: 210 },
    ],
  },
  {
    id: "p3",
    name: "Riku Tan",
    position: "CB",
    rating: 82,
    team: "Away",
    topSpeed: 7.2,
    avgSpeed: 5.9,
    heatmap: [
      { x: 140, y: 240 },
      { x: 180, y: 260 },
      { x: 220, y: 240 },
      { x: 260, y: 220 },
    ],
  },
];

export const mockEvents = [
  { id: uuid(), time: "12:04", type: "Pass", player: "Amina Duarte", speed: 6.2 },
  { id: uuid(), time: "23:18", type: "Shot", player: "Leo Kruger", speed: 7.8 },
  { id: uuid(), time: "30:45", type: "Tackle", player: "Riku Tan" },
  { id: uuid(), time: "55:10", type: "Pass", player: "Amina Duarte", speed: 6.5 },
  { id: uuid(), time: "71:33", type: "Shot", player: "Leo Kruger", speed: 8.1 },
];
