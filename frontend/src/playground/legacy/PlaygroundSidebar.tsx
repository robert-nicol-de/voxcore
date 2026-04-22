import { useState } from "react";
import type { PlaygroundDataset } from "@/playground/types";

export type PlaygroundSection = "playground" | "policies" | "insights" | "emd";

interface PlaygroundSidebarProps {
  activeSection: PlaygroundSection;
  onSectionChange: (section: PlaygroundSection) => void;
  activeDataset: PlaygroundDataset;
  onDatasetChange: (dataset: PlaygroundDataset) => void;
}

const sectionItems = [
  { key: "playground" as const, label: "AI Query Lab", icon: "⚡", badge: "ACTIVE" },
  { key: "emd" as const, label: "Data Explorer", icon: "🔍", badge: "CORE" },
  { key: "insights" as const, label: "Insight Library", icon: "💡", badge: "NEW" },
  { key: "policies" as const, label: "Governance Rules", icon: "🛡️", badge: "POLICY" },
];

const datasetItems = [
  { key: "sales" as const, label: "Sales" },
  { key: "users" as const, label: "Users" },
  { key: "orders" as const, label: "Orders" },
];

export function PlaygroundSidebar({
  activeSection,
  onSectionChange,
  activeDataset,
  onDatasetChange,
}: PlaygroundSidebarProps) {
  const [datasetOpen, setDatasetOpen] = useState(true);

  return (
    <aside className="fixed left-0 top-[97px] z-30 flex h-[calc(100vh-97px)] w-[92px] shrink-0 flex-col overflow-y-auto border-r border-white/10 bg-[#020817]/96 px-3 py-4 backdrop-blur-xl sm:top-[105px] sm:h-[calc(100vh-105px)] sm:w-[104px] sm:px-3.5 lg:top-[109px] lg:h-[calc(100vh-109px)] lg:w-[248px] lg:px-5 lg:py-5">
      {/* Header */}
      <div className="mb-6 animate-fade-in lg:mb-8">
        <div className="rounded-[20px] border border-sky-500/20 bg-sky-500/[0.05] p-3 lg:p-4">
          <p className="hidden text-[10px] font-semibold uppercase tracking-[0.2em] text-sky-300/70 lg:block">
            VoxCore Playground
          </p>
          <h2 className="mt-1 text-center text-sm font-semibold text-white lg:mt-2 lg:text-left lg:text-base">
            Governed Preview
          </h2>
          <p className="mt-2 hidden text-xs leading-5 text-slate-400 lg:block">
            Explore AI governance in action with safe, bounded sample data.
          </p>
        </div>
      </div>

      {/* Workspace Section */}
      <div className="mb-6">
        <p className="mb-3 hidden text-[10px] font-semibold uppercase tracking-[0.2em] text-sky-300/60 lg:block">
          Features
        </p>
        <div className="space-y-2">
          {sectionItems.map((item: any) => {
            const isActive = activeSection === item.key;
            return (
              <button
                key={item.key}
                type="button"
                onClick={() => onSectionChange(item.key)}
                className={`flex w-full items-center gap-3 rounded-[14px] px-3 py-3 text-left text-sm font-medium transition duration-200 lg:py-2.5 ${
                  isActive
                    ? "border border-sky-300/40 bg-sky-400/15 text-sky-100 shadow-[inset_0_0_12px_rgba(120,200,255,0.08)]"
                    : "border border-white/5 text-slate-300 hover:border-white/15 hover:bg-white/5"
                }`}
              >
                <span className="flex w-full items-center justify-center text-lg lg:w-auto lg:justify-start lg:text-base">
                  {item.icon}
                </span>
                <span className="hidden lg:block">{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Demo Data Section */}
      <div className="mb-auto">
        <button
          onClick={() => setDatasetOpen(!datasetOpen)}
          className="mb-3 hidden w-full items-center justify-between px-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-sky-300/60 transition hover:text-sky-300/80 lg:flex"
        >
          <span>Sample Data</span>
          <span className={`transition-transform ${ datasetOpen ? 'rotate-180' : '' }`}>▼</span>
        </button>
        {datasetOpen && (
          <div className="space-y-1.5">
            {datasetItems.map((item) => {
              const isActive = activeDataset === item.key;
              return (
                <button
                  key={item.key}
                  type="button"
                  onClick={() => onDatasetChange(item.key)}
                  className={`w-full rounded-[12px] px-3 py-2.5 text-center text-[11px] font-medium transition duration-200 lg:text-left lg:text-xs ${
                    isActive
                      ? "border border-emerald-300/40 bg-emerald-400/15 text-emerald-100 shadow-[inset_0_0_8px_rgba(34,197,94,0.08)]"
                      : "border border-white/5 text-slate-400 hover:border-white/10 hover:bg-white/3"
                  }`}
                >
                  {item.label}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Workspace footer */}
      <div className="mt-8 border-t border-white/5 pt-5">
        <div className="rounded-[16px] border border-white/8 bg-white/[0.03] px-3 py-3.5 lg:px-4">
          <div className="hidden text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-500 lg:block">
            Workspace scope
          </div>
          <div className="mt-0 text-center text-[11px] leading-5 text-slate-400 lg:mt-2 lg:text-left lg:text-xs">
            Governed sample datasets, bounded execution, and terminal-state review stay inside this workspace.
          </div>
        </div>
      </div>
    </aside>
  );
}
