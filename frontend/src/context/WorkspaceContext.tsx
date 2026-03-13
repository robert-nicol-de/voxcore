import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { apiUrl } from '../lib/api';

type Workspace = {
  id: number;
  name: string;
  slug?: string;
  org_id?: number;
};

type Org = {
  id: number;
  name: string;
  slug?: string;
};

type WorkspaceContextValue = {
  loading: boolean;
  org: Org | null;
  role: string;
  isSuperAdmin: boolean;
  workspaces: Workspace[];
  currentWorkspace: Workspace | null;
  setCurrentWorkspaceId: (workspaceId: number) => Promise<void>;
};

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

function readToken(): string {
  return localStorage.getItem('voxcore_token') || '';
}

function parseNumber(value: string | null, fallback: number): number {
  const n = Number(value);
  return Number.isFinite(n) && n > 0 ? n : fallback;
}

export function WorkspaceProvider({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true);
  const [org, setOrg] = useState<Org | null>(null);
  const [role, setRole] = useState<string>('viewer');
  const [isSuperAdmin, setIsSuperAdmin] = useState<boolean>(false);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [currentWorkspace, setCurrentWorkspace] = useState<Workspace | null>(null);

  useEffect(() => {
    const load = async () => {
      const token = readToken();
      if (!token) {
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const meRes = await fetch(apiUrl('/api/v1/auth/me'), {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!meRes.ok) {
          setLoading(false);
          return;
        }

        const me = await meRes.json();
        const orgId = Number(me.org_id || me.company_id || 1);
        const workspaceId = Number(me.workspace_id || 1);

        localStorage.setItem('voxcore_org_id', String(orgId));
        localStorage.setItem('voxcore_company_id', String(me.company_id || orgId));
        localStorage.setItem('voxcore_workspace_id', String(workspaceId));
        if (me.org_name) localStorage.setItem('voxcore_org_name', String(me.org_name));
        if (me.workspace_name) localStorage.setItem('voxcore_workspace_name', String(me.workspace_name));
        localStorage.setItem('voxcore_role', String(me.role || 'viewer'));
        localStorage.setItem('voxcore_is_super_admin', String(Boolean(me.is_super_admin)));
        setRole(String(me.role || 'viewer'));
        setIsSuperAdmin(Boolean(me.is_super_admin));

        setOrg({ id: orgId, name: String(me.org_name || 'Organization') });

        const wsRes = await fetch(apiUrl(`/api/v1/orgs/${orgId}/workspaces`), {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (wsRes.ok) {
          const wsData = await wsRes.json();
          const list: Workspace[] = wsData.workspaces || [];
          setWorkspaces(list);
          const selected = list.find((w) => Number(w.id) === workspaceId) || list[0] || null;
          setCurrentWorkspace(selected);
          if (selected) {
            localStorage.setItem('voxcore_workspace_id', String(selected.id));
            localStorage.setItem('voxcore_workspace_name', selected.name);
          }
        } else {
          const fallback: Workspace = {
            id: parseNumber(localStorage.getItem('voxcore_workspace_id'), workspaceId || 1),
            name: localStorage.getItem('voxcore_workspace_name') || 'Default',
          };
          setWorkspaces([fallback]);
          setCurrentWorkspace(fallback);
        }
      } catch {
        const fallbackOrg: Org = {
          id: parseNumber(localStorage.getItem('voxcore_org_id'), 1),
          name: localStorage.getItem('voxcore_org_name') || 'VoxCore Demo',
        };
        const fallbackWs: Workspace = {
          id: parseNumber(localStorage.getItem('voxcore_workspace_id'), 1),
          name: localStorage.getItem('voxcore_workspace_name') || 'Default',
        };
        setOrg(fallbackOrg);
        setRole(localStorage.getItem('voxcore_role') || 'viewer');
        setIsSuperAdmin(localStorage.getItem('voxcore_is_super_admin') === 'true');
        setWorkspaces([fallbackWs]);
        setCurrentWorkspace(fallbackWs);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const setCurrentWorkspaceId = async (workspaceId: number) => {
    const token = readToken();
    const selected = workspaces.find((w) => Number(w.id) === Number(workspaceId));
    if (!selected) return;

    try {
      const response = await fetch(apiUrl('/api/v1/auth/switch-workspace'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ workspace_id: workspaceId }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.access_token) {
          localStorage.setItem('voxcore_token', data.access_token);
        }
      }
    } catch {
      // Keep local switch behavior even if server-side switch endpoint is unavailable.
    }

    setCurrentWorkspace(selected);
    localStorage.setItem('voxcore_workspace_id', String(selected.id));
    localStorage.setItem('voxcore_workspace_name', selected.name);
  };

  const value = useMemo(
    () => ({
      loading,
      org,
      role,
      isSuperAdmin,
      workspaces,
      currentWorkspace,
      setCurrentWorkspaceId,
    }),
    [loading, org, role, isSuperAdmin, workspaces, currentWorkspace]
  );

  return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>;
}

export function useWorkspace() {
  const ctx = useContext(WorkspaceContext);
  if (!ctx) {
    throw new Error('useWorkspace must be used inside WorkspaceProvider');
  }
  return ctx;
}
