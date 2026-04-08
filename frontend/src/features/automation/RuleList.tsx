import React from "react";

export function RuleList({ rules }: { rules: any[] }) {
  if (!rules || rules.length === 0) return <div className="text-gray-400">No rules yet.</div>;
  return (
    <div className="space-y-3">
      {rules.map(r => (
        <div key={r.id || r.metric + r.action_type + r.mode} className="p-3 border rounded-lg flex flex-col gap-1">
          <div className="font-medium flex items-center gap-2">
            {r.action_type === "launch_promo" ? "🚀 Launch Promotion" : "🔔 Notify Team"}
            <span className="text-xs px-2 py-0.5 rounded bg-blue-50 text-blue-700">{r.metric}</span>
            <span className="text-xs px-2 py-0.5 rounded bg-yellow-50 text-yellow-700">{r.threshold}%</span>
            <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-700">{r.mode === "auto" ? "Auto" : "Approval"}</span>
          </div>
          <div className="text-sm text-gray-500">
            Confidence ≥ {Math.round((r.min_confidence || 0) * 100)}%, Success Rate ≥ {Math.round((r.min_success_rate || 0) * 100)}%
          </div>
        </div>
      ))}
    </div>
  );
}
