import React from 'react';
import '../styles/theme.css';
import './AppLayout.css';

export default function AppLayout({ children }) {
  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo">VoxQuery</div>
          <div className="logo-subtitle">Powered by VoxCore</div>
        </div>
        
        <nav className="sidebar-nav">
          <SidebarItem 
            label="Ask Query" 
            icon="💬"
            active={true}
          />
          <SidebarItem 
            label="Query History" 
            icon="📋"
          />
          <SidebarItem 
            label="Governance Logs" 
            icon="🛡️"
          />
          <SidebarItem 
            label="Policies" 
            icon="⚙️"
          />
        </nav>

        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">R</div>
            <div className="user-details">
              <div className="user-name">Robert</div>
              <div className="user-status">Online</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="main-container">
        {/* Top Bar */}
        <header className="top-bar">
          <div className="status-info">
            <span className="status-badge">Production</span>
            <span className="status-separator">•</span>
            <span className="status-text">SQL Server</span>
          </div>
          <div className="header-actions">
            <button className="icon-button">🔔</button>
            <button className="icon-button">⚙️</button>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="main-content">
          {children}
        </main>
      </div>
    </div>
  );
}

function SidebarItem({ label, icon, active = false }) {
  return (
    <div className={`sidebar-item ${active ? 'active' : ''}`}>
      <span className="sidebar-icon">{icon}</span>
      <span className="sidebar-label">{label}</span>
    </div>
  );
}
