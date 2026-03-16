import React from "react";

const EnterpriseHeader: React.FC = () => (
  <header className="enterprise-header">
    <div className="header-content">
      <div className="logo-group">
        <span className="logo-main">VoxCloud</span>
        <span className="logo-powered">Powered by VoxCore Engine</span>
      </div>
      <nav className="nav-links">
        <a href="#platform">Platform</a>
        <a href="#how-it-works">How It Works</a>
        <a href="#security">Security</a>
        <a href="#pricing">Pricing</a>
        <a href="#about">About</a>
      </nav>
      <div className="header-actions">
        <button className="btn-outline">VoxCore Playground</button>
        <button className="btn-primary">Launch VoxCloud</button>
      </div>
    </div>
  </header>
);

export default EnterpriseHeader;
