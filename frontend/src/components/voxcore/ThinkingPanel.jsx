import "./ThinkingPanel.css";

export default function ThinkingPanel({ steps }) {
  if (!steps || steps.length === 0) return null;
  return (
    <div className="thinking-panel">
      <h3>🧠 AI Thinking</h3>
      <ul>
        {steps.map((step, i) => (
          <li key={i}>{step}</li>
        ))}
      </ul>
    </div>
  );
}
