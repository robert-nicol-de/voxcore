import RevenueAnomalyDrilldownShell from "./RevenueAnomalyDrilldownShell";
import type { RevenueAnomalyDetailResponse } from "./revenueAnomalyTypes";
import type { RevenueAnomalyDrilldownViewModel } from "./revenueAnomalyViewModels";

const mapDetailResponse = (response: RevenueAnomalyDetailResponse): RevenueAnomalyDrilldownViewModel => ({
  entity: response.entity,
  accentClassName: "text-violet-300/80",
  headlineClassName: "text-violet-200",
  description: "Aggregate-first anomaly detail fetched from the governed analytics endpoint.",
  emptyMessage: "No bounded anomaly timeline data is available for this entity yet.",
  loadingLabel: "Anomaly detail loading",
  chartTitle: "Anomaly Timeline",
  chartHint: "Bounded timeline comparing actual and expected revenue.",
  detailBarFill: "#8b5cf6",
  expectedBarFill: "#38bdf8",
  summary: response.summary,
  timeline: response.timeline,
  insight_summary: response.insight_summary,
  governance: response.governance,
  response_meta: response.response_meta,
});

export default function RevenueAnomalyDrilldownModal({
  entity,
  onClose,
}: {
  entity: string;
  onClose: () => void;
}) {
  return (
    <RevenueAnomalyDrilldownShell
      entity={entity}
      detailPathBuilder={(encodedEntity) => `/api/v1/analytics/revenue-anomalies/${encodedEntity}`}
      mapDetailResponse={mapDetailResponse}
      initialCopy={{
        accentClassName: "text-violet-300/80",
        description: "Aggregate-first anomaly detail fetched from the governed analytics endpoint.",
        loadingLabel: "Anomaly detail loading",
      }}
      onClose={onClose}
    />
  );
}
