import { useQueryStore } from "../store/queryStore";

/**
 * Hook for accessing query execution functionality
 * Provides clean interface to store with memoization
 */
export function useQueryExecution() {
  return useQueryStore((state) => ({
    // State
    query: state.query,
    status: state.status,
    result: state.result,
    error: state.error,
    auditLogs: state.auditLogs,
    sessionId: state.sessionId,
    currentUser: state.currentUser,
    currentEnvironment: state.currentEnvironment,
    currentSource: state.currentSource,
    pendingApprovals: state.pendingApprovals,

    // Actions
    setQuery: state.setQuery,
    run: state.run,
    approve: state.approve,
    reset: state.reset,
    clearAuditLogs: state.clearAuditLogs,
    setContext: state.setContext,
    setEnvironment: state.setEnvironment,
    setSource: state.setSource,
    hydrateAuditLogs: state.hydrateAuditLogs,

    // Derived state
    isLoading: state.status === "analyzing",
    isDone: state.status === "done",
    isError: state.status === "error",
    riskScore: state.riskScore ?? null,
    confidence: state.confidence ?? null,
    analysisTime: state.analysisTime ?? null,
    reasons: state.reasons ?? [],
    rewrittenQuery: state.rewrittenQuery ?? null,
    isBlocked: state.isBlocked,
    isPendingApproval: state.isPendingApproval,
    queryHash: state.queryHash ?? null,
  }));
}

/**
 * Hook for accessing only audit logs
 */
export function useAuditLog() {
  return useQueryStore((state) => ({
    logs: state.auditLogs,
    clear: state.clearAuditLogs,
  }));
}
