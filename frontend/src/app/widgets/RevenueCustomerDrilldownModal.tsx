import RankedRevenueDrilldownShell from "./RankedRevenueDrilldownShell";
import { createRankedDetailMapper } from "./rankedAnalyticsMappers";
import type { CustomerDetailResponse } from "./revenueByCustomerTypes";

const mapDetailResponse = createRankedDetailMapper<"customer">("customer", {
  accentClassName: "text-violet-300/80",
  headlineClassName: "text-violet-200",
  description: "Aggregate-first customer detail fetched from the governed analytics endpoint.",
  emptyMessage: "No bounded peer comparison data is available for this customer yet.",
  loadingLabel: "Customer detail loading",
  peerComparisonHint: "Bound aggregate comparison across top customer peers.",
  leaderLabel: "Leader",
  tableDimensionLabel: "Customer",
  detailBarFill: "#8b5cf6",
  detailSelectedFill: "#22c55e",
});

export default function RevenueCustomerDrilldownModal({
  customer,
  onClose,
}: {
  customer: string;
  onClose: () => void;
}) {
  return (
    <RankedRevenueDrilldownShell
      dimensionValue={customer}
      detailPathBuilder={(encodedCustomer) => `/api/v1/analytics/revenue-by-customer/${encodedCustomer}`}
      mapDetailResponse={
        mapDetailResponse as (
          response: CustomerDetailResponse,
          dimensionValue: string,
        ) => ReturnType<typeof mapDetailResponse>
      }
      initialCopy={{
        accentClassName: "text-violet-300/80",
        description: "Aggregate-first customer detail fetched from the governed analytics endpoint.",
        loadingLabel: "Customer detail loading",
      }}
      onClose={onClose}
    />
  );
}
