import { apiUrl } from "./api";

export const DEFAULT_GOVERNED_JOB_POLL_INTERVAL_MS = 2500;
export const DEFAULT_GOVERNED_JOB_MAX_ATTEMPTS = 24;

export type GovernedJobSnapshot = {
  job_id: string;
  status: string;
  created_at?: string | null;
  updated_at?: string | null;
  payload?: Record<string, unknown>;
  result?: Record<string, unknown> | null;
  error?: string | null;
};

type PollGovernedJobOptions<TState> = {
  jobId: string;
  initialState: TState;
  isCurrent: () => boolean;
  mergeSnapshot: (current: TState, job: GovernedJobSnapshot) => TState;
  onUpdate: (next: TState) => void;
  onTimeout?: (current: TState, jobId: string) => TState;
  onError?: (current: TState, error: Error) => TState;
  intervalMs?: number;
  maxAttempts?: number;
};

export function isTerminalGovernedJobStatus(status: string): boolean {
  return status === "completed" || status === "failed" || status === "blocked";
}

export async function pollGovernedJob<TState>({
  jobId,
  initialState,
  isCurrent,
  mergeSnapshot,
  onUpdate,
  onTimeout,
  onError,
  intervalMs = DEFAULT_GOVERNED_JOB_POLL_INTERVAL_MS,
  maxAttempts = DEFAULT_GOVERNED_JOB_MAX_ATTEMPTS,
}: PollGovernedJobOptions<TState>): Promise<TState> {
  let currentState = initialState;

  try {
    for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
      await new Promise((resolve) => window.setTimeout(resolve, intervalMs));
      if (!isCurrent()) {
        return currentState;
      }

      const response = await fetch(apiUrl(`/api/v1/query/jobs/${jobId}`), {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Job polling failed: ${response.status}`);
      }

      const job = (await response.json()) as GovernedJobSnapshot;
      currentState = mergeSnapshot(currentState, job);

      if (!isCurrent()) {
        return currentState;
      }

      onUpdate(currentState);

      if (isTerminalGovernedJobStatus(String(job.status || ""))) {
        if (job.status === "failed") {
          throw new Error(job.error || "Governed query execution failed.");
        }
        return currentState;
      }
    }

    if (!isCurrent()) {
      return currentState;
    }

    if (onTimeout) {
      currentState = onTimeout(currentState, jobId);
      if (isCurrent()) {
        onUpdate(currentState);
      }
    }

    return currentState;
  } catch (error) {
    if (!isCurrent()) {
      return currentState;
    }

    if (onError) {
      currentState = onError(
        currentState,
        error instanceof Error ? error : new Error("Polling for query completion failed.")
      );
      if (isCurrent()) {
        onUpdate(currentState);
      }
      return currentState;
    }

    throw error;
  }
}
