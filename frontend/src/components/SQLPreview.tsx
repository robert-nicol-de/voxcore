interface SQLPreviewProps {
  query: string;
  label?: string;
  className?: string;
}

export function SQLPreview({ query, label = "SQL Query", className = "" }: SQLPreviewProps) {
  return (
    <div className={className}>
      {label && <div className="text-xs text-gray-500 mb-2 uppercase tracking-wider">{label}</div>}
      <pre className="bg-[#0B0F19] border border-white/10 rounded-2xl p-4 text-sm text-green-400 overflow-x-auto">
        <code>{query}</code>
      </pre>
    </div>
  );
}
