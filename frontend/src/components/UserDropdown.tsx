import React, { useState, useEffect } from 'react';
import './UserDropdown.css';
import { RoleBadge } from './RoleBadge';
import { isAdmin, isDeveloper } from '../utils/permissions';

interface UserInfo {
  email: string;
  name: string;
  role: string;
  role_label: string;
  company: string;
  company_id: number;
}

interface UserDropdownProps {
  token: string;
  onLogout: () => void;
  onNavigate?: (page: any) => void;
}

export const UserDropdown: React.FC<UserDropdownProps> = ({ token, onLogout, onNavigate }) => {
  const [open, setOpen] = useState(false);
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    fetch('/auth/me', {
      headers: { 'Authorization': `Bearer ${token}` },
    })
      .then(res => res.ok ? res.json() : Promise.reject(res))
      .then(data => {
        setUser(data);
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to load user info');
        setLoading(false);
      });
  }, [token]);

  const handleLogout = () => {
    fetch('/api/logout', { method: 'POST' }).catch(() => {
      // Ignore logout API errors; client-side token clearing is the source of truth.
    });
    localStorage.removeItem('token');
    localStorage.removeItem('voxcore_token');
    localStorage.removeItem('voxcore_user_name');
    localStorage.removeItem('voxcore_user_email');
    sessionStorage.clear();
    onLogout();
    window.location.href = '/login';
  };

  const handleNavigate = (page: string) => {
    if (onNavigate) {
      onNavigate(page);
    }
    setOpen(false);
  };

  // Role-based menu with navigation actions
  const menu = [
    { label: 'Profile', action: () => handleNavigate('profile') },
    { label: 'My Queries', action: () => handleNavigate('queries') },
    { label: 'API Keys', action: () => handleNavigate('api-keys') },
    { label: '🎬 Try Demo', action: () => window.location.href = '/app?demo=true' },
  ];
  
  // Admin menu items (god and admin bypass)
  if (user && isAdmin(user.role)) {
    menu.push({ label: 'Admin Panel', action: () => handleNavigate('admin') });
    menu.push({ label: 'User Management', action: () => handleNavigate('admin-users') });
  }
  
  // Developer menu items (god, admin, developer)
  if (user && isDeveloper(user.role)) {
    menu.push({ label: 'Dev Space', action: () => handleNavigate('devspace') });
  }

  return (
    <div className="user-dropdown-root">
      <div className="user-menu" onClick={() => setOpen(v => !v)}>
        <span>👤 {user ? user.email : 'User'}</span>
        <span className="dropdown-arrow">▼</span>
      </div>
      {open && (
        <div className="user-dropdown">
          {loading ? (
            <div className="dropdown-loading">Loading...</div>
          ) : error ? (
            <div className="dropdown-error">{error}</div>
          ) : user ? (
            <>
              <div className="dropdown-header">
                <div className="dropdown-email">{user.email}</div>
                <div className="dropdown-company">Company: {user.company}</div>
                <div className="dropdown-role-container">
                  <RoleBadge role={user.role} />
                </div>
              </div>
              <hr />
              {menu.map((item, idx) => (
                <button key={idx} className="dropdown-item" onClick={item.action}>
                  {item.label}
                </button>
              ))}
              <hr />
              <button className="dropdown-item dropdown-logout" onClick={handleLogout}>
                Logout
              </button>
            </>
          ) : null}
        </div>
      )}
    </div>
  );
};
