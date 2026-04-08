import { useState } from "react";
import { sendQuery } from "../api/voxcoreApi";
import ChartRenderer from "../components/ChartRenderer";
import DataTable from "../components/DataTable";

export default function AskQueryScreen() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAsk = async (q?: string) => {
    const askValue = typeof q === "string" ? q : query;
    if (!askValue.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await sendQuery(askValue, sessionId);
      setSessionId(res.session_id);
      setResponse(res);
    } catch (err) {
      setError("Failed to fetch insights");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">

      {/* 🔍 Query Bar */}
      <div className="bg-gradient-to-br from-gray-900 to-gray-800 p-6 rounded-2xl shadow-xl border border-gray-700">
        <h2 className="text-lg text-gray-400 mb-2">Ask VoxCore</h2>
        <div className="flex gap-3">
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            className="flex-1 bg-black/40 border border-gray-700 rounded-xl px-4 py-3 text-white"
            placeholder="Ask anything about your data..."
            onKeyDown={e => { if (e.key === "Enter") handleAsk(); }}
          />
          <button
            onClick={() => handleAsk()}
            className="bg-blue-600 hover:bg-blue-500 px-6 rounded-xl font-medium text-white"
            disabled={loading}
          >
            Ask
          </button>
        </div>
      </div>

      {/* 🧠 MAIN INSIGHT */}
      {response && (
        <div className="bg-gradient-to-br from-blue-900/40 to-gray-900 p-6 rounded-2xl border border-blue-800 shadow-lg transition-all duration-500 ease-out">
          <div className="text-sm text-blue-400 mb-2">Key Insight</div>
          <div className="text-2xl font-semibold text-white">
            {response.narrative}
          </div>
        </div>
      )}

      {/* 📊 DATA + CHART */}
      {response && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chart */}
          <div className="lg:col-span-2 bg-gray-900 p-6 rounded-2xl border border-gray-800">
            <div className="text-sm text-gray-400 mb-4">Visualization</div>
            {response.chart && response.data && (
              <ChartRenderer data={response.data} config={response.chart} />
            )}
          </div>
          {/* Metrics Panel */}
          <div className="bg-gray-900 p-6 rounded-2xl border border-gray-800 space-y-4">
            <div>
              <div className="text-gray-400 text-sm">Risk Score</div>
              <div className="text-green-400 text-xl font-semibold">
                {response.metadata?.cost_score}
              </div>
            </div>
            <div>
              <div className="text-gray-400 text-sm">Execution Time</div>
              <div className="text-white text-xl">
                {response.metadata?.execution_time} ms
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 💡 SUGGESTIONS */}
      {response && (
        <div className="bg-gray-900 p-6 rounded-2xl border border-gray-800">
          <div className="text-sm text-gray-400 mb-3">Explore Further</div>
          <div className="flex flex-wrap gap-3">
            {response.suggestions?.map((s: string) => (
              <button
                key={s}
                onClick={() => handleAsk(s)}
                className="px-4 py-2 bg-blue-600/20 border border-blue-500 rounded-xl hover:bg-blue-600/30 text-white"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-blue-400 animate-pulse text-center">
          Analyzing your data...
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="text-red-400 text-center">
          {error}
        </div>
      )}

    </div>
  );
}

