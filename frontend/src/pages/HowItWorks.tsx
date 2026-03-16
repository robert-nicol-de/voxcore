import React from "react";
const HowItWorks: React.FC = () => (
  <div className="section">
    <h1 className="section-title">How VoxCore Works</h1>
    <div className="card" style={{ maxWidth: 700, margin: '0 auto' }}>
      <h3>AI Query Security Pipeline</h3>
      <ol style={{ fontSize: 18, marginTop: 24 }}>
        <li>User Prompt – AI asks a database question</li>
        <li>AI Generates SQL – Query created automatically</li>
        <li>VoxCore Query Inspector – Structure and intent analyzed</li>
        <li>Risk Engine – Detects dangerous operations</li>
        <li>Policy Engine – Applies governance rules</li>
        <li>Sandbox Execution – Query tested safely</li>
        <li>Production Database – Approved queries executed</li>
      </ol>
    </div>
    {/* CTA */}
    <div style={{ marginTop: 48 }}>
      <button className="btn-primary">Launch VoxCloud</button>
    </div>
  </div>
);
export default HowItWorks;
