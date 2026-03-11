import React, { useState } from 'react';
import { apiUrl } from '../lib/api';

type SchemaColumn = {
  name: string;
  type: string;
};

type SchemaTable = {
  table: string;
  columns: SchemaColumn[];
};

export default function Databases() {
  const [dbType, setDbType] = useState('sqlserver');
  const [host, setHost] = useState('');
  const [database, setDatabase] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [result, setResult] = useState<string | null>(null);
  const [testing, setTesting] = useState(false);
  const [connected, setConnected] = useState(false);
  const [schemaLoading, setSchemaLoading] = useState(false);
  const [schema, setSchema] = useState<SchemaTable[]>([]);
  const [connectionName, setConnectionName] = useState('');

  const companyId = 'default';

  async function testConnection() {
    setTesting(true);
    setResult(null);
    try {
      const response = await fetch(apiUrl('/api/v1/auth/test-connection'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          database: dbType,
          credentials: {
            host,
            database,
            username,
            password,
          },
        }),
      });

      const data = await response.json();

      if (data.ok) {
        const savedConnectionName = `${dbType}-default`;

        const saveResponse = await fetch(apiUrl('/api/v1/auth/connections/save'), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            company_id: companyId,
            connection_name: savedConnectionName,
            database: dbType,
            credentials: {
              type: dbType,
              host,
              database,
              username,
              password,
            },
          }),
        });

        const saveData = await saveResponse.json().catch(() => ({}));
        if (!saveResponse.ok || !saveData.ok) {
          setConnected(false);
          setResult(saveData.detail || saveData.message || 'Connected, but failed to save connection');
          return;
        }

        setConnectionName(savedConnectionName);
        setConnected(true);
        setResult(`Connected (${data.database})`);
      } else {
        setConnected(false);
        setResult(`${data.message || data.detail || 'Connection failed'}`);
      }
    } catch {
      setConnected(false);
      setResult('Network error');
    } finally {
      setTesting(false);
    }
  }

  async function loadSchema() {
    if (!connectionName) {
      setResult('No saved connection found for schema discovery');
      return;
    }

    setSchemaLoading(true);
    try {
      const response = await fetch(
        apiUrl(`/api/v1/schema/discover?company_id=${encodeURIComponent(companyId)}&connection_name=${encodeURIComponent(connectionName)}`)
      );
      const data = await response.json();

      if (!response.ok) {
        setResult(data.detail || 'Schema discovery failed');
        return;
      }

      setSchema(data.schema || []);
    } catch {
      setResult('Schema discovery request failed');
    } finally {
      setSchemaLoading(false);
    }
  }

  const inputStyle: React.CSSProperties = {
    width: '100%',
    marginBottom: 12,
    padding: '10px 12px',
    borderRadius: 8,
    border: '1px solid rgba(255,255,255,0.2)',
    background: 'rgba(15,23,42,0.6)',
    color: '#e2e8f0',
  };

  return (
    <div style={{ padding: 40, color: '#e2e8f0' }}>
      <h1>Database Manager</h1>

      <div style={{ maxWidth: 500 }}>
        <select
          value={dbType}
          onChange={(e) => setDbType(e.target.value)}
          style={inputStyle}
        >
          <option value="sqlserver">SQL Server</option>
          <option value="postgres">PostgreSQL</option>
          <option value="mysql">MySQL</option>
        </select>

        <input placeholder="Host" value={host} onChange={(e) => setHost(e.target.value)} style={inputStyle} />

        <input
          placeholder="Database"
          value={database}
          onChange={(e) => setDatabase(e.target.value)}
          style={inputStyle}
        />

        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={inputStyle}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={inputStyle}
        />

        <button
          onClick={testConnection}
          disabled={testing}
          style={{
            padding: '10px 14px',
            borderRadius: 8,
            border: '1px solid #60a5fa',
            background: testing ? 'rgba(96,165,250,0.2)' : '#2563eb',
            color: '#fff',
            cursor: testing ? 'default' : 'pointer',
          }}
        >
          {testing ? 'Testing...' : 'Test Connection'}
        </button>

        {connected && (
          <button
            onClick={loadSchema}
            disabled={schemaLoading}
            style={{
              marginLeft: 10,
              padding: '10px 14px',
              borderRadius: 8,
              border: '1px solid #22c55e',
              background: schemaLoading ? 'rgba(34,197,94,0.2)' : '#15803d',
              color: '#fff',
              cursor: schemaLoading ? 'default' : 'pointer',
            }}
          >
            {schemaLoading ? 'Discovering...' : 'Discover Schema'}
          </button>
        )}

        {result && <p style={{ marginTop: 14 }}>{result}</p>}

        {schema.map((table) => (
          <div key={table.table} style={{ marginTop: 16, background: 'rgba(28,35,48,0.7)', padding: 12, borderRadius: 8 }}>
            <h3 style={{ margin: '0 0 8px 0' }}>{table.table}</h3>

            {table.columns.map((col) => (
              <p key={`${table.table}-${col.name}`} style={{ margin: '2px 0', fontFamily: 'monospace' }}>
                {col.name} ({col.type})
              </p>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
