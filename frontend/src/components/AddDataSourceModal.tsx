import { useState } from 'react';
import DataSourceSelector, { PlatformOption } from './DataSourceSelector';
import SnowflakeConnectionSetup from './SnowflakeConnectionSetup';

export interface AddDataSourceModalProps {
  workspace_id: number;
  onComplete?: (datasourceId: number) => void;
  onClose?: () => void;
}

type FlowStep = 'platform-select' | 'connection-setup' | 'success';

/**
 * AddDataSourceModal
 *
 * Orchestrates the multi-step flow for adding a new data source:
 * 1. User selects platform
 * 2. User enters connection credentials
 * 3. Connection saved and success shown
 */
export default function AddDataSourceModal({ workspace_id, onComplete, onClose }: AddDataSourceModalProps) {
  const [step, setStep] = useState<FlowStep>('platform-select');
  const [selectedPlatform, setSelectedPlatform] = useState<PlatformOption | null>(null);
  const [datasourceName, setDatasourceName] = useState('');
  const [creatingDatasource, setCreatingDatasource] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newDatasourceId, setNewDatasourceId] = useState<number | null>(null);

  const handleSelectPlatform = (platform: PlatformOption) => {
    setSelectedPlatform(platform);
    setError(null);
    // For now, only Snowflake has a dedicated setup form
    // Other platforms would have similar components
    if (platform.code === 'snowflake') {
      setStep('connection-setup');
    }
  };

  const handleConnect = async (credentials: Record<string, string>) => {
    if (!selectedPlatform || !datasourceName.trim()) {
      setError('Datasource name is required');
      return;
    }

    setCreatingDatasource(true);
    setError(null);

    try {
      const res = await fetch(`/api/v1/datasources?workspace_id=${workspace_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          platform: selectedPlatform.code,
          name: datasourceName.trim(),
          credentials,
        }),
      });

      if (!res.ok) {
        const body = (await res.json().catch(() => ({}))) as { detail?: string };
        throw new Error(body.detail || 'Failed to create datasource');
      }

      const data = (await res.json()) as { id: number };
      setNewDatasourceId(data.id);
      setStep('success');

      // Auto-close after 3 seconds
      setTimeout(() => {
        if (onComplete) onComplete(data.id);
        if (onClose) onClose();
      }, 3000);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Network error');
    } finally {
      setCreatingDatasource(false);
    }
  };

  // Render modals backdrop and content
  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.6)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 100,
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: 'var(--platform-card-bg)',
          borderRadius: 16,
          border: '1px solid var(--platform-border)',
          maxWidth: '900px',
          maxHeight: '90vh',
          overflow: 'auto',
          boxShadow: '0 20px 60px rgba(0,0,0,0.4)',
        }}
        onClick={e => e.stopPropagation()}
      >
        {step === 'platform-select' && (
          <>
            <div style={{ borderBottom: '1px solid var(--platform-border)', padding: '16px 24px' }}>
              <h1 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: '#fff' }}>
                Add Data Source
              </h1>
            </div>
            <DataSourceSelector
              onSelect={handleSelectPlatform}
              onCancel={onClose}
            />
          </>
        )}

        {step === 'connection-setup' && selectedPlatform && (
          <>
            <div style={{ borderBottom: '1px solid var(--platform-border)', padding: '16px 24px' }}>
              <h1 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: '#fff' }}>
                {selectedPlatform.name} Connection
              </h1>
            </div>
            <div style={{ padding: '24px' }}>
              <div style={{ marginBottom: 20 }}>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, marginBottom: 6, color: '#e2e8f0' }}>
                  Datasource Name <span style={{ color: '#ff5050' }}>*</span>
                </label>
                <input
                  type="text"
                  value={datasourceName}
                  onChange={e => setDatasourceName(e.target.value)}
                  placeholder="e.g., Production Analytics, Warehouse Dev"
                  style={{
                    width: '100%',
                    maxWidth: '400px',
                    background: 'rgba(255,255,255,0.07)',
                    border: '1px solid var(--platform-border)',
                    borderRadius: 8,
                    color: '#fff',
                    padding: '10px 14px',
                    fontSize: 13,
                    boxSizing: 'border-box',
                    outline: 'none',
                  }}
                />
              </div>

              {selectedPlatform.code === 'snowflake' && (
                <SnowflakeConnectionSetup
                  onConnect={handleConnect}
                  onCancel={() => setStep('platform-select')}
                />
              )}

              {error && (
                <div
                  style={{
                    background: 'rgba(255,80,80,0.1)',
                    border: '1px solid rgba(255,80,80,0.3)',
                    borderRadius: 8,
                    padding: '10px 14px',
                    color: '#ff5050',
                    fontSize: 12,
                    marginTop: 16,
                  }}
                >
                  {error}
                </div>
              )}
            </div>
          </>
        )}

        {step === 'success' && newDatasourceId && (
          <div style={{ padding: '60px 32px', textAlign: 'center' }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>✓</div>
            <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: '#22c55e', marginBottom: 8 }}>
              Connection Created
            </h2>
            <p style={{ margin: '0 0 24px 0', color: 'var(--platform-muted)', fontSize: 13 }}>
              "{datasourceName}" has been connected successfully.
            </p>
            <p style={{ margin: 0, color: 'var(--platform-muted)', fontSize: 12 }}>
              Closing in 3 seconds…
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
