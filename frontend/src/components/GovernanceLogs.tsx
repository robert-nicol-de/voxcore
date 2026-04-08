import React, { useState } from "react";
import "./GovernanceLogs.css";

interface LogEntry {
  id: string;
  timestamp: string;
  event: string;
  severity: "info" | "warning" | "error" | "critical";
  user: string;
  action: string;
  details: string;
}

export const GovernanceLogs: React.FC = () => {
  const mockLogs: LogEntry[] = [
    {
      id: "1",
      timestamp: "2024-03-01 14:45:22",
      event: "Query Executed",
      severity: "info",
      user: "robert.nicol",
      action: "SELECT",
      details: "Query executed successfully on AdventureWorks2022 database",
    },
    {
      id: "2",
      timestamp: "2024-03-01 14:32:15",
      event: "Policy Violation Detected",
      severity: "warning",
      user: "robert.nicol",
      action: "QUERY_REWRITE",
      details: "Query was rewritten to comply with data governance policies",
    },
    {
      id: "3",
      timestamp: "2024-03-01 14:15:08",
      event: "Access Denied",
      severity: "error",
      user: "john.smith",
      action: "BLOCKED",
      details: "Attempted access to restricted table: SensitiveData",
    },
    {
      id: "4",
      timestamp: "2024-03-01 13:52:33",
      event: "Configuration Changed",
      severity: "info",
      user: "admin",
      action: "CONFIG_UPDATE",
      details: "Governance policy updated: Row-level security enabled",
    },
    {
      id: "5",
      timestamp: "2024-03-01 13:28:19",
      event: "Suspicious Activity",
      severity: "critical",
      user: "unknown",
      action: "ALERT",
      details: "Multiple failed authentication attempts detected from IP 192.168.1.100",
    },
    {
      id: "6",
      timestamp: "2024-03-01 13:05:44",
      event: "User Login",
      severity: "info",
      user: "robert.nicol",
      action: "LOGIN",
      details: "User logged in successfully from 192.168.1.50",
    },
    {
      id: "7",
      timestamp: "2024-03-01 12:42:11",
      event: "Data Export",
      severity: "warning",
      user: "sarah.johnson",
      action: "EXPORT",
      details: "Large dataset exported: 50,000 rows from Customers table",
    },
    {
      id: "8",
      timestamp: "2024-03-01 12:15:33",
      event: "Schema Change",
      severity: "error",
      user: "admin",
      action: "BLOCKED",
      details: "Attempted schema modification blocked by governance policy",
    },
  ];

  const [logs] = useState<LogEntry[]>(mockLogs);
  const [filterSeverity, setFilterSeverity] = useState<string>("all");

  const filteredLogs = filterSeverity === "all" 
    ? logs 
    : logs.filter(log => log.severity === filterSeverity);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "info": return "#3b82f6";
      case "warning": return "#f59e0b";
      case "error": return "#ef4444";
      case "critical": return "#dc2626";
      default: return "#6b7280";
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "info": return "ℹ️";
      case "warning": return "⚠️";
      case "error": return "❌";
      case "critical": return "🚨";
      default: return "•";
    }
  };

  return (
    <div className="governance-logs">
      <div className="logs-header">
        <h1>Governance Logs</h1>
        <p className="logs-subtitle">Audit trail of all governance events and actions</p>
      </div>

      <div className="logs-stats">
        <div className="stat-card">
          <div className="stat-label">Total Events</div>
          <div className="stat-value">{logs.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Info</div>
          <div className="stat-value">{logs.filter(l => l.severity === "info").length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Warnings</div>
          <div className="stat-value">{logs.filter(l => l.severity === "warning").length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Critical</div>
          <div className="stat-value">{logs.filter(l => l.severity === "critical").length}</div>
        </div>
      </div>

      <div className="logs-filter">
        <label>Filter by Severity:</label>
        <div className="filter-buttons">
          <button 
            className={`filter-btn ${filterSeverity === "all" ? "active" : ""}`}
            onClick={() => setFilterSeverity("all")}
          >
            All
          </button>
          <button 
            className={`filter-btn ${filterSeverity === "info" ? "active" : ""}`}
            onClick={() => setFilterSeverity("info")}
          >
            Info
          </button>
          <button 
            className={`filter-btn ${filterSeverity === "warning" ? "active" : ""}`}
            onClick={() => setFilterSeverity("warning")}
          >
            Warning
          </button>
          <button 
            className={`filter-btn ${filterSeverity === "error" ? "active" : ""}`}
            onClick={() => setFilterSeverity("error")}
          >
            Error
          </button>
          <button 
            className={`filter-btn ${filterSeverity === "critical" ? "active" : ""}`}
            onClick={() => setFilterSeverity("critical")}
          >
            Critical
          </button>
        </div>
      </div>

      <div className="logs-table">
        <div className="table-header">
          <div className="col-severity">Severity</div>
          <div className="col-timestamp">Timestamp</div>
          <div className="col-event">Event</div>
          <div className="col-user">User</div>
          <div className="col-action">Action</div>
          <div className="col-details">Details</div>
        </div>

        {filteredLogs.map((log) => (
          <div key={log.id} className="table-row">
            <div className="col-severity">
              <span className="severity-badge" style={{ borderLeftColor: getSeverityColor(log.severity) }}>
                {getSeverityIcon(log.severity)} {log.severity.toUpperCase()}
              </span>
            </div>
            <div className="col-timestamp">⏱ {log.timestamp}</div>
            <div className="col-event">{log.event}</div>
            <div className="col-user">👤 {log.user}</div>
            <div className="col-action">
              <span className="action-badge">{log.action}</span>
            </div>
            <div className="col-details">{log.details}</div>
          </div>
        ))}
      </div>
    </div>
  );
};
