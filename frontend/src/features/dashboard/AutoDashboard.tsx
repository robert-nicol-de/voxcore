import { GoogleSheetsConnector } from "./GoogleSheetsConnector";
import React, { useState } from "react";
import ChartRenderer from "./ChartRenderer";

export function AutoDashboard({ charts, insights }) {
  return (
    <div className="space-y-6">
      {/* Insights */}
      <div className="grid grid-cols-3 gap-4">
        {insights.map((i) => (
          <div key={i.id} className="p-4 bg-white rounded-xl border">
            {i.insight}
          </div>
        ))}
      </div>
      {/* Charts */}
      <div className="grid grid-cols-2 gap-4">
        {charts.map((c, i) => (
          <ChartRenderer key={i} config={c} />
        ))}
      </div>
    </div>
  );
}

export default function AutoDashboardGenerator() {
  const [charts, setCharts] = useState([]);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFile = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch("/api/data/upload", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    setCharts(data.charts || []);
    setInsights(data.insights || []);
    setLoading(false);
  };

  return (
    <div className="space-y-8">
      <div className="flex gap-4 items-center">
        <input type="file" accept=".csv,.xlsx" onChange={handleFile} />
        <GoogleSheetsConnector />
      </div>
      {loading && <div>Loading...</div>}
      {(charts.length > 0 || insights.length > 0) && (
        <AutoDashboard charts={charts} insights={insights} />
      )}
    </div>
  );
}
