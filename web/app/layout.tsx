import "./globals.css";
import { Space_Grotesk } from "next/font/google";
import React from "react";

const font = Space_Grotesk({ subsets: ["latin"], weight: ["400", "500", "600", "700"] });

export const metadata = {
  title: "Soccer Analytics Dashboard",
  description: "Player avatars, heatmaps, speeds, and events in one view.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={font.className}>{children}</body>
    </html>
  );
}
