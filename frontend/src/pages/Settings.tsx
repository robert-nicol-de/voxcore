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

export default function SettingsPage() {
  const { org, workspaces, currentWorkspace } = useWorkspace();
  const [users, setUsers] = useState<OrgUser[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);

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

    loadUsers();
  }, [org?.id]);

  return (
    <div style={{ color: '#e2e8f0' }}>
      <PageHeader title="Settings" subtitle="Organization, Workspace, and Access Management" />

      <section style={{ marginTop: 12, background: '#111827', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, padding: 14 }}>
        <h3 style={{ marginTop: 0 }}>Tenant Context</h3>
        <div>Organization: {org?.name || 'Unknown'}</div>
        <div>Current Workspace: {currentWorkspace?.name || 'Unknown'}</div>
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
    </div>
  );
}
