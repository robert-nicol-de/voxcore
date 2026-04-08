import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle login logic here
    navigate("/app");
  };

  return (
    <div className="bg-[#0B0F19] text-white min-h-screen flex flex-col">
      <Navbar />

      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md space-y-8">
          {/* Logo */}
          <div className="text-center">
            <div className="flex justify-center mb-6">
              <img
                src="/assets/logo-icon.png"
                alt="VoxCore"
                className="h-12 w-12"
              />
            </div>
          </div>

          {/* LEFT SIDE INFO */}
          <div className="text-center mb-12">
            <h1 className="text-3xl font-bold mb-3">Welcome Back</h1>
            <p className="text-gray-400">
              Sign in to your VoxCore account to manage your data security
            </p>
          </div>

          {/* LOGIN FORM */}
          <form onSubmit={handleLogin} className="space-y-6">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
                className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/30 transition"
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/30 transition"
              />
            </div>

            {/* Remember & Forgot */}
            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 text-gray-400 cursor-pointer hover:text-gray-300">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded bg-white/10 border border-white/20 cursor-pointer"
                />
                Remember me
              </label>
              <button
                type="button"
                onClick={() => navigate("/reset-password")}
                className="text-blue-400 hover:text-blue-300 transition"
              >
                Forgot password?
              </button>
            </div>

            {/* Sign In Button */}
            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-lg transition shadow-lg shadow-blue-500/20"
            >
              Sign In
            </button>
          </form>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white/10" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-[#0B0F19] text-gray-500">or</span>
            </div>
          </div>

          {/* OAuth Options */}
          <div className="space-y-3">
            <button
              type="button"
              className="w-full px-4 py-3 rounded-lg border border-white/10 hover:border-white/20 text-white font-medium transition flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Continue with Google
            </button>

            <button
              type="button"
              className="w-full px-4 py-3 rounded-lg border border-white/10 hover:border-white/20 text-white font-medium transition flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M11.4 24c-6.336 0-11.4-5.06-11.4-11.4 0-6.34 5.06-11.4 11.4-11.4 6.34 0 11.4 5.06 11.4 11.4 0 6.34-5.06 11.4-11.4 11.4zm0-1.44c5.544 0 9.96-4.416 9.96-9.96 0-5.544-4.416-9.96-9.96-9.96-5.544 0-9.96 4.416-9.96 9.96 0 5.544 4.416 9.96 9.96 9.96zm5.496-7.416c.288 0 .432.216.432.504 0 .432-.288.9-.504 1.332-.42.792-1.404 1.62-3.06 1.62H7.2V6.612h6.912c1.584 0 2.52.756 2.88 1.728.324.792.324 1.512.144 2.052.144.216.288.432.468.648.288.36.324.972-.072 1.44-.252.324-.504.684-.612 1.08.108.216.216.5.468.792zm-5.832-3.6h-3.78V10.572h3.78V8.988zm0 4.068h-3.78v1.512h3.78v-1.512z"/>
              </svg>
              Continue with Microsoft
            </button>
          </div>

          {/* Sign Up Link */}
          <p className="text-center text-sm text-gray-400">
            Don't have an account?{" "}
            <button
              onClick={() => navigate("/signup")}
              className="text-blue-400 hover:text-blue-300 font-medium transition"
            >
              Sign up free
            </button>
          </p>

          {/* Features List */}
          <div className="border-t border-white/10 pt-8 mt-8">
            <p className="text-xs uppercase text-gray-600 mb-4">You get access to</p>
            <ul className="space-y-2 text-sm text-gray-300">
              <li className="flex items-center gap-2">
                <span className="w-4 h-4 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 text-xs">✓</span>
                Real-time query analysis
              </li>
              <li className="flex items-center gap-2">
                <span className="w-4 h-4 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 text-xs">✓</span>
                Complete audit trails
              </li>
              <li className="flex items-center gap-2">
                <span className="w-4 h-4 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 text-xs">✓</span>
                Policy enforcement
              </li>
              <li className="flex items-center gap-2">
                <span className="w-4 h-4 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 text-xs">✓</span>
                Team management
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-white/10 text-center text-sm text-gray-500 py-6">
        <p>
          <button className="hover:text-gray-400 transition">Privacy Policy</button>
          {" • "}
          <button className="hover:text-gray-400 transition">Terms of Service</button>
          {" • "}
          <button className="hover:text-gray-400 transition">Help</button>
        </p>
      </footer>
    </div>
  );
}
