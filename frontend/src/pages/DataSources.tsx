import React, { useCallback, useEffect, useState } from 'react';
import PageHeader from '../components/PageHeader';
import DataSourceSelector from '../components/datasources/DataSourceSelector';
import { apiUrl } from '../lib/api';

type DatasourceRow = {
  id: number;
  name: string;
  platform?: string;
  type?: string;
  status?: string;
  workspace_id?: number;
  created_at?: string;
};

export default function DataSourcesPage() {
  const [openSelector, setOpenSelector] = useState(false);
  const [sources, setSources] = useState<DatasourceRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const workspaceId = Number(localStorage.getItem('voxcore_workspace_id') || '1');

  const fetchSources = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('voxcore_token') || localStorage.getItem('vox_token') || '';
      const res = await fetch(apiUrl(`/api/v1/datasources?workspace_id=${workspaceId}`), {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) {
        const payload = (await res.json().catch(() => ({}))) as { detail?: string };
        throw new Error(payload.detail || 'Failed to load data sources.');
      }

      const rows = (await res.json().catch(() => [])) as DatasourceRow[];
      setSources(Array.isArray(rows) ? rows : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data sources.');
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    fetchSources();
  }, [fetchSources]);

  return (
    <div>
      <PageHeader
        title="Data Sources"
        subtitle="Manage database and warehouse connections for VoxQuery"
      />

      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
        <button className="secondary-btn" onClick={fetchSources} style={{ marginRight: 10 }}>
          Refresh
        </button>
        <button className="primary-btn" onClick={() => setOpenSelector(true)}>
          Add Source
        </button>
      </div>

      <section className="datasources-panel">
        <div className="datasources-panel-title">Connected Sources</div>
        <p className="datasources-panel-subtitle">
          Add a source to enable schema discovery, AI SQL assistance, and policy governance.
        </p>

        {loading && <div className="ds-message" style={{ marginTop: 14 }}>Loading data sources...</div>}
        {error && <div className="ds-message" style={{ marginTop: 14, color: '#ff9a9a' }}>{error}</div>}

        {!loading && !error && sources.length === 0 && (
          <div className="ds-message" style={{ marginTop: 14 }}>
            No data sources connected yet.
          </div>
        )}

        {!loading && !error && sources.length > 0 && (
          <div style={{ marginTop: 16, overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={cellHead}>Name</th>
                  <th style={cellHead}>Platform</th>
                  <th style={cellHead}>Status</th>
                  <th style={cellHead}>Workspace</th>
                  <th style={cellHead}>Created</th>
                </tr>
              </thead>
              <tbody>
                {sources.map((s) => (
                  <tr key={s.id}>
                    <td style={cellBody}>{s.name}</td>
                    <td style={cellBody}>{(s.platform || s.type || 'unknown').toUpperCase()}</td>
                    <td style={cellBody}>{(s.status || 'active').toUpperCase()}</td>
                    <td style={cellBody}>{String(s.workspace_id || workspaceId)}</td>
                    <td style={cellBody}>{formatDate(s.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {openSelector && (
        <div className="ds-modal-overlay" onClick={() => setOpenSelector(false)}>
          <div className="ds-modal" onClick={(e) => e.stopPropagation()}>
            <DataSourceSelector onClose={() => setOpenSelector(false)} />
          </div>
        </div>
      )}
    </div>
  );
}

const cellHead: React.CSSProperties = {
  textAlign: 'left',
  padding: '10px 8px',
  fontSize: 12,
  color: '#9ec3ff',
  borderBottom: '1px solid #24344d',
};

const cellBody: React.CSSProperties = {
  textAlign: 'left',
  padding: '10px 8px',
  fontSize: 13,
  color: '#d8e5fb',
  borderBottom: '1px solid #1e2b3f',
};

function formatDate(value?: string) {
  if (!value) return '-';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString();
}
