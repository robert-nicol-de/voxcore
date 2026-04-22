import type { GovernedJobSnapshot } from "./governedJobPolling";

export type GovernedCompatibilityStatus = "blocked" | "allowed" | "pending_approval";

export type GovernedNormalizedJobResult = {
  canonicalStatus: string;
  jobId: string | null;
  status: GovernedCompatibilityStatus;
  success: boolean;
  message: string;
  error?: string;
  sql: string;
  results: any[];
  rowsReturned: number;
  riskScore: number;
  reasons: string[];
  rawResult: Record<string, unknown>;
  rawJob: GovernedJobSnapshot;
};

type PayloadLike = Record<string, any>;

function asObject(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" ? (value as Record<string, unknown>) : {};
}

function asString(value: unknown, fallback = ""): string {
  return typeof value === "string" && value.trim() ? value : fallback;
}

function asNumber(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

export function normalizeGovernedCompatibilityStatus(
  jobStatus: string,
  payloadStatus?: unknown
): GovernedCompatibilityStatus {
  if (jobStatus === "blocked" || payloadStatus === "blocked") {
    return "blocked";
  }
  if (payloadStatus === "approval_required" || payloadStatus === "pending_approval") {
    return "pending_approval";
  }
  return "allowed";
}

export function getGovernedSqlText(payloadLike: PayloadLike = {}): string {
  return asString(payloadLike.final_sql)
    || asString(payloadLike.generated_sql)
    || asString(payloadLike.sql)
    || asString(payloadLike.rewritten_sql)
    || asString(payloadLike.original_sql);
}

export function getGovernedResults(payloadLike: PayloadLike = {}): any[] {
  if (Array.isArray(payloadLike.results)) {
    return payloadLike.results;
  }
  if (Array.isArray(payloadLike.data)) {
    return payloadLike.data;
  }
  return [];
}

export function getGovernedRowsReturned(payloadLike: PayloadLike = {}): number {
  const execution = asObject(payloadLike.execution);
  return asNumber(payloadLike.rows_returned,
    asNumber(payloadLike.row_count,
      asNumber(execution.rows_returned, getGovernedResults(payloadLike).length)));
}

export function getGovernedRiskScore(payloadLike: PayloadLike = {}): number {
  return asNumber(payloadLike.risk_score, 0);
}

export function normalizeGovernedJobResult(
  job: GovernedJobSnapshot,
  current: PayloadLike = {}
): GovernedNormalizedJobResult {
  const rawResult = asObject(job.result);
  const merged: PayloadLike = {
    ...current,
    ...rawResult,
    canonical_status: asString(job.status, asString(current.canonical_status, "queued")),
    job_id: asString(job.job_id, asString(current.job_id)) || null,
  };

  const canonicalStatus = asString(merged.canonical_status, "queued");
  const status = normalizeGovernedCompatibilityStatus(canonicalStatus, merged.status);
  const sql = getGovernedSqlText(merged);
  const results = getGovernedResults(merged);
  const rowsReturned = getGovernedRowsReturned(merged);
  const riskScore = getGovernedRiskScore(merged);
  const reasons = asStringArray(merged.reasons);

  let message =
    asString(merged.message)
    || (reasons.length > 0 ? reasons[0] : "")
    || (canonicalStatus === "completed"
      ? "Response received"
      : canonicalStatus === "blocked"
        ? "Query blocked by governance policy."
        : canonicalStatus === "failed"
          ? "Governed query execution failed."
          : "Query queued for governed execution.");

  let error: string | undefined;
  let success = true;

  if (canonicalStatus === "failed") {
    error = asString(job.error) || asString(merged.error) || "Governed query execution failed.";
    message = error;
    success = false;
  } else if (canonicalStatus === "blocked" || status === "blocked") {
    error =
      asString(merged.error)
      || asString(merged.message)
      || (reasons.length > 0 ? reasons[0] : "")
      || "Query blocked by governance policy.";
    message = error;
    success = false;
  }

  return {
    canonicalStatus,
    jobId: typeof merged.job_id === "string" ? merged.job_id : null,
    status,
    success,
    message,
    error,
    sql,
    results,
    rowsReturned,
    riskScore,
    reasons,
    rawResult,
    rawJob: job,
  };
}
