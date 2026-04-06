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

interface GovernancePoliciesViewProps {
  currentDataset: DatasetMetaItem
}

export function GovernancePoliciesView({
  currentDataset,
}: GovernancePoliciesViewProps) {
  return (
    <div className="space-y-6">
      <div className="rounded-[28px] border border-white/10 bg-white/[0.03] p-8">
        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-sky-300/70">
          Governance Policies
        </p>
        <h2 className="mt-3 text-3xl font-semibold text-white">
          Active controls for {currentDataset.title}
        </h2>
        <p className="mt-3 text-sm leading-6 text-slate-300">
          These are demo policy controls designed to show how VoxCore constrains unsafe AI access before execution.
        </p>
      </div>

      <div className="grid gap-4">
        {currentDataset.policies.map((policy) => (
          <div
            key={policy}
            className="rounded-[24px] border border-white/10 bg-white/[0.03] p-5"
          >
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-lg font-semibold text-white">{policy}</p>
                <p className="mt-2 text-sm text-slate-300">
                  Demo control policy active for the selected dataset.
                </p>
              </div>

              <span className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-emerald-300">
                Active
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
