

import React, { useState, useEffect } from "react";
import "../../index.css";
import { useNavigate } from "react-router-dom";
import { login } from "../../services/authService";
import AuthLayout from "../../layouts/AuthLayout";

const Login = () => {
  const navigate = useNavigate();

  // ✅ STATE FIRST
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // ✅ AUTO REDIRECT IF LOGGED IN
  useEffect(() => {
    const token = localStorage.getItem("voxcore_token");
    if (token) {
      navigate("/dashboard");
    }
  }, [navigate]);

  // ✅ LOGIN HANDLER
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const data = await login(email, password);
      localStorage.setItem("voxcore_token", data.token);
      navigate("/dashboard");
    } catch (err: any) {
      console.error(err);
      setError("Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  // ✅ UI
  return (
    <AuthLayout>
      <div className="w-full max-w-md">
        {/* Branding/Identity */}
        <div className="text-center mb-6">
          <div className="text-sky-400 text-sm tracking-widest mb-2">
            AI GOVERNANCE CORE
          </div>
          <h1 className="text-4xl font-extrabold">
            Vox<span className="text-sky-400">Core</span>
          </h1>
          <p className="text-gray-400 mt-2 text-sm">
            Protecting databases from AI access
          </p>
        </div>
        {/* Glassmorphism Card */}
        <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 shadow-2xl">
          <h2 className="text-3xl font-bold mb-2 text-center">Welcome Back</h2>
          <p className="text-center text-gray-400 mb-6 text-sm">Sign in to access your VoxCore dashboard</p>
          {error && (
            <div className="text-red-400 text-sm mb-4 text-center">{error}</div>
          )}
          <form onSubmit={handleLogin}>
            <input
              type="email"
              className="w-full mb-4 p-3 rounded-lg bg-white/10 border border-white/10 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-sky-500"
              placeholder="Email"
              value={email}
              onChange={e => setEmail(e.target.value)}
            />
            <input
              type="password"
              className="w-full mb-2 p-3 rounded-lg bg-white/10 border border-white/10 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-sky-500"
              placeholder="Password"
              value={password}
              onChange={e => setPassword(e.target.value)}
            />
            <div className="flex items-center justify-between mb-6 text-sm">
              <label className="flex items-center gap-2 text-gray-400">
                <input type="checkbox" className="accent-sky-500" />
                Remember me
              </label>
              <button className="text-sky-400 hover:underline" type="button">Forgot password?</button>
            </div>
            <button
              type="submit"
              className="w-full bg-sky-500 hover:bg-sky-600 transition p-3 rounded-lg font-semibold"
              disabled={loading}
            >
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>
          {/* Divider above OAuth */}
          <div className="flex items-center my-6">
            <div className="flex-1 h-px bg-white/10"></div>
            <span className="px-3 text-gray-400 text-sm">or</span>
            <div className="flex-1 h-px bg-white/10"></div>
          </div>
          {/* OAuth Buttons */}
          <div className="space-y-3">
            <button className="w-full bg-white text-black p-3 rounded-lg font-medium hover:bg-gray-200 transition">
              Continue with Google
            </button>
            <button className="w-full bg-[#2F2F2F] text-white p-3 rounded-lg font-medium hover:bg-[#3a3a3a] transition">
              Continue with Microsoft
            </button>
          </div>
        </div>
      </div>
    </AuthLayout>
  );
};

export default Login;
