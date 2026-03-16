import React, { useEffect, useState } from 'react';
import { apiUrl } from '../lib/api';
import PageHeader from '@/components/layout/PageHeader';
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
  metrics_status?: { status?: string; available?: boolean; detail?: string | null };
  approval_queue_status?: { status?: string; available?: boolean; detail?: string | null };
};

type CompanyPolicies = {
  query_approval_mode?: { enabled?: boolean };
  risk_based_approval?: { enabled?: boolean; threshold?: number };
  protect_sensitive_columns?: { enabled?: boolean; blocked_columns?: string[] };
};

type PlatformGravitySnapshot = {
  control_plane?: {
    status?: string;
    orchestrated_flows?: string[];
    systems?: string[];
  };
  rbac?: {
    workspace_users?: number;
    roles?: Array<{ role?: string; permissions?: string[] }>;
  };
  data_connectors?: {
    supported?: string[];
    configured_total?: number;
    configured_by_platform?: Record<string, number>;
  };
  semantic_layer?: {
    semantic_models?: number;
    builder_status?: string;
  };
  audit_log?: {
    events?: number;
    queries_with_ids?: number;
    latest_query_id?: string | null;
  };
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
    <div className="text-primary">
      <PageHeader title="Settings" subtitle="Organization, Workspace, and Access Management" />

      {/* Tenant Context */}
      <section className="bg-surface rounded-md border-default" style={{ marginTop: 'var(--spacing-1)', borderWidth: 1, padding: 'var(--spacing-2)' }}>
        <h3 className="text-primary" style={{ marginTop: 0 }}>Tenant Context</h3>
        <div>Organization: {org?.name || 'Unknown'}</div>
        <div>Current Workspace: {currentWorkspace?.name || 'Unknown'}</div>
        <div>Environment: {String((currentWorkspace as { environment?: string } | null)?.environment || 'dev').toUpperCase()}</div>
        <div>Workspace Count: {workspaces.length}</div>
      </section>

      {/* Enterprise Governance Snapshot */}
      <section className="bg-surface rounded-md border-default" style={{ marginTop: 'var(--spacing-1)', borderWidth: 1, padding: 'var(--spacing-2)' }}>
        <h3 className="text-primary" style={{ marginTop: 0 }}>Enterprise Governance Snapshot</h3>
        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 'var(--spacing-1)', marginBottom: 'var(--spacing-1)' }}>
          {/* Card metric blocks */}
          <div className="bg-primary rounded-sm border-default shadow-sm" style={{ borderWidth: 1, padding: 'var(--spacing-1)' }}>
            <div className="text-secondary" style={{ fontSize: 12 }}>Pending AI Queries</div>
            <div style={{ fontSize: 22, fontWeight: 700 }}>{inspector?.pending_approvals?.length || 0}</div>
          </div>
          <div className="bg-primary rounded-sm border-default shadow-sm" style={{ borderWidth: 1, padding: 'var(--spacing-1)' }}>
            <div className="text-secondary" style={{ fontSize: 12 }}>Risk Threshold</div>
            <div style={{ fontSize: 22, fontWeight: 700 }}>{Number(policies?.risk_based_approval?.threshold ?? 0.7).toFixed(2)}</div>
          </div>
          <div className="bg-primary rounded-sm border-default shadow-sm" style={{ borderWidth: 1, padding: 'var(--spacing-1)' }}>
            <div className="text-secondary" style={{ fontSize: 12 }}>Sensitive Columns Tagged</div>
            <div style={{ fontSize: 22, fontWeight: 700 }}>{sensitiveColumns.length}</div>
          </div>
          <div className="bg-primary rounded-sm border-default shadow-sm" style={{ borderWidth: 1, padding: 'var(--spacing-1)' }}>
            <div className="text-secondary" style={{ fontSize: 12 }}>Audit Events (Recent)</div>
            <div style={{ fontSize: 22, fontWeight: 700 }}>{inspector?.firewall_audit?.length || 0}</div>
          </div>
        </div>

        <div className="grid text-muted" style={{ gap: 6, fontSize: 12, marginBottom: 'var(--spacing-1)' }}>
          <div>Metrics service: {(inspector?.metrics_status?.status || 'unknown').toUpperCase()}</div>
          <div>Approval queue: {(inspector?.approval_queue_status?.status || 'unknown').toUpperCase()}</div>
        </div>

        <div className="text-muted" style={{ marginBottom: 'var(--spacing-1)', fontSize: 12 }}>
          Approval workflow: {policies?.query_approval_mode?.enabled ? 'ENABLED' : 'DISABLED'} •
          Risk-based approval: {policies?.risk_based_approval?.enabled === false ? 'DISABLED' : 'ENABLED'}
        </div>

        {sensitiveColumns.length > 0 && (
          <div className="text-muted" style={{ marginBottom: 'var(--spacing-1)', fontSize: 12 }}>
            Sensitive policy coverage: {sensitiveColumns.slice(0, 8).join(', ')}
            {sensitiveColumns.length > 8 ? ' ...' : ''}
          </div>
        )}

        <div className="grid" style={{ gap: 'var(--spacing-1)' }}>
          {(inspector?.pending_approvals || []).slice(0, 3).map((row) => (
            <div key={row.id} className="bg-primary rounded-sm border-default shadow-sm" style={{ border: '1px solid var(--color-warning)', padding: 'var(--spacing-1)' }}>
              <div style={{ fontWeight: 700 }}>Query #{row.id} · Risk {(row.risk_score ?? 0).toString()} ({(row.risk_level || 'unknown').toUpperCase()})</div>
              <div className="text-muted" style={{ fontSize: 12 }}>{row.query || row.query_text || 'No query text available'}</div>
            </div>
          ))}
          {(inspector?.pending_approvals || []).length === 0 && (
            <div className="text-muted" style={{ fontSize: 12 }}>No pending approvals right now.</div>
          )}
        </div>
      </section>

      {/* Platform Gravity Preview */}
      <section className="bg-surface rounded-md border-brand" style={{ marginTop: 'var(--spacing-1)', borderWidth: 1, padding: 'var(--spacing-2)' }}>
        <h3 className="text-primary" style={{ marginTop: 0 }}>Platform Gravity Preview</h3>
        <div className="text-accent" style={{ marginBottom: 'var(--spacing-1)', fontSize: 12 }}>
          Foundations for AI Copilot, Autonomous Agents, Governance Simulator, and Data Intelligence Graph.
        </div>

        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--spacing-1)', marginBottom: 'var(--spacing-1)' }}>
          {/* Card metric blocks */}
          <div className="bg-primary rounded-sm border-brand shadow-sm" style={{ borderWidth: 1, padding: 'var(--spacing-1)' }}>
            <div className="text-accent" style={{ fontSize: 12 }}>Copilot Semantic Context</div>
            <div style={{ fontSize: 20, fontWeight: 700 }}>{gravity?.copilot_context?.semantic_models ?? 0} models</div>
          </div>
          <div className="bg-primary rounded-sm border-brand shadow-sm" style={{ borderWidth: 1, padding: 'var(--spacing-1)' }}>
            <div className="text-accent" style={{ fontSize: 12 }}>Autonomous Agent Signals</div>
            <div style={{ fontSize: 20, fontWeight: 700 }}>{gravity?.autonomous_agents?.insights_detected ?? 0} insights</div>
          </div>
          <div className="bg-primary rounded-sm border-brand shadow-sm" style={{ borderWidth: 1, padding: 'var(--spacing-1)' }}>
            <div className="text-accent" style={{ fontSize: 12 }}>Intelligence Graph Tables</div>
            <div style={{ fontSize: 20, fontWeight: 700 }}>{gravity?.intelligence_graph?.nodes?.tables ?? 0}</div>
          </div>
          <div className="bg-primary rounded-sm border-brand shadow-sm" style={{ borderWidth: 1, padding: 'var(--spacing-1)' }}>
            <div className="text-accent" style={{ fontSize: 12 }}>Graph Query Volume</div>
            <div style={{ fontSize: 20, fontWeight: 700 }}>{gravity?.intelligence_graph?.nodes?.queries ?? 0}</div>
          </div>
        </div>

        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 'var(--spacing-1)', marginBottom: 'var(--spacing-1)' }}>
          <div className="bg-primary rounded-sm border-brand shadow-sm" style={{ borderWidth: 1, padding: 'var(--spacing-1)' }}>
            <div className="text-accent" style={{ fontSize: 12 }}>Control Plane</div>
            <div style={{ fontSize: 20, fontWeight: 700 }}>{(gravity?.control_plane?.status || 'inactive').toUpperCase()}</div>
          </div>
          <div className="bg-primary rounded-sm border-brand shadow-sm" style={{ borderWidth: 1, padding: 'var(--spacing-1)' }}>
            <div className="text-accent" style={{ fontSize: 12 }}>RBAC Roles</div>
            <div style={{ fontSize: 20, fontWeight: 700 }}>{gravity?.rbac?.roles?.length ?? 0}</div>
          </div>
          <div className="bg-primary rounded-sm border-brand shadow-sm" style={{ borderWidth: 1, padding: 'var(--spacing-1)' }}>
            <div className="text-accent" style={{ fontSize: 12 }}>Connectors Supported</div>
            <div style={{ fontSize: 20, fontWeight: 700 }}>{gravity?.data_connectors?.supported?.length ?? 0}</div>
          </div>
          <div className="bg-primary rounded-sm border-brand shadow-sm" style={{ borderWidth: 1, padding: 'var(--spacing-1)' }}>
            <div className="text-accent" style={{ fontSize: 12 }}>Audited Query IDs</div>
            <div style={{ fontSize: 20, fontWeight: 700 }}>{gravity?.audit_log?.queries_with_ids ?? 0}</div>
          </div>
        </div>

        <div className="bg-primary rounded-sm border-brand shadow-sm text-accent" style={{ borderWidth: 1, padding: 'var(--spacing-1)', marginBottom: 'var(--spacing-1)', fontSize: 12 }}>
          <div>Core platform systems: {(gravity?.control_plane?.systems || []).join(', ') || 'No systems reported yet.'}</div>
          <div>Latest audited query: {gravity?.audit_log?.latest_query_id || 'None yet'}</div>
          <div>Semantic builder status: {(gravity?.semantic_layer?.builder_status || 'ready').toUpperCase()}</div>
          <div>Configured connector count: {gravity?.data_connectors?.configured_total ?? 0}</div>
        </div>

        {Array.isArray(gravity?.rbac?.roles) && gravity?.rbac?.roles?.length ? (
          <div className="bg-primary rounded-sm border-brand shadow-sm" style={{ borderWidth: 1, padding: 'var(--spacing-1)', marginBottom: 'var(--spacing-1)' }}>
            <div style={{ fontWeight: 700, marginBottom: 8 }}>Enterprise Role Matrix</div>
            <div className="grid" style={{ gap: 'var(--spacing-1)' }}>
              {(gravity?.rbac?.roles || []).map((roleDef) => (
                <div key={roleDef.role} className="text-muted" style={{ fontSize: 12 }}>
                  <strong className="text-accent">{roleDef.role}</strong>: {(roleDef.permissions || []).slice(0, 6).join(', ')}
                </div>
              ))}
            </div>
          </div>
        ) : null}

        {Array.isArray(gravity?.data_connectors?.supported) && gravity?.data_connectors?.supported?.length ? (
          <div className="bg-primary rounded-sm border-brand shadow-sm text-muted" style={{ borderWidth: 1, padding: 'var(--spacing-1)', marginBottom: 'var(--spacing-1)', fontSize: 12 }}>
            Supported connectors: {(gravity?.data_connectors?.supported || []).join(', ')}
          </div>
        ) : null}

        <div className="flex items-center" style={{ gap: 'var(--spacing-1)', marginBottom: 'var(--spacing-1)' }}>
          <button
            onClick={() => void runGovernanceSimulation()}
            className="bg-brand text-primary rounded-sm"
            style={{ border: 'none', padding: '8px 12px', cursor: 'pointer' }}
            disabled={simLoading}
          >
            {simLoading ? 'Simulating...' : 'Run AI Governance Simulator (30d)'}
          </button>
        </div>

        {simulation && (
          <div className="bg-primary rounded-sm border-brand shadow-sm text-accent" style={{ borderWidth: 1, padding: 'var(--spacing-1)', fontSize: 12 }}>
            <div>Queries analyzed: {simulation.queries_analyzed ?? 0}</div>
            <div>Queries affected: {simulation.queries_affected ?? 0}</div>
            <div>Queries blocked: {simulation.queries_blocked ?? 0}</div>
            <div>Approval required: {simulation.queries_requiring_approval ?? 0}</div>
            <div>High cost queries: {simulation.high_cost_queries ?? 0}</div>
            <div>Risky queries prevented: {simulation.risky_queries_prevented ?? 0}</div>
          </div>
        )}

        {Array.isArray(gravity?.intelligence_graph?.highlights) && gravity?.intelligence_graph?.highlights?.length ? (
          <div className="text-muted" style={{ marginTop: 'var(--spacing-1)', fontSize: 12 }}>
            {(gravity?.intelligence_graph?.highlights || []).slice(0, 2).map((h) => (
              <div key={h}>• {h}</div>
            ))}
          </div>
        ) : null}
      </section>

      {/* Organization Users */}
      <section className="bg-surface rounded-md border-default" style={{ marginTop: 'var(--spacing-1)', borderWidth: 1, padding: 'var(--spacing-2)' }}>
        <h3 className="text-primary" style={{ marginTop: 0 }}>Organization Users</h3>
        {loadingUsers ? (
          <div>Loading users...</div>
        ) : users.length === 0 ? (
          <div>No users found or insufficient permissions.</div>
        ) : (
          <div className="grid" style={{ gap: 'var(--spacing-1)' }}>
            {users.map((u) => (
              <div key={u.id} className="bg-primary rounded-sm border-default shadow-sm" style={{ borderWidth: 1, padding: 'var(--spacing-1)' }}>
                <div style={{ fontWeight: 700 }}>{u.email}</div>
                <div className="text-secondary" style={{ fontSize: 12 }}>Role: {u.role}</div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Workspaces */}
      <section className="bg-surface rounded-md border-default" style={{ marginTop: 'var(--spacing-1)', borderWidth: 1, padding: 'var(--spacing-2)' }}>
        <h3 className="text-primary" style={{ marginTop: 0 }}>Workspaces</h3>
        <div className="grid" style={{ gap: 'var(--spacing-1)' }}>
          {workspaces.map((ws) => (
            <div key={ws.id} className="bg-primary rounded-sm border-default shadow-sm" style={{ borderWidth: 1, padding: 'var(--spacing-1)' }}>
              <div style={{ fontWeight: 700 }}>{ws.name}</div>
              <div className="text-secondary" style={{ fontSize: 12 }}>Workspace ID: {ws.id}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Data Sources */}
      <section className="bg-surface rounded-md border-default" style={{ marginTop: 'var(--spacing-1)', borderWidth: 1, padding: 'var(--spacing-2)' }}>
        <h3 className="text-primary" style={{ marginTop: 0 }}>Data Sources</h3>
        {datasources.length === 0 ? (
          <div>No data sources found or insufficient permissions.</div>
        ) : (
          <div className="grid" style={{ gap: 'var(--spacing-1)' }}>
            {datasources.map((d) => (
              <div key={d.id} className="bg-primary rounded-sm border-default shadow-sm" style={{ borderWidth: 1, padding: 'var(--spacing-1)' }}>
                <div style={{ fontWeight: 700 }}>{d.name}</div>
                <div className="text-secondary" style={{ fontSize: 12 }}>
                  {(d.platform || 'unknown').toUpperCase()} • {d.workspace_name || 'workspace'} • {(d.status || 'active').toUpperCase()}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* API Keys */}
      <section className="bg-surface rounded-md border-default" style={{ marginTop: 'var(--spacing-1)', borderWidth: 1, padding: 'var(--spacing-2)' }}>
        <h3 className="text-primary" style={{ marginTop: 0 }}>API Keys</h3>
        <div className="flex items-center" style={{ gap: 'var(--spacing-1)', marginBottom: 'var(--spacing-1)' }}>
          <input
            value={newApiKeyName}
            onChange={(e) => setNewApiKeyName(e.target.value)}
            placeholder="Key name"
            className="bg-primary rounded-sm border-default text-primary"
            style={{ flex: 1, borderWidth: 1, padding: '8px 10px' }}
          />
          <button onClick={() => void createApiKey()} className="bg-info text-primary rounded-sm" style={{ border: 'none', padding: '8px 12px', cursor: 'pointer' }}>
            Create
          </button>
        </div>
        {newApiKeySecret && (
          <div className="text-warning" style={{ marginBottom: 'var(--spacing-1)', fontSize: 12 }}>
            New key (save now): {newApiKeySecret}
          </div>
        )}
        {apiKeys.length === 0 ? (
          <div>No API keys created.</div>
        ) : (
          <div className="grid" style={{ gap: 'var(--spacing-1)' }}>
            {apiKeys.map((k) => (
              <div key={k.id} className="bg-primary rounded-sm border-default shadow-sm flex items-center justify-between" style={{ borderWidth: 1, padding: 'var(--spacing-1)' }}>
                <div>
                  <div style={{ fontWeight: 700 }}>{k.name}</div>
                  <div className="text-secondary" style={{ fontSize: 12 }}>{k.key_prefix} • {k.is_active ? 'ACTIVE' : 'REVOKED'}</div>
                </div>
                {k.is_active ? (
                  <button onClick={() => void revokeApiKey(k.id)} className="text-error border-error rounded-sm" style={{ background: 'transparent', borderWidth: 1, padding: '6px 10px', cursor: 'pointer' }}>
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
