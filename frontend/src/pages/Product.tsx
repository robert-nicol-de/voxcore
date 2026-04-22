import React from "react";
import {
  Sparkles,
  Workflow,
  Shield,
  Database,
  Search,
  AlertTriangle,
  ShieldCheck,
  ScrollText,
  Users,
  Gauge,
} from "lucide-react";
import MarketingLayout from "@/components/layout/MarketingLayout";

type FlowCard = {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  tags?: string[];
  highlight?: boolean;
};

type CapabilityCard = {
  title: string;
  body: React.ReactNode;
  outcome: string;
  icon: React.ComponentType<{ className?: string }>;
};

type OutcomeCard = {
  title: string;
  body: string;
  tone: string;
  hoverNote: string;
};

export default function Product() {
  const heroChips = [
    "Query Inspection",
    "Risk Scoring",
    "Policy Enforcement",
    "Audit Logging",
  ];

  const flowCards: FlowCard[] = [
    {
      title: "AI Request",
      icon: Sparkles,
    },
    {
      title: "Query Plan",
      icon: Workflow,
    },
    {
      title: "VoxCore Governance Layer",
      icon: Shield,
      tags: ["Policy", "Risk", "Audit", "Control"],
      highlight: true,
    },
    {
      title: "Database Execution",
      icon: Database,
    },
  ];

  const riskCards = [
    {
      title: "Unsafe Execution",
      body: "AI-generated queries can be expensive, unbounded, or unsafe before a human ever sees them.",
      metric: "Unbounded AI requests increase operational risk.",
      tone: "border-red-400/15 bg-red-400/[0.04]",
    },
    {
      title: "Wrong Answers",
      body: "If AI interprets data incorrectly, the result is not just bad SQL — it is bad business judgment.",
      metric: "False confidence leads to bad business decisions.",
      tone: "border-amber-400/15 bg-amber-400/[0.04]",
    },
    {
      title: "No Traceability",
      body: "Without auditability and decision controls, organizations cannot prove what happened or why.",
      metric: "Lack of traceability weakens enterprise trust.",
      tone: "border-cyan-400/15 bg-cyan-400/[0.04]",
    },
  ];

  const pipeline = [
    {
      number: "01",
      title: "Query Generated",
      subtext: "AI produces a SQL request or structured data intent.",
    },
    {
      number: "02",
      title: "Query Inspected",
      subtext: "Structure, access scope, and request context are validated.",
    },
    {
      number: "03",
      title: "Risk Scored",
      subtext: "Cost + sensitivity + complexity are evaluated.",
    },
    {
      number: "04",
      title: "Policy Evaluated",
      subtext: "Rules allow, block, rewrite, or escalate the request.",
    },
    {
      number: "05",
      title: "Decision Enforced",
      subtext: "Only approved, bounded actions proceed to execution.",
    },
  ];

  const capabilities: CapabilityCard[] = [
    {
      title: "Query Inspection",
      icon: Search,
      body: (
        <>
          Inspects every AI-generated query before execution to validate
          structure, intent, and safety.
        </>
      ),
      outcome: "Prevent unsafe requests early.",
    },
    {
      title: "Risk Scoring",
      icon: AlertTriangle,
      body: (
        <>
          Scores each request based on access scope, sensitivity, complexity,
          and execution cost.
        </>
      ),
      outcome: "Understand what needs review.",
    },
    {
      title: "Policy Enforcement",
      icon: ShieldCheck,
      body: (
        <>
          <span className="font-semibold text-white">
            Controls every decision path
          </span>{" "}
          by allowing, blocking, rewriting, or routing requests for approval.
        </>
      ),
      outcome: "Control every decision path.",
    },
    {
      title: "Audit Logging",
      icon: ScrollText,
      body: (
        <>
          Captures the full request, decision, and execution trail so every AI
          action is traceable.
        </>
      ),
      outcome: "Build trust and accountability.",
    },
    {
      title: "Approval Workflows",
      icon: Users,
      body: (
        <>
          Escalates sensitive or high-risk requests for human review before
          execution.
        </>
      ),
      outcome: "Keep humans in control.",
    },
    {
      title: "Execution Guardrails",
      icon: Gauge,
      body: (
        <>
          <span className="font-semibold text-white">
            Protects production systems
          </span>{" "}
          with row limits, timeouts, and bounded execution controls.
        </>
      ),
      outcome: "Protect production systems.",
    },
  ];

  const outcomes: OutcomeCard[] = [
    {
      title: "Blocked",
      body: "High-risk or policy-violating requests are stopped before execution.",
      tone:
        "border-red-400/20 bg-red-400/[0.04] text-red-300 hover:shadow-[0_0_24px_rgba(248,113,113,0.10)]",
      hoverNote: "Requires policy override to proceed.",
    },
    {
      title: "Pending Approval",
      body: "Sensitive or ambiguous requests can be routed for human review.",
      tone:
        "border-amber-400/20 bg-amber-400/[0.04] text-amber-300 hover:shadow-[0_0_24px_rgba(251,191,36,0.10)]",
      hoverNote: "Human approval is required before execution.",
    },
    {
      title: "Allowed",
      body: "Safe, policy-compliant requests proceed within defined execution boundaries.",
      tone:
        "border-emerald-400/20 bg-emerald-400/[0.04] text-emerald-300 hover:shadow-[0_0_24px_rgba(52,211,153,0.10)]",
      hoverNote: "Request meets policy and execution controls.",
    },
    {
      title: "Rewritten",
      body: "Unsafe or inefficient requests can be transformed into safer versions before execution.",
      tone:
        "border-cyan-400/20 bg-cyan-400/[0.04] text-cyan-300 hover:shadow-[0_0_24px_rgba(34,211,238,0.10)]",
      hoverNote: "Request is adjusted into a safer compliant form.",
    },
  ];

  const premiumCard =
    "rounded-3xl border border-white/10 bg-white/[0.03] p-6 transition-all duration-300 ease-out hover:-translate-y-1 hover:border-cyan-400/20 hover:bg-white/[0.05] hover:shadow-[0_0_20px_rgba(34,211,238,0.08)]";

  const primaryBtn =
    "rounded-full bg-white px-6 py-4 text-base font-medium text-slate-950 shadow-[0_0_30px_rgba(255,255,255,0.18)] transition-all duration-300 ease-out hover:-translate-y-0.5 hover:scale-[1.02] hover:shadow-[0_0_36px_rgba(255,255,255,0.22)]";

  const secondaryBtn =
    "rounded-full border border-white/15 bg-transparent px-6 py-4 text-base font-medium text-white transition-all duration-300 ease-out hover:-translate-y-0.5 hover:bg-white/5";

  return (
    <MarketingLayout>
      <section className="relative overflow-hidden py-16 md:py-24">
        <div className="absolute left-1/2 top-0 -z-10 h-[420px] w-[420px] -translate-x-1/2 rounded-full bg-cyan-400/10 blur-3xl" />

        <div className="mx-auto max-w-7xl px-6 md:px-10">
          <p className="text-[12px] uppercase tracking-[0.28em] text-cyan-400">
            Product Architecture
          </p>

          <h1 className="mt-4 max-w-4xl text-5xl font-semibold leading-[0.95] tracking-tight text-white md:text-6xl lg:text-7xl">
            Control how AI accesses your data
          </h1>

          <p className="mt-6 max-w-2xl text-lg leading-9 text-slate-300">
            VoxCore sits between AI systems and your databases to inspect
            queries, enforce policy, score risk, and control execution before
            data is touched.
          </p>

          <div className="mt-8 flex flex-col gap-4 sm:flex-row">
            <button className={primaryBtn}>Open Playground</button>
            <button className={secondaryBtn}>Book Demo</button>
          </div>

          <p className="mt-4 text-sm text-slate-400">
            Used to govern AI access before production execution.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            {heroChips.map((item) => (
              <span
                key={item}
                className="rounded-full border border-white/10 px-4 py-2 text-sm text-slate-300"
              >
                {item}
              </span>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16 md:py-24">
        <div className="mx-auto max-w-7xl px-6 md:px-10">
          <h2 className="max-w-4xl text-4xl font-semibold leading-tight text-white md:text-6xl">
            VoxCore inserts governance into the AI-to-data path
          </h2>

          <p className="mt-6 max-w-2xl text-lg leading-9 text-slate-300">
            Instead of allowing AI tools to connect directly to production data,
            VoxCore creates a controlled execution layer where every request can
            be inspected, evaluated, and governed before execution.
          </p>

          <div className="mt-12 hidden items-center gap-4 lg:flex">
            {flowCards.map((card, index) => {
              const Icon = card.icon;
              return (
                <React.Fragment key={card.title}>
                  <div
                    className={`flex h-full min-h-[220px] w-full flex-col rounded-3xl border p-6 transition-all duration-300 ease-out hover:-translate-y-1 ${
                      card.highlight
                        ? "border-cyan-400/20 bg-cyan-400/5 shadow-[0_0_30px_rgba(34,211,238,0.12)]"
                        : "border-white/10 bg-white/[0.03] hover:border-cyan-400/20 hover:bg-white/[0.05]"
                    }`}
                  >
                    <Icon className="h-6 w-6 text-cyan-300" />
                    <h3 className="mt-4 max-w-[12rem] text-2xl font-semibold text-white">
                      {card.title}
                    </h3>

                    {card.tags && (
                      <div className="mt-5 flex flex-wrap gap-2">
                        {card.tags.map((tag) => (
                          <span
                            key={tag}
                            className="rounded-full border border-cyan-400/20 px-3 py-1 text-xs text-cyan-300"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {index < flowCards.length - 1 && (
                    <>
                      <div className="h-px flex-1 bg-gradient-to-r from-cyan-400/40 to-transparent" />
                      <div className="text-cyan-300">→</div>
                      <div className="h-px flex-1 bg-gradient-to-r from-cyan-400/40 to-white/5" />
                    </>
                  )}
                </React.Fragment>
              );
            })}
          </div>

          <div className="mt-12 grid gap-6 lg:hidden lg:grid-cols-4">
            {flowCards.map((card) => {
              const Icon = card.icon;
              return (
                <div
                  key={card.title}
                  className={`flex min-h-[220px] flex-col rounded-3xl border p-6 ${
                    card.highlight
                      ? "border-cyan-400/20 bg-cyan-400/5 shadow-[0_0_30px_rgba(34,211,238,0.12)]"
                      : "border-white/10 bg-white/[0.03]"
                  }`}
                >
                  <Icon className="h-6 w-6 text-cyan-300" />
                  <h3 className="mt-4 text-2xl font-semibold text-white">
                    {card.title}
                  </h3>

                  {card.tags && (
                    <div className="mt-5 flex flex-wrap gap-2">
                      {card.tags.map((tag) => (
                        <span
                          key={tag}
                          className="rounded-full border border-cyan-400/20 px-3 py-1 text-xs text-cyan-300"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="py-16 md:py-24">
        <div className="mx-auto max-w-7xl px-6 md:px-10">
          <h2 className="max-w-4xl text-4xl font-semibold leading-tight text-white md:text-6xl">
            AI-generated access needs a control layer
          </h2>

          <p className="mt-6 max-w-2xl text-lg leading-9 text-slate-300">
            AI can generate useful requests, but it can also produce unsafe SQL,
            incorrect logic, excessive access, or actions with no clear audit
            trail. VoxCore exists to govern that path before execution, not
            explain failures afterward.
          </p>

          <div className="mt-14 grid gap-6 md:grid-cols-3">
            {riskCards.map((card) => (
              <div
                key={card.title}
                className={`rounded-3xl border p-6 ${card.tone}`}
              >
                <h3 className="text-2xl font-semibold text-white">
                  {card.title}
                </h3>
                <p className="mt-4 max-w-sm text-base leading-8 text-slate-300">
                  {card.body}
                </p>
                <p className="mt-5 text-sm font-medium text-slate-200">
                  {card.metric}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16 md:py-24">
        <div className="mx-auto max-w-7xl px-6 md:px-10">
          <h2 className="max-w-4xl text-4xl font-semibold leading-tight text-white md:text-6xl">
            How governed execution works
          </h2>

          <p className="mt-6 max-w-2xl text-lg leading-9 text-slate-300">
            Every request follows a controlled path before reaching production
            data.
          </p>

          <div className="mt-12 hidden items-center gap-4 lg:flex">
            {pipeline.map((step, i) => (
              <React.Fragment key={step.number}>
                <div className="flex h-12 w-12 items-center justify-center rounded-full border border-cyan-400/20 bg-cyan-400/5 text-sm font-semibold text-cyan-300">
                  {step.number}
                </div>
                {i < pipeline.length - 1 && (
                  <div className="h-px flex-1 bg-gradient-to-r from-cyan-400/40 to-white/5" />
                )}
              </React.Fragment>
            ))}
          </div>

          <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            {pipeline.map((step) => (
              <div
                key={step.title}
                className="rounded-2xl border border-white/10 bg-white/[0.03] px-5 py-5 transition-all duration-300 hover:border-cyan-400/30 hover:bg-cyan-400/[0.04] hover:shadow-[0_0_20px_rgba(34,211,238,0.08)]"
              >
                <div className="text-sm text-cyan-400">{step.number}</div>
                <div className="mt-2 text-base font-medium text-white">
                  {step.title}
                </div>
                <div className="mt-2 text-sm leading-6 text-slate-400">
                  {step.subtext}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16 md:py-24">
        <div className="mx-auto max-w-7xl px-6 md:px-10">
          <h2 className="max-w-4xl text-4xl font-semibold leading-tight text-white md:text-6xl">
            Core governance capabilities
          </h2>

          <div className="mt-12 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
            {capabilities.map((card) => {
              const Icon = card.icon;
              return (
                <div key={card.title} className={premiumCard}>
                  <Icon className="h-6 w-6 text-cyan-300" />
                  <h3 className="mt-4 text-2xl font-semibold text-white">
                    {card.title}
                  </h3>
                  <p className="mt-4 max-w-xs text-base leading-8 text-slate-300">
                    {card.body}
                  </p>
                  <div className="mt-6 rounded-2xl border border-cyan-400/15 bg-cyan-400/5 px-4 py-4 text-sm text-cyan-100">
                    {card.outcome}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="py-16 md:py-24">
        <div className="mx-auto max-w-7xl px-6 md:px-10">
          <div className="mb-10 flex flex-wrap gap-3">
            {[
              "100% Traceability",
              "Human Approval Controls",
              "Policy Enforcement",
              "Bounded Execution",
            ].map((item) => (
              <span
                key={item}
                className="rounded-full border border-white/10 bg-white/[0.03] px-4 py-2 text-sm text-slate-300"
              >
                {item}
              </span>
            ))}
          </div>

          <h2 className="max-w-4xl text-4xl font-semibold leading-tight text-white md:text-6xl">
            Governed decision outcomes
          </h2>

          <p className="mt-6 max-w-2xl text-lg leading-9 text-slate-300">
            Every request resolves into a clear, enforceable outcome.
          </p>

          <div className="mt-12 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
            {outcomes.map((item) => (
              <div
                key={item.title}
                className={`group rounded-3xl border p-6 transition-all duration-300 ease-out hover:-translate-y-1 ${item.tone}`}
              >
                <h3 className="text-2xl font-semibold">{item.title}</h3>
                <p className="mt-4 text-base leading-8 text-slate-200">
                  {item.body}
                </p>
                <p className="mt-4 text-sm text-slate-400 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                  {item.hoverNote}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16 md:py-24">
        <div className="mx-auto max-w-6xl px-6 md:px-10">
          <div className="rounded-[32px] border border-white/10 bg-white/[0.03] p-10">
            <h2 className="max-w-4xl text-4xl font-semibold leading-tight text-white md:text-6xl">
              Governance you can prove
            </h2>

            <p className="mt-6 max-w-4xl text-lg leading-9 text-slate-300">
              Every query handled by VoxCore is traceable, explainable, and
              governed before execution. Teams gain visibility into what was
              requested, how it was evaluated, what decision was made, and why
              that decision was enforced.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              {[
                "Full Decision Trace",
                "Explainable Enforcement",
                "Audit-Ready History",
                "Safer AI Access",
              ].map((item) => (
                <span
                  key={item}
                  className="rounded-full border border-cyan-400/15 bg-cyan-400/[0.05] px-4 py-2 text-sm font-medium text-cyan-100 shadow-[0_0_12px_rgba(34,211,238,0.04)]"
                >
                  {item}
                </span>
              ))}
            </div>

            <p className="mt-8 text-base leading-8 text-slate-300">
              Built for security teams, data leaders, and regulated environments
              that need explainable control over AI-driven data access.
            </p>

            <p className="mt-8 text-lg font-medium text-white">
              VoxCore is built to give organizations control they can operate
              with and trust they can defend.
            </p>
          </div>
        </div>
      </section>

      <section className="py-16 md:py-24">
        <div className="mx-auto max-w-5xl px-6 text-center md:px-10">
          <p className="text-[12px] uppercase tracking-[0.28em] text-cyan-400">
            See the control layer in action
          </p>

          <h2 className="mx-auto mt-4 max-w-4xl text-4xl font-semibold leading-tight text-white md:text-6xl">
            Control AI access before it reaches production data
          </h2>

          <p className="mx-auto mt-6 max-w-3xl text-lg leading-9 text-slate-300">
            Deploy safer AI workflows with governance, auditability, and
            enforcement built in from day one.
          </p>

          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <button className={primaryBtn}>Open Playground</button>
            <button className={secondaryBtn}>Book Demo</button>
          </div>

          <button className="mt-5 text-sm font-medium text-slate-300 transition-colors hover:text-white">
            Talk to Sales
          </button>
        </div>
      </section>

    </MarketingLayout>
  );
}
