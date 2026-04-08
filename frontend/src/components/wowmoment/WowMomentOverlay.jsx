import { useState } from "react";
import "./WowMomentOverlay.css";

export default function WowMomentOverlay({ riskScore, reason, onClose, onTryAnother }) {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) {
    return null;
  }

  const isBlocked = riskScore >= 70; // HIGH risk

  return (
    <div className="wow-overlay">
      <div className="wow-card">
        <button className="wow-close" onClick={() => setDismissed(true)}>✕</button>

        <div className="wow-content">
          {isBlocked ? (
            <>
              <div className="wow-icon wow-icon-blocked">⛔</div>
              <h2 className="wow-title">VoxCore Just Saved Your Database</h2>
              <p className="wow-subtitle">This query would have scanned your entire user table</p>

              <div className="wow-explanation">
                <p className="wow-reason">{reason}</p>
                <div className="wow-metric">
                  <span className="label">Risk Score</span>
                  <span className="value">{riskScore}%</span>
                </div>
              </div>

              <div className="wow-cta-container">
                <button className="wow-cta-primary" onClick={onTryAnother}>
                  👉 Try Another Query
                </button>
                <button className="wow-cta-secondary" onClick={() => setDismissed(true)}>
                  Skip for now
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="wow-icon wow-icon-success">✓</div>
              <h2 className="wow-title">Query Approved</h2>
              <p className="wow-subtitle">This query is safe and within policy</p>

              <div className="wow-explanation">
                <p className="wow-reason">{reason}</p>
                <div className="wow-metric">
                  <span className="label">Risk Score</span>
                  <span className="value">{riskScore}%</span>
                </div>
              </div>

              <p className="wow-insight">
                VoxCore is intelligent — it blocks unsafe queries, but allows safe ones.
                You can trust the system.
              </p>

              <button className="wow-cta-primary" onClick={() => setDismissed(true)}>
                👉 Continue
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
