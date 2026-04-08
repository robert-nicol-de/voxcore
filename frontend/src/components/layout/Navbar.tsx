
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const navLink = (path: string, label: string) => (
    <button
      className={`nav-link ${location.pathname === path ? "nav-link--active" : ""}`}
      onClick={() => {
        setOpen(false);
        navigate(path, { replace: true });
      }}
    >
      {label}
    </button>
  );

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <div className="navbar-brand">
        <img src="/assets/voxcore-logo-symbol.svg" alt="VoxQuery" className="navbar-logo" />
        <span className="navbar-title">VoxQuery</span>

        <button className="navbar-hamburger" onClick={() => setOpen((v) => !v)}>
          <span />
          <span />
          <span />
        </button>

        <div className={`navbar-links${open ? " navbar-links--open" : ""}`}>
          {navLink("/", "Home")}
          {navLink("/about", "About")}
          {navLink("/pricing", "Pricing")}
          {navLink("/architecture", "Architecture")}
          {navLink("/ai-model", "AI Model")}
          {navLink("/security", "Security")}
          <button
            className="nav-link"
            style={{ color: location.pathname === "/login" ? "#3fb3ff" : "#cbd5e1" }}
            onClick={() => {
              setOpen(false);
              navigate("/login", { replace: true });
            }}
          >
            Login
          </button>
          <button
            className="nav-get-started"
            onClick={() => {
              setOpen(false);
              navigate("/playground", { replace: true });
            }}
          >
            Try Playground
          </button>
        </div>
      </div>
    </nav>
  );
}
