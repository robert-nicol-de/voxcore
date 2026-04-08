import React from "react";

const HeroSection: React.FC = () => (
  <section className="max-w-7xl mx-auto px-6 pt-20 pb-16">
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
      {/* LEFT SIDE */}
      <div>
        <h1 className="text-4xl font-bold leading-tight">
          The AI Governance Layer<br />For Production Databases
        </h1>
        <p className="mt-4 text-gray-400 max-w-lg">
          Control how AI interacts with your databases.<br />Inspect, validate, and audit every AI-generated SQL query before execution.
        </p>
        <div className="mt-6 flex gap-4">
          <button className="btn-primary">Launch VoxCloud</button>
          <button className="btn-secondary">Playground</button>
        </div>
        <ul className="mt-6 space-y-1 text-[16px] text-[var(--text-secondary)]">
          <li>✔ Policy-controlled AI access</li>
          <li>✔ Full audit & explainability</li>
          <li>✔ Prevent costly / unsafe queries</li>
        </ul>
      </div>
      {/* RIGHT SIDE */}
      <div className="bg-[#111827] rounded-2xl p-6 shadow-xl border border-gray-800">
        <div className="pipeline-card-glow">
          <ol className="pipeline-list">
            <li>User Prompt</li>
            <li>AI Generates SQL</li>
            <li>VoxCore Query Inspector</li>
            <li>AI Risk Engine</li>
            <li>Policy Engine</li>
            <li>Sandbox Execution</li>
            <li>Production Database</li>
          </ol>
        </div>
      </div>
    </div>
  </section>
);

export default HeroSection;
