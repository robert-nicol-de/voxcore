// DashboardPanel.jsx
// Displays live insights, anomalies, trends, root cause graphs, and suggestions
import React, { useEffect, useState } from 'react';

export default function DashboardPanel({ data, sessionId }) {
  const [insights, setInsights] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [trends, setTrends] = useState([]);
  const [rootCauses, setRootCauses] = useState([]);
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    // Optionally, fetch live data from backend APIs
    fetch('/api/insights/latest').then(r => r.json()).then(d => setInsights(d.insights || []));
    fetch('/api/insights/anomalies').then(r => r.json()).then(d => setAnomalies(d.anomalies || []));
    fetch('/api/insights/trends').then(r => r.json()).then(d => setTrends(d.trends || []));
    fetch('/api/insights/root_causes').then(r => r.json()).then(d => setRootCauses(d.root_causes || []));
    fetch('/api/exploration/suggestions').then(r => r.json()).then(d => setSuggestions(d.suggestions || []));
  }, [sessionId, data]);

  return (
    <div className="dashboard-panel-inner">
      <section>
        <h3>Live Insights</h3>
        {insights.map((i, idx) => <div key={idx} className="insight-card">{i.insight || i.description}</div>)}
      </section>
      <section>
        <h3>Anomalies</h3>
        {anomalies.map((a, idx) => <div key={idx} className="anomaly-card">{a.insight || a.description}</div>)}
      </section>
      <section>
        <h3>Trends</h3>
        {trends.map((t, idx) => <div key={idx} className="trend-card">{t.insight || t.description}</div>)}
      </section>
      <section>
        <h3>Root Cause Graph</h3>
        {/* Placeholder: render root cause chains as a list or use D3.js for a graph */}
        {rootCauses.map((edge, idx) => <div key={idx}>{edge.from} → {edge.relationship} → {edge.to}</div>)}
      </section>
      <section>
        <h3>Exploration Suggestions</h3>
        <ul>
          {suggestions.map((s, idx) => <li key={idx}>{s.metric} by {s.dimension}</li>)}
        </ul>
      </section>
    </div>
  );
}
