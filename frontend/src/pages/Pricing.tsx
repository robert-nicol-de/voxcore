import { Card } from "@/components/Card";
import { Button } from "@/components/Button";
import MarketingLayout from "@/components/layout/MarketingLayout";
import { MarketingContainer } from "@/components/layout/MarketingLayout";

const plans = [
  {
    name: "Starter",
    tag: "Development",
    price: "Free",
    desc: "Protect non-production data. Validate query behavior before rollout.",
    features: ["Query Inspection", "Basic Risk Scoring", "Audit Logging"],
    cta: "Start Free",
  },
  {
    name: "Professional",
    tag: "Production",
    price: "$49/mo",
    desc: "Enforce policies at scale. Monitor real-time query risk in live environments.",
    features: [
      "Advanced Risk Scoring",
      "Policy Enforcement",
      "Anomaly Detection",
      "Real-time Monitoring",
    ],
    cta: "Enable Governance",
  },
  {
    name: "Enterprise",
    tag: "Governance",
    price: "Custom",
    desc: "Full governance layer for compliance, audit readiness, and critical systems.",
    features: [
      "Custom Policy Engine",
      "Compliance Automation",
      "Query Forensics",
      "Dedicated Support",
    ],
    cta: "Contact Sales",
  },
];

const includedFeatures = [
  "Query Inspection",
  "Risk Scoring",
  "Policy Enforcement",
  "Audit Logging",
];

const comparisonRows = [
  { feature: "Connected Databases", starter: "Up to 10", pro: "Unlimited", ent: "Unlimited" },
  { feature: "Queries / Month", starter: "1M", pro: "50M+", ent: "Unlimited" },
  { feature: "Real-time SQL Analysis", starter: "✓", pro: "✓", ent: "✓" },
  { feature: "Risk Classification", starter: "✓", pro: "Advanced", ent: "Advanced+" },
  { feature: "Audit Retention", starter: "7 days", pro: "90 days", ent: "Unlimited" },
  { feature: "Query Context Tracking", starter: "✗", pro: "✓", ent: "✓" },
  { feature: "Anomaly Detection", starter: "✗", pro: "✓", ent: "✓" },
  { feature: "Custom Policies", starter: "Templates", pro: "Full", ent: "Custom Built" },
  { feature: "Role-Based Access", starter: "Basic", pro: "Advanced", ent: "Enterprise SSO" },
  { feature: "API Access", starter: "✗", pro: "✓", ent: "✓" },
  { feature: "Support SLA", starter: "Email", pro: "4 hours", ent: "1 hour (24/7)" },
  { feature: "Compliance Automation", starter: "✗", pro: "Add-on", ent: "Included" },
];

const faqs = [
  {
    q: "What's included in the free trial?",
    a: "All trials come with full Professional plan features for 14 days. No credit card required.",
  },
  {
    q: "How are queries counted?",
    a: "Every SQL statement analyzed by VoxCore counts as one query, including blocked, approved, and reviewed executions.",
  },
  {
    q: "Can I scale up mid-month?",
    a: "Yes. Upgrades take effect immediately and billing is prorated automatically.",
  },
  {
    q: "Do you offer annual discounts?",
    a: "Yes. Annual plans receive discounted pricing, and Enterprise volume agreements are available.",
  },
  {
    q: "Can VoxCore be deployed on-premise?",
    a: "Yes. Enterprise plans support private cloud and on-premise deployment options.",
  },
];

