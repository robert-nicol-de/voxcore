import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useWorkspace } from '../context/WorkspaceContext';

const links = [
  { to: '/app/dashboard', label: 'Dashboard' },
  { to: '/app/databases', label: 'Databases' },
  { to: '/app', label: 'SQL Assistant' },
  { to: '/app/policies', label: 'Policies' },
  { to: '/app/query-logs', label: 'Query Logs' },
  { to: '/app/sandbox', label: 'Sandbox' },
  { to: '/app/settings', label: 'Settings' },
];

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const { org, workspaces, currentWorkspace, setCurrentWorkspaceId } = useWorkspace();

  return (
    <aside
      style={{
        width: 240,
        minHeight: '100vh',
        background: '#0b1220',
        borderRight: '1px solid rgba(255,255,255,0.08)',
        padding: '22px 18px',
      }}
    >
      <div style={{ fontSize: 24, fontWeight: 700, color: '#93c5fd', marginBottom: 8 }}>VoxCloud</div>
      <div style={{ fontSize: 12, color: '#94a3b8', marginBottom: 12 }}>
        Org: {org?.name || 'Organization'}
      </div>
      <label style={{ fontSize: 11, color: '#cbd5e1', display: 'block', marginBottom: 6 }}>
        Workspace
      </label>
      <select
        value={currentWorkspace?.id ?? ''}
        onChange={(e) => setCurrentWorkspaceId(Number(e.target.value))}
        style={{
          width: '100%',
          marginBottom: 16,
          borderRadius: 8,
          border: '1px solid rgba(255,255,255,0.16)',
          background: 'rgba(15,23,42,0.85)',
          color: '#e2e8f0',
          padding: '8px 10px',
          fontSize: 13,
        }}
      >
        {workspaces.map((ws) => (
          <option key={ws.id} value={ws.id}>
            {ws.name}
          </option>
        ))}
      </select>
      <nav style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {links.map((item) => {
          const active = location.pathname === item.to;
          return (
            <Link
              key={item.to}
              to={item.to}
              style={{
                color: active ? '#0f172a' : '#cbd5e1',
                textDecoration: 'none',
                background: active ? '#93c5fd' : 'transparent',
                border: active ? '1px solid #93c5fd' : '1px solid rgba(255,255,255,0.08)',
                borderRadius: 10,
                padding: '10px 12px',
                fontSize: 14,
                fontWeight: 600,
              }}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
};
