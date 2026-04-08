import React from "react";
import "./SidebarNav.css";
const SidebarNav: React.FC = () => (
  <nav className="sidebar-nav">
    <ul>
      <li><span className="nav-icon">📊</span> Dashboard</li>
      <li><span className="nav-icon">🕵️‍♂️</span> AI Query Inspector</li>
      <li><span className="nav-icon">📈</span> Query Activity</li>
      <li><span className="nav-icon">🧪</span> Sandbox Testing</li>
      <hr />
      <li><span className="nav-icon">🗄️</span> Databases</li>
      <li><span className="nav-icon">🧬</span> Schema Explorer</li>
      <li><span className="nav-icon">⚖️</span> Policies</li>
      <hr />
      <li><span className="nav-icon">💡</span> Insights</li>
      <li><span className="nav-icon">📑</span> Reports</li>
      <hr />
      <li><span className="nav-icon">🔒</span> Admin</li>
      <li><span className="nav-icon">⚙️</span> Settings</li>
    </ul>
  </nav>
);
export default SidebarNav;
