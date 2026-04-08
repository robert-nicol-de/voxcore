import { useState, useEffect } from "react";

  const [executed, setExecuted] = useState<{ [k: number]: boolean }>({});
  const [outcomes, setOutcomes] = useState<{ [k: number]: any }>({});
  const [learning, setLearning] = useState<{ [k: number]: any }>({});
  useEffect(() => {
    if (!insightId) return;
    fetch(`/api/actions/executions/${insightId}`)
      .then(res => res.json())
      .then(data => {
        const byAction: { [k: number]: any } = {};
        (data.executions || []).forEach((e: any) => {
          byAction[e.action_id] = e;
        });
        setOutcomes(byAction);
      });
    // Fetch learning for each action
    actions.forEach((a, i) => {
      fetch(`/api/actions/learning/${a.id || i}/${a.metric || 'revenue'}/${a.context || 'South region'}`)
        .then(res => res.json())
        .then(data => {
          setLearning(prev => ({ ...prev, [a.id || i]: data }));
        });
    });
  }, [insightId, executed, actions]);

  if (!actions || actions.length === 0) return <div className="text-gray-400">No suggested actions.</div>;
  const handleTakeAction = async (action: any, idx: number) => {
    if (!insightId || !userId) return;
    await fetch("/api/actions/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        insight_id: insightId,
        action_id: action.id || idx,
        user_id: userId
      })
    });
    setExecuted(prev => ({ ...prev, [idx]: true }));
  };
  return (
    <div className="space-y-4">
      {actions.map((a, i) => {
        const outcome = outcomes[a.id || i];
        const learn = learning[a.id || i];
        return (
          <div key={i} className="p-4 rounded-xl bg-gray-50 border">
            <div className="flex justify-between">
              <h3 className="font-semibold">{a.title}</h3>
              <span className={`text-sm ${a.priority === "high" ? "text-red-500" : a.priority === "medium" ? "text-yellow-600" : "text-green-600"}`}>{a.priority}</span>
            </div>
            {a.impact && <div className="text-xs text-blue-500">Impact: {a.impact}</div>}
            <p className="text-sm text-gray-600 mt-1">{a.description}</p>
            {learn && learn.success_rate !== undefined && (
              <div className="mt-2 text-xs text-green-600">
                🔥 Proven: {(learn.success_rate * 100).toFixed(0)}% success • Avg +{(learn.avg_impact * 100).toFixed(1)}%
              </div>
            )}
            <button
              className="mt-3 px-3 py-1 bg-black text-white rounded-lg text-sm"
              disabled={executed[i] || (outcome && outcome.status === "completed")}
              onClick={() => handleTakeAction(a, i)}
            >
              {executed[i] || (outcome && outcome.status === "completed") ? "Action Taken" : "Take Action"}
            </button>
            {outcome && outcome.status === "completed" && (
              <div className="mt-3 p-3 bg-green-50 rounded-xl text-sm">
                📈 Result: {outcome.metric} {outcome.impact > 0 ? "increased" : "decreased"} {Math.abs((outcome.impact * 100).toFixed(1))}% in {outcome.entity}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
