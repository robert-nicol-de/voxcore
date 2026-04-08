import React from "react";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen relative overflow-hidden bg-[#07111f] text-white flex flex-col">
      {/* Animated Gradient Glow */}
      <div className="absolute w-[600px] h-[600px] bg-sky-500/20 blur-[120px] rounded-full top-[-100px] left-[-100px] animate-pulse" />
      <div className="absolute w-[500px] h-[500px] bg-purple-500/20 blur-[120px] rounded-full bottom-[-100px] right-[-100px] animate-pulse" />
      {/* Content */}
      <div className="relative z-10 flex flex-col min-h-screen">
        {/* Header */}
        <header className="border-b border-white/10 px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <img
                src="/assets/logo-icon.png"
                alt="VoxCore"
                className="h-8 w-8"
              />
              <h1 className="text-lg font-bold text-white">VoxCore</h1>
            </div>
            <nav className="hidden md:flex gap-6 text-sm text-gray-400">
              <button className="hover:text-white">Features</button>
              <button className="hover:text-white">Pricing</button>
              <button className="hover:text-white">Docs</button>
            </nav>
          </div>
          <div className="flex gap-3">
            <button className="text-sm text-gray-400 hover:text-white">Sign Up</button>
          </div>
        </header>
        {/* Main */}
        <main className="flex-1 flex items-center justify-center px-4">
          {children}
        </main>
        {/* Footer */}
        <footer className="border-t border-white/10 text-sm text-gray-400 py-6 px-6">
          <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
            <div>© {new Date().getFullYear()} VoxCore</div>
            <div className="flex gap-6">
              <button className="hover:text-white">Privacy</button>
              <button className="hover:text-white">Terms</button>
              <button className="hover:text-white">Contact</button>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
