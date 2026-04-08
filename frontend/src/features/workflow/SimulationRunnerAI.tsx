import { useState } from "react";

function getConfidenceColor(confidence) {
  if (confidence >= 0.85) return "text-green-600";
  if (confidence >= 0.7) return "text-yellow-600";
  return "text-red-600";
}

export function SimulationResults({ predictions, summary }) {
  if (!predictions?.length) return null;
  return (
    <div className="mt-6 space-y-3">
      {summary && (
        <div className="p-4 bg-blue-50 rounded-xl mb-4">
          <h3 className="font-semibold">🧪 Simulation Result</h3>
          <p>
            Estimated Impact: <span className="text-green-600 font-medium">+{(summary.total_impact * 100).toFixed(1)}%</span>
          </p>
          <p>Confidence: {(summary.confidence * 100).toFixed(0)}%</p>
          <p className={summary.risk < 0.3 ? "text-green-600" : "text-red-500"}>
            Risk: {(summary.risk * 100).toFixed(0)}%
          </p>
        </div>
      )}
      {predictions.filter(p => p.step !== "outcome").map((p, i) => (
        <div key={i} className="p-3 rounded-lg border bg-gray-50">
          <div className="font-medium">{p.label}</div>
          {p.step === "action" && (
            <div className="flex justify-between items-center mt-1">
              <span className="text-xs text-green-600">
                +{(p.impact_range ? p.impact_range[0] * 100 : p.predicted_impact * 100).toFixed(0)}%
                {p.impact_range && (
                  <span> → {(p.impact_range[1] * 100).toFixed(0)}%</span>
                )}
              </span>
              <span className="text-xs text-gray-500">
                {(p.confidence * 100).toFixed(0)}%
              </span>
            </div>
          )}
          {p.step === "condition" && (
            <div>
              YES: <span className="text-green-600 font-semibold">{Math.round((p.probability_true || 0) * 100)}%</span> &nbsp; NO: <span className="text-red-600 font-semibold">{Math.round((p.probability_false || 0) * 100)}%</span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export function SimulationRunnerAI({ workflow, setNodePredictions, setBranchProbs }) {
  const [predictions, setPredictions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [running, setRunning] = useState(false);

  const runSimulation = async () => {
    setRunning(true);
    setPredictions([]);
    setSummary(null);
    const res = await fetch("/api/workflows/simulate-ai", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(workflow)
    });
    const data = await res.json();
    setPredictions(data.predictions);
    setSummary(data.summary);
    if (setNodePredictions && Array.isArray(data.predictions)) {
      setNodePredictions(data.predictions);
    }
    if (setBranchProbs && data.branch_probs) {
      setBranchProbs(data.branch_probs);
    }
    setRunning(false);
  };

  return (
    <div>
      <button
        onClick={runSimulation}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg"
      >
        🧪 Simulate
      </button>
      {predictions.length > 0 && <SimulationResults predictions={predictions} summary={summary} />}
    </div>
  );
}
