import React from "react";
import {
  Shield,
  Scan,
  Lock,
  ScrollText,
  Database,
  AlertTriangle,
  Coins,
  Clock3,
  UserCog,
  CheckCircle2,
  Ban,
  Wand2,
  UserCheck,
} from "lucide-react";
import MarketingLayout from "@/components/layout/MarketingLayout";

type Principle = {
  title: string;
  body: string;
  icon: React.ComponentType<{ className?: string }>;
};

type RiskLayer = {
  title: string;
  body: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  tone?: string;
};

type EnforcementOutcome = {
  title: string;
  body: string;
  icon: React.ComponentType<{ className?: string }>;
  tone: string;
};

export default function Security() {
  const trustChips = [
    "Policy Enforced",
    "Risk Scored",
    "Audited",
    "Bounded Execution",
  ];

  const principles: Principle[] = [
    {
      title: "Inspect before execution",
      body: "Every AI-generated request is evaluated before it reaches the database.",
      icon: Scan,
    },
    {
      title: "Enforce centrally",
      body: "Governance rules are applied consistently across users, queries, and data boundaries.",
      icon: Shield,
    },
    {
      title: "Bound execution safely",
      body: "Row limits, timeouts, and safe execution controls reduce operational risk.",
      icon: Lock,
    },
    {
      title: "Log every decision",
      body: "Every request and outcome is recorded for review, accountability, and auditability.",
      icon: ScrollText,
    },
  ];

  const riskLayers: RiskLayer[] = [
    {
      title: "Table-Level Detection",
      body: "Identifies requests involving sensitive, restricted, or high-risk tables.",
      icon: Database,
      label: "Sensitive",
    },
    {
      title: "Query Pattern Detection",
      body: "Flags destructive or unsafe statements such as DELETE, DROP, unrestricted scans, or suspicious access patterns.",
      icon: AlertTriangle,
      label: "Pattern",
      tone: "border-red-400/20 bg-red-400/[0.04]",
    },
    {
      title: "Cost-Based Scoring",
      body: "Detects expensive queries, full table scans, and execution patterns likely to create operational risk.",
      icon: Coins,
      label: "Cost",
    },
    {
      title: "Temporal Detection",
      body: "Identifies anomalous request timing, bursts, recurrence, or unusual activity windows.",
      icon: Clock3,
      label: "Time",
    },
    {
      title: "Contextual Detection",
      body: "Evaluates user role, request context, behavior patterns, and governance scope before allowing access.",
      icon: UserCog,
      label: "Context",
    },
  ];

  const enforcementOutcomes: EnforcementOutcome[] = [
    {
      title: "Allow",
      body: "Safe, policy-compliant requests proceed within controlled execution boundaries.",
      icon: CheckCircle2,
      tone:
        "border-emerald-400/20 bg-emerald-400/[0.04] text-emerald-300 hover:shadow-[0_0_24px_rgba(52,211,153,0.12)]",
    },
    {
      title: "Block",
      body: "High-risk or prohibited requests are stopped before touching data.",
      icon: Ban,
      tone:
        "border-red-400/20 bg-red-400/[0.04] text-red-300 hover:shadow-[0_0_24px_rgba(248,113,113,0.12)]",
    },
    {
      title: "Rewrite",
      body: "Unsafe or inefficient queries can be transformed into safer, policy-compliant versions.",
      icon: Wand2,
      tone:
        "border-cyan-400/20 bg-cyan-400/[0.04] text-cyan-300 hover:shadow-[0_0_24px_rgba(34,211,238,0.12)]",
    },
    {
      title: "Require Approval",
      body: "Sensitive or ambiguous actions can be routed for human review before execution.",
      icon: UserCheck,
      tone:
        "border-amber-400/20 bg-amber-400/[0.04] text-amber-300 hover:shadow-[0_0_24px_rgba(251,191,36,0.12)]",
    },
  ];

  const auditItems = [
    "Request fingerprint",
    "Decision outcome",
    "Policy context",
    "Execution metadata",
    "Explainable trail",
  ];

  const productionChips = [
    "Explainable enforcement",
    "Audit-ready history",
    "Safer production access",
    "Centralized control",
  ];

  const primaryBtn =
    "rounded-full bg-white px-8 py-4 text-base font-medium text-slate-950 shadow-[0_0_30px_rgba(255,255,255,0.18)] transition-all duration-300 ease-out hover:-translate-y-0.5 hover:scale-[1.02]";

  const secondaryBtn =
    "rounded-full border border-white/15 bg-transparent px-8 py-4 text-base font-medium text-white transition-all duration-300 ease-out hover:-translate-y-0.5 hover:bg-white/5";

  const sectionHeading =
    "max-w-4xl text-4xl font-semibold leading-tight text-white md:text-6xl";

  const sectionBody =
    "mt-6 max-w-3xl text-lg leading-8 text-slate-300";

  const premiumCard =
    "flex h-full min-h-[250px] flex-col rounded-3xl border border-white/10 bg-white/[0.03] p-7 md:p-8 transition-all duration-300 ease-out hover:-translate-y-1 hover:border-cyan-400/20 hover:bg-white/[0.05] hover:shadow-[0_0_20px_rgba(34,211,238,0.08)]";

  return (
    <MarketingLayout>
        {/* HERO */}
        <section className="relative overflow-hidden py-20 md:py-28">
          <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.14),transparent_28%),radial-gradient(circle_at_85%_15%,rgba(168,85,247,0.08),transparent_18%)]" />
          <div className="absolute left-1/2 top-0 -z-10 h-[460px] w-[460px] -translate-x-1/2 rounded-full bg-cyan-400/10 blur-3xl" />

          <div className="mx-auto max-w-7xl px-6 md:px-10">
            <p className="text-[12px] uppercase tracking-[0.28em] text-cyan-400">
              Security and Governance
            </p>

            <h1 className="mt-4 max-w-4xl text-5xl font-semibold leading-[0.95] tracking-tight text-white md:text-6xl lg:text-7xl">
              Built to secure AI access before execution
            </h1>

            <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-300">
              VoxCore inspects, classifies, scores, and controls every
              AI-generated request before it reaches production data.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              {trustChips.map((item) => (
                <span
                  key={item}
                  className="rounded-full border border-white/10 px-4 py-2 text-sm text-slate-300 transition-all duration-300 ease-out hover:-translate-y-0.5 hover:border-cyan-400/25 hover:bg-white/[0.04] hover:text-white"
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        </section>

        {/* SECURITY PRINCIPLES */}
        <section className="py-16 md:py-24">
          <div className="mx-auto max-w-7xl px-6 md:px-10">
            <h2 className={sectionHeading}>Security principles behind VoxCore</h2>

            <p className={sectionBody}>
              VoxCore is designed to govern AI-generated data access through
              inspection, enforcement, bounded execution, and full traceability.
            </p>

            <div className="mt-12 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
              {principles.map((item) => {
                const Icon = item.icon;
                return (
                  <div key={item.title} className={premiumCard}>
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-400/[0.06] shadow-[0_0_18px_rgba(34,211,238,0.08)]">
                      <Icon className="h-6 w-6 text-cyan-300" />
                    </div>

                    <h3 className="mt-4 text-2xl font-semibold text-white">
                      {item.title}
                    </h3>

                    <p className="mt-4 text-base leading-8 text-slate-300">
                      {item.body}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* RISK DETECTION */}
        <section className="py-16 md:py-24">
          <div className="mx-auto max-w-7xl px-6 md:px-10">
            <h2 className={sectionHeading}>Risk detection before execution</h2>

            <p className={sectionBody}>
              VoxCore evaluates requests across multiple dimensions so unsafe,
              anomalous, or sensitive access patterns can be identified before
              execution.
            </p>

            <div className="mt-12 grid gap-6 md:gap-8 md:grid-cols-2 xl:grid-cols-3">
              {riskLayers.map((item) => {
                const Icon = item.icon;
                return (
                  <div
                    key={item.title}
                    className={`rounded-3xl border p-7 md:p-8 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)] transition-all duration-300 ease-out hover:-translate-y-1 hover:scale-[1.01] ${
                      item.tone
                        ? item.tone
                        : "border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))]"
                    }`}
                  >
                    <span className="inline-flex rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 text-xs uppercase tracking-[0.18em] text-slate-400">
                      {item.label}
                    </span>

                    <div className="mt-5 flex h-12 w-12 items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-400/[0.06] shadow-[0_0_18px_rgba(34,211,238,0.08)]">
                      <Icon
                        className={`h-6 w-6 ${
                          item.tone ? "text-red-300" : "text-cyan-300"
                        }`}
                      />
                    </div>

                    <h3 className="mt-4 text-2xl font-semibold text-white">
                      {item.title}
                    </h3>

                    <p className="mt-4 text-base leading-8 text-slate-300">
                      {item.body}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* POLICY ENFORCEMENT */}
        <section className="py-16 md:py-24">
          <div className="mx-auto max-w-7xl px-6 md:px-10">
            <h2 className={sectionHeading}>Enforcement, not observation</h2>

            <p className={sectionBody}>
              VoxCore does not just detect risk. It applies policy in real time to
              allow, block, rewrite, or escalate requests before execution.
            </p>

            <div className="mt-14 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
              {enforcementOutcomes.map((item) => {
                const Icon = item.icon;
                return (
                  <div
                    key={item.title}
                    className={`flex h-full min-h-[230px] flex-col rounded-3xl border p-6 transition-all duration-300 ease-out hover:-translate-y-1 ${item.tone}`}
                  >
                    <Icon className="h-7 w-7" />
                    <h3 className="mt-4 text-2xl font-semibold">{item.title}</h3>
                    <p className="mt-4 text-base leading-8 text-slate-200">
                      {item.body}
                    </p>
                  </div>
                );
              })}
            </div>

            <p className="mt-10 max-w-4xl text-base leading-8 text-slate-300">
              Centralized policy logic applies across tables, queries, users, risk
              thresholds, and execution constraints.
            </p>
          </div>
        </section>

        {/* AUDIT LOGGING */}
        <section className="py-16 md:py-24">
          <div className="mx-auto max-w-7xl px-6 md:px-10">
            <h2 className={sectionHeading}>Audit trails built into every request</h2>

            <p className={sectionBody}>
              Every AI-generated request is logged with fingerprinting, decision
              outcomes, policy context, and execution metadata so teams can review
              what happened and why.
            </p>

            <div className="mt-10 flex flex-wrap gap-3 md:gap-4">
              {auditItems.map((item) => (
                <span
                  key={item}
                  className="inline-flex items-center gap-2 rounded-full border border-cyan-400/15 bg-cyan-400/[0.05] px-4 py-2 text-sm font-medium text-cyan-100 shadow-[0_0_12px_rgba(34,211,238,0.04)] backdrop-blur-sm"
                >
                  <Shield className="h-4 w-4" />
                  {item}
                </span>
              ))}
            </div>
          </div>
        </section>

        {/* PRODUCTION TRUST */}
        <section className="py-16 md:py-24">
          <div className="mx-auto max-w-6xl px-6 md:px-10">
            <div className="rounded-[32px] border border-white/10 bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.08),transparent_40%),rgba(255,255,255,0.03)] p-10 shadow-[0_0_40px_rgba(34,211,238,0.04)]">
              <h2 className={sectionHeading}>
                Built for governed AI access in production
              </h2>

              <p className={sectionBody}>
                VoxCore gives organizations the controls, visibility, and
                auditability needed to safely operate AI against real data in
                production environments.
              </p>

              <div className="mt-8 flex flex-wrap gap-3">
                {productionChips.map((item) => (
                  <span
                    key={item}
                    className="rounded-full border border-cyan-400/15 bg-cyan-400/[0.05] px-4 py-2 text-sm font-medium text-cyan-100 shadow-[0_0_12px_rgba(34,211,238,0.04)] transition-all duration-300 hover:-translate-y-0.5 hover:border-cyan-300/30 hover:bg-cyan-400/[0.08]"
                  >
                    {item}
                  </span>
                ))}
              </div>

              <p className="mt-8 max-w-4xl text-xl font-medium leading-8 text-white">
                VoxCore is designed to give teams the confidence to use AI with
                real data — without surrendering control.
              </p>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-16 md:py-20">
          <div className="mx-auto max-w-5xl px-6 text-center md:px-10">
            <p className="text-[12px] uppercase tracking-[0.28em] text-cyan-400">
              See how governed AI security works in practice
            </p>

            <h2 className="mx-auto mt-4 max-w-4xl text-4xl font-semibold leading-tight text-white md:text-6xl">
              Explore secure AI data access with VoxCore
            </h2>

            <p className="mx-auto mt-6 max-w-3xl text-lg leading-8 text-slate-300">
              Explore how VoxCore secures AI-generated data access, or speak with
              us about deploying it in your environment.
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
