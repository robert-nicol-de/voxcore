import React from "react";

export function highlightNumbers(text: string) {
  // Highlight +12% or -18% as bold and green/red
  return text.split(/(\+?\-?\d+\.?\d*%)/g).map((part, i) => {
    if (/^\+\d/.test(part)) return <b key={i} className="text-green-600 font-bold">{part}</b>;
    if (/^\-\d/.test(part)) return <b key={i} className="text-red-600 font-bold">{part}</b>;
    return part;
  });
}

type Props = {
  story: string;
  confidence?: number;
  tone?: "executive" | "casual";
};

export function ImpactStory({ story, confidence, tone }: Props) {
  return (
    <div className="p-4 bg-blue-50 rounded-2xl border mb-4">
      <div className="text-sm text-blue-600 mb-1 flex items-center gap-2">
        🧠 Impact Story
        {confidence !== undefined && (
          <span className="ml-2 px-2 py-0.5 rounded bg-blue-100 text-blue-700 text-xs">Confidence: {confidence >= 0.9 ? "High" : confidence >= 0.7 ? "Medium" : "Low"} ({confidence.toFixed(2)})</span>
        )}
        {tone && (
          <span className="ml-2 px-2 py-0.5 rounded bg-gray-100 text-gray-700 text-xs">{tone === "executive" ? "Executive" : "Casual"}</span>
        )}
      </div>
      <p className="text-sm text-gray-800 leading-relaxed">
        {highlightNumbers(story)}
      </p>
    </div>
  );
}
