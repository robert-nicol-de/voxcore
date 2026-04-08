import { Card } from "@/components/Card";
import { MarketingContainer, MarketingLayout } from "@/components/layout/MarketingLayout";
import { Link } from "react-router-dom";

export const Home = () => {
  return (
    <MarketingLayout>
      <section className="pb-24 pt-14 lg:pb-32 lg:pt-20">
        <MarketingContainer>
          <div className="space-y-24 lg:space-y-28">
            <div className="grid gap-10 lg:grid-cols-[minmax(0,1.15fr)_minmax(320px,0.85fr)] lg:items-end">
              <div className="max-w-5xl space-y-8">
                <div className="inline-flex rounded-full border border-sky-400/20 bg-sky-400/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.28em] text-sky-200/80">
                  VoxCore • Production AI Governance
                </div>
                <div className="space-y-5">
                  <div className="text-sm font-semibold uppercase tracking-[0.34em] text-sky-300/70">
                    VoxCore
                  </div>
                  <h1 className="max-w-6xl text-6xl font-semibold leading-[0.98] tracking-tight sm:text-7xl xl:text-[5.4rem]">
                    Every AI query should be governed before it touches your data.
                  </h1>
                  <p className="max-w-3xl text-xl leading-8 text-slate-300">
                    VoxCore is the governance and intelligence layer between AI and your database —
                    inspecting queries, enforcing policy, and preventing unsafe execution before damage is done.
                  </p>
                </div>

                <div className="flex flex-wrap gap-4">
                  <Link
                    to="/playground"
                    className="rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-950 transition hover:scale-[1.01] hover:bg-slate-100"
                  >
                    Open Playground
                  </Link>
                  <Link
                    to="/pricing"
                    className="rounded-full border border-sky-300/20 bg-sky-400/10 px-6 py-3 text-sm font-medium text-sky-100 transition hover:border-sky-200/35 hover:bg-sky-400/15"
                  >
                    Deploy VoxCore
                  </Link>
                  <Link
                    to="/product"
                    className="rounded-full border border-white/12 px-6 py-3 text-sm font-medium text-slate-200 transition hover:border-white/30 hover:bg-white/6 hover:text-white"
                  >
                    Explore Product
                  </Link>
                </div>
              </div>

              <div className="rounded-[2rem] border border-white/10 bg-[linear-gradient(160deg,rgba(15,23,42,0.92),rgba(7,12,24,0.84))] p-8 shadow-[0_24px_80px_rgba(2,8,23,0.55)]">
                <div className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-300/75">
                  Live Governance Path
                </div>
                <div className="mt-6 space-y-4">
                  {[
                    "Query Router",
                    "Governance Engine",
                    "Bounded Execution",
                    "Insight Layer",
                  ].map((step, index) => (
                    <div
                      key={step}
                      className="flex items-center justify-between rounded-2xl border border-white/8 bg-white/5 px-4 py-4"
                    >
                      <div>
                        <div className="text-sm font-medium text-white">{step}</div>
                        <div className="mt-1 text-sm text-slate-400">
                          {index === 0 && "Incoming AI query is routed into a governed path."}
                          {index === 1 && "Risk, policy, and safety checks run before execution."}
                          {index === 2 && "Limits, timeouts, and non-destructive controls stay enforced."}
                          {index === 3 && "Results become narratives, alerts, and explainable actions."}
                        </div>
                      </div>
                      <div className="ml-4 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-emerald-200">
                        Active
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <Card className="border border-white/10 bg-white/5 p-8 shadow-[0_24px_80px_rgba(2,8,23,0.45)]">
              <div className="flex flex-wrap items-center gap-3 text-sm text-gray-400">
                <span>AI</span>
                <span>→</span>
                <span>SQL Query</span>
                <span>→</span>
                <span className="font-medium text-blue-400">VoxCore (Control Layer)</span>
                <span>→</span>
                <span>Database</span>
              </div>
            </Card>

            <div className="grid gap-6 md:grid-cols-2">
              <Card className="border border-rose-400/15 bg-rose-400/5 p-7">
                <h3 className="mb-3 text-red-400 font-semibold">Blocked Query</h3>
                <p className="mb-3 text-sm text-gray-400">DELETE FROM users;</p>
                <p className="text-sm text-gray-500">Risk Score: 100 — No WHERE clause detected</p>
              </Card>

              <Card className="border border-emerald-400/15 bg-emerald-400/5 p-7">
                <h3 className="mb-3 text-green-400 font-semibold">Allowed Query</h3>
                <p className="mb-3 text-sm text-gray-400">SELECT id FROM users LIMIT 100;</p>
                <p className="text-sm text-gray-500">Risk Score: 12 — Safe read-only query</p>
              </Card>
            </div>

            <div>
              <h2 className="mb-6 text-xl font-semibold">Core Capabilities</h2>

              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {[
                  "Query Inspection",
                  "Risk Scoring",
                  "Policy Enforcement",
                  "Audit Logging",
                ].map((item) => (
                  <Card key={item} className="border border-white/10 bg-white/5 p-6">
                    <p className="text-sm text-gray-300">{item}</p>
                  </Card>
                ))}
              </div>
            </div>

            <div>
              <h2 className="mb-6 text-xl font-semibold">How It Works</h2>

              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {[
                  "Receive Query",
                  "Analyze Structure",
                  "Apply Policies",
                  "Enforce Decision",
                ].map((step) => (
                  <Card key={step} className="border border-white/10 bg-white/5 p-6">
                    <p className="text-sm text-gray-300">{step}</p>
                  </Card>
                ))}
              </div>
            </div>

            <Card className="border border-white/10 bg-[linear-gradient(135deg,rgba(56,189,248,0.12),rgba(15,23,42,0.4))] p-8">
              <h2 className="mb-4 text-xl font-semibold">Built for Control and Compliance</h2>

              <p className="mb-4 text-gray-400">
                Every query is logged, traceable, and governed. VoxCore ensures compliance across SOC 2, HIPAA, GDPR, and PCI-DSS.
              </p>

              <p className="text-sm text-gray-500">SOC 2 • HIPAA • GDPR • PCI-DSS</p>
            </Card>

            <div className="max-w-3xl rounded-[2rem] border border-white/10 bg-white/5 p-8">
              <h2 className="mb-4 text-3xl font-semibold">Connect AI to your database — safely.</h2>

              <p className="mb-6 text-base leading-7 text-gray-400">
                Without governance, one query can break production.
              </p>

              <Link
                to="/pricing"
                className="inline-flex rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-950 transition hover:scale-[1.01] hover:bg-slate-100"
              >
                Deploy VoxCore
              </Link>
            </div>
          </div>
        </MarketingContainer>
      </section>
    </MarketingLayout>
  );
};

export default Home;
