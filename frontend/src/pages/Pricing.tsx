import React from "react";
const Pricing: React.FC = () => (
  <div className="section">
    <h1 className="section-title">Pricing</h1>
    <div className="grid">
      <div className="card">
        <h3>Starter</h3>
        <p>$49/month</p>
        <ul>
          <li>Basic features</li>
          <li>AI query inspection</li>
        </ul>
      </div>
      <div className="card">
        <h3>Professional</h3>
        <p>$199/month</p>
        <ul>
          <li>Advanced policies</li>
          <li>Audit logs</li>
          <li>SSO</li>
        </ul>
      </div>
      <div className="card">
        <h3>Enterprise</h3>
        <p>Custom pricing</p>
        <ul>
          <li>Dedicated support</li>
          <li>Compliance readiness</li>
        </ul>
      </div>
    </div>
    {/* CTA */}
    <div style={{ marginTop: 48 }}>
      <button className="btn-primary">Contact Sales</button>
    </div>
  </div>
);
export default Pricing;
