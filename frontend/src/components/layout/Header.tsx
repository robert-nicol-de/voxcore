import { useNavigate } from "react-router-dom";

export default function Header() {
  const navigate = useNavigate();
  return (
    <header className="border-b border-white/10 px-8 py-4 flex justify-between items-center">
      {/* Logo */}
      <div className="flex items-center gap-2">
        <span className="text-white font-bold text-lg cursor-pointer" onClick={() => navigate("/")}>VoxCore</span>
      </div>
      {/* Nav */}
      <nav className="hidden md:flex gap-6 text-sm text-gray-400">
        <button onClick={() => navigate("/")}>Home</button>
        <button onClick={() => navigate("/about")}>About</button>
        <button onClick={() => navigate("/pricing")}>Pricing</button>
        <button onClick={() => navigate("/architecture")}>Architecture</button>
        <button onClick={() => navigate("/ai-model")}>AI Model</button>
        <button onClick={() => navigate("/security")}>Security</button>
      </nav>
      {/* Actions */}
      <div className="flex gap-3">
        <button className="border border-white/20 px-4 py-1 rounded text-sm" onClick={() => navigate("/login")}>Login</button>
        <button className="bg-blue-500 px-4 py-1 rounded text-sm" onClick={() => navigate("/playground")}>Get Started</button>
      </div>
    </header>
  );
}
