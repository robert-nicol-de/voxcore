import React from "react";

const PlatformCapabilities: React.FC = () => (
  <section className="features">
    <div className="section">
      <h2>The VoxCore Platform</h2>
      <p>Enterprise tools for governing AI-generated database queries.</p>
      <div className="feature-grid">
        <div className="feature">
          <h3>Dashboard</h3>
          <p>Monitor AI activity across databases</p>
        </div>
        <div className="feature">
          <h3>Database Manager</h3>
          <p>Connect and manage data sources</p>
        </div>
        <div className="feature">
          <h3>SQL Assistant</h3>
          <p>Generate and validate SQL safely</p>
        </div>
        <div className="feature">
          <h3>Query Activity Monitor</h3>
          <p>Track every AI-generated query</p>
        </div>
        <div className="feature">
          <h3>AI Query Sandbox</h3>
          <p>Test queries before production</p>
        </div>
        <div className="feature">
          <h3>Policy Engine</h3>
          <p>Define governance rules</p>
        </div>
        <div className="feature">
          <h3>Schema Intelligence</h3>
          <p>Understand database structure</p>
        </div>
      </div>
    </div>
  </section>
);

export default PlatformCapabilities;
