import { Insight } from "../types/insight";

// Utility to fetch the latest outcome for each insight
export async function fetchInsightsWithOutcomes(insights: Insight[]): Promise<(Insight & { latestOutcome?: { impact: number } })[]> {
  // For each insight, fetch executions and attach the latest completed outcome
  return Promise.all(
    insights.map(async (insight) => {
      const res = await fetch(`/api/actions/executions/${insight.id || insight.insight}`);
      const data = await res.json();
      const completed = (data.executions || []).filter((e: any) => e.status === "completed");
      if (completed.length > 0) {
        // Use the most recent completed execution
        const latest = completed.sort((a: any, b: any) => (b.evaluated_at || "").localeCompare(a.evaluated_at || ""))[0];
        return { ...insight, latestOutcome: { impact: latest.impact } };
      }
      return insight;
    })
  );
}
