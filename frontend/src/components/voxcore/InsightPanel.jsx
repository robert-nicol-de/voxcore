
import "./InsightPanel.css";


export default function InsightPanel({ insights }) {
  if (!insights) return null;

  // Always normalize to narrative, never JSON
  let safeText = typeof insights === "string"
    ? insights
    : insights?.insight || "Insight detected";
  let key_takeaway = (typeof insights === "object" && insights !== null && insights.key_takeaway) ? insights.key_takeaway : "";
  let confidence = (typeof insights === "object" && insights !== null && typeof insights.confidence === "number") ? insights.confidence : null;

  return (
    <div className="insight-card">
      <h3>🧠 Insight</h3>
      {safeText && (
        <p className="text-[var(--text-primary)]">{safeText}</p>
      )}
      {key_takeaway && (
        <div className="insight-takeaway">💡 {key_takeaway}</div>
      )}
      {typeof confidence === "number" && (
        <div className="confidence-bar" style={{ marginTop: 12 }}>
          Confidence: {Math.round(confidence * 100)}%
          <div style={{ background: '#3b82f6', height: 6, borderRadius: 3, width: `${Math.round(confidence * 100)}%`, marginTop: 4 }} />
        </div>
      )}
    </div>
  );
}
