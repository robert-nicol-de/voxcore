import React, { useState, useEffect } from 'react';
import './Sidebar.css';

interface SidebarProps {
  onClose?: () => void;
  onQuestionSelect?: (question: string) => void;
  onNavigate?: (view: 'dashboard' | 'query' | 'history' | 'logs' | 'policies' | 'schema') => void;
  currentView?: 'dashboard' | 'query' | 'history' | 'logs' | 'policies' | 'schema';
  isOpen?: boolean;
  onToggle?: () => void;
}

interface Question {
  id: string;
  text: string;
  custom?: boolean;
  pinned?: boolean;
}

function Sidebar({ onClose, onQuestionSelect, onNavigate, currentView, isOpen, onToggle }: SidebarProps) {
  const defaultQuestions: Question[] = [
    { id: '1', text: 'Show me sales trends' },
    { id: '2', text: 'What\'s the revenue by customer?' },
    { id: '3', text: 'Who are the top customers?' },
    { id: '4', text: 'Sales by region' },
    { id: '5', text: 'Show top 10 customers by revenue' },
    { id: '6', text: 'Monthly recurring revenue analysis' },
  ];

  const [questions, setQuestions] = useState<Question[]>(defaultQuestions);
  const [showSettings, setShowSettings] = useState(false);
  const [showNewQueryModal, setShowNewQueryModal] = useState(false);
  const [newQueryText, setNewQueryText] = useState('');
  const [selectedDatabase, setSelectedDatabase] = useState(() => {
    // Load last used database from localStorage
    return localStorage.getItem('lastUsedDatabase') || 'snowflake';
  });
  const [showDatabaseModal, setShowDatabaseModal] = useState(false);
  const [sqlServerAuthType, setSqlServerAuthType] = useState<'windows' | 'sql'>('windows');
  const [dbCredentials, setDbCredentials] = useState({
    host: '',
    username: '',
    password: '',
    database: '',
    port: ''
  });
  const [connectionStatus, setConnectionStatus] = useState<string>('');
  const [rememberMe, setRememberMe] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  // Check connection status on mount and when it changes
  useEffect(() => {
    const checkConnectionStatus = () => {
      const status = localStorage.getItem('dbConnectionStatus');
      const isConnected = status === 'connected';
      setIsConnected(isConnected);
      console.log('[Sidebar] Connection status updated:', isConnected);
    };

    checkConnectionStatus();

    // Listen for connection status changes
    const handleConnectionChange = (event: any) => {
      console.log('[Sidebar] connectionStatusChanged event received:', event.detail);
      checkConnectionStatus();
    };

    window.addEventListener('connectionStatusChanged', handleConnectionChange);
    return () => window.removeEventListener('connectionStatusChanged', handleConnectionChange);
  }, []);

  // Load saved credentials for selected database and last used database on mount
  useEffect(() => {
    // Load last used database
    const lastDb = localStorage.getItem('lastUsedDatabase') || 'snowflake';
    setSelectedDatabase(lastDb);

    // Load saved credentials for this database
    const saved = localStorage.getItem(`db_connection_${lastDb}`);
    const isRemembered = localStorage.getItem(`db_remember_${lastDb}`) === 'true';
    
    if (saved && isRemembered) {
      try {
        setDbCredentials(JSON.parse(saved));
        setRememberMe(true);
      } catch (error) {
        console.error('Error loading saved credentials:', error);
      }
    }
  }, []);

  // Load custom questions from localStorage on mount
  useEffect(() => {
    const savedQuestions = localStorage.getItem('customQuestions');
    const pinnedQuestions = localStorage.getItem('pinnedQuestions');
    let pinnedIds = [];
    
    if (pinnedQuestions) {
      try {
        pinnedIds = JSON.parse(pinnedQuestions);
      } catch (error) {
        console.error('Error loading pinned questions:', error);
      }
    }

    let allQuestions = defaultQuestions.map(q => ({
      ...q,
      pinned: pinnedIds.includes(q.id)
    }));

    if (savedQuestions) {
      try {
        const customQuestions = JSON.parse(savedQuestions);
        const customWithPins = customQuestions.map((q: Question) => ({
          ...q,
          pinned: pinnedIds.includes(q.id)
        }));
        allQuestions = [...allQuestions, ...customWithPins];
      } catch (error) {
        console.error('Error loading custom questions:', error);
      }
    }

    setQuestions(allQuestions);
  }, []);

  const addCustomQuestion = () => {
    if (!newQueryText.trim()) {
      alert('Please enter a query');
      return;
    }

    const newQuestion: Question = {
      id: `custom-${Date.now()}`,
      text: newQueryText,
      custom: true
    };

    const customQuestions = questions.filter(q => q.custom);
    customQuestions.push(newQuestion);

    // Save to localStorage
    localStorage.setItem('customQuestions', JSON.stringify(customQuestions));

    setQuestions([...defaultQuestions, ...customQuestions]);
    setNewQueryText('');
    setShowNewQueryModal(false);
  };

  const deleteCustomQuestion = (id: string) => {
    const customQuestions = questions.filter(q => q.custom && q.id !== id);
    localStorage.setItem('customQuestions', JSON.stringify(customQuestions));
    setQuestions(questions.filter(q => q.id !== id));
  };

  const togglePinQuestion = (id: string) => {
    const updatedQuestions = questions.map(q => 
      q.id === id ? { ...q, pinned: !q.pinned } : q
    );
    
    // Save pinned state to localStorage
    const pinnedIds = updatedQuestions
      .filter(q => q.pinned)
      .map(q => q.id);
    localStorage.setItem('pinnedQuestions', JSON.stringify(pinnedIds));
    
    setQuestions(updatedQuestions);
  };

  const getSortedQuestions = () => {
    return [...questions].sort((a, b) => {
      if (a.pinned === b.pinned) return 0;
      return a.pinned ? -1 : 1;
    });
  };

  const handleDatabaseSelect = (dbType: string) => {
    setSelectedDatabase(dbType);
    setShowDatabaseModal(true);
    // Reset credentials when opening modal for new database
    setDbCredentials({
      host: '',
      username: '',
      password: '',
      database: '',
      port: ''
    });
  };

  const handleDatabaseDropdownChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const dbType = e.target.value;
    if (dbType) {
      setSelectedDatabase(dbType);
      // Save last used database
      localStorage.setItem('lastUsedDatabase', dbType);
      
      // Load saved credentials for this database if they exist
      const saved = localStorage.getItem(`db_connection_${dbType}`);
      const isRemembered = localStorage.getItem(`db_remember_${dbType}`) === 'true';
      
      if (saved && isRemembered) {
        try {
          setDbCredentials(JSON.parse(saved));
          setRememberMe(true);
          setConnectionStatus(''); // Clear status when switching databases
        } catch (error) {
          console.error('Error loading credentials:', error);
          resetCredentials();
          setRememberMe(false);
        }
      } else {
        resetCredentials();
        setRememberMe(false);
      }
      
      // Don't close the modal - just update the selection
      // Modal stays open so user can continue with connection
    }
  };

  const resetCredentials = () => {
    setDbCredentials({
      host: '',
      username: '',
      password: '',
      database: '',
      port: ''
    });
  };

  const handleCredentialChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setDbCredentials(prev => ({
      ...prev,
      [name]: value,
      auth_type: sqlServerAuthType
    }));
  };

  const handleAuthTypeChange = (authType: 'windows' | 'sql') => {
    setSqlServerAuthType(authType);
    setDbCredentials(prev => ({
      ...prev,
      auth_type: authType
    }));
  };

  const handleTestConnection = async () => {
    // Validate required fields based on auth type
    if (sqlServerAuthType === 'windows') {
      if (!dbCredentials.host || !dbCredentials.database) {
        setConnectionStatus('❌ Please fill in Server and Database fields');
        return;
      }
    } else {
      if (!dbCredentials.host || !dbCredentials.username) {
        setConnectionStatus('❌ Please fill in Host and Username fields');
        return;
      }
    }

    setConnectionStatus('🔄 Testing connection...');

    try {
      // Send test connection request to backend
      const response = await fetch('http://localhost:8000/api/v1/auth/test-connection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          database: selectedDatabase,
          credentials: {
            ...dbCredentials,
            auth_type: sqlServerAuthType
          }
        })
      });

      if (response.ok) {
        setConnectionStatus(`✅ Successfully connected to ${selectedDatabase}!`);
      } else {
        const error = await response.json();
        setConnectionStatus(`❌ Connection failed: ${error.detail}`);
      }
    } catch (error) {
      setConnectionStatus(`❌ Error testing connection: ${error}`);
    }
  };

  const handleConnect = async () => {
    // Validate required fields based on auth type
    if (sqlServerAuthType === 'windows') {
      if (!dbCredentials.host || !dbCredentials.database) {
        setConnectionStatus('❌ Please fill in Server and Database fields');
        return;
      }
    } else {
      if (!dbCredentials.host || !dbCredentials.username) {
        setConnectionStatus('❌ Please fill in Host and Username fields');
        return;
      }
    }

    setConnectionStatus('🔄 Connecting...');

    try {
      // Call backend connect endpoint
      const response = await fetch('http://localhost:8000/api/v1/auth/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          database: selectedDatabase,
          credentials: {
            ...dbCredentials,
            auth_type: sqlServerAuthType
          }
        })
      });

      if (response.ok) {
        // Save to localStorage if "Remember Me" is checked
        if (rememberMe) {
          localStorage.setItem(
            `db_connection_${selectedDatabase}`,
            JSON.stringify(dbCredentials)
          );
          localStorage.setItem(
            `db_remember_${selectedDatabase}`,
            'true'
          );
        } else {
          // Clear saved credentials if "Remember Me" is unchecked
          localStorage.removeItem(`db_connection_${selectedDatabase}`);
          localStorage.removeItem(`db_remember_${selectedDatabase}`);
        }

        // Save last used database
        localStorage.setItem('lastUsedDatabase', selectedDatabase);

        // Save database and host info for ConnectionHeader
        localStorage.setItem('selectedDatabase', selectedDatabase);
        localStorage.setItem('dbHost', dbCredentials.host);
        localStorage.setItem('dbDatabase', dbCredentials.database);
        localStorage.setItem('dbConnectionStatus', 'connected');

        // Dispatch event to notify other components
        const event = new CustomEvent('connectionStatusChanged', {
          detail: { connected: true, database: selectedDatabase }
        });
        window.dispatchEvent(event);

        setConnectionStatus(`✅ Connected! Generated smart questions.`);
        
        // Generate smart questions based on schema
        generateSmartQuestions(selectedDatabase);
      } else {
        const error = await response.json();
        setConnectionStatus(`❌ Connection failed: ${error.detail}`);
      }
    } catch (error) {
      setConnectionStatus(`❌ Error connecting: ${error}`);
    }
  };

  const generateSmartQuestions = async (database: string) => {
    try {
      setConnectionStatus('🔄 Generating smart questions...');
      
      const response = await fetch('http://localhost:8000/api/v1/schema/generate-questions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          warehouse_type: database,
          limit: 8
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.questions && data.questions.length > 0) {
          // Convert generated questions to Question objects
          const generatedQuestions: Question[] = data.questions.map((q: string, idx: number) => ({
            id: `gen_${idx}`,
            text: q,
            custom: false,
            pinned: false
          }));
          
          // Keep custom questions, replace default ones with generated ones
          const customQuestions = questions.filter(q => q.custom);
          setQuestions([...generatedQuestions, ...customQuestions]);
          
          setConnectionStatus(`✅ Connected! Generated ${data.questions.length} smart questions.`);
        }
      } else {
        console.log('Could not generate smart questions');
        setConnectionStatus(`✅ Connected to ${database}!`);
      }
    } catch (error) {
      console.log('Error generating smart questions:', error);
      setConnectionStatus(`✅ Connected!`);
    }
  };

  const handleQuestionClick = (question: string) => {
    if (onQuestionSelect) {
      onQuestionSelect(question);
    }
    if (onNavigate) {
      onNavigate('query');
    }
  };

  return (
    <div className="sidebar-content">
      <div className="sidebar-header">
        <div className="voxcore-branding">
          <h1 className="voxcore-title">VoxCore</h1>
          <p className="voxcore-subtitle">GOVERNANCE</p>
        </div>
        <button className="new-chat-btn" onClick={() => setShowNewQueryModal(true)} title="Add Custom Query">+ New</button>
      </div>

      {/* Navigation Sections - Moved to Top */}
      <div className="sidebar-nav">
        <div className="nav-section">
          <button 
            className="nav-btn"
            onClick={() => {
              console.log('Clicked: dashboard');
              if (onNavigate) onNavigate('dashboard');
            }}
            title="Dashboard"
          >
            🏠 Dashboard
          </button>
          <button 
            className="nav-btn"
            onClick={() => {
              console.log('Clicked: query');
              if (onNavigate) onNavigate('query');
            }}
            title="Ask Query"
          >
            💬 Ask Query
          </button>
          <button 
            className="nav-btn"
            onClick={() => {
              console.log('Clicked: history');
              if (onNavigate) onNavigate('history');
            }}
            title="History"
          >
            📜 Query History
          </button>
        </div>

        <div className="nav-section">
          <h3 className="nav-section-title">Governance</h3>
          <button 
            className="nav-btn"
            onClick={() => {
              console.log('Clicked: logs');
              if (onNavigate) onNavigate('logs');
            }}
            title="Logs"
          >
            📋 Governance Logs
          </button>
          <button 
            className="nav-btn"
            onClick={() => {
              console.log('Clicked: policies');
              if (onNavigate) onNavigate('policies');
            }}
            title="Policies"
          >
            ⚙️ Policies
          </button>
        </div>

        <div className="nav-section">
          <h3 className="nav-section-title">Tools</h3>
          <button 
            className="nav-btn"
            onClick={() => {
              console.log('Clicked: schema');
              if (onNavigate) onNavigate('schema');
            }}
            title="Schema"
          >
            🔍 Schema Explorer
          </button>
        </div>
      </div>

      {currentView === 'query' && (
        <div className="conversations">
          {getSortedQuestions().map(q => (
            <div 
              key={q.id} 
              className={`conversation-item ${q.custom ? 'custom-question' : ''} ${q.pinned ? 'pinned-question' : ''}`}
              onClick={() => handleQuestionClick(q.text)}
            >
              <div className="conv-info">
                <p className="conv-name">{q.text}</p>
              </div>
              <div className="conv-actions">
                <button 
                  className={`conv-pin ${q.pinned ? 'pinned' : ''}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    togglePinQuestion(q.id);
                  }}
                  title={q.pinned ? 'Unpin question' : 'Pin question'}
                >
                  📌
                </button>
                {q.custom && (
                  <button 
                    className="conv-delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteCustomQuestion(q.id);
                    }}
                    title="Delete custom query"
                  >
                    ✕
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="sidebar-footer">
        <div className="connection-status-footer">
          {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
        </div>
      </div>



      {/* New Custom Query Modal */}
      {showNewQueryModal && (
        <div className="modal-overlay" onClick={() => setShowNewQueryModal(false)}>
          <div className="db-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>➕ New Custom Query</h2>
              <button className="modal-close" onClick={() => setShowNewQueryModal(false)}>✕</button>
            </div>

            <div className="modal-content">
              <div className="modal-form">
                <div className="form-group">
                  <label>Query Text *</label>
                  <textarea 
                    placeholder="Enter your custom query (e.g., 'Show me revenue by product category')"
                    value={newQueryText}
                    onChange={(e) => setNewQueryText(e.target.value)}
                    className="form-textarea"
                    rows={4}
                    autoFocus
                  />
                </div>
              </div>

              <div className="modal-actions">
                <button className="btn-save" onClick={addCustomQuestion}>
                  ➕ Add Query
                </button>
                <button className="btn-cancel" onClick={() => setShowNewQueryModal(false)}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Database Connection Modal */}
      {showDatabaseModal && (
        <div className="modal-overlay" onClick={() => setShowDatabaseModal(false)}>
          <div className="db-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>🔐 Database Connection</h2>
              <button className="modal-close" onClick={() => setShowDatabaseModal(false)}>✕</button>
            </div>

            <div className="modal-content">
              <div className="db-platform-badge">
                {selectedDatabase === 'snowflake' && '❄️ Snowflake'}
                {selectedDatabase === 'redshift' && '🔴 Redshift'}
                {selectedDatabase === 'postgres' && '🐘 PostgreSQL'}
                {selectedDatabase === 'bigquery' && '☁️ BigQuery'}
                {selectedDatabase === 'sqlserver' && '🟦 SQL Server'}
              </div>

              <div className="modal-form">
                <div className="form-group">
                  <label>Select Database Type *</label>
                  <select 
                    value={selectedDatabase} 
                    onChange={handleDatabaseDropdownChange}
                    className="form-select"
                  >
                    <option value="snowflake">❄️ Snowflake</option>
                    <option value="redshift">🔴 Redshift</option>
                    <option value="postgres">🐘 PostgreSQL</option>
                    <option value="bigquery">☁️ BigQuery</option>
                    <option value="sqlserver">🟦 SQL Server</option>
                  </select>
                </div>

                {selectedDatabase === 'sqlserver' && (
                  <div className="auth-type-selector">
                    <label>Authentication Type</label>
                    <div className="auth-options">
                      <button 
                        className={`auth-btn ${sqlServerAuthType === 'windows' ? 'active' : ''}`}
                        onClick={() => handleAuthTypeChange('windows')}
                      >
                        🪟 Windows Auth
                      </button>
                      <button 
                        className={`auth-btn ${sqlServerAuthType === 'sql' ? 'active' : ''}`}
                        onClick={() => handleAuthTypeChange('sql')}
                      >
                        🔑 SQL Server Auth
                      </button>
                    </div>
                  </div>
                )}

                <div className="form-group">
                  <label>Host / Server *
                    {selectedDatabase === 'snowflake' && (
                      <span className="label-hint">
                        e.g., we08391.sf-south-1.aws
                      </span>
                    )}
                    {selectedDatabase === 'redshift' && (
                      <span className="label-hint">
                        e.g., my-cluster.123456.us-east-1.redshift.amazonaws.com
                      </span>
                    )}
                    {selectedDatabase === 'postgres' && (
                      <span className="label-hint">
                        e.g., localhost or db.example.com
                      </span>
                    )}
                  </label>
                  <input 
                    type="text" 
                    name="host"
                    placeholder={
                      selectedDatabase === 'snowflake' ? 'e.g., we08391.sf-south-1.aws' :
                      selectedDatabase === 'redshift' ? 'e.g., my-cluster.redshift.amazonaws.com' :
                      selectedDatabase === 'postgres' ? 'e.g., localhost' :
                      selectedDatabase === 'bigquery' ? 'project_id' :
                      'server address'
                    }
                    value={dbCredentials.host}
                    onChange={handleCredentialChange}
                    className="form-input"
                    autoFocus
                  />
                </div>

                {sqlServerAuthType === 'sql' && (
                  <div className="form-group">
                    <label>Username *</label>
                    <input 
                      type="text" 
                      name="username"
                      placeholder="username"
                      value={dbCredentials.username}
                      onChange={handleCredentialChange}
                      className="form-input"
                    />
                  </div>
                )}

                {sqlServerAuthType === 'sql' && (
                  <>
                    <div className="form-group">
                      <label>Password</label>
                      <input 
                        type="password" 
                        name="password"
                        placeholder="Database password"
                        value={dbCredentials.password}
                        onChange={handleCredentialChange}
                        className="form-input"
                      />
                    </div>

                    <div className="form-group">
                      <label>Port (optional)</label>
                      <input 
                        type="text" 
                        name="port"
                        placeholder="1433"
                        value={dbCredentials.port}
                        onChange={handleCredentialChange}
                        className="form-input"
                      />
                    </div>
                  </>
                )}

                <div className="form-group">
                  <label>Database / Schema</label>
                  <input 
                    type="text" 
                    name="database"
                    placeholder="Database name"
                    value={dbCredentials.database}
                    onChange={handleCredentialChange}
                    className="form-input"
                  />
                </div>

                {selectedDatabase !== 'sqlserver' && (
                  <div className="form-group">
                    <label>Port (Optional)</label>
                    <input 
                      type="text" 
                      name="port"
                      placeholder="Port number"
                      value={dbCredentials.port}
                      onChange={handleCredentialChange}
                      className="form-input"
                    />
                  </div>
                )}

                <div className="form-group checkbox-group">
                  <label>
                    <input 
                      type="checkbox" 
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      className="form-checkbox"
                    />
                    <span>Remember me for this database</span>
                  </label>
                </div>
              </div>

              {connectionStatus && (
                <div className="connection-status">
                  {connectionStatus}
                </div>
              )}

              <div className="modal-actions">
                <button className="btn-test" onClick={handleTestConnection}>
                  🔗 Test Connection
                </button>
                <button className="btn-connect" onClick={handleConnect}>
                  ✅ Connect
                </button>
                <button className="btn-cancel" onClick={() => setShowDatabaseModal(false)}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Sidebar;
