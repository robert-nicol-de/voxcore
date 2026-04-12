import React, { useMemo } from "react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { PlaygroundResult } from "../types/playground";
import { mapResultToChartData } from "../utils/playgroundMappers";

interface PlaygroundChartCardProps {
  /** The result payload containing chart config and data rows */
  result: PlaygroundResult;
  /** Optional CSS class name */
  className?: string;
}

/**
 * PlaygroundChartCard
 *
 * Clean visualization of query results using Recharts.
 * Handles missing data gracefully and supports both bar and line charts.
 *
 * Features:
 * - Responsive chart container (adapts to viewport width)
 * - Bar or line chart based on result.chart.kind
 * - Minimal styling: no clutter, supports the story
 * - Graceful empty state with premium guidance
 * - Clean tooltips on hover
 * - Legend auto-disabled for single series
 *
 * Rules enforced:
 * - One chart only, no dual-axis complexity
 * - No over-styled chrome around the chart
 * - Chart layout minimal (gridlines faint, labels clear)
 * - Color palette: single series in sky-400
 */
export function PlaygroundChartCard({
  result,
  className = "",
}: PlaygroundChartCardProps) {
  const chartData = useMemo(() => mapResultToChartData(result), [result]);

  // If no data, show premium empty state
  if (chartData.isEmpty || !chartData.data || chartData.data.length === 0) {
    return (
      <div
        className={`rounded-2xl border border-white/10 bg-white/[0.03] p-8 flex items-center justify-center min-h-[400px] ${className}`}
      >
        <div className="text-center space-y-3">
          <p className="text-slate-400 font-medium">No data available</p>
          <p className="text-sm text-slate-500">
            Try refining your question to include specific time periods or metrics.
          </p>
        </div>
      </div>
    );
  }

  // Determine chart renderer based on kind
  const isLineChart = result.chart.kind === "line";

  return (
    <div
      className={`rounded-2xl border border-white/10 bg-white/[0.03] p-8 ${className}`}
    >
      {/* Chart title */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-400">
          Results
        </h3>
        <p className="text-xs text-slate-500 mt-1">
          {result.chart.seriesLabel} by {result.chart.dataKey}
        </p>
      </div>

      {/* Responsive chart container */}
      <div className="h-[400px] -mx-8 px-8 flex items-center justify-center">
        <ResponsiveContainer width="100%" height="100%">
          {isLineChart ? (
            <LineChart
              data={chartData.data as any}
              margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(255, 255, 255, 0.05)"
                vertical={false}
              />
              <XAxis
                dataKey={chartData.xKey}
                stroke="rgba(148, 163, 184, 0.5)"
                style={{ fontSize: "0.75rem" }}
              />
              <YAxis
                stroke="rgba(148, 163, 184, 0.5)"
                style={{ fontSize: "0.75rem" }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(15, 23, 42, 0.95)",
                  border: "1px solid rgba(100, 200, 255, 0.3)",
                  borderRadius: "0.5rem",
                  color: "rgb(226, 232, 240)",
                }}
                labelStyle={{ color: "rgb(226, 232, 240)" }}
                cursor={{ stroke: "rgba(100, 200, 255, 0.3)" }}
              />
              <Line
                type="monotone"
                dataKey={chartData.yKey}
                stroke="rgb(100, 200, 255)"
                strokeWidth={2}
                dot={{ fill: "rgb(100, 200, 255)", r: 4 }}
                activeDot={{ r: 6 }}
                isAnimationActive={true}
              />
            </LineChart>
          ) : (
            <BarChart
              data={chartData.data as any}
              margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(255, 255, 255, 0.05)"
                vertical={false}
              />
              <XAxis
                dataKey={chartData.xKey}
                stroke="rgba(148, 163, 184, 0.5)"
                style={{ fontSize: "0.75rem" }}
              />
              <YAxis
                stroke="rgba(148, 163, 184, 0.5)"
                style={{ fontSize: "0.75rem" }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(15, 23, 42, 0.95)",
                  border: "1px solid rgba(100, 200, 255, 0.3)",
                  borderRadius: "0.5rem",
                  color: "rgb(226, 232, 240)",
                }}
                labelStyle={{ color: "rgb(226, 232, 240)" }}
                cursor={{ fill: "rgba(100, 200, 255, 0.1)" }}
              />
              <Bar
                dataKey={chartData.yKey}
                fill="rgb(100, 200, 255)"
                radius={[8, 8, 0, 0]}
                isAnimationActive={true}
              />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* Data summary */}
      <div className="mt-6 border-t border-white/5 pt-4 flex items-center justify-between">
        <p className="text-xs text-slate-500">
          {chartData.data.length} data point{chartData.data.length !== 1 ? "s" : ""}
        </p>
        <p className="text-xs text-slate-500">{result.dataset}</p>
      </div>
    </div>
  );
}
