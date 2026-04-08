interface RiskScoreCardProps {
  score: number;
  label?: string;
  theme?: "danger" | "warning" | "safe";
  className?: string;
}

export function RiskScoreCard({
  score,
  label = "Risk Score",
  theme = score > 70 ? "danger" : score > 40 ? "warning" : "safe",
  className = "",
}: RiskScoreCardProps) {
  const colors = {
    danger: { text: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/30" },
    warning: { text: "text-yellow-400", bg: "bg-yellow-500/10", border: "border-yellow-500/30" },
    safe: { text: "text-green-400", bg: "bg-green-500/10", border: "border-green-500/30" },
  };

  const color = colors[theme];

  return (
    <div className={`${color.bg} border ${color.border} rounded-2xl p-6 ${className}`}>
      <div className="text-xs uppercase text-gray-500 tracking-wider mb-2">{label}</div>
      <div className={`text-5xl font-bold ${color.text} mb-2`}>{score}</div>
      <div className="text-xs text-gray-400">
        {theme === "danger" && "High risk query detected"}
        {theme === "warning" && "Medium risk - Review recommended"}
        {theme === "safe" && "Safe to execute"}
      </div>
    </div>
  );
}
