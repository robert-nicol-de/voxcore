import React from "react";

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

const ErrorState: React.FC<ErrorStateProps> = ({ message, onRetry }) => (
  <div style={{
    color: "#ff4d4f",
    background: "#1a2233",
    border: "1px solid #ff4d4f",
    borderRadius: 10,
    padding: 32,
    margin: 24,
    textAlign: "center",
    fontWeight: 600,
    fontSize: 18,
    boxShadow: "0 2px 12px rgba(255,77,79,0.08)",
  }}>
    <div>{message}</div>
    {onRetry && (
      <button
        style={{
          marginTop: 18,
          padding: "8px 24px",
          background: "#ff4d4f",
          color: "#fff",
          border: "none",
          borderRadius: 6,
          fontWeight: 700,
          cursor: "pointer",
        }}
        onClick={onRetry}
      >
        Retry
      </button>
    )}
  </div>
);

export default ErrorState;
