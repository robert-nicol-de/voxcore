import React, { useEffect, useMemo, useState } from 'react';
import './PoliciesManager.css';
import { apiUrl, isApiNotFound } from '../lib/api';

interface CompanyPolicies {
  block_destructive_queries: {
    enabled: boolean;
    blocked_keywords: string[];
  };
  protect_sensitive_columns: {
    enabled: boolean;
    blocked_columns: string[];
  };
  read_only_ai_mode: {
    enabled: boolean;
    allowed_statements: string[];
  };
  query_result_limits: {
    enabled: boolean;
    max_rows: number;
  };
}

interface QueryTestResult {
  allowed: boolean;
  message: string;
  blocked: boolean;
  reasons: string[];
  original_query: string;
  rewritten_query: string;
}

const DEFAULT_POLICIES: CompanyPolicies = {
  block_destructive_queries: {
    enabled: true,
    blocked_keywords: ['drop', 'truncate', 'alter', 'delete'],
  },
  protect_sensitive_columns: {
    enabled: true,
    blocked_columns: ['password', 'ssn', 'social_security_number', 'credit_card', 'credit_card_number', 'salary', 'private_key', 'api_key', 'secret_key', 'access_token', 'refresh_token', 'bank_account', 'routing_number', 'email'],
  },
  read_only_ai_mode: {
    enabled: false,
    allowed_statements: ['select', 'with'],
  },
  query_result_limits: {
    enabled: false,
    max_rows: 1000,
  },
};

const normalizeCsv = (value: string): string[] =>
  value
    .split(',')
    .map((item) => item.trim().toLowerCase())
    .filter(Boolean);

