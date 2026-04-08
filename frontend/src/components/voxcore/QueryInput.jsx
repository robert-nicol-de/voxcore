import { useState } from "react";

export default function QueryInput({ onSubmit, value: externalValue, onChange: externalOnChange }) {
  const [query, setQuery] = useState("");
  
  // Support both controlled and uncontrolled modes
  const isControlled = externalValue !== undefined;
  const currentValue = isControlled ? externalValue : query;
  
  const handleChange = (e) => {
    const newValue = e.target.value;
    if (isControlled) {
      externalOnChange?.(newValue);
    } else {
      setQuery(newValue);
    }
  };

  return (
    <div style={{ marginBottom: 20 }}>
      <input
        value={currentValue}
        onChange={handleChange}
        placeholder="Ask your data..."
        style={{
          width: "100%",
          padding: 12,
          borderRadius: "8px",
          border: "1px solid #475569",
          backgroundColor: "#1e293b",
          color: "#ffffff",
          placeholderColor: "#94a3b8",
          fontSize: "14px",
          boxSizing: "border-box",
          transition: "all 0.2s",
          outline: "none"
        }}
        onFocus={(e) => {
          e.target.style.borderColor = "#0087ff";
          e.target.style.boxShadow = "0 0 0 3px rgba(0, 135, 255, 0.1)";
        }}
        onBlur={(e) => {
          e.target.style.borderColor = "#475569";
          e.target.style.boxShadow = "none";
        }}
      />

      <button
        onClick={() => onSubmit(currentValue)}
        style={{
          marginTop: 10,
          padding: "10px 20px",
          backgroundColor: "#0087ff",
          color: "#ffffff",
          border: "none",
          borderRadius: "8px",
          cursor: "pointer",
          fontWeight: "600",
          fontSize: "14px",
          transition: "all 0.2s",
          boxShadow: "0 4px 12px rgba(0, 135, 255, 0.3)"
        }}
        onMouseOver={(e) => {
          e.target.style.backgroundColor = "#0066cc";
          e.target.style.boxShadow = "0 6px 16px rgba(0, 135, 255, 0.4)";
        }}
        onMouseOut={(e) => {
          e.target.style.backgroundColor = "#0087ff";
          e.target.style.boxShadow = "0 4px 12px rgba(0, 135, 255, 0.3)";
        }}
      >
        Run Query
      </button>
    </div>
  );
}
