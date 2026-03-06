import React, { useState } from 'react';
import './Login.css';

interface LoginProps {
  onLogin?: () => void;
}

export const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const loginsLocked = true; // Set to false to enable logins

  const handleLogin = () => {
    if (loginsLocked) {
      return; // Do nothing if locked
    }
    setIsLoggedIn(true);
    if (onLogin) {
      onLogin();
    }
  };

  return (
    <div className="login-container">
      <div className="login-content">
        <img 
          src="/voxcore-landing.png" 
          alt="VoxCore" 
          className="login-image"
        />
        
        {loginsLocked ? (
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
