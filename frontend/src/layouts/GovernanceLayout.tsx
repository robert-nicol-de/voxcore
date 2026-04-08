// VoxCore Layout Shell — Step 2: Card + layout shell
import React from "react";
import "../styles/global.css";

export default function GovernanceLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-start gap-32 bg-[var(--bg-primary)]">
      {/* HEADER */}
      <header className="w-full flex flex-col items-center gap-8 mt-16">
        <img
          src="/assets/logo-icon.png"
          alt="VoxCore"
          className="h-12 w-12"
        />
        <h1 className="text-3xl font-bold tracking-tight" style={{ letterSpacing: 0.5 }}>We Govern Them.</h1>
        <h2 className="text-lg font-semibold text-[var(--accent-blue)]">VoxCore</h2>
      </header>
      {/* MAIN CARD */}
      <main className="card max-w-main w-full flex flex-col items-center gap-24">
        {children}
      </main>
    </div>
  );
}
