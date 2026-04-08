export function ResultSuggestionsRow({
  suggestions,
  onSuggestionClick,
}) {
  if (!suggestions?.length) return null;

  return (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
      <div className="mb-4">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
          Suggested Next Questions
        </p>
      </div>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            type="button"
            onClick={() => onSuggestionClick?.(suggestion)}
            className="rounded-2xl border border-white/10 bg-black/20 p-4 text-left transition hover:-translate-y-0.5 hover:border-blue-400/30 hover:bg-blue-500/10"
          >
            <p className="text-sm font-medium text-white">{suggestion}</p>
            <p className="mt-2 text-xs text-slate-400">Run this next</p>
          </button>
        ))}
      </div>
    </div>
  );
}

export default ResultSuggestionsRow;
