import { useState, useEffect } from 'react';

interface ZeroTrustPolicy {
  mode: string;
  allow_tables: string;
  deny_tables: string;
  pii_protected_columns: string;
  max_rows: number;
  block_delete: boolean;
  block_drop: boolean;
  block_update: boolean;
  require_query_token: boolean;
  allowed_ai_applications: string;
  allowed_user_roles: string;
}

export default function ZeroTrustPolicy() {
  const [tenant, setTenant] = useState<string>('tenant_acme_corp');
  const [policies, setPolicies] = useState<ZeroTrustPolicy | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchPolicy = async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/v1/tenants/${tenant}/config`, {
          headers: { 'X-Tenant-ID': tenant }
        });
        if (response.ok) {
          const data = await response.json();
          if (data.policies && data.policies.zero_trust) {
            setPolicies(data.policies.zero_trust);
          }
        }
      } catch (error) {
        console.error('Failed to fetch policy:', error);
      } finally {
        setLoading(false);
      }
    };

    if (tenant) {
      fetchPolicy();
    }
  }, [tenant]);

  const parseList = (str: string): string[] => {
    return str ? str.split(',').map(s => s.trim()).filter(Boolean) : [];
  };

  return (
    <div className="zero-trust-policy">
      <div className="policy-header">
        <h2>🔐 Zero-Trust AI Security Policy</h2>
        <p>Enforce mandatory security rules for all AI queries</p>
      </div>

      <div className="policy-selector">
        <label>Tenant:</label>
        <select value={tenant} onChange={(e) => setTenant(e.target.value)}>
          <option value="tenant_acme_corp">Acme Corp (Enterprise)</option>
          <option value="tenant_techstartup_inc">TechStartup Inc (Pro)</option>
          <option value="tenant_enterprise_solutions">Enterprise Solutions (Enterprise)</option>
        </select>
      </div>

      {loading ? (
        <div className="loading">Loading policy...</div>
      ) : policies ? (
        <>
          {/* Mode */}
          <div className="policy-section">
            <div className="section-title">🎯 Zero-Trust Mode</div>
            <div className="policy-stat">
              <span className="stat-label">Status</span>
              <span className="stat-value" style={{ color: policies.mode === 'enabled' ? '#22c55e' : '#ef4444' }}>
                {policies.mode === 'enabled' ? '✓ ENABLED' : '✗ DISABLED'}
              </span>
            </div>
          </div>

          {/* Table Access Control */}
          <div className="policy-section">
            <div className="section-title">📋 Table Access Control</div>
            
            <div className="policy-list">
              <div className="list-header">✓ Allowed Tables (Whitelist)</div>
              <div className="table-list">
                {parseList(policies.allow_tables).map((table, idx) => (
                  <span key={idx} className="table-tag allowed">{table}</span>
                ))}
              </div>
            </div>

            <div className="policy-list">
              <div className="list-header">✗ Denied Tables (Blacklist)</div>
              <div className="table-list">
                {parseList(policies.deny_tables).map((table, idx) => (
                  <span key={idx} className="table-tag denied">{table}</span>
                ))}
              </div>
            </div>
          </div>

          {/* Column Security */}
          <div className="policy-section">
            <div className="section-title">🔑 PII Protected Columns</div>
            <div className="policy-list">
              <div className="table-list">
                {parseList(policies.pii_protected_columns).map((col, idx) => (
                  <span key={idx} className="column-tag pii">{col}</span>
                ))}
              </div>
            </div>
          </div>

          {/* Operation Control */}
          <div className="policy-section">
            <div className="section-title">⚠️ Blocked Operations</div>
            <div className="operation-grid">
              <div className={`operation ${policies.block_delete ? 'blocked' : 'allowed'}`}>
                <div className="op-icon">🗑️</div>
                <div className="op-name">DELETE</div>
                <div className="op-status">{policies.block_delete ? 'BLOCKED' : 'ALLOWED'}</div>
              </div>
              <div className={`operation ${policies.block_drop ? 'blocked' : 'allowed'}`}>
                <div className="op-icon">💥</div>
                <div className="op-name">DROP</div>
                <div className="op-status">{policies.block_drop ? 'BLOCKED' : 'ALLOWED'}</div>
              </div>
              <div className={`operation ${policies.block_update ? 'blocked' : 'allowed'}`}>
                <div className="op-icon">✏️</div>
                <div className="op-name">UPDATE</div>
                <div className="op-status">{policies.block_update ? 'BLOCKED' : 'ALLOWED'}</div>
              </div>
            </div>
          </div>

          {/* Query Limits */}
          <div className="policy-section">
            <div className="section-title">📊 Query Limits</div>
            <div className="policy-stat">
              <span className="stat-label">Max Rows Per Query</span>
              <span className="stat-value">{policies.max_rows.toLocaleString()}</span>
            </div>
          </div>

          {/* Authentication */}
          <div className="policy-section">
            <div className="section-title">🔑 Authentication Requirements</div>
            <div className="policy-stat">
              <span className="stat-label">Require Query Token</span>
              <span className="stat-value" style={{ color: policies.require_query_token ? '#ef4444' : '#22c55e' }}>
                {policies.require_query_token ? '✓ REQUIRED' : '✗ OPTIONAL'}
              </span>
            </div>
          </div>

          {/* Application Allowlist */}
          <div className="policy-section">
            <div className="section-title">🤖 Allowed AI Applications</div>
            <div className="app-list">
              {parseList(policies.allowed_ai_applications).map((app, idx) => (
                <span key={idx} className="app-tag">{app}</span>
              ))}
            </div>
          </div>

          {/* Role Allowlist */}
          <div className="policy-section">
            <div className="section-title">👤 Allowed User Roles</div>
            <div className="role-list">
              {parseList(policies.allowed_user_roles).map((role, idx) => (
                <span key={idx} className={`role-tag role-${role}`}>{role}</span>
              ))}
            </div>
          </div>

          {/* Policy Summary */}
          <div className="policy-summary">
            <div className="summary-header">📋 Policy Summary</div>
            <div className="summary-stats">
              <div className="stat">
                <span className="stat-name">Allowed Tables</span>
                <span className="stat-count">{parseList(policies.allow_tables).length}</span>
              </div>
              <div className="stat">
                <span className="stat-name">Denied Tables</span>
                <span className="stat-count">{parseList(policies.deny_tables).length}</span>
              </div>
              <div className="stat">
                <span className="stat-name">Protected Columns</span>
                <span className="stat-count">{parseList(policies.pii_protected_columns).length}</span>
              </div>
              <div className="stat">
                <span className="stat-name">Risk Level</span>
                <span className="stat-count" style={{ color: calculateRiskColor(policies) }}>
                  {calculateRiskLevel(policies)}
                </span>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="error">No zero-trust policy configured for this tenant</div>
      )}
    </div>
  );
}

function calculateRiskLevel(policy: ZeroTrustPolicy): string {
  let riskScore = 0;
  
  // More restrictions = lower risk
  if (policy.block_delete) riskScore += 1;
  if (policy.block_drop) riskScore += 1;
  if (policy.block_update) riskScore += 1;
  if (policy.require_query_token) riskScore += 2;
  
  // Active protections = lower risk
  if (policy.allow_tables) riskScore += 2;
  if (policy.pii_protected_columns) riskScore += 1;
  
  if (riskScore >= 6) return '🟢 LOW';
  if (riskScore >= 3) return '🟡 MEDIUM';
  return '🔴 HIGH';
}

function calculateRiskColor(policy: ZeroTrustPolicy): string {
  let riskScore = 0;
  
  if (policy.block_delete) riskScore += 1;
  if (policy.block_drop) riskScore += 1;
  if (policy.block_update) riskScore += 1;
  if (policy.require_query_token) riskScore += 2;
  if (policy.allow_tables) riskScore += 2;
  if (policy.pii_protected_columns) riskScore += 1;
  
  if (riskScore >= 6) return '#22c55e';
  if (riskScore >= 3) return '#f59e0b';
  return '#ef4444';
}
