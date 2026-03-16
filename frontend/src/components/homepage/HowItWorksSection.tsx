import React from "react";

const HowItWorksSection: React.FC = () => (
  <section className="how-it-works-section">
    <div className="how-it-works-content">
      <div className="how-it-works-left">
        <ol className="how-pipeline-list">
          <li>User Prompt</li>
          <li>AI Generates SQL</li>
          <li>VoxCore Query Inspector</li>
          <li>AI Risk Engine</li>
          <li>Policy Engine</li>
          <li>Sandbox Execution</li>
          <li>Production Database</li>
        </ol>
      </div>
      <div className="how-it-works-right">
        <ul className="feature-list">
          <li>✔ SQL structure inspection</li>
          <li>✔ AI risk analysis</li>
          <li>✔ policy enforcement</li>
          <li>✔ sandbox testing</li>
          <li>✔ audit logging</li>
        </ul>
      </div>
    </div>
  </section>
);

export default HowItWorksSection;
