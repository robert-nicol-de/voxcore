import React from "react";
import type { PlaygroundSuggestion } from "../types/playground";
import { PlaygroundSuggestionCard } from "./PlaygroundSuggestionCard";

interface PlaygroundSuggestionsRowProps {
  /** Array of suggestion cards to display */
  suggestions: PlaygroundSuggestion[];
  /** Callback when user clicks a suggestion card */
  onSelectSuggestion?: (query: string) => void;
  /** Optional CSS class name */
  className?: string;
}

/**
 * PlaygroundSuggestionsRow
 *
 * Turn follow-ups into action with deliberate, useful suggestion cards.
 * Encourages natural conversation flow without overwhelming users.
 *
 * Features:
 * - Renders 3-5 suggestion cards
 * - Click to submit next question
 * - Cards feel deliberate and useful, not spammy
 * - Responsive layout (stacks on mobile, wraps on desktop)
 * - Clear visual feedback on hover/click
 * - Arrow icon to encourage action
 * - Graceful empty state (returns null if no suggestions)
 *
 * Design philosophy:
 * - Suggestions are "next logical steps," not random options
 * - Cards should feel like conversation continuations
 * - Visual prominence: secondary to results but visible
 * - Hover states show interactivity clearly
 */
export function PlaygroundSuggestionsRow({
  suggestions,
  onSelectSuggestion,
  className = "",
}: PlaygroundSuggestionsRowProps) {
  // Filter to 3-5 suggestions
  const displaySuggestions = suggestions.slice(0, 5);

  // If no suggestions, don't render
  if (!displaySuggestions || displaySuggestions.length === 0) {
    return null;
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Section header */}
      <div>
        <h3 className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-400">
          Try Next
        </h3>
        <p className="text-xs text-slate-500 mt-1">
          Suggested follow-up questions to explore further
        </p>
      </div>

      {/* Suggestion cards grid */}
      <div
        className={`grid gap-3 ${
          displaySuggestions.length === 1
            ? "grid-cols-1"
            : displaySuggestions.length === 2
              ? "grid-cols-1 sm:grid-cols-2"
              : displaySuggestions.length === 3
                ? "grid-cols-1 sm:grid-cols-3"
                : "grid-cols-1 sm:grid-cols-2 lg:grid-cols-5"
        }`}
      >
        {displaySuggestions.map((suggestion, idx) => (
          <PlaygroundSuggestionCard
            key={idx}
            suggestion={suggestion}
            onSelect={(query) => onSelectSuggestion?.(query)}
          />
        ))}
      </div>

      {/* Encouragement text */}
      <div className="flex items-center gap-2 rounded-lg bg-slate-900/30 px-3 py-2 border border-slate-700/20">
        <span className="text-sky-400">💡</span>
        <p className="text-xs text-slate-400">
          These suggestions are curated based on your question and results.
        </p>
      </div>
    </div>
  );
}
