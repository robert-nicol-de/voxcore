import { useEffect, useState } from "react";
import { AutoActionMetrics, Metrics } from "./components/AutoActionMetrics";

export function AutoActionMetricsPanel() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  useEffect(() => {
    fetch("/api/actions/auto-metrics")
      .then(res => res.json())
      .then(setMetrics);
  }, []);
  if (!metrics) return null;
  return <AutoActionMetrics metrics={metrics} />;
}
