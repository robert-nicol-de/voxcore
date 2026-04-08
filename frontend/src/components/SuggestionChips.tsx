import React from "react";

interface Props {
  suggestions: string[];
  onClick?: (suggestion: string) => void;
}

export default function SuggestionChips({ suggestions, onClick }: Props) {
  if (!suggestions || suggestions.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-2 mt-2">
      {suggestions.map((s, i) => (
        <span
          key={i}
          className="px-3 py-1 rounded bg-[var(--bg-hover)] text-xs cursor-pointer hover:bg-[var(--bg-elevated)] transition"
          onClick={() => onClick?.(s)}
        >
          {s}
        </span>
      ))}
    </div>
  );
}
