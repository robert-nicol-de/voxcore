import React, { useState } from "react";
import { apiUrl } from "../../lib/api";

type Props = {
  onSaved?: () => void;
};

const starterJson = `{
  "entities": {
    "customers": {
      "table": "customers",
      "metrics": {
        "revenue": "SUM(order_total)"
      }
    },
    "orders": {
      "table": "orders",
      "metrics": {
        "order_count": "COUNT(order_id)"
      }
    }
  }
}`;

export default function SemanticModelCreator({ onSaved }: Props) {
  const [name, setName] = useState("Sales Model");
  const [sourceDatabase, setSourceDatabase] = useState("Snowflake");
  const [definition, setDefinition] = useState(starterJson);
  const [message, setMessage] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const workspaceId = Number(localStorage.getItem("voxcore_workspace_id") || "1");

  const save = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const token = localStorage.getItem("voxcore_token") || localStorage.getItem("vox_token") || "";
      const parsed = JSON.parse(definition);
      const res = await fetch(apiUrl(`/api/v1/datasources/models?workspace_id=${workspaceId}`), {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          datasource_id: 1,
          name,
          description: `Source Database: ${sourceDatabase}`,
          definition: parsed,
        }),
      });
      if (!res.ok) {
        const err = (await res.json().catch(() => ({}))) as { detail?: string };
        setMessage(err.detail || "Failed to save semantic model.");
        return;
      }
      setMessage("Semantic model saved. VoxQuery can now use business context.");
      onSaved?.();
    } catch {
      setMessage("Invalid JSON definition or network issue.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="ds-form-wrap">
      <h2>Create Semantic Model</h2>
      <div className="ds-form-grid">
        <label>Name<input value={name} onChange={(e) => setName(e.target.value)} /></label>
        <label>Source Database<input value={sourceDatabase} onChange={(e) => setSourceDatabase(e.target.value)} /></label>
      </div>

      <div className="semantic-entities">
        <h3>Entities</h3>
        <div className="entity-chips">
          <span>customers</span>
          <span>orders</span>
          <span>products</span>
        </div>
      </div>

      <label className="semantic-json-label">Model JSON</label>
      <textarea
        className="semantic-json"
        value={definition}
        onChange={(e) => setDefinition(e.target.value)}
      />

      {message && <div className="ds-message">{message}</div>}

      <div className="ds-actions">
        <button className="primary-btn" onClick={save} disabled={saving}>
          {saving ? "Saving..." : "Save Semantic Model"}
        </button>
      </div>
    </div>
  );
}
