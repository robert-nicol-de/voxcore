import React, { useState } from "react";

interface Metrics {
  executionTime: string;
  rowsReturned: number;
  tablesScanned: number;
  indexesUsed: boolean;
}

export const QueryMetrics: React.FC = () => {
  const [metrics] = useState<Metrics>({
    executionTime: "42 ms",
    rowsReturned: 120,
    tablesScanned: 2,
    indexesUsed: true,
  });

  return (
    <div className="query-metrics">
      <h2>⚡ Execution Metrics</h2>

      <div className="metrics-grid">
        <div className="metric">
          <span className="label">Execution Time</span>
          <span className="value">{metrics.executionTime}</span>
        </div>

        <div className="metric">
          <span className="label">Rows Returned</span>
          <span className="value">{metrics.rowsReturned}</span>
        </div>

        <div className="metric">
          <span className="label">Tables Scanned</span>
          <span className="value">{metrics.tablesScanned}</span>
        </div>

        <div className="metric">
          <span className="label">Indexes Used</span>
          <span className="value metric-status">
            {metrics.indexesUsed ? "✓ YES" : "✗ NO"}
          </span>
        </div>
      </div>
    </div>
  );
};
