import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useWorkspace } from '../context/WorkspaceContext';
import { canAccessControlCenter } from '../utils/permissions';

const primaryLinks = [
  { to: '/app/dashboard',     label: 'Dashboard' },
  { to: '/app',               label: 'SQL Assistant' },
  { to: '/app/policies',      label: 'Policies' },
  { to: '/app/query-logs',    label: 'Query Logs' },
  { to: '/app/sandbox',       label: 'Sandbox' },
  { to: '/app/architecture',  label: 'Architecture' },
  { to: '/app/agents',        label: 'AI Agents' },
  { to: '/app/settings',      label: 'Settings' },
];

const dataLinks = [
  { to: '/app/datasources', label: 'Data Sources' },
  { to: '/app/semantic-models', label: 'Semantic Models' },
  { to: '/app/schema', label: 'Schema Explorer' },
];

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const { org, role, isSuperAdmin, workspaces, currentWorkspace, setCurrentWorkspaceId } = useWorkspace();
  const showControlCenter = canAccessControlCenter(role, isSuperAdmin);
  const platformLinks = showControlCenter
    ? [...primaryLinks, { to: '/app/control-center', label: 'VoxCore Control Center' }]
    : primaryLinks;

  return (
    <aside
      style={{
        width: 264,
        minHeight: 'calc(100vh - 72px)',
        background: 'var(--platform-sidebar-bg)',
        borderRight: '1px solid var(--platform-border)',
        padding: 24,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
        <img src="/assets/vc_logo.png" alt="VoxCloud" style={{ width: 30, height: 30, objectFit: 'contain' }} />
        <div style={{ fontSize: 24, fontWeight: 700, color: '#ffffff' }}>VoxCloud</div>
      </div>
      <div style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.12em', color: 'var(--platform-muted)', marginBottom: 8 }}>
        Platform
      </div>
      <div style={{ fontSize: 12, color: 'var(--platform-muted)', marginBottom: 16 }}>
        Org: {org?.name || 'Organization'}
      </div>
      <label style={{ fontSize: 11, color: 'var(--platform-muted)', display: 'block', marginBottom: 6 }}>
        Workspace
      </label>
      <select
        value={currentWorkspace?.id ?? ''}
        onChange={(e) => setCurrentWorkspaceId(Number(e.target.value))}
        style={{
          width: '100%',
          marginBottom: 24,
          borderRadius: 8,
          border: '1px solid var(--platform-border)',
          background: 'var(--platform-card-bg)',
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
      <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--platform-muted)', marginBottom: 8 }}>
        Data
      </div>
      <nav style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 16 }}>
        {dataLinks.map((item) => {
          const active = location.pathname === item.to || location.pathname.startsWith(`${item.to}/`);
          return (
            <Link
              key={item.to}
              to={item.to}
              className={`sidebar-item${active ? ' active' : ''}`}
              style={{
                textDecoration: 'none',
                borderRadius: 10,
                padding: '10px 12px',
                fontSize: 14,
                fontWeight: 600,
                display: 'block',
              }}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--platform-muted)', marginBottom: 8 }}>
        Platform
      </div>
      <nav style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {platformLinks.map((item) => {
          const active = location.pathname === item.to || location.pathname.startsWith(`${item.to}/`);
          return (
            <Link
              key={item.to}
              to={item.to}
              className={`sidebar-item${active ? ' active' : ''}`}
              style={{
                textDecoration: 'none',
                borderRadius: 10,
                padding: '10px 12px',
                fontSize: 14,
                fontWeight: 600,
                display: 'block',
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
