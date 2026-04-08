interface RiskBreakdownProps {
  score: number;
  factors: Array<{ name: string; value: number }>;
  className?: string;
}

export function RiskBreakdown({ score, factors, className = "" }: RiskBreakdownProps) {
  const total = factors.reduce((sum, f) => sum + f.value, 0);

  return (
    <div className={`bg-red-500/10 border border-red-500/30 rounded-2xl p-6 ${className}`}>
      <div className="mb-6">
        <div className="text-xs uppercase text-gray-500 tracking-wider mb-1">Risk Score</div>
        <div className="text-5xl font-bold text-red-400">{score}</div>
      </div>
      
      <div className="space-y-3">
        <div className="text-xs uppercase text-gray-500 tracking-wider">Breakdown</div>
        {factors.map((factor, idx) => (
          <div key={idx} className="flex items-center justify-between">
            <span className="text-sm text-gray-300">{factor.name}</span>
            <div className="flex items-center gap-2">
              <div className="w-32 h-2 bg-white/5 rounded">
                <div
                  className="h-2 bg-red-400 rounded"
                  style={{ width: `${(factor.value / total) * 100}%` }}
                />
              </div>
              <span className="text-sm font-semibold text-red-400 w-8">+{factor.value}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
