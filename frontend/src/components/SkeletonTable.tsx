export default function SkeletonTable() {
  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border-default)] rounded-xl p-6 animate-pulse mb-4">
      <div className="h-6 w-1/4 bg-[var(--bg-elevated)] rounded mb-4"></div>
      <div className="h-4 w-full bg-[var(--bg-elevated)] rounded mb-2"></div>
      <div className="h-4 w-full bg-[var(--bg-elevated)] rounded mb-2"></div>
      <div className="h-4 w-5/6 bg-[var(--bg-elevated)] rounded"></div>
    </div>
  );
}