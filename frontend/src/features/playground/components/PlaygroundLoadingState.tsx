/**
 * PlaygroundLoadingState
 *
 * Elegant loading experience while query executes.
 * Shows soft skeleton screens without technical jargon.
 *
 * Responsibilities:
 * - Display placeholder cards matching result stack shape
 * - Show governed processing message (governance language, not technical)
 * - Maintain visual continuity (match final result dimensions)
 * - Signal progress without spinning chaos
 *
 * Design principles:
 * - Soft, animated skeletons (pulse effect)
 * - Governance-focused messaging ("Reviewing", "Governed")
 * - No spinning icons or technical language
 * - Calm, reassuring tone
 * - Matches result stack height/structure
 */

interface PlaygroundLoadingStateProps {
  className?: string;
  message?: string;
}

const DEFAULT_MESSAGE =
  "Reviewing request against governance policy and preparing preview…";

export function PlaygroundLoadingState({
  className = "",
  message = DEFAULT_MESSAGE,
}: PlaygroundLoadingStateProps) {
  return (
    <div className={`space-y-6 ${className}`}>
      {/* Trust Bar Skeleton */}
      <div className="h-12 rounded-[1rem] bg-white/5 animate-pulse" />

      {/* Hero Insight Card Skeleton */}
      <div className="rounded-[1.25rem] border border-white/10 bg-white/[0.03] p-8 space-y-4">
        <div className="space-y-3">
          <div className="h-8 w-2/3 rounded bg-white/5 animate-pulse" />
          <div className="h-4 w-full rounded bg-white/5 animate-pulse" />
          <div className="h-4 w-3/4 rounded bg-white/5 animate-pulse" />
        </div>
        <div className="pt-4 border-t border-white/10">
          <div className="h-6 w-1/3 rounded bg-white/5 animate-pulse" />
        </div>
      </div>

      {/* Governance Card + Why This Answer Grid Skeleton */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Governance Card */}
        <div className="rounded-[1.25rem] border border-white/10 bg-white/[0.03] p-6 space-y-4">
          <div className="h-6 w-1/3 rounded bg-white/5 animate-pulse" />
          <div className="grid grid-cols-2 gap-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div
                key={i}
                className="rounded-lg border border-white/10 bg-black/20 p-3 space-y-2"
              >
                <div className="h-3 w-2/3 rounded bg-white/5 animate-pulse" />
                <div className="h-5 w-1/2 rounded bg-white/5 animate-pulse" />
              </div>
            ))}
          </div>
        </div>

        {/* Why This Answer Card */}
        <div className="rounded-[1.25rem] border border-white/10 bg-white/[0.03] p-6 space-y-4">
          <div className="h-6 w-1/3 rounded bg-white/5 animate-pulse" />
          <div className="space-y-3">
            <div className="h-4 w-full rounded bg-white/5 animate-pulse" />
            <div className="h-4 w-full rounded bg-white/5 animate-pulse" />
            <div className="h-4 w-2/3 rounded bg-white/5 animate-pulse" />
          </div>
        </div>
      </div>

      {/* Chart Card Skeleton */}
      <div className="rounded-[1.25rem] border border-white/10 bg-white/[0.03] p-6 space-y-4">
        <div className="h-6 w-1/4 rounded bg-white/5 animate-pulse" />
        <div className="h-80 rounded-lg bg-white/5 animate-pulse" />
      </div>

      {/* Data Preview Table Skeleton */}
      <div className="rounded-[1.25rem] border border-white/10 bg-white/[0.03] p-6 space-y-4">
        <div className="h-6 w-1/4 rounded bg-white/5 animate-pulse" />
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-8 rounded bg-white/5 animate-pulse" />
          ))}
        </div>
      </div>

      {/* Processing Message with Pulsing Indicator */}
      <div className="flex items-center justify-center gap-3 py-6">
        {/* Subtle pulse indicator (not a spinner) */}
        <div className="flex gap-1.5">
          <div className="h-2 w-2 rounded-full bg-sky-400/40 animate-pulse" style={{ animationDelay: "0ms" }} />
          <div className="h-2 w-2 rounded-full bg-sky-400/60 animate-pulse" style={{ animationDelay: "150ms" }} />
          <div className="h-2 w-2 rounded-full bg-sky-400/40 animate-pulse" style={{ animationDelay: "300ms" }} />
        </div>
        <p className="text-sm text-slate-400">{message}</p>
      </div>
    </div>
  );
}
