import React from "react";
import './GlobalHeader.css';
const GlobalHeader: React.FC = () => (
  <header className="global-header">
    <div className="header-left">
      <span className="logo">VoxCloud</span>
      <span className="powered">Powered by VoxCore Engine</span>
      <div className="workspace-dropdown">Production Workspace ▼</div>
    </div>
    <div className="header-center">
      <input className="search-bar" placeholder="Search queries or tables" />
    </div>
    <div className="header-right">
      <span className="icon notification" title="Alerts">🔔</span>
      <span className="icon help" title="Docs">❓</span>
      <span className="icon user" title="Profile">👤 Robert</span>
    </div>
  </header>
);
export default GlobalHeader;
