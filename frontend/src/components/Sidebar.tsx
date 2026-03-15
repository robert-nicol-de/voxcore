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
    <aside className="sidebar bg-surface-elevated border-default shadow-md" style={{ width: 'var(--sidebar-desktop)', minHeight: '100vh', padding: 'var(--spacing-3)' }}>
      <div className="flex items-center gap-2 mb-2">
        <img src="/assets/vc_logo.png" alt="VoxCloud" style={{ width: 30, height: 30, objectFit: 'contain' }} />
        <div className="text-xl font-semibold text-primary">VoxCloud</div>
      </div>
      <div className="text-xs uppercase tracking-wide text-muted mb-2">Platform</div>
      <div className="text-xs text-muted mb-4">Org: {org?.name || 'Organization'}</div>
      <label className="text-xs text-muted block mb-1">Workspace</label>
      <select
        value={currentWorkspace?.id ?? ''}
        onChange={(e) => setCurrentWorkspaceId(Number(e.target.value))}
        className="w-full mb-6 rounded-sm border-default bg-surface text-secondary px-3 py-2 text-sm"
      >
        {workspaces.map((ws) => (
          <option key={ws.id} value={ws.id}>
            {ws.name}
          </option>
        ))}
      </select>
      <div className="text-xs uppercase tracking-wide text-muted mb-2">Data</div>
      <nav className="flex flex-col gap-2 mb-4">
        {dataLinks.map((item) => {
          const active = location.pathname === item.to || location.pathname.startsWith(`${item.to}/`);
          return (
            <Link
              key={item.to}
              to={item.to}
              className={`sidebar-item${active ? ' active' : ''}`}
              tabIndex={0}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="text-xs uppercase tracking-wide text-muted mb-2">Platform</div>
      <nav className="flex flex-col gap-2">
        {platformLinks.map((item) => {
          const active = location.pathname === item.to || location.pathname.startsWith(`${item.to}/`);
          return (
            <Link
              key={item.to}
              to={item.to}
              className={`sidebar-item${active ? ' active' : ''}`}
              tabIndex={0}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
};
