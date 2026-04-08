/**
 * Operational Dashboard — Mission Control for VoxQuery
 * 
 * 4-Panel Layout:
 * 1. Health Status — System vitals at a glance
 * 2. Performance — Latency, throughput, cache
 * 3. Cost Tracking — By organization and query
 * 4. Governance — Policy violations, audit trail
 * 
 * Real-time updates via polling (every 5 seconds)
 */

import React, { useState, useEffect, useCallback } from "react";
import {
  Activity,
  AlertTriangle,
  TrendingUp,
  Shield,
  RefreshCw,
  ChevronDown,
  Zap,
  Clock,
  DollarSign,
  Users,
  Lock,
  Eye,
  Server,
  BarChart3,
} from "lucide-react";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function OperationalDashboard() {
  // State
  const [systemHealth, setSystemHealth] = useState(null);
  const [recentQueries, setRecentQueries] = useState([]);
  const [topCostQueries, setTopCostQueries] = useState([]);
  const [criticalAlerts, setCriticalAlerts] = useState([]);
  const [governanceMetrics, setGovernanceMetrics] = useState(null);
  const [expandedPanel, setExpandedPanel] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch all metrics
  const refreshMetrics = useCallback(async () => {
    setLoading(true);
    try {
      const [health, queries, costs, alerts, gov] = await Promise.all([
        fetch(`${API_BASE}/api/metrics/summary`).then((r) => r.json()),
        fetch(`${API_BASE}/api/metrics/queries/recent`).then((r) => r.json()),
        fetch(`${API_BASE}/api/metrics/queries/top-cost`).then((r) => r.json()),
        fetch(`${API_BASE}/api/metrics/alerts/critical`).then((r) => r.json()),
        fetch(`${API_BASE}/api/metrics/governance`).then((r) => r.json()),
      ]);

      setSystemHealth(health);
      setRecentQueries(queries);
      setTopCostQueries(costs);
      setCriticalAlerts(alerts);
      setGovernanceMetrics(gov);
      setLastRefresh(new Date());
    } catch (error) {
      console.error("Failed to refresh metrics:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-refresh every 5 seconds
  useEffect(() => {
    refreshMetrics();
    const interval = setInterval(refreshMetrics, 5000);
    return () => clearInterval(interval);
  }, [refreshMetrics]);

  if (!systemHealth) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-950">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-slate-300">Loading operational dashboard...</p>
        </div>
      </div>
    );
  }

  // Determine health color
  const getHealthColor = () => {
    if (systemHealth.error_rate > 10) return "from-red-600 to-red-900";
    if (systemHealth.error_rate > 5) return "from-yellow-600 to-yellow-900";
    return "from-green-600 to-green-900";
  };

  const getHealthText = () => {
    if (systemHealth.error_rate > 10) return "CRITICAL";
    if (systemHealth.error_rate > 5) return "DEGRADED";
    return "HEALTHY";
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Zap className="w-8 h-8 text-blue-500" />
            Mission Control
          </h1>
          <p className="text-sm text-slate-400 mt-1">VoxQuery Operational Hub</p>
        </div>
        <div className="text-right">
          <button
            onClick={refreshMetrics}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded flex items-center gap-2 text-sm disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
          <p className="text-xs text-slate-500 mt-2">
            Last: {lastRefresh ? lastRefresh.toLocaleTimeString() : "Never"}
          </p>
        </div>
      </div>

      {/* Critical Alerts Banner */}
      {criticalAlerts.length > 0 && (
        <div className="mb-6 p-4 bg-red-900/30 border-l-4 border-red-600 rounded">
          <div className="flex items-center gap-3 text-red-400">
            <AlertTriangle className="w-6 h-6" />
            <div>
              <p className="font-semibold">{criticalAlerts.length} Critical Alert(s)</p>
              <p className="text-sm text-red-300">{criticalAlerts[0]?.message}</p>
            </div>
          </div>
        </div>
      )}

      {/* Grid Layout: 2x2 Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Panel 1: Health Status */}
        <PanelHealth systemHealth={systemHealth} />

        {/* Panel 2: Performance Metrics */}
        <PanelPerformance systemHealth={systemHealth} />

        {/* Panel 3: Cost Tracking */}
        <PanelCost topCostQueries={topCostQueries} />

        {/* Panel 4: Governance Activity */}
        <PanelGovernance governanceMetrics={governanceMetrics} />
      </div>

      {/* Debug View: Recent Queries */}
      <div className="bg-slate-900 border border-slate-700 rounded-lg p-6">
        <div className="flex items-center gap-2 mb-4">
          <Eye className="w-5 h-5 text-blue-500" />
          <h2 className="text-lg font-semibold">Debug: Recent Queries</h2>
          <span className="text-xs px-2 py-1 bg-slate-800 rounded text-slate-300">
            Last 20
          </span>
        </div>

        {recentQueries.length === 0 ? (
          <p className="text-slate-400 text-sm">No queries yet</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-slate-400 border-b border-slate-700">
                <tr>
                  <th className="text-left py-2 px-3">Query ID</th>
                  <th className="text-right py-2 px-3">Latency (ms)</th>
                  <th className="text-right py-2 px-3">Cost Score</th>
                  <th className="text-right py-2 px-3">Rows</th>
                  <th className="text-center py-2 px-3">Status</th>
                  <th className="text-left py-2 px-3">User / Org</th>
                </tr>
              </thead>
              <tbody>
                {recentQueries.slice(0, 20).map((query) => (
                  <tr key={query.query_id} className="border-b border-slate-800 hover:bg-slate-800/50">
                    <td className="py-2 px-3 font-mono text-xs text-blue-400">
                      {query.query_id.substring(0, 12)}...
                    </td>
                    <td className="text-right py-2 px-3 text-slate-300">
                      {query.execution_time_ms.toFixed(0)}
                    </td>
                    <td className="text-right py-2 px-3">
                      <span
                        className={`px-2 py-1 rounded text-xs font-semibold ${
                          query.cost_score > 75
                            ? "bg-red-900/50 text-red-300"
                            : query.cost_score > 50
                            ? "bg-yellow-900/50 text-yellow-300"
                            : "bg-green-900/50 text-green-300"
                        }`}
                      >
                        {query.cost_score}
                      </span>
                    </td>
                    <td className="text-right py-2 px-3 text-slate-300">
                      {query.rows_returned}
                    </td>
                    <td className="text-center py-2 px-3">
                      <span
                        className={`inline-block w-2 h-2 rounded-full ${
                          query.status === "valid"
                            ? "bg-green-500"
                            : query.status === "warning"
                            ? "bg-yellow-500"
                            : "bg-red-500"
                        }`}
                      />
                    </td>
                    <td className="py-2 px-3 text-slate-400 text-xs">
                      {query.user_id.substring(0, 8)} / {query.org_id}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// PANEL COMPONENTS
// ============================================================================

function PanelHealth({ systemHealth }) {
  const isHealthy = systemHealth.error_rate < 5;
  const isDegraded = systemHealth.error_rate >= 5 && systemHealth.error_rate < 10;

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-6">
      <div className="flex items-center gap-3 mb-4">
        <Activity className="w-5 h-5 text-emerald-500" />
        <h2 className="text-lg font-semibold">System Health</h2>
      </div>

      {/* Status Indicator */}
      <div
        className={`
        p-4 rounded-lg mb-4 bg-gradient-to-r
        ${
          isHealthy
            ? "from-green-600/20 to-green-900/20 border border-green-600/50"
            : isDegraded
            ? "from-yellow-600/20 to-yellow-900/20 border border-yellow-600/50"
            : "from-red-600/20 to-red-900/20 border border-red-600/50"
        }
      `}
      >
        <p className={`text-2xl font-bold ${isHealthy ? "text-green-400" : isDegraded ? "text-yellow-400" : "text-red-400"}`}>
          {isHealthy ? "✓ HEALTHY" : isDegraded ? "⚠ DEGRADED" : "✕ CRITICAL"}
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="space-y-3">
        <MetricRow
          label="Error Rate"
          value={`${systemHealth.error_rate.toFixed(1)}%`}
          color={
            systemHealth.error_rate < 5
              ? "text-green-400"
              : systemHealth.error_rate < 10
              ? "text-yellow-400"
              : "text-red-400"
          }
          icon={AlertTriangle}
        />
        <MetricRow
          label="Avg Latency"
          value={`${systemHealth.avg_latency_ms.toFixed(0)}ms`}
          color={systemHealth.avg_latency_ms < 1000 ? "text-green-400" : "text-yellow-400"}
          icon={Clock}
        />
        <MetricRow
          label="Queue Depth"
          value={`${systemHealth.queue_depth} jobs`}
          color={systemHealth.queue_depth < 10 ? "text-green-400" : "text-yellow-400"}
          icon={Server}
        />
        <MetricRow
          label="Cache Hit Rate"
          value={`${systemHealth.cache_hit_rate.toFixed(1)}%`}
          color={systemHealth.cache_hit_rate > 50 ? "text-green-400" : "text-slate-400"}
          icon={Zap}
        />
      </div>
    </div>
  );
}

function PanelPerformance({ systemHealth }) {
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-6">
      <div className="flex items-center gap-3 mb-4">
        <BarChart3 className="w-5 h-5 text-cyan-500" />
        <h2 className="text-lg font-semibold">Performance</h2>
      </div>

      <div className="space-y-4">
        {/* Latency Distribution */}
        <div>
          <p className="text-sm text-slate-400 mb-2">Latency Distribution (Percentiles)</p>
          <div className="space-y-2">
            <PercentileBar
              label="Average"
              value={systemHealth.avg_latency_ms}
              max={5000}
            />
            <PercentileBar
              label="P95"
              value={systemHealth.p95_latency_ms}
              max={5000}
            />
            <PercentileBar
              label="P99"
              value={systemHealth.p99_latency_ms}
              max={5000}
            />
          </div>
        </div>

        {/* Throughput */}
        <div className="pt-4 border-t border-slate-700">
          <p className="text-sm text-slate-300">
            <span className="text-slate-400">Throughput:</span>{" "}
            <span className="font-semibold text-cyan-400">
              {systemHealth.throughput_qps.toFixed(1)} QPS
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}

function PanelCost({ topCostQueries }) {
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-6">
      <div className="flex items-center gap-3 mb-4">
        <DollarSign className="w-5 h-5 text-yellow-500" />
        <h2 className="text-lg font-semibold">Top Cost Queries</h2>
      </div>

      {topCostQueries.length === 0 ? (
        <p className="text-slate-400 text-sm">No data yet</p>
      ) : (
        <div className="space-y-2">
          {topCostQueries.slice(0, 5).map((query, i) => (
            <div key={query.query_id} className="flex items-center gap-3 p-2 bg-slate-800/50 rounded">
              <span className="text-lg font-bold text-slate-500 w-6">{i + 1}</span>
              <div className="flex-1 min-w-0">
                <p className="text-xs text-slate-400 truncate font-mono">
                  {query.query_id.substring(0, 20)}...
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-bold text-yellow-400">{query.cost_score}/100</p>
                <p className="text-xs text-slate-400">{query.execution_time_ms.toFixed(0)}ms</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function PanelGovernance({ governanceMetrics }) {
  if (!governanceMetrics) return null;

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-6">
      <div className="flex items-center gap-3 mb-4">
        <Shield className="w-5 h-5 text-purple-500" />
        <h2 className="text-lg font-semibold">Governance</h2>
      </div>

      <div className="space-y-3">
        <MetricRow
          label="Policies Triggered"
          value={governanceMetrics.policies_triggered}
          color="text-purple-400"
          icon={Lock}
        />
        <MetricRow
          label="Queries Blocked"
          value={governanceMetrics.policies_blocked}
          color={governanceMetrics.policies_blocked > 0 ? "text-red-400" : "text-green-400"}
          icon={Lock}
        />
        <MetricRow
          label="Columns Masked"
          value={governanceMetrics.columns_masked}
          color="text-blue-400"
          icon={Eye}
        />
        <MetricRow
          label="Cost Limit Hits"
          value={governanceMetrics.cost_limit_hits}
          color={governanceMetrics.cost_limit_hits > 0 ? "text-yellow-400" : "text-green-400"}
          icon={AlertTriangle}
        />
      </div>
    </div>
  );
}

// ============================================================================
// UTILITY COMPONENTS
// ============================================================================

function MetricRow({ label, value, color, icon: Icon }) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        {Icon && <Icon className={`w-4 h-4 ${color}`} />}
        <span className="text-slate-400 text-sm">{label}</span>
      </div>
      <span className={`font-semibold ${color}`}>{value}</span>
    </div>
  );
}

function PercentileBar({ label, value, max }) {
  const percentage = Math.min((value / max) * 100, 100);
  const barColor =
    percentage < 20 ? "bg-green-600" : percentage < 50 ? "bg-yellow-600" : "bg-red-600";

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-slate-400 w-12">{label}</span>
      <div className="flex-1 bg-slate-800 rounded h-6 overflow-hidden">
        <div
          className={`${barColor} h-full flex items-center justify-center transition-all`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-xs text-slate-300 w-12 text-right">
        {value.toFixed(0)}ms
      </span>
    </div>
  );
}
