import { useNavigate } from "react-router-dom";
import { useState } from "react";

export default function Navbar() {
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const links = [
    { label: "Product", href: "/product" },
    { label: "Security", href: "/security" },
    { label: "Pricing", href: "/pricing" },
  ];

  return (
    <>
      <div style={{ background: 'red', color: 'white', padding: '8px', textAlign: 'center' }}>
        TEST NAV CHANGE — IF YOU SEE THIS, NAVBAR.TSX IS BEING RENDERED
      </div>
      <nav className="border-b border-white/10 sticky top-0 z-50 backdrop-blur-xl bg-[#0B0F19]/95">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <button
          onClick={() => navigate("/")}
          className="flex items-center gap-3 hover:opacity-80 transition"
        >
          <img 
            src="/assets/voxcore-logo-symbol.svg" 
            alt="VoxQuery" 
            className="h-8 w-8"
          />
          <span className="text-lg font-bold tracking-tight">VoxQuery</span>
        </button>

        {/* Desktop Nav */}
        <div className="hidden md:flex items-center gap-8">
          {links.map((link) => (
            <button
              key={link.href}
              onClick={() => navigate(link.href)}
              className="text-sm text-gray-400 hover:text-white transition"
            >
              {link.label}
            </button>
          ))}
        </div>

        {/* CTA Buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate("/login")}
            className="text-sm text-gray-400 hover:text-white transition px-3 py-2"
          >
            Login
          </button>
          <button
            onClick={() => navigate("/app")}
            className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition shadow-lg shadow-blue-500/20"
          >
            Launch App
          </button>
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="md:hidden text-gray-400 hover:text-white"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-white/10 bg-[#0B0F19]/98 px-6 py-4 space-y-3">
          {links.map((link) => (
            <button
              key={link.href}
              onClick={() => {
                navigate(link.href);
                setMobileOpen(false);
              }}
              className="block w-full text-left text-sm text-gray-400 hover:text-white transition py-2"
            >
              {link.label}
            </button>
          ))}
        </div>
      )}
    </nav>
    </>
  );
}
