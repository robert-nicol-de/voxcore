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

type InspectorSnapshot = {
  pending_approvals?: Array<{ id: number; query?: string; query_text?: string; risk_score?: number; risk_level?: string; submitted_at?: string }>;
  firewall_audit?: Array<{ timestamp?: string; status?: string; stage?: string; query?: string; reasons?: string[] }>;
};

type CompanyPolicies = {
  query_approval_mode?: { enabled?: boolean };
  risk_based_approval?: { enabled?: boolean; threshold?: number };
  protect_sensitive_columns?: { enabled?: boolean; blocked_columns?: string[] };
};

type PlatformGravitySnapshot = {
  copilot_context?: {
    semantic_models?: number;
    data_sources?: number;
    governance_rules?: number;
    recent_queries?: number;
    insights_history?: number;
  };
  autonomous_agents?: {
    insights_detected?: number;
    anomalies?: number;
    policy_blocks?: number;
  };
  governance_simulator_preview?: {
    window_days?: number;
    queries_seen?: number;
    blocked_queries?: number;
    risky_queries_prevented?: number;
  };
  intelligence_graph?: {
    nodes?: {
      metrics?: number;
      tables?: number;
      users?: number;
      policies?: number;
      queries?: number;
      workspaces?: number;
    };
    highlights?: string[];
  };
};

type GovernanceSimulation = {
  queries_analyzed?: number;
  queries_affected?: number;
  queries_blocked?: number;
  queries_requiring_approval?: number;
  high_cost_queries?: number;
  risky_queries_prevented?: number;
};

