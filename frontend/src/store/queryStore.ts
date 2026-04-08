import { create } from "zustand";
import { runQuery } from "../lib/api";

/**
 * Generate a simple hash for query fingerprinting
 */
function generateHash(query: string): string {
  let hash = 0;
  for (let i = 0; i < query.length; i++) {
    const char = query.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return "0x" + Math.abs(hash).toString(16).toUpperCase().padStart(8, "0");
}

export interface AuditLog {
  id: string;
  query: string;
  riskScore: number;
  status: "blocked" | "allowed" | "pending_approval" | "analyzed";
  timestamp: string;
  error?: string;
  
  // Execution context
  user: string;
  source: "playground" | "api" | "dashboard";
  environment: "dev" | "staging" | "prod";
  
  // Query metadata
  hash: string;
  executionTimeMs: number;
}

export interface QueryResult {
  fingerprint: string;
  hash: string;
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

export type QueryStatus = "idle" | "analyzing" | "done" | "error";

interface QueryState {
  // Current query state
  query: string;
  status: QueryStatus;
  result: QueryResult | null;
  error: string | null;
  riskScore: number | null;
  isBlocked: boolean;
  isPendingApproval: boolean;
  confidence: number | null;
  analysisTime: number | null;
  reasons: string[];
  rewrittenQuery: string | null;
  queryHash: string | null;

  // Audit logs
  auditLogs: AuditLog[];
  sessionId: string;
  
  // Execution context
  currentUser: string;
  currentEnvironment: "dev" | "staging" | "prod";
  currentSource: "playground" | "api" | "dashboard";
  
  // Approval queue
  pendingApprovals: Map<string, QueryResult>;

  // Actions
  setQuery: (query: string) => void;
  run: (query: string) => Promise<void>;
  approve: (queryHash: string) => Promise<void>;
  reset: () => void;
  clearAuditLogs: () => void;
  setContext: (user: string, environment: "dev" | "staging" | "prod", source: "playground" | "api" | "dashboard") => void;
  setEnvironment: (env: "dev" | "staging" | "prod") => void;
  setSource: (source: "playground" | "api" | "dashboard") => void;
  hydrateAuditLogs: (orgId: string) => Promise<void>;
}

const DESTRUCTIVE_KEYWORDS = ["drop", "truncate", "delete from", "alter table"];
const DEMO_MODE = true;

export const useQueryStore = create<QueryState>((set, get) => ({
  // Initial state
  query: "",
  status: "idle",
  result: null,
  error: null,
  riskScore: null,
  isBlocked: false,
  isPendingApproval: false,
  confidence: null,
  analysisTime: null,
  reasons: [],
  rewrittenQuery: null,
  queryHash: null,
  auditLogs: [],
  sessionId: localStorage.getItem("voxcore_session_id") || "demo-session",
  currentUser: "ai-agent",
  currentEnvironment: "dev",
  currentSource: "playground",
  pendingApprovals: new Map(),

  // Set execution context
  setContext: (user: string, environment: "dev" | "staging" | "prod", source: "playground" | "api" | "dashboard") => {
    set({ currentUser: user, currentEnvironment: environment, currentSource: source });
  },

  // Set environment
  setEnvironment: (env: "dev" | "staging" | "prod") => {
    set({ currentEnvironment: env });
  },

  // Set source
  setSource: (source: "playground" | "api" | "dashboard") => {
    set({ currentSource: source });
  },

  // Update query without running
  setQuery: (query: string) => {
    set({ query, error: null });
  },

  // Execute query with safety checks
  run: async (query: string) => {
    const state = get();

    // Reset state
    set({ status: "analyzing", query, error: null, result: null });

    // Frontend safety check
    const lowerQuery = query.toLowerCase();
    for (const keyword of DESTRUCTIVE_KEYWORDS) {
      if (lowerQuery.includes(keyword)) {
        const error = "❌ Destructive queries are not allowed. Use SELECT statements only.";
        set({
          status: "error",
          error,
        });

        // Log to audit
        const queryHash = generateHash(query);
        set((s) => ({
          auditLogs: [
            {
              id: Date.now().toString(),
              query,
              riskScore: 100,
              status: "blocked",
              timestamp: new Date().toISOString(),
              error,
              user: state.currentUser,
              source: state.currentSource,
              environment: state.currentEnvironment,
              hash: queryHash,
              executionTimeMs: 0,
            },
            ...s.auditLogs,
          ].slice(0, 50),
        }));

        return;
      }
    }

    // Simulate backend thinking time
    await new Promise((resolve) => setTimeout(resolve, DEMO_MODE ? 300 : 100));

    try {
      // Execute query
      const response = await runQuery(query, {
        sessionId: state.sessionId,
        user: state.currentUser,
        environment: state.currentEnvironment,
        source: state.currentSource,
      });

      const riskScore = response.riskScore;
      const isBlocked = response.status === "blocked";
      const isPendingApproval = response.status === "pending_approval";
      const queryHash = generateHash(query);

      // Build result object
      const result: QueryResult = {
        fingerprint: response.fingerprint,
        hash: queryHash,
        status: response.status,
        riskScore,
        confidence: response.confidence,
        reasons: response.reasons,
        analysisTime: response.analysisTime,
        originalSql: response.originalSql,
        rewrittenSql: response.rewrittenSql,
        execution: response.execution,
        context: response.context,
      };

      set({
        status: "done",
        result,
        riskScore,
        isBlocked,
        isPendingApproval,
        confidence: response.confidence,
        analysisTime: response.analysisTime,
        reasons: response.reasons,
        rewrittenQuery: response.rewrittenSql !== response.originalSql ? response.rewrittenSql : null,
        queryHash,
      });

      // Add to audit log
      const auditEntry: AuditLog = {
        id: response.id,
        query,
        riskScore,
        status: response.status,
        timestamp: new Date().toISOString(),
        user: state.currentUser,
        source: state.currentSource,
        environment: state.currentEnvironment,
        hash: queryHash,
        executionTimeMs: response.analysisTime,
      };

      set((s) => ({
        auditLogs: [auditEntry, ...s.auditLogs].slice(0, 50),
      }));

      // Add to pending approvals if needed
      if (isPendingApproval) {
        set((s) => {
          const newMap = new Map(s.pendingApprovals);
          newMap.set(queryHash, result);
          return { pendingApprovals: newMap };
        });
      }
    } catch (e: any) {
      const errorMsg = e?.message || "Query execution failed";

      set({
        status: "error",
        error: errorMsg,
      });

      // Log error to audit
      const queryHash = generateHash(query);
      set((s) => ({
        auditLogs: [
          {
            id: Date.now().toString(),
            query,
            riskScore: 0,
            status: "blocked",
            timestamp: new Date().toISOString(),
            error: errorMsg,
            user: state.currentUser,
            source: state.currentSource,
            environment: state.currentEnvironment,
            hash: queryHash,
            executionTimeMs: 0,
          },
          ...s.auditLogs,
        ].slice(0, 50),
      }));
    }
  },

  // Approve a pending query
  approve: async (queryHash: string) => {
    const state = get();
    const query = state.pendingApprovals.get(queryHash);
    
    if (!query) return;

    // Remove from pending
    set((s) => {
      const newMap = new Map(s.pendingApprovals);
      newMap.delete(queryHash);
      return { pendingApprovals: newMap };
    });

    // Update audit log status
    set((s) => ({
      auditLogs: s.auditLogs.map((log) =>
        log.hash === queryHash ? { ...log, status: "allowed" as const } : log
      ),
    }));
  },

  // Reset to initial state
  reset: () => {
    set({
      query: "",
      status: "idle",
      result: null,
      error: null,
    });
  },

  // Clear audit log
  clearAuditLogs: () => {
    set({ auditLogs: [] });
  },

  // Hydrate audit logs from backend persistence layer
  hydrateAuditLogs: async (orgId: string) => {
    try {
      const response = await fetch(
        `/api/queries/recent?org_id=${encodeURIComponent(orgId)}&limit=50`,
        {
          headers: {
            "x-api-key": import.meta.env.VITE_API_KEY || "",
          },
        }
      );

      if (!response.ok) {
        console.warn("Failed to hydrate audit logs:", response.statusText);
        return;
      }

      const logs = await response.json();

      // Convert backend format to frontend format
      const auditLogs: AuditLog[] = logs.map((log: any) => ({
        id: log.query_id,
        query: log.sql,
        riskScore: log.risk_score,
        status: log.status,
        timestamp: log.created_at || new Date().toISOString(),
        user: log.user_id || "unknown",
        source: log.source || "playground",
        environment: log.environment || "dev",
        hash: log.fingerprint,
        executionTimeMs: log.analysis_time_ms || 0,
      }));

      set({ auditLogs });

      console.info(`Hydrated ${auditLogs.length} audit logs from backend`);
    } catch (error) {
      console.error("Error hydrating audit logs:", error);
    }
  },
}));
