import React, { useState } from "react";
import { ConnectionModal } from "../components/connections/ConnectionModal";
import { useNavigate } from "react-router-dom";
import Layout from "../components/layout/Layout";
import "./Connections.css";

type Connection = {
  id: string;
  name: string;
  type: string;
  status: "connected" | "error" | "testing";
};


export default function Connections() {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [form, setForm] = useState({
    name: "",
    type: "postgres",
    host: "",
    port: "",
    database: "",
    user: "",
    password: ""
  });
  const [loading, setLoading] = useState(false);
  const [selectedDB, setSelectedDB] = useState<string|null>(null);
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();

  const openConnectionModal = (db: string) => {
    setSelectedDB(db);
    setShowModal(true);
  };

  const handleConnect = () => {
    setShowModal(false);
    // Simulate success, navigate to schema explorer
    navigate("/app/connections/1/schema");
  };

  async function handleCreateConnection(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);

    try {

      // Step 1: Add as 'testing'
      const tempConnection: Connection = {
        id: Date.now().toString(),
        name: form.name,
        type: form.type,
        status: "testing"
      };
      setConnections(prev => [...prev, tempConnection]);

      setForm({
        name: "",
        type: "postgres",
        host: "",
        port: "",
        database: "",
        user: "",
        password: ""
      });

      // Step 2: Simulate validation
      setTimeout(() => {
        setConnections(prev =>
          prev.map(conn =>
            conn.id === tempConnection.id
              ? { ...conn, status: "connected" }
              : conn
          )
        );
      }, 1500);

    } catch {
      alert("Connection failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Layout>
      <div className="connections-container">

        <div className="header">
          <h1>Data Connections</h1>
          <p>Securely connect and manage your data sources</p>
        </div>

        {/* CREATE CONNECTION */}
        <form className="connection-form" onSubmit={handleCreateConnection}>
          <input
            placeholder="Connection Name"
            value={form.name}
            onChange={e => setForm({ ...form, name: e.target.value })}
            required
          />

          <select
            value={form.type}
            onChange={e => setForm({ ...form, type: e.target.value })}
          >
            <option value="postgres">PostgreSQL</option>
            <option value="snowflake">Snowflake</option>
          </select>

          <input placeholder="Host" value={form.host}
            onChange={e => setForm({ ...form, host: e.target.value })} />

          <input placeholder="Port" value={form.port}
            onChange={e => setForm({ ...form, port: e.target.value })} />

          <input placeholder="Database" value={form.database}
            onChange={e => setForm({ ...form, database: e.target.value })} />

          <input placeholder="User" value={form.user}
            onChange={e => setForm({ ...form, user: e.target.value })} />

          <input type="password" placeholder="Password" value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })} />

          <button type="submit" disabled={loading}>
            {loading ? "Testing..." : "Connect"}
          </button>
        </form>

        {/* CONNECTION LIST */}
        <div className="connection-list">
          {connections.map(conn => (
            <div
              key={conn.id}
              className="connection-card hover:scale-105 transition"
              style={{ cursor: "pointer" }}
              onClick={() => openConnectionModal(conn.type)}
            >
              <div>
                <strong>{conn.name}</strong>
                <p>{conn.type}</p>
              </div>
              <span className={`status ${conn.status}`}>
                {conn.status}
              </span>
            </div>
          ))}
        </div>

        {/* Mount the modal */}
        {showModal && (
          <ConnectionModal
            db={selectedDB}
            onClose={() => setShowModal(false)}
            onConnect={handleConnect}
          />
        )}

      </div>
    </Layout>
  );
}
