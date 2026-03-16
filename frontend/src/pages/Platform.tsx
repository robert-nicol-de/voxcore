import React from "react";
const Platform: React.FC = () => (
  <div className="section">
    <h1 className="section-title">The VoxCloud Platform</h1>
    {/* Platform Overview, Core Modules, Architecture Diagram, Integration Support, CTA */}
    <div className="grid">
      <div className="card"><h3>Dashboard</h3><p>Monitor AI activity across databases</p></div>
      <div className="card"><h3>Database Manager</h3><p>Connect and manage data sources</p></div>
      <div className="card"><h3>SQL Assistant</h3><p>Generate and validate SQL safely</p></div>
      <div className="card"><h3>Query Activity Monitor</h3><p>Track every AI-generated query</p></div>
      <div className="card"><h3>AI Query Sandbox</h3><p>Test queries before production</p></div>
      <div className="card"><h3>Policy Engine</h3><p>Define governance rules</p></div>
      <div className="card"><h3>Schema Intelligence</h3><p>Understand database structure</p></div>
    </div>
    {/* CTA */}
    <div style={{ marginTop: 48 }}>
      <button className="btn-primary">Launch VoxCloud</button>
    </div>
  </div>
);
export default Platform;
