import React from 'react';
import './ConnectionStatus.css';

interface ConnectionStatusProps {
  isOpen: boolean;
  status: 'connecting' | 'success' | 'error';
  message?: string;
  errorReason?: string;
  onClose: () => void;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({
  isOpen,
  status,
  message,
  errorReason,
  onClose,
}) => {
  if (!isOpen) return null;

  return (
    <div className="connection-status-overlay">
      <div className="connection-status-modal">
        {status === 'connecting' && (
          <>
            <div className="spinner"></div>
            <h2>🔄 Connecting...</h2>
            <p className="status-message">{message || 'Establishing connection to database'}</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="success-icon">✅</div>
            <h2>Connection Successful</h2>
            <p className="status-message">{message || 'Successfully connected to database'}</p>
            <button className="close-btn" onClick={onClose}>
              Continue
            </button>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="error-icon">❌</div>
            <h2>Unable to Connect</h2>
            <p className="status-message">Connection failed</p>
            <div className="error-reason">
              <strong>Reason:</strong>
              <p>{errorReason || 'Unknown error occurred'}</p>
            </div>
            <button className="close-btn error" onClick={onClose}>
              Try Again
            </button>
          </>
        )}
      </div>
    </div>
  );
};
