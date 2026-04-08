import React, { useState, useEffect } from "react";
import { useQueryExecution } from "../hooks/useQueryExecution";

export function QueryExecutionDemo() {
  const {
    query,
    status,
    result,
    error,
    riskScore,
    confidence,
    analysisTime,
    reasons,
    rewrittenQuery,
    isBlocked,
    isPendingApproval,
    queryHash,
    auditLogs,
    currentUser,
    currentEnvironment,
    currentSource,
    setQuery,
    run,
    approve,
    reset,
    clearAuditLogs,
    setEnvironment,
    setSource,
    hydrateAuditLogs,
  } = useQueryExecution();

  const [showAuditLog, setShowAuditLog] = useState(false);
  const [displayRisk, setDisplayRisk] = useState(0);

  // Load audit logs from backend on mount
  useEffect(() => {
    hydrateAuditLogs("default-org");
  }, [hydrateAuditLogs]);

  // Risk score animation
  useEffect(() => {
    if (riskScore !== null && riskScore > 0) {
      let current = 0;
      const interval = setInterval(() => {
        current += Math.ceil(riskScore / 10);
        if (current >= riskScore) {
          setDisplayRisk(riskScore);
          clearInterval(interval);
        } else {
          setDisplayRisk(current);
        }
      }, 30);
      return () => clearInterval(interval);
    }
  }, [riskScore]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      await run(query);
    }
  };

  const getConfidenceLevel = (conf: number | null) => {
    if (!conf) return { text: "Medium", color: "text-yellow-400" };
    if (conf > 0.8) return { text: "High", color: "text-green-400" };
    if (conf > 0.6) return { text: "Medium", color: "text-yellow-400" };
    return { text: "Low", color: "text-red-400" };
  };

  const confidenceLevel = getConfidenceLevel(confidence);

  const getRiskColor = (score: number) => {
    if (score >= 81) return "text-red-400";
    if (score >= 61) return "text-orange-400";
    if (score >= 31) return "text-yellow-400";
    return "text-green-400";
  };

  return (
    <div className="min-h-screen bg-[#0B0F19] text-white">
      {/* Header */}
      <div className="border-b border-white/10 bg-[#0B0F19]/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold">VoxCore Governance</h1>
              <p className="text-sm text-gray-400">Real-time Query Analysis & Risk Assessment</p>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowAuditLog(!showAuditLog)}
                className="px-4 py-2 rounded-lg border border-blue-500/30 text-sm hover:border-blue-500/60 transition"
              >
                📋 Audit Log ({auditLogs.length})
              </button>
              <button
                onClick={reset}
                className="px-4 py-2 rounded-lg border border-white/10 text-sm hover:border-white/30 transition"
              >
                Reset
              </button>
            </div>
          </div>

          {/* Execution Context Controls */}
          <div className="flex items-center gap-6">
            <div>
              <label className="text-xs text-gray-500 block mb-1">Environment</label>
              <select
                value={currentEnvironment}
                onChange={(e) => setEnvironment(e.target.value as any)}
                className="px-3 py-1 rounded text-sm bg-white/10 border border-white/20 hover:border-blue-500/50 transition"
              >
                <option value="dev">Dev</option>
                <option value="staging">Staging</option>
                <option value="prod">Prod</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-500 block mb-1">Source</label>
              <select
                value={currentSource}
                onChange={(e) => setSource(e.target.value as any)}
                className="px-3 py-1 rounded text-sm bg-white/10 border border-white/20 hover:border-blue-500/50 transition"
              >
                <option value="playground">Playground</option>
                <option value="api">API</option>
                <option value="dashboard">Dashboard</option>
              </select>
            </div>
            <div className="ml-auto">
              <p className="text-xs text-gray-500 mb-1">Current User</p>
              <p className="text-sm text-blue-400 font-mono">{currentUser}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Input Section */}
          <div className="lg:col-span-2 space-y-6">
            {/* Query Input */}
            <div>
              <label className="block text-sm font-semibold mb-3">SQL Query</label>
              <form onSubmit={handleSubmit} className="space-y-3">
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="SELECT * FROM users WHERE active = true ORDER BY created_at DESC"
                  className="w-full bg-[#111827] border border-white/10 rounded-lg p-4 text-white placeholder-gray-500 focus:border-blue-500/50 focus:outline-none font-mono text-sm"
                  rows={6}
                />
                <button
                  type="submit"
                  disabled={status === "analyzing" || !query.trim()}
                  className={`w-full py-3 rounded-lg font-medium transition ${
                    status === "analyzing"
                      ? "bg-gray-600 cursor-not-allowed"
                      : "bg-blue-600 hover:bg-blue-700 active:bg-blue-800"
                  }`}
                >
                  {status === "analyzing" ? "🔍 Analyzing..." : "Analyze Query"}
                </button>
              </form>
            </div>

            {/* Status Messages */}
            {status === "analyzing" && (
              <div className="bg-yellow-600/10 border border-yellow-500/30 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <div className="animate-spin text-yellow-400">⚙️</div>
                  <div>
                    <p className="font-semibold text-yellow-400">Analyzing Query</p>
                    <p className="text-sm text-yellow-300">Running governance assessment...</p>
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="bg-red-600/10 border border-red-500/30 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <div className="text-red-400 text-xl">⚠️</div>
                  <div>
                    <p className="font-semibold text-red-400">Error</p>
                    <p className="text-sm text-red-300">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Results */}
            {result && status === "done" && (
              <div className="space-y-4">
                {/* Risk Assessment Card with Glow */}
                <div
                  className={`rounded-lg border p-6 transition-all ${
                    isBlocked
                      ? "bg-red-600/10 border-red-500/30"
                      : isPendingApproval
                      ? "bg-orange-600/10 border-orange-500/30"
                      : "bg-green-600/10 border-green-500/30"
                  }`}
                  style={{
                    boxShadow:
                      status === "done"
                        ? `0 0 20px ${
                            isBlocked
                              ? "rgba(239, 68, 68, 0.4)"
                              : isPendingApproval
                              ? "rgba(251, 146, 60, 0.4)"
                              : "rgba(34, 197, 94, 0.4)"
                          }`
                        : "none",
                  }}
                >
                  {/* Decision Moment - Bigger, Clearer, More Decisive */}
                  <div className="mb-6 pb-6 border-b border-white/10">
                    <p className="text-gray-400 text-sm mb-2">Decision</p>
                    <p
                      className={`text-4xl font-bold leading-tight ${
                        isBlocked
                          ? "text-red-400"
                          : isPendingApproval
                          ? "text-orange-400"
                          : "text-green-400"
                      }`}
                    >
                      {isBlocked
                        ? "🚫 Query Blocked"
                        : isPendingApproval
                        ? "⏳ Approval Required"
                        : "✅ Query Approved"}
                    </p>
                  </div>

                  <div className="grid grid-cols-3 gap-6 mb-6">
                    <div>
                      <p className="text-gray-400 text-sm mb-2">Risk Score</p>
                      <p className={`text-4xl font-bold ${getRiskColor(displayRisk || 0)}`}>
                        {displayRisk || 0}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-sm mb-2">Confidence</p>
                      <p className={`text-2xl font-bold ${confidenceLevel.color}`}>
                        {confidenceLevel.text}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-sm mb-2">Analysis Time</p>
                      <p className="text-2xl font-bold text-blue-400">{analysisTime}ms</p>
                    </div>
                  </div>

                  {/* Query Metadata */}
                  <div className="grid grid-cols-2 gap-4 mb-6 pb-6 border-b border-white/10">
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Query ID</p>
                      <p className="text-xs text-gray-300 font-mono">{queryHash}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Fingerprint</p>
                      <p className="text-xs text-gray-300 font-mono">{result.fingerprint}</p>
                    </div>
                  </div>

                  {/* Reasons */}
                  {reasons && reasons.length > 0 && (
                    <div className="mb-6">
                      <p className="text-sm font-semibold mb-3 text-gray-300">Risk Factors:</p>
                      <ul className="space-y-2">
                        {reasons.map((reason, i) => (
                          <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                            <span className="text-orange-400 mt-0.5">•</span>
                            <span>{reason}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Approval Button (for pending) */}
                  {isPendingApproval && queryHash && (
                    <div className="pt-6 border-t border-white/10">
                      <button
                        onClick={() => approve(queryHash)}
                        className="w-full py-3 px-4 rounded-lg bg-yellow-500 hover:bg-yellow-600 text-black font-semibold transition active:bg-yellow-700"
                      >
                        ✓ Approve Query
                      </button>
                    </div>
                  )}
                </div>

                {/* Rewrite Visualization */}
                {rewrittenQuery && rewrittenQuery !== query && (
                  <div className="bg-[#111827] border border-white/10 rounded-lg p-6">
                    <p className="text-sm font-semibold mb-4 text-gray-300">Query Optimization</p>
                    <div className="space-y-3">
                      <div>
                        <p className="text-xs text-gray-500 mb-1">Original</p>
                        <pre className="bg-red-600/10 border border-red-500/20 rounded p-3 text-xs text-gray-300 font-mono overflow-x-auto">
                          {query}
                        </pre>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 mb-1">Optimized</p>
                        <pre className="bg-green-600/10 border border-green-500/20 rounded p-3 text-xs text-gray-300 font-mono overflow-x-auto">
                          {rewrittenQuery}
                        </pre>
                      </div>
                    </div>
                  </div>
                )}

                {/* Data Preview */}
                {result.data && (
                  <div className="bg-[#111827] border border-white/10 rounded-lg p-6">
                    <p className="text-sm font-semibold mb-3 text-gray-300">Data Preview</p>
                    <pre className="text-xs text-gray-400 overflow-x-auto max-h-64 font-mono">
                      {JSON.stringify(result.data, null, 2).slice(0, 500)}...
                    </pre>
                  </div>
                )}

                {/* Suggestions */}
                {result.suggestions && result.suggestions.length > 0 && (
                  <div className="bg-[#111827] border border-white/10 rounded-lg p-6">
                    <p className="text-sm font-semibold mb-3 text-gray-300">Exploration Suggestions</p>
                    <ul className="space-y-2">
                      {result.suggestions.map((suggestion, i) => (
                        <li
                          key={i}
                          className="text-sm text-blue-400 hover:text-blue-300 cursor-pointer hover:underline"
                          onClick={() => setQuery(suggestion)}
                        >
                          • {suggestion}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Sidebar: Stats & Audit Log */}
          <div className="space-y-6">
            {/* Query Stats */}
            <div className="bg-[#111827] border border-white/10 rounded-lg p-6">
              <p className="text-sm font-semibold mb-4 text-gray-300">Stats</p>
              <div className="space-y-3">
                <div>
                  <p className="text-xs text-gray-500 mb-1">Queries Analyzed</p>
                  <p className="text-3xl font-bold text-blue-400">{auditLogs.length}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Blocked</p>
                  <p className="text-2xl font-bold text-red-400">
                    {auditLogs.filter((l) => l.status === "blocked").length}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Pending Approval</p>
                  <p className="text-2xl font-bold text-orange-400">
                    {auditLogs.filter((l) => l.status === "pending_approval").length}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Allowed</p>
                  <p className="text-2xl font-bold text-green-400">
                    {auditLogs.filter((l) => l.status === "allowed").length}
                  </p>
                </div>
              </div>
            </div>

            {/* Quick Queries */}
            <div className="bg-[#111827] border border-white/10 rounded-lg p-6">
              <p className="text-sm font-semibold mb-3 text-gray-300">Quick Queries</p>
              <div className="space-y-2">
                {[
                  "SELECT COUNT(*) FROM users",
                  "SELECT * FROM orders WHERE status = 'pending'",
                  "SELECT SUM(amount) FROM transactions",
                ].map((q, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setQuery(q);
                      setTimeout(() => run(q), 100);
                    }}
                    className="w-full text-left text-xs p-2 rounded border border-white/10 hover:border-blue-500/50 hover:bg-blue-600/10 transition"
                  >
                    {q.slice(0, 30)}...
                  </button>
                ))}
              </div>
            </div>

            {/* Audit Log Sidebar */}
            {showAuditLog && (
              <div className="bg-[#111827] border border-white/10 rounded-lg p-6">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-sm font-semibold text-gray-300">Audit Log</p>
                  <button
                    onClick={clearAuditLogs}
                    className="text-xs px-2 py-1 rounded border border-white/10 hover:border-red-500/50 text-gray-400 hover:text-red-400 transition"
                  >
                    Clear
                  </button>
                </div>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {auditLogs.length === 0 ? (
                    <p className="text-xs text-gray-500">No queries yet</p>
                  ) : (
                    auditLogs.map((log) => (
                      <div key={log.id} className="text-xs p-2 rounded bg-white/5 border border-white/10">
                        <p className="font-mono text-gray-300 mb-1 truncate" title={log.query}>
                          {log.query.slice(0, 35)}...
                        </p>
                        <div className="flex items-center justify-between">
                          <span
                            className={`text-xs font-semibold ${
                              log.status === "blocked"
                                ? "text-red-400"
                                : log.status === "pending_approval"
                                ? "text-orange-400"
                                : log.status === "allowed"
                                ? "text-green-400"
                                : "text-yellow-400"
                            }`}
                          >
                            {log.status.toUpperCase()} ({log.riskScore})
                          </span>
                        </div>
                        <div className="flex items-center justify-between mt-1 text-gray-500 text-xs">
                          <span>{log.hash}</span>
                          <span>{new Date(log.timestamp).toLocaleTimeString()}</span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
