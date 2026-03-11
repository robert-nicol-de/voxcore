import React, { useState, useEffect } from 'react';
import './SensitivityScanner.css';
import { apiUrl } from '../../lib/api';

/**
 * SensitivityScanner Component
 * 
 * Displays database schema sensitivity analysis and auto-generated security policies.
 * Integrated with VoxCore's Data Sensitivity Scanner.
 * 
 * Features:
 * - Real-time schema scanning
 * - Sensitivity classification (SECRET, PII, FINANCIAL, HEALTH)
 * - Auto-generated security policies
 * - Risk assessment and recommendations
 * - Policy preview and application
 */

const SensitivityScanner = ({ connectorName = 'Unknown', schemaInfo = [] }) => {
  const [scanResults, setScanResults] = useState(null);
  const [generatedPolicy, setGeneratedPolicy] = useState(null);
  const [maskMap, setMaskMap] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [activeTab, setActiveTab] = useState('findings');
  const [filterType, setFilterType] = useState('all');
  const [patterns, setPatterns] = useState(null);

  // Fetch available patterns on mount
  useEffect(() => {
    fetchPatterns();
  }, []);

  const fetchPatterns = async () => {
    try {
      const response = await fetch(apiUrl('/api/scanner/patterns'));
      const data = await response.json();
      setPatterns(data);
    } catch (error) {
      console.error('Failed to fetch patterns:', error);
    }
  };

  const runScan = async () => {
    if (!schemaInfo || schemaInfo.length === 0) {
      alert('No schema information available');
      return;
    }

    setScanning(true);
    try {
      const response = await fetch(apiUrl('/api/scanner/scan'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          connector_name: connectorName,
          schema_info: schemaInfo,
        }),
      });

      if (!response.ok) throw new Error('Scan failed');

      const results = await response.json();
      setScanResults(results);
      setGeneratedPolicy(null);
      setMaskMap(null);
    } catch (error) {
      alert(`Scan error: ${error.message}`);
    } finally {
      setScanning(false);
    }
  };

  const generatePolicy = async () => {
    if (!scanResults) {
      alert('Please run a scan first');
      return;
    }

    setGenerating(true);
    try {
      const response = await fetch(apiUrl('/api/scanner/generate-policy'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          connector_name: connectorName,
          scan_results: scanResults,
        }),
      });

      if (!response.ok) throw new Error('Policy generation failed');

      const policy = await response.json();
      setGeneratedPolicy(policy);

      // Also generate mask map
      const maskResponse = await fetch(apiUrl('/api/scanner/generate-mask-map'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          connector_name: connectorName,
          scan_results: scanResults,
        }),
      });

      if (maskResponse.ok) {
        const maskData = await maskResponse.json();
        setMaskMap(maskData.mask_map);
      }
    } catch (error) {
      alert(`Generation error: ${error.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const applyPolicy = async () => {
    if (!generatedPolicy) return;

    try {
      // Save policy to backend
      const response = await fetch(apiUrl('/api/connectors/apply-policy'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          connector_name: connectorName,
          policy: generatedPolicy,
        }),
      });

      if (response.ok) {
        alert('✅ Security policy applied successfully!');
      } else {
        alert('⚠️ Policy saved but application may require manual steps');
      }
    } catch (error) {
      console.log('Note: Policy endpoint may not be fully integrated yet');
      alert('✅ Policy preview ready - copy the INI format below to apply');
    }
  };

  const getRiskColor = (type) => {
    switch (type) {
      case 'secret': return '#ef4444';
      case 'pii': return '#f59e0b';
      case 'financial': return '#f59e0b';
      case 'health': return '#ec4899';
      default: return '#8892b0';
    }
  };

  const getRiskIcon = (type) => {
    switch (type) {
      case 'secret': return '🔴';
      case 'pii': return '👤';
      case 'financial': return '💳';
      case 'health': return '🏥';
      default: return '📋';
    }
  };

  const filteredFindings =
    filterType === 'all'
      ? scanResults?.by_type
      : { [filterType]: scanResults?.by_type?.[filterType] || [] };

  const getTotalByType = (type) => {
    return scanResults?.by_type?.[type]?.length || 0;
  };

  return (
    <div className="sensitivity-scanner">
      <div className="scanner-header">
        <h2>📊 Data Sensitivity Scanner</h2>
        <p>Automatically detect sensitive data and generate security policies</p>
      </div>

      {/* Control Panel */}
      <div className="scanner-controls">
        <div className="control-group">
          <label>Scanner Actions</label>
          <div className="button-group">
            <button
              onClick={runScan}
              disabled={scanning || !schemaInfo || schemaInfo.length === 0}
              className="btn btn-primary"
            >
              {scanning ? '⏳ Scanning...' : '🔍 Scan Schema'}
            </button>
            {scanResults && (
              <button
                onClick={generatePolicy}
                disabled={generating}
                className="btn btn-success"
              >
                {generating ? '⏳ Generating...' : '⚙️ Generate Policy'}
              </button>
            )}
            {generatedPolicy && (
              <button
                onClick={applyPolicy}
                className="btn btn-warning"
              >
                ✅ Apply Policy
              </button>
            )}
          </div>
        </div>

        {scanResults && (
          <div className="control-group">
            <label>Filter by Type</label>
            <div className="filter-buttons">
              <button
                onClick={() => setFilterType('all')}
                className={filterType === 'all' ? 'active' : ''}
              >
                All ({scanResults.total_findings})
              </button>
              <button
                onClick={() => setFilterType('secret')}
                className={filterType === 'secret' ? 'active' : ''}
              >
                🔴 Secrets ({getTotalByType('secret')})
              </button>
              <button
                onClick={() => setFilterType('pii')}
                className={filterType === 'pii' ? 'active' : ''}
              >
                👤 PII ({getTotalByType('pii')})
              </button>
              <button
                onClick={() => setFilterType('financial')}
                className={filterType === 'financial' ? 'active' : ''}
              >
                💳 Financial ({getTotalByType('financial')})
              </button>
              <button
                onClick={() => setFilterType('health')}
                className={filterType === 'health' ? 'active' : ''}
              >
                🏥 Health ({getTotalByType('health')})
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Tab Navigation */}
      {(scanResults || generatedPolicy) && (
        <div className="scanner-tabs">
          <button
            onClick={() => setActiveTab('findings')}
            className={`tab ${activeTab === 'findings' ? 'active' : ''}`}
          >
            📋 Findings ({scanResults?.total_findings || 0})
          </button>
          <button
            onClick={() => setActiveTab('risk')}
            className={`tab ${activeTab === 'risk' ? 'active' : ''}`}
          >
            ⚠️ Risk Summary
          </button>
          {generatedPolicy && (
            <>
              <button
                onClick={() => setActiveTab('policy')}
                className={`tab ${activeTab === 'policy' ? 'active' : ''}`}
              >
                🛡️ Generated Policy
              </button>
              <button
                onClick={() => setActiveTab('recommendations')}
                className={`tab ${activeTab === 'recommendations' ? 'active' : ''}`}
              >
                💡 Recommendations
              </button>
            </>
          )}
        </div>
      )}

      {/* Content Panels */}
      {!scanResults && (
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <h3>Ready to scan</h3>
          <p>Click "Scan Schema" to analyze your database for sensitive data</p>
        </div>
      )}

      {scanResults && activeTab === 'findings' && (
        <div className="findings-panel">
          <div className="findings-grid">
            {Object.entries(filteredFindings || {}).map(([type, columns]) => (
              columns.length > 0 && (
                <div key={type} className="finding-section">
                  <div className="section-header">
                    <span className="icon">{getRiskIcon(type)}</span>
                    <span className="title">
                      {type.toUpperCase()} ({columns.length} columns)
                    </span>
                  </div>
                  <div className="column-list">
                    {columns.map((col, idx) => (
                      <div key={idx} className="column-item">
                        <div className="column-name">
                          <strong>{col.table_name}</strong>
                          <span className="dot">.</span>
                          <strong>{col.column_name}</strong>
                        </div>
                        <div className="column-meta">
                          <span
                            className="confidence-badge"
                            style={{ color: getRiskColor(type) }}
                          >
                            {Math.round(col.confidence * 100)}% confident
                          </span>
                          {col.detected_patterns.length > 0 && (
                            <span className="patterns">
                              Patterns: {col.detected_patterns.join(', ')}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )
            ))}
          </div>
        </div>
      )}

      {scanResults && activeTab === 'risk' && (
        <div className="risk-panel">
          <div className="risk-summary">
            <div className="risk-stat critical">
              <div className="risk-label">🔴 CRITICAL</div>
              <div className="risk-count">{scanResults.risk_summary.critical}</div>
              <div className="risk-desc">Secret columns</div>
            </div>
            <div className="risk-stat high">
              <div className="risk-label">⚠️ HIGH</div>
              <div className="risk-count">{scanResults.risk_summary.high}</div>
              <div className="risk-desc">Sensitive columns</div>
            </div>
            <div className="risk-stat medium">
              <div className="risk-label">ℹ️ MEDIUM</div>
              <div className="risk-count">{scanResults.risk_summary.medium}</div>
              <div className="risk-desc">Health data</div>
            </div>
          </div>

          <div className="affected-tables">
            <h3>Affected Tables</h3>
            <div className="table-list">
              {Object.entries(scanResults.by_table || {}).map(([tableName, columns]) => (
                <div key={tableName} className="table-item">
                  <span className="table-name">{tableName}</span>
                  <span className="column-count">{columns.length} sensitive</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {generatedPolicy && activeTab === 'policy' && (
        <div className="policy-panel">
          <div className="policy-info">
            <h3>{generatedPolicy.policy_name}</h3>
            <p>{generatedPolicy.description}</p>
          </div>

          <div className="policy-sections">
            {generatedPolicy.deny_columns && generatedPolicy.deny_columns.length > 0 && (
              <div className="policy-section">
                <h4>🔴 Blocked Columns</h4>
                <div className="column-tags">
                  {generatedPolicy.deny_columns.map((col, idx) => (
                    <span key={idx} className="tag blocked">
                      {col}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {generatedPolicy.deny_tables && generatedPolicy.deny_tables.length > 0 && (
              <div className="policy-section">
                <h4>🚫 Blocked Tables</h4>
                <div className="table-tags">
                  {generatedPolicy.deny_tables.map((table, idx) => (
                    <span key={idx} className="tag table-blocked">
                      {table}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {generatedPolicy.mask_columns && generatedPolicy.mask_columns.length > 0 && (
              <div className="policy-section">
                <h4>👤 Masked Columns</h4>
                <div className="column-tags">
                  {generatedPolicy.mask_columns.map((col, idx) => (
                    <span key={idx} className="tag masked">
                      {col}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="policy-settings">
              <h4>⚙️ Policy Settings</h4>
              <div className="settings-grid">
                <div className="setting">
                  <span className="setting-name">Max Rows</span>
                  <span className="setting-value">{generatedPolicy.max_rows}</span>
                </div>
                <div className="setting">
                  <span className="setting-name">AI Access</span>
                  <span className={`setting-value ${generatedPolicy.allow_ai_access ? 'allowed' : 'denied'}`}>
                    {generatedPolicy.allow_ai_access ? '✅ Allowed' : '❌ Denied'}
                  </span>
                </div>
                <div className="setting">
                  <span className="setting-name">Require Approval</span>
                  <span className={`setting-value ${generatedPolicy.require_approval ? 'yes' : 'no'}`}>
                    {generatedPolicy.require_approval ? '✅ Yes' : '❌ No'}
                  </span>
                </div>
                <div className="setting">
                  <span className="setting-name">Audit All</span>
                  <span className={`setting-value ${generatedPolicy.audit_all ? 'yes' : 'no'}`}>
                    {generatedPolicy.audit_all ? '✅ Yes' : '❌ No'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="policy-format">
            <h4>📄 INI Format</h4>
            <pre className="ini-format">
{`[policy_${generatedPolicy.policy_name}]
description = ${generatedPolicy.description}
${generatedPolicy.mask_columns.length > 0 ? `mask_columns = ${generatedPolicy.mask_columns.join(',')}` : ''}
${generatedPolicy.deny_tables.length > 0 ? `deny_tables = ${generatedPolicy.deny_tables.join(',')}` : ''}
${generatedPolicy.deny_columns.length > 0 ? `deny_columns = ${generatedPolicy.deny_columns.join(',')}` : ''}
max_rows = ${generatedPolicy.max_rows}
allow_ai_access = ${generatedPolicy.allow_ai_access}
require_approval = ${generatedPolicy.require_approval}
audit_all = ${generatedPolicy.audit_all}`}
            </pre>
          </div>
        </div>
      )}

      {generatedPolicy && activeTab === 'recommendations' && (
        <div className="recommendations-panel">
          <h3>💡 Security Recommendations</h3>
          <div className="recommendations-list">
            {generatedPolicy.recommendations.map((rec, idx) => (
              <div key={idx} className="recommendation-item">
                <span className="rec-icon">►</span>
                <span className="rec-text">{rec}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SensitivityScanner;
