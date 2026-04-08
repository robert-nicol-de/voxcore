import React, { useState } from "react";

const configFields = {
  action: [
    { key: "action_type", label: "Action Type", type: "text" },
    { key: "target", label: "Target", type: "text" }
  ],
  slack: [
    { key: "message", label: "Message", type: "text" }
  ],
  wait: [
    { key: "days", label: "Days", type: "number" }
  ],
  evaluate: [
    { key: "metric", label: "Metric", type: "text" }
  ],
  email: [
    { key: "type", label: "Email Type", type: "text" }
  ],
  trigger: [
    { key: "trigger_type", label: "Trigger Type", type: "text" }
  ],
  condition: [
    { key: "field", label: "Field", type: "select", options: ["impact", "confidence", "success_rate", "metric_value", "action_score", "churn_score"] },
    { key: "operator", label: "Operator", type: "select", options: [">", "<", "=", ">=", "<="] },
    { key: "value", label: "Value", type: "number" }
  ],
  loop: [
    { key: "max_retries", label: "Max Retries", type: "number" },
    { key: "retry_strategy", label: "Retry Strategy", type: "text" }
  ],
  score: [
    { key: "score_formula", label: "Score Formula", type: "text" },
    { key: "threshold", label: "Threshold", type: "number" }
  ]
};

export default function NodeConfigPanel({ node, onClose, setNodes }) {
  const [config, setConfig] = useState(node.data.config || {});
  const fields = configFields[node.data.type] || [];

  const onSave = () => {
    setNodes((nds) =>
      nds.map((n) =>
        n.id === node.id ? { ...n, data: { ...n.data, config } } : n
      )
    );
    onClose();
  };

  return (
    <div className="w-72 p-4 bg-white rounded-xl border ml-4 shadow-lg">
      <div className="font-bold mb-2">Configure: {node.data.label}</div>
      {fields.map((f) => (
        <div key={f.key} className="mb-2">
          <label className="block text-sm mb-1">{f.label}</label>
          {f.type === "select" ? (
            <select
              className="w-full border rounded px-2 py-1"
              value={config[f.key] || ""}
              onChange={(e) => setConfig({ ...config, [f.key]: e.target.value })}
            >
              <option value="">Select...</option>
              {f.options.map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          ) : (
            <input
              type={f.type}
              className="w-full border rounded px-2 py-1"
              value={config[f.key] || ""}
              onChange={(e) => setConfig({ ...config, [f.key]: e.target.value })}
            />
          )}
        </div>
      ))}
      <div className="flex gap-2 mt-4">
        <button className="px-3 py-1 bg-blue-600 text-white rounded" onClick={onSave}>
          Save
        </button>
        <button className="px-3 py-1 bg-gray-200 rounded" onClick={onClose}>
          Cancel
        </button>
      </div>
    </div>
  );
}
