import React from "react";
const Playground: React.FC = () => (
  <div className="section">
    <h1 className="section-title">VoxCore Playground</h1>
    <div className="card" style={{ maxWidth: 700, margin: '0 auto' }}>
      <h3>Experience VoxCore Instantly</h3>
      <p>Try the VoxCore Playground with a live dataset.<br />Prompt suggestions:</p>
      <ul>
        <li>Show revenue by region</li>
        <li>Which products are declining</li>
        <li>What drove growth last quarter</li>
      </ul>
    </div>
    {/* CTA */}
    <div style={{ marginTop: 48 }}>
      <button className="btn-primary">Open Playground</button>
    </div>
  </div>
);
export default Playground;
