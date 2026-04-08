const configuredApiUrl = (import.meta.env.VITE_API_URL as string | undefined)?.trim();

const isLocalhostHost =
  window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";

const runtimeDefaultApiUrl = isLocalhostHost
  ? `http://${window.location.hostname}:8000`
  : window.location.origin;

const shouldIgnoreConfiguredLocalhost =
  !isLocalhostHost &&
  !!configuredApiUrl &&
  /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/i.test(configuredApiUrl);

const shouldIgnoreConfiguredPlaceholderDomain =
  !!configuredApiUrl &&
  /yourdomain\.com/i.test(configuredApiUrl);

const resolvedApiBase =
  shouldIgnoreConfiguredLocalhost || shouldIgnoreConfiguredPlaceholderDomain
    ? runtimeDefaultApiUrl
    : (configuredApiUrl || runtimeDefaultApiUrl);

export const API_BASE_URL = resolvedApiBase.replace(/\/+$/, "");

export const apiUrl = (path: string) => {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;

  // Avoid /api/api/... if VITE_API_URL already includes /api and caller passes /api/... paths.
  const normalizedBase = API_BASE_URL.toLowerCase();
  const dedupedPath =
    normalizedBase.endsWith("/api") && normalizedPath.toLowerCase().startsWith("/api/")
      ? normalizedPath.slice(4)
      : normalizedPath;

  return `${API_BASE_URL}${dedupedPath}`;
};

export const isApiNotFound = (response: Response | { status?: number } | null | undefined) => {
  return response?.status === 404;
};

/**
 * Backend contract - stable response shape
 */
export interface BackendQueryResponse {
  query_id: string;
  fingerprint: string;
  status: "blocked" | "allowed" | "pending_approval";
  risk_score: number;
  confidence: number;
  reasons: string[];
  analysis_time_ms: number;
  original_sql: string;
  rewritten_sql: string;
  execution: {
    rows_returned: number;
    execution_time_ms: number;
  };
  context: {
    user: string;
    environment: string;
    source: string;
  };
}

/**
 * Frontend normalized shape (matches QueryResult interface)
 */
export interface NormalizedQueryResult {
  id: string;
  fingerprint: string;
  status: "blocked" | "allowed" | "pending_approval";
  riskScore: number;
  confidence: number;
  reasons: string[];
  analysisTime: number;
  originalSql: string;
  rewrittenSql: string;
  execution: {
    rowsReturned: number;
    executionTimeMs: number;
  };
  context: {
    user: string;
    environment: string;
    source: string;
  };
}

/**
 * Normalize backend response to frontend shape
 */
function normalize(res: BackendQueryResponse): NormalizedQueryResult {
  return {
    id: res.query_id,
    fingerprint: res.fingerprint,
    status: res.status,
    riskScore: res.risk_score,
    confidence: res.confidence,
    reasons: res.reasons ?? [],
    analysisTime: res.analysis_time_ms,
    originalSql: res.original_sql,
    rewrittenSql: res.rewritten_sql,
    execution: {
      rowsReturned: res.execution.rows_returned,
      executionTimeMs: res.execution.execution_time_ms,
    },
    context: res.context,
  };
}

/**
 * Execute a query against VoxCore backend
 * Returns risk score, status, and analysis results
 */
export async function runQuery(
  text: string,
  options?: {
    sessionId?: string;
    environment?: string;
    source?: string;
    user?: string;
  }
): Promise<NormalizedQueryResult> {
  if (!text || text.trim().length === 0) {
    throw new Error("Query cannot be empty");
  }

  try {
    const apiKey = import.meta.env.VITE_API_KEY || "";
    const res = await fetch(apiUrl("/api/playground/query"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
      },
      body: JSON.stringify({
        text: text.trim(),
        session_id: options?.sessionId || "default",
        environment: options?.environment || "dev",
        source: options?.source || "playground",
        user: options?.user || "ai-agent",
      }),
    });

    if (!res.ok) {
      const errorText = await res.text();
      if (res.status === 403) {
        throw new Error("Invalid API key. Check your configuration.");
      }
      throw new Error(`Query execution failed: ${res.status} - ${errorText}`);
    }

    const data: BackendQueryResponse = await res.json();
    return normalize(data);
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("Unknown error occurred during query execution");
  }
}