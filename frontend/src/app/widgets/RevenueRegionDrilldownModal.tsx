import RankedRevenueDrilldownShell from "./RankedRevenueDrilldownShell";
import { createRankedDetailMapper } from "./rankedAnalyticsMappers";
import type { RegionDetailResponse } from "./revenueByRegionTypes";

const mapDetailResponse = createRankedDetailMapper<"region">("region", {
  accentClassName: "text-sky-300/80",
  headlineClassName: "text-sky-200",
  description: "Aggregate-first regional detail fetched from the governed analytics endpoint.",
  emptyMessage: "No bounded peer comparison data is available for this region yet.",
  loadingLabel: "Region detail loading",
  peerComparisonHint: "Bound aggregate comparison across top regional peers.",
  leaderLabel: "Leader",
  tableDimensionLabel: "Region",
  detailBarFill: "#38bdf8",
  detailSelectedFill: "#22c55e",
});

export default function RevenueRegionDrilldownModal({
  region,
  onClose,
}: {
  region: string;
  onClose: () => void;
}) {
  return (
    <RankedRevenueDrilldownShell
      dimensionValue={region}
      detailPathBuilder={(encodedRegion) => `/api/v1/analytics/revenue-by-region/${encodedRegion}`}
      mapDetailResponse={mapDetailResponse as (response: RegionDetailResponse, dimensionValue: string) => ReturnType<typeof mapDetailResponse>}
      initialCopy={{
        accentClassName: "text-sky-300/80",
        description: "Aggregate-first regional detail fetched from the governed analytics endpoint.",
        loadingLabel: "Region detail loading",
      }}
      onClose={onClose}
    />
  );
}
