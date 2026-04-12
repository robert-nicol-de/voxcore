/**
 * PlaygroundEmptyState
 *
 * Shown when no query has been executed yet.
 * First impression — make it clear what to do next.
 *
 * Responsibilities:
 * - Welcome new users to Playground
 * - Explain what Playground does
 * - Provide guided prompts to get started
 * - Visual indicator of ready state
 *
 * Design principles:
 * - Strong, clear heading (what is this?)
 * - One-line explanation (why should I care?)
 * - Prompt chips (how do I start?)
 * - Lightweight visual structure (spatial hierarchy)
 */

import { PlaygroundPromptChips } from "./PlaygroundPromptChips";

interface PlaygroundEmptyStateProps {
  onSelectPrompt?: (prompt: string) => void;
  className?: string;
}

export function PlaygroundEmptyState({
  onSelectPrompt,
  className = "",
}: PlaygroundEmptyStateProps) {
  return (
    <div
      className={`rounded-[1.75rem] border border-white/10 bg-white/[0.03] px-8 py-16 lg:py-20 ${className}`}
    >
      <div className="mx-auto max-w-2xl space-y-6">
        {/* Visual indicator: lightweight structure hint */}
        <div className="flex justify-center">
          <div className="text-6xl text-slate-700">◯</div>
        </div>

        {/* Heading: strong, clear, action-oriented */}
        <div className="space-y-2 text-center">
          <h2 className="text-3xl font-bold text-white lg:text-4xl">
            Ask your data anything
          </h2>
          <p className="text-lg text-slate-400">
            Natural language queries with governance, insights, and transparency
          </p>
        </div>

        {/* Divider: subtle visual break */}
        <div className="flex justify-center">
          <div className="h-px w-12 bg-gradient-to-r from-transparent via-slate-500 to-transparent" />
        </div>

        {/* Prompt chips: guided starting points */}
        {onSelectPrompt && (
          <div className="pt-2">
            <PlaygroundPromptChips
              onSelectPrompt={onSelectPrompt}
              prompts={[
                "Show revenue by region for last month",
                "Compare top products by sales",
                "Why did South region revenue decline?",
                "Explain this dataset",
                "Show category performance trend",
              ]}
            />
          </div>
        )}

        {/* Helper text: manage expectations */}
        <div className="rounded-lg border border-white/8 bg-slate-900/30 px-4 py-3">
          <p className="text-sm text-slate-400">
            <span className="font-semibold text-sky-300">💡 Tip:</span> Start with a question
            like "What are the top 3 sales regions?" or "Show me trends over time."
          </p>
        </div>
      </div>
    </div>
  );
}
