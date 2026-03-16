import React from "react";

const ProblemSection: React.FC = () => (
  <section className="problem-section">
    <h2>AI + Databases Without Guardrails Is Dangerous</h2>
    <p>AI tools can generate powerful SQL queries in seconds.<br />But connecting them directly to production databases creates serious risk.</p>
    <div className="risk-cards">
      <div className="risk-card">Destructive queries</div>
      <div className="risk-card">Sensitive data exposure</div>
      <div className="risk-card">Unauthorized access</div>
      <div className="risk-card">Compliance violations</div>
    </div>
  </section>
);

export default ProblemSection;
