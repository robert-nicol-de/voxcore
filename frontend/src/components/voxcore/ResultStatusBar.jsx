function badgeTone(decision) {
  if (decision === 'SAFE') return 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30';
  if (decision === 'REVIEW') return 'bg-amber-500/15 text-amber-300 border-amber-500/30';
  if (decision === 'BLOCKED') return 'bg-red-500/15 text-red-300 border-red-500/30';
  return 'bg-slate-500/15 text-slate-300 border-slate-500/30';
}

export function ResultStatusBar({
  decision,
  riskScore,
  mode,
  notice,
}) {
  const isDemo = mode === 'demo' || mode === 'Demo Fallback';
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <div className="flex flex-wrap items-center gap-3">
        <span className={`rounded-full border px-3 py-1 text-xs font-semibold tracking-wide ${badgeTone(decision)}`}>
          {decision ?? 'UNKNOWN'}
        </span>

        <span className="rounded-full border border-blue-500/30 bg-blue-500/15 px-3 py-1 text-xs font-semibold text-blue-300">
          Risk {riskScore ?? 0}
        </span>

        <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold text-slate-300">
          {isDemo ? 'Demo Fallback' : 'Live Backend'}
        </span>
      </div>

      {notice ? (
        <p className="mt-3 text-sm text-amber-300">
          {notice}
        </p>
      ) : null}
    </div>
  );
}

export default ResultStatusBar;
