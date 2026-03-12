import React, { useEffect, useMemo, useRef, useState } from 'react';
import { apiUrl } from '../lib/api';
import { useWorkspace } from '../context/WorkspaceContext';

type WorkspaceItem = {
  id: number;
  name: string;
};

type DatasourceItem = {
  id: number;
  name: string;
  platform?: string;
  config?: Record<string, unknown>;
};

function badgeFromWorkspace(name: string) {
  const normalized = (name || '').toLowerCase();
  if (normalized.includes('prod') || normalized.includes('production')) {
    return { label: 'PROD', color: '#ff6b6b', bg: 'rgba(255,107,107,0.18)' };
  }
  if (normalized.includes('test') || normalized.includes('qa') || normalized.includes('uat')) {
    return { label: 'TEST', color: '#ffd166', bg: 'rgba(255,209,102,0.18)' };
  }
  return { label: 'DEV', color: '#35d07f', bg: 'rgba(53,208,127,0.18)' };
}

export default function WorkspaceSwitcher() {
  const { org, currentWorkspace, setCurrentWorkspaceId } = useWorkspace();

  const [open, setOpen] = useState(false);
  const [workspaces, setWorkspaces] = useState<WorkspaceItem[]>([]);
  const [datasources, setDatasources] = useState<DatasourceItem[]>([]);
  const [selectedDatasourceId, setSelectedDatasourceId] = useState(() => Number(localStorage.getItem('voxcore_datasource_id') || '0'));
  const [selectedSchema, setSelectedSchema] = useState(() => localStorage.getItem('voxcore_schema') || 'public');

  const [creating, setCreating] = useState(false);
  const [newWorkspaceName, setNewWorkspaceName] = useState('');
  const [createError, setCreateError] = useState<string | null>(null);

  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  useEffect(() => {
    const loadWorkspaces = async () => {
      const res = await fetch(apiUrl('/api/v1/workspaces'));
      if (!res.ok) return;
      const data = (await res.json().catch(() => [])) as WorkspaceItem[];
      setWorkspaces(Array.isArray(data) ? data : []);
    };

    const loadDatasources = async () => {
      const workspaceId = Number(localStorage.getItem('voxcore_workspace_id') || '1');
      const res = await fetch(apiUrl(`/api/v1/datasources?workspace_id=${workspaceId}`));
      if (!res.ok) return;
      const data = (await res.json().catch(() => [])) as DatasourceItem[];
      const list = Array.isArray(data) ? data : [];
      setDatasources(list);

      if (!selectedDatasourceId && list.length > 0) {
        setSelectedDatasourceId(list[0].id);
        localStorage.setItem('voxcore_datasource_id', String(list[0].id));
      }
    };

    void loadWorkspaces();
    void loadDatasources();
  }, [currentWorkspace?.id, selectedDatasourceId]);

  const currentWorkspaceName = currentWorkspace?.name || localStorage.getItem('voxcore_workspace_name') || 'Default';
  const badge = badgeFromWorkspace(currentWorkspaceName);

  const selectedDatasource = useMemo(
    () => datasources.find((d) => d.id === selectedDatasourceId) || datasources[0],
    [datasources, selectedDatasourceId],
  );

  useEffect(() => {
    if (selectedDatasource?.id) {
      localStorage.setItem('voxcore_datasource_id', String(selectedDatasource.id));
    }
  }, [selectedDatasource?.id]);

  useEffect(() => {
    localStorage.setItem('voxcore_schema', selectedSchema);
  }, [selectedSchema]);

  const handleSwitchWorkspace = async (workspaceId: number) => {
    await setCurrentWorkspaceId(workspaceId);
    localStorage.setItem('vox_workspace', String(workspaceId));
    setOpen(false);
    window.location.reload();
  };

  const handleCreateWorkspace = async () => {
    const trimmed = newWorkspaceName.trim();
    if (!trimmed) {
      setCreateError('Workspace name is required');
      return;
    }

    const orgId = org?.id || Number(localStorage.getItem('voxcore_org_id') || '1');
    const res = await fetch(apiUrl(`/api/v1/orgs/${orgId}/workspaces`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: trimmed }),
    });

    if (!res.ok) {
      const body = (await res.json().catch(() => ({}))) as { detail?: string };
      setCreateError(body.detail || 'Failed to create workspace');
      return;
    }

    const created = (await res.json()) as { workspace?: WorkspaceItem };
    if (created.workspace?.id) {
      await handleSwitchWorkspace(created.workspace.id);
    }
  };

  return (
    <div ref={rootRef} className="workspace-switcher">
      <div className="workspace-row">
        <button className="workspace-pill" onClick={() => setOpen((v) => !v)}>
          <span className="workspace-pill-label">Workspace:</span>
          <span className="workspace-pill-value">{currentWorkspaceName}</span>
          <span className="workspace-pill-arrow">{open ? '▲' : '▼'}</span>
        </button>

        <span className="workspace-badge" style={{ color: badge.color, background: badge.bg, borderColor: badge.color }}>
          {badge.label}
        </span>
      </div>

      {open && (
        <div className="workspace-menu">
          <div className="workspace-menu-title">Select Workspace</div>
          <div className="workspace-menu-list">
            {workspaces.map((ws) => (
              <button key={ws.id} className="workspace-menu-item" onClick={() => void handleSwitchWorkspace(ws.id)}>
                {ws.name}
              </button>
            ))}
          </div>
          <div className="workspace-menu-sep" />

          {!creating ? (
            <button className="workspace-menu-create" onClick={() => { setCreating(true); setCreateError(null); }}>
              + Create Workspace
            </button>
          ) : (
            <div className="workspace-menu-form">
              <input
                value={newWorkspaceName}
                onChange={(e) => setNewWorkspaceName(e.target.value)}
                placeholder="Workspace name"
              />
              {createError && <div className="workspace-menu-error">{createError}</div>}
              <div className="workspace-menu-actions">
                <button onClick={() => void handleCreateWorkspace()}>Create</button>
                <button
                  onClick={() => {
                    setCreating(false);
                    setNewWorkspaceName('');
                    setCreateError(null);
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="workspace-context-row">
        <label>
          Organization
          <select value={org?.name || 'Organization'} disabled>
            <option value={org?.name || 'Organization'}>{org?.name || 'Organization'}</option>
          </select>
        </label>

        <label>
          Database
          <select
            value={selectedDatasource?.id || ''}
            onChange={(e) => setSelectedDatasourceId(Number(e.target.value || '0'))}
          >
            {datasources.length === 0 && <option value="">No datasource</option>}
            {datasources.map((d) => (
              <option key={d.id} value={d.id}>{d.name} ({(d.platform || 'unknown').toUpperCase()})</option>
            ))}
          </select>
        </label>

        <label>
          Schema
          <select value={selectedSchema} onChange={(e) => setSelectedSchema(e.target.value)}>
            <option value="public">public</option>
            <option value="analytics">analytics</option>
            <option value="dbo">dbo</option>
          </select>
        </label>
      </div>
    </div>
  );
}
