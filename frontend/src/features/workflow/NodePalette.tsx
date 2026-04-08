import React from "react";

const nodeTypes = [
  { type: "action", label: "Action", color: "#222" },
  { type: "slack", label: "Slack", color: "#ede9fe" },
  { type: "wait", label: "Wait", color: "#fef9c3" },
  { type: "evaluate", label: "Evaluate", color: "#dcfce7" },
  { type: "email", label: "Email", color: "#f0f9ff" },
  { type: "condition", label: "Condition", color: "#FEF3C7", border: "2px solid #F59E0B" },
  { type: "loop", label: "Loop/Retry", color: "#f3f4f6", border: "2px dashed #6b7280" },
  { type: "score", label: "Score", color: "#fef9c3", border: "2px solid #f59e0b" }
];

export default function NodePalette({ onNodeDrop }) {
  return (
    <div className="w-40 p-4 bg-white rounded-xl border h-[600px] flex flex-col gap-4">
      <div className="font-bold text-lg mb-2">+ Add Step</div>
      {nodeTypes.map((n) => (
        <button
          key={n.type}
          className="w-full py-2 rounded-lg mb-2 shadow text-left"
          style={{ background: n.color, border: n.border || "1px solid #e5e7eb" }}
          onClick={() => onNodeDrop(n.type)}
        >
          {n.label}
        </button>
      ))}
    </div>
  );
}
