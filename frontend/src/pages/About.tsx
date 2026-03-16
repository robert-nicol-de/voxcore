import React from "react";
const About: React.FC = () => (
  <div className="section">
    <h1 className="section-title">About VoxCore</h1>
    <div className="card" style={{ maxWidth: 700, margin: '0 auto' }}>
      <h3>Our Mission</h3>
      <p>AI systems are rapidly gaining access to enterprise data.<br />VoxCore ensures those interactions remain secure, transparent, and controlled.</p>
      <h3 style={{ marginTop: 32 }}>Why VoxCore Exists</h3>
      <p>AI governance is essential for protecting production databases from uncontrolled queries.</p>
      <h3 style={{ marginTop: 32 }}>Future Vision</h3>
      <p>VoxCore will become the global standard for AI database governance.</p>
    </div>
    {/* CTA */}
    <div style={{ marginTop: 48 }}>
      <button className="btn-primary">Contact Us</button>
    </div>
  </div>
);
export default About;
