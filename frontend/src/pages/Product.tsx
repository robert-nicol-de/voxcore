import { Card } from "@/components/Card";
import { MarketingContainer, MarketingLayout } from "@/components/layout/MarketingLayout";

export const Product = () => {
  const features = [
    {
      title: "Query Inspection",
      desc: "Every SQL query is parsed and validated before execution.",
    },
    {
      title: "Risk Scoring",
      desc: "Queries are classified based on structure, cost, and sensitivity.",
    },
    {
      title: "Policy Enforcement",
      desc: "Custom policies define what queries are allowed, blocked, or require approval.",
    },
    {
      title: "Audit Logging",
      desc: "Every query is logged with context, fingerprint, and decision outcome.",
    },
  ];

  const flow = [
    "AI generates SQL",
    "VoxCore inspects query",
    "Risk score calculated",
    "Policy engine evaluates",
    "Decision enforced",
  ];

  return (
    <MarketingLayout>
      <section className="pb-24 pt-14 lg:pb-32 lg:pt-20">
        <MarketingContainer>
          <div className="space-y-18">
            {/* HEADER */}
            <div className="max-w-4xl space-y-5">
              <div className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-300/80">
                Product Architecture
              </div>
              <h1 className="text-5xl font-semibold leading-tight tracking-tight lg:text-6xl">
                The Governance Layer for AI Data Access
              </h1>
              <p className="max-w-3xl text-lg leading-8 text-gray-400">
                VoxCore sits between AI systems and your database, inspecting every query before execution.
              </p>
            </div>

            {/* CONTROL LAYER */}
            <Card className="border border-white/10 bg-white/5 p-8">
              <h2 className="text-xl font-semibold mb-6">How VoxCore Works</h2>

              <div className="flex flex-col md:flex-row md:items-center gap-4 text-sm text-gray-400">
                <span>AI</span>
                <span>→</span>
                <span>SQL Generation</span>
                <span>→</span>
                <span className="text-blue-400 font-medium">VoxCore (Control Layer)</span>
                <span>→</span>
                <span>Database</span>
              </div>
            </Card>

            {/* PIPELINE */}
            <div>
              <h2 className="text-xl font-semibold mb-6">Query Execution Pipeline</h2>

              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
                {flow.map((step) => (
                  <Card key={step} className="border border-white/10 bg-white/5 p-6">
                    <p className="text-sm text-gray-300">{step}</p>
                  </Card>
                ))}
              </div>
            </div>

            {/* CORE FEATURES */}
            <div>
              <h2 className="text-xl font-semibold mb-6">Core Capabilities</h2>

              <div className="grid md:grid-cols-2 gap-6">
                {features.map((f) => (
                  <Card key={f.title} className="border border-white/10 bg-white/5 p-7">
                    <h3 className="font-semibold mb-2">{f.title}</h3>
                    <p className="text-gray-400 text-sm">{f.desc}</p>
                  </Card>
                ))}
              </div>
            </div>

            {/* DECISION OUTCOMES */}
            <div>
              <h2 className="text-xl font-semibold mb-6">Decision Outcomes</h2>

              <div className="grid md:grid-cols-3 gap-6">
                <Card className="border border-rose-400/15 bg-rose-400/5 p-7">
                  <h3 className="text-red-400 font-semibold mb-2">Blocked</h3>
                  <p className="text-sm text-gray-400">
                    High-risk queries are prevented from executing.
                  </p>
                </Card>

                <Card className="border border-amber-400/15 bg-amber-400/5 p-7">
                  <h3 className="text-yellow-400 font-semibold mb-2">Pending Approval</h3>
                  <p className="text-sm text-gray-400">
                    Medium-risk queries require human approval.
                  </p>
                </Card>

                <Card className="border border-emerald-400/15 bg-emerald-400/5 p-7">
                  <h3 className="text-green-400 font-semibold mb-2">Allowed</h3>
                  <p className="text-sm text-gray-400">
                    Safe queries execute within defined policies.
                  </p>
                </Card>
              </div>
            </div>

            {/* TRUST LAYER */}
            <Card className="border border-white/10 bg-[linear-gradient(135deg,rgba(59,130,246,0.12),rgba(15,23,42,0.4))] p-8">
              <h2 className="text-xl font-semibold mb-4">
                Built for Control and Transparency
              </h2>

              <p className="text-gray-400">
                Every query is traceable, explainable, and governed. VoxCore ensures your data remains protected even when accessed through AI systems.
              </p>
            </Card>
          </div>
        </MarketingContainer>
      </section>
    </MarketingLayout>
  );
};

export default Product;
