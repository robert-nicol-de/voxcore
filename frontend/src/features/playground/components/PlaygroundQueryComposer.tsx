/**
 * PlaygroundQueryComposer
 *
 * The primary input surface for query submission.
 * Focuses entirely on input experience without internal messaging.
 *
 * Responsibilities:
 * - Text input (expandable textarea)
 * - Submit button with loading state
 * - Clear/reset action (optional)
 * - Label and helper text
 * - Focus states and accessibility
 *
 * UX requirements:
 * - Luxurious padding
 * - Strong focus ring
 * - Obvious call-to-action button
 * - Helpful placeholder and guidance
 * - Loading state feedback
 *
 * Design principles:
 * - Input is the star
 * - Button is obvious but not loud
 * - Helper text guides usage
 */

import { forwardRef } from "react";

interface PlaygroundQueryComposerProps {
  query: string;
  onQueryChange: (value: string) => void;
  onRun: () => void;
  isRunning: boolean;
  onClear?: () => void;
}

export const PlaygroundQueryComposer = forwardRef<
  HTMLTextAreaElement | null,
  PlaygroundQueryComposerProps
>(function PlaygroundQueryComposer(
  { query, onQueryChange, onRun, isRunning, onClear },
  ref
) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // CMD/CTRL + Enter to submit
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      onRun();
    }
  };

  return (
    <div className="rounded-[2.5rem] border border-white/10 bg-gradient-to-b from-white/[0.05] to-transparent p-8 lg:p-10 shadow-[0_24px_80px_rgba(2,8,23,0.4)]">
      {/* Label */}
      <div className="mb-6 flex items-center justify-between">
        <label className="text-xs font-semibold uppercase tracking-[0.32em] text-sky-300/70">
          Governed Preview
        </label>
        {onClear && query && (
          <button
            type="button"
            onClick={onClear}
            className="text-xs text-slate-400 transition hover:text-white"
          >
            Clear
          </button>
        )}
      </div>

      {/* Input container with focus treatment */}
      <div className="relative rounded-[1.75rem] border border-white/10 bg-black/30 p-1 transition focus-within:border-sky-300/30 focus-within:ring-2 focus-within:ring-sky-400/20">
        <textarea
          ref={ref}
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a business question. e.g., Show revenue by region"
          rows={4}
          className="w-full resize-none rounded-[1.5rem] bg-transparent px-6 py-5 font-mono text-base leading-relaxed text-white outline-none placeholder:text-slate-500 caret-sky-300"
        />
      </div>

      {/* Helper text */}
      <p className="mt-4 text-sm text-slate-400">
        Results are returned from a safe sandbox with governance controls applied.
      </p>

      {/* Actions row */}
      <div className="mt-8 flex items-center justify-end gap-3">
        <button
          type="button"
          onClick={onRun}
          disabled={isRunning || !query.trim()}
          className="inline-flex items-center justify-center gap-2 rounded-full bg-sky-400 px-8 py-3 font-semibold text-slate-950 transition hover:bg-sky-300 hover:shadow-[0_12px_30px_rgba(56,189,248,0.3)] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:shadow-none disabled:hover:bg-sky-400"
        >
          {isRunning ? (
            <>
              <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-slate-950/30 border-t-slate-950" />
              Inspecting...
            </>
          ) : (
            <>
              <span>Run Query</span>
              <span className="text-sm opacity-75">⌘↵</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
});

PlaygroundQueryComposer.displayName = "PlaygroundQueryComposer";
