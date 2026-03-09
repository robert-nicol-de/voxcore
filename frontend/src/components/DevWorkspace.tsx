import React, { useState } from 'react';
import './DevWorkspace.css';
import SensitivityScanner from './DevConsole/SensitivityScanner';

interface DevWorkspaceProps {
  onClose?: () => void;
}

export const DevWorkspace: React.FC<DevWorkspaceProps> = ({ onClose }) => {
  const [sqlQuery, setSqlQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [tables, setTables] = useState([
    'customers', 'orders', 'products', 'employees', 'departments'
  ]);
  const [activeTab, setActiveTab] = useState<'editor' | 'scanner'>('editor');
  
  // Sample schema for scanner demo
  const [sampleSchema] = useState([
    {
      table_name: 'users',
      columns: ['id', 'username', 'email', 'password', 'phone_number', 'date_of_birth']
    },
    {
      table_name: 'payments',
      columns: ['id', 'user_id', 'card_number', 'cvv', 'expiry_date', 'amount']
    },
    {
      table_name: 'employees',
      columns: ['id', 'name', 'email', 'ssn', 'salary', 'department']
    }
  ]);

  const handleRunQuery = async () => {
    if (!sqlQuery.trim()) {
      setError('Enter a SQL query');
      return;
    }

    setLoading(true);
    setError('');
    setResults([]);

    try {
      // TODO: Connect to actual API endpoint
      // For now, show mock results
      setTimeout(() => {
        setResults([
          { id: 1, column1: 'value1', column2: 'value2' },
          { id: 2, column1: 'value3', column2: 'value4' },
        ]);
        setLoading(false);
      }, 800);
    } catch (err) {
      setError('Query execution failed');
      setLoading(false);
    }
  };

  const clearQuery = () => {
    setSqlQuery('');
    setResults([]);
    setError('');
  };

  return (
    <div className="dev-workspace">
      {/* Workspace Tabs */}
      <div className="workspace-tabs">
        <button 
          className={`tab-button ${activeTab === 'editor' ? 'active' : ''}`}
          onClick={() => setActiveTab('editor')}
        >
          ⚙️ SQL Editor
        </button>
        <button 
          className={`tab-button ${activeTab === 'scanner' ? 'active' : ''}`}
          onClick={() => setActiveTab('scanner')}
        >
          📊 Sensitivity Scanner
        </button>
      </div>

      <div className="dev-layout">
        {/* Editor View */}
        {activeTab === 'editor' && (
          <>
            {/* Schema Explorer Panel */}
            <div className="schema-panel">
              <div className="schema-header">
                <h3>📊 Schema Explorer</h3>
              </div>
              <div className="tables-list">
                <h4>Tables</h4>
                {tables.map((table) => (
                  <div
                    key={table}
                    className="table-item"
                    onClick={() => setSqlQuery(prev => `${prev}${prev ? '\n' : ''}SELECT * FROM ${table}`)}
                    title={`Click to add table to query`}
                  >
                    📋 {table}
                  </div>
                ))}
              </div>
              <div className="schema-info">
                <p style={{ fontSize: '12px', color: '#888', marginTop: '20px' }}>
                  Click a table to add it to your query.
                </p>
              </div>
            </div>

            {/* SQL Editor & Results */}
            <div className="sql-workspace">
          <div className="editor-header">
            <h3>⚙️ SQL Editor</h3>
            <div className="editor-actions">
              <button 
                className="btn btn-primary"
                onClick={handleRunQuery}
                disabled={loading}
              >
                {loading ? '⏳ Running...' : '▶ Run Query'}
              </button>
              <button 
                className="btn btn-secondary"
                onClick={clearQuery}
              >
                🔄 Clear
              </button>
            </div>
          </div>

          {/* SQL Input */}
          <div className="editor-section">
            <textarea
              className="sql-editor"
              value={sqlQuery}
              onChange={(e) => setSqlQuery(e.target.value)}
              placeholder="SELECT * FROM customers WHERE id > 100;&#10;&#10;Tips:&#10;- Click table names on the left to add them&#10;- Use standard SQL syntax&#10;- Press Ctrl+Enter to run"
              spellCheck="false"
            />
          </div>

          {/* Error Display */}
          {error && (
            <div className="error-box">
              <span>❌ {error}</span>
            </div>
          )}

          {/* Results */}
          <div className="results-section">
            <div className="results-header">
              <h4>Query Results</h4>
              {results.length > 0 && (
                <span className="result-count">{results.length} rows</span>
              )}
            </div>

            {loading && (
              <div className="loading">
                ⏳ Executing query...
              </div>
            )}

            {!loading && results.length === 0 && !error && (
              <div className="placeholder">
                Results will appear here
              </div>
            )}

            {!loading && results.length > 0 && (
              <div className="results-table">
                <table>
                  <thead>
                    <tr>
                      {Object.keys(results[0]).map((key) => (
                        <th key={key}>{key}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((row, idx) => (
                      <tr key={idx}>
                        {Object.values(row).map((val: any, cellIdx) => (
                          <td key={cellIdx}>{String(val)}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
        </>
        )}

        {/* Scanner View */}
        {activeTab === 'scanner' && (
          <div className="scanner-container">
            <SensitivityScanner 
              connectorName="VoxQuery_Demo"
              schemaInfo={sampleSchema}
            />
          </div>
        )}
      </div>
    </div>
  );
};
