import React, { useState } from 'react';
import './PoliciesManager.css';

interface Policy {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  category: string;
  rules: string[];
  lastModified: string;
}

export const PoliciesManager: React.FC = () => {
  const mockPolicies: Policy[] = [
    {
      id: '1',
      name: 'Row-Level Security',
      description: 'Restrict data access based on user roles and attributes',
      enabled: true,
      category: 'Access Control',
      rules: [
        'Users can only access rows where department matches their assigned department',
        'Managers can access all rows in their department',
        'Admins have unrestricted access',
      ],
      lastModified: '2024-02-28 10:30:00',
    },
    {
      id: '2',
      name: 'Data Masking',
      description: 'Automatically mask sensitive data in query results',
      enabled: true,
      category: 'Data Protection',
      rules: [
        'Social Security Numbers are masked as XXX-XX-XXXX',
        'Credit card numbers are masked as XXXX-XXXX-XXXX-****',
        'Email addresses show only domain for non-admins',
      ],
      lastModified: '2024-02-27 14:15:00',
    },
    {
      id: '3',
      name: 'Query Rewriting',
      description: 'Automatically rewrite queries to comply with policies',
      enabled: true,
      category: 'Query Governance',
      rules: [
        'Add WHERE clauses to enforce row-level security',
        'Remove SELECT * and replace with explicit column lists',
        'Add LIMIT clauses to prevent large data exports',
      ],
      lastModified: '2024-02-26 09:45:00',
    },
    {
      id: '4',
      name: 'Audit Logging',
      description: 'Log all database access and modifications',
      enabled: true,
      category: 'Compliance',
      rules: [
        'Log all SELECT queries with user and timestamp',
        'Log all INSERT, UPDATE, DELETE operations',
        'Retain logs for minimum 90 days',
      ],
      lastModified: '2024-02-25 16:20:00',
    },
    {
      id: '5',
      name: 'Schema Protection',
      description: 'Prevent unauthorized schema modifications',
      enabled: false,
      category: 'Data Integrity',
      rules: [
        'Block ALTER TABLE commands from non-admin users',
        'Block DROP TABLE commands from all users',
        'Require approval for schema changes',
      ],
      lastModified: '2024-02-24 11:00:00',
    },
    {
      id: '6',
      name: 'Performance Limits',
      description: 'Enforce query performance and resource limits',
      enabled: true,
      category: 'Performance',
      rules: [
        'Maximum query execution time: 5 minutes',
        'Maximum result set size: 1 million rows',
        'Maximum concurrent queries per user: 5',
      ],
      lastModified: '2024-02-23 13:30:00',
    },
  ];

  const [policies, setPolicies] = useState<Policy[]>(mockPolicies);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const togglePolicy = (id: string) => {
    setPolicies(policies.map(p => 
      p.id === id ? { ...p, enabled: !p.enabled } : p
    ));
  };

  const enabledCount = policies.filter(p => p.enabled).length;
  const categories = [...new Set(policies.map(p => p.category))];

  return (
    <div className="policies-manager">
      <div className="policies-header">
        <h1>Governance Policies</h1>
        <p className="policies-subtitle">Configure and manage data governance policies</p>
      </div>

      <div className="policies-stats">
        <div className="stat-card">
          <div className="stat-label">Total Policies</div>
          <div className="stat-value">{policies.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Enabled</div>
          <div className="stat-value">{enabledCount}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Disabled</div>
          <div className="stat-value">{policies.length - enabledCount}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Categories</div>
          <div className="stat-value">{categories.length}</div>
        </div>
      </div>

      <div className="policies-list">
        {policies.map((policy) => (
          <div key={policy.id} className={`policy-card ${policy.enabled ? 'enabled' : 'disabled'}`}>
            <div className="policy-header">
              <div className="policy-left">
                <div className="policy-toggle">
                  <input
                    type="checkbox"
                    checked={policy.enabled}
                    onChange={() => togglePolicy(policy.id)}
                    id={`toggle-${policy.id}`}
                  />
                  <label htmlFor={`toggle-${policy.id}`}></label>
                </div>
                <div className="policy-info">
                  <div className="policy-name">{policy.name}</div>
                  <div className="policy-description">{policy.description}</div>
                  <div className="policy-meta">
                    <span className="meta-category">📁 {policy.category}</span>
                    <span className="meta-modified">📅 {policy.lastModified}</span>
                  </div>
                </div>
              </div>
              <button 
                className="expand-btn"
                onClick={() => toggleExpand(policy.id)}
              >
                {expandedId === policy.id ? '▼' : '▶'}
              </button>
            </div>

            {expandedId === policy.id && (
              <div className="policy-details">
                <div className="rules-section">
                  <h4>Policy Rules:</h4>
                  <ul className="rules-list">
                    {policy.rules.map((rule, idx) => (
                      <li key={idx}>
                        <span className="rule-bullet">•</span>
                        {rule}
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="policy-actions">
                  <button className="action-btn edit">✏️ Edit</button>
                  <button className="action-btn duplicate">📋 Duplicate</button>
                  <button className="action-btn delete">🗑️ Delete</button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="policies-footer">
        <button className="btn-primary">+ Create New Policy</button>
      </div>
    </div>
  );
};
