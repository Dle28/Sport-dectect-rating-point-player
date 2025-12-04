"use client";

import React, { Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";

function FloatingGrid() {
  return (
    <mesh rotation-x={-Math.PI / 2} position={[0, -1.5, 0]}>
      <planeGeometry args={[40, 40, 40, 40]} />
      <meshBasicMaterial wireframe color="#1f8fff" opacity={0.12} transparent />
    </mesh>
  );
}

function GlowSphere() {
  return (
    <mesh position={[0, 3, -6]}>
      <sphereGeometry args={[2.6, 32, 32]} />
      <meshBasicMaterial color="#31e8ae" opacity={0.08} transparent />
    </mesh>
  );
}

export function SceneBackground() {
  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 0, pointerEvents: "none", opacity: 0.85 }}>
      <Canvas camera={{ position: [6, 6, 6], fov: 55 }}>
        <ambientLight intensity={0.5} />
        <Suspense fallback={null}>
          <FloatingGrid />
          <GlowSphere />
        </Suspense>
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.6} />
      </Canvas>
    </div>
  );
}
