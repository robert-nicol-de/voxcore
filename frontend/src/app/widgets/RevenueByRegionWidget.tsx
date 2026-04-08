import RankedRevenueAnalyticsWidgetShell from "./RankedRevenueAnalyticsWidgetShell";
import RevenueRegionDrilldownModal from "./RevenueRegionDrilldownModal";
import { createRankedAggregateMapper } from "./rankedAnalyticsMappers";
import type { RevenueResponse } from "./revenueByRegionTypes";

const BAR_COLORS = ["#60a5fa", "#38bdf8", "#22d3ee", "#0ea5e9", "#2563eb", "#0284c7"];

const mapAggregateResponse = createRankedAggregateMapper<"region">("region", {
  widgetTestId: "revenue-by-region-widget",
  eyebrowClassName: "text-sky-300/80",
  headlineClassName: "text-sky-200",
  governanceBadgeClassName: "border-sky-400/20 bg-sky-400/10 text-sky-100",
  summaryTones: [
    "from-sky-500/20 to-blue-500/5",
    "from-cyan-500/20 to-sky-500/5",
    "from-emerald-500/20 to-sky-500/5",
  ],
  topDimensionLabel: "Top Region",
  coverageLabel: "Regions Covered",
  chartTitle: "Revenue Distribution",
  chartHint: "Click a bar to inspect governed regional detail.",
  tableTitle: "Regional Revenue Table",
  tableHint: "Sortable, governed aggregate results",
});

export default function RevenueByRegionWidget() {
  return (
    <RankedRevenueAnalyticsWidgetShell
      aggregatePath="/api/v1/analytics/revenue-by-region"
      mapAggregateResponse={mapAggregateResponse as (response: RevenueResponse) => ReturnType<typeof mapAggregateResponse>}
      chartPalette={BAR_COLORS}
      rowTestIdPrefix="region-row"
      dimensionColumnLabel="Region"
      renderDrilldownModal={(selectedRegion, onClose) => (
        <RevenueRegionDrilldownModal region={selectedRegion} onClose={onClose} />
      )}
    />
  );
}
