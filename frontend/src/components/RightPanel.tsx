import React, { useState, useEffect } from "react";

// (Optional) For future-proofing, import getSessionId if API calls are added here
// import { getSessionId } from "@/lib/session";

interface Insight {
  id: string;
  title: string;
  narrative: string;
  icon?: string;
  type?: string;
}

interface RightPanelProps {
  open: boolean;
  onClose: () => void;
}

export default function RightPanel({ open, onClose }: RightPanelProps) {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(false);

  // Lazy load insights when panel opens
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (open) {
      setLoading(true);
      fetch("/api/insights/latest")
        .then((res) => res.json())
        .then((data) => setInsights(data.insights || []))
        .finally(() => setLoading(false));
      // Auto-refresh every 60s
      interval = setInterval(() => {
        fetch("/api/insights/latest")
          .then((res) => res.json())
          .then((data) => setInsights(data.insights || []));
      }, 60000);
    }
    return () => interval && clearInterval(interval);
  }, [open]);

  return (
    <aside
      className={`right-panel fixed top-0 right-0 h-full w-96 bg-[var(--bg-elevated)] shadow-lg z-40 transition-transform duration-300 ease-in-out ${open ? "translate-x-0" : "translate-x-full"}`}
      style={{ borderLeft: "1px solid var(--border-default)" }}
      aria-label="Insights Panel"
    >
      <div className="flex items-center justify-between p-6 border-b border-[var(--border-default)]">
        <h2 className="text-lg font-bold text-[var(--accent-primary)]">Insights</h2>
        <button onClick={onClose} className="text-[var(--text-secondary)] hover:text-[var(--accent-primary)] transition-colors text-xl">×</button>
      </div>
      <div className="p-6 overflow-y-auto h-[calc(100%-64px)]">
        {loading ? (
          <div className="animate-pulse text-[var(--text-secondary)]">Loading insights...</div>
        ) : insights.length === 0 ? (
          <div className="text-[var(--text-secondary)]">No insights available.</div>
        ) : (
          insights.map((insight) => (
            <div key={insight.id} className="mb-6 p-4 bg-[var(--bg-surface)] rounded-xl shadow-sm hover:shadow-md transition-all">
              <div className="flex items-center gap-2 mb-2">
                {insight.icon && <span className="text-2xl">{insight.icon}</span>}
                <span className="font-semibold text-[var(--accent-primary)]">{insight.title}</span>
              </div>
              <div className="text-[var(--text-primary)] text-sm">{insight.narrative}</div>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}
