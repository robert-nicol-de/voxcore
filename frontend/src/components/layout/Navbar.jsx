
import { Link, useLocation } from "react-router-dom";

export default function Navbar() {
  const location = useLocation();
  const navLink = (path, label) => (
    <Link
      to={path}
      className={`px-3 py-1 rounded-lg font-medium transition text-base ${location.pathname === path ? "text-blue-400" : "text-slate-300 hover:text-white"}`}
    >
      {label}
    </Link>
  );

  return (
    <nav className="sticky top-0 z-50 backdrop-blur bg-[#020617]/80 border-b border-[#1e293b] px-8 py-4 flex justify-between items-center shadow-sm">
      {/* LEFT: Logo */}
      <Link to="/" className="text-white font-bold text-xl tracking-tight select-none">
        VoxCore
      </Link>

      {/* CENTER: Nav Links */}
      <div className="flex gap-6 items-center">
        {navLink("/", "Home")}
        {navLink("/about", "About")}
        {navLink("/pricing", "Pricing")}
        {navLink("/architecture", "Architecture")}
        {navLink("/ai-model", "AI Model")}
        {navLink("/security", "Security")}
      </div>

      {/* RIGHT: Auth + CTA */}
      <div className="flex gap-4 items-center">
        <Link to="/login" className="text-slate-300 hover:text-white px-3 py-1 rounded-lg font-medium transition">
          Login
        </Link>
        <Link to="/playground">
          <button className="bg-blue-500 hover:bg-blue-600 text-white px-5 py-2 rounded-xl font-semibold transition shadow-md">
            Try Demo
          </button>
        </Link>
      </div>
    </nav>
  );
}
