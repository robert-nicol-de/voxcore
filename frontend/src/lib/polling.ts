const MAX_BACKOFF_STEPS = 4;

export const BASE_POLL_MS = 5000;
export const MAX_POLL_MS = 60000;

export function nextPollDelayMs(
  failureStreak: number,
  baseMs: number = BASE_POLL_MS,
  maxMs: number = MAX_POLL_MS,
): number {
  if (failureStreak <= 0) {
    return baseMs;
  }

  const steps = Math.min(failureStreak, MAX_BACKOFF_STEPS);
  return Math.min(maxMs, baseMs * (2 ** steps));
}

export function isRetryableHttpFailure(status: number): boolean {
  return status === 404 || status === 429 || status >= 500;
}
