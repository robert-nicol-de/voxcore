
import { useState, useCallback } from "react";

function getPreview({ metric, threshold, action, confidence, successRate, mode }: any) {
  return `When ${metric} drops more than ${threshold}%, ${mode === "auto" ? "automatically" : "with approval"} ${action === "launch_promo" ? "launch a promotion" : "notify the team"} if confidence is above ${Math.round(confidence*100)}% and success rate is above ${Math.round(successRate*100)}%.`;
}

  const [metric, setMetric] = useState("revenue");
  const [threshold, setThreshold] = useState(10);
  const [action, setAction] = useState("launch_promo");
  const [mode, setMode] = useState<"auto" | "approval">("approval");
  const [confidence, setConfidence] = useState(0.8);
  const [successRate, setSuccessRate] = useState(0.7);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  // Simulation state
  const [simulation, setSimulation] = useState(null);
  const [loadingSim, setLoadingSim] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    await fetch("/api/actions/auto-rule", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        metric,
        threshold,
        action_type: action,
        min_confidence: confidence,
        min_success_rate: successRate,
        mode
      })
    });
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  // Safety indicator logic
  let safety = "🟢 Safe to automate";
  if (mode === "auto" && (confidence < 0.7 || successRate < 0.6)) safety = "🟡 Requires approval";
  if (mode === "auto" && (confidence < 0.5 || successRate < 0.4)) safety = "🔴 High risk";

  // Simulation API call
  const runSimulation = useCallback(async () => {
    setLoadingSim(true);
    setSimulation(null);
    try {
      const res = await fetch("/api/actions/simulate-rule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          metric,
          condition: "drop",
          threshold,
          action_type: action
        })
      });
      const data = await res.json();
      setSimulation(data);
    } catch (e) {
      setSimulation(null);
    }
    setLoadingSim(false);
  }, [metric, threshold, action]);

  return (
    <div className="p-6 bg-white rounded-2xl shadow space-y-6">
      <h2 className="text-xl font-semibold">Create Automation Rule</h2>
      {/* IF */}
      <div>
        <p className="text-sm text-gray-500 mb-2">IF</p>
        <div className="flex gap-3 items-center">
          <span className="px-2 py-1 bg-blue-50 rounded text-blue-700 text-xs">{metric}</span>
          <select value={metric} onChange={e => setMetric(e.target.value)}>
            <option value="revenue">Revenue</option>
            <option value="sales">Sales</option>
          </select>
          <span>drops more than</span>
          <input type="number" value={threshold} onChange={e => setThreshold(Number(e.target.value))} className="w-20 border rounded px-2" />
          <span className="px-2 py-1 bg-yellow-50 rounded text-yellow-700 text-xs">{threshold}%</span>
          <span>%</span>
        </div>
      </div>
      {/* THEN */}
      <div>
        <p className="text-sm text-gray-500 mb-2">THEN</p>
        <select value={action} onChange={e => setAction(e.target.value)}>
          <option value="launch_promo">Launch Promotion</option>
          <option value="notify_team">Notify Team</option>
        </select>
        <span className="ml-2 px-2 py-1 bg-green-50 rounded text-green-700 text-xs">{action === "launch_promo" ? "Promotion" : "Notify"}</span>
      </div>
      {/* CONDITIONS */}
      <div>
        <p className="text-sm text-gray-500 mb-2">WHEN</p>
        <div className="space-y-2">
          <div>
            Confidence ≥ {confidence}
            <input type="range" min={0} max={1} step={0.05} value={confidence} onChange={e => setConfidence(Number(e.target.value))} />
          </div>
          <div>
            Success Rate ≥ {successRate}
            <input type="range" min={0} max={1} step={0.05} value={successRate} onChange={e => setSuccessRate(Number(e.target.value))} />
          </div>
        </div>
      </div>
      {/* MODE */}
      <div>
        <p className="text-sm text-gray-500 mb-2">MODE</p>
        <div className="flex gap-4">
          <button onClick={() => setMode("approval")} className={mode === "approval" ? "font-bold" : ""}>Approval</button>
          <button onClick={() => setMode("auto")} className={mode === "auto" ? "font-bold" : ""}>Auto</button>
        </div>
      </div>
      {/* PREVIEW & SAFETY */}
      <div className="p-3 bg-gray-50 rounded flex flex-col gap-2">
        <div className="text-sm text-gray-700 italic">{getPreview({ metric, threshold, action, confidence, successRate, mode })}</div>
        <div className="text-xs font-semibold">{safety}</div>
      </div>

      {/* SIMULATION MODE */}
      <div className="mt-4">
        <button onClick={runSimulation} className="text-sm text-blue-600" disabled={loadingSim}>
          {loadingSim ? "Running..." : "Run Simulation"}
        </button>
        {simulation && (
          <div className="p-4 bg-blue-50 rounded-xl border mt-4">
            <div className="font-semibold text-sm mb-2">
              🧠 VoxCore Simulation
            </div>
            <div className="text-sm text-gray-700 space-y-1">
              <div>Triggers: {simulation.triggers}</div>
              <div>Avg Impact: +{(simulation.avgImpact * 100).toFixed(1)}%</div>
              <div>Success Rate: {(simulation.successRate * 100).toFixed(0)}%</div>
            </div>
            <div className="mt-2 text-xs text-gray-500">
              ⚡ Estimated outcome: {simulation.avgImpact > 0 ? "Likely positive impact" : "Uncertain / risky"}
            </div>
            <div className="mt-2 text-xs">
              Confidence: {
                simulation.successRate > 0.8 ? "🟢 High" :
                simulation.successRate > 0.5 ? "🟡 Medium" :
                "🔴 Low"
              }
            </div>
          </div>
        )}
      </div>

      {/* SAVE */}
      <button onClick={handleSave} className="px-4 py-2 bg-black text-white rounded-lg" disabled={saving}>{saving ? "Saving..." : "Save Rule"}</button>
      {saved && <div className="text-green-600 text-sm mt-2">Rule saved!</div>}
    </div>
  );
}
