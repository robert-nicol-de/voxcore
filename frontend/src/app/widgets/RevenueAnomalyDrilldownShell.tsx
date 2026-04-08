import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fetchRankedAnalyticsDrilldown } from "./rankedAnalyticsApi";
import { formatCurrency } from "./revenueAnalyticsUtils";
import type { RevenueAnomalyDrilldownViewModel } from "./revenueAnomalyViewModels";

type RevenueAnomalyDrilldownShellProps<TResponse> = {
  entity: string;
  detailPathBuilder: (encodedEntity: string) => string;
  mapDetailResponse: (response: TResponse, entity: string) => RevenueAnomalyDrilldownViewModel;
  initialCopy: {
    accentClassName: string;
    description: string;
    loadingLabel: string;
  };
  onClose: () => void;
};

export default function RevenueAnomalyDrilldownShell<TResponse>({
  entity,
  detailPathBuilder,
  mapDetailResponse,
  initialCopy,
  onClose,
}: RevenueAnomalyDrilldownShellProps<TResponse>) {
  const [payload, setPayload] = useState<RevenueAnomalyDrilldownViewModel | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const json = await fetchRankedAnalyticsDrilldown<TResponse>(detailPathBuilder, entity, controller.signal);
        setPayload(mapDetailResponse(json, entity));
      } catch (fetchError) {
        if (!controller.signal.aborted) {
          setError(fetchError instanceof Error ? fetchError.message : "Failed to load anomaly detail");
          setPayload(null);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    };

    void load();
    return () => controller.abort();
  }, [detailPathBuilder, entity, mapDetailResponse]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 py-6 backdrop-blur-sm"
      onClick={onClose}
      role="presentation"
    >
      <div
        className="w-full max-w-4xl rounded-[1.75rem] border border-white/10 bg-[#09111d] p-6 text-white shadow-[0_24px_80px_rgba(2,8,23,0.65)]"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className={`text-xs font-semibold uppercase tracking-[0.24em] ${payload?.accentClassName || initialCopy.accentClassName}`}>
              Governed Drill-Down
            </div>
            <h3 className="mt-2 text-2xl font-semibold">{entity}</h3>
            <p className="mt-2 text-sm text-slate-300">{payload?.description || initialCopy.description}</p>
          </div>
          <button
            className="rounded-full border border-white/10 px-3 py-1 text-sm text-slate-200 transition hover:border-white/30 hover:text-white"
            onClick={onClose}
          >
            Close
          </button>
        </div>

        {loading ? <LoadingState label={payload?.loadingLabel || initialCopy.loadingLabel} /> : null}
        {!loading && error ? <ErrorState error={error} /> : null}
        {!loading && !error && payload && payload.timeline.rows.length === 0 ? (
          <EmptyState message={payload.emptyMessage} />
        ) : null}
        {!loading && !error && payload && payload.timeline.rows.length > 0 ? (
          <DrilldownContent payload={payload} />
        ) : null}
      </div>
    </div>
  );
}

