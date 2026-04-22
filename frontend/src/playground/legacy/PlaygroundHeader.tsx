import { DisabledFeatureButton } from "./DisabledFeatureButton";
import type { PlaygroundMode } from "../types";

type PlaygroundHeaderProps = {
  mode: PlaygroundMode;
};

export function PlaygroundHeader({ mode }: PlaygroundHeaderProps) {
  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-[#07101d]/85 px-4 py-4 backdrop-blur-xl sm:px-6 lg:px-8">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div className="min-w-0">
          <div className="text-[11px] font-semibold uppercase tracking-[0.3em] text-sky-300/75">Interactive Demo</div>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight text-white sm:text-3xl">VoxCore Playground</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
            Simulated governance, bounded analytics, and explainable insight generation over safe demo datasets.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5 lg:justify-end">
          <div className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3.5 py-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-emerald-200">
            {mode}
          </div>
          <DisabledFeatureButton label="Connect Database" />
          <DisabledFeatureButton label="Deploy Policy" />
        </div>
      </div>
    </header>
  );
}
