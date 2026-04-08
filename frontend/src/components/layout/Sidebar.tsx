// Moved from src/components/Sidebar.tsx as part of enterprise SaaS architecture refactor
import React from "react";
import { Link, useLocation } from "react-router-dom";
import { useWorkspace } from "../../context/WorkspaceContext";
import { canAccessControlCenter } from "../../utils/permissions";

const primaryLinks = [
  { to: "/app/dashboard",     label: "Dashboard" },
  { to: "/app",               label: "SQL Assistant" },
  { to: "/app/policies",      label: "Policies" },
  { to: "/app/query-logs",    label: "Query Logs" },
  { to: "/app/sandbox",       label: "Sandbox" },
  { to: "/app/architecture",  label: "Architecture" },
  { to: "/app/agents",        label: "AI Agents" },
  { to: "/app/settings",      label: "Settings" },
];

const dataLinks = [
  { to: "/app/datasources", label: "Data Sources" },
  { to: "/app/semantic-models", label: "Semantic Models" },
  { to: "/app/schema", label: "Schema Explorer" },
];

export default function Sidebar() {
  const location = useLocation();
  const { org, role, isSuperAdmin, workspaces, currentWorkspace, setCurrentWorkspaceId } = useWorkspace();
  const showControlCenter = canAccessControlCenter(role, isSuperAdmin);
  const platformLinks = showControlCenter
    ? [...primaryLinks, { to: "/app/control-center", label: "VoxCore Control Center" }]
    : primaryLinks;

  return (
    <aside className="sidebar bg-[var(--bg-card)] border-r border-[rgba(255,255,255,0.05)] shadow-lg shadow-[inset_-1px_0_0_rgba(255,255,255,0.05)]" style={{ width: "var(--sidebar-desktop)", minHeight: "100vh", padding: "var(--spacing-3)" }}>
      <div className="flex items-center gap-2 mb-2">
        <img src="/assets/voxcore-logo-symbol.svg" alt="VoxQuery" style={{ width: 32, height: 32, objectFit: "contain" }} />
        <div className="text-xl font-semibold text-primary">VoxQuery</div>
      </div>
      <div className="text-xs uppercase tracking-wide text-muted mb-2">Platform</div>
      <div className="text-xs text-muted mb-4">Org: {org?.name || "Organization"}</div>
      <label className="text-xs text-muted block mb-1">Workspace</label>
      <select
        className="mb-4"
        value={currentWorkspace?.id || ""}
        onChange={e => setCurrentWorkspaceId?.(Number(e.target.value))}
      >
        {workspaces?.map(ws => (
          <option key={ws.id} value={ws.id}>{ws.name}</option>
        ))}
      </select>
      <nav>
        <ul>
          {platformLinks.map(link => (
            <li key={link.to} className={location.pathname === link.to ? "bg-[rgba(59,130,246,0.1)] border-l-2 border-[var(--accent-blue)] transition-all duration-200" : "transition-all duration-200"}>
              <Link to={link.to}>{link.label}</Link>
            </li>
          ))}
        </ul>
        <div className="mt-4">
          <div className="text-xs uppercase tracking-wide text-muted mb-2">Data</div>
          <ul>
            {dataLinks.map(link => (
              <li key={link.to} className={location.pathname === link.to ? "active" : ""}>
                <Link to={link.to}>{link.label}</Link>
              </li>
            ))}
          </ul>
        </div>
      </nav>
    </aside>
  );
}
