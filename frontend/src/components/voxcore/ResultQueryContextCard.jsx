function ContextChip({ label, value }) {
  if (!value) return null;

  return (
    <div className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-200">
      <span className="text-slate-400">{label}: </span>
      <span className="font-medium text-white">{value}</span>
    </div>
  );
}

export function ResultQueryContextCard({
  context,
  mode,
}) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
        Query Context
      </p>

      <div className="mt-4 flex flex-wrap gap-3">
        <ContextChip label="Metric" value={context?.metric} />
        <ContextChip label="Dimension" value={context?.dimension} />
        <ContextChip label="Time" value={context?.timeFilter} />
        <ContextChip label="Intent" value={context?.intent} />
        <ContextChip label="Source" value={context?.source} />
        <ContextChip label="Mode" value={mode === 'demo' ? 'Demo Fallback' : 'Live Backend'} />
      </div>
    </div>
  );
}

export default ResultQueryContextCard;