export default function SettingsPage() {
  const { org, workspaces, currentWorkspace } = useWorkspace();
  const [users, setUsers] = useState<OrgUser[]>([]);
  const [datasources, setDatasources] = useState<OrgDatasource[]>([]);
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [newApiKeyName, setNewApiKeyName] = useState('');
  const [newApiKeySecret, setNewApiKeySecret] = useState<string | null>(null);
  const [inspector, setInspector] = useState<InspectorSnapshot | null>(null);
  const [policies, setPolicies] = useState<CompanyPolicies | null>(null);
  const [sensitiveColumns, setSensitiveColumns] = useState<string[]>([]);
  const [gravity, setGravity] = useState<PlatformGravitySnapshot | null>(null);
  const [simulation, setSimulation] = useState<GovernanceSimulation | null>(null);
  const [simLoading, setSimLoading] = useState(false);

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

    const loadEnterpriseSnapshot = async () => {
      if (!org?.id) return;
      const token = localStorage.getItem('voxcore_token') || '';
      const workspaceHeader: Record<string, string> = currentWorkspace?.id
        ? { 'X-Workspace-ID': String(currentWorkspace.id) }
        : {};

      try {
        const [inspectorRes, policyRes] = await Promise.all([
          fetch(apiUrl('/api/inspector'), {
            headers: { Authorization: `Bearer ${token}`, ...workspaceHeader },
          }),
          fetch(apiUrl(`/api/v1/policies/${org.id}`), {
            headers: { Authorization: `Bearer ${token}` },
          }),
        ]);

        try {
          const gravityRes = await fetch(apiUrl('/api/v1/platform/gravity'), {
            headers: { Authorization: `Bearer ${token}`, ...workspaceHeader },
          });
          if (gravityRes.ok) {
            const gravityData = await gravityRes.json();
            setGravity(gravityData || null);
          } else {
            setGravity(null);
          }
        } catch {
          setGravity(null);
        }

        if (inspectorRes.ok) {
          const data = await inspectorRes.json();
          setInspector(data || null);
        } else {
          setInspector(null);
        }

        if (policyRes.ok) {
          const data = await policyRes.json();
          setPolicies(data.policies || null);
          const cols = data?.policies?.protect_sensitive_columns?.blocked_columns;
          setSensitiveColumns(Array.isArray(cols) ? cols.slice(0, 25).map((v: any) => String(v)) : []);
        } else {
          setPolicies(null);
          setSensitiveColumns([]);
        }
      } catch {
        setInspector(null);
        setPolicies(null);
        setSensitiveColumns([]);
        setGravity(null);
      }
    };

    loadUsers();
    loadDatasources();
    loadApiKeys();
    loadEnterpriseSnapshot();
  }, [org?.id, currentWorkspace?.id]);

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

  const runGovernanceSimulation = async () => {
    if (!org?.id) return;
    setSimLoading(true);
    const token = localStorage.getItem('voxcore_token') || '';
    const workspaceHeader: Record<string, string> = currentWorkspace?.id
      ? { 'X-Workspace-ID': String(currentWorkspace.id) }
      : {};
    try {
      const res = await fetch(apiUrl('/api/v1/platform/governance/simulate'), {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
          ...workspaceHeader,
        },
        body: JSON.stringify({ window_days: 30, policy_overrides: {} }),
      });
      if (!res.ok) {
        setSimulation(null);
        return;
      }
      const data = await res.json();
      setSimulation(data || null);
    } catch {
      setSimulation(null);
    } finally {
      setSimLoading(false);
    }
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
        <h3 style={{ marginTop: 0 }}>Enterprise Governance Snapshot</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 10, marginBottom: 12 }}>
          <div style={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, padding: 10 }}>
            <div style={{ fontSize: 12, color: '#93c5fd' }}>Pending AI Queries</div>
            <div style={{ fontSize: 22, fontWeight: 700 }}>{inspector?.pending_approvals?.length || 0}</div>
          </div>
          <div style={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, padding: 10 }}>
            <div style={{ fontSize: 12, color: '#93c5fd' }}>Risk Threshold</div>
            <div style={{ fontSize: 22, fontWeight: 700 }}>{Number(policies?.risk_based_approval?.threshold ?? 0.7).toFixed(2)}</div>
          </div>
          <div style={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, padding: 10 }}>
            <div style={{ fontSize: 12, color: '#93c5fd' }}>Sensitive Columns Tagged</div>
            <div style={{ fontSize: 22, fontWeight: 700 }}>{sensitiveColumns.length}</div>
          </div>
          <div style={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, padding: 10 }}>
            <div style={{ fontSize: 12, color: '#93c5fd' }}>Audit Events (Recent)</div>
            <div style={{ fontSize: 22, fontWeight: 700 }}>{inspector?.firewall_audit?.length || 0}</div>
          </div>
        </div>

        <div style={{ marginBottom: 10, fontSize: 12, color: '#cbd5e1' }}>
          Approval workflow: {policies?.query_approval_mode?.enabled ? 'ENABLED' : 'DISABLED'} •
          Risk-based approval: {policies?.risk_based_approval?.enabled === false ? 'DISABLED' : 'ENABLED'}
        </div>

        {sensitiveColumns.length > 0 && (
          <div style={{ marginBottom: 10, fontSize: 12, color: '#94a3b8' }}>
            Sensitive policy coverage: {sensitiveColumns.slice(0, 8).join(', ')}
            {sensitiveColumns.length > 8 ? ' ...' : ''}
          </div>
        )}

        <div style={{ display: 'grid', gap: 8 }}>
          {(inspector?.pending_approvals || []).slice(0, 3).map((row) => (
            <div key={row.id} style={{ background: '#0f172a', border: '1px solid rgba(245, 158, 11, 0.35)', borderRadius: 8, padding: 10 }}>
              <div style={{ fontWeight: 700 }}>Query #{row.id} · Risk {(row.risk_score ?? 0).toString()} ({(row.risk_level || 'unknown').toUpperCase()})</div>
              <div style={{ fontSize: 12, color: '#cbd5e1' }}>{row.query || row.query_text || 'No query text available'}</div>
            </div>
          ))}
          {(inspector?.pending_approvals || []).length === 0 && (
            <div style={{ fontSize: 12, color: '#94a3b8' }}>No pending approvals right now.</div>
          )}
        </div>
      </section>

      <section style={{ marginTop: 14, background: '#111827', border: '1px solid rgba(124, 58, 237, 0.35)', borderRadius: 10, padding: 14 }}>
        <h3 style={{ marginTop: 0 }}>Platform Gravity Preview</h3>
        <div style={{ marginBottom: 10, fontSize: 12, color: '#c4b5fd' }}>
          Foundations for AI Copilot, Autonomous Agents, Governance Simulator, and Data Intelligence Graph.
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 10, marginBottom: 12 }}>
          <div style={{ background: '#0f172a', border: '1px solid rgba(124, 58, 237, 0.25)', borderRadius: 8, padding: 10 }}>
            <div style={{ fontSize: 12, color: '#c4b5fd' }}>Copilot Semantic Context</div>
            <div style={{ fontSize: 20, fontWeight: 700 }}>{gravity?.copilot_context?.semantic_models ?? 0} models</div>
          </div>
          <div style={{ background: '#0f172a', border: '1px solid rgba(124, 58, 237, 0.25)', borderRadius: 8, padding: 10 }}>
            <div style={{ fontSize: 12, color: '#c4b5fd' }}>Autonomous Agent Signals</div>
            <div style={{ fontSize: 20, fontWeight: 700 }}>{gravity?.autonomous_agents?.insights_detected ?? 0} insights</div>
          </div>
          <div style={{ background: '#0f172a', border: '1px solid rgba(124, 58, 237, 0.25)', borderRadius: 8, padding: 10 }}>
            <div style={{ fontSize: 12, color: '#c4b5fd' }}>Intelligence Graph Tables</div>
            <div style={{ fontSize: 20, fontWeight: 700 }}>{gravity?.intelligence_graph?.nodes?.tables ?? 0}</div>
          </div>
          <div style={{ background: '#0f172a', border: '1px solid rgba(124, 58, 237, 0.25)', borderRadius: 8, padding: 10 }}>
            <div style={{ fontSize: 12, color: '#c4b5fd' }}>Graph Query Volume</div>
            <div style={{ fontSize: 20, fontWeight: 700 }}>{gravity?.intelligence_graph?.nodes?.queries ?? 0}</div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 10 }}>
          <button
            onClick={() => void runGovernanceSimulation()}
            style={{ background: '#7c3aed', border: 'none', borderRadius: 8, color: '#fff', padding: '8px 12px', cursor: 'pointer' }}
            disabled={simLoading}
          >
            {simLoading ? 'Simulating...' : 'Run AI Governance Simulator (30d)'}
          </button>
        </div>

        {simulation && (
          <div style={{ background: '#0f172a', border: '1px solid rgba(124, 58, 237, 0.25)', borderRadius: 8, padding: 10, fontSize: 12, color: '#ddd6fe' }}>
            <div>Queries analyzed: {simulation.queries_analyzed ?? 0}</div>
            <div>Queries affected: {simulation.queries_affected ?? 0}</div>
            <div>Queries blocked: {simulation.queries_blocked ?? 0}</div>
            <div>Approval required: {simulation.queries_requiring_approval ?? 0}</div>
            <div>High cost queries: {simulation.high_cost_queries ?? 0}</div>
            <div>Risky queries prevented: {simulation.risky_queries_prevented ?? 0}</div>
          </div>
        )}

        {Array.isArray(gravity?.intelligence_graph?.highlights) && gravity?.intelligence_graph?.highlights?.length ? (
          <div style={{ marginTop: 10, fontSize: 12, color: '#cbd5e1' }}>
            {(gravity?.intelligence_graph?.highlights || []).slice(0, 2).map((h) => (
              <div key={h}>• {h}</div>
            ))}
          </div>
        ) : null}
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
