/**
 * Playground Formatters
 *
 * Pure formatting functions for display values.
 * Used by components to format numbers, dates, strings, etc.
 *
 * Responsibilities:
 * - Number formatting (currency, percentages, thousands)
 * - Date/time formatting
 * - Risk level labeling
 * - Status badge text
 * - Truncation and ellipsis
 */

import type { PlaygroundRiskLevel, PlaygroundDecision } from "../types/playground";

/**
 * Format number as USD currency.
 */
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

/**
 * Format number as percentage.
 */
export function formatPercentage(value: number, decimals = 1): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Format number with thousands separator.
 */
export function formatNumber(value: number, decimals = 0): string {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: decimals,
    minimumFractionDigits: decimals,
  }).format(value);
}

/**
 * Format number as "K" / "M" notation for large numbers.
 */
export function formatCompactNumber(value: number): string {
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M`;
  }
  if (value >= 1_000) {
    return `${(value / 1_000).toFixed(1)}K`;
  }
  return value.toString();
}

/**
 * Format date to readable string.
 */
export function formatDate(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(d);
}

/**
 * Format date and time.
 */
export function formatDateTime(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(d);
}

/**
 * Format ISO date string to human-readable format.
 */
export function formatIsoDate(isoString: string): string {
  try {
    return formatDate(new Date(isoString));
  } catch {
    return isoString;
  }
}

/**
 * Truncate string with ellipsis.
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  return `${text.slice(0, maxLength - 3)}...`;
}

/**
 * Truncate text to character limit, word-aware.
 */
export function truncateWords(text: string, maxWords: number): string {
  const words = text.split(" ");
  if (words.length <= maxWords) {
    return text;
  }
  return `${words.slice(0, maxWords).join(" ")}...`;
}

/**
 * Format risk level for display.
 */
export function formatRiskLevel(level: PlaygroundRiskLevel): string {
  const map: Record<PlaygroundRiskLevel, string> = {
    SAFE: "Safe",
    MEDIUM: "Medium Risk",
    HIGH: "High Risk",
  };
  return map[level];
}

/**
 * Format risk score with label.
 */
export function formatRiskScore(score: number): string {
  if (score >= 75) {
    return `${score} (High)`;
  }
  if (score >= 35) {
    return `${score} (Medium)`;
  }
  return `${score} (Safe)`;
}

/**
 * Format decision for display.
 */
export function formatDecision(decision: PlaygroundDecision): string {
  const map: Record<PlaygroundDecision, string> = {
    Allowed: "Query Allowed",
    Review: "Requires Review",
    Blocked: "Query Blocked",
  };
  return map[decision];
}

/**
 * Format cost level for display.
 */
export function formatCostLevel(cost: "LOW" | "MEDIUM" | "HIGH"): string {
  const map = {
    LOW: "Low Cost",
    MEDIUM: "Medium Cost",
    HIGH: "High Cost",
  };
  return map[cost];
}

/**
 * Format execution time in milliseconds.
 */
export function formatExecutionTime(ms: number): string {
  if (ms < 1000) {
    return `${Math.round(ms)}ms`;
  }
  return `${(ms / 1000).toFixed(2)}s`;
}

/**
 * Format row count with label.
 */
export function formatRowCount(count: number): string {
  if (count === 0) {
    return "No rows";
  }
  if (count === 1) {
    return "1 row";
  }
  return `${formatNumber(count)} rows`;
}

/**
 * Format column name from key (snake_case to Title Case).
 */
export function formatColumnName(key: string): string {
  return key
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

/**
 * Format boolean value as "Yes" or "No".
 */
export function formatBoolean(value: boolean): string {
  return value ? "Yes" : "No";
}

/**
 * Format generic value based on type.
 */
export function formatValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "—";
  }
  if (typeof value === "boolean") {
    return formatBoolean(value);
  }
  if (typeof value === "number") {
    // Try to detect currency by context
    if (value > 1000 || value < -1000) {
      return formatCompactNumber(value);
    }
    return formatNumber(value, 2);
  }
  if (typeof value === "string") {
    return value;
  }
  return JSON.stringify(value);
}

/**
 * Format time duration (seconds to human readable).
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${Math.round(seconds)}s`;
  }
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.round(seconds % 60);
  return `${minutes}m ${remainingSeconds}s`;
}

/**
 * Format relative time (e.g., "2 hours ago").
 */
export function formatRelativeTime(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 60) {
    return "just now";
  }
  if (diffMin < 60) {
    return `${diffMin} minute${diffMin !== 1 ? "s" : ""} ago`;
  }
  if (diffHour < 24) {
    return `${diffHour} hour${diffHour !== 1 ? "s" : ""} ago`;
  }
  return `${diffDay} day${diffDay !== 1 ? "s" : ""} ago`;
}

/**
 * Capitalize first letter.
 */
export function capitalize(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1);
}

/**
 * Convert camelCase to Title Case.
 */
export function camelCaseToTitleCase(text: string): string {
  return text
    .replace(/([A-Z])/g, " $1")
    .replace(/^./, (str) => str.toUpperCase())
    .trim();
}
