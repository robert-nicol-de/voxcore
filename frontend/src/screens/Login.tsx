import React, { useState } from 'react';
import './Login.css';

interface LoginProps {
  onLogin?: (userName?: string) => void;
  isDemoMode?: boolean;
}

export const Login: React.FC<LoginProps> = ({ onLogin, isDemoMode = false }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // Validate input before submitting
    if (!email.trim()) {
      setError('Please enter your email address');
      return;
    }
    if (!password.trim()) {
      setError('Please enter your password');
      return;
    }
    if (email.trim().length < 5 || !email.includes('@')) {
      setError('Please enter a valid email address');
      return;
    }
    
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: email.trim().toLowerCase(), password }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || 'Invalid email or password');
      }

      const data = await response.json();
      
      // Validate response has required token
      if (!data.access_token) {
        throw new Error('Authentication failed: No token received');
      }
      
      // Store token & user info
      localStorage.setItem('voxcore_token', data.access_token);
      if (data.user_name) localStorage.setItem('voxcore_user_name', data.user_name);
      if (data.user_email) localStorage.setItem('voxcore_user_email', data.user_email);

      // Only call onLogin after successful validation
      if (onLogin) {
        onLogin(data.user_name);
      }
    } catch (err: any) {
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
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

        <div className="login-form-card">
          <h3 className="login-form-title">Sign in to VoxCore</h3>
          <p className="login-form-subtitle">Enter your credentials to access the platform</p>

          <form onSubmit={handleSubmit} className="login-form">
            <div className="login-field">
              <label htmlFor="email">Email Address</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                autoComplete="email"
                autoFocus
              />
            </div>

            <div className="login-field">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
                autoComplete="current-password"
              />
            </div>

            {error && (
              <div className="login-error">
                <span>⚠️</span> {error}
              </div>
            )}

            <button type="submit" className="login-button" disabled={isLoading}>
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