function DrilldownContent({ payload }: { payload: RevenueAnomalyDrilldownViewModel }) {
  return (
    <div className="mt-6 grid gap-5 xl:grid-cols-[minmax(0,1.3fr)_minmax(320px,1fr)]">
      <div className="space-y-5">
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <DrilldownStat label="Current Revenue" value={formatCurrency(payload.summary.current_revenue)} />
          <DrilldownStat label="Baseline" value={formatCurrency(payload.summary.baseline_revenue)} />
          <DrilldownStat label="Delta %" value={`${payload.summary.delta_percent.toFixed(2)}%`} />
          <DrilldownStat label="Severity" value={payload.summary.severity} />
        </div>

        <div className="rounded-[1.25rem] border border-white/8 bg-[#0d1728] p-4">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-white">{payload.chartTitle}</div>
              <div className="text-xs text-slate-400">{payload.chartHint}</div>
            </div>
            <div className="text-xs text-slate-400">Points {payload.timeline.row_limit}</div>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={payload.timeline.rows} margin={{ top: 8, right: 16, left: 0, bottom: 16 }}>
                <CartesianGrid stroke="rgba(148,163,184,0.12)" vertical={false} />
                <XAxis dataKey="period" stroke="#94a3b8" tickLine={false} axisLine={false} />
                <YAxis
                  stroke="#94a3b8"
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) => formatCurrency(Number(value))}
                />
                <Tooltip
                  cursor={{ fill: "rgba(139,92,246,0.12)" }}
                  contentStyle={{
                    background: "#0f172a",
                    border: "1px solid rgba(148,163,184,0.2)",
                    borderRadius: "16px",
                    color: "#e2e8f0",
                  }}
                />
                <Bar dataKey="revenue" radius={[14, 14, 6, 6]}>
                  {payload.timeline.rows.map((entry) => (
                    <Cell
                      key={`${entry.period}-revenue`}
                      fill={entry.is_anomaly ? payload.detailBarFill : payload.expectedBarFill}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 overflow-hidden rounded-2xl border border-white/6">
            <table className="min-w-full divide-y divide-white/6 text-sm">
              <thead className="bg-white/5 text-slate-300">
                <tr>
                  <th className="px-4 py-3 text-left font-medium">Period</th>
                  <th className="px-4 py-3 text-left font-medium">Revenue</th>
                  <th className="px-4 py-3 text-left font-medium">Expected</th>
                  <th className="px-4 py-3 text-left font-medium">Deviation %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/6 bg-[#0a101c]">
                {payload.timeline.rows.map((row) => (
                  <tr key={row.period} className={row.is_anomaly ? "bg-violet-500/10" : "transition hover:bg-white/5"}>
                    <td className="px-4 py-3 font-medium text-white">{row.period}</td>
                    <td className="px-4 py-3 text-slate-200">{formatCurrency(row.revenue)}</td>
                    <td className="px-4 py-3 text-slate-300">{formatCurrency(row.expected_revenue)}</td>
                    <td className="px-4 py-3 text-slate-300">{row.deviation_percent.toFixed(2)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <aside className="space-y-4">
        <div className="rounded-[1.25rem] border border-white/8 bg-[#0d1728] p-5">
          <div className="text-sm font-medium text-white">Insight Summary</div>
          <div className={`mt-3 text-lg font-semibold ${payload.headlineClassName}`}>
            {payload.insight_summary.headline}
          </div>
          <p className="mt-3 text-sm leading-6 text-slate-300">{payload.insight_summary.narrative}</p>
          <ul className="mt-4 space-y-2 text-sm text-slate-200">
            {payload.insight_summary.highlights.map((highlight) => (
              <li key={highlight} className="rounded-xl bg-white/5 px-3 py-2">
                {highlight}
              </li>
            ))}
          </ul>
        </div>

        <div className="rounded-[1.25rem] border border-white/8 bg-[#0d1728] p-5">
          <div className="text-sm font-medium text-white">Governance</div>
          <div className="mt-4 grid gap-3">
            <GovernancePanel title="Summary Query" payload={payload.governance.summary_query} />
            <GovernancePanel title="Timeline Query" payload={payload.governance.peer_query} />
          </div>
          <div className="mt-4 text-xs text-slate-400">
            Aggregate-only: {payload.response_meta.aggregate_only ? "Yes" : "No"} · Bounded:{" "}
            {payload.response_meta.bounded ? "Yes" : "No"}
          </div>
        </div>
      </aside>
    </div>
  );
}

function GovernancePanel({
  title,
  payload,
}: {
  title: string;
  payload: RevenueAnomalyDrilldownViewModel["governance"]["summary_query"];
}) {
  return (
    <div className="rounded-xl border border-white/8 bg-white/5 p-3 text-sm">
      <div className="font-medium text-white">{title}</div>
      <div className="mt-2 text-slate-300">Risk score: {payload.risk_score}</div>
      <div className="text-slate-300">Cost level: {payload.cost_level}</div>
      <div className="text-slate-300">Row limit: {payload.row_limit}</div>
      <div className="text-slate-300">Timeout: {payload.timeout_seconds}s</div>
    </div>
  );
}

function LoadingState({ label }: { label: string }) {
  return (
    <div className="mt-6 animate-pulse space-y-4" aria-label={label}>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="h-24 rounded-2xl bg-white/10" />
        <div className="h-24 rounded-2xl bg-white/10" />
        <div className="h-24 rounded-2xl bg-white/10" />
        <div className="h-24 rounded-2xl bg-white/10" />
      </div>
      <div className="h-72 rounded-2xl bg-white/10" />
    </div>
  );
}

function ErrorState({ error }: { error: string }) {
  return (
    <div className="mt-6 rounded-[1.25rem] border border-rose-500/25 bg-rose-500/10 p-4 text-sm text-rose-100">
      {error}
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="mt-6 rounded-[1.25rem] border border-white/8 bg-[#0d1728] p-5 text-sm text-slate-300">
      {message}
    </div>
  );
}

function DrilldownStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[1.15rem] border border-white/8 bg-[#0d1728] p-4">
      <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">{label}</div>
      <div className="mt-3 text-xl font-semibold text-white">{value}</div>
    </div>
  );
}
