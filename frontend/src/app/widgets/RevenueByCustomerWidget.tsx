import RankedRevenueAnalyticsWidgetShell from "./RankedRevenueAnalyticsWidgetShell";
import RevenueCustomerDrilldownModal from "./RevenueCustomerDrilldownModal";
import { createRankedAggregateMapper } from "./rankedAnalyticsMappers";
import type { CustomerRevenueResponse } from "./revenueByCustomerTypes";

const BAR_COLORS = ["#a78bfa", "#8b5cf6", "#c084fc", "#7c3aed", "#d8b4fe", "#6366f1"];

const mapAggregateResponse = createRankedAggregateMapper<"customer">("customer", {
  widgetTestId: "revenue-by-customer-widget",
  eyebrowClassName: "text-violet-300/80",
  headlineClassName: "text-violet-200",
  governanceBadgeClassName: "border-violet-400/20 bg-violet-400/10 text-violet-100",
  summaryTones: [
    "from-violet-500/20 to-indigo-500/5",
    "from-fuchsia-500/20 to-violet-500/5",
    "from-sky-500/20 to-violet-500/5",
  ],
  topDimensionLabel: "Top Customer",
  coverageLabel: "Customers Covered",
  chartTitle: "Revenue Distribution",
  chartHint: "Click a bar to inspect governed customer detail.",
  tableTitle: "Customer Revenue Table",
  tableHint: "Sortable, governed aggregate results",
});

export default function RevenueByCustomerWidget() {
  return (
    <RankedRevenueAnalyticsWidgetShell
      aggregatePath="/api/v1/analytics/revenue-by-customer"
      mapAggregateResponse={
        mapAggregateResponse as (response: CustomerRevenueResponse) => ReturnType<typeof mapAggregateResponse>
      }
      chartPalette={BAR_COLORS}
      rowTestIdPrefix="customer-row"
      dimensionColumnLabel="Customer"
      renderDrilldownModal={(selectedCustomer, onClose) => (
        <RevenueCustomerDrilldownModal customer={selectedCustomer} onClose={onClose} />
      )}
    />
  );
}
