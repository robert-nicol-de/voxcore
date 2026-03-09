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
}

export const UserDropdown: React.FC<UserDropdownProps> = ({ token, onLogout }) => {
  const [open, setOpen] = useState(false);
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    fetch('/api/v1/auth/me', {
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
    onLogout();
  };

  // Role-based menu
  const menu = [
    { label: 'Profile', action: () => {} },
    { label: 'My Queries', action: () => {} },
    { label: 'API Keys', action: () => {} },
  ];
  if (user && (user.role === 'god' || user.role === 'admin')) {
    menu.push({ label: 'Admin Panel', action: () => {} });
    menu.push({ label: 'User Management', action: () => {} });
  }
  if (user && user.role === 'developer') {
    menu.push({ label: 'Dev Space', action: () => {} });
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
                <div className="dropdown-item" key={idx} onClick={item.action}>{item.label}</div>
              ))}
              <hr />
              <div className="dropdown-item dropdown-logout" onClick={handleLogout}>Logout</div>
            </>
          ) : null}
        </div>
      )}
    </div>
  );
};
