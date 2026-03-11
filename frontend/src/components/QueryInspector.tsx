import React, { useState } from 'react';
import { apiUrl } from '../lib/api';

interface RiskProfile {
  score: number;
  injection: number;
  policy: number;
  sensitive: number;
}

interface InspectorResponse {
  approved: boolean;
  safe: boolean;
  read_only: boolean;
  dangerous_keywords: string[];
  table_checks: Array<{ table: string; exists: boolean }>;
  column_checks: Array<{ column: string; exists: boolean }>;
  missing_tables: string[];
  missing_columns: string[];
  reasons: string[];
}

export const QueryInspector: React.FC = () => {
  const [question] = useState('Show revenue by region');

  const [sql, setSql] = useState(`SELECT region,
       SUM(revenue) AS total_revenue
FROM sales
GROUP BY region
ORDER BY total_revenue DESC`);

  const [risk, setRisk] = useState<RiskProfile>({
    score: 0.12,
    injection: 0.01,
    policy: 0,
    sensitive: 0,
  });

  const [fingerprint] = useState('7d31f91c');
  const [loading, setLoading] = useState(false);
  const [inspectResult, setInspectResult] = useState<InspectorResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runInspection = async () => {
    try {
      setLoading(true);
      setError(null);

      const selectedDatabase = localStorage.getItem('dbDatabase') || undefined;
      const response = await fetch(apiUrl('/api/v1/query/inspect'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sql,
          database: selectedDatabase,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Inspector request failed (${response.status})`);
      }

      const data: InspectorResponse = await response.json();
      setInspectResult(data);

      const blockedSignals =
        data.dangerous_keywords.length + data.missing_tables.length + data.missing_columns.length;
      const nextRisk = Math.min(1, blockedSignals * 0.2 + (data.read_only ? 0.05 : 0.4));
      setRisk({
        score: nextRisk,
        injection: data.dangerous_keywords.length > 0 ? 0.4 : 0.01,
        policy: data.read_only ? 0 : 0.5,
        sensitive: data.missing_tables.length > 0 ? 0.2 : 0,
      });
    } catch (inspectError: any) {
      setError(inspectError?.message || 'Inspection failed');
      setInspectResult(null);
    } finally {
      setLoading(false);
    }
  };

  const riskColor = risk.score < 0.2 ? '#22c55e' : risk.score < 0.5 ? '#f59e0b' : '#ef4444';

  return (
    <div className="query-inspector">
      <h2>🔍 Query Inspector</h2>

      <div className="pipeline-flow">
        <span>User Question</span>
        <span>→</span>
        <span>AI SQL</span>
        <span>→</span>
        <span>Firewall</span>
        <span>→</span>
        <span>Fingerprint</span>
        <span>→</span>
        <span>Results</span>
      </div>

      <div className="pipeline-grid">
        {/* User Question */}
        <section>
          <h3>User Question</h3>
          <pre>{question}</pre>
        </section>

        {/* Generated SQL */}
        <section>
          <h3>Generated SQL</h3>
          <textarea
            value={sql}
            onChange={(event) => setSql(event.target.value)}
            rows={6}
            style={{ width: '100%', fontFamily: 'monospace', fontSize: 13 }}
          />
          <button
            onClick={runInspection}
            disabled={loading || !sql.trim()}
            style={{ marginTop: 8 }}
          >
            {loading ? 'Inspecting...' : 'Run Inspector'}
          </button>
          {error && <p style={{ color: '#ef4444', marginTop: 8 }}>{error}</p>}
        </section>

        {/* Firewall Analysis */}
        <section>
          <h3>Firewall Analysis</h3>
          <p style={{ color: riskColor }}>
            <strong>Risk Score: {(risk.score * 100).toFixed(1)}%</strong>
          </p>
          <ul>
            <li>💉 Injection Risk: {(risk.injection * 100).toFixed(1)}%</li>
            <li>⚠️ Policy Violations: {(risk.policy * 100).toFixed(1)}%</li>
            <li>🔐 Sensitive Tables: {(risk.sensitive * 100).toFixed(1)}%</li>
          </ul>
        </section>

        {/* Query Fingerprint */}
        <section>
          <h3>Query Fingerprint</h3>
          <pre>{fingerprint}</pre>
          <p className="fingerprint-note">Unique query ID for tracking & caching</p>
        </section>

        {/* Inspector Decision */}
        <section>
          <h3>Inspector Decision</h3>
          {!inspectResult ? (
            <p>Run the inspector to validate table/column existence and safety checks.</p>
          ) : (
            <>
              <p style={{ color: inspectResult.approved ? '#22c55e' : '#ef4444', fontWeight: 700 }}>
                {inspectResult.approved ? 'APPROVED' : 'REJECTED'}
              </p>
              {inspectResult.reasons.length === 0 ? (
                <p>No blocking reasons found.</p>
              ) : (
                <ul>
                  {inspectResult.reasons.map((reason) => (
                    <li key={reason}>{reason}</li>
                  ))}
                </ul>
              )}
            </>
          )}
        </section>
      </div>
    </div>
  );
};
