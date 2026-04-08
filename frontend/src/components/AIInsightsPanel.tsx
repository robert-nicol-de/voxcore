import { useEffect, useState } from "react";
import Card from "@/components/ui/Card";
import SkeletonCard from "@/components/ui/skeletons/SkeletonCard";
import { getSessionId } from "@/lib/session";

export default function AIInsightsPanel() {
  const [insights, setInsights] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchInsights = async () => {
    const session_id = getSessionId();
    const res = await fetch(`/api/insights/latest?session_id=${session_id}`);
    const json = await res.json();
    setInsights(json.insights || []);
    setLoading(false);
  };

  useEffect(() => {
    fetchInsights();
    const interval = setInterval(fetchInsights, 60000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-full flex flex-col bg-[var(--bg-elevated)] px-6 py-6 border-l border-[var(--border-color)] shadow-lg">
      <h2 className="text-xl font-bold mb-4 tracking-tight text-[var(--accent-primary)]">AI Insights</h2>
      <div className="flex-1 overflow-y-auto custom-scrollbar pr-1">
        {loading ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : insights.length === 0 ? (
          <div className="text-sm text-[var(--text-secondary)] mt-8">
            No insights yet. Run queries to generate intelligence.
          </div>
        ) : (
          insights.map((i, idx) => (
            <div
              key={idx}
              className="mb-4 p-3 rounded-lg bg-[rgba(59,130,246,0.05)] border border-[rgba(59,130,246,0.15)] shadow-[0_2px_8px_rgba(59,130,246,0.08)] transition-all"
            >
              <div className="text-base font-medium mb-1 text-[var(--text-primary)]">{i.title || "Insight"}</div>
              <p className="text-sm text-[var(--text-secondary)] mb-1">{i.insight}</p>
              {i.suggestion && (
                <div className="text-xs text-[var(--accent-primary)] mt-1">
                  💡 {i.suggestion}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
