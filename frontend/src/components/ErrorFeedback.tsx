import React from "react";
import "./ErrorFeedback.css";

const ErrorFeedback: React.FC<{ reason: string }> = ({ reason }) => (
  <div className="error-feedback">
    <div className="error-title">Query blocked by governance policy</div>
    <div className="error-reason">Reason: {reason}</div>
  </div>
);
export default ErrorFeedback;
