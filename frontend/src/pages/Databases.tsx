import React, { useState } from 'react';
import { apiUrl } from '../lib/api';
import EmptyState from '../components/EmptyState';
import PageHeader from '../components/PageHeader';
import SchemaExplorer from '../components/SchemaExplorer';
import DataSourceSelector, { type PlatformOption } from '../components/DataSourceSelector';

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
  const [showSelector, setShowSelector] = useState(false);
  const [selectedSource, setSelectedSource] = useState<PlatformOption | null>(null);
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
  const [showModal, setShowModal] = useState(false);
  const [rememberConnection, setRememberConnection] = useState(true);
  const [connectedDatabases, setConnectedDatabases] = useState<Array<{ name: string; type: string; host: string; status: string }>>(() => {
    try {
      const stored = localStorage.getItem('voxcloud_connected_databases');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  const companyId = localStorage.getItem('voxcore_company_id') || 'default';
  const workspaceId = localStorage.getItem('voxcore_workspace_id') || 'default';
  const token = localStorage.getItem('voxcore_token') || localStorage.getItem('vox_token') || '';

  async function testConnection() {
    setTesting(true);
    setResult(null);
    try {
      const response = await fetch(apiUrl('/api/v1/auth/test-connection'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          database: dbType,
          host,
          warehouse_host: host,
          username,
          password,
          database_name: database,
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
        setConnected(true);
        setResult(`Connected (${data.database})`);

        // Only save if user checked "Remember connection"
        if (rememberConnection) {
          const savedConnectionName = `${dbType}-default`;

          const saveResponse = await fetch(apiUrl('/api/v1/auth/connections/save'), {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
              company_id: companyId,
              workspace_id: workspaceId,
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
            setResult(saveData.detail || saveData.message || 'Connected, but failed to save connection');
            return;
          }

          setConnectionName(savedConnectionName);
          const dbRecord = {
            name: database || `${dbType}-database`,
            type: dbType,
            host,
            status: 'Connected',
          };
          const next = [dbRecord, ...connectedDatabases.filter((item) => item.name !== dbRecord.name)];
          setConnectedDatabases(next);
          localStorage.setItem('voxcloud_connected_databases', JSON.stringify(next));
        }

        setShowModal(false);
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
        apiUrl(`/api/v1/schema/discover?company_id=${encodeURIComponent(companyId)}&workspace_id=${encodeURIComponent(workspaceId)}&connection_name=${encodeURIComponent(connectionName)}`),
        { headers: { Authorization: `Bearer ${token}` } }
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

  function closeModal() {
    setShowModal(false);
    setSelectedSource(null);
    setDbType('sqlserver');
    setHost('');
    setDatabase('');
    setUsername('');
    setPassword('');
    setRememberConnection(true);
    setResult(null);
  }

  function disconnectDatabase(dbName: string) {
    const updated = connectedDatabases.filter((db) => db.name !== dbName);
    setConnectedDatabases(updated);
    localStorage.setItem('voxcloud_connected_databases', JSON.stringify(updated));
    setResult(`Disconnected from ${dbName}`);
  }

  const inputStyle: React.CSSProperties = {
    width: '100%',
    marginBottom: 12,
    padding: '10px 12px',
    borderRadius: 8,
    border: '1px solid var(--platform-border)',
    background: 'rgba(10,16,28,0.8)',
    color: '#e2e8f0',
  };

  return (
    <div style={{ color: '#e2e8f0' }}>
      <h1 style={{ marginTop: 0, fontSize: '2rem', letterSpacing: '-0.03em' }}>Databases</h1>

      {showSelector && (
        <section style={panelStyle}>
          <DataSourceSelector
            onSelect={(source) => {
              setSelectedSource(source);
              setDbType(source.code);
              setShowSelector(false);
              if (source.code === 'semantic') {
                setResult('Use Semantic Models from the Semantic Models page.');
                return;
              }
              setShowModal(true);
            }}
            onCancel={() => setShowSelector(false)}
          />
        </section>
      )}

      <section style={panelStyle}>
        <h2 style={sectionTitle}>Connected Databases</h2>
        <div style={{ display: 'grid', gap: 12 }}>
          {connectedDatabases.length === 0 ? (
            <EmptyState
              title="No databases connected"
              message="Connect your first database to begin analyzing queries and protecting your data."
              variant="compact"
              action={<button className="primary-btn" onClick={() => setShowSelector(true)}>Add Data Source</button>}
            />
          ) : (
            connectedDatabases.map((db) => (
              <div key={db.name} style={databaseRowStyle}>
                <div>
                  <div style={{ fontWeight: 700, color: '#ffffff' }}>{db.name}</div>
                  <div style={{ color: 'var(--platform-muted)', fontSize: 13, marginTop: 4 }}>{db.type.toUpperCase()} • {db.host || 'host not provided'}</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                  <div style={{ color: '#35d07f', fontWeight: 700 }}>Status: {db.status}</div>
                  <button
                    onClick={() => disconnectDatabase(db.name)}
                    style={{
                      padding: '6px 12px',
                      borderRadius: 6,
                      border: '1px solid #ff6b6b',
                      background: 'transparent',
                      color: '#ff6b6b',
                      fontSize: 12,
                      fontWeight: 600,
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                    }}
                    onMouseEnter={(e) => {
                      (e.target as HTMLButtonElement).style.background = 'rgba(255, 107, 107, 0.1)';
                    }}
                    onMouseLeave={(e) => {
                      (e.target as HTMLButtonElement).style.background = 'transparent';
                    }}
                  >
                    Disconnect
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        <div style={{ display: 'flex', gap: 12, marginTop: 20, flexWrap: 'wrap' }}>
          <button onClick={() => setShowSelector(true)} style={primaryButton}>Add Data Source</button>
          {connected && (
            <button onClick={loadSchema} disabled={schemaLoading} style={secondaryButton}>
              {schemaLoading ? 'Discovering...' : 'Discover Schema'}
            </button>
          )}
        </div>

        {result && <p style={{ marginTop: 14, color: '#d6e4ff' }}>{result}</p>}

        {schema.length > 0 && (
          <div style={{ marginTop: 18, display: 'grid', gap: 10 }}>
            {schema.map((table) => (
              <div key={table.table} style={{ background: 'rgba(11,17,30,0.8)', border: '1px solid var(--platform-border)', padding: 12, borderRadius: 8 }}>
                <h3 style={{ margin: '0 0 8px 0' }}>{table.table}</h3>
                {table.columns.map((col) => (
                  <p key={`${table.table}-${col.name}`} style={{ margin: '2px 0', fontFamily: 'monospace', color: '#c9dbff' }}>
                    {col.name} ({col.type})
                  </p>
                ))}
              </div>
            ))}
          </div>
        )}

        <div style={{ marginTop: 24 }}>
          <SchemaExplorer connectionName={connectionName || undefined} />
        </div>
      </section>

      {showModal && (
        <div style={overlayStyle}>
          <div style={modalStyle}>
            <h2 style={{ marginTop: 0, marginBottom: 14 }}>
              Add {selectedSource?.name || 'Database'} Connection
            </h2>
            <input placeholder="Host" value={host} onChange={(e) => setHost(e.target.value)} style={inputStyle} />
            <input placeholder="Database" value={database} onChange={(e) => setDatabase(e.target.value)} style={inputStyle} />
            <input placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} style={inputStyle} />
            <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} style={inputStyle} />
            
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 12, marginBottom: 16, fontSize: 13, color: '#9fb3c8', cursor: 'pointer' }}>
              <input 
                type="checkbox" 
                checked={rememberConnection} 
                onChange={(e) => setRememberConnection(e.target.checked)}
                style={{ cursor: 'pointer' }}
              />
              Remember this connection
            </label>

            <div style={{ display: 'flex', gap: 10 }}>
              <button onClick={testConnection} disabled={testing} style={primaryButton}>
                {testing ? 'Testing...' : 'Test & Connect'}
              </button>
              <button onClick={closeModal} style={secondaryButton}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const panelStyle: React.CSSProperties = {
  background: 'var(--platform-card-bg)',
  border: '1px solid var(--platform-border)',
  borderRadius: 12,
  padding: 24,
};

const sectionTitle: React.CSSProperties = {
  marginTop: 0,
  marginBottom: 12,
  fontSize: '1.1rem',
};

const databaseRowStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  gap: 12,
  padding: 16,
  borderRadius: 10,
  border: '1px solid var(--platform-border)',
  background: 'rgba(10,16,28,0.8)',
};

const primaryButton: React.CSSProperties = {
  padding: '10px 14px',
  borderRadius: 10,
  border: '1px solid var(--platform-accent)',
  background: 'var(--platform-accent)',
  color: '#fff',
  cursor: 'pointer',
  fontWeight: 700,
};

const secondaryButton: React.CSSProperties = {
  padding: '10px 14px',
  borderRadius: 10,
  border: '1px solid var(--platform-border)',
  background: 'transparent',
  color: '#e2e8f0',
  cursor: 'pointer',
  fontWeight: 700,
};

const overlayStyle: React.CSSProperties = {
  position: 'fixed',
  inset: 0,
  background: 'rgba(3, 7, 18, 0.75)',
  display: 'grid',
  placeItems: 'center',
  padding: 24,
  zIndex: 60,
};

const modalStyle: React.CSSProperties = {
  width: 'min(560px, 100%)',
  background: '#101826',
  border: '1px solid var(--platform-border)',
  borderRadius: 12,
  padding: 24,
};
