import { runQuery } from "@/lib/api";

import { runPlaygroundQuery } from "./simulator";
import type { PlaygroundMode, PlaygroundQueryContext, PlaygroundResult, PlaygroundViewModel } from "./types";

type PlaygroundExecutionSource = "backend" | "local-fallback";

// Force demo mode when env var is set (for clean testing without backend)
const FORCE_DEMO_MODE = import.meta.env.VITE_PLAYGROUND_FORCE_DEMO === 'true';

const classificationFromBackend = (
  status: "blocked" | "allowed" | "pending_approval",
  riskScore: number,
): PlaygroundResult["governance"]["classification"] => {
  if (status === "blocked" || riskScore >= 75) {
    return "HIGH";
  }
  if (status === "pending_approval" || riskScore >= 35) {
    return "MEDIUM";
  }
  return "SAFE";
};

const decisionFromBackend = (
  status: "blocked" | "allowed" | "pending_approval",
): PlaygroundResult["decision"] => {
  if (status === "blocked") {
    return "Blocked";
  }
  if (status === "pending_approval") {
    return "Review";
  }
  return "Allowed";
};

const modeLabel = (source: PlaygroundExecutionSource): PlaygroundMode => {
  return source === "backend" ? "Live Backend" : "Demo Fallback";
};

function buildQueryContext(
  sessionId: string,
  source: PlaygroundExecutionSource,
  backendContext?: {
    user?: string;
    environment?: string;
    source?: string;
  },
): PlaygroundQueryContext {
  return {
    user: backendContext?.user || "ai-agent",
    environment: backendContext?.environment || (source === "backend" ? "dev" : "demo"),
    source: backendContext?.source || (source === "backend" ? "playground" : "playground-simulator"),
    route: "Query Router -> Governance Engine -> Query Execution -> Insight Engine -> Exploration Engine",
    sessionId,
    orgId: window.localStorage.getItem("voxcore_org_id") || "default-org",
  };
}

function buildViewModel(
  source: PlaygroundExecutionSource,
  result: PlaygroundResult,
  notice: string,
): PlaygroundViewModel {
  return {
    mode: modeLabel(source),
    notice,
    result,
  };
}

export function buildInitialPlaygroundViewModel(): PlaygroundViewModel {
  const result = runPlaygroundQuery("Show revenue by region");
  return buildViewModel("local-fallback", {
    ...result,
    governance: {
      ...result.governance,
      warnings: Array.from(
        new Set([
          ...result.governance.warnings,
          "Connecting to live governance pipeline...",
        ]),
      ),
    },
  }, "Demo workspace using sample data — live governance pipeline connected");
}

export async function executePlaygroundQuery(
  query: string,
  sessionId: string,
): Promise<PlaygroundViewModel> {
  // If forced demo mode, skip backend entirely
  if (FORCE_DEMO_MODE) {
    const localResult = runPlaygroundQuery(query);
    return buildViewModel("local-fallback", {
      ...localResult,
      queryContext: buildQueryContext(sessionId, "local-fallback"),
      governance: {
        ...localResult.governance,
        warnings: Array.from(
          new Set([
            ...localResult.governance.warnings,
            "Demo mode enabled - backend skipped for clean testing.",
          ]),
        ),
      },
    }, "Running in demo mode for clean testing.");
  }

  const localResult = runPlaygroundQuery(query);

  try {
    const backend = await runQuery(query, {
      sessionId,
      environment: "dev",
      source: "playground",
      user: "ai-agent",
    });

    return buildViewModel("backend", {
      ...localResult,
      decision: decisionFromBackend(backend.status),
      governance: {
        ...localResult.governance,
        classification: classificationFromBackend(backend.status, backend.riskScore),
        riskScore: backend.riskScore,
        policyStatus:
          backend.status === "blocked"
            ? "BLOCKED"
            : backend.status === "pending_approval"
              ? "REVIEW"
              : "APPROVED",
        rationale:
          backend.reasons.length > 0
            ? backend.reasons.join(" ")
            : localResult.governance.rationale,
        warnings: backend.reasons.length > 0
          ? Array.from(new Set([...backend.reasons, ...localResult.governance.warnings]))
          : localResult.governance.warnings,
      },
      queryContext: buildQueryContext(sessionId, "backend", backend.context),
    }, "Live query executed through voxcore governance pipeline");
  } catch {
    return buildViewModel("local-fallback", {
      ...localResult,
      queryContext: buildQueryContext(sessionId, "local-fallback"),
      governance: {
        ...localResult.governance,
        warnings: Array.from(
          new Set([
            ...localResult.governance.warnings,
            "Demo data source not connected — using sample data.",
          ]),
        ),
      },
    }, "Live governance pipeline reached — demo data available");
  }
}
