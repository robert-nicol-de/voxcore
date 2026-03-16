import React from "react";
const Security: React.FC = () => (
  <div className="section">
    <h1 className="section-title">Built for Secure AI Adoption</h1>
    <div className="card" style={{ maxWidth: 700, margin: '0 auto' }}>
      <ul style={{ fontSize: 18, marginTop: 24 }}>
        <li>✔ Query inspection</li>
        <li>✔ AI risk scoring</li>
        <li>✔ Sandbox execution</li>
        <li>✔ Policy enforcement</li>
        <li>✔ Query activity logs</li>
        <li>✔ Sensitive data detection</li>
        <li>✔ Access control</li>
        <li>✔ Encryption</li>
        <li>✔ Monitoring</li>
        <li>✔ Compliance readiness</li>
      </ul>
    </div>
    {/* CTA */}
    <div style={{ marginTop: 48 }}>
      <button className="btn-primary">Launch VoxCloud</button>
    </div>
  </div>
);
export default Security;
