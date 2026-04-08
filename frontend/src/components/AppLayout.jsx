import React from 'react';
import '../styles/theme.css';
import '../styles/design-system.css';
import Sidebar from './layout/Sidebar';

export default function AppLayout({ children, demoMode = false }) {
  return (
    <div className="app-layout flex">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="main-container flex flex-col bg-primary">
        {demoMode && (
          <div style={{ background: '#081b2f', color: '#68f0e2', padding: '10px 16px', textAlign: 'center', borderBottom: '1px solid rgba(104, 240, 226, 0.25)' }}>
            🧪 Demo Mode — Your real databases are protected by VoxCore Guardian
          </div>
        )}

        {/* Top Bar */}
        <header className="top-bar flex items-center justify-between px-8 bg-surface-elevated border-default" style={{ height: 'var(--header-height-desktop)' }}>
          <div className="status-info flex items-center gap-2 text-secondary text-sm">
            <span className="status-badge bg-accent-primary text-white rounded px-3 py-1 text-xs font-medium">{demoMode ? 'Demo' : 'Production'}</span>
            <span className="status-separator text-muted">•</span>
            <span className="status-text text-secondary">SQL Server</span>
          </div>
          <div className="header-actions flex items-center gap-3">
            <button className="icon-button rounded-sm text-secondary hover:bg-surface-elevated hover:text-primary transition-fast">🔔</button>
            <button className="icon-button rounded-sm text-secondary hover:bg-surface-elevated hover:text-primary transition-fast">⚙️</button>
          </div>
        </header>
        {/* Main Content Area */}
        <main className="main-content flex-1 p-8 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
