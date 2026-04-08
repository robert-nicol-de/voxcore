export default function SkeletonCard() {
  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border-default)] rounded-xl p-6 animate-pulse mb-4">
      <div className="h-6 w-1/3 bg-[var(--bg-elevated)] rounded mb-4"></div>
      <div className="h-4 w-2/3 bg-[var(--bg-elevated)] rounded mb-2"></div>
      <div className="h-4 w-1/2 bg-[var(--bg-elevated)] rounded"></div>
    </div>
  );
}