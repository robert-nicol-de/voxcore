import React, { useState } from "react";
import "./AuditPanel.css";

interface AuditPanelProps {
  audit: {
    reasoning: string;
    selectedTables?: string[];
    foundColumns?: string[];
    generatedSQL?: string;
    confidence?: number;
    schemaUsed?: boolean;
    [key: string]: any;
  };
}

const AuditPanel: React.FC<AuditPanelProps> = ({ audit }) => {
  const [open, setOpen] = useState(false);
  const confidencePercent = audit.confidence !== undefined ? Math.round((audit.confidence || 0) * 100) : null;

  return (
    <div className="audit-panel">
      <button className="audit-toggle" onClick={() => setOpen(v => !v)}>
        {open ? "▼ Hide AI Reasoning" : "▲ Show AI Reasoning"}
      </button>
      {open && (
        <div className="audit-details">
          <div className="audit-section">
            <strong>🧠 Reasoning</strong>
            <div>{audit.reasoning}</div>
          </div>
          {audit.selectedTables && (
            <div className="audit-section">
              <strong>Selected:</strong> {audit.selectedTables.join(", ")}
            </div>
          )}
          {audit.foundColumns && (
            <div className="audit-section">
              <strong>Found:</strong> {audit.foundColumns.join(", ")}
            </div>
          )}
          {audit.generatedSQL && (
            <div className="audit-section">
              <strong>Generated SQL:</strong>
              <pre>{audit.generatedSQL}</pre>
            </div>
          )}
          {confidencePercent !== null && (
            <div className="audit-section">
              <strong>Confidence:</strong> {confidencePercent}%
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AuditPanel;
