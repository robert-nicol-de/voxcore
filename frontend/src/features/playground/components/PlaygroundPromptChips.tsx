/**
 * PlaygroundPromptChips
 *
 * Guide first-time usage with curated example prompts.
 * Renders 4-6 enterprise-style prompt starters (not cute/fluffy).
 *
 * Responsibilities:
 * - Display curated example queries
 * - Handle prompt selection via callback
 * - Look professional and analytical
 * - Encourage serious query usage
 *
 * Design principles:
 * - Enterprise-focused examples
 * - Clean, minimal presentation
 * - Clear affordance (clickable)
 * - Hierarchical emphasis (most useful first)
 */

interface PlaygroundPromptChipsProps {
  onSelectPrompt: (prompt: string) => void;
  prompts?: string[];
  className?: string;
}

const DEFAULT_PROMPTS = [
  "Show revenue by region for last month",
  "Compare top products by sales",
  "Why did South region revenue decline?",
  "Explain this dataset",
  "Show category performance trend",
];

export function PlaygroundPromptChips({
  onSelectPrompt,
  prompts = DEFAULT_PROMPTS,
  className = "",
}: PlaygroundPromptChipsProps) {
  return (
    <div className={`space-y-3 ${className}`}>
      {/* Label */}
      <p className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-500">
        Try these
      </p>

      {/* Chips grid */}
      <div className="flex flex-wrap gap-2">
        {prompts.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => onSelectPrompt(prompt)}
            className="rounded-full border border-white/12 bg-white/[0.04] px-4 py-2 text-sm text-slate-300 transition hover:border-sky-300/30 hover:bg-sky-400/10 hover:text-white focus:outline-none focus:ring-2 focus:ring-sky-400/40 focus:ring-offset-2 focus:ring-offset-[#020817]"
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  );
}
