import { useState } from "react";

export default function QueryInspector({ data }) {
  const [open, setOpen] = useState(false);
  if (!data) return null;
  const { risk_score, status, sql, rows, execution_time, reasons, approval_id } = data;
  function getRiskLevel(score) {
    if (score < 30) return { label: "SAFE", color: "bg-green-500" };
    if (score < 70) return { label: "MEDIUM", color: "bg-yellow-500" };
    return { label: "HIGH", color: "bg-red-500" };
  }
  const risk = getRiskLevel(risk_score);
  return (
    <div className="border rounded-2xl p-4 shadow-sm bg-white">
      {/* TOP BAR */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className={`text-white px-3 py-1 rounded-full text-xs ${risk.color}`}>
            {risk.label}
          </span>
          <span className="text-sm text-gray-600" title="Risk is calculated based on joins, filters, and scan size">
            Risk: {risk_score}
          </span>
          {rows !== undefined && (
            <span className="text-sm text-gray-500">
              Rows: {rows}
            </span>
          )}
          {execution_time && (
            <span className="text-sm text-gray-500">
              {execution_time} ms
            </span>
          )}
        </div>
        <button
          onClick={() => setOpen(!open)}
          className="text-sm text-blue-500"
        >
          {open ? "Hide SQL" : "View SQL"}
        </button>
      </div>
      {/* STATUS */}
      <div className="mt-2 text-sm">
        {status === "blocked" && (
          <span className="text-red-600">Blocked</span>
        )}
        {status === "success" && (
          <span className="text-green-600">Executed</span>
        )}
        {status === "rewritten" && (
          <span className="text-yellow-600">Optimized</span>
        )}
        {status === "require_approval" && (
          <span className="text-yellow-600">Needs Approval</span>
        )}
      </div>
      {/* APPROVAL STATE */}
      {approval_id && (
        <div className="mt-2 text-yellow-600 text-sm">
          Requires approval (ID: {approval_id})
        </div>
      )}
      {/* REASONS */}
      {reasons?.length > 0 && (
        <div className="mt-2 text-xs text-red-500">
          {reasons.map((r, i) => (
            <div key={i}>⚠️ {r}</div>
          ))}
        </div>
      )}
      {/* SQL PREVIEW */}
      {open && (
        <div className="mt-3 bg-gray-900 text-green-400 p-3 rounded-lg text-xs overflow-auto">
          <pre>{sql}</pre>
          <button onClick={() => navigator.clipboard.writeText(sql)} className="mt-2 text-xs text-blue-400 underline">Copy SQL</button>
        </div>
      )}
    </div>
  );
}
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
