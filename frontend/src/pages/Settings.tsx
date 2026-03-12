import React, { useEffect, useState } from 'react';
import { apiUrl } from '../lib/api';
import PageHeader from '../components/PageHeader';
import { useWorkspace } from '../context/WorkspaceContext';

type OrgUser = {
  id: number;
  email: string;
  role: string;
  workspace_id?: number | null;
};

type OrgDatasource = {
  id: number;
  name: string;
  platform?: string;
  workspace_name?: string;
  status?: string;
};

type ApiKey = {
  id: number;
  name: string;
  key_prefix: string;
  is_active: number;
  created_at?: string;
};

export default function SettingsPage() {
  const { org, workspaces, currentWorkspace } = useWorkspace();
  const [users, setUsers] = useState<OrgUser[]>([]);
  const [datasources, setDatasources] = useState<OrgDatasource[]>([]);
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [newApiKeyName, setNewApiKeyName] = useState('');
  const [newApiKeySecret, setNewApiKeySecret] = useState<string | null>(null);

  useEffect(() => {
    const loadUsers = async () => {
      if (!org?.id) return;
      setLoadingUsers(true);
      try {
        const token = localStorage.getItem('voxcore_token') || '';
        const res = await fetch(apiUrl(`/api/v1/orgs/${org.id}/users`), {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) {
          setUsers([]);
          return;
        }
        const data = await res.json();
        setUsers(data.users || []);
      } catch {
        setUsers([]);
      } finally {
        setLoadingUsers(false);
      }
    };

    const loadDatasources = async () => {
      if (!org?.id) return;
      try {
        const token = localStorage.getItem('voxcore_token') || '';
        const res = await fetch(apiUrl(`/api/v1/orgs/${org.id}/datasources`), {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) {
          setDatasources([]);
          return;
        }
        const data = await res.json();
        setDatasources(data.datasources || []);
      } catch {
        setDatasources([]);
      }
    };

    const loadApiKeys = async () => {
      if (!org?.id) return;
      try {
        const token = localStorage.getItem('voxcore_token') || '';
        const res = await fetch(apiUrl(`/api/v1/orgs/${org.id}/api-keys`), {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) {
          setApiKeys([]);
          return;
        }
        const data = await res.json();
        setApiKeys(data.api_keys || []);
      } catch {
        setApiKeys([]);
      }
    };

    loadUsers();
    loadDatasources();
    loadApiKeys();
  }, [org?.id]);

  const createApiKey = async () => {
    if (!org?.id || !newApiKeyName.trim()) return;
    const token = localStorage.getItem('voxcore_token') || '';
    const res = await fetch(apiUrl(`/api/v1/orgs/${org.id}/api-keys`), {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name: newApiKeyName.trim() }),
    });
    if (!res.ok) return;
    const data = await res.json();
    const created = data.api_key as { api_key?: string } | undefined;
    setNewApiKeySecret(created?.api_key || null);
    setNewApiKeyName('');

    const refresh = await fetch(apiUrl(`/api/v1/orgs/${org.id}/api-keys`), {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (refresh.ok) {
      const payload = await refresh.json();
      setApiKeys(payload.api_keys || []);
    }
  };

  const revokeApiKey = async (id: number) => {
    if (!org?.id) return;
    const token = localStorage.getItem('voxcore_token') || '';
    const res = await fetch(apiUrl(`/api/v1/orgs/${org.id}/api-keys/${id}`), {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return;
    setApiKeys((prev) => prev.map((k) => (k.id === id ? { ...k, is_active: 0 } : k)));
  };

  return (
    <div style={{ color: '#e2e8f0' }}>
      <PageHeader title="Settings" subtitle="Organization, Workspace, and Access Management" />

      <section style={{ marginTop: 12, background: '#111827', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, padding: 14 }}>
        <h3 style={{ marginTop: 0 }}>Tenant Context</h3>
        <div>Organization: {org?.name || 'Unknown'}</div>
        <div>Current Workspace: {currentWorkspace?.name || 'Unknown'}</div>
        <div>Environment: {String((currentWorkspace as { environment?: string } | null)?.environment || 'dev').toUpperCase()}</div>
        <div>Workspace Count: {workspaces.length}</div>
      </section>

      <section style={{ marginTop: 14, background: '#111827', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, padding: 14 }}>
        <h3 style={{ marginTop: 0 }}>Organization Users</h3>
        {loadingUsers ? (
          <div>Loading users...</div>
        ) : users.length === 0 ? (
          <div>No users found or insufficient permissions.</div>
        ) : (
          <div style={{ display: 'grid', gap: 8 }}>
            {users.map((u) => (
              <div key={u.id} style={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, padding: 10 }}>
                <div style={{ fontWeight: 700 }}>{u.email}</div>
                <div style={{ fontSize: 12, color: '#93c5fd' }}>Role: {u.role}</div>
              </div>
            ))}
          </div>
        )}
      </section>

      <section style={{ marginTop: 14, background: '#111827', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, padding: 14 }}>
        <h3 style={{ marginTop: 0 }}>Workspaces</h3>
        <div style={{ display: 'grid', gap: 8 }}>
          {workspaces.map((ws) => (
            <div key={ws.id} style={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, padding: 10 }}>
              <div style={{ fontWeight: 700 }}>{ws.name}</div>
              <div style={{ fontSize: 12, color: '#93c5fd' }}>Workspace ID: {ws.id}</div>
            </div>
          ))}
        </div>
      </section>

      <section style={{ marginTop: 14, background: '#111827', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, padding: 14 }}>
        <h3 style={{ marginTop: 0 }}>Data Sources</h3>
        {datasources.length === 0 ? (
          <div>No data sources found or insufficient permissions.</div>
        ) : (
          <div style={{ display: 'grid', gap: 8 }}>
            {datasources.map((d) => (
              <div key={d.id} style={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, padding: 10 }}>
                <div style={{ fontWeight: 700 }}>{d.name}</div>
                <div style={{ fontSize: 12, color: '#93c5fd' }}>
                  {(d.platform || 'unknown').toUpperCase()} • {d.workspace_name || 'workspace'} • {(d.status || 'active').toUpperCase()}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <section style={{ marginTop: 14, background: '#111827', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, padding: 14 }}>
        <h3 style={{ marginTop: 0 }}>API Keys</h3>
        <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
          <input
            value={newApiKeyName}
            onChange={(e) => setNewApiKeyName(e.target.value)}
            placeholder="Key name"
            style={{ flex: 1, background: '#0f172a', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 8, color: '#e2e8f0', padding: '8px 10px' }}
          />
          <button onClick={() => void createApiKey()} style={{ background: '#2563eb', border: 'none', borderRadius: 8, color: '#fff', padding: '8px 12px', cursor: 'pointer' }}>
            Create
          </button>
        </div>
        {newApiKeySecret && (
          <div style={{ marginBottom: 10, fontSize: 12, color: '#fde68a' }}>
            New key (save now): {newApiKeySecret}
          </div>
        )}
        {apiKeys.length === 0 ? (
          <div>No API keys created.</div>
        ) : (
          <div style={{ display: 'grid', gap: 8 }}>
            {apiKeys.map((k) => (
              <div key={k.id} style={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, padding: 10, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 700 }}>{k.name}</div>
                  <div style={{ fontSize: 12, color: '#93c5fd' }}>{k.key_prefix} • {k.is_active ? 'ACTIVE' : 'REVOKED'}</div>
                </div>
                {k.is_active ? (
                  <button onClick={() => void revokeApiKey(k.id)} style={{ background: 'transparent', border: '1px solid #ef4444', color: '#ef4444', borderRadius: 8, padding: '6px 10px', cursor: 'pointer' }}>
                    Revoke
                  </button>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
