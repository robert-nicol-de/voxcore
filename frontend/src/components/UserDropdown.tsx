import React, { useState, useEffect } from 'react';
import './UserDropdown.css';

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
  onNavigate?: (page: string) => void;
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
    localStorage.removeItem('voxcore_token');
    localStorage.removeItem('voxcore_user_name');
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
  ];
  if (user && (user.role === 'god' || user.role === 'admin')) {
    menu.push({ label: 'Admin Panel', action: () => handleNavigate('admin') });
    menu.push({ label: 'User Management', action: () => handleNavigate('admin-users') });
  }
  if (user && user.role === 'developer') {
    menu.push({ label: 'Dev Space', action: () => handleNavigate('dev-space') });
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
                <div className="dropdown-role">Role: {user.role_label}</div>
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
