import React, { useState } from "react";

export function SemanticModelBuilder({ columns, onSave }) {
  const [model, setModel] = useState({});

  const update = (col, type) => {
    setModel((prev) => ({
      ...prev,
      [col]: type,
    }));
  };

  return (
    <div className="space-y-3">
      <h3 className="font-semibold">Define Your Data</h3>
      {columns.map((col) => (
        <div key={col} className="flex justify-between">
          <span>{col}</span>
          <select onChange={(e) => update(col, e.target.value)}>
            <option>Ignore</option>
            <option>Dimension</option>
            <option>Metric (SUM)</option>
            <option>Metric (COUNT)</option>
            <option>Date</option>
          </select>
        </div>
      ))}
      <button
        onClick={() => onSave(model)}
        className="px-4 py-2 bg-black text-white rounded-lg"
      >
        Save Model
      </button>
    </div>
  );
}
