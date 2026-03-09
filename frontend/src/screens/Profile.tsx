import React, { useState, useEffect } from 'react';
import { RoleBadge } from '../components/RoleBadge';

interface UserInfo {
  email: string;
  name: string;
  role: string;
  role_label: string;
  company: string;
  company_id: number;
}

interface ProfileProps {
  token: string;
}

export const Profile: React.FC<ProfileProps> = ({ token }) => {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    fetch('/auth/me', {
      headers: { 'Authorization': `Bearer ${token}` },
    })
      .then(res => res.ok ? res.json() : Promise.reject(res))
      .then(data => {
        setUser(data);
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to load profile');
        setLoading(false);
      });
  }, [token]);

  if (loading) return <div className="view-content"><p>Loading...</p></div>;
  if (error) return <div className="view-content"><p className="error">{error}</p></div>;
  if (!user) return <div className="view-content"><p>No user data</p></div>;

  return (
    <div className="view-content">
      <div className="panel">
        <h2>User Profile</h2>
        <div className="profile-section">
          <label>Email:</label>
          <p>{user.email}</p>
        </div>
        <div className="profile-section">
          <label>Name:</label>
          <p>{user.name}</p>
        </div>
        <div className="profile-section">
          <label>Company:</label>
          <p>{user.company}</p>
        </div>
        <div className="profile-section">
          <label>Role:</label>
          <div style={{ marginTop: '8px' }}>
            <RoleBadge role={user.role} />
          </div>
        </div>
        
        <hr />
        
        <h3>Security</h3>
        <button className="btn btn-primary">Change Password</button>
        
        <hr />
        
        <h3>Sessions</h3>
        <p>Active sessions: 1</p>
        <button className="btn btn-secondary">Logout of all devices</button>
      </div>
    </div>
  );
};
