import React, { useEffect, useState } from 'react';
import '../styles/DevSpace.css';
import { isAdmin, isDeveloper, getRoleLabel } from '../utils/permissions';

interface DevSpaceProps {
  token: string;
}

export const DevSpace: React.FC<DevSpaceProps> = ({ token }) => {
  const [userRole, setUserRole] = useState<string>('');
  const [loading, setLoading] = useState(true);

  // Fetch user role from /auth/me endpoint
  useEffect(() => {
    const fetchUserRole = async () => {
      try {
        const response = await fetch('/auth/me', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const user = await response.json();
          setUserRole(user.role);
        }
      } catch (error) {
        console.error('Failed to fetch user role:', error);
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchUserRole();
    }
  }, [token]);

  if (loading) {
    return (
      <div className="devspace-container">
        <p>Loading...</p>
      </div>
    );
  }

  // Check access: admin (god/admin) + developer can access
  if (!isAdmin(userRole) && !isDeveloper(userRole)) {
    return (
      <div className="devspace-container">
        <div className="access-denied">
          <h2>🔒 Access Denied</h2>
          <p>Developer Space is only available to Admin and Developer users.</p>
          <p>Your role: <strong>{getRoleLabel(userRole)}</strong></p>
        </div>
      </div>
    );
  }

  return (
    <div className="devspace-container">
      <div className="devspace-header">
        <h1>🛠️ VoxCore Developer Space</h1>
        <p className="devspace-subtitle">Advanced debugging tools for AI queries and firewall analysis</p>
      </div>

      <div className="devspace-grid">
        {/* Prompt Debugger */}
        <div className="devspace-card">
          <div className="card-header">
            <h2>📝 Prompt Debugger</h2>
            <span className="badge">DEBUG</span>
          </div>
          <div className="card-content">
            <p>Analyze and debug user prompts before SQL generation.</p>
            <div className="code-block">
              <pre>Prompt analysis output will appear here...</pre>
            </div>
            <button className="card-btn">Test Prompt</button>
          </div>
        </div>

        {/* SQL Generator */}
        <div className="devspace-card">
          <div className="card-header">
            <h2>🚀 SQL Generator</h2>
            <span className="badge">GENERATE</span>
          </div>
          <div className="card-content">
            <p>View and inspect generated SQL queries in real-time.</p>
            <div className="code-block">
              <pre>Generated SQL will appear here...</pre>
            </div>
            <button className="card-btn">Generate SQL</button>
          </div>
        </div>

        {/* Firewall Analysis */}
        <div className="devspace-card">
          <div className="card-header">
            <h2>🔥 Firewall Analysis</h2>
            <span className="badge">SECURITY</span>
          </div>
          <div className="card-content">
            <p>Review risk scores and security rule violations.</p>
            <div className="code-block">
              <pre>Firewall analysis results will appear here...</pre>
            </div>
            <button className="card-btn">Analyze Risk</button>
          </div>
        </div>

        {/* Query Fingerprint */}
        <div className="devspace-card">
          <div className="card-header">
            <h2>👁️ Query Fingerprint</h2>
            <span className="badge">INSPECT</span>
          </div>
          <div className="card-content">
            <p>Explore query patterns and data access signatures.</p>
            <div className="code-block">
              <pre>Fingerprint data will appear here...</pre>
            </div>
            <button className="card-btn">Fingerprint Query</button>
          </div>
        </div>

        {/* Schema Explorer */}
        <div className="devspace-card">
          <div className="card-header">
            <h2>📊 Schema Explorer</h2>
            <span className="badge">EXPLORE</span>
          </div>
          <div className="card-content">
            <p>View database schema structure and relationships.</p>
            <div className="code-block">
              <pre>Schema structure will appear here...</pre>
            </div>
            <button className="card-btn">Explore Schema</button>
          </div>
        </div>

        {/* AI Model Info */}
        <div className="devspace-card">
          <div className="card-header">
            <h2>🤖 AI Model Info</h2>
            <span className="badge">MODEL</span>
          </div>
          <div className="card-content">
            <p>View active AI models and configuration settings.</p>
            <div className="code-block">
              <pre>Model configuration will appear here...</pre>
            </div>
            <button className="card-btn">View Config</button>
          </div>
        </div>
      </div>

      {/* Quick Links */}
      <div className="devspace-footer">
        <h3>📚 Developer Resources</h3>
        <ul>
          <li><a href="#">VoxCore API Documentation</a></li>
          <li><a href="#">Firewall Rules Reference</a></li>
          <li><a href="#">SQL Dialect Guide</a></li>
          <li><a href="#">Error Code Reference</a></li>
        </ul>
      </div>
    </div>
  );
};
