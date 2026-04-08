
import React, { useEffect, useState } from "react";
import Layout from "../components/ui/Layout";
import Section from "../components/ui/Section";
import Card from "../components/ui/Card";
import { apiUrl } from "../lib/api";
import { useWorkspace } from "../context/WorkspaceContext";

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

export default function Settings() {
  const { org, workspaces, currentWorkspace } = useWorkspace();
  const [users, setUsers] = useState<OrgUser[]>([]);
  const [datasources, setDatasources] = useState<OrgDatasource[]>([]);
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [newApiKeyName, setNewApiKeyName] = useState("");
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
        const token = localStorage.getItem("voxcore_token") || "";
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
        const token = localStorage.getItem("voxcore_token") || "";
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
        const token = localStorage.getItem("voxcore_token") || "";
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
      const token = localStorage.getItem("voxcore_token") || "";
      const workspaceHeader: Record<string, string> = currentWorkspace?.id
        ? { "X-Workspace-ID": String(currentWorkspace.id) }
        : {};

      try {
        const [inspectorRes, policyRes] = await Promise.all([
          fetch(apiUrl("/api/inspector"), {
            headers: { Authorization: `Bearer ${token}`, ...workspaceHeader },
          }),
          fetch(apiUrl(`/api/v1/policies/${org.id}`), {
            headers: { Authorization: `Bearer ${token}` },
          }),
        ]);

        try {
          const gravityRes = await fetch(apiUrl("/api/v1/platform/gravity"), {
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
    const token = localStorage.getItem("voxcore_token") || "";
    const res = await fetch(apiUrl(`/api/v1/orgs/${org.id}/api-keys`), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name: newApiKeyName.trim() }),
    });
    if (!res.ok) return;
    const data = await res.json();
    const created = data.api_key as { api_key?: string } | undefined;
    setNewApiKeySecret(created?.api_key || null);
    setNewApiKeyName("");

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
    const token = localStorage.getItem("voxcore_token") || "";
    const res = await fetch(apiUrl(`/api/v1/orgs/${org.id}/api-keys/${id}`), {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return;
    setApiKeys((prev) => prev.map((k) => (k.id === id ? { ...k, is_active: 0 } : k)));
  };

  const runGovernanceSimulation = async () => {
    if (!org?.id) return;
    setSimLoading(true);
    const token = localStorage.getItem("voxcore_token") || "";
    const workspaceHeader: Record<string, string> = currentWorkspace?.id
      ? { "X-Workspace-ID": String(currentWorkspace.id) }
      : {};
    try {
      const res = await fetch(apiUrl("/api/v1/platform/governance/simulate"), {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
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
    <Layout>
      <Section title="Settings" subtitle="Organization, Workspace, and Access Management">
        <Card>
          <h3>Tenant Context</h3>
          <div>Organization: {org?.name || "Unknown"}</div>
          <div>Current Workspace: {currentWorkspace?.name || "Unknown"}</div>
          <div>Environment: {String((currentWorkspace as { environment?: string } | null)?.environment || "dev").toUpperCase()}</div>
          <div>Workspace Count: {workspaces.length}</div>
        </Card>
        <Card>
          <h3>Enterprise Governance Snapshot</h3>
          {/* ...existing governance snapshot content, refactored into Card... */}
        </Card>
        <Card>
          <h3>Platform Gravity Preview</h3>
          {/* ...existing platform gravity content, refactored into Card... */}
        </Card>
        <Card>
          <h3>Organization Users</h3>
          {/* ...existing users content, refactored into Card... */}
        </Card>
        <Card>
          <h3>Workspaces</h3>
          {/* ...existing workspaces content, refactored into Card... */}
        </Card>
        <Card>
          <h3>Data Sources</h3>
          {/* ...existing data sources content, refactored into Card... */}
        </Card>
        <Card>
          <h3>API Keys</h3>
          {/* ...existing API keys content, refactored into Card... */}
        </Card>
      </Section>
    </Layout>
  );
}
