import Skeleton from "./Skeleton";

export default function SkeletonTable() {
  return (
    <div className="space-y-2">
      {[...Array(6)].map((_, i) => (
        <div
          key={i}
          className="grid grid-cols-4 gap-4 p-3 rounded-lg bg-[var(--bg-card)]"
        >
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-full" />
        </div>
      ))}
    </div>
  );
}
