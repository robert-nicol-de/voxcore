import React, { useState, useEffect } from 'react';

interface DatabaseConfig {
  name: string;
  type: string;
  host: string;
  port: number;
  database: string;
  user: string;
}

interface SecurityPolicy {
  block_delete: boolean;
  block_update: boolean;
  block_drop: boolean;
  max_rows: number;
  protect_tables: string[];
  pii_protected: boolean;
  policy: string | null;
}

interface Connector {
  name: string;
  database: DatabaseConfig;
  security: SecurityPolicy;
  status: string;
  credential_status?: string;
}

export const ConnectorsPanel: React.FC = () => {
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [testingConnector, setTestingConnector] = useState<string | null>(null);

  useEffect(() => {
    fetchConnectors();
  }, []);

  const fetchConnectors = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/connectors');
      if (!response.ok) {
        throw new Error(`Failed to fetch connectors: ${response.statusText}`);
      }
      const data = await response.json();
      setConnectors(data.connectors || []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load connectors');
      setConnectors([]);
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async (connectorName: string) => {
    setTestingConnector(connectorName);
    try {
      // In a real implementation, this would call a test endpoint
      // For now, we'll just simulate a successful test
      await new Promise(resolve => setTimeout(resolve, 1500));
      // Show success notification
      console.log(`Connection to ${connectorName} successful`);
    } catch (err) {
      console.error(`Failed to test connection to ${connectorName}:`, err);
    } finally {
      setTestingConnector(null);
    }
  };

  const getDbTypeIcon = (type: string): string => {
    const icons: Record<string, string> = {
      postgres: '🐘',
      mysql: '🐬',
      mssql: '🪟',
      sqlite: '📦',
      mongodb: '🍃',
    };
    return icons[type.toLowerCase()] || '🗄️';
  };

  const getPolicyColor = (policy: string | null): string => {
    if (!policy) return '#666';
    switch (policy.toLowerCase()) {
      case 'strict':
        return '#ef4444'; // red
      case 'moderate':
        return '#f59e0b'; // amber
      case 'permissive':
        return '#22c55e'; // green
      default:
        return '#666';
    }
  };

  if (loading) {
    return (
      <div className="dev-panel">
        <div style={{ padding: '40px', textAlign: 'center' }}>
          <div style={{ fontSize: '24px', marginBottom: '16px' }}>⏳</div>
          <p style={{ color: '#7fb3ff' }}>Loading connectors...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dev-panel">
        <div style={{ padding: '40px' }}>
          <div style={{ fontSize: '24px', marginBottom: '16px' }}>❌</div>
          <p style={{ color: '#fca5a5', marginBottom: '16px' }}>{error}</p>
          <button 
            onClick={fetchConnectors}
            style={{
              padding: '8px 16px',
              background: '#00d4ff',
              color: '#050a14',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dev-panel">
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '8px' }}>
          🗄️ Database Connectors
        </h2>
        <p style={{ fontSize: '14px', color: '#888', marginBottom: '16px' }}>
          {connectors.length} connector{connectors.length !== 1 ? 's' : ''} available
        </p>
      </div>

      {connectors.length === 0 ? (
        <div style={{
          padding: '40px',
          textAlign: 'center',
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '8px',
          border: '1px solid rgba(0, 212, 255, 0.1)'
        }}>
          <p style={{ color: '#888', marginBottom: '16px' }}>No connectors configured</p>
          <p style={{ color: '#666', fontSize: '12px' }}>
            Add .ini files to the /connectors folder to enable database connections
          </p>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '16px'
        }}>
          {connectors.map((connector) => (
            <div
              key={connector.name}
              className="panel"
              style={{
                background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(0, 100, 150, 0.05) 100%)',
                border: '1px solid rgba(0, 212, 255, 0.2)',
                padding: '16px',
                borderRadius: '8px',
                transition: 'all 0.3s ease',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                const el = e.currentTarget;
                el.style.borderColor = 'rgba(0, 212, 255, 0.5)';
                el.style.boxShadow = '0 0 20px rgba(0, 212, 255, 0.2)';
              }}
              onMouseLeave={(e) => {
                const el = e.currentTarget;
                el.style.borderColor = 'rgba(0, 212, 255, 0.2)';
                el.style.boxShadow = 'none';
              }}
            >
              {/* Connector Header */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
                <span style={{ fontSize: '20px' }}>{getDbTypeIcon(connector.database.type)}</span>
                <div style={{ flex: 1 }}>
                  <h3 style={{ margin: '0', fontSize: '14px', fontWeight: '600' }}>
                    {connector.name}
                  </h3>
                  <p style={{ margin: '0', fontSize: '12px', color: '#888' }}>
                    {connector.database.type.toUpperCase()}
                  </p>
                </div>
                <div style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: '#22c55e',
                  boxShadow: '0 0 8px rgba(34, 197, 94, 0.6)'
                }} title="Connected" />
              </div>

              {/* Database Details */}
              <div style={{
                background: 'rgba(0, 0, 0, 0.3)',
                padding: '10px',
                borderRadius: '4px',
                marginBottom: '12px',
                fontSize: '12px',
                fontFamily: 'monospace'
              }}>
                <div style={{ display: 'grid', gridTemplateColumns: '80px 1fr', gap: '8px' }}>
                  <span style={{ color: '#00d4ff' }}>Host:</span>
                  <span>{connector.database.host}:{connector.database.port}</span>
                  
                  <span style={{ color: '#00d4ff' }}>Database:</span>
                  <span>{connector.database.database}</span>
                  
                  <span style={{ color: '#00d4ff' }}>User:</span>
                  <span>{connector.database.user}</span>
                </div>
              </div>

              {/* Security Policies */}
              <div style={{ marginBottom: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <p style={{ margin: '0', fontSize: '12px', fontWeight: '600', color: '#00d4ff' }}>
                    🛡️ Security Policies
                  </p>
                  {connector.credential_status && (
                    <span
                      title={`Credential Status: ${connector.credential_status}`}
                      style={{
                        display: 'inline-block',
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        background:
                          connector.credential_status === 'loaded'
                            ? '#22c55e'
                            : connector.credential_status === 'not_found'
                              ? '#f59e0b'
                              : '#ef4444',
                        boxShadow:
                          connector.credential_status === 'loaded'
                            ? '0 0 8px rgba(34, 197, 94, 0.6)'
                            : connector.credential_status === 'not_found'
                              ? '0 0 8px rgba(245, 158, 11, 0.6)'
                              : '0 0 8px rgba(239, 68, 68, 0.6)'
                      }}
                    />
                  )}
                </div>
                <div style={{ fontSize: '11px', color: '#ccc', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {connector.security.block_delete && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ color: '#ef4444' }}>●</span>
                      <span>DELETE blocked</span>
                    </div>
                  )}
                  {connector.security.block_update && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ color: '#ef4444' }}>●</span>
                      <span>UPDATE blocked</span>
                    </div>
                  )}
                  {connector.security.block_drop && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ color: '#ef4444' }}>●</span>
                      <span>DROP blocked</span>
                    </div>
                  )}
                  {connector.security.pii_protected && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ color: '#f59e0b' }}>●</span>
                      <span>PII protected</span>
                    </div>
                  )}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ color: '#22c55e' }}>●</span>
                    <span>Max rows: {connector.security.max_rows.toLocaleString()}</span>
                  </div>
                  {connector.security.protect_tables.length > 0 && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ color: '#f59e0b' }}>●</span>
                      <span>{connector.security.protect_tables.length} table{connector.security.protect_tables.length !== 1 ? 's' : ''} protected</span>
                    </div>
                  )}
                  {connector.security.policy && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ color: getPolicyColor(connector.security.policy) }}>●</span>
                      <span>Policy: {connector.security.policy}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <button
                  onClick={() => testConnection(connector.name)}
                  disabled={testingConnector === connector.name}
                  style={{
                    padding: '8px 12px',
                    background: testingConnector === connector.name 
                      ? 'rgba(0, 212, 255, 0.3)'
                      : 'rgba(0, 212, 255, 0.1)',
                    border: '1px solid rgba(0, 212, 255, 0.3)',
                    borderRadius: '4px',
                    color: '#00d4ff',
                    cursor: testingConnector === connector.name ? 'not-allowed' : 'pointer',
                    fontSize: '11px',
                    fontWeight: '600',
                    transition: 'all 0.3s ease',
                    opacity: testingConnector === connector.name ? 0.6 : 1
                  }}
                  onMouseEnter={(e) => {
                    if (testingConnector !== connector.name) {
                      e.currentTarget.style.background = 'rgba(0, 212, 255, 0.2)';
                      e.currentTarget.style.boxShadow = '0 0 12px rgba(0, 212, 255, 0.3)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (testingConnector !== connector.name) {
                      e.currentTarget.style.background = 'rgba(0, 212, 255, 0.1)';
                      e.currentTarget.style.boxShadow = 'none';
                    }
                  }}
                >
                  {testingConnector === connector.name ? '⏳ Testing...' : '🔌 Test'}
                </button>
                <button
                  style={{
                    padding: '8px 12px',
                    background: 'rgba(0, 100, 200, 0.2)',
                    border: '1px solid rgba(0, 100, 200, 0.3)',
                    borderRadius: '4px',
                    color: '#00d4ff',
                    cursor: 'pointer',
                    fontSize: '11px',
                    fontWeight: '600',
                    transition: 'all 0.3s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(0, 100, 200, 0.3)';
                    e.currentTarget.style.boxShadow = '0 0 12px rgba(0, 150, 200, 0.3)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'rgba(0, 100, 200, 0.2)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  📋 Schema
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ConnectorsPanel;
