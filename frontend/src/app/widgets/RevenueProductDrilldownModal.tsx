import RankedRevenueDrilldownShell from "./RankedRevenueDrilldownShell";
import { createRankedDetailMapper } from "./rankedAnalyticsMappers";
import type { ProductDetailResponse } from "./revenueByProductTypes";

const mapDetailResponse = createRankedDetailMapper<"product">("product", {
  accentClassName: "text-emerald-300/80",
  headlineClassName: "text-emerald-200",
  description: "Aggregate-first product detail fetched from the governed analytics endpoint.",
  emptyMessage: "No bounded peer comparison data is available for this product yet.",
  loadingLabel: "Product detail loading",
  peerComparisonHint: "Bound aggregate comparison across top product peers.",
  leaderLabel: "Leader",
  tableDimensionLabel: "Product",
  detailBarFill: "#34d399",
  detailSelectedFill: "#f59e0b",
});

export default function RevenueProductDrilldownModal({
  product,
  onClose,
}: {
  product: string;
  onClose: () => void;
}) {
  return (
    <RankedRevenueDrilldownShell
      dimensionValue={product}
      detailPathBuilder={(encodedProduct) => `/api/v1/analytics/revenue-by-product/${encodedProduct}`}
      mapDetailResponse={mapDetailResponse as (response: ProductDetailResponse, dimensionValue: string) => ReturnType<typeof mapDetailResponse>}
      initialCopy={{
        accentClassName: "text-emerald-300/80",
        description: "Aggregate-first product detail fetched from the governed analytics endpoint.",
        loadingLabel: "Product detail loading",
      }}
      onClose={onClose}
    />
  );
}
