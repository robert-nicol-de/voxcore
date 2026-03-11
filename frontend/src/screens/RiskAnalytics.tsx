import React, { useEffect, useState } from 'react';
import { Card, Badge } from '../components';
import './RiskAnalytics.css';
import { apiUrl } from '../lib/api';

interface TableStats {
  table: string;
  query_count: number;
  percentage: number;
}

interface Pattern {
  pattern: string;
  count: number;
  percentage: number;
  avg_risk_score: number;
  blocked_count?: number;
  rewritten_count?: number;
}

interface Anomaly {
  id: string;
  type: string;
  user: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  timestamp: string;
  action_recommended: string;
}

export const RiskAnalytics: React.FC = () => {
  const [tables, setTables] = useState<TableStats[]>([]);
  const [patterns, setPatterns] = useState<{ high_risk_patterns: Pattern[]; frequent_rewrites: Pattern[] } | null>(null);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const [tablesRes, patternsRes, anomaliesRes] = await Promise.all([
          fetch(apiUrl('/api/governance/analytics/tables?limit=10')),
          fetch(apiUrl('/api/governance/analytics/patterns')),
          fetch(apiUrl('/api/governance/analytics/anomalies')),
        ]);

        if (!tablesRes.ok || !patternsRes.ok || !anomaliesRes.ok) {
          throw new Error('Failed to fetch analytics');
        }

        const tablesData = await tablesRes.json();
        const patternsData = await patternsRes.json();
        const anomaliesData = await anomaliesRes.json();

        setTables(tablesData);
        setPatterns(patternsData);
        setAnomalies(anomaliesData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  const getSeverityBadgeVariant = (severity: string) => {
    switch (severity) {
      case 'low':
        return 'safe';
      case 'medium':
        return 'warning';
      case 'high':
        return 'danger';
      default:
        return 'info';
    }
  };

  if (loading) return <div className="analytics-loading">Loading risk analytics...</div>;
  if (error) return <div className="analytics-error">Error: {error}</div>;

  return (
    <div className="risk-analytics">
      <h1>Risk Analytics</h1>

      {/* Most Queried Tables */}
      <Card elevation="md">
        <h2>Most Queried Tables</h2>
        <div className="analytics-chart">
          {tables.map((table) => (
            <div key={table.table} className="chart-item">
              <div className="chart-label">{table.table}</div>
              <div className="chart-bar">
                <div
                  className="chart-fill"
                  style={{ width: `${table.percentage * 10}%` }}
                ></div>
              </div>
              <div className="chart-value">{table.query_count} queries ({table.percentage}%)</div>
            </div>
          ))}
        </div>
      </Card>

      {/* High-Risk Patterns */}
      {patterns && (
        <Card elevation="md">
          <h2>High-Risk Query Patterns</h2>
          <div className="patterns-list">
            {patterns.high_risk_patterns.map((pattern) => (
              <div key={pattern.pattern} className="pattern-item">
                <div className="pattern-header">
                  <div className="pattern-name">{pattern.pattern}</div>
                  <Badge variant="danger">Risk: {pattern.avg_risk_score}</Badge>
                </div>
                <div className="pattern-stats">
                  <div className="stat">
                    <span className="stat-label">Occurrences:</span>
                    <span className="stat-value">{pattern.count} ({pattern.percentage}%)</span>
                  </div>
                  {pattern.blocked_count !== undefined && (
                    <div className="stat">
                      <span className="stat-label">Blocked:</span>
                      <span className="stat-value">{pattern.blocked_count}</span>
                    </div>
                  )}
                  {pattern.rewritten_count !== undefined && (
                    <div className="stat">
                      <span className="stat-label">Rewritten:</span>
                      <span className="stat-value">{pattern.rewritten_count}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Frequent Rewrites */}
      {patterns && (
        <Card elevation="md">
          <h2>Frequent Rewrite Patterns</h2>
          <div className="rewrites-list">
            {patterns.frequent_rewrites.map((rewrite) => (
              <div key={rewrite.pattern} className="rewrite-item">
                <div className="rewrite-type">{rewrite.pattern}</div>
                <div className="rewrite-bar">
                  <div
                    className="rewrite-fill"
                    style={{ width: `${rewrite.percentage * 5}%` }}
                  ></div>
                </div>
                <div className="rewrite-stats">{rewrite.count} times ({rewrite.percentage}%)</div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Anomalies */}
      <Card elevation="md">
        <h2>Suspicious Behavior Patterns</h2>
        {anomalies.length === 0 ? (
          <div className="anomalies-empty">No anomalies detected</div>
        ) : (
          <div className="anomalies-list">
            {anomalies.map((anomaly) => (
              <div key={anomaly.id} className="anomaly-item">
                <div className="anomaly-header">
                  <div className="anomaly-type">{anomaly.type.replace(/_/g, ' ')}</div>
                  <Badge variant={getSeverityBadgeVariant(anomaly.severity)}>
                    {anomaly.severity.toUpperCase()}
                  </Badge>
                </div>
                <div className="anomaly-user">{anomaly.user}</div>
                <div className="anomaly-description">{anomaly.description}</div>
                <div className="anomaly-footer">
                  <span className="anomaly-time">
                    {new Date(anomaly.timestamp).toLocaleString()}
                  </span>
                  <Badge variant="info">{anomaly.action_recommended}</Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};
