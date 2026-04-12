import React, { useMemo } from "react";
import type { PlaygroundResult } from "../types/playground";

interface PlaygroundDataPreviewTableProps {
  /** The result payload containing rows and columns */
  result: PlaygroundResult;
  /** Maximum number of rows to display (default: 5) */
  maxRows?: number;
  /** Optional CSS class name */
  className?: string;
}

/**
 * PlaygroundDataPreviewTable
 *
 * Shows a bounded preview of query result rows.
 * Reassures technical users without overwhelming non-technical users.
 *
 * Features:
 * - Limited row display (configurable, default 5)
 * - Horizontal scroll on overflow (elegant handling)
 * - Small caption explaining safety limits
 * - Clean styling matching design system
 * - Responsive columns based on data structure
 * - Graceful empty state
 * - Row count indicator showing bounded safe execution
 *
 * Design philosophy:
 * - Not a full data explorer (that's a separate feature)
 * - Preview only: shows enough to verify answer is reasonable
 * - Safety first: caption explains rows are limited
 * - Technical reassurance: count indicator shows governance in action
 */
export function PlaygroundDataPreviewTable({
  result,
  maxRows = 5,
  className = "",
}: PlaygroundDataPreviewTableProps) {
  const displayRows = useMemo(() => {
    return result.rows.slice(0, maxRows);
  }, [result.rows, maxRows]);

  const isLimited = result.rows.length > maxRows;

  // If no rows, show empty state
  if (!result.rows || result.rows.length === 0) {
    return (
      <div
        className={`rounded-lg border border-white/5 bg-white/[0.02] p-6 text-center ${className}`}
      >
        <p className="text-sm text-slate-500">No data rows available</p>
      </div>
    );
  }

  // Extract column names from first row
  const columnNames = useMemo(() => {
    if (!displayRows[0]) return [];
    return Object.keys(displayRows[0]);
  }, [displayRows]);

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Caption explaining preview and safety */}
      <div>
        <p className="text-xs text-slate-500 leading-relaxed">
          Preview rows returned under Playground safety limits.
          {isLimited && (
            <>
              {" "}
              Showing <span className="text-sky-300 font-semibold">{displayRows.length}</span> of{" "}
              <span className="text-slate-400">{result.rows.length}</span> total rows.
            </>
          )}
        </p>
      </div>

      {/* Scrollable table container */}
      <div className="rounded-lg border border-white/5 bg-white/[0.02] overflow-x-auto">
        <table className="w-full text-sm">
          {/* Header */}
          <thead>
            <tr className="border-b border-white/5">
              {columnNames.map((colName) => (
                <th
                  key={colName}
                  className="px-4 py-3 text-left font-semibold text-slate-300 whitespace-nowrap bg-black/20 text-xs uppercase tracking-[0.12em]"
                >
                  {colName}
                </th>
              ))}
            </tr>
          </thead>

          {/* Body */}
          <tbody>
            {displayRows.map((row, rowIdx) => (
              <tr
                key={rowIdx}
                className={`border-b border-white/5 hover:bg-white/[0.03] transition-colors ${
                  rowIdx === displayRows.length - 1 ? "border-b-0" : ""
                }`}
              >
                {columnNames.map((colName) => {
                  const value = row[colName];
                  const displayValue =
                    typeof value === "number"
                      ? typeof value === "number" && value > 999
                        ? value.toLocaleString()
                        : value
                      : String(value || "—");

                  return (
                    <td
                      key={`${rowIdx}-${colName}`}
                      className="px-4 py-3 text-slate-300 whitespace-nowrap"
                    >
                      {displayValue}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Row count and safety indicator */}
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>
          {displayRows.length} row{displayRows.length !== 1 ? "s" : ""} displayed
        </span>
        <span className="flex items-center gap-1">
          <span className="text-sky-400">🛡️</span>
          <span>Safe execution limits applied</span>
        </span>
      </div>
    </div>
  );
}
