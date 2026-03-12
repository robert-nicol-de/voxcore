import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { apiUrl } from '../lib/api';

type QueryLogItem = {
  id?: string | number;
  time?: string;
  prompt?: string;
  query?: string;
  generated_sql?: string;
  effective_query?: string;
  risk?: string;
  status?: string;
  reasons?: string[];
  execution_status?: string;
  sandbox_status?: string;
  agent?: string;
  user?: string;
  touched_data?: string[];
};

export default function QueryInvestigation() {
  const { id } = useParams();
  const [item, setItem] = useState<QueryLogItem | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadInvestigation = async () => {
      const companyId = localStorage.getItem('voxcore_company_id') || 'default';
      const workspaceId = localStorage.getItem('voxcore_workspace_id') || 'default';

      try {
        const response = await fetch(
          apiUrl(`/api/v1/query/logs?company_id=${encodeURIComponent(companyId)}&workspace_id=${encodeURIComponent(workspaceId)}`),
        );

        let logs: QueryLogItem[] = [];
        if (response.ok) {
          const payload = await response.json();
          logs = (payload.logs || []).map((entry: QueryLogItem, index: number) => ({
            ...entry,
            id: buildForensicId(entry, index),
          }));
        }

        if (!logs.length) {
          try {
            const cached = localStorage.getItem('voxcloud_query_logs_cache');
            logs = cached ? JSON.parse(cached) : [];
          } catch {
            logs = [];
          }
        }

        const found = logs.find((entry) => String(entry.id) === String(id));
        setItem(found || null);
      } catch {
        setItem(null);
      } finally {
        setLoading(false);
      }
    };

    loadInvestigation();
  }, [id]);

  const derived = useMemo(() => {
    if (!item) {
      return {
        prompt: '--',
        sql: '--',
        risk: 'UNKNOWN',
        policy: 'UNKNOWN',
        sandbox: 'Unknown',
        execution: 'Unknown',
        reasons: ['No reasons captured'],
        triggeredBy: 'Unknown',
        touchedData: ['Unknown'],
      };
    }

    const risk = String(item.risk || 'low').toUpperCase();
    const blocked = isBlocked(item.status);

    return {
      prompt: item.prompt || item.query || '--',
      sql: item.effective_query || item.generated_sql || item.query || '--',
      risk,
      policy: blocked ? 'BLOCKED' : 'ALLOWED',
      sandbox: item.sandbox_status || (blocked ? 'Not executed' : 'Executed in preview mode'),
      execution: item.execution_status || (blocked ? 'Denied' : 'Completed/Allowed'),
      reasons: item.reasons && item.reasons.length > 0 ? item.reasons : [defaultReason(item.status, risk)],
      triggeredBy: item.user || item.agent || 'sql_assistant',
      touchedData: item.touched_data && item.touched_data.length > 0 ? item.touched_data : inferTouchedData(item.query),
    };
  }, [item]);

  if (loading) {
    return <div style={{ color: '#dce8ff' }}>Loading query investigation...</div>;
  }

  if (!item) {
    return (
      <div className="investigation">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
          <h1>AI Query Investigation</h1>
          <Link to="/app/query-logs" className="secondary-btn" style={{ textDecoration: 'none' }}>
            Back to Query Logs
          </Link>
        </div>
        <div className="card">
          <h3>Investigation Not Found</h3>
          <p style={{ margin: 0, color: '#9fb3c8' }}>
            This log entry is no longer available. Run a new query to generate a fresh forensic trail.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="investigation">
      <div className="investigation-header">
        <div>
          <h1>AI Query Investigation</h1>
          <p>
            Forensic ID: <strong>{String(item.id)}</strong> • Time: <strong>{item.time || '--:--'}</strong>
          </p>
        </div>
        <Link to="/app/query-logs" className="secondary-btn" style={{ textDecoration: 'none' }}>
          Back to Query Logs
        </Link>
      </div>

      <div className="investigation-grid">
        <section className="card">
          <h3>User Prompt</h3>
          <p>{derived.prompt}</p>
        </section>

        <section className="card">
          <h3>AI Generated SQL</h3>
          <pre className="investigation-sql">{derived.sql}</pre>
        </section>

        <section className="card">
          <h3>Risk Analysis</h3>
          <span className={`risk ${riskClass(derived.risk)} investigation-risk`}>{derived.risk}</span>
          <p style={{ marginTop: 12, color: '#9fb3c8' }}>Reason: {derived.reasons[0]}</p>
        </section>

        <section className="card">
          <h3>Policy Decision</h3>
          <span className={`investigation-decision ${isBlocked(item.status) ? 'blocked' : 'allowed'}`}>{derived.policy}</span>
        </section>

        <section className="card">
          <h3>Sandbox Result</h3>
          <p>{derived.sandbox}</p>
        </section>

        <section className="card">
          <h3>Execution</h3>
          <p>{derived.execution}</p>
        </section>

        <section className="card">
          <h3>Who Triggered It</h3>
          <p>{derived.triggeredBy}</p>
        </section>

        <section className="card">
          <h3>Data Touched</h3>
          <ul className="investigation-list">
            {derived.touchedData.map((entry) => (
              <li key={entry}>{entry}</li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}

function buildForensicId(item: QueryLogItem, index: number) {
  const time = String(item.time || '').replace(/[^0-9]/g, '');
  const seed = `${time}-${index}`;
  return seed || String(index);
}

function isBlocked(status?: string) {
  const value = (status || '').toLowerCase();
  return value === 'blocked' || value === 'blocked_sensitive';
}

function riskClass(value: string) {
  const normalized = value.toLowerCase();
  if (normalized.includes('high') || normalized.includes('critical')) return 'high';
  if (normalized.includes('med')) return 'medium';
  return 'low';
}

function defaultReason(status: string | undefined, risk: string) {
  if ((status || '').toLowerCase() === 'blocked_sensitive') {
    return 'Sensitive column access detected';
  }
  if ((status || '').toLowerCase() === 'blocked') {
    return 'Blocked by policy or safety validation';
  }
  if (risk.toLowerCase().includes('high')) {
    return 'High risk pattern detected';
  }
  return 'No major policy violations detected';
}

function inferTouchedData(query?: string) {
  if (!query) return ['Unknown'];
  const match = query.match(/from\s+([a-zA-Z0-9_]+)/i);
  if (match?.[1]) {
    return [match[1]];
  }
  return ['Unknown'];
}