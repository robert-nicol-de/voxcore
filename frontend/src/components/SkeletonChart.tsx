export default function SkeletonChart() {
  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border-default)] rounded-xl p-6 animate-pulse mb-4 flex flex-col items-center justify-center" style={{ height: 320 }}>
      <div className="h-8 w-1/3 bg-[var(--bg-elevated)] rounded mb-6"></div>
      <div className="h-48 w-5/6 bg-[var(--bg-elevated)] rounded"></div>
    </div>
  );
}