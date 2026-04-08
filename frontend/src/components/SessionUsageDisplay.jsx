import React, { useState, useEffect } from "react";

/**
 * SessionUsageDisplay - Metering widget for header/footer
 * 
 * Shows:
 * - Queries executed
 * - Rows scanned
 * - Total execution time
 * - Estimated cost
 * 
 * Usage:
 * <SessionUsageDisplay sessionId={sessionId} />
 */
export function SessionUsageDisplay({ sessionId, hideOnEmpty = false }) {
  const [usage, setUsage] = useState(null);
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(false);

  // Fetch usage whenever sessionId changes
  useEffect(() => {
    if (!sessionId) return;

    const fetchUsage = async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/sessions/${sessionId}/usage`);
        if (response.ok) {
          const data = await response.json();
          setUsage(data);
        }
      } catch (error) {
        console.error("Failed to fetch usage:", error);
      } finally {
        setLoading(false);
      }
    };

    // Fetch immediately
    fetchUsage();

    // Poll every 10 seconds for updates
    const interval = setInterval(fetchUsage, 10000);
    return () => clearInterval(interval);
  }, [sessionId]);

  if (!usage || (hideOnEmpty && usage.queries_count === 0)) {
    return null;
  }

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
    if (num >= 1000) return (num / 1000).toFixed(1) + "K";
    return num.toString();
  };

  return (
    <div
      style={{
        padding: "8px 16px",
        backgroundColor: "#1a1a1a",
        borderRadius: "8px",
        border: "1px solid #333",
        fontSize: "13px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        gap: "16px",
      }}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        style={{
          background: "none",
          border: "none",
          color: "#ddd",
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          gap: "8px",
          fontSize: "13px",
          fontWeight: "500",
        }}
      >
        <span>📊 Session Usage</span>
        <span style={{ color: "#888", fontSize: "11px" }}>
          {expanded ? "▼" : "▶"}
        </span>
      </button>

      {!expanded && (
        <div style={{ display: "flex", gap: "16px", color: "#aaa" }}>
          <div>
            <span style={{ color: "#888" }}>Queries:</span> {usage.queries_count}
          </div>
          <div>
            <span style={{ color: "#888" }}>Rows:</span> {formatNumber(usage.rows_scanned_total)}
          </div>
          <div>
            <span style={{ color: "#888" }}>Time:</span> {usage.execution_time_total}ms
          </div>
        </div>
      )}

      {expanded && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, 1fr)",
            gap: "16px",
            flex: 1,
            fontSize: "12px",
          }}
        >
          <div>
            <div style={{ color: "#888", marginBottom: "2px" }}>Queries</div>
            <div style={{ fontSize: "16px", fontWeight: "bold", color: "#00d084" }}>
              {usage.queries_count}
            </div>
          </div>
          <div>
            <div style={{ color: "#888", marginBottom: "2px" }}>Rows Scanned</div>
            <div style={{ fontSize: "16px", fontWeight: "bold", color: "#00d084" }}>
              {formatNumber(usage.rows_scanned_total)}
            </div>
          </div>
          <div>
            <div style={{ color: "#888", marginBottom: "2px" }}>Total Time</div>
            <div style={{ fontSize: "16px", fontWeight: "bold", color: "#00d084" }}>
              {(usage.execution_time_total / 1000).toFixed(2)}s
            </div>
          </div>
          <div>
            <div style={{ color: "#888", marginBottom: "2px" }}>Cost</div>
            <div style={{ fontSize: "16px", fontWeight: "bold", color: "#ffb800" }}>
              ${usage.cost_spent.toFixed(2)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
