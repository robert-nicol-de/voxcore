/**
 * PlaygroundErrorState
 *
 * Calm, premium failure state when query execution encounters an error.
 * Reassures user about sandbox safety and offers retry/fallback options.
 *
 * Responsibilities:
 * - Display helpful error message (no technical jargon)
 * - Reassure user about query safety and data governance
 * - Provide retry button to rerun same query
 * - Offer fallback prompts to explore different queries
 * - Maintain premium design consistency (warm colors, calm tone)
 *
 * Design principles:
 * - Warm, reassuring tone (not scary or technical)
 * - Amber accent color (caution, not alarm)
 * - Clear next steps (retry or try example)
 * - No stack traces, no "fallback failed", no jargon
 * - Premium card styling matching other components
 */

import { usePlaygroundStore } from "../state";

interface PlaygroundErrorStateProps {
  /** User-facing error message (normalized by service layer) */
  error: string;
  /**
   * Optional callback when user clicks a fallback prompt.
   * If provided, user can explore different queries.
   */
  onSelectPrompt?: (prompt: string) => void;
  /** Optional CSS class for outer container */
  className?: string;
}

/** Fallback prompts user can try when initial query fails */
const FALLBACK_PROMPTS = [
  "Show me high-level data overview",
  "What are the main categories?",
  "Compare top 5 items by value",
  "Show me recent trends",
  "Explain this dataset to me",
];

export function PlaygroundErrorState({
  error,
  onSelectPrompt,
  className = "",
}: PlaygroundErrorStateProps) {
  // Get retry action from store
  const store = usePlaygroundStore.getState();
  const currentQuery = usePlaygroundStore((state) => state.query);

  /**
   * Retry: Submit the same query again
   * User may have hit a temporary issue; retry often succeeds
   */
  const handleRetry = () => {
    store.submitQuery(currentQuery);
  };

  /**
   * Fallback: User selects a prompt to try
   * Delegates to parent if callback provided, otherwise fall back
   */
  const handleFallbackPrompt = (prompt: string) => {
    if (onSelectPrompt) {
      onSelectPrompt(prompt);
    } else {
      store.setQuery(prompt);
      store.submitQuery(prompt);
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Error card: Warm, reassuring design */}
      <div className="rounded-[1.75rem] border border-amber-500/20 bg-gradient-to-br from-amber-500/10 to-amber-500/5 px-8 py-10 space-y-6">
        {/* Header: Icon + Heading */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-amber-500/20 text-lg text-amber-300">
                ⚡
              </div>
              <h2 className="text-xl font-semibold text-amber-200">
                We hit a bump
              </h2>
            </div>
          </div>

          {/* Reassurance message */}
          <p className="text-base text-slate-300 leading-relaxed">
            Your query encountered an issue during execution. This is a temporary
            hiccup — your data is safe, and all queries are governed by our
            security policies. Let's try again.
          </p>

          {/* Error explanation (user-friendly) */}
          <div className="rounded-lg bg-white/5 px-4 py-3 border border-white/10">
            <p className="text-sm text-slate-400">
              <span className="font-semibold text-slate-300">What happened:</span>{" "}
              {error}
            </p>
          </div>
        </div>

        {/* Action buttons: Retry + Fallback options */}
        <div className="flex flex-col gap-3 pt-2">
          {/* Retry button (primary action) */}
          <button
            onClick={handleRetry}
            className="rounded-[0.875rem] bg-gradient-to-r from-sky-500/80 to-sky-400/80 hover:from-sky-500 hover:to-sky-400 px-6 py-3 font-medium text-white transition-all duration-200 flex items-center justify-center gap-2 group"
          >
            <span className="text-lg">↻</span>
            <span>Retry Query</span>
          </button>

          {/* Or divider */}
          <div className="flex items-center gap-3 py-2">
            <div className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent" />
            <span className="text-xs text-slate-500 font-medium">or try</span>
            <div className="h-px flex-1 bg-gradient-to-l from-white/10 to-transparent" />
          </div>
        </div>
      </div>

      {/* Fallback prompts: Suggestions if initial query failed */}
      {FALLBACK_PROMPTS.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-400 px-2">
            Try something simpler
          </h3>

          <div className="grid gap-2">
            {FALLBACK_PROMPTS.map((prompt, index) => (
              <button
                key={index}
                onClick={() => handleFallbackPrompt(prompt)}
                className="group rounded-[0.875rem] border border-white/10 bg-white/[0.03] hover:bg-white/[0.06] px-4 py-3 text-left transition-all duration-200"
              >
                <p className="text-sm text-slate-300 group-hover:text-white font-medium">
                  {prompt}
                </p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Footer: Reassurance */}
      <div className="rounded-[1rem] border border-sky-500/10 bg-sky-500/5 px-4 py-4">
        <p className="text-xs text-sky-200/70 leading-relaxed">
          💡 <span className="font-semibold">All good:</span> Your request is
          always reviewed against governance policies. The secure sandbox
          protects your data. Try again whenever you're ready.
        </p>
      </div>
    </div>
  );
}
