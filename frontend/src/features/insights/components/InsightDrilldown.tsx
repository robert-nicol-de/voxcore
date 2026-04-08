import { useEffect, useState } from "react";
import { Insight } from "../types/insight";
import { InsightChart } from "./InsightChart";
import { Tabs } from "./Tabs";
import { SuggestedActions } from "./SuggestedActions";

import { ImpactStory } from "./ImpactStory";
import { InsightTimeline, TimelineEvent } from "./InsightTimeline";


  insight: Insight & { chart?: any; data?: any[]; id?: string };
  onClose: () => void;
}) => {
  const [actions, setActions] = useState<any[]>([]);
  const [actionsLoading, setActionsLoading] = useState(false);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [timelineLoading, setTimelineLoading] = useState(false);
  const [impactStory, setImpactStory] = useState<string>("");

  useEffect(() => {
    if (!insight.id) return;
    setActionsLoading(true);
    fetch(`/api/insights/actions/${insight.id}`)
      .then(res => res.json())
      .then(data => setActions(data.actions || []))
      .catch(() => setActions([]))
      .finally(() => setActionsLoading(false));
    setTimelineLoading(true);
    fetch(`/api/insights/${insight.id}/timeline`)
      .then(res => res.json())
      .then(data => setTimeline(data || []))
      .catch(() => setTimeline([]))
      .finally(() => setTimelineLoading(false));
    // Fetch impact story
    fetch(`/api/insights/impact-story/${insight.id}`)
      .then(res => res.json())
      .then(data => setImpactStory(data.story || ""));
  }, [insight.id]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-2xl relative">
        <button className="absolute top-2 right-2 text-gray-500" onClick={onClose}>
          ✖
        </button>
        {impactStory && <ImpactStory story={impactStory} confidence={insight.confidence} tone="executive" />}
        <h2 className="text-xl font-bold mb-2">Insight Analysis</h2>
        <div className="mb-2 text-base font-semibold">{insight.insight}</div>
        <div className="mb-2 text-xs text-gray-500">Type: {insight.type} | Confidence: {insight.confidence.toFixed(2)}</div>
        <Tabs labels={["Overview", "Root Cause", "Suggested Actions 🔥", "Timeline 🧠"]}>
          {/* Overview Tab */}
          <div>
            {insight.chart && insight.data && (
              <div className="my-4">
                <InsightChart data={insight.data} config={insight.chart} />
              </div>
            )}
            <div className="mt-4 text-gray-600 italic">AI explanation, data table coming soon…</div>
          </div>
          {/* Root Cause Tab */}
          <div>
            <div className="text-gray-500">Root cause graph coming soon…</div>
          </div>
          {/* Suggested Actions Tab */}
          <div>
            {actionsLoading ? (
              <div className="text-gray-400">Loading actions…</div>
            ) : (
              <SuggestedActions actions={actions} insightId={insight.id} userId={"user_123"} />
            )}
          </div>
          {/* Timeline Tab */}
          <div>
            {timelineLoading ? (
              <div className="text-gray-400">Loading timeline…</div>
            ) : timeline.length === 0 ? (
              <div className="text-gray-400">No timeline events yet.</div>
            ) : (
              <InsightTimeline events={timeline} />
            )}
          </div>
        </Tabs>
      </div>
    </div>
  );
}

export const InsightDrilldown = InsightDrilldown;
