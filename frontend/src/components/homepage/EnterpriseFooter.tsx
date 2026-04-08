import React from "react";

const EnterpriseFooter: React.FC = () => (
  <footer className="footer">
    <div className="section">
      <div className="footer-grid">
        <div>
          <h4>Product</h4>
          <a href="#platform">Platform</a>
          <a href="#how-it-works">How It Works</a>
          <a href="#security">Security</a>
          <a href="#pricing">Pricing</a>
        </div>
        <div>
          <h4>Company</h4>
          <a href="#about">About</a>
          <a href="#contact">Contact</a>
          <a href="#careers">Careers</a>
        </div>
        <div>
          <h4>Resources</h4>
          <a href="#docs">Documentation</a>
          <a href="#api">API</a>
          <a href="#playground">Playground</a>
          <a href="#blog">Blog</a>
        </div>
        <div>
          <h4>Legal</h4>
          <a href="#privacy">Privacy</a>
          <a href="#terms">Terms</a>
          <a href="#security">Security</a>
        </div>
      </div>
      <p className="copyright">© {new Date().getFullYear()} VoxCore. All rights reserved.</p>
    </div>
  </footer>
);

export default EnterpriseFooter;
