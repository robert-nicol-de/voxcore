import React from "react";

const SolutionSection: React.FC = () => (
  <section className="solution-section">
    <h2>Meet VoxCore</h2>
    <p>VoxCore acts as a governance layer between AI and your database,<br />ensuring every query is inspected before execution.</p>
    <div className="solution-diagram">
      <div className="diagram-item">AI Tool</div>
      <div className="diagram-arrow">↓</div>
      <div className="diagram-item highlighted">VoxCore Governance Layer</div>
      <div className="diagram-arrow">↓</div>
      <div className="diagram-item">Production Database</div>
    </div>
    <div className="solution-caption">Every query becomes safe, auditable, and policy-compliant.</div>
  </section>
);

export default SolutionSection;
