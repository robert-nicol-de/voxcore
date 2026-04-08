import { useEffect, useMemo, useState, type ReactNode } from "react";
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
import { fetchRankedAnalyticsAggregate } from "./rankedAnalyticsApi";
import type { RevenueAnomalyAggregateViewModel } from "./revenueAnomalyViewModels";

type SortKey = "entity" | "delta_percent" | "anomaly_score";

type RevenueAnomaliesWidgetShellProps<TResponse> = {
  aggregatePath: string;
  mapAggregateResponse: (response: TResponse) => RevenueAnomalyAggregateViewModel;
  chartPalette: string[];
  rowTestIdPrefix: string;
  renderDrilldownModal: (entity: string, onClose: () => void) => ReactNode;
};

export default function RevenueAnomaliesWidgetShell<TResponse>({
  aggregatePath,
  mapAggregateResponse,
  chartPalette,
  rowTestIdPrefix,
  renderDrilldownModal,
}: RevenueAnomaliesWidgetShellProps<TResponse>) {
  const [payload, setPayload] = useState<RevenueAnomalyAggregateViewModel | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEntity, setSelectedEntity] = useState<string | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>("anomaly_score");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");

  useEffect(() => {
    const controller = new AbortController();

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const json = await fetchRankedAnalyticsAggregate<TResponse>(aggregatePath, controller.signal);
        setPayload(mapAggregateResponse(json));
      } catch (fetchError) {
        if (!controller.signal.aborted) {
          setError(fetchError instanceof Error ? fetchError.message : "Failed to load anomalies");
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
  }, [aggregatePath, mapAggregateResponse]);

  const rows = payload?.data || [];
  const sortedRows = useMemo(() => {
    const next = [...rows];
    next.sort((a, b) => {
      const aValue = a[sortKey];
      const bValue = b[sortKey];
      if (typeof aValue === "number" && typeof bValue === "number") {
        return sortDirection === "asc" ? aValue - bValue : bValue - aValue;
      }
      return sortDirection === "asc"
        ? String(aValue).localeCompare(String(bValue))
        : String(bValue).localeCompare(String(aValue));
    });
    return next;
  }, [rows, sortDirection, sortKey]);

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDirection((current) => (current === "asc" ? "desc" : "asc"));
      return;
    }
    setSortKey(key);
    setSortDirection(key === "entity" ? "asc" : "desc");
  };

  if (loading) {
    return (
      <div className="rounded-[1.5rem] border border-white/10 bg-[#101826] p-6 shadow-[0_20px_60px_rgba(2,8,23,0.45)]">
        <div className="animate-pulse space-y-4">
          <div className="h-6 w-56 rounded bg-white/10" />
          <div className="grid gap-4 md:grid-cols-3">
            <div className="h-24 rounded-2xl bg-white/10" />
            <div className="h-24 rounded-2xl bg-white/10" />
            <div className="h-24 rounded-2xl bg-white/10" />
          </div>
          <div className="h-80 rounded-2xl bg-white/10" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-[1.5rem] border border-rose-500/30 bg-[#161122] p-6 text-rose-100 shadow-[0_20px_60px_rgba(59,7,18,0.35)]">
        <div className="text-lg font-semibold">{payload?.title || "Governed Revenue Anomalies"}</div>
        <p className="mt-2 text-sm text-rose-200/85">{error}</p>
      </div>
    );
  }

  if (!payload) {
    return null;
  }

  return (
    <>
      <section
        className="rounded-[1.5rem] border border-white/10 bg-[#101826] p-6 text-white shadow-[0_20px_60px_rgba(2,8,23,0.45)]"
        data-testid={payload.widgetTestId}
      >
        <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <p className={`text-xs font-semibold uppercase tracking-[0.24em] ${payload.eyebrowClassName}`}>
              Governed Analytics
            </p>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight">{payload.title}</h2>
            <p className="mt-2 max-w-3xl text-sm text-slate-300">{payload.narrative}</p>
          </div>
          <div className={`rounded-2xl border px-4 py-3 text-sm ${payload.governanceBadgeClassName}`}>
            <div>Risk score: {payload.governance.risk_score}</div>
            <div>Cost level: {payload.governance.cost_level}</div>
          </div>
        </div>

        <div className="mt-6 grid gap-4 xl:grid-cols-[minmax(0,2fr)_minmax(320px,1fr)]">
          <div className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <SummaryStat
                label={payload.summary_card.metric_label}
                value={String(payload.summary_card.metric_value)}
                tone={payload.summaryTones[0]}
              />
              <SummaryStat
                label="Top Entity"
                value={payload.summary_card.top_entity}
                helper={`Score ${payload.summary_card.highest_anomaly_score.toFixed(2)}`}
                tone={payload.summaryTones[1]}
              />
              <SummaryStat
                label="High Severity"
                value={String(payload.summary_card.high_severity_count)}
                helper={`Timeout ${payload.governance.timeout_seconds}s`}
                tone={payload.summaryTones[2]}
              />
            </div>

            <div className="rounded-[1.25rem] border border-white/8 bg-[#0b1220] p-4">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-white">{payload.chartTitle}</div>
                  <div className="text-xs text-slate-400">{payload.chartHint}</div>
                </div>
                <div className="text-xs text-slate-400">Row limit {payload.governance.row_limit}</div>
              </div>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={payload.data} margin={{ top: 8, right: 16, left: 0, bottom: 16 }}>
                    <CartesianGrid stroke="rgba(148,163,184,0.12)" vertical={false} />
                    <XAxis dataKey="entity" stroke="#94a3b8" tickLine={false} axisLine={false} />
                    <YAxis stroke="#94a3b8" tickLine={false} axisLine={false} />
                    <Tooltip
                      cursor={{ fill: "rgba(249,115,22,0.12)" }}
                      contentStyle={{
                        background: "#0f172a",
                        border: "1px solid rgba(148,163,184,0.2)",
                        borderRadius: "16px",
                        color: "#e2e8f0",
                      }}
                      formatter={(value: number | string | ReadonlyArray<number | string> | undefined) =>
                        `${Number(Array.isArray(value) ? value[0] : (value ?? 0)).toFixed(2)}%`
                      }
                    />
                    <Bar dataKey="delta_percent" radius={[16, 16, 6, 6]}>
                      {payload.data.map((entry, index) => (
                        <Cell
                          key={entry.entity}
                          fill={chartPalette[index % chartPalette.length]}
                          onClick={() => setSelectedEntity(entry.entity)}
                          style={{ cursor: "pointer" }}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="rounded-[1.25rem] border border-white/8 bg-[#0b1220] p-4">
              <div className="mb-3 flex items-center justify-between">
                <div className="text-sm font-medium text-white">{payload.tableTitle}</div>
                <div className="text-xs text-slate-400">{payload.tableHint}</div>
              </div>
              <div className="overflow-hidden rounded-2xl border border-white/6">
                <table className="min-w-full divide-y divide-white/6 text-sm">
                  <thead className="bg-white/5 text-slate-300">
                    <tr>
                      <HeaderButton label="Entity" onClick={() => toggleSort("entity")} />
                      <HeaderButton label="Delta %" onClick={() => toggleSort("delta_percent")} />
                      <HeaderButton label="Score" onClick={() => toggleSort("anomaly_score")} />
                      <th className="px-4 py-3 text-left font-medium">Type</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/6 bg-[#0a101c]">
                    {sortedRows.map((row) => (
                      <tr
                        key={row.entity}
                        className="cursor-pointer transition hover:bg-white/5"
                        onClick={() => setSelectedEntity(row.entity)}
                        data-testid={`${rowTestIdPrefix}-${row.entity}`}
                      >
                        <td className="px-4 py-3 font-medium text-white">{row.entity}</td>
                        <td className="px-4 py-3 text-slate-200">{row.delta_percent.toFixed(2)}%</td>
                        <td className="px-4 py-3 text-slate-300">{row.anomaly_score.toFixed(2)}</td>
                        <td className="px-4 py-3 text-slate-300">{row.anomaly_type}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <aside className="space-y-4">
            <div className="rounded-[1.25rem] border border-white/8 bg-[#0b1220] p-5">
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

            <div className="rounded-[1.25rem] border border-amber-400/15 bg-amber-400/5 p-5">
              <div className="text-sm font-medium text-amber-200">Risk Signal</div>
              <p className="mt-3 text-sm leading-6 text-amber-100/85">
                {payload.insight_summary.risk || "No elevated governance risk reported for this governed view."}
              </p>
              {payload.governance.warnings.length > 0 && (
                <ul className="mt-3 space-y-2 text-xs text-amber-100/80">
                  {payload.governance.warnings.map((warning) => (
                    <li key={warning}>{warning}</li>
                  ))}
                </ul>
              )}
            </div>
          </aside>
        </div>
      </section>

      {selectedEntity ? renderDrilldownModal(selectedEntity, () => setSelectedEntity(null)) : null}
    </>
  );
}

function SummaryStat({
  label,
  value,
  helper,
  tone,
}: {
  label: string;
  value: string;
  helper?: string;
  tone: string;
}) {
  return (
    <div className={`rounded-[1.25rem] border border-white/8 bg-gradient-to-br ${tone} p-4`}>
      <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-300">{label}</div>
      <div className="mt-3 text-2xl font-semibold text-white">{value}</div>
      {helper ? <div className="mt-2 text-sm text-slate-300">{helper}</div> : null}
    </div>
  );
}

function HeaderButton({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <th className="px-4 py-3 text-left">
      <button className="font-medium transition hover:text-white" onClick={onClick}>
        {label}
      </button>
    </th>
  );
}
