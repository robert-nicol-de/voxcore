import React, { useState, useEffect } from "react";
import "./ConnectionModal.css";
import { apiUrl } from "../lib/api";

interface ConnectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConnect: (warehouseType: string) => void;
}

interface Credentials {
  host: string;
  username: string;
  password: string;
  database: string;
  port?: string;
  warehouse?: string;
  role?: string;
  schema_name?: string;
  auth_type?: string;
}

// Test credentials for development
const testCredentials: Record<string, Credentials> = {
  sqlserver: {
    host: "localhost",
    username: "sa",
    password: "YourPassword123!",
    database: "AdventureWorks2022",
    port: "1433",
    auth_type: "sql"
  },
  snowflake: {
    host: "ko05278.af-south-1.aws",
    username: "VoxQuery",
    password: "Robert210680!@#$",
    database: "VOXQUERYTRAININGPIN2025",
    warehouse: "VOXQUERY_WH",
    role: "ACCOUNTADMIN",
    schema_name: "PUBLIC"
  }
};

const databases = [
  {
    id: "snowflake",
    name: "Snowflake",
    description: "Cloud Data Warehouse",
    icon: "❄️",
    status: "active"
  },
  {
    id: "semantic",
    name: "Semantic Model",
    description: "AI-Enhanced Semantic Layer",
    icon: "🧠",
    status: "active"
  },
  {
    id: "sqlserver",
    name: "SQL Server",
    description: "Microsoft SQL Server",
    icon: "◆",
    status: "active"
  },
  {
    id: "postgres",
    name: "PostgreSQL",
    description: "Open Source Database",
    icon: "🐘",
    status: "coming"
  },
  {
    id: "redshift",
    name: "Redshift",
    description: "AWS Data Warehouse",
    icon: "●",
    status: "coming"
  },
  {
    id: "bigquery",
    name: "BigQuery",
    description: "Google Cloud Data Warehouse",
    icon: "📊",
    status: "coming"
  }
];

