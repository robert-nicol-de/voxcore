import React from "react";
export default function FeatureSection() {
  return (
    <section className="bg-[#101828] text-white py-16 px-6">
      {/* TODO: Add feature highlights */}
      <h2 className="text-3xl font-bold text-center mb-10">Why Choose VoxCore?</h2>
      <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
        <div className="bg-[#0f172a] p-6 rounded-xl">
          <h3 className="font-semibold mb-2">Query Firewall</h3>
          <p className="text-sm opacity-80">Every AI-generated SQL is validated for safety and compliance.</p>
        </div>
        <div className="bg-[#0f172a] p-6 rounded-xl">
          <h3 className="font-semibold mb-2">Multi-Database</h3>
          <p className="text-sm opacity-80">Connect Snowflake, PostgreSQL, SQL Server, and more.</p>
        </div>
        <div className="bg-[#0f172a] p-6 rounded-xl">
          <h3 className="font-semibold mb-2">Full Audit Trail</h3>
          <p className="text-sm opacity-80">Track every query, decision, and user action for governance.</p>
        </div>
      </div>
    </section>
  );
}
