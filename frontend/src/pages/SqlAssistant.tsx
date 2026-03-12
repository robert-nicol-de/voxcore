import React, { useState } from 'react';
import { apiUrl } from '../lib/api';

type ExecuteResult = {
  status?: string;
  risk_level?: string;
  effective_query?: string;
  reasons?: string[];
};

export default function SqlAssistant() {
  const [databaseName, setDatabaseName] = useState('AdventureWorks2022');
  const [question, setQuestion] = useState('Show top 10 customers by revenue');
  const [generatedSql, setGeneratedSql] = useState('');
  const [riskLevel, setRiskLevel] = useState('LOW');
  const [previewRows, setPreviewRows] = useState<any[]>([]);
  const [executionResult, setExecutionResult] = useState<ExecuteResult | null>(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [loadingExecute, setLoadingExecute] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const companyId = localStorage.getItem('voxcore_company_id') || 'default';
  const workspaceId = localStorage.getItem('voxcore_workspace_id') || 'default';

  async function generateAndAnalyze() {
    if (!question.trim()) return;
    setError(null);
    setLoadingPreview(true);
    setPreviewRows([]);
    setExecutionResult(null);

    try {
      const riskRes = await fetch(apiUrl('/api/v1/query/risk'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: question }),
      });
      const riskData = await riskRes.json();
      setRiskLevel((riskData.risk_level || 'low').toUpperCase());

      const sandboxRes = await fetch(apiUrl('/api/v1/query/sandbox'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: question }),
      });

      const sandboxData = await sandboxRes.json();
      if (!sandboxRes.ok) {
        setGeneratedSql(question);
        setError(sandboxData.detail || 'Preview failed. Check query syntax.');
        return;
      }

      setGeneratedSql(question);
      setPreviewRows(sandboxData.preview || []);
    } catch {
      setError('Could not reach SQL assistant services.');
    } finally {
      setLoadingPreview(false);
    }
  }

  async function executeQuery() {
    if (!question.trim()) return;
    setError(null);
    setLoadingExecute(true);
    setExecutionResult(null);

    try {
      const res = await fetch(apiUrl('/api/v1/query'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_id: companyId,
          workspace_id: workspaceId,
          query: question,
          agent: 'sql_assistant',
        }),
      });
      const data = await res.json();

      if (!res.ok || data.status !== 'queued' || !data.job_id) {
        setError(data.detail || data.message || 'Execution request failed.');
        return;
      }

      let finalResult: any = null;
      for (let i = 0; i < 25; i += 1) {
        await new Promise((resolve) => window.setTimeout(resolve, 700));
        const jobRes = await fetch(apiUrl(`/api/v1/query/jobs/${data.job_id}`));
        if (!jobRes.ok) continue;
        const jobData = await jobRes.json();
        if (jobData.status === 'completed' || jobData.status === 'failed' || jobData.status === 'blocked') {
          finalResult = jobData;
          break;
        }
      }

      if (!finalResult) {
        setError('Execution is still running. Check Query Logs for status.');
        return;
      }

      if (finalResult.status === 'failed') {
        setError(finalResult.error || 'Execution failed.');
        return;
      }

      const resultData = finalResult.result || {};
      setExecutionResult({
        status: finalResult.status,
        risk_level: resultData.risk_level,
        effective_query: resultData.effective_query,
        reasons: resultData.reasons,
      });
      if (resultData.effective_query) {
        setGeneratedSql(resultData.effective_query);
      }
      if (resultData.risk_level) {
        setRiskLevel(String(resultData.risk_level).toUpperCase());
      }
    } catch {
      setError('Could not execute query.');
    } finally {
      setLoadingExecute(false);
    }
  }

  return (
    <div style={{ color: '#e8f0ff' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 18 }}>
        <img src="/assets/vc_logo.png" alt="VoxCloud" style={{ width: 40, height: 40, objectFit: 'contain' }} />
        <div>
          <h1 style={{ marginTop: 0, marginBottom: 2, fontSize: '2rem', letterSpacing: '-0.03em' }}>VoxQuery</h1>
          <p style={{ margin: 0, color: 'var(--platform-muted)' }}>Natural Language SQL Assistant</p>
        </div>
      </div>

      <section style={panelStyle}>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 12 }}>
          <label style={{ color: 'var(--platform-muted)', fontSize: 13 }}>Database:</label>
          <select
            value={databaseName}
            onChange={(e) => setDatabaseName(e.target.value)}
            style={inputStyle}
          >
            <option value="AdventureWorks2022">AdventureWorks2022</option>
            <option value="FinancialDW">FinancialDW</option>
            <option value="SalesAnalytics">SalesAnalytics</option>
          </select>
        </div>

        <div style={{ marginTop: 22 }}>
          <div style={{ marginBottom: 8, color: 'var(--platform-muted)' }}>Ask a question about your data:</div>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={3}
            style={{ ...inputStyle, width: '100%', resize: 'vertical', borderRadius: 12 }}
            placeholder="Show top 10 customers by revenue"
          />
          <div style={{ display: 'flex', gap: 12, marginTop: 12, flexWrap: 'wrap' }}>
            <button onClick={generateAndAnalyze} disabled={loadingPreview} style={primaryButton}>
              {loadingPreview ? 'Generating...' : 'Preview in Sandbox'}
            </button>
            <button onClick={executeQuery} disabled={loadingExecute} style={secondaryButton}>
              {loadingExecute ? 'Executing...' : 'Execute'}
            </button>
          </div>
        </div>
      </section>

      <section style={{ ...panelStyle, marginTop: 24 }}>
        <h2 style={sectionTitle}>AI Generated SQL</h2>
        <pre
          style={{
            margin: 0,
            padding: 16,
            borderRadius: 10,
            background: 'rgba(10,16,28,0.9)',
            border: '1px solid var(--platform-border)',
            color: '#b9d1ff',
            overflowX: 'auto',
            fontSize: 13,
          }}
        >
          {generatedSql || '-- SQL will appear here after preview or execute'}
        </pre>
        <div style={{ marginTop: 16, fontWeight: 600 }}>
          Risk Level: <span style={{ color: riskLevelColor(riskLevel) }}>{riskLevel}</span>
        </div>
      </section>

      <section style={{ ...panelStyle, marginTop: 24 }}>
        <h2 style={sectionTitle}>Sandbox Preview</h2>
        {previewRows.length === 0 ? (
          <div style={{ color: 'var(--platform-muted)' }}>No preview rows yet.</div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  {Object.keys(previewRows[0] || {}).map((key) => (
                    <th key={key} style={tableHeadCell}>{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {previewRows.map((row, idx) => (
                  <tr key={idx}>
                    {Object.keys(previewRows[0] || {}).map((key) => (
                      <td key={`${idx}-${key}`} style={tableCell}>{String(row[key] ?? '')}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {executionResult && (
        <section style={{ ...panelStyle, marginTop: 24 }}>
          <h2 style={sectionTitle}>Execution Result</h2>
          <div>Status: {executionResult.status || 'unknown'}</div>
          <div style={{ marginTop: 6 }}>Risk: {(executionResult.risk_level || 'unknown').toUpperCase()}</div>
          {executionResult.reasons && executionResult.reasons.length > 0 && (
            <div style={{ marginTop: 10, color: 'var(--platform-muted)' }}>
              {executionResult.reasons.join(' | ')}
            </div>
          )}
        </section>
      )}

      {error && <div style={{ marginTop: 20, color: '#ff8b8b' }}>{error}</div>}
    </div>
  );
}

function riskLevelColor(level: string) {
  const value = level.toLowerCase();
  if (value.includes('high') || value.includes('critical')) return '#ff6b6b';
  if (value.includes('med')) return '#ffd166';
  return '#35d07f';
}

const panelStyle: React.CSSProperties = {
  background: 'var(--platform-card-bg)',
  border: '1px solid var(--platform-border)',
  borderRadius: 12,
  padding: 24,
};

const sectionTitle: React.CSSProperties = {
  marginTop: 0,
  marginBottom: 14,
  fontSize: '1.1rem',
};

const inputStyle: React.CSSProperties = {
  background: 'rgba(10,16,28,0.8)',
  color: '#e8f0ff',
  border: '1px solid var(--platform-border)',
  borderRadius: 8,
  padding: '10px 12px',
  fontSize: 14,
};

const primaryButton: React.CSSProperties = {
  background: 'var(--platform-accent)',
  color: '#ffffff',
  border: '1px solid var(--platform-accent)',
  borderRadius: 10,
  padding: '10px 16px',
  fontWeight: 700,
  cursor: 'pointer',
};

const secondaryButton: React.CSSProperties = {
  background: 'transparent',
  color: '#d7e5ff',
  border: '1px solid var(--platform-border)',
  borderRadius: 10,
  padding: '10px 16px',
  fontWeight: 700,
  cursor: 'pointer',
};

const tableHeadCell: React.CSSProperties = {
  textAlign: 'left',
  padding: '10px 12px',
  borderBottom: '1px solid var(--platform-border)',
  color: 'var(--platform-muted)',
  fontSize: 12,
  textTransform: 'uppercase',
  letterSpacing: '0.06em',
};

const tableCell: React.CSSProperties = {
  textAlign: 'left',
  padding: '10px 12px',
  borderBottom: '1px solid rgba(79,140,255,0.1)',
  color: '#dbe7ff',
  fontSize: 13,
};
