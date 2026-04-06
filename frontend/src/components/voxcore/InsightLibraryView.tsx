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

interface InsightLibraryViewProps {
  currentDataset: DatasetMetaItem
}

export function InsightLibraryView({
  currentDataset,
}: InsightLibraryViewProps) {
  return (
    <div className="space-y-6">
      <div className="rounded-[28px] border border-white/10 bg-white/[0.03] p-8">
        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-sky-300/70">
          Insight Library
        </p>
        <h2 className="mt-3 text-3xl font-semibold text-white">
          Saved intelligence for {currentDataset.title}
        </h2>
        <p className="mt-3 text-sm leading-6 text-slate-300">
          Stored narratives, anomalies, and operational signals surfaced by VoxCore.
        </p>
      </div>

      <div className="grid gap-4">
        {currentDataset.libraryInsights.map((item) => (
          <div
            key={item}
            className="rounded-[24px] border border-white/10 bg-white/[0.03] p-5"
          >
            <p className="text-lg font-semibold text-white">{item}</p>
            <p className="mt-2 text-sm text-slate-300">
              Demo saved insight entry for the selected dataset.
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}
