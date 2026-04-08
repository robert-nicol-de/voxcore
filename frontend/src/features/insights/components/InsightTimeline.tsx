import React from "react";

export type TimelineEvent = {
  id: string;
  type: "insight" | "action" | "result" | "auto_action";
  title: string;
  description?: string;
  timestamp: string;
  impact?: number;
};

export function InsightTimeline({ events }: { events: TimelineEvent[] }) {
  return (
    <div className="border-l-2 border-gray-200 pl-6 space-y-6">
      {events.map((e, i) => (
        <div key={e.id} className="flex gap-4 items-start animate-fade-in">
          {/* ICON */}
          <div className={`mt-1 w-3 h-3 rounded-full transition-all duration-300 ${
            e.type === "insight"
              ? "bg-blue-500"
              : e.type === "action"
              ? "bg-gray-700"
              : e.type === "result"
              ? "bg-green-500"
              : "bg-purple-500 border-2 border-purple-300"
          }`} />

          {/* CONTENT */}
          <div>
            <div className={`font-medium ${e.type === "auto_action" ? "text-purple-700 font-bold" : ""}`}>
              {e.type === "auto_action" && "⚡ "}{e.title}
            </div>
            <div className="text-xs text-gray-500">
              {new Date(e.timestamp).toLocaleString()}
            </div>
            {e.type === "result" && e.impact !== undefined && (
              <div className="text-sm text-green-600 mt-1">
                📈 +{(e.impact * 100).toFixed(1)}% impact
              </div>
            )}
            {e.description && (
              <div className="text-xs text-gray-600 mt-1">{e.description}</div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
