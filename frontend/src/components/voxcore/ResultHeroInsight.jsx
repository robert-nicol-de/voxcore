export function ResultHeroInsight({
  title,
  summary,
  stat,
}) {
  return (
    <div className="rounded-3xl border border-blue-500/20 bg-gradient-to-br from-blue-500/10 to-transparent p-6 shadow-[0_0_0_1px_rgba(255,255,255,0.03)]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-blue-300/80">
            Key Insight
          </p>
          <h3 className="mt-2 text-2xl font-semibold text-white">
            {title || 'Governed query result ready'}
          </h3>
          <p className="mt-2 max-w-3xl text-sm text-slate-300">
            {summary || 'VoxCore analyzed the request and returned a governed response.'}
          </p>
        </div>

        {stat ? (
          <div className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-right">
            <p className="text-xs uppercase tracking-wide text-slate-400">Signal</p>
            <p className="mt-1 text-lg font-semibold text-white">{stat}</p>
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default ResultHeroInsight;
