import React from "react";
import "./Layout.css";
import { useNavigate, useLocation } from "react-router-dom";

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  return (
    <div className="app-shell">

      {/* SIDEBAR (FIXED SYSTEM NAV) */}
      <aside className="sidebar">
        <div className="logo">VoxCore</div>

        <nav className="nav">
          <button
            className={`nav-item ${location.pathname === "/intelligence" ? "active" : ""}`}
            onClick={() => navigate("/intelligence")}
          >
            Intelligence
          </button>
          <button
            className={`nav-item ${location.pathname === "/timeline" ? "active" : ""}`}
            onClick={() => navigate("/timeline")}
          >
            Timeline
          </button>
          <button
            className={`nav-item ${location.pathname === "/connections" ? "active" : ""}`}
            onClick={() => navigate("/connections")}
          >
            Connections
          </button>
        </nav>
      </aside>

      {/* MAIN AREA */}
      <main className="main-content">
        {children}
      </main>

    </div>
  );
};

export default Layout;
