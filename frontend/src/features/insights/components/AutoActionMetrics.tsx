import React from "react";

export type Metrics = {
  automation_rate: number;
  success_rate: number;
  total_impact: number;
};

export function AutoActionMetrics({ metrics }: { metrics: Metrics }) {
  // Status color for success rate
  let statusColor = "text-gray-700";
  if (metrics.success_rate > 0.8) statusColor = "text-green-600";
  else if (metrics.success_rate < 0.5) statusColor = "text-red-500";

  return (
    <div className="grid grid-cols-3 gap-4 mb-6">
      {/* Automation Rate */}
      <div className="p-4 bg-white rounded-2xl shadow-sm border">
        <div className="text-sm text-gray-500 flex items-center gap-1">
          <span role="img" aria-label="automation">⚡</span> Automation Rate
        </div>
        <div className="text-xl font-semibold">{(metrics.automation_rate * 100).toFixed(0)}%</div>
      </div>
      {/* Success Rate */}
      <div className="p-4 bg-white rounded-2xl shadow-sm border">
        <div className="text-sm text-gray-500 flex items-center gap-1">
          <span role="img" aria-label="success">🎯</span> Success Rate
        </div>
        <div className={`text-xl font-semibold ${statusColor}`}>
          {(metrics.success_rate * 100).toFixed(0)}%
        </div>
      </div>
      {/* Total Impact */}
      <div className="p-4 bg-white rounded-2xl shadow-sm border">
        <div className="text-sm text-gray-500 flex items-center gap-1">
          <span role="img" aria-label="impact">📈</span> Impact Generated
        </div>
        <div className="text-xl font-semibold text-green-600">
          +{(metrics.total_impact * 100).toFixed(1)}%
        </div>
      </div>
    </div>
  );
}
