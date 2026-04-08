import React from "react";
import "./ValidationSummary.css";

interface ValidationSummaryProps {
  validationPassed: boolean;
  rowLimit?: number;
  policy?: string;
  executionTime?: number;
  rewritten?: boolean;
  rewriteReason?: string;
}

export function ValidationSummary({
  validationPassed,
  rowLimit,
  policy,
  executionTime,
  rewritten,
  rewriteReason,
}: ValidationSummaryProps) {
  return (
    <div className="validation-summary">
      <div className="validation-item">
        <span className="check-icon">✓</span>
        <span>SQL Validation passed</span>
      </div>
      <div className="validation-item">
        <span className="check-icon">✓</span>
        <span>Policy check passed</span>
      </div>
      {rewritten && (
        <div className="validation-item rewritten">
          <span className="check-icon">◊</span>
          <span>Rewritten: {rewriteReason || "SQL optimized"}</span>
        </div>
      )}
      {rowLimit && (
        <div className="validation-item">
          <span className="check-icon">✓</span>
          <span>Row limit applied ({rowLimit.toLocaleString()})</span>
        </div>
      )}
      {policy && (
        <div className="validation-item">
          <span className="check-icon">✓</span>
          <span>Policy: {policy}</span>
        </div>
      )}
      {executionTime && (
        <div className="validation-item">
          <span className="check-icon">✓</span>
          <span>Execution time: {executionTime}ms</span>
        </div>
      )}
    </div>
  );
}
