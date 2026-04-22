import React from "react";
import { Link } from "react-router-dom";
import {
  Shield,
  Mail,
  Lock,
  User,
  Building2,
  CheckCircle2,
  Chrome,
  Users,
} from "lucide-react";
import MarketingLayout from "../components/layout/MarketingLayout";

export default function Signup() {
  const benefits = [
    "Govern AI access before execution",
    "Create audit-ready decision trails",
    "Manage teams and roles",
    "Launch secure data workflows faster",
  ];

  const trustChips = ["SSO Ready", "RBAC", "Audit Logs", "Secure Onboarding"];

  return (
    <MarketingLayout contentClassName="flex min-h-[calc(100vh-96px)] items-center justify-center px-6 py-16 md:px-10 md:py-24">
        <div className="w-full max-w-6xl">
          <div className="grid gap-10 lg:grid-cols-[1.05fr_0.95fr]">
            {/* Left side */}
            <section className="flex flex-col justify-center">
              <div className="inline-flex w-fit items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/[0.06] px-4 py-2 text-[12px] uppercase tracking-[0.24em] text-cyan-300">
                <Shield className="h-4 w-4" />
                Secure Onboarding
              </div>

              <h1 className="mt-6 max-w-xl text-5xl font-semibold leading-[0.95] tracking-tight text-white md:text-6xl">
                Start with governed AI access from day one
              </h1>

              <p className="mt-6 max-w-xl text-lg leading-8 text-slate-300">
                Create your VoxCore account to secure AI-generated data access,
                apply policy controls, and build trusted execution workflows.
              </p>

              <div className="mt-8 flex flex-wrap gap-3">
                {trustChips.map((chip) => (
                  <span
                    key={chip}
                    className="rounded-full border border-white/10 bg-white/[0.03] px-4 py-2 text-sm text-slate-300 transition-all duration-300 hover:-translate-y-0.5 hover:border-cyan-400/20 hover:bg-white/[0.05] hover:text-white"
                  >
                    {chip}
                  </span>
                ))}
              </div>

              <div className="mt-10 hidden rounded-[28px] border border-white/10 bg-white/[0.03] p-6 shadow-[0_0_40px_rgba(0,0,0,0.35)] lg:block">
                <p className="text-[12px] uppercase tracking-[0.24em] text-cyan-400">
                  You can start with
                </p>

                <div className="mt-6 space-y-4">
                  {benefits.map((item) => (
                    <div key={item} className="flex items-center gap-3">
                      <CheckCircle2 className="h-5 w-5 text-cyan-300" />
                      <span className="text-base text-slate-200">{item}</span>
                    </div>
                  ))}
                </div>

                <p className="mt-8 text-sm text-slate-400">
                  Built for teams securing AI access to real production data.
                </p>
              </div>
            </section>

            {/* Right side form */}
            <section className="rounded-[32px] border border-white/10 bg-white/[0.03] p-6 shadow-[0_0_40px_rgba(0,0,0,0.35)] backdrop-blur-xl md:p-8">
              <div className="flex justify-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl border border-cyan-400/15 bg-cyan-400/[0.05] shadow-[0_0_24px_rgba(34,211,238,0.08)]">
                  <img
                    src="/assets/voxcore-logo-symbol.svg"
                    alt="VoxCore"
                    className="h-9 w-9 object-contain"
                  />
                </div>
              </div>

              <h2 className="mt-6 text-center text-4xl font-semibold text-white">
                Create account
              </h2>

              <p className="mt-3 text-center text-base leading-7 text-slate-300">
                Set up your workspace and start governing AI access securely.
              </p>

              <form className="mt-8 space-y-6">
                <div>
                  <label className="mb-3 block text-sm font-medium text-slate-200">
                    Full Name
                  </label>
                  <div className="relative">
                    <User className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-500" />
                    <input
                      type="text"
                      placeholder="Jane Smith"
                      className="h-14 w-full rounded-2xl border border-white/10 bg-white/[0.04] pl-12 pr-5 text-white placeholder:text-slate-500 outline-none transition-all duration-300 focus:border-cyan-400/40 focus:ring-2 focus:ring-cyan-400/20"
                    />
                  </div>
                </div>

                <div>
                  <label className="mb-3 block text-sm font-medium text-slate-200">
                    Work Email
                  </label>
                  <div className="relative">
                    <Mail className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-500" />
                    <input
                      type="email"
                      placeholder="you@company.com"
                      className="h-14 w-full rounded-2xl border border-white/10 bg-white/[0.04] pl-12 pr-5 text-white placeholder:text-slate-500 outline-none transition-all duration-300 focus:border-cyan-400/40 focus:ring-2 focus:ring-cyan-400/20"
                    />
                  </div>
                </div>

                <div>
                  <label className="mb-3 block text-sm font-medium text-slate-200">
                    Company Name
                  </label>
                  <div className="relative">
                    <Building2 className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-500" />
                    <input
                      type="text"
                      placeholder="Your company"
                      className="h-14 w-full rounded-2xl border border-white/10 bg-white/[0.04] pl-12 pr-5 text-white placeholder:text-slate-500 outline-none transition-all duration-300 focus:border-cyan-400/40 focus:ring-2 focus:ring-cyan-400/20"
                    />
                  </div>
                </div>

                <div>
                  <label className="mb-3 block text-sm font-medium text-slate-200">
                    Password
                  </label>
                  <div className="relative">
                    <Lock className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-500" />
                    <input
                      type="password"
                      placeholder="Create a secure password"
                      className="h-14 w-full rounded-2xl border border-white/10 bg-white/[0.04] pl-12 pr-5 text-white placeholder:text-slate-500 outline-none transition-all duration-300 focus:border-cyan-400/40 focus:ring-2 focus:ring-cyan-400/20"
                    />
                  </div>
                </div>

                <label className="flex items-start gap-3 text-sm leading-6 text-slate-300">
                  <input
                    type="checkbox"
                    className="mt-1 h-4 w-4 rounded border-white/20 bg-white/[0.04] text-cyan-400 focus:ring-cyan-400/30"
                  />
                  <span>
                    I agree to the{" "}
                    <Link to="/terms" className="text-cyan-300 transition hover:text-white">
                      Terms of Service
                    </Link>{" "}
                    and{" "}
                    <Link to="/privacy" className="text-cyan-300 transition hover:text-white">
                      Privacy Policy
                    </Link>
                    .
                  </span>
                </label>

                <button
                  type="submit"
                  className="w-full rounded-full bg-white px-6 py-4 text-base font-semibold text-slate-950 shadow-[0_0_24px_rgba(255,255,255,0.14)] transition-all duration-300 hover:-translate-y-0.5 hover:scale-[1.01]"
                >
                  Create Account
                </button>
              </form>

              <div className="my-8 flex items-center gap-4">
                <div className="h-px flex-1 bg-white/10" />
                <span className="text-sm text-slate-400">or</span>
                <div className="h-px flex-1 bg-white/10" />
              </div>

              <div className="space-y-4">
                <button className="flex h-14 w-full items-center justify-center gap-3 rounded-2xl border border-white/10 bg-white/[0.02] text-base font-medium text-white transition-all duration-300 hover:-translate-y-0.5 hover:bg-white/[0.05]">
                  <Chrome className="h-5 w-5" />
                  Continue with Google
                </button>

                <button className="flex h-14 w-full items-center justify-center gap-3 rounded-2xl border border-white/10 bg-white/[0.02] text-base font-medium text-white transition-all duration-300 hover:-translate-y-0.5 hover:bg-white/[0.05]">
                  <Users className="h-5 w-5" />
                  Continue with Microsoft
                </button>
              </div>

              <p className="mt-8 text-center text-sm text-slate-400">
                Already have an account?{" "}
                <Link to="/login" className="text-cyan-300 transition hover:text-white">
                  Sign in
                </Link>
              </p>

              <div className="mt-8 border-t border-white/10 pt-8 lg:hidden">
                <p className="text-[12px] uppercase tracking-[0.24em] text-slate-500">
                  You can start with
                </p>

                <div className="mt-5 space-y-4">
                  {benefits.map((item) => (
                    <div key={item} className="flex items-center gap-3">
                      <CheckCircle2 className="h-5 w-5 text-cyan-300" />
                      <span className="text-base text-slate-200">{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          </div>
        </div>
    </MarketingLayout>
  );
}
