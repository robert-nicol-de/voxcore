import React, { useState } from "react";

/**
 * WhyThisAnswer — Pure Renderer of Backend Metadata
 * 
 * CRITICAL: This modal displays ONLY what the backend provides,
 * backed by ExecutionMetadata. It does NOT infer or guess.
 * 
 * This is the "source of truth" view for executives.
 */
export function WhyThisAnswer({ result, metadata, isOpen, onClose }) {
  if (!isOpen) return null;
  
  // Use metadata if provided, fall back to result for backward compatibility
  const data = metadata || result;
  
  if (!data) return null;

  // Modal styles
  const modalOverlayStyle = {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0, 0, 0, 0.7)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
    backdropFilter: "blur(4px)",
  };

  const modalStyle = {
    backgroundColor: "#1a1a1a",
    borderRadius: "12px",
    border: "1px solid #333",
    maxWidth: "800px",
    width: "90%",
    maxHeight: "85vh",
    overflowY: "auto",
    padding: 0,
    boxShadow: "0 10px 40px rgba(0, 0, 0, 0.5)",
  };

  const headerStyle = {
    padding: "24px",
    borderBottom: "1px solid #333",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: "#1f1f1f",
  };

  const contentStyle = {
    padding: "24px",
  };

  return (
    <div style={modalOverlayStyle} onClick={onClose}>
      <div style={modalStyle} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={headerStyle}>
          <h2 style={{ margin: 0, fontSize: "20px", fontWeight: "700" }}>
            🧠 Why This Answer?
          </h2>
          <button
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              fontSize: "24px",
              cursor: "pointer",
              color: "#888",
              padding: "0",
              width: "32px",
              height: "32px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              borderRadius: "6px",
              transition: "all 0.2s",
            }}
            onMouseOver={(e) => {
              e.target.style.backgroundColor = "#2a2a2a";
              e.target.style.color = "#fff";
            }}
            onMouseOut={(e) => {
              e.target.style.backgroundColor = "transparent";
              e.target.style.color = "#888";
            }}
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div style={contentStyle}>
          {/* Execution Info — FROM METADATA */}
          <div style={{ marginBottom: "24px", padi: "12px", backgroundColor: "#0f0f0f", borderRadius: "8px", border: "1px solid #333" }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px" }}>
              <div>
                <div style={{ color: "#888", fontSize: "11px", marginBottom: "4px" }}>Query ID</div>
                <div style={{ color: "#0087ff", fontFamily: "monospace", fontSize: "11px", wordBreak: "break-all" }}>
                  {data.query_id}
                </div>
              </div>
              <div>
                <div style={{ color: "#888", fontSize: "11px", marginBottom: "4px" }}>Execution Time</div>
                <div style={{ color: "#00bcd4", fontWeight: "700", fontSize: "14px" }}>
                  {Math.round(data.execution_time_ms)}ms
                </div>
              </div>
              <div>
                <div style={{ color: "#888", fontSize: "11px", marginBottom: "4px" }}>Validation Status</div>
                <div style={{ color: data.validation_status === "valid" ? "#4caf50" : "#f44336", fontWeight: "600", fontSize: "12px" }}>
                  {data.validation_status?.toUpperCase()}
                </div>
              </div>
            </div>
          </div>

          {/* Original SQL — FROM METADATA.sql */}
          {data.sql && (
            <div style={{ marginBottom: "24px" }}>
              <h3 style={{ margin: "0 0 12px 0", fontSize: "12px", fontWeight: "600", color: "#ffffff" }}>
                📌 Original Query (as submitted)
              </h3>
              <div
                style={{
                  padding: "12px",
                  backgroundColor: "#0f0f0f",
                  borderRadius: "6px",
                  border: "1px solid #333",
                  fontFamily: "monospace",
                  fontSize: "11px",
                  color: "#ddd",
                  lineHeight: "1.5",
                  whiteSpace: "pre-wrap",
                  wordBreak: "break-word",
                }}
              >
                {data.sql}
              </div>
            </div>
          )}

          {/* Final SQL (with transformations) — FROM METADATA.final_sql */}
          {data.final_sql && data.final_sql !== data.sql && (
            <div style={{ marginBottom: "24px" }}>
              <h3 style={{ margin: "0 0 12px 0", fontSize: "12px", fontWeight: "600", color: "#ffb800" }}>
                ⚙️ Final Query (after transformation)
              </h3>
              <div style={{ marginBottom: "8px", fontSize: "11px", color: "#888" }}>
                Query was rewritten to add: tenant isolation, optimization, filters
              </div>
              <div
                style={{
                  padding: "12px",
                  backgroundColor: "#0f0f0f",
                  borderRadius: "6px",
                  border: "1px solid #333",
                  fontFamily: "monospace",
                  fontSize: "11px",
                  color: "#ddd",
                  lineHeight: "1.5",
                  maxHeight: "250px",
                  overflowY: "auto",
                  whiteSpace: "pre-wrap",
                  wordBreak: "break-word",
                }}
              >
                {data.final_sql}
              </div>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(data.final_sql);
                  alert("SQL copied to clipboard!");
                }}
                style={{
                  marginTop: "8px",
                  padding: "6px 12px",
                  backgroundColor: "#2a2a2a",
                  border: "1px solid #444",
                  borderRadius: "4px",
                  color: "#ddd",
                  cursor: "pointer",
                  fontSize: "11px",
                  fontWeight: "600",
                  transition: "all 0.2s",
                }}
                onMouseOver={(e) => (e.target.style.backgroundColor = "#3a3a3a")}
                onMouseOut={(e) => (e.target.style.backgroundColor = "#2a2a2a")}
              >
                📋 Copy SQL
              </button>
            </div>
          )}

          {/* Policies Applied — FROM METADATA.policies_applied */}
          {data.policies_applied && data.policies_applied.length > 0 && (
            <div style={{ marginBottom: "24px" }}>
              <h3 style={{ margin: "0 0 12px 0", fontSize: "12px", fontWeight: "600", color: "#4caf50" }}>
                ✔️ Governance Policies Applied
              </h3>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
                {data.policies_applied.map((policy, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: "10px",
                      backgroundColor: "#0f0f0f",
                      borderRadius: "4px",
                      border: "1px solid #333",
                      fontSize: "11px",
                    }}
                  >
                    <div style={{ color: "#4caf50", fontWeight: "600", marginBottom: "3px" }}>
                      {policy.name}
                    </div>
                    <div style={{ color: "#888", fontSize: "10px", marginBottom: "2px" }}>
                      Effect: <span style={{ color: "#0087ff" }}>{policy.effect}</span>
                    </div>
                    {policy.column && (
                      <div style={{ color: "#888", fontSize: "10px", marginBottom: "2px" }}>
                        Column: <span style={{ color: "#ffb800" }}>{policy.column}</span>
                      </div>
                    )}
                    {policy.reason && (
                      <div style={{ color: "#666", fontSize: "10px", fontStyle: "italic" }}>
                        {policy.reason}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Columns Masked — FROM METADATA.columns_masked */}
          {data.columns_masked && data.columns_masked.length > 0 && (
            <div style={{ marginBottom: "24px" }}>
              <h3 style={{ margin: "0 0 12px 0", fontSize: "12px", fontWeight: "600", color: "#f44336" }}>
                🔐 Columns Masked
              </h3>
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                {data.columns_masked.map((col, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: "6px 10px",
                      backgroundColor: "#f4433620",
                      border: "1px solid #f44336",
                      borderRadius: "4px",
                      fontSize: "11px",
                      color: "#f44336",
                      fontWeight: "600",
                    }}
                  >
                    {col}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Execution Flags — FROM METADATA.execution_flags */}
          {data.execution_flags && data.execution_flags.length > 0 && (
            <div style={{ marginBottom: "24px" }}>
              <h3 style={{ margin: "0 0 12px 0", fontSize: "12px", fontWeight: "600", color: "#9c27b0" }}>
                ⚡ What Actually Happened
              </h3>
              <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
                {data.execution_flags.map((flag, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: "6px 10px",
                      backgroundColor: "#9c27b020",
                      border: "1px solid #9c27b0",
                      borderRadius: "4px",
                      fontSize: "10px",
                      color: "#9c27b0",
                      fontWeight: "600",
                      fontFamily: "monospace",
                    }}
                    title={`Execution flag: ${flag}`}
                  >
                    {flag.replace(/_/g, " ")}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Performance Metrics — FROM METADATA */}
          <div style={{ marginBottom: "24px" }}>
            <h3 style={{ margin: "0 0 12px 0", fontSize: "12px", fontWeight: "600", color: "#00bcd4" }}>
              📊 Performance Metrics
            </h3>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "8px" }}>
              <div style={{ padding: "10px", backgroundColor: "#0f0f0f", borderRadius: "4px", border: "1px solid #333" }}>
                <div style={{ color: "#888", fontSize: "10px", marginBottom: "3px" }}>Rows Returned</div>
                <div style={{ color: "#00bcd4", fontWeight: "700", fontSize: "14px" }}>
                  {data.rows_returned}
                </div>
              </div>
              <div style={{ padding: "10px", backgroundColor: "#0f0f0f", borderRadius: "4px", border: "1px solid #333" }}>
                <div style={{ color: "#888", fontSize: "10px", marginBottom: "3px" }}>Rows Scanned</div>
                <div style={{ color: "#00bcd4", fontWeight: "700", fontSize: "14px" }}>
                  {(data.rows_scanned || 0).toLocaleString()}
                </div>
              </div>
              <div style={{ padding: "10px", backgroundColor: "#0f0f0f", borderRadius: "4px", border: "1px solid #333" }}>
                <div style={{ color: "#888", fontSize: "10px", marginBottom: "3px" }}>Cost Score</div>
                <div style={{ color: "#ffb800", fontWeight: "700", fontSize: "14px" }}>
                  {data.cost_score}/100
                </div>
              </div>
            </div>
          </div>

          {/* Signature — FROM METADATA.signature */}
          {data.signature && (
            <div style={{ padding: "10px", backgroundColor: "#0f0f0f", borderRadius: "4px", border: "1px solid #333", fontSize: "11px" }}>
              <div style={{ color: "#888", marginBottom: "4px" }}>
                ✔️ Verified Execution
              </div>
              <div style={{ color: "#666", fontFamily: "monospace", fontSize: "10px", wordBreak: "break-all" }}>
                {data.signature.substring(0, 32)}...
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
