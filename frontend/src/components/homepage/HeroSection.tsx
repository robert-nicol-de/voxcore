import React from "react";

const HeroSection: React.FC = () => (
  <section className="hero-section">
    <div className="hero-content">
      <div className="hero-left">
        <h1 className="hero-title">The AI Governance Layer<br />For Production Databases</h1>
        <p className="hero-subtitle">Control how AI interacts with your databases.<br />Inspect, validate, and audit every AI-generated SQL query before execution.</p>
        <div className="hero-buttons">
          <button className="btn-primary">Launch VoxCloud</button>
          <button className="btn-outline">VoxCore Playground</button>
        </div>
      </div>
      <div className="hero-right">
        <div className="pipeline-card-glow">
          <ol className="pipeline-list">
            <li>User Prompt</li>
            <li>AI Generates SQL</li>
            <li>VoxCore Query Inspector</li>
            <li>AI Risk Engine</li>
            <li>Policy Engine</li>
            <li>Sandbox Execution</li>
            <li>Production Database</li>
          </ol>
        </div>
      </div>
    </div>
  </section>
);

export default HeroSection;
