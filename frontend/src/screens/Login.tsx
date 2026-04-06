import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";
import { apiUrl } from "../lib/api";

interface LoginProps {
  onLogin?: (userName?: string) => void;
  isDemoMode?: boolean;
}

export const Login: React.FC<LoginProps> = ({ onLogin, isDemoMode = false }) => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // console.log("LOGIN CLICKED", { email, password: password ? "***" : "" });
    setError("");
    
    // Validate input before submitting
    if (!email.trim()) {
      setError("Please enter your email address");
      return;
    }
    if (!password.trim()) {
      setError("Please enter your password");
      return;
    }
    if (email.trim().length < 5 || !email.includes("@")) {
      setError("Please enter a valid email address");
      return;
    }
    
    setLoading(true);

    try {
      const url = apiUrl("/api/v1/auth/login");
      // console.log("Login request URL:", url);
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: email.trim().toLowerCase(), password }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || "Invalid email or password");
      }

      const data = await response.json();
      // console.log("Login response:", response.status, data);
      
      // Validate response has required token
      if (!data.access_token) {
        throw new Error("Authentication failed: No token received");
      }
      
      // Store token & user info
      localStorage.setItem("voxcore_token", data.access_token);
      if (data.user_name) localStorage.setItem("voxcore_user_name", data.user_name);
      if (data.user_email) localStorage.setItem("voxcore_user_email", data.user_email);
      if (data.org_id != null) localStorage.setItem("voxcore_org_id", String(data.org_id));
      if (data.org_name) localStorage.setItem("voxcore_org_name", String(data.org_name));
      if (data.workspace_id != null) localStorage.setItem("voxcore_workspace_id", String(data.workspace_id));
      if (data.workspace_name) localStorage.setItem("voxcore_workspace_name", String(data.workspace_name));
      if (data.company_id != null) localStorage.setItem("voxcore_company_id", String(data.company_id));
      localStorage.setItem("voxcore_role", String(data.role || "viewer"));
      localStorage.setItem("voxcore_is_super_admin", String(Boolean(data.is_super_admin)));

      // Only call onLogin after successful validation
      if (onLogin) {
        onLogin(data.user_name);
      }

      // Enforce a direct post-login route so auth never falls back to marketing view.
      navigate("/app/dashboard", { replace: true });
    } catch (err: any) {
      setError(err.message || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <div className="w-full max-w-md bg-[#111827]/80 backdrop-blur-xl border border-gray-700 rounded-2xl shadow-2xl p-10">
        <h2 className="text-2xl font-semibold text-center text-white mb-6">
          Sign In
        </h2>
        {error && (
          <div className="text-red-400 text-sm mb-4 text-center">
            {error}
          </div>
        )}
        <form onSubmit={handleLogin} className="space-y-4">
          <input
            type="email"
            placeholder="Email address"
            className="w-full p-3 rounded-lg bg-gray-800 text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 outline-none"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            className="w-full p-3 rounded-lg bg-gray-800 text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 outline-none"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <div className="flex justify-between text-sm text-gray-400">
            <label className="flex items-center gap-2">
              <input type="checkbox" />
              Remember me
            </label>
            <span className="hover:text-white cursor-pointer">
              Forgot password?
            </span>
          </div>
          <button
            type="submit"
            className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 p-3 rounded-lg font-semibold text-white hover:opacity-90 transition"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>
        <div className="text-center text-gray-500 text-sm my-4">or</div>
        <button className="w-full border border-gray-600 p-3 rounded-lg hover:bg-gray-800 transition mb-3 text-white">
          Continue with Google
        </button>
        <button className="w-full border border-gray-600 p-3 rounded-lg hover:bg-gray-800 transition text-white">
          Continue with Microsoft
        </button>
        <p className="text-center text-sm text-gray-400 mt-6">
          Don’t have an account?{" "}
          <span className="text-blue-400 cursor-pointer hover:underline">
            Create one
          </span>
        </p>
      </div>
    </AuthLayout>
  );
};
