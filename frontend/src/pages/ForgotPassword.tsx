import React from "react";
import { Link } from "react-router-dom";
import {
  Shield,
  Mail,
  ArrowLeft,
  CheckCircle2,
} from "lucide-react";
import MarketingLayout from "../components/layout/MarketingLayout";

export default function ForgotPassword() {
  const trustChips = ["Secure Recovery", "Encrypted Sessions", "Audit Ready", "Workspace Protected"];
  const recoveryNotes = ["Reset access securely", "Protect governed workspaces", "Return to policy-controlled AI workflows"];

  return (
    <MarketingLayout contentClassName="flex min-h-[calc(100vh-96px)] items-center justify-center px-6 py-16 md:px-10 md:py-24">
      <div className="w-full max-w-5xl">
        <div className="grid gap-10 lg:grid-cols-[1.05fr_0.95fr]">
          <section className="flex flex-col justify-center">
            <div className="inline-flex w-fit items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/[0.06] px-4 py-2 text-[12px] uppercase tracking-[0.24em] text-cyan-300">
              <Shield className="h-4 w-4" />
              Secure Recovery
            </div>

            <h1 className="mt-6 max-w-xl text-5xl font-semibold leading-[0.95] tracking-tight text-white md:text-6xl">
              Recover access securely
            </h1>

            <p className="mt-6 max-w-xl text-lg leading-8 text-slate-300">
              Enter your work email and we'll send you a secure reset link.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              {trustChips.map((chip) => (
                <span
                  key={chip}
                  className="rounded-full border border-white/10 bg-white/[0.03] px-4 py-2 text-sm text-slate-300"
                >
                  {chip}
                </span>
              ))}
            </div>

            <div className="mt-8 hidden border-t border-white/10 pt-8 lg:block">
              <p className="text-[12px] uppercase tracking-[0.24em] text-slate-500">
                Recovery includes
              </p>

              <div className="mt-5 space-y-4">
                {recoveryNotes.map((note) => (
                  <div key={note} className="flex items-center gap-3">
                    <CheckCircle2 className="h-5 w-5 text-cyan-300" />
                    <span className="text-base text-slate-200">{note}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section className="rounded-[32px] border border-white/10 bg-white/[0.03] p-6 shadow-[0_0_0_1px_rgba(255,255,255,0.02)] backdrop-blur-xl md:p-8">
            <div className="mb-8 flex items-center gap-3">
              <Link
                to="/login"
                className="inline-flex items-center gap-2 text-sm text-slate-400 transition hover:text-white"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to Login
              </Link>
            </div>

            <form className="space-y-6">
              <div>
                <label className="mb-3 block text-sm font-medium text-slate-200">
                  Email Address
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

              <button
                type="submit"
                className="w-full rounded-full bg-white px-6 py-4 text-base font-semibold text-slate-950 shadow-[0_0_24px_rgba(255,255,255,0.14)] transition-all duration-300 hover:-translate-y-0.5 hover:scale-[1.01]"
              >
                Send Reset Link
              </button>
            </form>

            <div className="mt-8 border-t border-white/10 pt-8 lg:hidden">
              <p className="text-[12px] uppercase tracking-[0.24em] text-slate-500">
                Recovery includes
              </p>

              <div className="mt-5 space-y-4">
                {recoveryNotes.map((note) => (
                  <div key={note} className="flex items-center gap-3">
                    <CheckCircle2 className="h-5 w-5 text-cyan-300" />
                    <span className="text-base text-slate-200">{note}</span>
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
