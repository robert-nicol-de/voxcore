import React, { useState } from 'react';
import LiveQueryFlow, { type QueryFlowStage } from '../components/LiveQueryFlow';
import PageHeader from '../components/PageHeader';
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
  const [flowStages, setFlowStages] = useState<QueryFlowStage[]>(defaultFlowStages());

  const companyId = localStorage.getItem('voxcore_company_id') || 'default';
  const workspaceId = localStorage.getItem('voxcore_workspace_id') || 'default';

  async function generateAndAnalyze() {
    if (!question.trim()) return;

    setError(null);
    setLoadingPreview(true);
    setPreviewRows([]);
    setExecutionResult(null);
    setGeneratedSql(question);

    setFlowStages([
      createStage('User Prompt', 'safe', previewPrompt(question)),
      createStage('AI Generated SQL', 'active', 'Generating SQL'),
      createStage('Risk Engine', 'idle', 'Waiting'),
      createStage('Policy Engine', 'idle', 'Waiting'),
      createStage('Sandbox', 'idle', 'Waiting'),
      createStage('Database', 'idle', 'Waiting'),
    ]);

    try {
      const riskRes = await fetch(apiUrl('/api/v1/query/risk'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: question }),
      });
      const riskData = await riskRes.json();
      const nextRiskLevel = (riskData.risk_level || 'low').toUpperCase();
      setRiskLevel(nextRiskLevel);

      setFlowStages([
        createStage('User Prompt', 'safe', previewPrompt(question)),
        createStage('AI Generated SQL', 'safe', 'SQL prepared'),
        createStage('Risk Engine', flowStatusFromRisk(nextRiskLevel), `${nextRiskLevel} RISK`),
        createStage('Policy Engine', 'active', 'Evaluating policy'),
        createStage('Sandbox', 'idle', 'Waiting'),
        createStage('Database', 'idle', 'Waiting'),
      ]);

      const sandboxRes = await fetch(apiUrl('/api/v1/query/sandbox'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: question }),
      });

      const sandboxData = await sandboxRes.json();
      if (!sandboxRes.ok) {
        setError(sandboxData.detail || 'Preview failed. Check query syntax.');
        const failedPreviewFlow = [
          createStage('User Prompt', 'safe', previewPrompt(question)),
          createStage('AI Generated SQL', 'safe', 'SQL prepared'),
          createStage('Risk Engine', flowStatusFromRisk(nextRiskLevel), `${nextRiskLevel} RISK`),
          createStage('Policy Engine', 'warning', 'Review required'),
          createStage('Sandbox', 'blocked', 'Preview failed'),
          createStage('Database', 'idle', 'Not reached'),
        ];
        setFlowStages(failedPreviewFlow);
        persistFlow(failedPreviewFlow);
        return;
      }

      const previewCount = (sandboxData.preview || []).length;
      setPreviewRows(sandboxData.preview || []);
      const previewFlow = [
        createStage('User Prompt', 'safe', previewPrompt(question)),
        createStage('AI Generated SQL', 'safe', 'SQL prepared'),
        createStage('Risk Engine', flowStatusFromRisk(nextRiskLevel), `${nextRiskLevel} RISK`),
        createStage('Policy Engine', 'safe', 'Passed policy checks'),
        createStage('Sandbox', 'safe', `Previewed ${previewCount} rows`),
        createStage('Database', 'idle', 'Awaiting execution'),
      ];
      setFlowStages(previewFlow);
      persistFlow(previewFlow);
    } catch {
      setError('Could not reach SQL assistant services.');
      const unavailableFlow = [
        createStage('User Prompt', 'safe', previewPrompt(question)),
        createStage('AI Generated SQL', 'warning', 'Service unavailable'),
        createStage('Risk Engine', 'idle', 'Waiting'),
        createStage('Policy Engine', 'idle', 'Waiting'),
        createStage('Sandbox', 'idle', 'Waiting'),
        createStage('Database', 'idle', 'Waiting'),
      ];
      setFlowStages(unavailableFlow);
      persistFlow(unavailableFlow);
    } finally {
      setLoadingPreview(false);
    }
  }

  async function executeQuery() {
    if (!question.trim()) return;

    setError(null);
    setLoadingExecute(true);
    setExecutionResult(null);

    const executionStartFlow = [
      createStage('User Prompt', 'safe', previewPrompt(question)),
      createStage('AI Generated SQL', generatedSql ? 'safe' : 'active', generatedSql ? 'SQL prepared' : 'Generating SQL'),
      createStage('Risk Engine', flowStatusFromRisk(riskLevel), `${riskLevel} RISK`),
      createStage('Policy Engine', 'active', 'Inspecting query'),
      createStage('Sandbox', previewRows.length > 0 ? 'safe' : 'idle', previewRows.length > 0 ? `Previewed ${previewRows.length} rows` : 'Waiting'),
      createStage('Database', 'idle', 'Waiting'),
    ];
    setFlowStages(executionStartFlow);
    persistFlow(executionStartFlow);

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
        const blockedFlow = [
          createStage('User Prompt', 'safe', previewPrompt(question)),
          createStage('AI Generated SQL', generatedSql ? 'safe' : 'warning', generatedSql ? 'SQL prepared' : 'Missing SQL'),
          createStage('Risk Engine', flowStatusFromRisk(riskLevel), `${riskLevel} RISK`),
          createStage('Policy Engine', 'blocked', 'Execution rejected'),
          createStage('Sandbox', previewRows.length > 0 ? 'safe' : 'idle', previewRows.length > 0 ? `Previewed ${previewRows.length} rows` : 'Waiting'),
          createStage('Database', 'idle', 'Not reached'),
        ];
        setFlowStages(blockedFlow);
        persistFlow(blockedFlow);
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
        const runningFlow = [
          createStage('User Prompt', 'safe', previewPrompt(question)),
          createStage('AI Generated SQL', 'safe', 'SQL prepared'),
          createStage('Risk Engine', flowStatusFromRisk(riskLevel), `${riskLevel} RISK`),
          createStage('Policy Engine', 'active', 'Queued for execution'),
          createStage('Sandbox', previewRows.length > 0 ? 'safe' : 'idle', previewRows.length > 0 ? `Previewed ${previewRows.length} rows` : 'Waiting'),
          createStage('Database', 'active', 'Executing'),
        ];
        setFlowStages(runningFlow);
        persistFlow(runningFlow);
        return;
      }

      if (finalResult.status === 'failed') {
        setError(finalResult.error || 'Execution failed.');
        const failedFlow = [
          createStage('User Prompt', 'safe', previewPrompt(question)),
          createStage('AI Generated SQL', 'safe', 'SQL prepared'),
          createStage('Risk Engine', flowStatusFromRisk(riskLevel), `${riskLevel} RISK`),
          createStage('Policy Engine', 'warning', 'Execution failed'),
          createStage('Sandbox', previewRows.length > 0 ? 'safe' : 'idle', previewRows.length > 0 ? `Previewed ${previewRows.length} rows` : 'Waiting'),
          createStage('Database', 'blocked', 'Execution failed'),
        ];
        setFlowStages(failedFlow);
        persistFlow(failedFlow);
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

      const nextRisk = resultData.risk_level ? String(resultData.risk_level).toUpperCase() : riskLevel;
      setRiskLevel(nextRisk);

      const finalFlow = finalResult.status === 'blocked'
        ? [
            createStage('User Prompt', 'safe', previewPrompt(question)),
            createStage('AI Generated SQL', 'safe', 'SQL prepared'),
            createStage('Risk Engine', flowStatusFromRisk(nextRisk), `${nextRisk} RISK`),
            createStage('Policy Engine', 'blocked', 'Blocked by policy'),
            createStage('Sandbox', previewRows.length > 0 ? 'safe' : 'warning', previewRows.length > 0 ? `Previewed ${previewRows.length} rows` : 'Preview recommended'),
            createStage('Database', 'blocked', 'Write prevented'),
          ]
        : [
            createStage('User Prompt', 'safe', previewPrompt(question)),
            createStage('AI Generated SQL', 'safe', 'SQL prepared'),
            createStage('Risk Engine', flowStatusFromRisk(nextRisk), `${nextRisk} RISK`),
            createStage('Policy Engine', 'safe', 'Allowed to proceed'),
            createStage('Sandbox', previewRows.length > 0 ? 'safe' : 'warning', previewRows.length > 0 ? `Previewed ${previewRows.length} rows` : 'Executed directly'),
            createStage('Database', 'safe', 'Query completed'),
          ];

      setFlowStages(finalFlow);
      persistFlow(finalFlow);
    } catch {
      setError('Could not execute query.');
      const unavailableFlow = [
        createStage('User Prompt', 'safe', previewPrompt(question)),
        createStage('AI Generated SQL', generatedSql ? 'safe' : 'warning', generatedSql ? 'SQL prepared' : 'Missing SQL'),
        createStage('Risk Engine', flowStatusFromRisk(riskLevel), `${riskLevel} RISK`),
        createStage('Policy Engine', 'warning', 'Execution unavailable'),
        createStage('Sandbox', previewRows.length > 0 ? 'safe' : 'idle', previewRows.length > 0 ? `Previewed ${previewRows.length} rows` : 'Waiting'),
        createStage('Database', 'idle', 'Not reached'),
      ];
      setFlowStages(unavailableFlow);
      persistFlow(unavailableFlow);
    } finally {
      setLoadingExecute(false);
    }
  }

  return (
    <div className="assistant-control-panel" style={{ color: '#e8f0ff' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 18 }}>
        <img src="/assets/vc_logo.png" alt="VoxCloud" style={{ width: 40, height: 40, objectFit: 'contain' }} />
        <PageHeader title="SQL Assistant" subtitle="Natural language SQL with live security pipeline and policy enforcement" />
      </div>

      <section className="assistant-grid" style={{ marginBottom: 24 }}>
        <div style={panelStyle}>
          <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 12 }}>
            <label style={{ color: 'var(--platform-muted)', fontSize: 13 }}>Database:</label>
            <select value={databaseName} onChange={(e) => setDatabaseName(e.target.value)} style={inputStyle}>
              <option value="AdventureWorks2022">AdventureWorks2022</option>
              <option value="FinancialDW">FinancialDW</option>
              <option value="SalesAnalytics">SalesAnalytics</option>
            </select>
          </div>

          <div style={{ marginTop: 22 }}>
            <div style={{ marginBottom: 8, color: 'var(--platform-muted)' }}>Prompt</div>
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
        </div>

        <LiveQueryFlow
          title="AI Security Pipeline"
          subtitle="Each stage lights up as the query moves through VoxCore security."
          stages={flowStages}
          compact
        />
      </section>

      <section style={panelStyle}>
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

      <LiveQueryFlow
        title="Live AI Query Flow"
        subtitle="Visual proof of how VoxCore protects databases from AI-generated queries."
        stages={flowStages}
      />

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

