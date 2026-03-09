import React from 'react'

interface DevSidebarProps {
  currentView: string
  setView: (view: string) => void
}

export default function DevSidebar({ currentView, setView }: DevSidebarProps) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'tenants', label: 'Tenants', icon: '👥' },
    { id: 'zerotrust', label: 'Zero Trust', icon: '🔐' },
    { id: 'sandbox', label: 'AI Sandbox', icon: '🧪' },
    { id: 'inspector', label: 'Query Inspector', icon: '🔍' },
    { id: 'schema', label: 'Schema Map', icon: '🗺️' },
    { id: 'connectors', label: 'Database Connectors', icon: '🗄️' },
    { id: 'connectorsecurity', label: 'Connector Security', icon: '🛡️' },
    { id: 'threatmonitor', label: 'Threat Monitor', icon: '📊' },
    { id: 'security', label: 'Security Shield', icon: '🔐' },
    { id: 'rules', label: 'Protection Rules', icon: '📋' },
    { id: 'attacks', label: 'Attack Simulator', icon: '⚔️' },
    { id: 'history', label: 'Query History', icon: '📜' },
    { id: 'metrics', label: 'Execution Metrics', icon: '⏱️' }
  ]

  return (
    <div className="dev-sidebar">
      <div className="sidebar-header">
        <h2 className="logo">VoxCore</h2>
        <span className="logo-subtitle">Dev Console</span>
      </div>

      <nav className="sidebar-nav">
        {navItems.map(item => (
          <button
            key={item.id}
            className={`nav-button ${currentView === item.id ? 'active' : ''}`}
            onClick={() => setView(item.id)}
            title={item.label}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <p>v1.0.0</p>
      </div>
    </div>
  )
}
