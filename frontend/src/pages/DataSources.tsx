import React, { useCallback, useEffect, useState } from 'react';
import PageHeader from '@/components/layout/PageHeader';
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
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Data Sources"
        subtitle="Manage database and warehouse connections for VoxQuery"
      />

      <div className="flex justify-end mb-4 gap-2">
        <button className="secondary-btn" onClick={fetchSources}>
          Refresh
        </button>
        <button className="primary-btn" onClick={() => setOpenSelector(true)}>
          Add Source
        </button>
      </div>

      <section className="datasources-panel card bg-surface border-default rounded-md p-6 shadow-sm">
        <div className="datasources-panel-title text-lg font-semibold mb-1">Connected Sources</div>
        <p className="datasources-panel-subtitle text-muted text-sm mb-4">
          Add a source to enable schema discovery, AI SQL assistance, and policy governance.
        </p>

        {loading && <div className="ds-message mt-3 text-secondary">Loading data sources...</div>}
        {error && <div className="ds-message mt-3 text-error">{error}</div>}

        {!loading && !error && sources.length === 0 && (
          <div className="ds-message mt-3 text-muted">
            No data sources connected yet.
          </div>
        )}

        {!loading && !error && sources.length > 0 && (
          <div className="mt-4 overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr>
                  <th className="text-left px-3 py-2 text-xs text-accent-primary border-b border-default">Name</th>
                  <th className="text-left px-3 py-2 text-xs text-accent-primary border-b border-default">Platform</th>
                  <th className="text-left px-3 py-2 text-xs text-accent-primary border-b border-default">Status</th>
                  <th className="text-left px-3 py-2 text-xs text-accent-primary border-b border-default">Workspace</th>
                  <th className="text-left px-3 py-2 text-xs text-accent-primary border-b border-default">Created</th>
                </tr>
              </thead>
              <tbody>
                {sources.map((s) => (
                  <tr key={s.id}>
                    <td className="px-3 py-2 text-sm text-primary border-b border-default">{s.name}</td>
                    <td className="px-3 py-2 text-sm text-secondary border-b border-default">{(s.platform || s.type || 'unknown').toUpperCase()}</td>
                    <td className="px-3 py-2 text-sm text-secondary border-b border-default">{(s.status || 'active').toUpperCase()}</td>
                    <td className="px-3 py-2 text-sm text-secondary border-b border-default">{String(s.workspace_id || workspaceId)}</td>
                    <td className="px-3 py-2 text-sm text-secondary border-b border-default">{formatDate(s.created_at)}</td>
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


function formatDate(value?: string) {
  if (!value) return '-';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString();
}