export const ConnectionModal: React.FC<ConnectionModalProps> = ({
  isOpen,
  onClose,
  onConnect
}) => {
  const [step, setStep] = useState<"select" | "credentials">("select");
  const [selectedDb, setSelectedDb] = useState<string | null>(null);
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [credentials, setCredentials] = useState<Credentials>({
    host: "",
    username: "",
    password: "",
    database: "",
    port: "",
    warehouse: "VOXQUERY_WH",
    role: "ACCOUNTADMIN",
    schema_name: "PUBLIC",
    auth_type: "sql"  // Default to SQL auth
  });

  // Load saved credentials when modal opens
  useEffect(() => {
    if (isOpen && selectedDb) {
      loadSavedCredentials(selectedDb);
    }
  }, [isOpen, selectedDb]);

  const loadSavedCredentials = async (dbType: string) => {
    try {
      const response = await fetch(apiUrl(`/api/v1/auth/load-ini-credentials/${dbType}`), {
        method: "POST"
      });
      if (response.ok) {
        const data = await response.json();
        if (data.credentials) {
          // console.log(`[ConnectionModal] Loaded credentials for ${dbType}:`, data.credentials);
          setCredentials(prev => ({
            ...prev,
            ...data.credentials
          }));
          setRememberMe(true);
        }
      }
    } catch (err) {
      // console.log(`[ConnectionModal] No saved credentials for ${dbType}`);
      // Silently fail - no saved credentials
    }
  };

  if (!isOpen) return null;

  const handleSelectDb = async (dbId: string, status: string) => {
    if (status === "active") {
      setSelectedDb(dbId);
      setStep("credentials");
      setError(null);
      
      // Pre-fill with test credentials if available
      if (testCredentials[dbId]) {
        setCredentials(testCredentials[dbId]);
      }
      
      // Also try to load saved credentials from INI
      await loadSavedCredentials(dbId);
    }
  };

  const handleCredentialChange = (field: keyof Credentials, value: string) => {
    setCredentials(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleConnect = async () => {
    if (!selectedDb) return;

    // Validate required fields
    if (!credentials.host || !credentials.database) {
      setError("Host and Database are required");
      return;
    }

    if (selectedDb === "snowflake" || selectedDb === "semantic") {
      if (!credentials.username || !credentials.password) {
        setError("Username and Password are required");
        return;
      }
    } else if (selectedDb === "sqlserver") {
      // For SQL Server, username/password only required for SQL auth
      if (credentials.auth_type === "sql" && (!credentials.username || !credentials.password)) {
        setError("Username and Password are required for SQL Authentication");
        return;
      }
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(apiUrl("/api/v1/auth/connect"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          database: selectedDb,
          credentials: credentials,
          remember_me: rememberMe
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Connection failed");
      }

      // Success! Store connection info in localStorage
      localStorage.setItem("selectedDatabase", selectedDb);
      localStorage.setItem("dbHost", credentials.host);
      localStorage.setItem("dbDatabase", credentials.database);
      localStorage.setItem("dbSchema", credentials.schema_name || "PUBLIC");
      localStorage.setItem("dbConnectionStatus", "connected");
      
      // Dispatch custom event with connection details
      const event = new CustomEvent("connectionStatusChanged", {
        detail: { connected: true, database: selectedDb }
      });
      window.dispatchEvent(event);
      
      // Call the callback
      onConnect(selectedDb);
      onClose();
      setStep("select");
      setSelectedDb(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Connection failed");
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setStep("select");
    setSelectedDb(null);
    setError(null);
    setCredentials({
      host: "",
      username: "",
      password: "",
      database: "",
      port: "",
      warehouse: "VOXQUERY_WH",
      role: "ACCOUNTADMIN",
      schema_name: "PUBLIC",
      auth_type: "sql"
    });
  };

  const handleCancel = () => {
    // Only close modal - don't set connection status
    // Connection status should only be set on successful connection
    onClose();
  };

  return (
    <div className="connection-modal-overlay">
      <div className="connection-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{step === "select" ? "Connect to Database" : `Connect to ${selectedDb?.toUpperCase()}`}</h2>
          <button className="modal-close" onClick={handleCancel}>✕</button>
        </div>

        <div className="modal-content">
          {step === "select" ? (
            <>
              <p className="modal-subtitle">Select your data warehouse</p>
              
              <div className="database-grid">
                {databases.map((db) => (
                  <div
                    key={db.id}
                    className={`database-card ${db.status === "coming" ? "disabled" : ""} ${selectedDb === db.id ? "selected" : ""}`}
                    onClick={() => handleSelectDb(db.id, db.status)}
                  >
                    <div className="card-icon">{db.icon}</div>
                    <h3 className="card-title">{db.name}</h3>
                    <p className="card-description">{db.description}</p>
                    {db.status === "coming" && (
                      <div className="coming-soon-badge">COMING SOON</div>
                    )}
                  </div>
                ))}
              </div>
            </>
          ) : (
            <>
              <div className="credentials-form">
                <div className="form-group">
                  <label>Host / Account</label>
                  <input
                    type="text"
                    placeholder={selectedDb === "snowflake" ? "e.g., ko05278.af-south-1.aws" : "e.g., localhost"}
                    value={credentials.host}
                    onChange={(e) => handleCredentialChange("host", e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label>Database</label>
                  <input
                    type="text"
                    placeholder={selectedDb === "snowflake" ? "e.g., VOXQUERYTRAININGPIN2025" : "e.g., mydb"}
                    value={credentials.database}
                    onChange={(e) => handleCredentialChange("database", e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label>Username</label>
                  <input
                    type="text"
                    placeholder="Username"
                    value={credentials.username}
                    onChange={(e) => handleCredentialChange("username", e.target.value)}
                    disabled={selectedDb === "sqlserver" && credentials.auth_type === "windows"}
                  />
                </div>

                <div className="form-group">
                  <label>Password</label>
                  <input
                    type="password"
                    placeholder="Password"
                    value={credentials.password}
                    onChange={(e) => handleCredentialChange("password", e.target.value)}
                    disabled={selectedDb === "sqlserver" && credentials.auth_type === "windows"}
                  />
                </div>

                {selectedDb === "snowflake" && (
                  <>
                    <div className="form-group">
                      <label>Warehouse</label>
                      <input
                        type="text"
                        placeholder="e.g., COMPUTE_WH"
                        value={credentials.warehouse || ""}
                        onChange={(e) => handleCredentialChange("warehouse", e.target.value)}
                      />
                    </div>

                    <div className="form-group">
                      <label>Role</label>
                      <input
                        type="text"
                        placeholder="e.g., ACCOUNTADMIN"
                        value={credentials.role || ""}
                        onChange={(e) => handleCredentialChange("role", e.target.value)}
                      />
                    </div>

                    <div className="form-group">
                      <label>Schema</label>
                      <input
                        type="text"
                        placeholder="e.g., PUBLIC"
                        value={credentials.schema_name || ""}
                        onChange={(e) => handleCredentialChange("schema_name", e.target.value)}
                      />
                    </div>
                  </>
                )}

                {selectedDb === "semantic" && (
                  <>
                    <div className="form-group">
                      <label htmlFor="conn-warehouse-sem">Warehouse</label>
                      <input
                        id="conn-warehouse-sem"
                        name="warehouse"
                        type="text"
                        placeholder="e.g., COMPUTE_WH"
                        value={credentials.warehouse || ""}
                        onChange={(e) => handleCredentialChange("warehouse", e.target.value)}
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="conn-role-sem">Role</label>
                      <input
                        id="conn-role-sem"
                        name="role"
                        type="text"
                        placeholder="e.g., ACCOUNTADMIN"
                        value={credentials.role || ""}
                        onChange={(e) => handleCredentialChange("role", e.target.value)}
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="conn-schema-sem">Schema</label>
                      <input
                        id="conn-schema-sem"
                        name="schema_name"
                        type="text"
                        placeholder="e.g., PUBLIC"
                        value={credentials.schema_name || ""}
                        onChange={(e) => handleCredentialChange("schema_name", e.target.value)}
                      />
                    </div>
                  </>
                )}

                {selectedDb === "sqlserver" && (
                  <div className="form-group">
                    <label htmlFor="conn-auth-type">Auth Type</label>
                    <select
                      id="conn-auth-type"
                      name="auth_type"
                      value={credentials.auth_type || "sql"}
                      onChange={(e) => handleCredentialChange("auth_type", e.target.value)}
                    >
                      <option value="sql">SQL Authentication</option>
                      <option value="windows">Windows Authentication</option>
                    </select>
                  </div>
                )}

                <div className="form-group checkbox">
                  <input
                    type="checkbox"
                    id="remember-me"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                  />
                  <label htmlFor="remember-me">Remember me (save credentials)</label>
                </div>

                {error && (
                  <div className="error-message">{error}</div>
                )}
              </div>
            </>
          )}
        </div>

        <div className="modal-footer">
          {step === "credentials" && (
            <button className="btn-cancel" onClick={handleBack} disabled={loading}>
              Back
            </button>
          )}
          {step === "select" && (
            <button className="btn-cancel" onClick={handleCancel}>Cancel</button>
          )}
          {step === "credentials" && (
            <button 
              className="btn-connect" 
              onClick={handleConnect}
              disabled={loading}
            >
              {loading ? "Connecting..." : "Connect"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
