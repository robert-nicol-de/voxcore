/**
 * Observability Dashboard Component
 * 
 * Real-time visualization of:
 * - System health status
 * - Latency metrics (p95, p99)
 * - Error rate
 * - Cache hit rate
 * - Cost breakdown
 * - Recent queries
 * - Active jobs
 * - Failed queries
 */

import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ObservabilityDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedQuery, setSelectedQuery] = useState(null);

  // Fetch dashboard data every 10 seconds
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/api/observability/dashboard/overview');
        const data = await response.json();
        setDashboardData(data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch dashboard data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 10000); // Refresh every 10s

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="dashboard-loading">
        <p>Loading observability data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <p>{error}</p>
      </div>
    );
  }

  if (!dashboardData) {
    return <div>No data available</div>;
  }

  const { system, metrics, recent_activity } = dashboardData;
  const { latency, errors, cache, queue, cost } = metrics;

  // Determine health color
  const getHealthColor = (status) => {
    switch (status) {
      case 'healthy':
        return '#22c55e'; // green
      case 'degraded':
        return '#f59e0b'; // amber
      case 'critical':
        return '#ef4444'; // red
      default:
        return '#6b7280'; // gray
    }
  };

  // Format cost
  const formatCost = (value) => `$${value.toFixed(2)}`;

  return (
    <div className="observability-dashboard">
      <div className="dashboard-header">
        <h1>🕵️ VoxQuery Observability Dashboard</h1>
        <p className="timestamp">Last updated: {new Date(dashboardData.timestamp).toLocaleTimeString()}</p>
      </div>

      {/* System Health Section */}
      <section className="dashboard-section">
        <h2>System Health</h2>
        <div className="health-cards">
          <div className="health-card">
            <div
              className="health-indicator"
              style={{ backgroundColor: getHealthColor(system.health) }}
            >
              {system.health.toUpperCase()}
            </div>
            <div className="health-details">
              <p><strong>Status:</strong> {system.health}</p>
              <p><strong>Uptime:</strong> {Math.floor(system.uptime_seconds / 3600)}h {Math.floor((system.uptime_seconds % 3600) / 60)}m</p>
              <p><strong>Connections:</strong> {system.active_connections}</p>
              <p><strong>Pending Jobs:</strong> {system.pending_jobs}</p>
            </div>
          </div>

          <div className="metric-card">
            <h3>Memory Usage</h3>
            <p className="big-number">{system.memory_percent.toFixed(1)}%</p>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{
                  width: `${system.memory_percent}%`,
                  backgroundColor: system.memory_percent > 80 ? '#ef4444' : '#22c55e'
                }}
              ></div>
            </div>
          </div>

          <div className="metric-card">
            <h3>CPU Usage</h3>
            <p className="big-number">{system.cpu_percent.toFixed(1)}%</p>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{
                  width: `${system.cpu_percent}%`,
                  backgroundColor: system.cpu_percent > 80 ? '#ef4444' : '#22c55e'
                }}
              ></div>
            </div>
          </div>
        </div>
      </section>

      {/* Key Metrics Section */}
      <section className="dashboard-section">
        <h2>Performance Metrics</h2>
        <div className="metrics-grid">
          {/* Latency Card */}
          <div className="metric-card large">
            <h3>Latency (ms)</h3>
            <div className="metric-details">
              <div className="metric-row">
                <span>Mean:</span>
                <strong>{latency.mean_ms.toFixed(1)}</strong>
              </div>
              <div className="metric-row">
                <span>P95:</span>
                <strong>{latency.p95_ms.toFixed(1)}</strong>
              </div>
              <div className="metric-row">
                <span>P99:</span>
                <strong className={latency.p99_ms > 10000 ? 'warning' : ''}>
                  {latency.p99_ms.toFixed(1)}
                </strong>
              </div>
              <div className="metric-row">
                <span>Max:</span>
                <strong>{latency.max_ms.toFixed(1)}</strong>
              </div>
              <div className="metric-subtext">Sample: {latency.sample_count} queries</div>
            </div>
          </div>

          {/* Error Rate Card */}
          <div className="metric-card large">
            <h3>Error Rate</h3>
            <p className="big-number" style={{ color: errors.error_rate_percent > 5 ? '#ef4444' : '#22c55e' }}>
              {errors.error_rate_percent.toFixed(2)}%
            </p>
            <div className="metric-details">
              <div className="metric-row">
                <span>Total Errors:</span>
                <strong>{errors.total_errors}</strong>
              </div>
              <div className="error-breakdown">
                {Object.entries(errors.errors_by_type).slice(0, 3).map(([type, count]) => (
                  <div key={type} className="error-type">
                    <span>{type}:</span> <strong>{count}</strong>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Cache Hit Rate Card */}
          <div className="metric-card large">
            <h3>Cache Performance</h3>
            <p className="big-number" style={{ color: cache.hit_rate_percent > 70 ? '#22c55e' : '#f59e0b' }}>
              {cache.hit_rate_percent.toFixed(1)}%
            </p>
            <div className="metric-details">
              <div className="metric-row">
                <span>Hits:</span>
                <strong>{cache.hits}</strong>
              </div>
              <div className="metric-row">
                <span>Misses:</span>
                <strong>{cache.misses}</strong>
              </div>
              <div className="metric-row">
                <span>Avg Hit Time:</span>
                <strong>{cache.avg_hit_time_ms.toFixed(2)}ms</strong>
              </div>
            </div>
          </div>

          {/* Cost Card */}
          <div className="metric-card large">
            <h3>Total Cost</h3>
            <p className="big-number cost-number">{formatCost(cost.total_cost)}</p>
            <div className="metric-details">
              <div className="metric-row">
                <span>Avg per Query:</span>
                <strong>{formatCost(cost.avg_cost_per_query)}</strong>
              </div>
              <div className="metric-row">
                <span>Max Query:</span>
                <strong>{formatCost(cost.max_cost)}</strong>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Cost Breakdown Charts */}
      <section className="dashboard-section">
        <h2>Cost Analysis</h2>
        <div className="charts-grid">
          {/* Cost by Role */}
          <div className="chart-container">
            <h3>Cost by Role</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={Object.entries(cost.cost_by_role || {}).map(([name, value]) => ({
                    name,
                    value
                  }))}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: $${value.toFixed(2)}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  <Cell fill="#3b82f6" />
                  <Cell fill="#8b5cf6" />
                  <Cell fill="#ec4899" />
                </Pie>
                <Tooltip formatter={(value) => formatCost(value)} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Cost by Organization */}
          <div className="chart-container">
            <h3>Cost by Organization</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={Object.entries(cost.cost_by_org || {}).map(([name, value]) => ({ name, cost: value }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => formatCost(value)} />
                <Bar dataKey="cost" fill="#10b981" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* Queue Metrics */}
      <section className="dashboard-section">
        <h2>Job Queue Status</h2>
        <div className="queue-metrics">
          <div className="metric-card">
            <h3>Queued Jobs</h3>
            <p className="big-number">{queue.waiting_count}</p>
            <p className="metric-subtext">Avg Wait: {queue.avg_wait_time_ms.toFixed(0)}ms</p>
          </div>
          <div className="metric-card">
            <h3>Processing Jobs</h3>
            <p className="big-number">{recent_activity.active_jobs_count || 0}</p>
            <p className="metric-subtext">Max Wait: {queue.max_wait_time_ms.toFixed(0)}ms</p>
          </div>
          <div className="metric-card">
            <h3>Processed Today</h3>
            <p className="big-number">{queue.processed_count}</p>
          </div>
        </div>
      </section>

      {/* Recent Activity */}
      <section className="dashboard-section">
        <h2>Recent Queries</h2>
        <div className="queries-table">
          <table>
            <thead>
              <tr>
                <th>Query ID</th>
                <th>Status</th>
                <th>Execution Time (ms)</th>
                <th>Rows</th>
                <th>Cost</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {recent_activity.recent_queries?.slice(0, 10).map((query) => (
                <tr key={query.query_id} onClick={() => setSelectedQuery(query)} className="clickable">
                  <td className="query-id">{query.query_id}</td>
                  <td>
                    <span className={`status-badge status-${query.status.toLowerCase()}`}>
                      {query.status}
                    </span>
                  </td>
                  <td>{query.execution_time_ms.toFixed(1)}</td>
                  <td>{query.rows_returned}</td>
                  <td>{formatCost(query.cost_score)}</td>
                  <td className="time-cell">
                    {new Date(query.submitted_at).toLocaleTimeString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Failed Queries */}
      {recent_activity.failed_queries?.length > 0 && (
        <section className="dashboard-section alert-section">
          <h2>⚠️ Failed Queries</h2>
          <div className="queries-table error-table">
            <table>
              <thead>
                <tr>
                  <th>Query ID</th>
                  <th>Error Type</th>
                  <th>Error Message</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {recent_activity.failed_queries.slice(0, 5).map((query) => (
                  <tr key={query.query_id}>
                    <td className="query-id">{query.query_id}</td>
                    <td>{query.error_type || 'Unknown'}</td>
                    <td className="error-message">{query.error_message}</td>
                    <td className="time-cell">
                      {new Date(query.submitted_at).toLocaleTimeString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Slow Queries */}
      {recent_activity.slow_queries?.length > 0 && (
        <section className="dashboard-section warning-section">
          <h2>🐢 Slow Queries (>1s)</h2>
          <div className="queries-table slow-table">
            <table>
              <thead>
                <tr>
                  <th>Query ID</th>
                  <th>Execution Time (ms)</th>
                  <th>Rows</th>
                  <th>User</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {recent_activity.slow_queries.slice(0, 5).map((query) => (
                  <tr key={query.query_id}>
                    <td className="query-id">{query.query_id}</td>
                    <td className="slow-time">{query.execution_time_ms.toFixed(1)}</td>
                    <td>{query.rows_returned}</td>
                    <td>{query.user_id}</td>
                    <td className="time-cell">
                      {new Date(query.submitted_at).toLocaleTimeString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Query Details Modal */}
      {selectedQuery && (
        <div className="modal" onClick={() => setSelectedQuery(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Query Details: {selectedQuery.query_id}</h2>
              <button className="close-button" onClick={() => setSelectedQuery(null)}>×</button>
            </div>
            <div className="modal-body">
              <div className="detail-group">
                <label>SQL:</label>
                <code>{selectedQuery.sql}</code>
              </div>
              <div className="detail-row">
                <div className="detail-col">
                  <label>Status:</label>
                  <p>{selectedQuery.status}</p>
                </div>
                <div className="detail-col">
                  <label>Organization:</label>
                  <p>{selectedQuery.org_id}</p>
                </div>
              </div>
              <div className="detail-row">
                <div className="detail-col">
                  <label>Execution Time:</label>
                  <p>{selectedQuery.execution_time_ms.toFixed(1)}ms</p>
                </div>
                <div className="detail-col">
                  <label>Rows Returned:</label>
                  <p>{selectedQuery.rows_returned}</p>
                </div>
              </div>
              <div className="detail-row">
                <div className="detail-col">
                  <label>Cost:</label>
                  <p>{formatCost(selectedQuery.cost_score)}</p>
                </div>
                <div className="detail-col">
                  <label>Cache Hit:</label>
                  <p>{selectedQuery.cache_hit ? 'Yes' : 'No'}</p>
                </div>
              </div>
              <div className="detail-group">
                <label>Submitted At:</label>
                <p>{new Date(selectedQuery.submitted_at).toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ObservabilityDashboard;
