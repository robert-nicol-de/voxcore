/**
 * PlaygroundHero
 *
 * The top messaging block above the query composer.
 * Establishes context and sets expectations for the Playground experience.
 *
 * Content:
 * - Headline: Core value proposition
 * - Subtitle: Brief explanation
 * - Trust message: Reassurance about sandbox/governance
 *
 * Design principles:
 * - Minimal and focused (not marketing-noisy)
 * - Single clear purpose
 * - Generous whitespace
 */

interface PlaygroundHeroProps {
  title?: string;
  subtitle?: string;
  trustMessage?: string;
  className?: string;
}

export function PlaygroundHero({
  title = "Govern every AI question before it reaches data",
  subtitle = "Ask a business question and see how VoxCore interprets, governs, and explains the result in a safe sandbox.",
  trustMessage = "All results are returned from a simulated environment with full governance controls applied.",
  className = "",
}: PlaygroundHeroProps) {
  return (
    <div className={`mb-12 space-y-4 lg:mb-16 ${className}`}>
      {/* Main headline */}
      <h1 className="text-4xl font-semibold leading-tight text-white lg:text-5xl">
        {title}
      </h1>

      {/* Subtitle explanation */}
      <p className="max-w-2xl text-lg text-slate-300 lg:text-base">
        {subtitle}
      </p>

      {/* Trust message (subtle but present) */}
      <div className="flex items-start gap-3 rounded-lg border border-sky-400/20 bg-sky-400/5 px-4 py-3 mt-6">
        <div className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-sky-400/20 text-xs text-sky-300">
          ✓
        </div>
        <p className="text-sm text-sky-200/80">
          {trustMessage}
        </p>
      </div>
    </div>
  );
}
