


import React from "react";

import Layout from "../components/ui/Layout";
import Section from "../components/ui/Section";
import DevAISection from "./DevAISection";

type Card = {
  title: string;
  desc: string;
  points: string[];
};

const cards: Card[] = [
  {
    title: "🛡️ Query Firewall",
    desc: "Blocks dangerous and invalid queries before they hit your database.",
    points: [
      "Prevents destructive operations",
      "Validates AI-generated SQL",
      "Enforces safety rules"
    ]
  },
  {
    title: "⚡ Cost Guard",
    desc: "Stops runaway queries before they become expensive mistakes.",
    points: [
      "Detects full table scans",
      "Flags high-cost joins",
      "Scores query risk"
    ]
  },
  {
    title: "📜 AI Audit Logs",
    desc: "Full visibility into every AI-generated query and decision.",
    points: [
      "Track every query",
      "Monitor behavior",
      "Full execution history"
    ]
  },
  {
    title: "🧠 Insight Engine",
    desc: "Turns raw data into real business insights automatically.",
    points: [
      "Detects trends",
      "Finds anomalies",
      "Suggests next actions"
    ]
  }
];

type ComparisonRow = {
  name: string;
  fabric: string;
  vox: string;
};

const comparison: ComparisonRow[] = [
  { name: "Natural language queries", fabric: "✅", vox: "✅" },
  { name: "SQL generation", fabric: "✅", vox: "✅" },
  { name: "Query safety enforcement", fabric: "❌", vox: "✅" },
  { name: "Cost control", fabric: "❌", vox: "✅" },
  { name: "Query blocking", fabric: "❌", vox: "✅" },
  { name: "Insight generation", fabric: "⚠️ Basic", vox: "✅ Advanced" },
  { name: "Cross-platform governance", fabric: "❌", vox: "✅" }
];

const LandingPage: React.FC = () => (
  <Layout>
    <Section center>
      <h1 className="text-5xl font-bold mb-6 tracking-tight">
        VoxCore: Governed AI for Data
      </h1>
      <p className="text-xl text-slate-400 mb-8 max-w-2xl mx-auto">
        AI that understands your data — and respects your rules. VoxCore turns natural language into governed, production-safe analytics. Ask questions in plain English, get safe, actionable insights — not just data.
      </p>
      <div className="grid md:grid-cols-2 gap-8 mb-12">
        <div>
          <h2 className="text-2xl font-semibold mb-4">How VoxCore Works</h2>
          <p>1. AI generates a query</p>
          <p>2. VoxCore intercepts it</p>
          <p>3. We validate, score risk, and optimize</p>
          <p>4. Unsafe queries are blocked</p>
          <p>5. Safe results + insights are returned</p>
        </div>
        <div className="grid grid-cols-1 gap-6">
          {cards.map((card) => (
            <div key={card.title} className="p-6 rounded-xl border border-white/10 bg-white/[0.02] hover:bg-white/[0.06] transition-all">
              <h3 className="text-xl font-bold mb-2">{card.title}</h3>
              <p className="mb-2 text-slate-300">{card.desc}</p>
              <ul className="list-disc list-inside text-slate-400">
                {card.points.map((pt) => (
                  <li key={pt}>{pt}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </Section>

    <Section center>
      <h2 className="text-3xl font-bold mb-6">VoxCore vs. Fabric AI</h2>
      <div className="overflow-x-auto">
        <table className="min-w-[400px] mx-auto border-collapse border border-slate-700">
          <thead>
            <tr>
              <th className="px-4 py-2 border-b border-slate-700 text-left">Feature</th>
              <th className="px-4 py-2 border-b border-slate-700">Fabric AI</th>
              <th className="px-4 py-2 border-b border-slate-700">VoxCore</th>
            </tr>
          </thead>
          <tbody>
            {comparison.map((row) => (
              <tr key={row.name}>
                <td className="px-4 py-2 border-b border-slate-800">{row.name}</td>
                <td className="px-4 py-2 border-b border-slate-800 text-center">{row.fabric}</td>
                <td className="px-4 py-2 border-b border-slate-800 text-center">{row.vox}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Section>

    <Section center>
      <div className="text-center py-24">
        <h2 className="text-4xl font-bold mb-6">Control the brain behind your data</h2>
        <button className="bg-blue-600 px-8 py-4 rounded-2xl text-lg">
          Get Started
        </button>
      </div>
    </Section>

    {/* Dev AI Product Reveal Section */}
    <DevAISection />
  </Layout>
);

export default LandingPage;
