import React from 'react';

interface AdminProps {
  token: string;
  onNavigate?: (page: string) => void;
}

export const Admin: React.FC<AdminProps> = ({ token, onNavigate }) => {
  const handleNavigate = (page: string) => {
    if (onNavigate) {
      onNavigate(page);
    }
  };

  return (
    <div className="view-content">
      <div className="panel">
        <h1>Admin Dashboard</h1>
        <p>Company-wide settings and configuration</p>
        
        <div className="admin-grid">
          <div className="admin-card" onClick={() => handleNavigate('admin-users')}>
            <h3>👥 User Management</h3>
            <p>Manage company users and roles</p>
          </div>
          
          <div className="admin-card">
            <h3>🔐 Security Settings</h3>
            <p>Password policies, 2FA, IP whitelist</p>
          </div>
          
          <div className="admin-card">
            <h3>📊 Company Settings</h3>
            <p>Company info, branding, integrations</p>
          </div>
          
          <div className="admin-card">
            <h3>🛡️ Firewall Rules</h3>
            <p>SQL policy enforcement</p>
          </div>
          
          <div className="admin-card">
            <h3>📋 Audit Logs</h3>
            <p>Activity and access logs</p>
          </div>
          
          <div className="admin-card">
            <h3>🔗 Database Connections</h3>
            <p>Manage database sources</p>
          </div>
        </div>
      </div>
    </div>
  );
};
