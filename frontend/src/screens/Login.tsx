import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';
import { apiUrl } from '../lib/api';

interface LoginProps {
  onLogin?: (userName?: string) => void;
  isDemoMode?: boolean;
}

export const Login: React.FC<LoginProps> = ({ onLogin, isDemoMode = false }) => {
  const navigate = useNavigate();
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
      const response = await fetch(apiUrl('/api/v1/auth/login'), {
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
      if (data.org_id != null) localStorage.setItem('voxcore_org_id', String(data.org_id));
      if (data.org_name) localStorage.setItem('voxcore_org_name', String(data.org_name));
      if (data.workspace_id != null) localStorage.setItem('voxcore_workspace_id', String(data.workspace_id));
      if (data.workspace_name) localStorage.setItem('voxcore_workspace_name', String(data.workspace_name));
      if (data.company_id != null) localStorage.setItem('voxcore_company_id', String(data.company_id));
      localStorage.setItem('voxcore_role', String(data.role || 'viewer'));
      localStorage.setItem('voxcore_is_super_admin', String(Boolean(data.is_super_admin)));

      // Only call onLogin after successful validation
      if (onLogin) {
        onLogin(data.user_name);
      }

      // Enforce a direct post-login route so auth never falls back to marketing view.
      navigate('/app/dashboard', { replace: true });
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
          src="/assets/VC_full_logo_text.png"
          alt="VoxCore Logo"
          className="login-image login-image-small"
        />

        <div className="login-form-card">
          <h3 className="login-form-title">Login to VoxCloud</h3>
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
