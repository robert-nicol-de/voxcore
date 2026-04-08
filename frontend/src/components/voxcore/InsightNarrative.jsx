export default function InsightNarrative({ text }) {
  if (!text) return null;
  return (
    <div className="mb-4">
      <h3 className="text-lg font-semibold mb-1 text-[var(--text-primary)]">Narrative</h3>
      <p className="text-[var(--text-primary)] text-base">{text}</p>
    </div>
  );
}
