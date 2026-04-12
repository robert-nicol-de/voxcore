import type { PlaygroundDataset } from "@/playground/types";

export type PlaygroundSection = "playground" | "policies" | "insights" | "emd";

interface PlaygroundSidebarProps {
  activeSection: PlaygroundSection;
  onSectionChange: (section: PlaygroundSection) => void;
  activeDataset: PlaygroundDataset;
  onDatasetChange: (dataset: PlaygroundDataset) => void;
}

const sectionItems = [
  { key: "playground" as const, label: "Live Playground", badge: "ACTIVE" },
  { key: "policies" as const, label: "Governance Policies", badge: "PREVIEW" },
  { key: "insights" as const, label: "Insight Library", badge: "PREVIEW" },
  { key: "emd" as const, label: "Explain My Data", badge: "CORE" },
];

const datasetItems = [
  { key: "users" as const, label: "Users" },
  { key: "sales" as const, label: "Sales" },
  { key: "orders" as const, label: "Orders" },
];

export function PlaygroundSidebar({
  activeSection,
  onSectionChange,
  activeDataset,
  onDatasetChange,
}: PlaygroundSidebarProps) {
  return (
    <aside className="w-full max-w-[250px] shrink-0 border-r border-white/10 bg-[#020817] px-5 py-7">
      <div className="rounded-[28px] border border-sky-500/20 bg-sky-500/[0.06] p-5">
        <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-sky-300/80">
          VoxCore Playground
        </p>
        <h2 className="mt-4 text-[18px] font-semibold leading-8 text-white">
          Governed query simulation
        </h2>
        <p className="mt-3 text-sm leading-7 text-slate-300">
          Explore how VoxCore inspects, bounds, and explains analytic requests before anything reaches data execution.
        </p>
      </div>

      <div className="mt-8">
        <p className="text-[11px] font-semibold uppercase tracking-[0.25em] text-sky-300/70">
          Workspace
        </p>

        <div className="mt-4 space-y-3">
          {sectionItems.map((item) => {
            const isActive = activeSection === item.key;
            return (
              <button
                key={item.key}
                type="button"
                onClick={() => onSectionChange(item.key)}
                className={`w-full rounded-[22px] border px-4 py-4 text-left transition ${
                  isActive
                    ? "border-white/30 bg-white/[0.06]"
                    : "border-white/10 bg-white/[0.03] hover:border-white/20 hover:bg-white/[0.05]"
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="text-base font-medium text-white">
                    {item.label}
                  </span>
                  <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-300">
                    {item.badge}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      <div className="mt-8">
        <p className="text-[11px] font-semibold uppercase tracking-[0.25em] text-sky-300/70">
          Datasets
        </p>

        <div className="mt-4 space-y-3">
          {datasetItems.map((item) => {
            const isActive = activeDataset === item.key;
            return (
              <button
                key={item.key}
                type="button"
                onClick={() => onDatasetChange(item.key)}
                className={`w-full rounded-[22px] border px-4 py-4 text-left transition ${
                  isActive
                    ? "border-white/30 bg-white/[0.06]"
                    : "border-white/10 bg-white/[0.03] hover:border-white/20 hover:bg-white/[0.05]"
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="text-base font-medium text-white">
                    {item.label}
                  </span>
                  <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-300">
                    DEMO
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </aside>
  );
}
