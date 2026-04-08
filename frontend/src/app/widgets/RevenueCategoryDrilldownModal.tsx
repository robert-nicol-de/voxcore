import RankedRevenueDrilldownShell from "./RankedRevenueDrilldownShell";
import { createRankedDetailMapper } from "./rankedAnalyticsMappers";
import type { CategoryDetailResponse } from "./revenueByCategoryTypes";

const mapDetailResponse = createRankedDetailMapper<"category">("category", {
  accentClassName: "text-amber-300/80",
  headlineClassName: "text-amber-200",
  description: "Aggregate-first category detail fetched from the governed analytics endpoint.",
  emptyMessage: "No bounded peer comparison data is available for this category yet.",
  loadingLabel: "Category detail loading",
  peerComparisonHint: "Bound aggregate comparison across top category peers.",
  leaderLabel: "Leader",
  tableDimensionLabel: "Category",
  detailBarFill: "#f59e0b",
  detailSelectedFill: "#fb7185",
});

export default function RevenueCategoryDrilldownModal({
  category,
  onClose,
}: {
  category: string;
  onClose: () => void;
}) {
  return (
    <RankedRevenueDrilldownShell
      dimensionValue={category}
      detailPathBuilder={(encodedCategory) => `/api/v1/analytics/revenue-by-category/${encodedCategory}`}
      mapDetailResponse={mapDetailResponse as (response: CategoryDetailResponse, dimensionValue: string) => ReturnType<typeof mapDetailResponse>}
      initialCopy={{
        accentClassName: "text-amber-300/80",
        description: "Aggregate-first category detail fetched from the governed analytics endpoint.",
        loadingLabel: "Category detail loading",
      }}
      onClose={onClose}
    />
  );
}
