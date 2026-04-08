export function ResultDrilldownModal({
  open,
  selectedPoint,
  onClose,
}) {
  if (!open || !selectedPoint) return null;

  // Calculate contribution percentage if we have numeric data
  const values = Object.values(selectedPoint).filter((v) => typeof v === "number");
  const total = values.reduce((a, b) => a + b, 0);
  const primaryValue = values[0] || 0;
  const contribution = total > 0 ? ((primaryValue / total) * 100).toFixed(1) : "0";

  // Generate a suggested follow-up based on the data
  const name = Object.values(selectedPoint).find((v) => typeof v === "string");
  const suggestedFollowUp = name ? `Analyze ${name} in detail` : "Drill down further";

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="w-full max-w-md rounded-3xl border border-white/10 bg-gradient-to-br from-slate-900 to-slate-950 p-6 shadow-2xl">
          {/* Header */}
          <div className="mb-6 flex items-start justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-blue-300/80">
                Segment Details
              </p>
              <h2 className="mt-2 text-2xl font-semibold text-white">
                {name || "Selected Point"}
              </h2>
            </div>
            <button
              onClick={onClose}
              className="rounded-full border border-white/10 bg-white/5 p-2 transition hover:bg-white/10"
              aria-label="Close"
            >
              <svg
                className="h-5 w-5 text-slate-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* Metrics Grid */}
          <div className="mb-6 grid gap-3">
            {Object.entries(selectedPoint).map(([key, value]) => (
              <div
                key={key}
                className="rounded-2xl border border-white/5 bg-black/20 p-4"
              >
                <p className="text-xs uppercase tracking-wide text-slate-400">
                  {key}
                </p>
                <p className="mt-1 text-lg font-semibold text-white">
                  {typeof value === "number"
                    ? new Intl.NumberFormat("en-US").format(value)
                    : value}
                </p>
              </div>
            ))}

            {/* Contribution */}
            <div className="rounded-2xl border border-blue-500/20 bg-blue-500/10 p-4">
              <p className="text-xs uppercase tracking-wide text-blue-300">
                Contribution
              </p>
              <p className="mt-1 text-lg font-semibold text-blue-200">
                {contribution}%
              </p>
            </div>
          </div>

          {/* Suggested Follow-up */}
          <div className="mb-6 rounded-2xl border border-amber-500/20 bg-amber-500/10 p-4">
            <p className="text-xs uppercase tracking-wide text-amber-300">
              Suggested Next Question
            </p>
            <p className="mt-2 text-sm text-amber-100">{suggestedFollowUp}</p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 rounded-xl border border-white/10 bg-white/5 px-4 py-2 font-medium text-white transition hover:bg-white/10"
            >
              Close
            </button>
            <button
              onClick={onClose}
              className="flex-1 rounded-xl bg-blue-600 px-4 py-2 font-medium text-white transition hover:bg-blue-500"
            >
              Ask About This
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

export default ResultDrilldownModal;
