const navSections = [
  {
    title: "Workspace",
    items: [
      { label: "Live Playground", state: "Active" },
      { label: "Governance Policies", state: "Preview" },
      { label: "Insight Library", state: "Preview" },
    ],
  },
  {
    title: "Datasets",
    items: [
      { label: "Users", state: "Demo" },
      { label: "Sales", state: "Demo" },
      { label: "Orders", state: "Demo" },
    ],
  },
];

export function PlaygroundSidebar() {
  return (
    <aside className="hidden border-r border-white/10 bg-[#060a17] xl:block xl:w-[280px]">
      <div className="flex h-full flex-col px-6 py-8">
        <div className="rounded-[1.75rem] border border-sky-400/20 bg-sky-400/10 p-5 shadow-[0_24px_60px_rgba(14,165,233,0.12)]">
          <div className="text-[11px] font-semibold uppercase tracking-[0.32em] text-sky-200/70">
            VoxCore Playground
          </div>
          <h2 className="mt-3 text-xl font-semibold text-white">Governed query simulation</h2>
          <p className="mt-3 text-sm leading-6 text-slate-300">
            Explore how VoxCore inspects, bounds, and explains analytic requests before anything reaches data execution.
          </p>
        </div>

        <div className="mt-8 space-y-6">
          {navSections.map((section) => (
            <div key={section.title}>
              <div className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-500">{section.title}</div>
              <div className="mt-3 space-y-2">
                {section.items.map((item) => (
                  <div
                    key={item.label}
                    className="flex items-center justify-between rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-3"
                  >
                    <span className="text-sm text-slate-200">{item.label}</span>
                    <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">
                      {item.state}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
}
