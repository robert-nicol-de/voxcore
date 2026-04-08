import RankedRevenueAnalyticsWidgetShell from "./RankedRevenueAnalyticsWidgetShell";
import RevenueProductDrilldownModal from "./RevenueProductDrilldownModal";
import { createRankedAggregateMapper } from "./rankedAnalyticsMappers";
import type { ProductRevenueResponse } from "./revenueByProductTypes";

const BAR_COLORS = ["#34d399", "#10b981", "#f59e0b", "#f97316", "#14b8a6", "#84cc16"];

const mapAggregateResponse = createRankedAggregateMapper<"product">("product", {
  widgetTestId: "revenue-by-product-widget",
  eyebrowClassName: "text-emerald-300/80",
  headlineClassName: "text-emerald-200",
  governanceBadgeClassName: "border-emerald-400/20 bg-emerald-400/10 text-emerald-100",
  summaryTones: [
    "from-emerald-500/20 to-teal-500/5",
    "from-lime-500/20 to-emerald-500/5",
    "from-amber-500/20 to-emerald-500/5",
  ],
  topDimensionLabel: "Top Product",
  coverageLabel: "Products Covered",
  chartTitle: "Revenue Distribution",
  chartHint: "Click a bar to inspect governed product detail.",
  tableTitle: "Product Revenue Table",
  tableHint: "Sortable, governed aggregate results",
});

export default function RevenueByProductWidget() {
  return (
    <RankedRevenueAnalyticsWidgetShell
      aggregatePath="/api/v1/analytics/revenue-by-product"
      mapAggregateResponse={mapAggregateResponse as (response: ProductRevenueResponse) => ReturnType<typeof mapAggregateResponse>}
      chartPalette={BAR_COLORS}
      rowTestIdPrefix="product-row"
      dimensionColumnLabel="Product"
      renderDrilldownModal={(selectedProduct, onClose) => (
        <RevenueProductDrilldownModal product={selectedProduct} onClose={onClose} />
      )}
    />
  );
}
