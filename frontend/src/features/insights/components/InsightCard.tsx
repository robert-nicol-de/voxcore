import { Insight } from "../types/insight";
import { InsightChart } from "./InsightChart";
// Outcome badge logic
function getImpactBadge(impact: number | undefined) {
  if (impact === undefined) return null;
  if (impact > 0.1) return <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full ml-2">🟢 High Impact</span>;
  if (impact > 0) return <span className="text-xs px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full ml-2">🟡 Moderate</span>;
  if (impact < 0) return <span className="text-xs px-2 py-1 bg-red-100 text-red-700 rounded-full ml-2">🔴 Negative</span>;
  return null;
}

const getPriority = (confidence: number) => {
  if (confidence > 0.9) return "high";
  if (confidence > 0.7) return "medium";
  return "low";
};

const priorityStyles = {
  high: "border-red-600 shadow-lg scale-105 bg-red-50 animate-glow",
  medium: "border-yellow-400 bg-yellow-50",
  low: "border-green-400 bg-green-50 opacity-80",
};

const priorityLabel = {
  high: "🔴 High",
  medium: "🟡 Medium",
  low: "🟢 Low",
};

export const InsightCard = ({ insight, onDrilldown }: {
  insight: Insight & { chart?: any; data?: any[]; latestOutcome?: { impact: number } };
  onDrilldown?: (insight: Insight) => void;
}) => {
  const priority = getPriority(insight.confidence);
  const outcome = insight.latestOutcome;
  return (
    <div
      className={`border-2 rounded-lg p-4 mb-2 transition-all cursor-pointer ${priorityStyles[priority]}`}
      onClick={() => onDrilldown?.(insight)}
    >
      <div className="flex gap-2 mb-1">
        {insight.sentToSlack && (
          <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full">📤 Sent to Slack</span>
        )}
      </div>
      <div className="flex items-center gap-2 mb-2">
        <span className="text-lg font-bold">{priorityLabel[priority]}</span>
        {getImpactBadge(outcome?.impact)}
      </div>
      <div className="text-base font-semibold mb-1">{insight.insight}</div>
      <div className="text-xs text-gray-500 mb-2">Type: {insight.type} | Confidence: {insight.confidence.toFixed(2)}</div>
      {/* Chart rendering if present */}
      {insight.chart && insight.data && (
        <div className="my-2">
          <InsightChart data={insight.data} config={insight.chart} />
        </div>
      )}
      {outcome && (
        <div className="mt-2 text-sm bg-green-50 p-2 rounded-lg">
          📈 +{(outcome.impact * 100).toFixed(1)}% improvement
        </div>
      )}
      <div className="flex gap-2 mt-2">
        <button className="px-3 py-1 bg-blue-600 text-white rounded text-xs" onClick={e => { e.stopPropagation(); onDrilldown?.(insight); }}>Drill Down</button>
        <button className="px-3 py-1 bg-gray-200 text-gray-800 rounded text-xs" onClick={e => e.stopPropagation()}>View Data</button>
      </div>
    </div>
  );
};
