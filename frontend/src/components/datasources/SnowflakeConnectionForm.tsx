import React, { useState } from 'react';
import { apiUrl } from '../../lib/api';

type Props = {
  onSaved?: () => void;
};

export default function SnowflakeConnectionForm({ onSaved }: Props) {
  const [name, setName] = useState('');
  const [account, setAccount] = useState('');
  const [warehouse, setWarehouse] = useState('');
  const [database, setDatabase] = useState('');
  const [schema, setSchema] = useState('public');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('');
  const [queryTimeout, setQueryTimeout] = useState('30');
  const [poolSize, setPoolSize] = useState('5');
  const [loadingTest, setLoadingTest] = useState(false);
  const [loadingSave, setLoadingSave] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const workspaceId = Number(localStorage.getItem('voxcore_workspace_id') || '1');
  const orgId = Number(localStorage.getItem('voxcore_org_id') || '1');

  const config = {
    type: 'snowflake',
    account,
    warehouse,
    database,
    schema,
    username,
    password,
    role,
    query_timeout: Number(queryTimeout || '30'),
    pool_size: Number(poolSize || '5'),
  };

  const testConnection = async () => {
    setLoadingTest(true);
    setMessage(null);
    try {
      const token = localStorage.getItem('voxcore_token') || localStorage.getItem('vox_token') || '';
      const res = await fetch(apiUrl('/api/v1/datasources/test-connection'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          platform: 'snowflake',
          credentials: {
            user: username,
            password,
            account,
            warehouse,
            database,
            schema,
            role,
          },
        }),
      });
      const data = (await res.json().catch(() => ({}))) as { valid?: boolean; error?: string };
      setMessage(data.valid ? 'Connection successful.' : data.error || 'Connection failed.');
    } catch {
      setMessage('Connection test failed due to network error.');
    } finally {
      setLoadingTest(false);
    }
  };

  const saveConnection = async () => {
    if (!name || !account || !warehouse || !database || !username || !password) {
      setMessage('Please fill all required fields.');
      return;
    }
    setLoadingSave(true);
    setMessage(null);
    try {
      const token = localStorage.getItem('voxcore_token') || localStorage.getItem('vox_token') || '';
      const res = await fetch(apiUrl(`/api/v1/datasources?workspace_id=${workspaceId}`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          org_id: orgId,
          workspace_id: workspaceId,
          name,
          type: 'snowflake',
          status: 'active',
          config,
          platform: 'snowflake',
          credentials: {
            user: username,
            password,
            account,
            warehouse,
            database,
            schema,
            role,
          },
        }),
      });
      if (!res.ok) {
        const err = (await res.json().catch(() => ({}))) as { detail?: string };
        setMessage(err.detail || 'Save failed.');
        return;
      }
      const saved = (await res.json().catch(() => ({}))) as { id?: number };
      if (saved.id) {
        await fetch(apiUrl(`/api/v1/datasources/${saved.id}/schema?force_refresh=true`), {
          headers: { Authorization: `Bearer ${token}` },
        }).catch(() => ({}));
      }
      setMessage('Connection saved. Schema discovery started and cache is being prepared.');
      onSaved?.();
    } catch {
      setMessage('Save failed due to network error.');
    } finally {
      setLoadingSave(false);
    }
  };

  return (
    <div className="ds-form-wrap">
      <h2>Add Snowflake Data Source</h2>
      <div className="ds-form-grid">
        <label>Connection Name<input value={name} onChange={(e) => setName(e.target.value)} /></label>
        <label>Account<input value={account} onChange={(e) => setAccount(e.target.value)} /></label>
        <label>Warehouse<input value={warehouse} onChange={(e) => setWarehouse(e.target.value)} /></label>
        <label>Database<input value={database} onChange={(e) => setDatabase(e.target.value)} /></label>
        <label>Schema<input value={schema} onChange={(e) => setSchema(e.target.value)} /></label>
        <label>Username<input value={username} onChange={(e) => setUsername(e.target.value)} /></label>
        <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label>
      </div>

      <details className="ds-advanced">
        <summary>Advanced Settings</summary>
        <div className="ds-form-grid" style={{ marginTop: 12 }}>
          <label>Role<input value={role} onChange={(e) => setRole(e.target.value)} /></label>
          <label>Query Timeout<input value={queryTimeout} onChange={(e) => setQueryTimeout(e.target.value)} /></label>
          <label>Connection Pool Size<input value={poolSize} onChange={(e) => setPoolSize(e.target.value)} /></label>
        </div>
      </details>

      {message && <div className="ds-message">{message}</div>}

      <div className="ds-actions">
        <button className="secondary-btn" onClick={testConnection} disabled={loadingTest}>
          {loadingTest ? 'Testing...' : 'Test Connection'}
        </button>
        <button className="primary-btn" onClick={saveConnection} disabled={loadingSave}>
          {loadingSave ? 'Saving...' : 'Save Connection'}
        </button>
      </div>
    </div>
  );
}
