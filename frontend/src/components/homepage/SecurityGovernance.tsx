import React from "react";

const SecurityGovernance: React.FC = () => (
  <section className="security-governance-section">
    <h2>Built for Secure AI Adoption</h2>
    <div className="security-governance-content">
      <div className="security-left">
        <p>VoxCore provides complete visibility and control<br />over AI database interactions.</p>
      </div>
      <div className="security-right">
        <ul className="security-feature-list">
          <li>Query inspection</li>
          <li>AI risk scoring</li>
          <li>Sandbox execution</li>
          <li>Policy enforcement</li>
          <li>Query activity logs</li>
          <li>Sensitive data detection</li>
        </ul>
      </div>
    </div>
  </section>
);

export default SecurityGovernance;
