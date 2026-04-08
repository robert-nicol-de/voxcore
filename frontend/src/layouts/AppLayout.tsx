import React, { useState } from "react";
import RightPanel from "../components/RightPanel";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const [rightPanelOpen, setRightPanelOpen] = useState(false);
  return (
    <div
      className="flex min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)]"
      style={{ minHeight: "100vh" }}
    >
      {/* Sidebar */}
      <aside
        className="sidebar fixed left-0 top-0 h-screen w-64 border-r border-[var(--border-default)] p-8 flex flex-col"
        style={{ background: "var(--bg-surface)", zIndex: 30 }}
      >
        <div className="flex items-center gap-3 mb-8">
          <img
            src="/assets/logo-icon.png"
            alt="VoxCore"
            className="h-8 w-8"
          />
          <h2 className="text-[var(--accent-primary)] font-bold text-lg tracking-wide">VoxCore</h2>
        </div>
        <nav className="flex flex-col gap-4 text-base">
          <button className="text-left hover:text-[var(--text-primary)] transition-colors">Dashboard</button>
          <button className="text-left hover:text-[var(--text-primary)] transition-colors">Playground</button>
          <button className="text-left hover:text-[var(--text-primary)] transition-colors">Query Logs</button>
          <button className="text-left hover:text-[var(--text-primary)] transition-colors">Policies</button>
          <button className="text-left hover:text-[var(--text-primary)] transition-colors">Settings</button>
        </nav>
        <button
          className="mt-8 px-4 py-2 rounded-lg bg-[var(--accent-primary)] text-white hover:bg-blue-500 transition"
          onClick={() => setRightPanelOpen((v) => !v)}
        >
          {rightPanelOpen ? "Hide Insights" : "Show Insights"}
        </button>
      </aside>
      {/* Main Content */}
      <div className="flex-1 flex flex-col ml-64 min-h-screen">
        {/* Top Bar */}
        <header
          className="sticky top-0 z-20 border-b border-[var(--border-default)] px-8 py-4 flex justify-between items-center bg-[var(--bg-surface)] backdrop-blur"
        >
          <span className="text-base text-[var(--text-secondary)] font-medium">Dashboard</span>
          <span className="text-base">👤 User</span>
        </header>
        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-8 bg-[var(--bg-primary)] page-fadein">
          {children}
        </main>
      </div>
      {/* RightPanel (slide-in) */}
      <RightPanel open={rightPanelOpen} onClose={() => setRightPanelOpen(false)} />
    </div>
  );
}
