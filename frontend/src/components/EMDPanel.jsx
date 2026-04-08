import { useState } from "react";

export default function EMDPanel() {
  const [insights, setInsights] = useState([]);

  const runEMD = async () => {
    const res = await fetch("/api/query?mode=explain");
    const data = await res.json();
    setInsights(data.insights);
  };

  return (
    <div className="bg-gray-900 p-6 rounded-2xl shadow-lg">
      <button
        onClick={runEMD}
        className="bg-neon-green text-black px-4 py-2 rounded-xl mb-4"
      >
        🧠 Explain My Data
      </button>
      <div className="space-y-3">
        {insights.map((i, idx) => (
          <div
            key={idx}
            className="bg-gray-800 p-3 rounded-lg border-l-4 border-neon-green"
          >
            {i}
          </div>
        ))}
      </div>
    </div>
  );
}
