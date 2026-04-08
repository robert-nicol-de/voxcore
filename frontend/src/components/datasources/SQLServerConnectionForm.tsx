import React, { useState } from "react";
import { apiUrl } from "../../lib/api";

type Props = {
  onSaved?: () => void;
};

export default function SQLServerConnectionForm({ onSaved }: Props) {
  const [name, setName] = useState("");
  const [host, setHost] = useState("");
  const [port, setPort] = useState("1433");
  const [database, setDatabase] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [encrypt, setEncrypt] = useState(true);
  const [trustServerCertificate, setTrustServerCertificate] = useState(false);
  const [queryTimeout, setQueryTimeout] = useState("30");
  const [poolSize, setPoolSize] = useState("5");
  const [loadingTest, setLoadingTest] = useState(false);
  const [loadingSave, setLoadingSave] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const workspaceId = Number(localStorage.getItem("voxcore_workspace_id") || "1");
  const orgId = Number(localStorage.getItem("voxcore_org_id") || "1");

  const config = {
    type: "sqlserver",
    host,
    port: Number(port || "1433"),
    database,
    username,
    password,
    encrypt,
    trust_server_certificate: trustServerCertificate,
    query_timeout: Number(queryTimeout || "30"),
    pool_size: Number(poolSize || "5"),
  };

  const testConnection = async () => {
    setLoadingTest(true);
    setMessage(null);
    try {
      const token = localStorage.getItem("voxcore_token") || localStorage.getItem("vox_token") || "";
      const res = await fetch(apiUrl("/api/v1/datasources/sqlserver/test"), {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          server: host,
          port: Number(port || "1433"),
          database,
          username,
          password,
          encrypt,
          trust_server_certificate: trustServerCertificate,
          timeout_seconds: Number(queryTimeout || "30"),
        }),
      });
      const data = (await res.json().catch(() => ({}))) as { valid?: boolean; detail?: string; error?: string };
      setMessage(data.valid ? "Connection successful." : data.detail || data.error || "Connection failed.");
    } catch {
      setMessage("Connection test failed due to network error.");
    } finally {
      setLoadingTest(false);
    }
  };

  const saveConnection = async () => {
    if (!name || !host || !database || !username || !password) {
      setMessage("Please fill all required fields.");
      return;
    }
    setLoadingSave(true);
    setMessage(null);
    try {
      const token = localStorage.getItem("voxcore_token") || localStorage.getItem("vox_token") || "";
      const res = await fetch(apiUrl(`/api/v1/datasources?workspace_id=${workspaceId}`), {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          org_id: orgId,
          workspace_id: workspaceId,
          name,
          type: "sqlserver",
          platform: "sqlserver",
          status: "active",
          config,
          credentials: {
            host,
            port: Number(port || "1433"),
            database,
            username,
            password,
            encrypt,
            trust_server_certificate: trustServerCertificate,
          },
        }),
      });
      if (!res.ok) {
        const err = (await res.json().catch(() => ({}))) as { detail?: string };
        setMessage(err.detail || "Save failed.");
        return;
      }
      setMessage("Connection saved successfully.");
      onSaved?.();
    } catch {
      setMessage("Save failed due to network error.");
    } finally {
      setLoadingSave(false);
    }
  };

  return (
    <div className="ds-form-wrap">
      <h2>Add SQL Server Data Source</h2>
      <div className="ds-form-grid">
        <label>Connection Name<input value={name} onChange={(e) => setName(e.target.value)} /></label>
        <label>Server<input value={host} onChange={(e) => setHost(e.target.value)} placeholder="sql.mycompany.local" /></label>
        <label>Port<input value={port} onChange={(e) => setPort(e.target.value)} /></label>
        <label>Database<input value={database} onChange={(e) => setDatabase(e.target.value)} /></label>
        <label>Username<input value={username} onChange={(e) => setUsername(e.target.value)} /></label>
        <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label>
      </div>

      <details className="ds-advanced">
        <summary>Advanced Settings</summary>
        <div className="ds-form-grid" style={{ marginTop: 12 }}>
          <label>
            Encrypt
            <select value={encrypt ? "true" : "false"} onChange={(e) => setEncrypt(e.target.value === "true")}>
              <option value="true">Enabled</option>
              <option value="false">Disabled</option>
            </select>
          </label>
          <label>
            Trust Server Certificate
            <select
              value={trustServerCertificate ? "true" : "false"}
              onChange={(e) => setTrustServerCertificate(e.target.value === "true")}
            >
              <option value="false">Disabled</option>
              <option value="true">Enabled</option>
            </select>
          </label>
          <label>Query Timeout (seconds)<input value={queryTimeout} onChange={(e) => setQueryTimeout(e.target.value)} /></label>
          <label>Connection Pool Size<input value={poolSize} onChange={(e) => setPoolSize(e.target.value)} /></label>
        </div>
      </details>

      {message && <div className="ds-message">{message}</div>}

      <div className="ds-actions">
        <button className="secondary-btn" onClick={testConnection} disabled={loadingTest}>
          {loadingTest ? "Testing..." : "Test Connection"}
        </button>
        <button className="primary-btn" onClick={saveConnection} disabled={loadingSave}>
          {loadingSave ? "Saving..." : "Save Connection"}
        </button>
      </div>
    </div>
  );
}
