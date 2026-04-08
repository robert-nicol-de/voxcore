import Skeleton from "./Skeleton";

export default function SkeletonChart() {
  return (
    <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
      <Skeleton className="h-40 w-full" />
    </div>
  );
}
