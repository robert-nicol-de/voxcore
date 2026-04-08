import RevenueAnomaliesWidgetShell from "./RevenueAnomaliesWidgetShell";
import RevenueAnomalyDrilldownModal from "./RevenueAnomalyDrilldownModal";
import type { RevenueAnomaliesResponse } from "./revenueAnomalyTypes";
import type { RevenueAnomalyAggregateViewModel } from "./revenueAnomalyViewModels";

const BAR_COLORS = ["#fb7185", "#f97316", "#f59e0b", "#ef4444", "#f43f5e", "#fda4af"];

const mapAggregateResponse = (response: RevenueAnomaliesResponse): RevenueAnomalyAggregateViewModel => ({
  widgetTestId: "revenue-anomalies-widget",
  eyebrowClassName: "text-rose-300/80",
  headlineClassName: "text-rose-200",
  governanceBadgeClassName: "border-rose-400/20 bg-rose-400/10 text-rose-100",
  summaryTones: [
    "from-rose-500/20 to-orange-500/5",
    "from-orange-500/20 to-red-500/5",
    "from-amber-500/20 to-rose-500/5",
  ],
  title: response.summary_card.title,
  narrative: response.insight_summary.narrative,
  chartTitle: "Anomaly Deviation",
  chartHint: "Click a bar to inspect governed anomaly detail.",
  tableTitle: "Revenue Anomaly Table",
  tableHint: "Sortable, governed anomaly signals",
  summary_card: response.summary_card,
  insight_summary: response.insight_summary,
  governance: response.governance,
  data: response.data,
});

export default function RevenueAnomaliesWidget() {
  return (
    <RevenueAnomaliesWidgetShell
      aggregatePath="/api/v1/analytics/revenue-anomalies"
      mapAggregateResponse={mapAggregateResponse}
      chartPalette={BAR_COLORS}
      rowTestIdPrefix="anomaly-row"
      renderDrilldownModal={(entity, onClose) => (
        <RevenueAnomalyDrilldownModal entity={entity} onClose={onClose} />
      )}
    />
  );
}
