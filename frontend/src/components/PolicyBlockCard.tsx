interface PolicyBlockCardProps {
  title: string;
  reason: string;
  policy?: string;
  suggestion?: string;
  className?: string;
}

export function PolicyBlockCard({
  title,
  reason,
  policy,
  suggestion,
  className = "",
}: PolicyBlockCardProps) {
  return (
    <div className={`bg-red-500/10 border border-red-500/30 rounded-2xl p-6 ${className}`}>
      <div className="flex items-start gap-3 mb-3">
        <div className="text-red-400">
          <svg className="w-5 h-5 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M13.477 14.89A6 6 0 15.828 4.172a6 6 0 00-2.35 10.718zM8 12a1 1 0 100-2 1 1 0 000 2zm0-8a1 1 0 100-2 1 1 0 000 2z" />
          </svg>
        </div>
        <div>
          <h3 className="font-semibold text-red-400">{title}</h3>
          <p className="text-sm text-gray-300 mt-1">{reason}</p>
        </div>
      </div>
      
      {policy && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Policy</div>
          <div className="text-sm text-gray-300">{policy}</div>
        </div>
      )}
      
      {suggestion && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Suggestion</div>
          <div className="text-sm text-gray-300">{suggestion}</div>
        </div>
      )}
    </div>
  );
}