function createStage(label: string, status: QueryFlowStage['status'], detail: string) {
  return { label, status, detail };
}

function defaultFlowStages(): QueryFlowStage[] {
  return [
    createStage('User Prompt', 'idle', 'Waiting for prompt'),
    createStage('AI Generated SQL', 'idle', 'Waiting for generation'),
    createStage('Risk Engine', 'idle', 'Waiting for analysis'),
    createStage('Policy Engine', 'idle', 'Waiting for policy check'),
    createStage('Sandbox', 'idle', 'Waiting for preview'),
    createStage('Database', 'idle', 'Waiting for execution'),
  ];
}

function previewPrompt(value: string) {
  const trimmed = value.trim();
  if (!trimmed) return 'Waiting for prompt';
  return trimmed.length > 38 ? `${trimmed.slice(0, 35)}...` : trimmed;
}

function flowStatusFromRisk(level: string): QueryFlowStage['status'] {
  const value = level.toLowerCase();
  if (value.includes('high') || value.includes('critical')) return 'warning';
  if (value.includes('med')) return 'warning';
  return 'safe';
}

function persistFlow(stages: QueryFlowStage[]) {
  try {
    localStorage.setItem('voxcloud_latest_query_flow', JSON.stringify(stages));
  } catch {
    // Ignore storage errors.
  }
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
