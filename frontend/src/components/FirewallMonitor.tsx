import React, { useState, useEffect } from 'react';
import './FirewallMonitor.css';

interface FirewallStats {
  queriesScanned: number;
  blocked: number;
  highRisk: number;
  executing: number;
}

export const FirewallMonitor: React.FC = () => {
  const [stats, setStats] = useState<FirewallStats>({
    queriesScanned: 182,
    blocked: 4,
    highRisk: 9,
    executing: 47,
  });

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setStats(prev => ({
        queriesScanned: prev.queriesScanned + Math.floor(Math.random() * 5),
        blocked: prev.blocked + Math.floor(Math.random() * 2),
        highRisk: Math.max(1, prev.highRisk + Math.floor(Math.random() * 3) - 1),
        executing: Math.max(0, prev.executing + Math.floor(Math.random() * 10) - 5),
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const blockRate = stats.queriesScanned > 0 
    ? ((stats.blocked / stats.queriesScanned) * 100).toFixed(1) 
    : '0.0';

  return (
    <div className="firewall-monitor">
      <div className="monitor-header">
        <h3>🛡️ SQL Firewall Monitor</h3>
        <div className="monitor-status">
          <span className="status-dot active"></span>
          Real-time Monitoring
        </div>
      </div>

      <div className="monitor-grid">
        {/* Queries Scanned */}
        <div className="monitor-card primary">
          <div className="card-label">Queries Scanned</div>
          <div className="card-value">{stats.queriesScanned}</div>
          <div className="card-detail">All-time total</div>
        </div>

        {/* Blocked */}
        <div className="monitor-card danger">
          <div className="card-label">🚫 Blocked</div>
          <div className="card-value">{stats.blocked}</div>
          <div className="card-detail">{blockRate}% block rate</div>
        </div>

        {/* High Risk */}
        <div className="monitor-card warning">
          <div className="card-label">⚠️ High Risk</div>
          <div className="card-value">{stats.highRisk}</div>
          <div className="card-detail">Requires review</div>
        </div>

        {/* Currently Executing */}
        <div className="monitor-card success">
          <div className="card-label">✓ Executing</div>
          <div className="card-value">{stats.executing}</div>
          <div className="card-detail">Active queries</div>
        </div>
      </div>

      {/* Firewall Status */}
      <div className="firewall-status">
        <h4>Firewall Status</h4>
        <div className="status-list">
          <div className="status-item">
            <div className="status-indicator active"></div>
            <span className="status-label">SQL Injection Protection</span>
            <span className="status-value">✓ Active</span>
          </div>
          <div className="status-item">
            <div className="status-indicator active"></div>
            <span className="status-label">Query Fingerprinting</span>
            <span className="status-value">✓ Active</span>
          </div>
          <div className="status-item">
            <div className="status-indicator active"></div>
            <span className="status-label">Policy Enforcement</span>
            <span className="status-value">✓ Active</span>
          </div>
          <div className="status-item">
            <div className="status-indicator active"></div>
            <span className="status-label">Audit Logging</span>
            <span className="status-value">✓ Recording</span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="monitor-actions">
        <button className="action-btn">
          📋 View Audit Logs
        </button>
        <button className="action-btn">
          ⚙️ Configure Rules
        </button>
        <button className="action-btn">
          📊 View Analytics
        </button>
      </div>
    </div>
  );
};

export default FirewallMonitor;
