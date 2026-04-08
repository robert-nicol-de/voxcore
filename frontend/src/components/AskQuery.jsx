import React, { useState } from 'react';

import RiskBadge from './RiskBadge';
import { apiUrl } from '../lib/api';

export default function AskQuery() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleGenerateSQL = async () => {
    if (!question.trim()) return;
    
    setLoading(true);
    try {
      const session_id = localStorage.getItem('voxcore_session_id') || 'default';
      const response = await fetch(apiUrl('/api/v1/query'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question, session_id }),
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
      setResult({
        success: false,
        error: 'Failed to generate SQL. Please try again.',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleGenerateSQL();
    }
  };


  return (
    <div className="flex flex-col gap-8 w-full max-w-5xl mx-auto p-6">
      {/* Header */}
      <div className="mb-2">
        <h1 className="text-2xl font-bold text-primary mb-2">Ask a Question</h1>
        <p className="text-base text-muted mb-1">
          Describe what you want to know about your data. VoxCore will generate and validate the SQL.
        </p>
      </div>

      {/* Query Input */}
      <div className="flex flex-col">
        <div className="card bg-platform-card border border-platform-border rounded-xl p-6 flex flex-col gap-4">
          <textarea
            className="input w-full min-h-[90px] max-h-48 rounded-lg border border-platform-border bg-platform-input text-primary-content text-base focus:border-accent focus:ring-2 focus:ring-accent/20 placeholder:text-muted"
            rows={4}
            placeholder="Ask a question about your data... (e.g., 'Show me top 10 customers by total sales')"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <div className="flex items-center justify-between mt-1">
            <span className="text-xs text-muted">Ctrl+Enter to submit</span>
            <button
              className="primary-btn px-5 py-2 rounded-lg text-base font-semibold shadow-md"
              onClick={handleGenerateSQL}
              disabled={loading || !question.trim()}
            >
              {loading ? 'Generating...' : 'Generate SQL'}
            </button>
          </div>
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className="flex flex-col gap-4 animate-fade-in">
          {result.success ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* SQL Panel */}
              <div className="card bg-platform-card border border-platform-border rounded-xl p-6 flex flex-col gap-4">
                <div className="flex items-center justify-between gap-4 mb-2">
                  <h3 className="text-lg font-bold text-primary">Generated SQL</h3>
                  <RiskBadge level={getRiskLevel(result.risk_score)} />
                </div>
                <div className="bg-platform-input border border-platform-border rounded-lg p-4 overflow-x-auto">
                  <pre className="text-sm text-code m-0">{result.final_sql || result.generated_sql}</pre>
                </div>
                <div className="flex flex-col gap-1 mt-2">
                  <div className="flex gap-2 text-sm">
                    <span className="text-muted">Risk Score:</span>
                    <span className="font-semibold">{result.risk_score}/100</span>
                  </div>
                  {result.was_rewritten && (
                    <div className="flex gap-2 text-xs text-success">
                      <span>✓ Rewritten for platform</span>
                    </div>
                  )}
                  <div className="flex gap-2 text-sm">
                    <span className="text-muted">Execution Time:</span>
                    <span className="font-semibold">{result.execution_time_ms?.toFixed(2)}ms</span>
                  </div>
                </div>
              </div>

              {/* Results Panel */}
              <div className="card bg-platform-card border border-platform-border rounded-xl p-6 flex flex-col gap-4">
                <div className="flex items-center justify-between gap-4 mb-2">
                  <h3 className="text-lg font-bold text-primary">Results</h3>
                  {result.rows_returned && (
                    <span className="text-sm text-muted bg-platform-input px-3 py-1 rounded-md">{result.rows_returned} rows</span>
                  )}
                </div>
                {result.results && result.results.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse">
                      <thead>
                        <tr>
                          {Object.keys(result.results[0]).map((key) => (
                            <th key={key} className="text-xs text-muted font-semibold py-2 px-3 bg-platform-input border-b border-platform-border uppercase tracking-wider">{key}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {result.results.slice(0, 10).map((row, idx) => (
                          <tr key={idx}>
                            {Object.values(row).map((val, i) => (
                              <td key={i} className="text-sm text-primary-content py-2 px-3 border-b border-platform-border">{String(val)}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {result.results.length > 10 && (
                      <div className="text-xs text-muted mt-2">Showing 10 of {result.rows_returned} rows</div>
                    )}
                  </div>
                ) : (
                  <div className="text-center text-muted py-6">No results returned</div>
                )}
              </div>
            </div>
          ) : (
            <div className="card bg-error/10 border border-error/30 rounded-xl p-8 flex flex-col items-center gap-2 text-error text-center">
              <div className="text-3xl mb-2">⚠️</div>
              <h3 className="text-xl font-bold mb-1">
                {result.status === 'blocked' ? 'Operation Blocked' : 'Error'}
              </h3>
              <p className="text-base mb-1">{result.error}</p>
              {result.status === 'blocked' && (
                <p className="text-sm text-muted">This operation is not allowed for security reasons.</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function getRiskLevel(score) {
  if (score <= 30) return 'safe';
  if (score <= 70) return 'warning';
  return 'danger';
}
