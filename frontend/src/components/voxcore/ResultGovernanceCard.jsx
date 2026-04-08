export function ResultGovernanceCard({
  decision,
  riskScore,
  rewritten,
  maxRows,
  mode,
  explanation,
}) {
  const rows = [
    { label: 'Decision', value: decision ?? 'Unknown' },
    { label: 'Risk Score', value: String(riskScore ?? 0) },
    { label: 'Rewritten', value: rewritten ? 'Yes' : 'No' },
    { label: 'Row Limit', value: String(maxRows ?? 0) },
    { label: 'Execution Mode', value: mode === 'demo' ? 'Demo Fallback' : 'Live Backend' },
  ];

  return (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
      <div className="mb-4">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
          Governance
        </p>
        <h3 className="mt-2 text-lg font-semibold text-white">
          Query Control Summary
        </h3>
      </div>

      <div className="space-y-3">
        {rows.map((row) => (
          <div
            key={row.label}
            className="flex items-center justify-between rounded-2xl border border-white/5 bg-black/20 px-4 py-3"
          >
            <span className="text-sm text-slate-400">{row.label}</span>
            <span className="text-sm font-medium text-white">{row.value}</span>
          </div>
        ))}
      </div>

      {explanation ? (
        <div className="mt-4 rounded-2xl border border-blue-500/20 bg-blue-500/10 p-4">
          <p className="text-sm text-slate-200">{explanation}</p>
        </div>
      ) : null}
    </div>
  );
}

export default ResultGovernanceCard;
