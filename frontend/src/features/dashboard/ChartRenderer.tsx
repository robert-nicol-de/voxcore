import React from "react";

export default function ChartRenderer({ config }) {
  // Simple chart stub, replace with real chart lib (e.g., Recharts, Chart.js)
  return (
    <div className="p-4 bg-gray-50 rounded-xl border text-xs">
      <div>Chart: {config.type}</div>
      <div>X: {config.x}</div>
      <div>Y: {config.y}</div>
    </div>
  );
}
