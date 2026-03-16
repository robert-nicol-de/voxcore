import React from "react";

const EnterpriseFooter: React.FC = () => (
  <footer className="enterprise-footer">
    <div className="footer-columns">
      <div className="footer-col">
        <h4>Product</h4>
        <a href="#platform">Platform</a>
        <a href="#how-it-works">How It Works</a>
        <a href="#security">Security</a>
        <a href="#pricing">Pricing</a>
      </div>
      <div className="footer-col">
        <h4>Company</h4>
        <a href="#about">About</a>
        <a href="#contact">Contact</a>
        <a href="#careers">Careers</a>
      </div>
      <div className="footer-col">
        <h4>Resources</h4>
        <a href="#docs">Documentation</a>
        <a href="#api">API</a>
        <a href="#playground">Playground</a>
        <a href="#blog">Blog</a>
      </div>
      <div className="footer-col">
        <h4>Legal</h4>
        <a href="#privacy">Privacy</a>
        <a href="#terms">Terms</a>
        <a href="#security">Security</a>
      </div>
    </div>
    <div className="footer-bottom">© {new Date().getFullYear()} VoxCore. All rights reserved.</div>
  </footer>
);

export default EnterpriseFooter;
