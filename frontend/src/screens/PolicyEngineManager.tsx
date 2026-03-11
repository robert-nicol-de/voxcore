import React, { useEffect, useState } from 'react';
import { Card, Button, Input, Badge } from '../components';
import './PolicyEngineManager.css';
import { apiUrl } from '../lib/api';

interface PolicyConfig {
  risk_thresholds: {
    safe_max: number;
    warning_max: number;
    danger_min: number;
  };
  allowed_operations: Record<string, boolean>;
  schema_whitelist: string[];
  masking_rules: Array<{ pattern: string; strategy: string; enabled: boolean }>;
  query_limits: {
    max_per_hour: number;
    max_result_rows: number;
    max_execution_seconds: number;
  };
  approval_workflows: {
    require_approval_for_high_risk: boolean;
    high_risk_threshold: number;
    approval_chain: string[];
    auto_approve_timeout_minutes: number;
  };
}

export const PolicyEngineManager: React.FC = () => {
  const [config, setConfig] = useState<PolicyConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await fetch(apiUrl('/api/governance/policies/config'));
        if (!response.ok) throw new Error('Failed to fetch policy config');
        const data = await response.json();
        setConfig(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchConfig();
  }, []);

  const handleSaveConfig = async () => {
    if (!config) return;
    setSaving(true);
    try {
      const response = await fetch(apiUrl('/api/governance/policies/update'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      if (!response.ok) throw new Error('Failed to save policy config');
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setSaving(false);
    }
  };

  const handleOperationToggle = (operation: string) => {
    if (!config) return;
    setConfig({
      ...config,
      allowed_operations: {
        ...config.allowed_operations,
        [operation]: !config.allowed_operations[operation],
      },
    });
  };

  if (loading) return <div className="manager-loading">Loading policy configuration...</div>;
  if (error) return <div className="manager-error">Error: {error}</div>;
  if (!config) return <div className="manager-error">No configuration available</div>;

  return (
    <div className="policy-engine-manager">
      <h1>Policy Engine Manager</h1>

      {saveSuccess && (
        <div className="save-success">
          <Badge variant="safe">✓ Configuration saved successfully</Badge>
        </div>
      )}

      {/* Risk Thresholds */}
      <Card elevation="md">
        <h2>Risk Thresholds</h2>
        <div className="policy-section">
          <div className="policy-item">
            <label>Safe Maximum Score</label>
            <Input
              value={config.risk_thresholds.safe_max.toString()}
              onChange={(val) =>
                setConfig({
                  ...config,
                  risk_thresholds: {
                    ...config.risk_thresholds,
                    safe_max: parseInt(val),
                  },
                })
              }
              type="number"
            />
            <span className="policy-hint">Queries with score ≤ {config.risk_thresholds.safe_max} are Safe</span>
          </div>

          <div className="policy-item">
            <label>Warning Maximum Score</label>
            <Input
              value={config.risk_thresholds.warning_max.toString()}
              onChange={(val) =>
                setConfig({
                  ...config,
                  risk_thresholds: {
                    ...config.risk_thresholds,
                    warning_max: parseInt(val),
                  },
                })
              }
              type="number"
            />
            <span className="policy-hint">Queries with score {config.risk_thresholds.safe_max + 1}-{config.risk_thresholds.warning_max} are Warning</span>
          </div>

          <div className="policy-item">
            <label>Danger Minimum Score</label>
            <Input
              value={config.risk_thresholds.danger_min.toString()}
              onChange={(val) =>
                setConfig({
                  ...config,
                  risk_thresholds: {
                    ...config.risk_thresholds,
                    danger_min: parseInt(val),
                  },
                })
              }
              type="number"
            />
            <span className="policy-hint">Queries with score ≥ {config.risk_thresholds.danger_min} are Danger</span>
          </div>
        </div>
      </Card>

      {/* Allowed Operations */}
      <Card elevation="md">
        <h2>Allowed Operations</h2>
        <div className="operations-grid">
          {Object.entries(config.allowed_operations).map(([operation, allowed]) => (
            <div key={operation} className="operation-toggle">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={allowed}
                  onChange={() => handleOperationToggle(operation)}
                  className="toggle-input"
                />
                <span className="toggle-text">{operation}</span>
              </label>
              <Badge variant={allowed ? 'safe' : 'danger'}>
                {allowed ? 'Allowed' : 'Blocked'}
              </Badge>
            </div>
          ))}
        </div>
      </Card>

      {/* Schema Whitelist */}
      <Card elevation="md">
        <h2>Schema Whitelist</h2>
        <div className="schema-list">
          {config.schema_whitelist.map((table) => (
            <div key={table} className="schema-item">
              <Badge variant="info">{table}</Badge>
            </div>
          ))}
        </div>
        <p className="policy-hint">Only whitelisted tables can be queried</p>
      </Card>

      {/* Masking Rules */}
      <Card elevation="md">
        <h2>Masking Rules</h2>
        <div className="masking-rules">
          {config.masking_rules.map((rule) => (
            <div key={rule.pattern} className="masking-item">
              <div className="masking-pattern">{rule.pattern}</div>
              <div className="masking-strategy">
                <Badge variant="warning">{rule.strategy}</Badge>
              </div>
              <div className="masking-status">
                <Badge variant={rule.enabled ? 'safe' : 'danger'}>
                  {rule.enabled ? 'Enabled' : 'Disabled'}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Query Limits */}
      <Card elevation="md">
        <h2>Query Limits</h2>
        <div className="policy-section">
          <div className="policy-item">
            <label>Max Queries Per Hour</label>
            <Input
              value={config.query_limits.max_per_hour.toString()}
              onChange={(val) =>
                setConfig({
                  ...config,
                  query_limits: {
                    ...config.query_limits,
                    max_per_hour: parseInt(val),
                  },
                })
              }
              type="number"
            />
          </div>

          <div className="policy-item">
            <label>Max Result Rows</label>
            <Input
              value={config.query_limits.max_result_rows.toString()}
              onChange={(val) =>
                setConfig({
                  ...config,
                  query_limits: {
                    ...config.query_limits,
                    max_result_rows: parseInt(val),
                  },
                })
              }
              type="number"
            />
          </div>

          <div className="policy-item">
            <label>Max Execution Time (seconds)</label>
            <Input
              value={config.query_limits.max_execution_seconds.toString()}
              onChange={(val) =>
                setConfig({
                  ...config,
                  query_limits: {
                    ...config.query_limits,
                    max_execution_seconds: parseInt(val),
                  },
                })
              }
              type="number"
            />
          </div>
        </div>
      </Card>

      {/* Approval Workflows */}
      <Card elevation="md">
        <h2>Approval Workflows</h2>
        <div className="policy-section">
          <div className="policy-item">
            <label className="toggle-label">
              <input
                type="checkbox"
                checked={config.approval_workflows.require_approval_for_high_risk}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    approval_workflows: {
                      ...config.approval_workflows,
                      require_approval_for_high_risk: e.target.checked,
                    },
                  })
                }
                className="toggle-input"
              />
              <span className="toggle-text">Require Approval for High-Risk Queries</span>
            </label>
          </div>

          <div className="policy-item">
            <label>High-Risk Threshold</label>
            <Input
              value={config.approval_workflows.high_risk_threshold.toString()}
              onChange={(val) =>
                setConfig({
                  ...config,
                  approval_workflows: {
                    ...config.approval_workflows,
                    high_risk_threshold: parseInt(val),
                  },
                })
              }
              type="number"
            />
          </div>

          <div className="policy-item">
            <label>Auto-Approve Timeout (minutes)</label>
            <Input
              value={config.approval_workflows.auto_approve_timeout_minutes.toString()}
              onChange={(val) =>
                setConfig({
                  ...config,
                  approval_workflows: {
                    ...config.approval_workflows,
                    auto_approve_timeout_minutes: parseInt(val),
                  },
                })
              }
              type="number"
            />
          </div>
        </div>
      </Card>

      {/* Save Button */}
      <div className="manager-actions">
        <Button
          variant="primary"
          onClick={handleSaveConfig}
          state={saving ? 'loading' : 'default'}
        >
          {saving ? 'Saving...' : 'Save Configuration'}
        </Button>
      </div>
    </div>
  );
};
