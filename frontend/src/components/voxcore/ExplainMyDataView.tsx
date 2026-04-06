type PlaygroundDataset = 'users' | 'sales' | 'orders'

// Matches the shape from datasetMeta
type DatasetMetaItem = {
  readonly title: string
  readonly description: string
  readonly emdInsights: readonly {
    readonly title: string
    readonly summary: string
    readonly stat: string
  }[]
  readonly libraryInsights: readonly string[]
  readonly policies: readonly string[]
}

interface ExplainMyDataViewProps {
  currentDataset: DatasetMetaItem
  activeDataset: PlaygroundDataset
}

export function ExplainMyDataView({
  currentDataset,
  activeDataset,
}: ExplainMyDataViewProps) {
  return (
    <div className="space-y-6">
      <div className="rounded-[28px] border border-white/10 bg-white/[0.03] p-8">
        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-sky-300/70">
          Explain My Data
        </p>

        <div className="mt-3 flex flex-wrap items-start justify-between gap-4">
          <div className="max-w-3xl">
            <h2 className="text-3xl font-semibold text-white">
              Auto-discover insights from {currentDataset.title}
            </h2>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              VoxCore scans the selected dataset, ranks patterns, detects anomalies, and generates insight narratives without requiring the user to know the perfect question first.
            </p>
          </div>

          <button
            type="button"
            className="rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-950"
          >
            Run EMD on {activeDataset}
          </button>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        {currentDataset.emdInsights.map((insight) => (
          <div
            key={insight.title}
            className="rounded-[24px] border border-white/10 bg-white/[0.03] p-5"
          >
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">
              Ranked Insight
            </p>
            <h3 className="mt-3 text-xl font-semibold text-white">
              {insight.title}
            </h3>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              {insight.summary}
            </p>
            <div className="mt-4 rounded-2xl border border-blue-500/20 bg-blue-500/10 px-4 py-3">
              <p className="text-xs uppercase tracking-wide text-slate-400">Signal</p>
              <p className="mt-1 text-lg font-semibold text-white">{insight.stat}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-[28px] border border-white/10 bg-white/[0.03] p-6">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">
            EMD Narrative
          </p>
          <h3 className="mt-3 text-2xl font-semibold text-white">
            What VoxCore would tell the operator
          </h3>
          <p className="mt-4 text-sm leading-7 text-slate-300">
            The selected dataset shows concentrated performance in a few strong segments, while a secondary pattern suggests operational friction in a smaller but meaningful subset. VoxCore would prioritize the strongest commercial signal first, then surface the anomaly chain and propose follow-up questions automatically.
          </p>
        </div>

        <div className="rounded-[28px] border border-white/10 bg-white/[0.03] p-6">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">
            Suggested Follow-ups
          </p>
          <div className="mt-4 space-y-3">
            {[
              `Why is ${activeDataset} trending this way?`,
              `Show anomalies in ${activeDataset}`,
              `Which segments explain the variance?`,
              `Compare top performers vs laggards`,
            ].map((item) => (
              <div
                key={item}
                className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white"
              >
                {item}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
