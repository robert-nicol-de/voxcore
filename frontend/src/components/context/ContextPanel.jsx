import React, { useState } from 'react';
import './ContextPanel.css';

/**
 * ContextPanel
 * 
 * Displays structured query context to users.
 * Shows:
 * - User role + permissions
 * - Available tables
 * - Sensitive columns
 * - Active policies
 * - Forbidden operations
 * 
 * Helps users understand what they can/can't do.
 */
const ContextPanel = ({ context, isExpanded = false }) => {
  const [expanded, setExpanded] = useState(isExpanded);

  if (!context) {
    return null;
  }

  const {
    user_role = 'viewer',
    permissions = {},
    schema = {},
    policies = {},
    forbidden_operations = [],
    sensitive_columns = [],
  } = context;

  const availableTables = schema.available_tables || [];
  const activePolicies = policies.active_policies || [];
  const policyConstraints = policies.policy_constraints || [];

  const roleColor = {
    admin: '#3b82f6',    // blue
    analyst: '#f59e0b',  // amber
    viewer: '#ef4444',   // red
  };

  return (
    <div className="context-panel" data-expanded={expanded}>
      {/* Header - Always visible */}
      <div 
        className="context-header"
        onClick={() => setExpanded(!expanded)}
        role="button"
        tabIndex={0}
      >
        <div className="context-header-left">
          <span className="context-toggle-icon">
            {expanded ? '▼' : '▶'}
          </span>
          <span className="context-title">Query Context</span>
        </div>
        
        <div className="context-role-badge" style={{ backgroundColor: roleColor[user_role] }}>
          {user_role.toUpperCase()}
        </div>
      </div>

      {/* Expandable Content */}
      {expanded && (
        <div className="context-content">
          
          {/* User Role & Permissions */}
          <section className="context-section">
            <h3 className="context-section-title">👤 Your Role</h3>
            <div className="context-role-info">
              <p className="role-description">{permissions.role_description}</p>
              
              <ul className="permissions-list">
                <li className={permissions.can_read_sensitive_data ? 'allowed' : 'blocked'}>
                  {permissions.can_read_sensitive_data ? '✓' : '✗'} Read sensitive data
                </li>
                <li className={permissions.can_join_tables ? 'allowed' : 'blocked'}>
                  {permissions.can_join_tables ? '✓' : '✗'} Join multiple tables
                  {permissions.max_joins && ` (max ${permissions.max_joins})`}
                </li>
                <li className={permissions.can_aggregate ? 'allowed' : 'blocked'}>
                  {permissions.can_aggregate ? '✓' : '✗'} Use aggregate functions
                </li>
              </ul>

              {permissions.max_rows_per_query && (
                <div className="context-limit-info">
                  <strong>Row limit per query:</strong> {permissions.max_rows_per_query.toLocaleString()}
                </div>
              )}
            </div>
          </section>

          {/* Available Tables */}
          {availableTables.length > 0 && (
            <section className="context-section">
              <h3 className="context-section-title">📊 Available Tables</h3>
              <div className="context-table-list">
                {availableTables.map((table, idx) => (
                  <span key={idx} className="context-table-badge">
                    {table}
                  </span>
                ))}
              </div>
              <p className="context-section-note">
                You can query these tables in your SQL
              </p>
            </section>
          )}

          {/* Sensitive Columns Warning */}
          {sensitiveColumns && sensitiveColumns.length > 0 && (
            <section className="context-section warning">
              <h3 className="context-section-title">⚠️ Sensitive Columns</h3>
              <p className="context-warning-note">
                {permissions.can_read_sensitive_data
                  ? "You have access to these columns, but they should be handled carefully:"
                  : "These columns will be MASKED in your results:"}
              </p>
              <div className="context-sensitive-list">
                {sensitiveColumns.slice(0, 5).map((col, idx) => (
                  <span key={idx} className="context-sensitive-badge">
                    🔒 {col}
                  </span>
                ))}
                {sensitiveColumns.length > 5 && (
                  <span className="context-count-badge">
                    +{sensitiveColumns.length - 5} more
                  </span>
                )}
              </div>
            </section>
          )}

          {/* Active Policies */}
          {activePolicies && activePolicies.length > 0 && (
            <section className="context-section">
              <h3 className="context-section-title">📋 Active Policies</h3>
              <div className="context-policies-list">
                {activePolicies.map((policy, idx) => (
                  <div key={idx} className="context-policy-item">
                    <div className="policy-header">
                      <strong>{policy.name}</strong>
                      <span className="policy-type">{policy.rule_type}</span>
                    </div>
                    {policy.description && (
                      <p className="policy-description">{policy.description}</p>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Policy Constraints */}
          {policyConstraints && policyConstraints.length > 0 && (
            <section className="context-section">
              <h3 className="context-section-title">⚡ Query Constraints</h3>
              <ul className="context-constraints-list">
                {policyConstraints.map((constraint, idx) => (
                  <li key={idx}>
                    <span className="constraint-icon">→</span>
                    {constraint}
                  </li>
                ))}
              </ul>
            </section>
          )}

          {/* Forbidden Operations */}
          {forbidden_operations && forbidden_operations.length > 0 && (
            <section className="context-section danger">
              <h3 className="context-section-title">🚫 Forbidden Operations</h3>
              <div className="context-forbidden-list">
                {forbidden_operations.map((op, idx) => (
                  <span key={idx} className="context-forbidden-badge">
                    {op}
                  </span>
                ))}
              </div>
              <p className="context-section-note">
                These SQL operations are not allowed for your role
              </p>
            </section>
          )}

          {/* Context Metadata */}
          <section className="context-section metadata">
            <div className="context-metadata">
              <small>Context built at: {new Date().toLocaleTimeString()}</small>
            </div>
          </section>

        </div>
      )}
    </div>
  );
};

export default ContextPanel;
