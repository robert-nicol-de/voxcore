import React from "react";
import "./SmartLoading.css";

const steps = [
  "Parsing query structure",
  "Identifying tables",
  "Detecting sensitive fields",
  "Applying governance policies"
];

const SmartLoading: React.FC<{ analyzing?: boolean }> = ({ analyzing = true }) => (
  <div className="smart-loading">
    <div className="loading-title">Analyzing SQL Query</div>
    <ul className="loading-steps">
      {steps.map((step, idx) => (
        <li key={step} className="loading-step">
          <span className="loading-check">✓</span> {step}
        </li>
      ))}
    </ul>
  </div>
);
export default SmartLoading;
