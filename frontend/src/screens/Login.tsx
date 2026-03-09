import React, { useState } from 'react';
import './Login.css';

interface LoginProps {
  onLogin?: () => void;
  isDemoMode?: boolean;
}

export const Login: React.FC<LoginProps> = ({ onLogin, isDemoMode = false }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showDemoDatabases, setShowDemoDatabases] = useState(false);
  const loginsLocked = !isDemoMode; // Only lock non-demo logins

  const demoDatabases = [
    { id: 'snowflake', name: 'Snowflake', description: 'Cloud Data Warehouse', icon: '❄️' },
    { id: 'sqlserver', name: 'SQL Server', description: 'Microsoft SQL Server', icon: '◆' },
    { id: 'semantic', name: 'Semantic Model', description: 'AI-Enhanced Semantic Layer', icon: '🧠' }
  ];

  const handleLogin = () => {
    if (loginsLocked) {
      return; // Do nothing if locked
    }
    setIsLoggedIn(true);
    if (onLogin) {
      onLogin();
    }
  };

  const handleDemodbSelect = () => {
    // In demo mode, clicking a database logs the user in
    setIsLoggedIn(true);
    if (onLogin) {
      onLogin();
    }
  };

  return (
    <div className="login-container">
      <div className="login-content">
        <img 
          src="/voxcore-landing-new.png"
          alt="VoxCore Logo"
          className="login-image login-image-small"
        />
        
        {isDemoMode && !showDemoDatabases ? (
          <div className="demo-welcome">
            <div className="demo-welcome-icon">🎯</div>
            <h3 className="demo-welcome-title">Welcome to VoxCore Demo</h3>
            <p className="demo-welcome-message">
              Explore VoxCore with locked demo databases. All features are visible but read-only.
            </p>
            <button 
              className="connect-demo-button" 
              onClick={() => setShowDemoDatabases(true)}
            >
              Connect Demo Database
            </button>
          </div>
        ) : isDemoMode && showDemoDatabases ? (
          <div className="demo-databases">
            <h3 style={{ 
              marginBottom: '24px', 
              color: '#fff', 
              textAlign: 'center', 
              fontSize: '18px',
              fontWeight: '600'
            }}>
              Select Demo Database
            </h3>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
              gap: '12px'
            }}>
              {demoDatabases.map(db => (
                <div 
                  key={db.id}
                  onClick={handleDemodbSelect}
                  style={{
                    background: 'rgba(20, 30, 50, 0.7)',
                    border: '2px solid rgba(100, 149, 255, 0.3)',
                    borderRadius: '12px',
                    padding: '16px',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    textAlign: 'center',
                    position: 'relative'
                  }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLElement).style.borderColor = '#6495ff';
                    (e.currentTarget as HTMLElement).style.backgroundColor = 'rgba(20, 30, 50, 0.9)';
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLElement).style.borderColor = 'rgba(100, 149, 255, 0.3)';
                    (e.currentTarget as HTMLElement).style.backgroundColor = 'rgba(20, 30, 50, 0.7)';
                  }}
                >
                  <div style={{ fontSize: '32px', marginBottom: '8px' }}>{db.icon}</div>
                  <div style={{ 
                    color: '#fff', 
                    fontWeight: '600', 
                    marginBottom: '4px',
                    fontSize: '14px'
                  }}>
                    {db.name}
                  </div>
                  <div style={{ 
                    color: '#888', 
                    fontSize: '12px',
                    marginBottom: '8px'
                  }}>
                    {db.description}
                  </div>
                  <div style={{
                    background: 'rgba(100, 149, 255, 0.1)',
                    border: '1px solid rgba(100, 149, 255, 0.3)',
                    borderRadius: '4px',
                    padding: '4px 8px',
                    fontSize: '11px',
                    color: '#6495ff',
                    fontWeight: '600'
                  }}>
                    🔒 Demo Mode
                  </div>
                </div>
              ))}
            </div>
            <button 
              className="browse-button"
              onClick={() => setShowDemoDatabases(false)}
              style={{ marginTop: '20px' }}
            >
              ← Back
            </button>
          </div>
        ) : loginsLocked ? (
          <div className="lockout-notice">
            <div className="lockout-icon">🔐</div>
            <h3 className="lockout-title">Logins Currently Locked</h3>
            <p className="lockout-message">
              Authentication is temporarily disabled. You can browse the governance dashboard to explore features.
            </p>
            <button 
              className="browse-button" 
              onClick={() => {
                setIsLoggedIn(true);
                if (onLogin) {
                  onLogin();
                }
              }}
            >
              Browse Dashboard
            </button>
          </div>
        ) : (
          <button 
            className="login-button" 
            onClick={handleLogin}
          >
            Enter VoxCore
          </button>
        )}
      </div>
    </div>
  );
};
