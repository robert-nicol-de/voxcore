import React, { useState } from 'react';
import './AskQuery.css';
import RiskBadge from './RiskBadge';

export default function AskQuery() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleGenerateSQL = async () => {
    if (!question.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
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
    <div className="ask-query-container">
      {/* Header */}
      <div className="query-header">
        <h1 className="query-title">Ask a Question</h1>
        <p className="query-subtitle">
          Describe what you want to know about your data. VoxCore will generate and validate the SQL.
        </p>
      </div>

      {/* Query Input */}
      <div className="query-input-section">
        <div className="query-input-box">
          <textarea
            className="query-textarea"
            rows="4"
            placeholder="Ask a question about your data... (e.g., 'Show me top 10 customers by total sales')"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <div className="query-input-footer">
            <span className="input-hint">Ctrl+Enter to submit</span>
            <button
              className="generate-button"
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
        <div className="results-section">
          {result.success ? (
            <div className="results-grid">
              {/* SQL Panel */}
              <div className="result-panel sql-panel">
                <div className="panel-header">
                  <h3 className="panel-title">Generated SQL</h3>
                  <RiskBadge level={getRiskLevel(result.risk_score)} />
                </div>
                
                <div className="sql-display">
                  <pre className="sql-code">{result.final_sql || result.generated_sql}</pre>
                </div>

                <div className="panel-metadata">
                  <div className="metadata-item">
                    <span className="metadata-label">Risk Score:</span>
                    <span className="metadata-value">{result.risk_score}/100</span>
                  </div>
                  {result.was_rewritten && (
                    <div className="metadata-item rewritten">
                      <span className="metadata-label">✓ Rewritten for platform</span>
                    </div>
                  )}
                  <div className="metadata-item">
                    <span className="metadata-label">Execution Time:</span>
                    <span className="metadata-value">{result.execution_time_ms?.toFixed(2)}ms</span>
                  </div>
                </div>
              </div>

              {/* Results Panel */}
              <div className="result-panel results-panel">
                <div className="panel-header">
                  <h3 className="panel-title">Results</h3>
                  {result.rows_returned && (
                    <span className="result-count">{result.rows_returned} rows</span>
                  )}
                </div>

                {result.results && result.results.length > 0 ? (
                  <div className="results-table">
                    <table>
                      <thead>
                        <tr>
                          {Object.keys(result.results[0]).map((key) => (
                            <th key={key}>{key}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {result.results.slice(0, 10).map((row, idx) => (
                          <tr key={idx}>
                            {Object.values(row).map((val, i) => (
                              <td key={i}>{String(val)}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {result.results.length > 10 && (
                      <div className="results-footer">
                        Showing 10 of {result.rows_returned} rows
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="empty-results">
                    <p>No results returned</p>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="error-panel">
              <div className="error-icon">⚠️</div>
              <h3 className="error-title">
                {result.status === 'blocked' ? 'Operation Blocked' : 'Error'}
              </h3>
              <p className="error-message">{result.error}</p>
              {result.status === 'blocked' && (
                <p className="error-hint">
                  This operation is not allowed for security reasons.
                </p>
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
