import React, { useState } from "react";
import AppLayout from "../../layouts/AppLayout";

export default function Sandbox() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<string | null>(null);
  const [risk, setRisk] = useState<string | null>(null);

  const handleRun = () => {
    setResult("[Real query results will appear here]");
    setRisk("Risk Score: -- (User Environment)");
  };

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto mt-8 bg-white/5 border border-white/10 rounded-xl p-8 relative">
        <div className="absolute top-4 right-4 text-xs text-sky-400 opacity-60 select-none">User Sandbox</div>
        <h1 className="text-2xl font-bold mb-2">Sandbox</h1>
        <p className="text-gray-400 mb-6">Test AI queries on your environment. (Real data, real risk analysis coming soon.)</p>
        <textarea
          className="w-full p-3 rounded bg-white/10 mb-4 text-white"
          rows={3}
          placeholder="Ask a question or type a SQL query..."
          value={query}
          onChange={e => setQuery(e.target.value)}
        />
        <button className="bg-blue-500 px-6 py-2 rounded font-semibold mb-4" onClick={handleRun}>
          Run Query
        </button>
        {result && (
          <div className="bg-white/10 rounded p-4 mt-4">
            <div className="mb-2 text-sm text-gray-300">{result}</div>
            <div className="text-xs text-sky-400">{risk}</div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
