import React, { useEffect, useState } from "react";
import { useInsights } from "./hooks/useInsights";
import { fetchInsightsWithOutcomes } from "./hooks/useInsightOutcomes";
import { InsightsHeader } from "./components/InsightsHeader";
import { AlertsBanner } from "./components/AlertsBanner";
import { InsightCard } from "./components/InsightCard";
import { InsightDrilldown } from "./components/InsightDrilldown";
import { ImpactSummary } from "./components/ImpactSummary";
import { AutoActionMetricsPanel } from "./components/AutoActionMetricsPanel";
import { Insight } from "./types/insight";

const Loader = () => (
  <div className="space-y-2">
    {[...Array(3)].map((_, i) => (
      <div key={i} className="h-20 bg-gray-100 animate-pulse rounded" />
    ))}
  </div>
);

const ErrorState = ({ error }: { error: string }) => (
  <div className="text-red-600 font-bold p-4">❌ {error}</div>
);

const EmptyState = () => (
  <div className="text-gray-400 text-center p-8">No insights yet — run a query to generate intelligence.</div>
);

export default function InsightsPage() {
  const { data, loading, error, refresh } = useInsights();
  const [drilldown, setDrilldown] = useState<Insight | null>(null);
  const [insightsWithOutcomes, setInsightsWithOutcomes] = useState<any[]>([]);

  useEffect(() => {
    if (data?.insights) {
      fetchInsightsWithOutcomes(data.insights).then(setInsightsWithOutcomes);
    }
  }, [data]);

  if (loading) return <Loader />;
  if (error || !data) return <ErrorState error={error || "Failed to load insights"} />;

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 space-y-6">
      <AutoActionMetricsPanel />
      <ImpactSummary />
      <InsightsHeader personalized={!!data.personalization} />
      <div className="flex items-center gap-4 mb-2">
        {/* Controls: TimeRangePicker, FilterDropdown, RefreshButton (stubs) */}
        <input type="date" className="border rounded px-2 py-1" />
        <select className="border rounded px-2 py-1">
          <option>All Types</option>
          <option>Anomaly</option>
          <option>Trend</option>
        </select>
        <button className="px-3 py-1 bg-blue-600 text-white rounded" onClick={refresh}>Refresh</button>
      </div>
      {data.alerts?.length > 0 && <AlertsBanner alerts={data.alerts} />}
      <div className="grid gap-4">
        {insightsWithOutcomes.length === 0 ? (
          <EmptyState />
        ) : (
          insightsWithOutcomes.map((insight, i) => (
            <InsightCard key={i} insight={insight} onDrilldown={setDrilldown} />
          ))
        )}
      </div>
      {/* DrilldownPanel (side modal) */}
      {drilldown && (
        <InsightDrilldown insight={drilldown} onClose={() => setDrilldown(null)} />
      )}
    </div>
  );
}
