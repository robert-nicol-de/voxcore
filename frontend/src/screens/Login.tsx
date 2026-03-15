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
    <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-primary-dark via-primary to-primary-darker">
      <div className="flex flex-col items-center justify-center gap-12 z-10 animate-fade-in">
        <img 
          src="/assets/VC_full_logo_text.png"
          alt="VoxCore Logo"
          className="w-full max-w-lg mb-6 drop-shadow-xl animate-slide-up"
        />

        <div className="card bg-opacity-90 border border-accent/20 rounded-2xl p-10 max-w-lg w-full backdrop-blur-md">
          <h3 className="text-2xl font-bold text-center text-primary-content mb-1">Login to VoxCloud</h3>
          <p className="text-base text-center text-muted mb-7">Enter your credentials to access the platform</p>

          <form onSubmit={handleSubmit} className="flex flex-col gap-5">
            <div className="flex flex-col gap-1">
              <label htmlFor="email" className="text-sm font-semibold text-muted">Email Address</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                autoComplete="email"
                autoFocus
                className="input px-4 py-3 rounded-lg border border-platform-border bg-platform-input text-primary-content text-base focus:border-accent focus:ring-2 focus:ring-accent/20 placeholder:text-muted"
              />
            </div>

            <div className="flex flex-col gap-1">
              <label htmlFor="password" className="text-sm font-semibold text-muted">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
                autoComplete="current-password"
                className="input px-4 py-3 rounded-lg border border-platform-border bg-platform-input text-primary-content text-base focus:border-accent focus:ring-2 focus:ring-accent/20 placeholder:text-muted"
              />
            </div>

            {error && (
              <div className="bg-error/10 border border-error/30 rounded-lg px-4 py-3 text-error text-sm flex items-center gap-2">
                <span>⚠️</span> {error}
              </div>
            )}

            <button type="submit" className="primary-btn w-full py-3 text-lg font-semibold rounded-lg shadow-lg mt-1" disabled={isLoading}>
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