export const Pricing = () => {
  return (
    <MarketingLayout>
      <section className="pb-24 pt-14 lg:pb-32 lg:pt-20">
        <MarketingContainer>
          <div className="space-y-16">
            <div className="max-w-4xl space-y-5">
              <div className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-300/80">
                Pricing
              </div>
              <h1 className="text-5xl font-semibold tracking-tight lg:text-6xl">
                Governance that scales with your infrastructure
              </h1>
              <p className="text-gray-400 max-w-3xl text-lg leading-8">
                Every query is inspected before execution. Choose the level of
                control your systems require.
              </p>
            </div>

            <Card className="border border-white/10 bg-white/5 p-8">
              <div className="space-y-3">
                <p className="text-red-400 font-medium">
                  AI-generated queries introduce uncontrolled risk.
                </p>
                <p className="text-gray-400 text-sm">
                  AI-generated and programmatic queries introduce uncontrolled
                  risk. Without inspection, a single malformed query can expose
                  sensitive data, violate compliance rules, or damage critical
                  infrastructure.
                </p>
                <p className="text-gray-400 text-sm">
                  VoxCore ensures every query is{" "}
                  <span className="text-blue-300 font-semibold">
                    inspected, controlled, and logged
                  </span>{" "}
                  before execution. This transforms query risk from a blind spot
                  into a managed, auditable system.
                </p>
              </div>
            </Card>

            <div className="space-y-6">
              <h2 className="text-xl font-semibold">Every plan includes</h2>
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {includedFeatures.map((item) => (
                  <Card key={item} className="border border-white/10 bg-white/5 p-6">
                    <p className="text-sm text-gray-300">{item}</p>
                  </Card>
                ))}
              </div>
            </div>

            <div className="grid gap-6 md:grid-cols-3">
              {plans.map((plan) => (
                <Card key={plan.name} className="border border-white/10 bg-white/5 p-8">
                  <div className="space-y-4">
                    <div>
                      <p className="text-blue-400 text-sm mb-1">{plan.tag}</p>
                      <h3 className="text-xl font-semibold">{plan.name}</h3>
                    </div>

                    <p className="text-2xl font-bold">{plan.price}</p>

                    <p className="text-gray-400 text-sm">{plan.desc}</p>

                    <div className="space-y-2">
                      {plan.features.map((feature) => (
                        <div key={feature} className="text-sm text-gray-300">
                          • {feature}
                        </div>
                      ))}
                    </div>

                    <Button>{plan.cta}</Button>
                  </div>
                </Card>
              ))}
            </div>

            <div className="text-gray-500 text-sm">
              SOC 2 • HIPAA • GDPR • PCI-DSS
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <Card className="border border-rose-400/15 bg-rose-400/5 p-8">
                <h3 className="text-red-400 font-semibold mb-4">
                  Without VoxCore
                </h3>
                <ul className="space-y-2 text-sm text-gray-400">
                  <li>Unbounded queries</li>
                  <li>Data exposure risks</li>
                  <li>No audit trail</li>
                  <li>Compliance gaps</li>
                  <li>High breach risk</li>
                </ul>
              </Card>

              <Card className="border border-sky-400/15 bg-sky-400/5 p-8">
                <h3 className="text-blue-400 font-semibold mb-4">
                  With VoxCore
                </h3>
                <ul className="space-y-2 text-sm text-gray-400">
                  <li>Controlled execution</li>
                  <li>Policy enforcement</li>
                  <li>Full audit visibility</li>
                  <li>Compliance-ready</li>
                  <li>Reduced risk</li>
                </ul>
              </Card>
            </div>

            <div className="space-y-6">
              <h2 className="text-3xl font-bold">Feature Comparison</h2>
              <div className="overflow-x-auto rounded-[1.5rem] border border-white/10 bg-white/5">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left py-4 px-4">Feature</th>
                      <th className="text-center py-4 px-4">Starter</th>
                      <th className="text-center py-4 px-4">Professional</th>
                      <th className="text-center py-4 px-4">Enterprise</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/10">
                    {comparisonRows.map((row) => (
                      <tr key={row.feature} className="hover:bg-white/5 transition">
                        <td className="py-4 px-4 text-gray-300">{row.feature}</td>
                        <td className="py-4 px-4 text-center text-gray-400">
                          {row.starter}
                        </td>
                        <td className="py-4 px-4 text-center text-gray-400">
                          {row.pro}
                        </td>
                        <td className="py-4 px-4 text-center text-gray-400">
                          {row.ent}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="space-y-6 max-w-3xl">
              <h2 className="text-3xl font-bold">Pricing FAQ</h2>
              {faqs.map((item) => (
                <Card key={item.q} className="border border-white/10 bg-white/5 p-7">
                  <h3 className="font-semibold mb-2">{item.q}</h3>
                  <p className="text-sm text-gray-400">{item.a}</p>
                </Card>
              ))}
            </div>

            <div className="max-w-3xl space-y-4 rounded-[2rem] border border-white/10 bg-[linear-gradient(135deg,rgba(56,189,248,0.12),rgba(15,23,42,0.4))] p-8">
              <h2 className="text-2xl font-semibold">
                Deploy VoxCore → Protect your database
              </h2>
              <p className="text-gray-400">
                The cost of one bad query is higher than this entire layer.
              </p>
              <Button>Deploy VoxCore</Button>
            </div>
          </div>
        </MarketingContainer>
      </section>
    </MarketingLayout>
  );
};

export default Pricing;
