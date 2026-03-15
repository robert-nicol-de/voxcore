import React from 'react';
import '../styles/theme.css';
import '../styles/design-system.css';
import Sidebar from './Sidebar';

export default function AppLayout({ children }) {
  return (
    <div className="app-layout flex">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="main-container flex flex-col bg-primary">
        {/* Top Bar */}
        <header className="top-bar flex items-center justify-between px-8 bg-surface-elevated border-default" style={{ height: 'var(--header-height-desktop)' }}>
          <div className="status-info flex items-center gap-2 text-secondary text-sm">
            <span className="status-badge bg-accent-primary text-white rounded px-3 py-1 text-xs font-medium">Production</span>
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
}