const getCompanyId = async (): Promise<string> => {
  const cached = localStorage.getItem('voxcore_company_id');
  if (cached) {
    return cached;
  }

  const token = localStorage.getItem('voxcore_token');
  if (!token) {
    return 'default';
  }

  try {
    const response = await fetch(apiUrl('/api/v1/auth/me'), {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.ok) {
      const profile = await response.json();
      const companyId = String(profile.company_id ?? 'default');
      localStorage.setItem('voxcore_company_id', companyId);
      return companyId;
    }
  } catch (error) {
    console.warn('Failed to resolve company id for policy manager', error);
  }

  return 'default';
};

export const PoliciesManager: React.FC = () => {
  const [companyId, setCompanyId] = useState<string>('default');
  const [policies, setPolicies] = useState<CompanyPolicies>(DEFAULT_POLICIES);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [message, setMessage] = useState<string>('');

  const [testQuery, setTestQuery] = useState<string>('SELECT * FROM customers');
  const [testingQuery, setTestingQuery] = useState<boolean>(false);
  const [testResult, setTestResult] = useState<QueryTestResult | null>(null);

  const enabledCount = useMemo(() => {
    return [
      policies.block_destructive_queries.enabled,
      policies.protect_sensitive_columns.enabled,
      policies.read_only_ai_mode.enabled,
      policies.query_result_limits.enabled,
    ].filter(Boolean).length;
  }, [policies]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError('');
      setMessage('');

      const resolvedCompanyId = await getCompanyId();
      setCompanyId(resolvedCompanyId);

      try {
        const response = await fetch(apiUrl(`/api/v1/policies/${resolvedCompanyId}`));
        if (isApiNotFound(response)) {
          setPolicies(DEFAULT_POLICIES);
          return;
        }
        if (!response.ok) {
          throw new Error('Failed to load policy configuration');
        }
        const data = await response.json();
        setPolicies(data.policies || DEFAULT_POLICIES);
      } catch (err: any) {
        setError(err?.message || 'Failed to load policies');
        setPolicies(DEFAULT_POLICIES);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const updatePolicyState = <K extends keyof CompanyPolicies>(key: K, patch: Partial<CompanyPolicies[K]>) => {
    setPolicies((prev) => ({
      ...prev,
      [key]: {
        ...prev[key],
        ...patch,
      },
    }));
  };

  const savePolicies = async () => {
    setSaving(true);
    setError('');
    setMessage('');
    try {
      const response = await fetch(apiUrl(`/api/v1/policies/${companyId}`), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ policies }),
      });
      if (isApiNotFound(response)) {
        setMessage('Policy service is unavailable in this deployment.');
        return;
      }
      if (!response.ok) {
        throw new Error('Failed to save policies');
      }
      setMessage('Policies saved successfully');
    } catch (err: any) {
      setError(err?.message || 'Failed to save policies');
    } finally {
      setSaving(false);
    }
  };

  const runPolicyTest = async () => {
    if (!testQuery.trim()) return;
    setTestingQuery(true);
    setError('');
    setTestResult(null);
    try {
      const response = await fetch(apiUrl(`/api/v1/policies/${companyId}/test-query`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: testQuery }),
      });
      if (isApiNotFound(response)) {
        setMessage('Policy test is unavailable in this deployment.');
        return;
      }
      if (!response.ok) {
        throw new Error('Policy test request failed');
      }
      const data = await response.json();
      setTestResult(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to test query');
    } finally {
      setTestingQuery(false);
    }
  };

  if (loading) {
    return <div className="policies-manager">Loading policy configuration...</div>;
  }

  return (
    <div className="policies-manager">
      <div className="policies-header">
        <h1>AI Security Policies</h1>
        <p className="policies-subtitle">
          Control how AI interacts with your data for company {companyId}
        </p>
      </div>

      <div className="policies-stats">
        <div className="stat-card">
          <div className="stat-label">Total Policies</div>
          <div className="stat-value">4</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Enabled</div>
          <div className="stat-value">{enabledCount}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Disabled</div>
          <div className="stat-value">{4 - enabledCount}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Mode</div>
          <div className="stat-value">Firewall</div>
        </div>
      </div>

      {error && <div className="policy-banner error">{error}</div>}
      {message && <div className="policy-banner success">{message}</div>}

      <div className="policies-list">
        <div className={`policy-card ${policies.block_destructive_queries.enabled ? 'enabled' : 'disabled'}`}>
          <div className="policy-header">
            <div className="policy-left">
              <div className="policy-toggle">
                <input
                  type="checkbox"
                  checked={policies.block_destructive_queries.enabled}
                  onChange={(e) => updatePolicyState('block_destructive_queries', { enabled: e.target.checked })}
                  id="toggle-destructive"
                />
                <label htmlFor="toggle-destructive"></label>
              </div>
              <div className="policy-info">
                <div className="policy-name">Block Destructive Queries</div>
                <div className="policy-description">Blocks DROP, TRUNCATE, ALTER, DELETE or custom keywords</div>
              </div>
            </div>
          </div>
          <div className="policy-details open">
            <div className="rules-section">
              <h4>Blocked Keywords (comma separated)</h4>
              <input
                className="policy-input"
                value={policies.block_destructive_queries.blocked_keywords.join(', ')}
                onChange={(e) =>
                  updatePolicyState('block_destructive_queries', {
                    blocked_keywords: normalizeCsv(e.target.value),
                  })
                }
                placeholder="drop, truncate, alter, delete"
              />
            </div>
          </div>
        </div>

        <div className={`policy-card ${policies.protect_sensitive_columns.enabled ? 'enabled' : 'disabled'}`}>
          <div className="policy-header">
            <div className="policy-left">
              <div className="policy-toggle">
                <input
                  type="checkbox"
                  checked={policies.protect_sensitive_columns.enabled}
                  onChange={(e) => updatePolicyState('protect_sensitive_columns', { enabled: e.target.checked })}
                  id="toggle-sensitive"
                />
                <label htmlFor="toggle-sensitive"></label>
              </div>
              <div className="policy-info">
                <div className="policy-name">Protect Sensitive Columns</div>
                <div className="policy-description">Blocks AI access to protected columns like ssn and credit card</div>
              </div>
            </div>
          </div>
          <div className="policy-details open">
            <div className="rules-section">
              <h4>Blocked Columns (comma separated)</h4>
              <input
                className="policy-input"
                value={policies.protect_sensitive_columns.blocked_columns.join(', ')}
                onChange={(e) =>
                  updatePolicyState('protect_sensitive_columns', {
                    blocked_columns: normalizeCsv(e.target.value),
                  })
                }
                placeholder="ssn, credit_card, password"
              />
            </div>
          </div>
        </div>

        <div className={`policy-card ${policies.read_only_ai_mode.enabled ? 'enabled' : 'disabled'}`}>
          <div className="policy-header">
            <div className="policy-left">
              <div className="policy-toggle">
                <input
                  type="checkbox"
                  checked={policies.read_only_ai_mode.enabled}
                  onChange={(e) => updatePolicyState('read_only_ai_mode', { enabled: e.target.checked })}
                  id="toggle-readonly"
                />
                <label htmlFor="toggle-readonly"></label>
              </div>
              <div className="policy-info">
                <div className="policy-name">Read-Only AI Mode</div>
                <div className="policy-description">Allows only statement types you explicitly whitelist</div>
              </div>
            </div>
          </div>
          <div className="policy-details open">
            <div className="rules-section">
              <h4>Allowed Statements (comma separated)</h4>
              <input
                className="policy-input"
                value={policies.read_only_ai_mode.allowed_statements.join(', ')}
                onChange={(e) =>
                  updatePolicyState('read_only_ai_mode', {
                    allowed_statements: normalizeCsv(e.target.value),
                  })
                }
                placeholder="select, with"
              />
            </div>
          </div>
        </div>

        <div className={`policy-card ${policies.query_result_limits.enabled ? 'enabled' : 'disabled'}`}>
          <div className="policy-header">
            <div className="policy-left">
              <div className="policy-toggle">
                <input
                  type="checkbox"
                  checked={policies.query_result_limits.enabled}
                  onChange={(e) => updatePolicyState('query_result_limits', { enabled: e.target.checked })}
                  id="toggle-limit"
                />
                <label htmlFor="toggle-limit"></label>
              </div>
              <div className="policy-info">
                <div className="policy-name">Query Result Limit</div>
                <div className="policy-description">Automatically appends LIMIT to eligible SELECT queries</div>
              </div>
            </div>
          </div>
          <div className="policy-details open">
            <div className="rules-section">
              <h4>Maximum Rows</h4>
              <input
                className="policy-input"
                type="number"
                min={1}
                max={1000000}
                value={policies.query_result_limits.max_rows}
                onChange={(e) =>
                  updatePolicyState('query_result_limits', {
                    max_rows: Math.max(1, Number(e.target.value || '1')),
                  })
                }
              />
            </div>
          </div>
        </div>
      </div>

      <div className="policy-tester">
        <h3>Test Query Against Policy</h3>
        <textarea
          className="policy-textarea"
          value={testQuery}
          onChange={(e) => setTestQuery(e.target.value)}
          rows={5}
          placeholder="SELECT * FROM transactions"
        />
        <div className="policy-actions">
          <button className="action-btn edit" onClick={runPolicyTest} disabled={testingQuery}>
            {testingQuery ? 'Testing...' : 'Run Policy Test'}
          </button>
        </div>

        {testResult && (
          <div className={`test-result ${testResult.allowed ? 'allowed' : 'blocked'}`}>
            <div className="test-title">{testResult.message}</div>
            {!testResult.allowed && testResult.reasons?.length > 0 && (
              <ul className="rules-list">
                {testResult.reasons.map((reason, idx) => (
                  <li key={idx}>{reason}</li>
                ))}
              </ul>
            )}
            {testResult.rewritten_query && testResult.rewritten_query !== testResult.original_query && (
              <div className="rewritten-query">
                Rewritten query: {testResult.rewritten_query}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="policies-footer">
        <button className="btn-primary" onClick={savePolicies} disabled={saving}>
          {saving ? 'Saving...' : 'Save Policies'}
        </button>
      </div>
    </div>
  );
};
