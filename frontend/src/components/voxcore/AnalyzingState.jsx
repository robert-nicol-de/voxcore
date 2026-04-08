import { useState, useEffect } from "react";

export default function AnalyzingState() {
  const [dots, setDots] = useState("");

  useEffect(() => {
    const interval = setInterval(() => {
      setDots((prev) => (prev.length >= 3 ? "" : prev + "."));
    }, 400);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      style={{
        background: "linear-gradient(135deg, #0B0F19 0%, #111827 100%)",
        border: "2px solid rgba(0, 172, 255, 0.3)",
        borderRadius: 16,
        padding: 32,
        marginTop: 24,
        marginBottom: 24,
        display: "flex",
        alignItems: "center",
        gap: 16,
      }}
    >
      {/* Animated spinner */}
      <div
        style={{
          width: 32,
          height: 32,
          borderRadius: "50%",
          border: "3px solid rgba(0, 172, 255, 0.2)",
          borderTopColor: "#0088ff",
          animation: "spin 0.8s linear infinite",
          flexShrink: 0,
        }}
      />

      {/* Text with typing animation */}
      <div style={{ display: "flex", alignItems: "center" }}>
        <span style={{ fontSize: 15, color: "#0088ff", fontWeight: 600 }}>
          Analyzing query
          <span style={{ display: "inline-block", width: "24px", textAlign: "left" }}>
            {dots}
          </span>
        </span>
      </div>

      <style>{`
        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  );
}
