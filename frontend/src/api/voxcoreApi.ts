// VoxCore API Layer
// Complete integration with multi-tenant + policy engine
import { apiUrl } from "@/lib/api";

/**
 * Query request normalized from frontend
 */
export interface QueryRequest {
  text: string;
  sessionId?: string;
  environment?: "dev" | "staging" | "prod";
  source?: string;
  orgId?: string;
  userId?: string;
}

/**
 * Query response from backend (normalized)
 */
export interface QueryResult {
  id: string;
  fingerprint: string;
  status: "blocked" | "allowed" | "pending_approval";
  risk: number;
  confidence: number;
  reasons: string[];
  analysisTime: number;
  original: string;
  rewritten: string;
  policy?: string;
  policyViolations: string[];
  context: {
    user: string;
    environment: string;
    org: string;
  };
  query_context?: any;  // NEW: Structured context for UI display
}

/**
 * Send a query for analysis and execution
 * Includes org_id and user_id for multi-tenant support
 */
export const sendQuery = async (
  query: string,
  sessionId?: string,
  options?: Partial<QueryRequest>
): Promise<QueryResult> => {
  const orgId = options?.orgId || localStorage.getItem("voxcore_org_id") || "default-org";
  const userId = options?.userId || localStorage.getItem("voxcore_user_id") || "unknown";
  const environment = options?.environment || "dev";
  const source = options?.source || "playground";
  const apiKey = import.meta.env.VITE_API_KEY || "dev-key-local-testing";

  try {
    const res = await fetch(apiUrl("/api/v1/query"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
      },
      body: JSON.stringify({
        text: query,
        session_id: sessionId || localStorage.getItem("voxcore_session_id"),
        environment,
        source,
        org_id: orgId,
        user_id: userId,
      }),
    });

    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || "Query failed");
    }

    const data = await res.json();
    return normalizeResponse(data);
  } catch (error) {
    console.warn("Backend unavailable → falling back to demo mode", error);
    
    // 👉 Graceful fallback: use demo simulator instead of crashing
    const { runPlaygroundQuery } = await import("../playground/simulator");
    const simResult = runPlaygroundQuery(query);
    
    // Normalize simulator result to QueryResult format
    return {
      id: simResult.id || `demo-${Date.now()}`,
      fingerprint: "demo-mode",
      status: simResult.governanceMeta?.classification === "HIGH" ? "blocked" : "allowed",
      risk: simResult.governanceMeta?.score || 0,
      confidence: 0.95,
      reasons: simResult.governanceMeta?.warnings || [],
      analysisTime: 150,
      original: query,
      rewritten: query,
      policy: undefined,
      policyViolations: [],
      context: {
        user: userId,
        environment: "demo",
        org: orgId,
      },
      query_context: simResult.queryContext,
      mode: "demo",
      notice: "Live backend unavailable - running in demo mode",
    } as any;
  }
};

/**
 * Normalize backend response to frontend format
 * Maps backend field names → frontend field names
 */
function normalizeResponse(raw: any): QueryResult {
  return {
    id: raw.query_id,
    fingerprint: raw.fingerprint,
    status: raw.status,
    risk: raw.risk_score,
    confidence: raw.confidence,
    reasons: raw.reasons || [],
    analysisTime: raw.analysis_time_ms,
    original: raw.original_sql,
    rewritten: raw.rewritten_sql,
    policy: raw.policy_applied,
    policyViolations: raw.policy_violations || [],
    context: {
      user: raw.context?.user || "unknown",
      environment: raw.context?.environment || "dev",
      org: raw.context?.org_id || "default-org",
    },
    query_context: raw.query_context,  // NEW: Pass through structured context
  };
}

/**
 * Approve a pending query (admin only)
 */
export const approveQuery = async (
  queryId: string,
  approve: boolean,
  reason?: string
): Promise<{ status: string; approved: boolean }> => {
  const apiKey = import.meta.env.VITE_API_KEY || "dev-key-local-testing";

  try {
    const res = await fetch(
      apiUrl(`/api/playground/queries/${queryId}/approve`),
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": apiKey,
        },
        body: JSON.stringify({
          approve,
          reason: reason || (approve ? "Approved by admin" : "Rejected by admin"),
        }),
      }
    );

    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || "Approval failed");
    }

    return res.json();
  } catch (error) {
    console.error("Approval error:", error);
    throw error;
  }
};

/**
 * Store org/user context in localStorage for multi-tenant support
 */
export const setContext = (orgId: string, userId: string) => {
  localStorage.setItem("voxcore_org_id", orgId);
  localStorage.setItem("voxcore_user_id", userId);
};
