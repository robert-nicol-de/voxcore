import { Card } from "@/components/Card";
import { MarketingContainer, MarketingLayout } from "@/components/layout/MarketingLayout";
import { RiskItem } from "@/components/voxcore/RiskItem";

export const Security = () => {
  const riskLayers = [
    {
      id: 1,
      title: "Table-Level",
      desc: "Sensitive data access detection",
    },
    {
      id: 2,
      title: "Query Pattern",
      desc: "Destructive operations (DELETE, DROP)",
    },
    {
      id: 3,
      title: "Cost-Based",
      desc: "Expensive queries and full table scans",
    },
    {
      id: 4,
      title: "Temporal",
      desc: "Time-based anomalies",
    },
    {
      id: 5,
      title: "Contextual",
      desc: "User role and behavior analysis",
    },
  ];

  return (
    <MarketingLayout>
      <section className="pb-24 pt-14 lg:pb-32 lg:pt-20">
        <MarketingContainer>
          <div className="space-y-12">
            <div className="max-w-4xl space-y-5">
              <div className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-300/80">
                Security and Governance
              </div>
              <h1 className="text-5xl font-semibold mb-4 tracking-tight lg:text-6xl">
                Security Architecture
              </h1>
              <p className="text-gray-400 max-w-3xl text-lg leading-8">
                Every query is inspected, classified, and controlled before execution.
              </p>
            </div>

            <Card className="border border-white/10 bg-white/5 p-8">
              <h2 className="text-xl font-semibold mb-6">
                Risk Detection Layers
              </h2>

              <div className="space-y-3">
                {riskLayers.map((risk) => (
                  <RiskItem key={risk.id} {...risk} />
                ))}
              </div>
            </Card>

            <Card className="border border-white/10 bg-white/5 p-8">
              <h2 className="text-xl font-semibold mb-4">
                Policy Enforcement Engine
              </h2>

              <p className="text-gray-400">
                VoxCore applies layered policies across tables, queries,
                cost thresholds, and user context before allowing execution.
              </p>
            </Card>

            <Card className="border border-white/10 bg-[linear-gradient(135deg,rgba(56,189,248,0.12),rgba(15,23,42,0.4))] p-8">
              <h2 className="text-xl font-semibold mb-4">
                Audit Logging
              </h2>

              <p className="text-gray-400">
                Every query is logged with fingerprinting, decision outcome,
                and contextual metadata for full traceability.
              </p>
            </Card>
          </div>
        </MarketingContainer>
      </section>
    </MarketingLayout>
  );
};

export default Security;
