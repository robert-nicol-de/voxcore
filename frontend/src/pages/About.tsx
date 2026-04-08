import React from "react";
import Section from "../components/ui/Section";

const About: React.FC = () => (
  <Section id="about" className="about">
    <div className="section">
      <h2>About VoxCore</h2>
      <p className="section-subtitle">
        AI governance is the future of secure, compliant, and auditable data usage.
      </p>
      <div className="card" style={{ maxWidth: 700, margin: "0 auto" }}>
        <h3>Our Mission</h3>
        <p>
          AI systems are rapidly gaining access to enterprise data. VoxCore ensures those interactions remain secure, transparent, and controlled.
        </p>
        <h3 style={{ marginTop: 32 }}>Why VoxCore Exists</h3>
        <p>AI governance is essential for protecting production databases from uncontrolled queries.</p>
        <h3 style={{ marginTop: 32 }}>Future Vision</h3>
        <p>VoxCore will become the global standard for AI database governance.</p>
      </div>
      <div style={{ marginTop: 48 }}>
        <button className="btn-primary">Contact Us</button>
      </div>
    </div>
  </Section>
);

export default About;
