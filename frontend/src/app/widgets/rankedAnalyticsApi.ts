import { apiUrl } from "../../lib/api";

const getSessionId = () => localStorage.getItem("voxcore_session_id") || "";

const withSessionId = (path: string) => {
  const sessionId = getSessionId();
  if (!sessionId) {
    return path;
  }

  const params = new URLSearchParams();
  params.set("session_id", sessionId);
  const suffix = params.toString();

  return suffix ? `${path}?${suffix}` : path;
};

async function fetchRankedAnalyticsJson<T>(path: string, signal: AbortSignal): Promise<T> {
  const response = await fetch(apiUrl(path), { signal });
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as { detail?: string };
    throw new Error(body.detail || "Failed to load analytics");
  }
  return (await response.json()) as T;
}

export function fetchRankedAnalyticsAggregate<T>(aggregatePath: string, signal: AbortSignal) {
  return fetchRankedAnalyticsJson<T>(withSessionId(aggregatePath), signal);
}

export function fetchRankedAnalyticsDrilldown<T>(
  detailPathBuilder: (encodedDimension: string) => string,
  dimensionValue: string,
  signal: AbortSignal,
) {
  const path = detailPathBuilder(encodeURIComponent(dimensionValue));
  return fetchRankedAnalyticsJson<T>(withSessionId(path), signal);
}
