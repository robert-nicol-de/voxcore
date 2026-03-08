import React, { useState, useEffect } from 'react';
import './ConnectionHeader.css';
import { ConnectionModal } from './ConnectionModal';

interface ConnectionHeaderProps {
  database?: string;
  host?: string;
  isConnected?: boolean;
  onDisconnect?: () => void;
  isPreviewMode?: boolean;
}

function ConnectionHeader({ database = 'Snowflake', host = 'we08391.af-south-1.aws', isConnected = true, onDisconnect, isPreviewMode = false }: ConnectionHeaderProps) {
  const [showConnectionModal, setShowConnectionModal] = useState(false);
  const displayDatabase = localStorage.getItem('selectedDatabase') || '';
  const displayHost = localStorage.getItem('dbHost') || '';
  const displayDatabaseName = localStorage.getItem('dbDatabase') || '';
  
  // Only show connected if we have a database name saved
  const isActuallyConnected = displayDatabaseName && displayDatabase;
  const displayStatus = isActuallyConnected ? 'connected' : 'disconnected';

  // Update localStorage connection status whenever it changes
  useEffect(() => {
    if (isActuallyConnected) {
      localStorage.setItem('dbConnectionStatus', 'connected');
    } else {
      localStorage.removeItem('dbConnectionStatus');
    }
    // Dispatch event to notify other components
    window.dispatchEvent(new Event('connectionStatusChanged'));
  }, [isActuallyConnected]);

  const handleDisconnect = () => {
    // Clear connection info from localStorage
    localStorage.removeItem('selectedDatabase');
    localStorage.removeItem('dbHost');
    localStorage.removeItem('dbDatabase');
    localStorage.removeItem('dbSchema');
    localStorage.removeItem('dbConnectionStatus');
    
    // Dispatch event to notify other components (Chat, etc.)
    window.dispatchEvent(new Event('connectionStatusChanged'));
    
    // Call the onDisconnect callback to navigate back to dashboard
    if (onDisconnect) {
      onDisconnect();
    }
  };

  return (
    <>
      <ConnectionModal 
        isOpen={showConnectionModal}
        onClose={() => setShowConnectionModal(false)}
        onConnect={() => {
          setShowConnectionModal(false);
        }}
      />
      <div className="connection-header">
        <div className="header-content">
          <div className="voxquery-info">
            <h1>VoxQuery</h1>
            <p>Natural Language SQL Assistant</p>
          </div>
          <div className="connection-info">
            <div className="server-details">
              {isActuallyConnected ? (
                <>
                  <div className="detail-item">
                    <span className="label">🗄️</span>
                    <span className="value">{displayDatabase}</span>
                  </div>
                  {displayDatabaseName && (
                    <div className="detail-item">
                      <span className="label">📊</span>
                      <span className="value">{displayDatabaseName}</span>
                    </div>
                  )}
                  <div className="detail-item">
                    <span className="label">🖥️</span>
                    <span className="value">{displayHost}</span>
                  </div>
                </>
              ) : null}
              <div className="detail-item">
                <span className={`status ${displayStatus}`}>
                  <span className="dot"></span>
                  {displayStatus === 'connected' ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
            {isActuallyConnected ? (
              <button className="disconnect-btn" onClick={handleDisconnect} title="Disconnect from database" disabled={isPreviewMode}>
                🔌 Disconnect
              </button>
            ) : (
              <>
                <button 
                  className="connect-btn" 
                  onClick={() => setShowConnectionModal(true)} 
                  title={isPreviewMode ? "Login required to connect a database" : "Connect to database"}
                  disabled={isPreviewMode}
                >
                  🔗 Connect
                </button>
                {isPreviewMode && <p className="preview-note">Login required to connect a database</p>}
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default ConnectionHeader;
