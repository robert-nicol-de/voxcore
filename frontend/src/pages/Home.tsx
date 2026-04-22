import { Card } from "@/components/Card";
import MarketingLayout from "@/components/layout/MarketingLayout";
import { MarketingContainer } from "@/components/layout/MarketingLayout";
import { Link } from "react-router-dom";

export const Home = () => {
  return (
    <MarketingLayout>
      <section className="py-16 md:py-24">
        <MarketingContainer>
          <div className="space-y-16 md:space-y-24">
            <div className="grid gap-10 lg:grid-cols-[minmax(0,1.08fr)_minmax(360px,0.92fr)] lg:items-stretch">
              {/* LEFT SIDE: HEADLINE + CTA + TRUST SIGNALS */}
              <div className="flex flex-col justify-center max-w-5xl space-y-8">
                {/* Top badge */}
                <div className="inline-flex w-fit items-center gap-2 rounded-full border border-sky-400/20 bg-sky-400/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.28em] text-sky-200/80">
                  <span className="h-2 w-2 rounded-full bg-emerald-300" />
                  VoxCore • AI Data Governance
                </div>

                {/* Headline block */}
                <div className="space-y-5">
                  <div className="text-sm font-semibold uppercase tracking-[0.34em] text-sky-300/70">
                    Governed Decision Intelligence
                  </div>

                  <h1 className="max-w-6xl text-5xl font-semibold leading-[0.98] tracking-tight text-white sm:text-6xl xl:text-[5.15rem]">
                    Let AI work with your data
                    <span className="block text-white/92">without giving up control.</span>
                  </h1>

                  <p className="max-w-3xl text-xl leading-8 text-slate-300">
                    VoxCore is the trust layer between AI and your databases — inspecting queries,
                    enforcing policy, bounding execution, and turning governed results into clear,
                    explainable business intelligence.
                  </p>
                </div>

                {/* CTA buttons - clear hierarchy */}
                <div className="flex flex-col sm:flex-row gap-3 pt-2">
                  <Link
                    to="/playground"
                    className="rounded-full bg-white px-8 py-4 text-base font-semibold text-slate-950 transition hover:scale-[1.02] hover:bg-slate-100 shadow-lg shadow-white/20"
                  >
                    Open Playground
                  </Link>

                  <Link
                    to="/contact"
                    className="rounded-full border border-sky-300/30 bg-sky-400/12 px-8 py-4 text-base font-semibold text-sky-100 transition hover:border-sky-200/50 hover:bg-sky-400/20"
                  >
                    Book Demo
                  </Link>
                </div>

                <button className="text-sm font-medium text-slate-300 transition hover:text-white">
                  Talk to Sales
                </button>

                {/* Friction-reducing micro copy */}
                <div className="pt-2 text-xs text-slate-400 font-medium">
                  No live database required • Sample environment included • Governance visible instantly
                </div>

                {/* Trust signal strip - balanced and consistent */}
                <div className="grid gap-4 sm:grid-cols-3 pt-4">
                  <div className="group rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-4 transition-all hover:border-white/20 hover:bg-white/[0.05]">
                    <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-500">
                      ✓ Query Control
                    </div>
                    <div className="mt-2 text-sm font-semibold text-white">Policy enforced before execution</div>
                  </div>

                  <div className="group rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-4 transition-all hover:border-white/20 hover:bg-white/[0.05]">
                    <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-500">
                      ✓ Trusted Output
                    </div>
                    <div className="mt-2 text-sm font-semibold text-white">Risk, mode, and controls visible</div>
                  </div>

                  <div className="group rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-4 transition-all hover:border-white/20 hover:bg-white/[0.05]">
                    <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-500">
                      ✓ Enterprise Ready
                    </div>
                    <div className="mt-2 text-sm font-semibold text-white">Governance, reporting, dashboards</div>
                  </div>
                </div>
              </div>

              {/* RIGHT SIDE: VOXCORE COMMAND SURFACE */}
              <div className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-[linear-gradient(160deg,rgba(8,15,30,0.96),rgba(4,10,20,0.88))] p-6 shadow-[0_24px_80px_rgba(2,8,23,0.55)]">
                <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(56,189,248,0.12),transparent_42%),radial-gradient(circle_at_bottom_right,rgba(16,185,129,0.08),transparent_34%)]" />

                <div className="relative z-10">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <div className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-300/75">
                        Live Governance Surface
                      </div>
                      <div className="mt-2 text-lg font-semibold text-white">
                        AI query enters a controlled path before any data is touched
                      </div>
                    </div>

                    <div className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-emerald-200">
                      Active
                    </div>
                  </div>

                  {/* Simulated prompt panel */}
                  <div className="mt-6 rounded-[1.6rem] border border-white/10 bg-black/20 p-4">
                    <div className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">
                      Query Interface
                    </div>
                    <div className="mt-3 rounded-[1.25rem] border border-white/8 bg-[#07111f] px-4 py-4 font-mono text-sm text-white">
                      Show revenue by region
                    </div>

                    <div className="mt-4 flex flex-wrap gap-2">
                      <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">
                        Governance: Policy Safe
                      </span>
                      <span className="rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-1 text-xs text-amber-200">
                        Execution: Demo Simulation
                      </span>
                      <span className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs text-emerald-200">
                        Risk: 23
                      </span>
                    </div>
                  </div>

                  {/* System path */}
                  <div className="mt-6 space-y-3">
                    {[
                      {
                        title: "Query Router",
                        body: "Incoming AI request is routed into a governed execution path.",
                      },
                      {
                        title: "Governance Engine",
                        body: "Policy, risk, and safety checks run before execution.",
                      },
                      {
                        title: "Bounded Execution",
                        body: "Row limits, timeout controls, and read-only enforcement stay active.",
                      },
                      {
                        title: "Insight Layer",
                        body: "Governed outputs become explainable narratives, dashboards, and actions.",
                      },
                    ].map((step) => (
                      <div
                        key={step.title}
                        className="flex items-start justify-between gap-4 rounded-2xl border border-white/8 bg-white/[0.04] px-4 py-4"
                      >
                        <div>
                          <div className="text-sm font-semibold text-white">{step.title}</div>
                          <div className="mt-1 text-sm leading-6 text-slate-400">{step.body}</div>
                        </div>

                        <div className="rounded-full border border-sky-300/20 bg-sky-400/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-sky-100">
                          Online
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* WHY VOXCORE EXISTS SECTION */}
            <div className="space-y-10 py-16 md:py-24">
              {/* Section header - constrained width for authority */}
              <div className="max-w-3xl">
                <div className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-300/75">
                  Why VoxCore Exists
                </div>
                <h2 className="mt-4 text-4xl font-semibold leading-[1.1] tracking-tight text-white sm:text-5xl">
                  AI access to data is accelerating. Control has not kept up.
                </h2>
                <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-300">
                  AI copilots, agents, and automation systems are increasingly being connected to operational and analytical data. Without a governance layer, those systems can generate unsafe queries, return misleading answers, exceed intended access, or act without a clear audit trail. VoxCore exists to put control, visibility, and trust between AI and your data.
                </p>
              </div>

              {/* Risk cards grid - with improved consistency */}
              <div className="grid gap-6 md:grid-cols-2">
                {[
                  {
                    number: "01",
                    title: "Unsafe Queries",
                    description: "AI-generated requests can be expensive, unbounded, or unsafe before a human ever sees them.",
                    icon: "⚠️",
                  },
                  {
                    number: "02",
                    title: "Wrong Answers",
                    description: "When AI interprets data incorrectly, the result is not just bad SQL — it is bad business judgment.",
                    icon: "❌",
                  },
                  {
                    number: "03",
                    title: "No Audit Trail",
                    description: "If every AI request is not logged, reviewed, and explained, trust breaks down fast.",
                    icon: "📭",
                  },
                  {
                    number: "04",
                    title: "Permission Drift",
                    description: "Static permissions do not provide enough control when AI systems act across tools, workflows, and datasets.",
                    icon: "🔓",
                  },
                ].map((risk) => (
                  <div
                    key={risk.number}
                    className="group rounded-2xl border border-rose-400/15 bg-rose-400/5 p-6 transition-all h-full hover:border-rose-400/25 hover:bg-rose-400/8"
                  >
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-500">
                        Risk {risk.number}
                      </div>
                      <div className="text-lg flex-shrink-0">{risk.icon}</div>
                    </div>
                    <h3 className="text-lg font-semibold text-white leading-snug">{risk.title}</h3>
                    <p className="mt-3 text-sm leading-6 text-slate-400">{risk.description}</p>
                  </div>
                ))}
              </div>

              {/* Closing statement - premium treatment */}
              <div className="rounded-2xl border border-sky-300/20 bg-[linear-gradient(160deg,rgba(56,189,248,0.08),rgba(15,23,42,0.08))] p-8 lg:p-10 shadow-lg shadow-sky-400/10">
                <p className="max-w-3xl text-lg font-semibold leading-8 text-white">
                  VoxCore was built to govern this entire path before execution, not explain the failure afterward.
                </p>
              </div>
            </div>

            {/* HOW VOXCORE WORKS SECTION */}
            <div className="space-y-10 py-16 md:py-24">
              {/* Section header */}
              <div className="max-w-3xl">
                <div className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-300/75">
                  How VoxCore Works
                </div>
                <h2 className="mt-4 text-4xl font-semibold leading-[1.1] tracking-tight text-white sm:text-5xl">
                  Three guardrails. Complete control.
                </h2>
                <p className="mt-3 text-lg text-slate-300">
                  From AI request to trusted result — with governance built into every step.
                </p>
              </div>

              {/* 3-step flow */}
              <div className="relative grid gap-6 lg:grid-cols-3">
                {/* Step 1: Understand */}
                <div className="group cursor-default overflow-hidden rounded-2xl border border-white/10 bg-white/[0.03] p-8 transition-all hover:border-sky-300/25 hover:bg-white/[0.06]">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full border border-sky-300/20 bg-sky-400/10">
                    <span className="text-sm font-semibold text-sky-200">1</span>
                  </div>
                  <h3 className="mt-5 text-xl font-semibold text-white">Understand</h3>
                  <p className="mt-3 text-sm leading-6 text-slate-400">
                    VoxCore ingests your AI request, parses its structure, and maps it against your data schema and access rules.
                  </p>
                  <div className="mt-6 overflow-hidden rounded-lg border border-white/8 bg-black/20 px-4 py-3 font-mono text-xs text-sky-200/80">
                    <div className="inline-block animate-pulse">SELECT revenue FROM sales</div>
                  </div>
                </div>

                {/* Branded connector 1 (desktop only) */}
                <div className="hidden lg:flex items-center justify-center">
                  <div className="relative w-full h-1">
                    <div className="absolute inset-0 bg-gradient-to-r from-sky-400 via-slate-600 to-transparent opacity-30" />
                    <div className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2">
                      <div className="h-2 w-2 rounded-full border border-sky-400/40 bg-sky-400/20 shadow-lg shadow-sky-400/10" />
                    </div>
                  </div>
                </div>
                <div className="group cursor-default overflow-hidden rounded-2xl border border-white/10 bg-white/[0.03] p-8 transition-all hover:border-emerald-300/25 hover:bg-white/[0.06] lg:col-span-1">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full border border-emerald-300/20 bg-emerald-400/10">
                    <span className="text-sm font-semibold text-emerald-200">2</span>
                  </div>
                  <h3 className="mt-5 text-xl font-semibold text-white">Govern</h3>
                  <p className="mt-3 text-sm leading-6 text-slate-400">
                    Policies run in parallel: risk scoring, safety checks, access validation, and row-level controls all execute before execution.
                  </p>
                  <div className="mt-6 flex flex-wrap gap-2">
                    <span className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-slate-300 opacity-100 transition-all group-hover:opacity-100 group-hover:animate-pulse">
                      ✓ Policy Safe
                    </span>
                    <span className="inline-flex items-center rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-200 opacity-100 transition-all group-hover:opacity-100 group-hover:animate-pulse" style={{animationDelay: '0.1s'}}>
                      Risk: 18
                    </span>
                  </div>
                </div>

                {/* Branded connector 2 (desktop only) */}
                <div className="hidden lg:flex items-center justify-center">
                  <div className="relative w-full h-1">
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-slate-600 to-emerald-400 opacity-30" />
                    <div className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2">
                      <div className="h-2 w-2 rounded-full border border-emerald-400/40 bg-emerald-400/20 shadow-lg shadow-emerald-400/10" />
                    </div>
                  </div>
                </div>
                <div className="group cursor-default overflow-hidden rounded-2xl border border-white/10 bg-white/[0.03] p-8 transition-all hover:border-slate-300/25 hover:bg-white/[0.06] lg:col-span-1">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full border border-slate-300/20 bg-slate-400/10">
                    <span className="text-sm font-semibold text-slate-200">3</span>
                  </div>
                  <h3 className="mt-5 text-xl font-semibold text-white">Deliver</h3>
                  <p className="mt-3 text-sm leading-6 text-slate-400">
                    Approved queries execute safely with constraints active. Results are audited, governance proof is returned, and actions become traceable.
                  </p>
                  <div className="mt-6 rounded-lg border border-emerald-400/20 bg-emerald-400/5 px-4 py-3 transition-all group-hover:border-emerald-400/40 group-hover:bg-emerald-400/10">
                    <div className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-200 opacity-0 transition-all group-hover:opacity-100" style={{transitionDelay: '0.15s'}}>
                      ✓ Governed Result
                    </div>
                  </div>
                </div>
              </div>

              {/* Bridge to capabilities */}
              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 lg:p-8">
                <p className="max-w-3xl text-base leading-7 text-slate-300">
                  Every step is logged, visible, and explainable. Your team knows exactly what happened, why it was allowed, and can audit the full path. That's governance that builds trust.
                </p>
              </div>
            </div>

            {/* GOVERNANCE CAPABILITIES SECTION */}
            <div className="space-y-12 py-16 md:py-24">
              <div className="mb-12 space-y-4">
                <div className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-300/75">
                  Governance Capabilities
                </div>
                <h2 className="max-w-4xl text-4xl font-semibold text-white">
                  The controls enterprise AI access has been missing.
                </h2>
                <p className="max-w-3xl text-lg leading-8 text-slate-400">
                  VoxCore gives organizations the governance layer needed to use AI safely at scale. Every request can be evaluated, constrained, approved, monitored, and explained before it reaches production data.
                </p>
              </div>

              {/* 8-Card Capabilities Grid */}
              <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
                {[
                  {
                    num: "01",
                    title: "Query Guardian",
                    description: "Inspects every AI-generated request before execution and blocks unsafe operations automatically.",
                    value: "Prevent costly mistakes before they happen.",
                    icon: "🛡️",
                  },
                  {
                    num: "02",
                    title: "Risk Engine",
                    description: "Scores requests based on complexity, access sensitivity, execution patterns, and policy rules.",
                    value: "Know what is safe, what needs review, and what should stop.",
                    icon: "📊",
                  },
                  {
                    num: "03",
                    title: "Approval Workflows",
                    description: "Require human approval for high-risk actions, sensitive data access, or privileged operations.",
                    value: "Keep humans in control where it matters most.",
                    icon: "✓",
                  },
                  {
                    num: "04",
                    title: "Full Audit Trail",
                    description: "Track what was requested, what SQL was generated, what ran, what changed, and why it was allowed.",
                    value: "Build trust, accountability, and compliance readiness.",
                    icon: "📋",
                  },
                  {
                    num: "05",
                    title: "Role-Based Access",
                    description: "Enforce permissions by organization, workspace, team, and user role.",
                    value: "The right people get the right access — nothing more.",
                    icon: "👥",
                  },
                  {
                    num: "06",
                    title: "Data Masking",
                    description: "Protect sensitive fields with masking, restrictions, or controlled visibility policies.",
                    value: "Enable AI without exposing critical data.",
                    icon: "👁️",
                  },
                  {
                    num: "07",
                    title: "Row Limits & Guardrails",
                    description: "Apply bounded execution, timeouts, row caps, and safe-result constraints automatically.",
                    value: "Protect performance and avoid runaway workloads.",
                    icon: "🔒",
                  },
                  {
                    num: "08",
                    title: "Query Rewrites",
                    description: "Automatically optimize or rewrite risky queries into safer, policy-compliant versions.",
                    value: "Improve safety without slowing users down.",
                    icon: "🔄",
                  },
                ].map((capability) => (
                  <div
                    key={capability.num}
                    className="group overflow-hidden rounded-2xl border border-white/10 bg-white/[0.03] p-6 transition-all hover:border-emerald-300/25 hover:bg-white/[0.05] h-full flex flex-col"
                  >
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-500">
                        Capability {capability.num}
                      </div>
                      <div className="text-xl flex-shrink-0">{capability.icon}</div>
                    </div>
                    <h3 className="text-base font-semibold text-white leading-snug">
                      {capability.title}
                    </h3>
                    <p className="mt-3 text-sm leading-6 text-slate-400 flex-grow">
                      {capability.description}
                    </p>
                    <div className="mt-5 rounded-lg border border-emerald-400/20 bg-emerald-400/5 px-3 py-2.5 transition-all group-hover:border-emerald-300/30 group-hover:bg-emerald-300/8">
                      <p className="text-xs font-medium text-emerald-200/90 leading-5">
                        {capability.value}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Control Strip */}
              <div className="mt-12 flex flex-wrap justify-center gap-4">
                {[
                  "Policy Safe",
                  "Risk Scored",
                  "Audited",
                  "Explainable",
                  "Enterprise Ready",
                ].map((tag) => (
                  <div
                    key={tag}
                    className="inline-flex items-center rounded-full border border-white/15 bg-white/5 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-300 transition hover:border-white/25 hover:bg-white/8"
                  >
                    {tag}
                  </div>
                ))}
              </div>

              {/* Closing Statement */}
              <div className="mt-12 text-center">
                <p className="mx-auto max-w-2xl text-lg leading-8 text-slate-300">
                  VoxCore does not ask you to trust AI blindly. It gives you <span className="font-semibold text-white">controls to trust it responsibly.</span>
                </p>
              </div>
            </div>

            {/* EXPLAIN MY DATA STUDIO SECTION */}
            <div className="space-y-12 py-16 md:py-24">
              {/* Section Intro */}
              <div className="space-y-4">
                <div className="text-xs font-semibold uppercase tracking-[0.28em] text-blue-300/75">
                  Decision Intelligence Layer
                </div>
                <h2 className="max-w-4xl text-4xl font-semibold text-white">
                  Turn governed data access into decisions people can act on.
                </h2>
                <p className="max-w-3xl text-lg leading-8 text-slate-400">
                  VoxCore goes beyond controlling AI requests. It transforms governed data into ranked insights, clear narratives, recommended actions, and guided follow-up analysis — helping teams move from raw answers to better decisions faster.
                </p>
              </div>

              {/* Two-Column Main Layout */}
              <div className="grid gap-8 lg:grid-cols-2 lg:items-stretch">
                {/* LEFT: Feature Stack + CTAs */}
                <div className="flex flex-col justify-between space-y-8">
                  <div className="space-y-6">
                    {[
                      {
                        title: "Ranked Insights",
                        description: "Surface the most important patterns, changes, risks, and opportunities automatically.",
                      },
                      {
                        title: "Clear Narratives",
                        description: "Convert technical outputs into executive-ready explanations people can understand.",
                      },
                      {
                        title: "Follow-Up Actions",
                        description: "Guide users to the next best question, deeper analysis, or recommended response.",
                      },
                      {
                        title: "Guided Exploration",
                        description: "Move naturally from one answer to the next without starting over.",
                      },
                    ].map((feature, idx) => (
                      <div key={idx} className="space-y-2">
                        <h3 className="text-base font-semibold text-white">{feature.title}</h3>
                        <p className="text-sm leading-6 text-slate-400">{feature.description}</p>
                        <div className="h-0.5 w-12 bg-gradient-to-r from-blue-400/60 to-blue-400/0" />
                      </div>
                    ))}
                  </div>

                  {/* Outcome Badge */}
                  <div className="rounded-xl border border-blue-400/20 bg-blue-400/8 p-4">
                    <p className="text-sm font-semibold text-blue-200">
                      ⚡ Faster Decisions
                    </p>
                    <p className="mt-2 text-xs text-blue-300/80 leading-5">
                      Reduce time between question, understanding, and action.
                    </p>
                  </div>

                  {/* CTA Buttons */}
                  <div className="flex flex-wrap gap-3">
                    <Link
                      to="/playground"
                      className="rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-950 transition hover:scale-[1.01] hover:bg-slate-100"
                    >
                      Open Playground
                    </Link>
                    <Link
                      to="/contact"
                      className="rounded-full border border-blue-300/20 bg-blue-400/10 px-6 py-3 text-sm font-medium text-blue-100 transition hover:border-blue-200/35 hover:bg-blue-400/15"
                    >
                      Book Demo
                    </Link>
                  </div>
                </div>

                {/* RIGHT: Premium Product Surface Mock */}
                <div className="relative overflow-hidden rounded-[2rem] border border-blue-400/20 bg-[linear-gradient(160deg,rgba(8,20,40,0.96),rgba(4,12,28,0.88))] p-6 shadow-[0_24px_80px_rgba(56,189,248,0.12)]">
                  <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(56,189,248,0.15),transparent_42%)]" />

                  <div className="relative z-10 space-y-6">
                    {/* Header */}
                    <div>
                      <div className="text-xs font-semibold uppercase tracking-[0.28em] text-blue-300/75">
                        Explain My Data Studio
                      </div>
                      <div className="mt-2 text-sm font-medium text-slate-300">
                        Analysis Results
                      </div>
                    </div>

                    {/* Key Insight Card */}
                    <div className="rounded-xl border border-emerald-400/25 bg-emerald-400/8 p-4">
                      <div className="text-xs font-semibold uppercase tracking-[0.16em] text-emerald-200/75">
                        Key Insight
                      </div>
                      <p className="mt-3 text-base font-semibold text-emerald-100">
                        Revenue increased 18% over the last 6 months
                      </p>
                      <p className="mt-2 text-xs text-emerald-200/70">
                        Top growth driven by West region and SmartWatch Pro.
                      </p>
                    </div>

                    {/* Narrative Panel */}
                    <div className="space-y-2 rounded-xl border border-white/12 bg-white/[0.04] p-4">
                      <div className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">
                        What Changed?
                      </div>
                      <p className="text-sm leading-6 text-slate-300">
                        Growth accelerated after new product launches and higher repeat customer activity.
                      </p>
                    </div>

                    {/* Follow-Up Action Chips */}
                    <div className="flex flex-wrap gap-2">
                      {[
                        "Compare Regions",
                        "Explain Drivers",
                        "Forecast Trend",
                        "Recommend Actions",
                      ].map((action) => (
                        <button
                          key={action}
                          className="rounded-full border border-blue-400/30 bg-blue-400/12 px-3 py-1.5 text-xs font-medium text-blue-200 transition hover:border-blue-300/50 hover:bg-blue-400/20"
                        >
                          {action}
                        </button>
                      ))}
                    </div>

                    {/* Confidence Footer */}
                    <div className="flex flex-wrap gap-2 border-t border-white/10 pt-4">
                      {["Governed", "Ranked", "Explainable", "Actionable"].map((tag) => (
                        <span
                          key={tag}
                          className="text-xs font-medium text-slate-400"
                        >
                          {tag}
                          {tag !== "Actionable" && <span className="ml-2">•</span>}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Outcome Cards Row */}
              <div className="grid gap-6 md:grid-cols-3">
                {[
                  {
                    icon: "⚡",
                    title: "Faster Decisions",
                    description: "Reduce analysis time from hours to minutes.",
                  },
                  {
                    icon: "🤝",
                    title: "Better Alignment",
                    description: "Give technical and business teams one shared explanation.",
                  },
                  {
                    icon: "✓",
                    title: "Trusted Insights",
                    description: "Every answer stays connected to governance and audit controls.",
                  },
                ].map((outcome) => (
                  <div
                    key={outcome.title}
                    className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 transition-all hover:border-blue-300/25 hover:bg-white/[0.05] h-full flex flex-col"
                  >
                    <div className="text-2xl mb-3">{outcome.icon}</div>
                    <h3 className="text-base font-semibold text-white">
                      {outcome.title}
                    </h3>
                    <p className="mt-2 text-sm text-slate-400">
                      {outcome.description}
                    </p>
                  </div>
                ))}
              </div>

              {/* Closing Bridge */}
              <div className="text-center">
                <p className="mx-auto max-w-2xl text-lg leading-8 text-slate-300">
                  VoxCore does not stop at safe access. It helps organizations <span className="font-semibold text-white">understand what matters next.</span>
                </p>
              </div>
            </div>

            {/* ENTERPRISE READINESS SECTION */}
            <div className="space-y-12 py-16 md:py-24">
              {/* Section Intro */}
              <div className="space-y-4">
                <div className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-400">
                  Enterprise Readiness
                </div>
                <h2 className="max-w-4xl text-4xl font-semibold text-white">
                  Built for real environments, not just demos.
                </h2>
                <p className="max-w-3xl text-lg leading-8 text-slate-400">
                  VoxCore is designed for organizations that need security, scale, accountability, and operational control. From multi-team deployments to governed integrations, every layer is built to support serious production use.
                </p>
              </div>

              {/* 6-Card Enterprise Grid */}
              <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
                {[
                  {
                    num: "01",
                    title: "Multi-Tenant Architecture",
                    description: "Separate organizations, teams, policies, and data boundaries within one controlled platform.",
                    value: "Secure isolation with centralized oversight.",
                    icon: "🏢",
                  },
                  {
                    num: "02",
                    title: "Role-Based Access Control",
                    description: "Manage permissions by role, workspace, admin level, and operational responsibility.",
                    value: "The right access for every user.",
                    icon: "🔐",
                  },
                  {
                    num: "03",
                    title: "Secure Connectors",
                    description: "Connect approved data sources through governed pathways with controlled execution rules.",
                    value: "Use existing systems without compromising standards.",
                    icon: "🔗",
                  },
                  {
                    num: "04",
                    title: "Monitoring & Reporting",
                    description: "Track platform activity, query behavior, risk trends, and operational health over time.",
                    value: "Full visibility for leaders and operators.",
                    icon: "📊",
                  },
                  {
                    num: "05",
                    title: "Scalable Operations",
                    description: "Designed to support growing workloads, more users, more teams, and expanding governance needs.",
                    value: "Start now and grow confidently.",
                    icon: "📈",
                  },
                  {
                    num: "06",
                    title: "Admin Control Center",
                    description: "Centralized controls for policies, users, approvals, settings, and platform governance.",
                    value: "One place to manage trust at scale.",
                    icon: "⚙️",
                  },
                ].map((capability) => (
                  <div
                    key={capability.num}
                    className="group overflow-hidden rounded-2xl border border-white/10 bg-white/[0.03] p-6 transition-all hover:border-slate-400/25 hover:bg-white/[0.05] h-full flex flex-col"
                  >
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-500">
                        Enterprise {capability.num}
                      </div>
                      <div className="text-xl flex-shrink-0">{capability.icon}</div>
                    </div>
                    <h3 className="text-base font-semibold text-white leading-snug">
                      {capability.title}
                    </h3>
                    <p className="mt-3 text-sm leading-6 text-slate-400 flex-grow">
                      {capability.description}
                    </p>
                    <div className="mt-5 rounded-lg border border-blue-400/20 bg-blue-400/5 px-3 py-2.5 transition-all group-hover:border-blue-300/30 group-hover:bg-blue-300/8">
                      <p className="text-xs font-medium text-blue-200/90 leading-5">
                        {capability.value}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Trust Strip */}
              <div className="flex flex-wrap justify-center gap-4">
                {[
                  "Secure by Design",
                  "Operationally Ready",
                  "Scalable Architecture",
                  "Admin Controlled",
                  "Enterprise Ready",
                ].map((tag) => (
                  <div
                    key={tag}
                    className="inline-flex items-center rounded-full border border-white/15 bg-white/5 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-300 transition hover:border-white/25 hover:bg-white/8"
                  >
                    {tag}
                  </div>
                ))}
              </div>

              {/* Deployment Examples */}
              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-8">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500 mb-4">
                  Works Across
                </p>
                <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                  {[
                    "Internal analytics teams",
                    "Multi-branch operations",
                    "Regulated environments",
                    "Executive reporting",
                    "AI copilots",
                    "Data platforms",
                  ].map((deployment) => (
                    <div key={deployment} className="flex items-center gap-3 text-sm text-slate-300">
                      <span className="h-1.5 w-1.5 rounded-full bg-slate-400/60" />
                      {deployment}
                    </div>
                  ))}
                </div>
              </div>

              {/* Closing Bridge */}
              <div className="text-center">
                <p className="mx-auto max-w-2xl text-lg leading-8 text-slate-300">
                  VoxCore is built to <span className="font-semibold text-white">earn trust in production</span> — not just impress in a demo.
                </p>
              </div>
            </div>

            {/* FINAL CTA SECTION - increased isolation and premium treatment */}
            <div className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-white/[0.03] p-8 lg:p-12 shadow-[0_24px_80px_rgba(56,189,248,0.08)] mt-16 md:mt-24">
              <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(56,189,248,0.08),transparent_48%)]" />

              <div className="relative z-10 space-y-8 text-center">
                {/* Section Label */}
                <div className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-300/70">
                  Ready to Deploy Trusted AI?
                </div>

                {/* Headline - compact and sharp */}
                <h2 className="mx-auto max-w-2xl text-4xl lg:text-5xl font-semibold text-white">
                  Let AI work with your data — with governance built in from day one.
                </h2>

                {/* Supporting Paragraph */}
                <p className="mx-auto max-w-2xl text-lg leading-8 text-slate-300">
                  VoxCore helps organizations control AI access, prevent unsafe execution, generate trusted insights, and scale with confidence. Whether you're exploring governed analytics or preparing for enterprise rollout, the next step starts here.
                </p>

                {/* CTA Buttons - clear primary/secondary */}
                <div className="flex flex-col sm:flex-row justify-center gap-3 pt-4">
                  <Link
                    to="/playground"
                    className="rounded-full bg-white px-8 py-4 text-base font-semibold text-slate-950 transition hover:scale-[1.02] hover:bg-slate-100 shadow-lg shadow-white/20"
                  >
                    Open Playground
                  </Link>

                  <Link
                    to="/contact"
                    className="rounded-full border border-sky-300/30 bg-sky-400/12 px-8 py-4 text-base font-semibold text-sky-100 transition hover:border-sky-200/50 hover:bg-sky-400/20"
                  >
                    Book Demo
                  </Link>
                </div>

                <button className="text-sm font-medium text-slate-300 transition hover:text-white">
                  Talk to Sales
                </button>

                {/* Trust Strip */}
                <div className="flex flex-wrap justify-center gap-3 pt-2">
                  {[
                    "No live database required",
                    "Fast evaluation path",
                    "Enterprise-ready architecture",
                    "Built for governed scale",
                  ].map((trust) => (
                    <div
                      key={trust}
                      className="inline-flex items-center rounded-full border border-white/12 bg-white/5 px-3 py-1.5 text-xs font-medium text-slate-400"
                    >
                      ✓ {trust}
                    </div>
                  ))}
                </div>

                {/* Optional Proof Card */}
                <div className="pt-4">
                  <div className="mx-auto max-w-2xl rounded-2xl border border-emerald-400/15 bg-emerald-400/5 p-6 lg:p-8">
                    <h3 className="text-base font-semibold text-emerald-100 mb-4">
                      Why Teams Choose VoxCore
                    </h3>
                    <div className="space-y-3">
                      {[
                        "Govern AI before execution",
                        "Reduce data risk",
                        "Improve trust in outputs",
                        "Accelerate decisions",
                        "Deploy with confidence",
                      ].map((reason, idx) => (
                        <div key={idx} className="flex items-center gap-3 text-sm text-emerald-200/90">
                          <span className="h-1.5 w-1.5 rounded-full bg-emerald-300/60" />
                          {reason}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Final Signature Line - elevated treatment */}
                <div className="pt-6">
                  <p className="mx-auto max-w-2xl text-lg leading-8 text-slate-300 italic">
                    The future of AI with data will belong to organizations that can <span className="font-semibold text-white">trust it.</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </MarketingContainer>
      </section>
    </MarketingLayout>
  );
};

export default Home;
