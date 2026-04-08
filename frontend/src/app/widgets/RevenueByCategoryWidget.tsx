import RankedRevenueAnalyticsWidgetShell from "./RankedRevenueAnalyticsWidgetShell";
import RevenueCategoryDrilldownModal from "./RevenueCategoryDrilldownModal";
import { createRankedAggregateMapper } from "./rankedAnalyticsMappers";
import type { CategoryRevenueResponse } from "./revenueByCategoryTypes";

const BAR_COLORS = ["#f59e0b", "#f97316", "#fbbf24", "#fb7185", "#eab308", "#fdba74"];

const mapAggregateResponse = createRankedAggregateMapper<"category">("category", {
  widgetTestId: "revenue-by-category-widget",
  eyebrowClassName: "text-amber-300/80",
  headlineClassName: "text-amber-200",
  governanceBadgeClassName: "border-amber-400/20 bg-amber-400/10 text-amber-100",
  summaryTones: [
    "from-amber-500/20 to-orange-500/5",
    "from-orange-500/20 to-amber-500/5",
    "from-rose-500/20 to-amber-500/5",
  ],
  topDimensionLabel: "Top Category",
  coverageLabel: "Categories Covered",
  chartTitle: "Revenue Distribution",
  chartHint: "Click a bar to inspect governed category detail.",
  tableTitle: "Category Revenue Table",
  tableHint: "Sortable, governed aggregate results",
});

export default function RevenueByCategoryWidget() {
  return (
    <RankedRevenueAnalyticsWidgetShell
      aggregatePath="/api/v1/analytics/revenue-by-category"
      mapAggregateResponse={mapAggregateResponse as (response: CategoryRevenueResponse) => ReturnType<typeof mapAggregateResponse>}
      chartPalette={BAR_COLORS}
      rowTestIdPrefix="category-row"
      dimensionColumnLabel="Category"
      renderDrilldownModal={(selectedCategory, onClose) => (
        <RevenueCategoryDrilldownModal category={selectedCategory} onClose={onClose} />
      )}
    />
  );
}
