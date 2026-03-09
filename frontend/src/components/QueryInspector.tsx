import React, { useState } from 'react';

interface RiskProfile {
  score: number;
  injection: number;
  policy: number;
  sensitive: number;
}

export const QueryInspector: React.FC = () => {
  const [question] = useState('Show revenue by region');

  const [sql] = useState(`SELECT region,
       SUM(revenue) AS total_revenue
FROM sales
GROUP BY region
ORDER BY total_revenue DESC`);

  const [risk] = useState<RiskProfile>({
    score: 0.12,
    injection: 0.01,
    policy: 0,
    sensitive: 0,
  });

  const [fingerprint] = useState('7d31f91c');

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
          <pre>{sql}</pre>
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
      </div>
    </div>
  );
};
