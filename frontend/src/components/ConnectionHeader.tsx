import React, { useState, useEffect } from 'react';
import './ConnectionHeader.css';

interface ConnectionHeaderProps {
  database?: string;
  host?: string;
  isConnected?: boolean;
}

function ConnectionHeader({ database = 'Snowflake', host = 'we08391.af-south-1.aws', isConnected = true }: ConnectionHeaderProps) {
  const displayDatabase = localStorage.getItem('selectedDatabase') || '';
  const displayHost = localStorage.getItem('dbHost') || '';
  const displayDatabaseName = localStorage.getItem('dbDatabase') || '';
  
  // Only show connected if we have a database name saved
  const isActuallyConnected = displayDatabaseName && displayDatabase;
  const displayStatus = isActuallyConnected ? 'connected' : 'disconnected';

  return (
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
        </div>
      </div>
    </div>
  );
}

export default ConnectionHeader;
