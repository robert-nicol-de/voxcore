import { forwardRef } from "react";
import { playgroundSampleQueries } from "./simulator";

type PlaygroundQueryComposerProps = {
  query: string;
  onQueryChange: (value: string) => void;
  onRun: () => void;
  isRunning: boolean;
};

export const PlaygroundQueryComposer = forwardRef<HTMLTextAreaElement | null, PlaygroundQueryComposerProps>(
  function PlaygroundQueryComposer(
    {
      query,
      onQueryChange,
      onRun,
      isRunning,
    },
    ref,
  ) {
    return (
      <section className="rounded-[2rem] border border-white/10 bg-[#09101c] p-8 shadow-[0_24px_80px_rgba(2,8,23,0.4)]">
        <div className="max-w-3xl">
          <div className="text-[11px] font-semibold uppercase tracking-[0.32em] text-sky-300/70">Query Interface</div>
          <h2 className="mt-3 text-3xl font-semibold text-white">Ask a governed question</h2>
          <p className="mt-3 text-sm leading-6 text-slate-300">
            Use natural language or SQL-like input. The playground always routes requests through a simulated governance layer and bounded result path.
          </p>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            type="button"
            onClick={onRun}
            className="inline-flex h-12 items-center justify-center rounded-full bg-white px-6 text-sm font-semibold text-slate-950 transition hover:scale-[1.01] hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isRunning}
          >
            {isRunning ? "Inspecting query..." : "Run through VoxCore"}
          </button>
        </div>

        <div className="mt-6 rounded-[1.75rem] border border-white/10 bg-black/20 p-5">
          <textarea
            ref={ref}
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
            rows={5}
            className="w-full resize-none rounded-[1.25rem] border border-white/10 bg-[#0b1322] px-5 py-4 font-mono text-sm leading-7 text-slate-50 caret-white outline-none transition placeholder:text-slate-400 focus:border-sky-300/40 focus:ring-2 focus:ring-sky-400/20"
            placeholder="Example: Show revenue by region"
          />
        </div>

        <div className="mt-5 flex flex-wrap gap-3">
          {playgroundSampleQueries.map((sample) => (
            <button
              key={sample}
              type="button"
              onClick={() => onQueryChange(sample)}
              className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-300 transition hover:border-sky-300/30 hover:bg-sky-400/10 hover:text-white"
            >
              {sample}
            </button>
          ))}
        </div>
      </section>
    );
  }
);
